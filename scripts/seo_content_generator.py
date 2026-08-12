from __future__ import annotations

import hashlib
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"


@dataclass(frozen=True)
class TargetPageContext:
    target_url: str
    page_type: str
    title: str
    meta_description: str
    h1: str
    intro: str
    faqs: tuple[tuple[str, str], ...]
    sitemap_urls: tuple[str, ...]
    base_content_hash: str


class PageContextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values = {"title": "", "description": "", "canonical": "", "h1": "", "intro": ""}
        self.faqs: list[tuple[str, str]] = []
        self.capture: str | None = None
        self.buffer: list[str] = []
        self.in_faq = False
        self.faq_question = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = set((values.get("class") or "").split())
        if tag == "meta" and values.get("name") == "description":
            self.values["description"] = values.get("content") or ""
        elif tag == "link" and values.get("rel") == "canonical":
            self.values["canonical"] = values.get("href") or ""
        elif tag == "details" and "faq-item" in classes:
            self.in_faq = True
        elif tag == "title" and not self.values["title"]:
            self.capture, self.buffer = "title", []
        elif tag == "h1" and not self.values["h1"]:
            self.capture, self.buffer = "h1", []
        elif tag == "p" and ({"seo-lede", "page-lede"} & classes) and not self.values["intro"]:
            self.capture, self.buffer = "intro", []
        elif self.in_faq and tag == "summary":
            self.capture, self.buffer = "faq_question", []
        elif self.in_faq and tag == "p":
            self.capture, self.buffer = "faq_answer", []

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        expected = {
            "title": "title",
            "h1": "h1",
            "summary": "faq_question",
            "p": self.capture if self.capture in {"intro", "faq_answer"} else None,
        }.get(tag)
        if self.capture and expected == self.capture:
            value = " ".join("".join(self.buffer).split())
            if self.capture == "faq_question":
                self.faq_question = value
            elif self.capture == "faq_answer":
                self.faqs.append((self.faq_question, value))
            else:
                self.values[self.capture] = value
            self.capture, self.buffer = None, []
        if tag == "details":
            self.in_faq = False


def canonical_to_artifact_path(target_url: str, artifacts_root: Path = ARTIFACTS) -> Path:
    parsed = urlparse(target_url)
    if parsed.scheme != "https" or parsed.netloc != "globalhomeatlas.com":
        raise ValueError(f"Unsupported target URL: {target_url}")
    relative = parsed.path.strip("/")
    return artifacts_root / relative / "index.html" if relative else artifacts_root / "index.html"


def content_hash(
    title: str,
    description: str,
    h1: str,
    intro: str,
    faqs: tuple[tuple[str, str], ...],
) -> str:
    payload = "\n".join([title, description, h1, intro, *[f"{q}\n{a}" for q, a in faqs]])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def page_type_for_url(target_url: str) -> str:
    parsed = urlparse(target_url)
    if parsed.scheme != "https" or parsed.netloc != "globalhomeatlas.com":
        raise ValueError(f"Unsupported target URL: {target_url}")
    if parsed.path == "/":
        return "homepage"
    if parsed.path.startswith("/countries/"):
        return "country"
    if parsed.path.startswith("/destinations/"):
        return "destination"
    return "guide"


def collect_target_context(
    target_url: str,
    sitemap_urls: list[str] | tuple[str, ...],
    artifacts_root: Path = ARTIFACTS,
) -> TargetPageContext:
    known_urls = tuple(sitemap_urls)
    if target_url not in known_urls:
        raise ValueError(f"Target URL is not present in sitemap: {target_url}")
    path = canonical_to_artifact_path(target_url, artifacts_root)
    if not path.exists():
        raise ValueError(f"Target artifact does not exist: {path}")
    parser = PageContextParser()
    parser.feed(path.read_text(encoding="utf-8"))
    if parser.values["canonical"] != target_url:
        raise ValueError(f"Canonical mismatch for {target_url}")
    missing = [field for field in ("title", "description", "h1") if not parser.values[field]]
    if missing:
        raise ValueError(f"Missing required page context: {', '.join(missing)}")
    faqs = tuple(parser.faqs)
    return TargetPageContext(
        target_url=target_url,
        page_type=page_type_for_url(target_url),
        title=parser.values["title"],
        meta_description=parser.values["description"],
        h1=parser.values["h1"],
        intro=parser.values["intro"],
        faqs=faqs,
        sitemap_urls=known_urls,
        base_content_hash=content_hash(
            parser.values["title"],
            parser.values["description"],
            parser.values["h1"],
            parser.values["intro"],
            faqs,
        ),
    )
