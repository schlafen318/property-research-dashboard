from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "retirement_costs.json"
DESTINATIONS_PATH = ROOT / "data" / "destinations.json"
CORE_CATEGORIES = {
    "food_household",
    "utilities_communications",
    "private_healthcare",
    "transport",
    "dining_leisure",
    "travel",
    "visa_admin",
    "contingency",
}
CONFIDENCE_LEVELS = {"low", "medium", "medium-high", "high"}


class RetirementCostDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        cls.records = {item["destination_id"]: item for item in cls.payload["destinations"]}
        cls.destination_ids = {
            item["id"]
            for item in json.loads(DESTINATIONS_PATH.read_text(encoding="utf-8"))
        }

    def test_release_destination_set_is_complete(self) -> None:
        self.assertEqual(30, len(self.records))
        self.assertTrue(set(self.records) <= self.destination_ids)

    def test_profiles_have_positive_single_and_couple_costs(self) -> None:
        for record in self.records.values():
            for household in ("single", "couple"):
                profile = record["profiles"][household]
                self.assertEqual(CORE_CATEGORIES, set(profile["categories_usd"]))
                self.assertTrue(all(value >= 0 for value in profile["categories_usd"].values()))
                self.assertGreater(profile["annual_rent_usd"], 0)
                self.assertGreater(profile["annual_owner_costs_usd"], 0)

    def test_couple_non_housing_costs_exceed_single_costs(self) -> None:
        for record in self.records.values():
            single = sum(record["profiles"]["single"]["categories_usd"].values())
            couple = sum(record["profiles"]["couple"]["categories_usd"].values())
            self.assertGreater(couple, single, record["destination_id"])

    def test_rates_property_and_confidence_are_bounded(self) -> None:
        for record in self.records.values():
            self.assertGreater(record["property"]["representative_price_usd"], 0)
            self.assertGreaterEqual(record["property"]["acquisition_cost_rate"], 0)
            self.assertLessEqual(record["property"]["acquisition_cost_rate"], 0.25)
            for value in record["inflation"].values():
                self.assertGreaterEqual(value, 0)
                self.assertLessEqual(value, 0.15)
            self.assertIn(record["confidence"]["overall"], CONFIDENCE_LEVELS)
            allowed_proxies = CORE_CATEGORIES | {"rent", "owner_costs", "property", "inflation"}
            self.assertTrue(set(record["confidence"]["proxy_categories"]) <= allowed_proxies)

    def test_every_record_has_dated_metric_sources(self) -> None:
        for record in self.records.values():
            self.assertGreaterEqual(len(record["sources"]), 3)
            self.assertTrue(record["property"]["price_basis"].strip())
            for source in record["sources"]:
                self.assertTrue(source["name"].strip())
                self.assertTrue(source["url"].startswith("https://"))
                self.assertTrue(source["metric_supported"].strip())
                self.assertTrue(source["source_date"].strip())
                self.assertRegex(source["accessed_on"], r"^\d{4}-\d{2}-\d{2}$")
                self.assertTrue(source["notes"].strip())


if __name__ == "__main__":
    unittest.main()
