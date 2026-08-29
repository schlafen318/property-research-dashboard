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
COMPOSITE_ACTIVE_SOURCES = {
    "algarve-cascais": {"portugal-algarve-active-1", "portugal-cascais-active-1"},
    "croatia-istria-dalmatia": {
        "croatia-istria-active-1",
        "croatia-dalmatia-active-1",
    },
    "phuket-koh-samui": {"thailand-phuket-active-1", "thailand-samui-active-1"},
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

    def test_launch_critical_verification_gaps_are_unranked(self) -> None:
        payload = load_fire_abroad()
        stay_gaps = (
            ("Croatia", "full_relocation"),
            ("Japan", "part_year"),
            ("Japan", "full_relocation"),
            ("Vietnam", "part_year"),
            ("Vietnam", "full_relocation"),
        )
        for country_id, mode in stay_gaps:
            route = payload["countries"][country_id]["stay_routes"][mode]
            self.assertEqual("needs_verification", route["status"])
            self.assertIsNone(route["base_score"])

        vietnam_health = payload["countries"]["Vietnam"]["healthcare"][
            "by_mode"
        ]["full_relocation"]
        self.assertEqual("needs_verification", vietnam_health["eligibility"])
        self.assertIsNone(vietnam_health["bridge_score"])

        for country in payload["countries"].values():
            for mode_tax in country["tax"]["by_mode"].values():
                self.assertIn("status", mode_tax)
                self.assertIn("rankable", mode_tax)

    def test_composite_destinations_cite_both_geographies(self) -> None:
        payload = load_fire_abroad()
        for destination_id, required_sources in COMPOSITE_ACTIVE_SOURCES.items():
            active_life = payload["destination_overrides"][destination_id][
                "active_life"
            ]
            for component, record in active_life.items():
                self.assertTrue(
                    required_sources.issubset(record["source_ids"]),
                    f"{destination_id} active_life.{component}.source_ids",
                )

    def test_noncanonical_launch_id_is_rejected_even_when_shared(self) -> None:
        payload = copy.deepcopy(load_fire_abroad())
        payload["launch_destination_ids"][0] = "chamonix"
        payload["destination_overrides"]["chamonix"] = payload[
            "destination_overrides"
        ].pop("algarve-cascais")

        errors = self.validate(payload)

        self.assertTrue(
            any(
                "payload" in error and "launch_destination_ids" in error
                for error in errors
            ),
            errors,
        )

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

    def test_needs_verification_numeric_scores_are_rejected(self) -> None:
        payload = copy.deepcopy(load_fire_abroad())
        payload["countries"]["Japan"]["stay_routes"]["part_year"][
            "base_score"
        ] = 2.0
        payload["countries"]["Vietnam"]["healthcare"]["by_mode"][
            "full_relocation"
        ]["bridge_score"] = 2.5

        errors = self.validate(payload)

        self.assertTrue(
            any(
                "Japan" in error and "stay_routes.part_year.base_score" in error
                for error in errors
            ),
            errors,
        )
        self.assertTrue(
            any(
                "Vietnam" in error
                and "healthcare.by_mode.full_relocation.bridge_score" in error
                for error in errors
            ),
            errors,
        )

    def test_rankable_tax_mode_requires_supported_score(self) -> None:
        payload = copy.deepcopy(load_fire_abroad())
        mode_tax = payload["countries"]["Portugal"]["tax"]["by_mode"][
            "part_year"
        ]
        mode_tax["status"] = "needs_verification"
        mode_tax["rankable"] = True

        errors = self.validate(payload)

        self.assertTrue(
            any(
                "Portugal" in error
                and "tax.by_mode.part_year.compatibility_score" in error
                for error in errors
            ),
            errors,
        )
        self.assertTrue(
            any(
                "Portugal" in error and "tax.by_mode.part_year.rankable" in error
                for error in errors
            ),
            errors,
        )

    def test_malformed_collections_accumulate_named_errors(self) -> None:
        payload = copy.deepcopy(load_fire_abroad())
        payload["launch_destination_ids"].append({"bad": "id"})
        payload["destination_overrides"]["bali"]["activity_tags"].append(
            ["walking"]
        )
        payload["destination_overrides"]["madeira"]["country"] = ["Portugal"]

        errors = self.validate(payload)

        for owner, field in (
            ("payload", "launch_destination_ids"),
            ("bali", "activity_tags"),
            ("madeira", "country"),
        ):
            self.assertTrue(
                any(owner in error and field in error for error in errors), errors
            )


if __name__ == "__main__":
    unittest.main()
