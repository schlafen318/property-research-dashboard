from __future__ import annotations

import copy
from datetime import date
import json
from pathlib import Path
import unittest

from src.fire_abroad import (
    ACTIVE_LIFE_WEIGHTS,
    FIRE_WEIGHTS,
    VALID_STAY_MODES,
    load_fire_abroad,
    validate_fire_abroad_payload,
)


ROOT = Path(__file__).resolve().parents[1]
LAUNCH_IDS = {
    "algarve-cascais",
    "bali",
    "croatia-istria-dalmatia",
    "crete",
    "da-nang-hoi-an",
    "fukuoka-itoshima",
    "madeira",
    "malaga-costa-del-sol",
    "phuket-koh-samui",
    "valencia",
}


class FireAbroadDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.destination_ids = {
            row["id"]
            for row in json.loads((ROOT / "data/destinations.json").read_text())
        }
        cls.retirement_ids = {
            row["destination_id"]
            for row in json.loads(
                (ROOT / "data/retirement_costs.json").read_text()
            )["destinations"]
        }

    def validate(self, payload: dict) -> list[str]:
        return validate_fire_abroad_payload(
            payload,
            destination_ids=self.destination_ids,
            retirement_ids=self.retirement_ids,
            as_of=date(2026, 8, 29),
        )

    def test_launch_contract_is_complete_and_valid(self) -> None:
        payload = load_fire_abroad()
        self.assertEqual(LAUNCH_IDS, set(payload["launch_destination_ids"]))
        self.assertEqual(1.0, sum(FIRE_WEIGHTS.values()))
        self.assertEqual(1.0, sum(ACTIVE_LIFE_WEIGHTS.values()))
        self.assertEqual(
            {"seasonal", "part_year", "full_relocation"}, VALID_STAY_MODES
        )
        self.assertEqual([], self.validate(payload))

    def test_missing_tax_source_names_country_and_field(self) -> None:
        payload = copy.deepcopy(load_fire_abroad())
        payload["countries"]["Portugal"]["tax"]["source_ids"] = []

        errors = self.validate(payload)

        self.assertTrue(
            any("Portugal" in error and "tax.source_ids" in error for error in errors),
            errors,
        )

    def test_missing_active_life_score_names_destination_and_field(self) -> None:
        payload = copy.deepcopy(load_fire_abroad())
        payload["destination_overrides"]["madeira"]["active_life"][
            "everyday_movement"
        ]["score"] = None

        errors = self.validate(payload)

        self.assertTrue(
            any(
                "madeira" in error
                and "active_life.everyday_movement.score" in error
                for error in errors
            ),
            errors,
        )

    def test_dangling_source_names_destination_and_field(self) -> None:
        payload = copy.deepcopy(load_fire_abroad())
        payload["destination_overrides"]["bali"]["source_ids"].append(
            "indonesia-source-that-does-not-exist"
        )

        errors = self.validate(payload)

        self.assertTrue(
            any("bali" in error and "source_ids" in error for error in errors),
            errors,
        )

    def test_stale_volatile_review_names_country_and_field(self) -> None:
        payload = copy.deepcopy(load_fire_abroad())
        payload["countries"]["Portugal"]["tax"]["last_reviewed"] = "2026-05-01"

        errors = self.validate(payload)

        self.assertTrue(
            any(
                "Portugal" in error and "tax.last_reviewed" in error
                for error in errors
            ),
            errors,
        )

    def test_malformed_enum_names_country_and_field(self) -> None:
        payload = copy.deepcopy(load_fire_abroad())
        payload["countries"]["Portugal"]["stay_routes"]["seasonal"]["status"] = [
            "eligible"
        ]

        errors = self.validate(payload)

        self.assertTrue(
            any(
                "Portugal" in error
                and "stay_routes.seasonal.status" in error
                for error in errors
            ),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
