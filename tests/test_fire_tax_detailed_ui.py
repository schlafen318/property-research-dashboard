from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from tests.test_fire_tax_detailed import detailed_payload


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src" / "fire_tax_detailed_ui.js"


def run_node(expression: str, payload: dict) -> object:
    script = (
        "const api=require(process.argv[1]);const input=JSON.parse(process.argv[2]);"
        f"process.stdout.write(JSON.stringify({expression}));"
    )
    completed = subprocess.run(
        ["node", "-e", script, str(MODULE), json.dumps(payload)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


class DetailedFireTaxUiTests(unittest.TestCase):
    def test_fully_enabled_destination_home_bundle_runs_end_to_end(self) -> None:
        calculation = detailed_payload()
        payload = {
            "destinationId": "fixture-destination",
            "homeJurisdictionId": "fixture-home",
            "uiPayload": {
                "sources": [],
                "jurisdictions": {
                    "fixture-destination": {
                        "detailed_enabled": True,
                        "synthetic": False,
                        "supported_home_jurisdiction_ids": ["fixture-home"],
                        "runtime_bundles": {
                            "fixture-home": {
                                "profile": calculation["profile"],
                                "rules": calculation["rules"],
                                "questions": [],
                            }
                        },
                    }
                },
            },
            "answers": {},
        }

        result = run_node("api.runRefinement(input)", payload)

        self.assertEqual("calculated", result["result"]["status"])
        self.assertEqual(21_150, result["result"]["totals"]["annualTax"])
        self.assertEqual(1, result["markup"].count("<table"))
        self.assertIn("Refined range", result["markup"])

    def test_access_requires_an_explicit_real_enabled_complete_bundle(self) -> None:
        payload = {
            "jurisdictions": {
                "disabled": {"detailed_enabled": False, "synthetic": False, "runtime_bundle": {}},
                "synthetic": {"detailed_enabled": True, "synthetic": True, "runtime_bundle": {}},
                "missing": {"detailed_enabled": True, "synthetic": False},
                "ready": {"detailed_enabled": True, "synthetic": False, "supported_home_jurisdiction_ids": ["home"], "runtime_bundles": {"home": {"rules": {}}}},
            }
        }

        result = run_node(
            "Object.fromEntries(Object.keys(input.jurisdictions).map(id=>[id,api.jurisdictionAccess(id,input,{homeJurisdictionId:'home'})]))",
            payload,
        )

        self.assertFalse(result["disabled"]["available"])
        self.assertFalse(result["synthetic"]["available"])
        self.assertFalse(result["missing"]["available"])
        self.assertTrue(result["ready"]["available"])

        no_home = run_node("api.jurisdictionAccess('ready',input,{homeJurisdictionId:''})", payload)
        self.assertFalse(no_home["available"])
        self.assertIn("home tax jurisdiction", no_home["reason"])

    def test_question_markup_uses_native_label_help_and_control_contract(self) -> None:
        question = {
            "id": "days-there",
            "fact": "daysThere",
            "control": "number",
            "label": "How many days will you spend there?",
            "reason": "This can change the residence branch.",
            "acceptedValues": {"min": 0, "max": 365, "step": 1, "integer": True},
        }

        markup = run_node("api.questionMarkup(input)", question)

        self.assertIn('<label for="fire-tax-question-days-there">', markup)
        self.assertIn('id="fire-tax-question-days-there"', markup)
        self.assertIn('type="number"', markup)
        self.assertIn('aria-describedby="fire-tax-question-days-there-help"', markup)
        self.assertIn('min="0" max="365" step="1"', markup)

    def test_select_and_radio_questions_keep_native_keyboard_controls_labeled(self) -> None:
        select_question = {
            "id": "ties", "fact": "ties", "control": "select", "label": "Where are your closest ties?",
            "reason": "This controls a branch.", "acceptedValues": ["home", "destination"],
        }
        radio_question = {
            "id": "account", "fact": "account", "control": "radio", "label": "Account type",
            "reason": "This controls a branch.", "acceptedValues": ["pension", "other"],
        }

        select_markup = run_node("api.questionMarkup(input)", select_question)
        radio_markup = run_node("api.questionMarkup(input)", radio_question)

        self.assertIn('for="fire-tax-question-ties"', select_markup)
        self.assertIn('id="fire-tax-question-ties"', select_markup)
        self.assertIn("<fieldset", radio_markup)
        self.assertIn("<legend>Account type</legend>", radio_markup)
        self.assertIn('id="fire-tax-question-account-0"', radio_markup)
        self.assertIn('for="fire-tax-question-account-0"', radio_markup)

    def test_result_markup_has_one_reconciled_table_branch_comparison_and_sources(self) -> None:
        payload = {
            "result": {
                "status": "conditional",
                "currency": "EUR",
                "taxYear": 2026,
                "totals": {
                    "annualTax": {"minimum": 1000, "maximum": 1800},
                    "oneTimeTaxes": 2500,
                    "grossDependableIncome": 30000,
                    "afterTaxDependableIncome": {"minimum": 28200, "maximum": 29000},
                },
                "retirementProjection": {
                    "status": "conditional",
                    "planningRange": {"minimum": 500000, "maximum": 700000},
                    "capitalRange": {"minimum": 540000, "maximum": 610000},
                },
                "scenarios": [
                    {"id": "resident", "totals": {"annualTax": 1800}},
                    {"id": "nonresident", "totals": {"annualTax": 1000}},
                ],
            },
            "audit": [
                {"id": "annual", "label": "Annual tax", "lines": [{
                    "label": "Pension tax", "value": {"minimum": 1000, "maximum": 1800},
                    "formula": "Validated rate bands applied to taxable pension.",
                    "assumptions": ["Residence remains unresolved."], "exclusions": [],
                    "confidence": "high", "ruleIds": ["pension-2026"],
                    "sourceIds": ["official-2026"], "taxYear": 2026,
                }]},
            ],
            "sources": [{"id": "official-2026", "publisher": "Tax authority", "url": "https://tax.example.gov/rule"}],
        }

        markup = run_node("api.resultMarkup(input.result,input.audit,input.sources)", payload)

        self.assertEqual(1, markup.count("<table"))
        self.assertIn("Planning range", markup)
        self.assertIn("Refined range", markup)
        self.assertIn("resident", markup)
        self.assertIn("nonresident", markup)
        self.assertIn("<details", markup)
        self.assertIn('href="https://tax.example.gov/rule"', markup)
        self.assertNotIn('aria-live="polite"', markup)

    def test_controller_keeps_answers_in_memory_and_announces_updates(self) -> None:
        payload = {
            "questions": [{
                "id": "days-there", "fact": "daysThere", "control": "number",
                "label": "Days?", "reason": "Material", "acceptedValues": {"min": 0, "max": 365, "step": 1},
            }]
        }
        expression = "(()=>{const c=api.createController(input);c.answer('daysThere',183);return {state:c.snapshot(),announcement:c.announcement()};})()"

        result = run_node(expression, payload)

        self.assertEqual({"daysThere": 183}, result["state"]["answers"])
        self.assertIn("updated", result["announcement"].lower())
        self.assertNotIn("url", result["state"])
        self.assertNotIn("storage", result["state"])

    def test_controller_rejects_answers_outside_the_active_question_contract(self) -> None:
        payload = {
            "questions": [{
                "id": "days-there", "fact": "daysThere", "control": "number",
                "acceptedValues": {"min": 0, "max": 365, "step": 1, "integer": True},
            }]
        }
        expression = "(()=>{const c=api.createController(input);try{c.answer('daysThere',365.5);return false;}catch(e){return e instanceof TypeError;}})()"

        self.assertTrue(run_node(expression, payload))

    def test_native_control_values_are_typed_before_calculation(self) -> None:
        payload = [
            {"question": {"control": "number"}, "value": "183", "checked": False},
            {"question": {"control": "checkbox"}, "value": "on", "checked": True},
            {"question": {"control": "select"}, "value": "destination", "checked": False},
        ]
        expression = "input.map(x=>api.coerceAnswer(x.question,x.value,x.checked))"

        self.assertEqual([183, True, "destination"], run_node(expression, payload))


if __name__ == "__main__":
    unittest.main()
