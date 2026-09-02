from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from tests.test_fire_tax_income import calculate_with_task_two_unknown_split


ROOT = Path(__file__).resolve().parents[1]
INCOME_ENGINE = ROOT / "src" / "fire_tax_income.js"
CREDIT_ENGINE = ROOT / "src" / "fire_tax_credits.js"
FIXTURE = ROOT / "tests" / "fixtures" / "fire_tax_income.json"


def fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def run_credit(category_results, credit_rules, expect_error=False):
    script = (
        "const api=require(process.argv[1]);const input=JSON.parse(process.argv[2]);"
        "try{process.stdout.write(JSON.stringify({value:api.applyForeignTaxCredits(input.results,input.rules)}));}"
        "catch(error){process.stdout.write(JSON.stringify({error:error.name,message:error.message}));}"
    )
    completed = subprocess.run(
        ["node", "-e", script, str(CREDIT_ENGINE), json.dumps({"results": category_results, "rules": credit_rules})],
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    if expect_error:
        return result
    if "error" in result:
        raise AssertionError(result)
    return result["value"]


def calculated_results():
    data = fixture()
    script = (
        "const api=require(process.argv[1]);const input=JSON.parse(process.argv[2]);"
        "process.stdout.write(JSON.stringify(api.calculateIncomeTax(input.profile,input.residence,input.rules)));"
    )
    completed = subprocess.run(
        ["node", "-e", script, str(INCOME_ENGINE), json.dumps(data)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def credit_rules():
    data = fixture()
    return [
        rule
        for rule in data["rules"]["jurisdictions"]["synthetic-destination"]["rules"]
        if rule["type"] == "credit_limit"
    ]


def category_result(
    category,
    domestic_tax,
    source_withholding,
    *,
    status="calculated",
    tax_year=2026,
    taxpayer_scope="resident",
    confidence="high",
):
    return {
        "category": category,
        "status": status,
        "currency": "EUR",
        "taxYear": tax_year,
        "taxpayerScope": taxpayer_scope,
        "confidence": confidence,
        "assumptions": ["Synthetic income-result assumption."],
        "explanations": ["Synthetic income-result explanation."],
        "domesticTax": domestic_tax,
        "sourceWithholding": source_withholding,
        "netTax": domestic_tax + source_withholding,
        "ruleIds": [f"{category}-rule-{tax_year}"],
        "sourceIds": [f"{category}-source-{tax_year}"],
    }


class FireTaxCreditTests(unittest.TestCase):
    def test_credit_is_category_matched_and_capped_at_domestic_tax(self):
        result = run_credit(calculated_results(), credit_rules())
        categories = {item["category"]: item for item in result["categories"]}
        dividend = categories["dividends"]
        self.assertEqual(750, dividend["creditApplied"])
        self.assertEqual(900, dividend["domesticTax"])
        self.assertEqual(750, dividend["sourceWithholding"])
        self.assertEqual(900, dividend["netTax"])
        rental = categories["rental_income"]
        self.assertEqual(600, rental["creditApplied"])
        self.assertEqual(1200, rental["netTax"])

    def test_credit_does_not_spill_into_another_category(self):
        results = [
            category_result("dividends", 100, 300),
            category_result("interest", 500, 0),
        ]
        result = run_credit(results, credit_rules())
        categories = {item["category"]: item for item in result["categories"]}
        self.assertEqual(100, categories["dividends"]["creditApplied"])
        self.assertEqual(500, categories["interest"]["netTax"])
        self.assertEqual(200, result["unusedCredits"][0]["amount"])

    def test_unsupported_foreign_tax_is_preserved_as_an_explanation(self):
        results = [category_result("government_pension", 100, 40)]
        result = run_credit(results, credit_rules())
        self.assertEqual(0, result["totalCreditsApplied"])
        self.assertEqual(140, result["totalNetTax"])
        self.assertEqual("government_pension", result["unsupportedCredits"][0]["category"])
        self.assertEqual(40, result["unsupportedCredits"][0]["amount"])
        self.assertIn("no validated matching", result["unsupportedCredits"][0]["explanation"])

    def test_totals_reconcile_and_credit_never_makes_tax_negative(self):
        result = run_credit(calculated_results(), credit_rules())
        self.assertEqual(
            result["totalDomesticTax"] + result["totalSourceWithholding"] - result["totalCreditsApplied"],
            result["totalNetTax"],
        )
        self.assertGreaterEqual(result["totalNetTax"], 0)
        self.assertTrue(all(item["netTax"] >= 0 for item in result["categories"] if item["status"] == "calculated"))

    def test_credit_audit_identifies_ordered_rule_and_sources(self):
        result = run_credit(calculated_results(), credit_rules())
        dividend = next(item for item in result["categories"] if item["category"] == "dividends")
        self.assertEqual(["synthetic-category-credit-2026"], dividend["creditRuleIds"])
        self.assertEqual(["synthetic-income-authority-2026"], dividend["creditSourceIds"])
        self.assertIn("minimum", dividend["creditFormula"])
        self.assertIn(
            "Source withholding is creditable",
            " ".join(dividend["creditAssumptions"]),
        )
        self.assertTrue(dividend["creditExplanations"])

    def test_conditional_ranges_are_preserved_for_later_branch_composition(self):
        results = [{
            "category": "dividends", "status": "conditional", "currency": "EUR",
            "taxYear": 2026, "taxpayerScope": "conditional", "confidence": "high",
            "assumptions": ["Synthetic conditional assumption."],
            "explanations": ["Synthetic conditional explanation."],
            "domesticTax": {"minimum": 0, "maximum": 100},
            "sourceWithholding": {"minimum": 0, "maximum": 50},
            "netTax": {"minimum": 0, "maximum": 150},
            "branches": [
                {"status": "out_of_scope", "taxpayerScope": "nonresident", "domesticTax": None, "sourceWithholding": None, "netTax": None},
                {"status": "calculated", "taxpayerScope": "resident", "domesticTax": 100, "sourceWithholding": 50, "netTax": 150},
            ],
            "ruleIds": ["dividend-rule-2026"], "sourceIds": ["source-2026"]
        }]
        result = run_credit(results, credit_rules())
        category = result["categories"][0]
        self.assertEqual("conditional", category["status"])
        self.assertEqual({"minimum": 0, "maximum": 50}, category["creditApplied"])
        self.assertEqual({"minimum": 0, "maximum": 100}, category["netTax"])

    def test_conditional_unused_and_unsupported_tax_keep_branch_audit(self):
        base = {
            "status": "conditional",
            "currency": "EUR",
            "taxYear": 2026,
            "taxpayerScope": "conditional",
            "confidence": "high",
            "assumptions": ["Synthetic conditional assumption."],
            "explanations": ["Synthetic conditional explanation."],
            "domesticTax": {"minimum": 0, "maximum": 100},
            "sourceWithholding": {"minimum": 0, "maximum": 150},
            "netTax": {"minimum": 0, "maximum": 250},
            "branches": [
                {"status": "out_of_scope", "taxpayerScope": "nonresident", "domesticTax": None, "sourceWithholding": None, "netTax": None, "assumedValue": 100},
                {"status": "calculated", "taxpayerScope": "resident", "domesticTax": 100, "sourceWithholding": 150, "netTax": 250, "assumedValue": 200},
            ],
            "ruleIds": ["synthetic-income-rule-2026"],
            "sourceIds": ["synthetic-income-source-2026"],
        }
        supported = run_credit([{**base, "category": "dividends"}], credit_rules())
        note = supported["unusedCredits"][0]
        self.assertEqual({"minimum": 0, "maximum": 50}, note["amount"])
        self.assertEqual([100, 200], [branch["assumedValue"] for branch in note["branches"]])

        unsupported = run_credit(
            [{**base, "category": "government_pension"}], credit_rules()
        )
        note = unsupported["unsupportedCredits"][0]
        self.assertEqual({"minimum": 0, "maximum": 150}, note["amount"])
        self.assertEqual(2, len(note["branches"]))

    def test_conditional_aggregates_are_recomputed_and_inconsistency_is_rejected(self):
        result = {
            "category": "dividends", "status": "conditional", "currency": "EUR",
            "taxYear": 2026, "taxpayerScope": "conditional", "confidence": "high",
            "assumptions": ["Synthetic conditional assumption."],
            "explanations": ["Synthetic conditional explanation."],
            "domesticTax": {"minimum": 0, "maximum": 999},
            "sourceWithholding": {"minimum": 0, "maximum": 50},
            "netTax": {"minimum": 0, "maximum": 150},
            "branches": [
                {"status": "out_of_scope", "taxpayerScope": "nonresident", "domesticTax": None, "sourceWithholding": None, "netTax": None},
                {"status": "calculated", "taxpayerScope": "resident", "domesticTax": 100, "sourceWithholding": 50, "netTax": 150},
            ],
            "ruleIds": ["dividend-rule-2026"], "sourceIds": ["source-2026"],
        }
        response = run_credit([result], credit_rules(), expect_error=True)
        self.assertEqual("FireTaxCreditInputError", response["error"])
        self.assertIn("domesticTax", response["message"])

        result["domesticTax"] = {"minimum": 0, "maximum": 100}
        result["branches"][0]["domesticTax"] = 999
        response = run_credit([result], credit_rules(), expect_error=True)
        self.assertEqual("FireTaxCreditInputError", response["error"])
        self.assertIn("out_of_scope", response["message"])

    def test_credit_rules_filter_by_tax_year_and_taxpayer_scope(self):
        dividend = category_result("dividends", 100, 50)
        inapplicable = {**credit_rules()[0], "id": "synthetic-category-credit-2025", "tax_year": 2025}
        result = run_credit([dividend], [inapplicable])
        self.assertEqual(0, result["totalCreditsApplied"])
        self.assertEqual(50, result["unsupportedCredits"][0]["amount"])

        nonresident_only = {
            **credit_rules()[0],
            "taxpayer_scope": ["nonresident"],
        }
        result = run_credit([dividend], [nonresident_only])
        self.assertEqual(0, result["totalCreditsApplied"])

    def test_credit_audit_uses_lowest_applicable_confidence(self):
        low_credit = {
            **credit_rules()[0],
            "confidence": "low",
            "assumptions": ["Low-confidence synthetic credit assumption."],
            "explanation": "Low-confidence synthetic credit explanation.",
        }
        result = run_credit(
            [category_result("dividends", 100, 50, confidence="medium_high")],
            [low_credit],
        )
        category = result["categories"][0]
        self.assertEqual("low", category["confidence"])
        self.assertEqual("low", result["confidence"])
        self.assertIn("Low-confidence synthetic credit assumption.", category["assumptions"])
        self.assertIn("Low-confidence synthetic credit explanation.", category["creditExplanations"])

    def test_task_two_nested_split_ranges_remain_valid_through_credits(self):
        income_results = calculate_with_task_two_unknown_split()["value"]
        result = run_credit(income_results, credit_rules())
        dividend = next(
            category
            for category in result["categories"]
            if category["category"] == "dividends"
        )
        self.assertEqual({"minimum": 0, "maximum": 750}, dividend["creditApplied"])
        self.assertEqual({"minimum": 0, "maximum": 900}, dividend["netTax"])
        split_branch = next(
            branch for branch in dividend["branches"] if branch["assumedValue"] is True
        )
        self.assertEqual("conditional", split_branch["status"])
        self.assertEqual({"minimum": 0, "maximum": 750}, split_branch["creditApplied"])

    def test_malformed_results_or_credit_rules_are_total_errors(self):
        malformed = [
            ([{**category_result("dividends", 1, 0), "domesticTax": -1, "netTax": -1}], credit_rules()),
            ([], [{**credit_rules()[0], "applies_to_categories": []}]),
            ([], [{**credit_rules()[0], "order": 0}]),
            ([], [{**credit_rules()[0], "credit_operand": "missing_operand"}]),
            (
                [{**category_result("dividends", 1, 0), "currency": "USD"}],
                credit_rules(),
            ),
            ([], [{**credit_rules()[0], "tax_year": "2026"}]),
            ([], [{**credit_rules()[0], "taxpayer_scope": []}]),
            ([], [{**credit_rules()[0], "confidence": "certain"}]),
            ([], [{**credit_rules()[0], "assumptions": []}]),
            ([], [{**credit_rules()[0], "explanation": ""}]),
        ]
        for results, rules in malformed:
            with self.subTest(results=results, rules=rules):
                response = run_credit(results, rules, expect_error=True)
                self.assertEqual("FireTaxCreditInputError", response["error"])


if __name__ == "__main__":
    unittest.main()
