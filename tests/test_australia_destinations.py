from __future__ import annotations

import json
import unittest
from pathlib import Path

from src import build_unified_app


ROOT = Path(__file__).resolve().parents[1]


class AustraliaDestinationTests(unittest.TestCase):
    def test_australian_destinations_have_complete_profiles_and_evidence(self) -> None:
        destinations = json.loads((ROOT / "data" / "destinations.json").read_text(encoding="utf-8"))
        listings = json.loads((ROOT / "data" / "listings.json").read_text(encoding="utf-8"))
        by_id = {item["id"]: item for item in destinations}

        self.assertEqual(len(destinations), 37)
        for destination_id in ("gold-coast-sunshine-coast", "perth-margaret-river"):
            with self.subTest(destination_id=destination_id):
                destination = by_id[destination_id]
                self.assertEqual(destination["country"], "Australia")
                self.assertEqual(len(destination["scores"]), 14)
                self.assertIn("new", destination["ownership_notes"].lower())
                destination_listings = [
                    item for item in listings if item["destination_id"] == destination_id
                ]
                self.assertEqual(len(destination_listings), 3)

    def test_fx_data_supports_australian_property_examples(self) -> None:
        fx = json.loads((ROOT / "data" / "fx_rates.json").read_text(encoding="utf-8"))

        self.assertGreater(fx["rates_to_usd"]["AUD"], 0)

    def test_homepage_hero_does_not_show_an_academic_research_snapshot(self) -> None:
        html = build_unified_app.build_landing_page([], [], [], 0)

        self.assertNotIn('class="trust-snapshot"', html)
        self.assertNotIn("Research coverage", html)
        self.assertNotIn("Evidence base", html)


if __name__ == "__main__":
    unittest.main()
