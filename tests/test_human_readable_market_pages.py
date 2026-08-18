from __future__ import annotations

import unittest
from datetime import date

from src import build_unified_app


class HumanReadableDestinationPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.destinations = build_unified_app.load_json("destinations.json")
        cls.dubai = next(item for item in cls.destinations if item["id"] == "dubai")
        cls.html = build_unified_app.build_destination_page(
            cls.dubai,
            [],
            cls.destinations,
            build_unified_app.SEO_PAGES,
        )

    def test_destination_hero_uses_plain_reader_facing_labels(self) -> None:
        self.assertIn("<h1>Dubai</h1>", self.html)
        self.assertNotIn("<h1>Dubai Property Research</h1>", self.html)
        self.assertIn("City · United Arab Emirates</p>", self.html)
        self.assertNotIn("City · United Arab Emirates · updated", self.html)
        self.assertIn("<span>Overall rating</span>", self.html)
        self.assertIn("<span>Price guide</span>", self.html)
        self.assertNotIn("<span>Decision score</span>", self.html)
        self.assertNotIn("<span>Entry benchmark</span>", self.html)

    def test_destination_has_one_compact_summary_and_six_part_reading_path(self) -> None:
        self.assertEqual(self.html.count('class="market-summary"'), 1)
        self.assertNotIn("Should this destination stay on your shortlist?", self.html)
        for label in ("Overview", "Buyer fit", "Areas", "Costs and risks", "Evidence", "Compare"):
            self.assertIn(f">{label}</a>", self.html)
        self.assertEqual(self.html.count('class="sticky-jump"'), 1)
        sticky_nav = self.html.split('class="sticky-jump"', 1)[1].split("</nav>", 1)[0]
        self.assertEqual(sticky_nav.count("<a "), 6)

    def test_destination_moves_supporting_links_and_date_to_the_bottom(self) -> None:
        self.assertNotIn('class="page-aside mobile-resources"', self.html)
        self.assertEqual(self.html.count('id="continue-research"'), 1)
        self.assertIn("Continue your research", self.html)
        resources_at = self.html.index('id="continue-research"')
        updated_at = self.html.index(f"Last updated {date.today().isoformat()}")
        self.assertGreater(resources_at, self.html.index('id="compare"'))
        self.assertGreater(updated_at, resources_at)

    def test_destination_has_one_reader_action_region(self) -> None:
        self.assertEqual(self.html.count('class="destination-actions"'), 1)
        self.assertNotIn('class="mobile-action-strip"', self.html)


if __name__ == "__main__":
    unittest.main()
