from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


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
            {"category": "dividends", "status": "calculated", "currency": "EUR", "domesticTax": 100, "sourceWithholding": 300, "netTax": 400, "ruleIds": ["dividend-rule-2026"], "sourceIds": ["source-2026"]},
            {"category": "interest", "status": "calculated", "currency": "EUR", "domesticTax": 500, "sourceWithholding": 0, "netTax": 500, "ruleIds": ["interest-rule-2026"], "sourceIds": ["source-2026"]},
        ]
        result = run_credit(results, credit_rules())
        categories = {item["category"]: item for item in result["categories"]}
        self.assertEqual(100, categories["dividends"]["creditApplied"])
        self.assertEqual(500, categories["interest"]["netTax"])
        self.assertEqual(200, result["unusedCredits"][0]["amount"])

    def test_unsupported_foreign_tax_is_preserved_as_an_explanation(self):
        results = [
            {"category": "government_pension", "status": "calculated", "currency": "EUR", "domesticTax": 100, "sourceWithholding": 40, "netTax": 140, "ruleIds": ["pension-rule-2026"], "sourceIds": ["source-2026"]}
        ]
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

    def test_conditional_ranges_are_preserved_for_later_branch_composition(self):
        results = [{
            "category": "dividends", "status": "conditional", "currency": "EUR",
            "domesticTax": {"minimum": 0, "maximum": 100},
            "sourceWithholding": {"minimum": 0, "maximum": 50},
            "netTax": {"minimum": 0, "maximum": 150},
            "branches": [
                {"status": "out_of_scope", "domesticTax": None, "sourceWithholding": None, "netTax": None},
                {"status": "calculated", "domesticTax": 100, "sourceWithholding": 50, "netTax": 150},
            ],
            "ruleIds": ["dividend-rule-2026"], "sourceIds": ["source-2026"]
        }]
        result = run_credit(results, credit_rules())
        category = result["categories"][0]
        self.assertEqual("conditional", category["status"])
        self.assertEqual({"minimum": 0, "maximum": 50}, category["creditApplied"])
        self.assertEqual({"minimum": 0, "maximum": 100}, category["netTax"])

    def test_malformed_results_or_credit_rules_are_total_errors(self):
        malformed = [
            ([{"category": "dividends", "status": "calculated", "currency": "EUR", "domesticTax": -1, "sourceWithholding": 0, "netTax": -1}], credit_rules()),
            ([], [{**credit_rules()[0], "applies_to_categories": []}]),
            ([], [{**credit_rules()[0], "order": 0}]),
            ([], [{**credit_rules()[0], "credit_operand": "missing_operand"}]),
            (
                [{"category": "dividends", "status": "calculated", "currency": "USD", "domesticTax": 1, "sourceWithholding": 0, "netTax": 1}],
                credit_rules(),
            ),
        ]
        for results, rules in malformed:
            with self.subTest(results=results, rules=rules):
                response = run_credit(results, rules, expect_error=True)
                self.assertEqual("FireTaxCreditInputError", response["error"])


if __name__ == "__main__":
    unittest.main()
