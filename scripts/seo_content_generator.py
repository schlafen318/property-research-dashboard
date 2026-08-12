from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
SEO_CONTENT_OVERRIDES_PATH = ROOT / "data" / "seo_content_overrides.json"
POLICY_FLAG_NAMES = ("legal", "tax", "visa", "ownership", "price", "yield", "return", "guarantee")

PROPOSAL_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "finding_fingerprint": {"type": "string"},
        "target_url": {"type": "string"},
        "base_content_hash": {"type": "string"},
        "title": {"type": ["string", "null"]},
        "meta_description": {"type": ["string", "null"]},
        "intro": {"type": ["string", "null"]},
        "faq_question": {"type": ["string", "null"]},
        "faq_answer": {"type": ["string", "null"]},
        "internal_link_target": {"type": ["string", "null"]},
        "internal_link_anchor": {"type": ["string", "null"]},
        "rationale": {"type": "string"},
        "source_fragments": {"type": "array", "items": {"type": "string"}},
        "policy_flags": {
            "type": "object",
            "properties": {name: {"type": "boolean"} for name in POLICY_FLAG_NAMES},
            "required": list(POLICY_FLAG_NAMES),
            "additionalProperties": False,
        },
    },
    "required": [
        "finding_fingerprint",
        "target_url",
        "base_content_hash",
        "title",
        "meta_description",
        "intro",
        "faq_question",
        "faq_answer",
        "internal_link_target",
        "internal_link_anchor",
        "rationale",
        "source_fragments",
        "policy_flags",
    ],
    "additionalProperties": False,
}


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


@dataclass(frozen=True)
class ContentProposal:
    finding_fingerprint: str
    target_url: str
    base_content_hash: str
    title: str | None
    meta_description: str | None
    intro: str | None
    faq_question: str | None
    faq_answer: str | None
    internal_link_target: str | None
    internal_link_anchor: str | None
    rationale: str
    source_fragments: tuple[str, ...]
    policy_flags: dict[str, bool]


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


def proposal_from_dict(payload: dict) -> ContentProposal:
    required = set(PROPOSAL_JSON_SCHEMA["required"])
    if set(payload) != required:
        missing = sorted(required - set(payload))
        extra = sorted(set(payload) - required)
        raise ValueError(f"Invalid proposal fields; missing={missing}, extra={extra}")
    flags = payload.get("policy_flags")
    if not isinstance(flags, dict) or set(flags) != set(POLICY_FLAG_NAMES):
        raise ValueError("Invalid proposal policy flags")
    if not all(isinstance(flags[name], bool) for name in POLICY_FLAG_NAMES):
        raise ValueError("Proposal policy flags must be booleans")
    fragments = payload.get("source_fragments")
    if not isinstance(fragments, list) or not all(isinstance(item, str) for item in fragments):
        raise ValueError("Proposal source_fragments must be strings")
    nullable_fields = (
        "title",
        "meta_description",
        "intro",
        "faq_question",
        "faq_answer",
        "internal_link_target",
        "internal_link_anchor",
    )
    if any(payload[field] is not None and not isinstance(payload[field], str) for field in nullable_fields):
        raise ValueError("Proposal content fields must be strings or null")
    return ContentProposal(
        finding_fingerprint=str(payload["finding_fingerprint"]),
        target_url=str(payload["target_url"]),
        base_content_hash=str(payload["base_content_hash"]),
        title=payload["title"],
        meta_description=payload["meta_description"],
        intro=payload["intro"],
        faq_question=payload["faq_question"],
        faq_answer=payload["faq_answer"],
        internal_link_target=payload["internal_link_target"],
        internal_link_anchor=payload["internal_link_anchor"],
        rationale=str(payload["rationale"]),
        source_fragments=tuple(fragments),
        policy_flags=dict(flags),
    )


def _source_text(context: TargetPageContext) -> str:
    return "\n".join(
        [
            context.title,
            context.meta_description,
            context.h1,
            context.intro,
            *[f"{question}\n{answer}" for question, answer in context.faqs],
        ]
    )


def _proposal_text(proposal: ContentProposal) -> str:
    return "\n".join(
        value
        for value in (
            proposal.title,
            proposal.meta_description,
            proposal.intro,
            proposal.faq_question,
            proposal.faq_answer,
            proposal.internal_link_anchor,
        )
        if value
    )


def validate_proposal(proposal: ContentProposal, context: TargetPageContext) -> list[str]:
    errors: list[str] = []
    if proposal.target_url != context.target_url:
        errors.append("Target URL does not match page context")
    if proposal.base_content_hash != context.base_content_hash:
        errors.append("Base content hash is stale")
    if not re.fullmatch(r"gha-[a-z0-9-]+", proposal.finding_fingerprint):
        errors.append("Finding fingerprint is invalid")
    if (proposal.faq_question is None) != (proposal.faq_answer is None):
        errors.append("FAQ question and answer must be paired")
    if context.page_type != "guide" and proposal.faq_question is not None:
        errors.append("FAQ changes are limited to guide pages")
    if (proposal.internal_link_target is None) != (proposal.internal_link_anchor is None):
        errors.append("Internal link target and anchor must be paired")
    if proposal.internal_link_target:
        if proposal.internal_link_target not in context.sitemap_urls:
            errors.append("Internal link target is not present in sitemap")
        if proposal.internal_link_target == context.target_url:
            errors.append("Internal link target cannot be the current page")
    if proposal.title is not None and not 30 <= len(proposal.title.strip()) <= 65:
        errors.append("Title must contain 30 to 65 characters")
    if proposal.meta_description is not None and not 70 <= len(proposal.meta_description.strip()) <= 165:
        errors.append("Meta description must contain 70 to 165 characters")
    content_values = [
        proposal.title,
        proposal.meta_description,
        proposal.intro,
        proposal.faq_question,
        proposal.faq_answer,
        proposal.internal_link_anchor,
    ]
    if any(value is not None and not value.strip() for value in content_values):
        errors.append("Proposed content fields cannot be blank")
    original_values = {
        context.title,
        context.meta_description,
        context.intro,
        *[item for pair in context.faqs for item in pair],
    }
    if all(value is None or value.strip() in original_values for value in content_values):
        errors.append("Proposal does not make a material content change")
    source_lower = _source_text(context).lower()
    for fragment in proposal.source_fragments:
        if not fragment.strip() or fragment.lower() not in source_lower:
            errors.append(f"Source fragment is not present in page context: {fragment}")
    proposed_text = _proposal_text(proposal)
    source_numbers = set(re.findall(r"(?:[$€£¥]\s*)?\d+(?:[.,]\d+)?%?", _source_text(context)))
    proposed_numbers = set(re.findall(r"(?:[$€£¥]\s*)?\d+(?:[.,]\d+)?%?", proposed_text))
    if proposed_numbers - source_numbers:
        errors.append("Proposal introduces a number absent from source context")
    for name, flagged in proposal.policy_flags.items():
        if flagged:
            errors.append(f"Proposal policy flag is set: {name}")
    for term in ("guarantee", "guaranteed", "return", "yield", "tax", "visa", "legal advice"):
        if term in proposed_text.lower() and term not in source_lower:
            errors.append(f"Proposal introduces prohibited claim language: {term}")
    return errors


def override_entry(
    proposal: ContentProposal,
    finding: dict,
    *,
    generated_at: str,
    model: str,
    cooldown_until: str,
) -> dict:
    return {
        "target_url": proposal.target_url,
        "finding_fingerprint": proposal.finding_fingerprint,
        "base_content_hash": proposal.base_content_hash,
        "generated_at": generated_at,
        "model": model,
        "signal": finding,
        "lifecycle": "proposed",
        "cooldown_until": cooldown_until,
        "content": {
            "title": proposal.title,
            "meta_description": proposal.meta_description,
            "intro": proposal.intro,
            "faq_question": proposal.faq_question,
            "faq_answer": proposal.faq_answer,
            "internal_link_target": proposal.internal_link_target,
            "internal_link_anchor": proposal.internal_link_anchor,
        },
    }


def load_override_entries(path: Path = SEO_CONTENT_OVERRIDES_PATH) -> list[dict]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("SEO content overrides must be a list")
    return [item for item in payload if isinstance(item, dict)]


def upsert_override_entry(entry: dict, path: Path = SEO_CONTENT_OVERRIDES_PATH) -> None:
    rows = load_override_entries(path)
    rows = [
        row
        for row in rows
        if row.get("target_url") != entry.get("target_url")
        and row.get("finding_fingerprint") != entry.get("finding_fingerprint")
    ]
    rows.append(entry)
    rows.sort(key=lambda row: str(row.get("target_url") or ""))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
