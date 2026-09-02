from __future__ import annotations

import copy
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE_ENGINE = ROOT / "src" / "fire_tax_profile.js"
RESIDENCE_ENGINE = ROOT / "src" / "fire_tax_residence.js"
FIXTURE = ROOT / "tests" / "fixtures" / "fire_tax_residence.json"


def bundles(mutate=None) -> tuple[dict, dict]:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    destination = copy.deepcopy(fixture["rules"])
    home = copy.deepcopy(fixture["rules"])
    destination["active_jurisdiction_id"] = fixture["destinationId"]
    home["active_jurisdiction_id"] = fixture["homeId"]
    if mutate:
        mutate(destination, home)
    return destination, home


def run_router(profile: object, current_result: object | None = None, mutate=None) -> object:
    destination, home = bundles(mutate)
    script = (
        "const profileApi = require(process.argv[1]);"
        "const residenceApi = require(process.argv[2]);"
        "const input = JSON.parse(process.argv[3]);"
        "const current = input.currentResult || residenceApi.evaluateResidence("
        "input.profile, input.rules.destinationRules, input.rules.homeRules);"
        "process.stdout.write(JSON.stringify(profileApi.nextQuestions("
        "input.profile, input.rules, current)));"
    )
    result = subprocess.run(
        [
            "node",
            "-e",
            script,
            str(PROFILE_ENGINE),
            str(RESIDENCE_ENGINE),
            json.dumps(
                {
                    "profile": profile,
                    "rules": {"destinationRules": destination, "homeRules": home},
                    "currentResult": current_result,
                }
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


COMPLETE_HOME = {
    "taxYear": 2026,
    "daysInDestination": 100,
    "daysInHome": 200,
    "destinationAvailableHome": False,
    "homeAvailableHome": False,
    "familyTies": "neither",
    "economicTies": "neither",
    "splitYear": False,
}


class FireTaxProfileQuestionTests(unittest.TestCase):
    def test_simulation_returns_only_the_unanswered_question_that_changes_result(self):
        profile = dict(COMPLETE_HOME)
        profile.pop("destinationAvailableHome")
        result = run_router(profile)

        self.assertEqual(["fire-tax-destination-home"], [question["id"] for question in result])
        question = result[0]
        self.assertEqual("checkbox", question["control"])
        self.assertEqual([True, False], question["acceptedValues"])
        self.assertEqual(["synthetic-destination-home-2026"], question["affectsRuleIds"])
        self.assertTrue(question["label"])
        self.assertTrue(question["reason"])
        self.assertNotIn("html", question)

    def test_deterministic_simulation_omits_unanswered_fact_with_identical_results(self):
        profile = {
            **COMPLETE_HOME,
            "daysInDestination": 200,
            "treatyPermanentHome": "destination",
        }
        profile.pop("economicTies")

        result = run_router(profile)

        self.assertNotIn("fire-tax-economic-ties", [question["id"] for question in result])

    def test_treaty_questions_follow_validated_rule_order(self):
        profile = {**COMPLETE_HOME, "destinationAvailableHome": True}
        first = run_router(profile)
        self.assertIn("fire-tax-treaty-home", [question["id"] for question in first])
        self.assertNotIn("fire-tax-treaty-centre", [question["id"] for question in first])

        profile["treatyPermanentHome"] = "both"
        second = run_router(profile)
        self.assertNotIn("fire-tax-treaty-home", [question["id"] for question in second])
        self.assertIn("fire-tax-treaty-centre", [question["id"] for question in second])

    def test_move_date_is_asked_only_after_split_year_is_active(self):
        destination_profile = {**COMPLETE_HOME, "daysInDestination": 200, "daysInHome": 100}
        destination_profile.pop("splitYear")
        before = run_router(destination_profile)
        self.assertIn("fire-tax-split-year", [question["id"] for question in before])
        self.assertNotIn("fire-tax-move-date", [question["id"] for question in before])

        destination_profile["splitYear"] = True
        after = run_router(destination_profile)
        self.assertIn("fire-tax-move-date", [question["id"] for question in after])

    def test_malformed_question_or_unresolved_affected_rule_is_omitted(self):
        profile = dict(COMPLETE_HOME)
        profile.pop("destinationAvailableHome")

        def mutate(destination, _home):
            question = destination["jurisdictions"]["synthetic-destination"]["questions"][1]
            question["accepted_values"] = [True]
            question["affects_rule_ids"] = ["missing-rule-2026"]

        self.assertEqual([], run_router(profile, mutate=mutate))

    def test_answered_unknown_is_not_repeated(self):
        profile = {**COMPLETE_HOME, "daysInDestination": 200, "destinationAvailableHome": True}
        profile["treatyPermanentHome"] = "unknown"
        result = run_router(profile)
        self.assertNotIn("fire-tax-treaty-home", [question["id"] for question in result])

    def test_invalid_enum_answer_is_not_treated_as_complete(self):
        profile = {
            **COMPLETE_HOME,
            "daysInDestination": 100,
            "daysInHome": 100,
            "familyTies": "banana",
        }

        result = run_router(profile)

        self.assertIn("fire-tax-family-ties", [question["id"] for question in result])

    def test_invalid_inputs_are_total_and_return_no_questions(self):
        script = (
            "const api = require(process.argv[1]);"
            "const input = JSON.parse(process.argv[2]);"
            "process.stdout.write(JSON.stringify(api.nextQuestions(input.profile, input.rules, input.current)));"
        )
        for payload in (
            {"profile": None, "rules": None, "current": None},
            {"profile": [], "rules": {}, "current": {}},
            {"profile": {}, "rules": {"destinationRules": {}}, "current": {}},
        ):
            result = subprocess.run(
                ["node", "-e", script, str(PROFILE_ENGINE), json.dumps(payload)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual([], json.loads(result.stdout))


if __name__ == "__main__":
    unittest.main()
