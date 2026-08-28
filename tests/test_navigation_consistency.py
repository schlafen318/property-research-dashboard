from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import Path


ARTIFACTS = Path(__file__).resolve().parents[1] / "artifacts"
EXPECTED_PRIMARY_LINKS = [
    ("/", "Global Home Atlas"),
    ("/dashboard/", "Destination Rankings"),
    ("/retirement-abroad-calculator/", "Retirement Calculator"),
    ("/countries/", "Country Guides"),
    ("/guides/", "Buying Guides"),
]


class PrimaryNavigationParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.nav_stack: list[str] = []
        self.in_primary = False
        self.in_mobile = False
        self.links: list[dict[str, str]] = []
        self.current_link: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "nav":
            label = attributes.get("aria-label", "")
            self.nav_stack.append(label)
            if label == "Primary":
                self.in_primary = True
            elif self.in_primary and label == "Mobile primary":
                self.in_mobile = True
        if not self.in_primary:
            return
        if tag == "a" and not self.in_mobile:
            self.current_link = {"href": attributes.get("href", ""), "label": ""}
            self.links.append(self.current_link)
        elif tag == "img" and self.current_link is not None:
            self.current_link["label"] += attributes.get("alt", "")

    def handle_data(self, data: str) -> None:
        if self.current_link is not None:
            self.current_link["label"] += data

    def handle_endtag(self, tag: str) -> None:
        if not self.in_primary:
            return
        if tag == "a":
            self.current_link = None
        if tag == "nav" and self.nav_stack:
            label = self.nav_stack.pop()
            if label == "Mobile primary":
                self.in_mobile = False
            elif label == "Primary":
                self.in_primary = False


class NavigationConsistencyTests(unittest.TestCase):
    def test_every_routed_page_uses_the_same_primary_navigation(self) -> None:
        pages = sorted(ARTIFACTS.rglob("index.html"))
        self.assertGreater(len(pages), 70)

        for page in pages:
            with self.subTest(page=page.relative_to(ARTIFACTS)):
                html = page.read_text(encoding="utf-8")
                if 'name="robots" content="noindex' in html:
                    continue
                parser = PrimaryNavigationParser()
                parser.feed(html)
                links = [(link["href"], " ".join(link["label"].split())) for link in parser.links]
                self.assertEqual(links, EXPECTED_PRIMARY_LINKS)

    def test_top_level_routes_use_the_shared_editorial_shell(self) -> None:
        for route in ("dashboard", "retirement-abroad-calculator", "countries", "guides"):
            with self.subTest(route=route):
                html = (ARTIFACTS / route / "index.html").read_text(encoding="utf-8")
                self.assertIn('class="gha-mode-utility gha-top-level', html)
                self.assertIn('<header class="gha-header">', html)
                self.assertIn('<footer class="gha-footer">', html)
                self.assertIn('id="gha-top-level-design"', html)


if __name__ == "__main__":
    unittest.main()
