from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
SITE_ORIGIN = "https://globalhomeatlas.com"

KEY_PAGES = [
    ARTIFACTS / "guides" / "index.html",
    ARTIFACTS / "best-countries-to-buy-property-as-a-foreigner" / "index.html",
    ARTIFACTS / "countries" / "spain-property" / "index.html",
]

REQUIRED_MARKERS = {
    ARTIFACTS / "guides" / "index.html": [
        "Start with the strongest route",
        "Ready to turn research into a shortlist?",
    ],
    ARTIFACTS / "best-countries-to-buy-property-as-a-foreigner" / "index.html": [
        "Decision Path",
        "Turn this guide into a shortlist",
    ],
    ARTIFACTS / "countries" / "spain-property" / "index.html": [
        "Buyer Next Step",
        "Turn Spain research into a shortlist",
    ],
}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in {"a", "link", "script", "img", "source"}:
            return
        lookup = dict(attrs)
        for attr in ("href", "src"):
            value = lookup.get(attr)
            if value:
                self.links.append(value)


def sitemap_count(path: Path) -> int:
    tree = ET.parse(path)
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return len(tree.findall(".//sm:url", namespace))


def local_target_exists(link: str) -> bool:
    parsed = urlparse(link)
    if parsed.scheme in {"mailto", "tel", "data", "javascript"}:
        return True
    if parsed.netloc and f"{parsed.scheme}://{parsed.netloc}" != SITE_ORIGIN:
        return True
    path = unquote(parsed.path or "/")
    if not path.startswith("/"):
        return True
    if path.endswith("/"):
        candidate = ARTIFACTS / path.lstrip("/") / "index.html"
    else:
        candidate = ARTIFACTS / path.lstrip("/")
        if candidate.suffix == "":
            candidate = candidate / "index.html"
    return candidate.exists()


def broken_local_links() -> list[str]:
    broken: list[str] = []
    for html_path in ARTIFACTS.rglob("*.html"):
        parser = LinkParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        for link in parser.links:
            if not local_target_exists(link):
                broken.append(f"{html_path.relative_to(ROOT)} -> {link}")
    return broken


def verify(min_sitemap_urls: int) -> list[str]:
    errors: list[str] = []
    for page in KEY_PAGES:
        if not page.exists():
            errors.append(f"Missing key page: {page.relative_to(ROOT)}")
    count = sitemap_count(ARTIFACTS / "sitemap.xml")
    if count < min_sitemap_urls:
        errors.append(f"Sitemap URL count {count} is below minimum {min_sitemap_urls}")
    for page, markers in REQUIRED_MARKERS.items():
        if not page.exists():
            continue
        text = re.sub(r"\s+", " ", page.read_text(encoding="utf-8"))
        for marker in markers:
            if marker not in text:
                errors.append(f"Missing marker {marker!r} in {page.relative_to(ROOT)}")
    errors.extend(broken_local_links())
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-sitemap-urls", type=int, default=65)
    args = parser.parse_args()
    errors = verify(args.min_sitemap_urls)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Static site verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
