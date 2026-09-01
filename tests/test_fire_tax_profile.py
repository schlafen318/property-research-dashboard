from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "fire_tax_profile.js"
FIXTURE = ROOT / "tests" / "fixtures" / "fire_tax_residence.json"


def run_router(payload: object) -> object:
    script = (
        "const api = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        "process.stdout.write(JSON.stringify(api.nextQuestions("
        "input.profile, input.rules, input.currentResult)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(ENGINE), json.dumps(payload)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


class FireTaxProfileQuestionTests(unittest.TestCase):
    def test_returns_only_unanswered_material_native_control_descriptors(self):
        rules = fixture()
        result = run_router(
            {
                "profile": {"daysInDestination": 120},
                "rules": rules,
                "currentResult": {
                    "unresolvedFacts": ["daysInDestination", "destinationAvailableHome", "familyTies"],
                    "materialFacts": ["destinationAvailableHome", "familyTies"],
                    "ruleIds": [
                        "synthetic-destination-home-2026",
                        "synthetic-destination-family-2026",
                    ],
                },
            }
        )

        self.assertEqual(
            ["fire-tax-destination-home", "fire-tax-family-ties"],
            [question["id"] for question in result],
        )
        for question in result:
            with self.subTest(question=question["id"]):
                self.assertIn(question["control"], {"number", "select", "date", "radio", "checkbox"})
                self.assertTrue(question["label"])
                self.assertTrue(question["reason"])
                self.assertTrue(question["acceptedValues"])
                self.assertTrue(question["affectsRuleIds"])
                self.assertNotIn("html", question)

    def test_omits_question_when_every_accepted_answer_has_same_active_result(self):
        rules = fixture()
        result = run_router(
            {
                "profile": {},
                "rules": rules,
                "currentResult": {
                    "unresolvedFacts": ["themePreference"],
                    "materialFacts": ["themePreference"],
                    "ruleIds": ["synthetic-destination-days-2026"],
                },
            }
        )

        self.assertEqual([], result)

    def test_omits_answered_and_inactive_questions(self):
        result = run_router(
            {
                "profile": {"familyTies": "home"},
                "rules": fixture(),
                "currentResult": {
                    "unresolvedFacts": ["familyTies", "economicTies"],
                    "materialFacts": ["familyTies"],
                    "ruleIds": ["synthetic-home-family-2026"],
                },
            }
        )

        self.assertEqual([], result)

    def test_invalid_inputs_are_total_and_return_no_questions(self):
        for profile, rules, current in (
            (None, None, None),
            ([], fixture(), {}),
            ({}, {"questions": "bad"}, {"materialFacts": []}),
        ):
            with self.subTest(profile=profile, rules=rules, current=current):
                self.assertEqual(
                    [],
                    run_router({"profile": profile, "rules": rules, "currentResult": current}),
                )


if __name__ == "__main__":
    unittest.main()
