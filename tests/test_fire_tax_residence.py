from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "fire_tax_residence.js"
FIXTURE = ROOT / "tests" / "fixtures" / "fire_tax_residence.json"


def fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def run_residence(profile: object, *, mutate=None) -> object:
    data = fixture()
    if mutate:
        mutate(data)
    script = (
        "const api = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        "process.stdout.write(JSON.stringify(api.evaluateResidence("
        "input.profile, input.destinationRules, input.homeRules)));"
    )
    result = subprocess.run(
        [
            "node",
            "-e",
            script,
            str(ENGINE),
            json.dumps(
                {
                    "profile": profile,
                    "destinationRules": data["destinationRules"],
                    "homeRules": data["homeRules"],
                }
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


BASE = {
    "taxYear": 2026,
    "daysInDestination": 100,
    "destinationAvailableHome": False,
    "daysInHome": 200,
    "homeAvailableHome": False,
    "familyTies": "neither",
    "economicTies": "neither",
}


class FireTaxResidenceTests(unittest.TestCase):
    def test_day_threshold_is_inclusive_and_changes_residence_scope(self):
        result = run_residence({**BASE, "daysInDestination": 183, "daysInHome": 100})

        self.assertEqual("likely_destination_resident", result["status"])
        self.assertEqual("worldwide_income", result["scopes"]["destination"])
        self.assertEqual("source_income", result["scopes"]["home"])
        self.assertIn("synthetic-destination-days-2026", result["ruleIds"])
        self.assertEqual([], result["unresolvedFacts"])

    def test_below_day_threshold_remains_likely_home_resident(self):
        result = run_residence({**BASE, "daysInDestination": 182})

        self.assertEqual("likely_home_resident", result["status"])
        self.assertEqual("source_income", result["scopes"]["destination"])
        self.assertEqual("worldwide_income", result["scopes"]["home"])

    def test_available_home_is_a_separate_domestic_residence_test(self):
        result = run_residence(
            {
                **BASE,
                "destinationAvailableHome": True,
                "treatyPermanentHome": "both",
                "treatyCentreOfVitalInterests": "both",
            }
        )

        self.assertEqual("possible_dual_resident", result["status"])
        self.assertIn("synthetic-destination-home-2026", result["ruleIds"])
        self.assertIn("synthetic-home-days-2026", result["ruleIds"])

    def test_family_and_economic_ties_can_create_dual_residence(self):
        neutral_treaty = {
            "treatyPermanentHome": "both",
            "treatyCentreOfVitalInterests": "both",
        }
        family = run_residence({**BASE, **neutral_treaty, "familyTies": "destination"})
        economic = run_residence({**BASE, **neutral_treaty, "economicTies": "both"})

        self.assertEqual("possible_dual_resident", family["status"])
        self.assertEqual("possible_dual_resident", economic["status"])
        self.assertIn("synthetic-destination-family-2026", family["ruleIds"])
        self.assertIn("synthetic-destination-economic-2026", economic["ruleIds"])

    def test_supported_treaty_tie_breaker_resolves_dual_residence_in_order(self):
        result = run_residence(
            {
                **BASE,
                "destinationAvailableHome": True,
                "treatyPermanentHome": "both",
                "treatyCentreOfVitalInterests": "destination",
            }
        )

        self.assertEqual("likely_destination_resident", result["status"])
        self.assertEqual("destination", result["treatyResidence"])
        self.assertEqual("worldwide_income", result["scopes"]["destination"])
        self.assertEqual("source_income", result["scopes"]["home"])
        self.assertIn("synthetic-treaty-tie-breaker-2026", result["ruleIds"])
        self.assertIn("synthetic-treaty-2026", result["sourceIds"])

    def test_unknown_controlling_fact_returns_conditional_not_zero_or_guess(self):
        profile = {**BASE}
        profile.pop("daysInDestination")
        result = run_residence(profile)

        self.assertEqual("conditional", result["status"])
        self.assertIn("daysInDestination", result["unresolvedFacts"])
        self.assertIn("daysInDestination", result["materialFacts"])
        self.assertEqual("conditional", result["scopes"]["destination"])
        self.assertGreaterEqual(len(result["branches"]), 2)

    def test_unknown_domestic_fact_preserves_treaty_residence_possibilities(self):
        profile = {
            **BASE,
            "treatyPermanentHome": "destination",
        }
        profile.pop("daysInDestination")
        result = run_residence(profile)

        self.assertEqual("conditional", result["status"])
        self.assertEqual(
            {"likely_home_resident", "likely_destination_resident"},
            {branch["status"] for branch in result["branches"]},
        )

    def test_supported_split_year_returns_non_overlapping_periods(self):
        result = run_residence(
            {
                **BASE,
                "daysInDestination": 200,
                "daysInHome": 100,
                "moveDate": "2026-07-01",
            }
        )

        self.assertEqual("likely_destination_resident", result["status"])
        self.assertEqual(
            [
                {
                    "start": "2026-01-01",
                    "end": "2026-06-30",
                    "status": "likely_home_resident",
                    "scopes": {"destination": "source_income", "home": "worldwide_income"},
                },
                {
                    "start": "2026-07-01",
                    "end": "2026-12-31",
                    "status": "likely_destination_resident",
                    "scopes": {"destination": "worldwide_income", "home": "source_income"},
                },
            ],
            result["periods"],
        )
        self.assertIn("synthetic-split-year-2026", result["ruleIds"])

    def test_first_day_move_is_a_full_destination_year_not_an_invalid_split(self):
        result = run_residence(
            {
                **BASE,
                "daysInDestination": 200,
                "daysInHome": 100,
                "moveDate": "2026-01-01",
            }
        )

        self.assertEqual("likely_destination_resident", result["status"])
        self.assertEqual([], result["unresolvedFacts"])
        self.assertEqual(
            [
                {
                    "start": "2026-01-01",
                    "end": "2026-12-31",
                    "status": "likely_destination_resident",
                    "scopes": {"destination": "worldwide_income", "home": "source_income"},
                }
            ],
            result["periods"],
        )

    def test_invalid_move_date_is_unresolved_when_split_year_is_active(self):
        result = run_residence(
            {
                **BASE,
                "daysInDestination": 200,
                "daysInHome": 100,
                "moveDate": "2026-02-30",
                "splitYear": True,
            }
        )

        self.assertEqual("conditional", result["status"])
        self.assertIn("moveDate", result["unresolvedFacts"])

    def test_unsupported_treaty_preserves_possible_dual_residence(self):
        result = run_residence(
            {**BASE, "destinationAvailableHome": True},
            mutate=lambda data: data["destinationRules"]["treatyTieBreaker"].update(
                {"supported": False}
            ),
        )

        self.assertEqual("possible_dual_resident", result["status"])
        self.assertIsNone(result["treatyResidence"])

    def test_result_includes_auditable_explanations_and_is_total_over_invalid_inputs(self):
        valid = run_residence(BASE)
        self.assertTrue(valid["explanations"])
        self.assertTrue(valid["ruleIds"])
        self.assertTrue(valid["sourceIds"])
        for explanation in valid["explanations"]:
            self.assertTrue(explanation["message"])
            self.assertIsInstance(explanation["ruleIds"], list)
            self.assertIsInstance(explanation["sourceIds"], list)

        for invalid in (None, [], "bad", {"daysInDestination": -1}):
            with self.subTest(profile=invalid):
                result = run_residence(invalid)
                self.assertEqual("conditional", result["status"])
                self.assertIsInstance(result["periods"], list)
                self.assertIsInstance(result["scopes"], dict)
                self.assertIsInstance(result["unresolvedFacts"], list)


if __name__ == "__main__":
    unittest.main()
