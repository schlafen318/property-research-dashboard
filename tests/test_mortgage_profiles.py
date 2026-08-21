from __future__ import annotations

import json
import unittest
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from src import build_unified_app


ROOT = Path(__file__).resolve().parents[1]


class MortgageProfileTests(unittest.TestCase):
    ALLOWED_AVAILABILITY = {
        "likely_available",
        "conditional",
        "no_standard_nonresident_route",
        "research_incomplete",
    }

    @classmethod
    def setUpClass(cls) -> None:
        cls.destinations = json.loads((ROOT / "data" / "destinations.json").read_text())
        retirement = json.loads((ROOT / "data" / "retirement_costs.json").read_text())
        cls.retirement_ids = {item["destination_id"] for item in retirement["destinations"]}
        cls.payload = build_unified_app.load_mortgage_profiles()

    def test_payload_has_nonresident_overseas_income_default(self) -> None:
        self.assertEqual(
            {"residency": "non_resident", "income_source": "overseas"},
            self.payload["default_buyer_profile"],
        )

    def test_every_retirement_destination_resolves_to_a_profile(self) -> None:
        covered = [item for item in self.destinations if item["id"] in self.retirement_ids]
        self.assertEqual(len(self.retirement_ids), len(covered))
        for destination in covered:
            with self.subTest(destination=destination["id"]):
                profile = build_unified_app.resolve_mortgage_profile(destination, self.payload)
                self.assertEqual(destination["id"], profile["destination_id"])
                self.assertIn(profile["availability"], self.ALLOWED_AVAILABILITY)
                self.assertIn(profile["confidence"], {"low", "medium", "medium-high", "high"})
                self.assertLessEqual(date.fromisoformat(profile["evidence_date"]), date.today())
                if profile["availability"] == "conditional":
                    self.assertTrue(profile["conditions"])
                if profile["availability"] != "research_incomplete":
                    self.assertTrue(profile["sources"])

    def test_profile_ranges_and_sources_are_valid(self) -> None:
        for country, profile in self.payload["countries"].items():
            with self.subTest(country=country):
                maximum_ltv = profile["maximum_ltv"]
                self.assertTrue(maximum_ltv is None or 0 <= maximum_ltv <= 1)
                self.assertIsInstance(profile["loan_currencies"], list)
                for source in profile["sources"]:
                    parsed = urlparse(source["url"])
                    self.assertEqual("https", parsed.scheme)
                    self.assertTrue(parsed.netloc)
                    self.assertTrue(source["name"].strip())

    def test_destination_override_does_not_mutate_country_profile(self) -> None:
        destination = next(item for item in self.destinations if item["id"] == "valencia")
        country_before = json.dumps(self.payload["countries"][destination["country"]], sort_keys=True)
        resolved = build_unified_app.resolve_mortgage_profile(destination, self.payload)
        resolved["conditions"].append("mutation")
        self.assertEqual(
            country_before,
            json.dumps(self.payload["countries"][destination["country"]], sort_keys=True),
        )


if __name__ == "__main__":
    unittest.main()
