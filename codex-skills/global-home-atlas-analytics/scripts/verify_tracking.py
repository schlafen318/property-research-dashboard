from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "artifacts"
EXPECTED_EVENTS = {
    "dashboard_open",
    "guide_click",
    "destination_click",
    "compare_selection",
    "memo_shortlist_add",
    "memo_shortlist_remove",
    "memo_shortlist_clear",
    "memo_export",
    "memo_preview_export",
    "private_brief_preview_render",
    "shortlist_share_link",
    "data_export_json",
    "data_export_csv",
    "outbound_listing_click",
    "shortlist_review_click",
    "report_teaser_click",
    "report_library_cta",
    "country_report_cta",
    "paid_memo_cta",
    "saved_shortlist_intake_prefill",
    "custom_shortlist_submit",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.h1 = 0
        self.title = ""
        self.in_title = False
        self.meta_description = 0
        self.canonical = 0
        self.forms: list[str] = []
        self.schema_blobs: list[str] = []
        self._in_schema = False
        self._schema_buffer: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if tag in {"script", "style"}:
            self._skip_depth += 1
            if tag == "script" and attr.get("type") == "application/ld+json":
                self._in_schema = True
                self._schema_buffer = []
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.in_title = True
        if tag == "meta" and attr.get("name") == "description":
            self.meta_description += 1
        if tag == "link" and attr.get("rel") == "canonical":
            self.canonical += 1
        if tag == "form":
            self.forms.append(attr.get("id") or "")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._skip_depth:
            if self._in_schema:
                self.schema_blobs.append("".join(self._schema_buffer))
                self._in_schema = False
            self._skip_depth -= 1
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_schema:
            self._schema_buffer.append(data)
        elif self.in_title:
            self.title += data


def sitemap_urls() -> list[str]:
    sitemap = ARTIFACTS / "sitemap.xml"
    root = ET.parse(sitemap).getroot()
    return [
        node.text or ""
        for node in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if node.text
    ]


def path_for_url(url: str) -> Path:
    rel = url.replace("https://globalhomeatlas.com/", "")
    if not rel:
        return ARTIFACTS / "index.html"
    return ARTIFACTS / rel.rstrip("/") / "index.html"


def main() -> int:
    failures: list[tuple[str, str]] = []
    urls = sitemap_urls()
    tracking_pages = 0

    for url in urls:
        path = path_for_url(url)
        if not path.exists():
            failures.append((url, "missing generated file"))
            continue
        html = path.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(html)

        if parser.h1 != 1:
            failures.append((url, f"h1 count {parser.h1}"))
        if not parser.title.strip():
            failures.append((url, "missing title"))
        if parser.meta_description < 1:
            failures.append((url, "missing meta description"))
        if parser.canonical != 1:
            failures.append((url, f"canonical count {parser.canonical}"))
        if not parser.schema_blobs:
            failures.append((url, "missing json-ld"))
        for blob in parser.schema_blobs:
            try:
                json.loads(blob)
            except json.JSONDecodeError:
                failures.append((url, "invalid json-ld"))

        if "window.GHA" in html and "gha_event_queue" in html:
            tracking_pages += 1
        else:
            failures.append((url, "missing tracking layer"))

    homepage = (ARTIFACTS / "index.html").read_text(encoding="utf-8")
    dashboard = (ARTIFACTS / "dashboard" / "index.html").read_text(encoding="utf-8")
    contact = (ARTIFACTS / "contact" / "index.html").read_text(encoding="utf-8")
    shortlist_review = (ARTIFACTS / "shortlist-review" / "index.html").read_text(encoding="utf-8")
    reports = (ARTIFACTS / "reports" / "index.html").read_text(encoding="utf-8")
    country_hub = (ARTIFACTS / "countries" / "spain-property" / "index.html").read_text(encoding="utf-8")
    tracked_surfaces = homepage + dashboard + contact + shortlist_review + reports + country_hub
    missing_events = sorted(event for event in EXPECTED_EVENTS if event not in tracked_surfaces)
    for event in missing_events:
        failures.append(("events", f"missing {event}"))
    if 'id="custom-shortlist-form"' not in contact:
        failures.append(("contact", "missing custom shortlist form"))
    if 'id="conversion"' not in homepage:
        failures.append(("homepage", "missing conversion section"))

    print(f"sitemap_urls={len(urls)}")
    print(f"tracking_pages={tracking_pages}")
    print(f"expected_events={len(EXPECTED_EVENTS)}")

    if failures:
        print("FAILURES")
        for item in failures[:80]:
            print(f"{item[0]}: {item[1]}")
        return 1
    print("tracking_verification=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
