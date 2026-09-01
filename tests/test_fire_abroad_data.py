import copy
import json
import unittest
from datetime import date
from pathlib import Path

from src.fire_abroad import (
    ACTIVE_LIFE_WEIGHTS,
    FIRE_WEIGHTS,
    LAUNCH_DESTINATION_IDS,
    load_fire_abroad,
    validate_fire_abroad_payload,
)


ROOT = Path(__file__).resolve().parents[1]


class FireAbroadDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.destination_ids = {
            row["id"]
            for row in json.loads((ROOT / "data" / "destinations.json").read_text(encoding="utf-8"))
        }
        cls.retirement_ids = {
            row["destination_id"]
            for row in json.loads((ROOT / "data" / "retirement_costs.json").read_text(encoding="utf-8"))["destinations"]
        }

    def setUp(self):
        self.payload = load_fire_abroad()

    def validate(self, payload):
        return validate_fire_abroad_payload(
            payload,
            destination_ids=self.destination_ids,
            retirement_ids=self.retirement_ids,
            as_of=date(2026, 9, 1),
        )

    def test_launch_contract_is_structurally_valid(self):
        self.assertEqual(1.0, sum(FIRE_WEIGHTS.values()))
        self.assertEqual(1.0, sum(ACTIVE_LIFE_WEIGHTS.values()))
        self.assertEqual(set(LAUNCH_DESTINATION_IDS), set(self.payload["launch_destination_ids"]))
        self.assertEqual([], self.validate(self.payload))

    def test_missing_tax_source_is_rejected_for_complete_country(self):
        payload = copy.deepcopy(self.payload)
        payload["countries"]["Spain"]["tax_screen"]["source_ids"] = []
        errors = self.validate(payload)
        self.assertTrue(
            any("countries.Spain.tax_screen.source_ids" in error for error in errors),
            errors,
        )

    def test_unordered_tax_bands_are_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload["countries"]["Spain"]["tax_screen"]["planning_bands"]["full_relocation"] = {
            "favorable_rate": 0.30,
            "central_rate": 0.20,
            "adverse_rate": 0.10,
        }
        errors = self.validate(payload)
        self.assertTrue(
            any("planning_bands.full_relocation" in error and "ordered" in error for error in errors),
            errors,
        )

    def test_missing_property_lifecycle_stage_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        del payload["countries"]["Spain"]["tax_screen"]["property_lifecycle"]["sale"]
        errors = self.validate(payload)
        self.assertTrue(
            any("property_lifecycle.sale" in error for error in errors),
            errors,
        )

    def test_pending_country_must_be_explicit_and_cannot_claim_tax_values(self):
        payload = copy.deepcopy(self.payload)
        pending = payload["countries"]["Portugal"]["tax_screen"]
        pending["planning_bands"] = {
            "seasonal": {"favorable_rate": 0, "central_rate": 0, "adverse_rate": 0}
        }
        errors = self.validate(payload)
        self.assertTrue(
            any("countries.Portugal.tax_screen.planning_bands" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
