from __future__ import annotations

import copy
import json
import subprocess
import unittest
from datetime import date
from pathlib import Path

from src.fire_tax_rules import validate_fire_tax_rules


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "fire_tax_income.js"
FIXTURE = ROOT / "tests" / "fixtures" / "fire_tax_income.json"


def fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def calculate(profile=None, residence=None, rules=None, expect_error=False):
    data = fixture()
    payload = {
        "profile": data["profile"] if profile is None else profile,
        "residence": data["residence"] if residence is None else residence,
        "rules": data["rules"] if rules is None else rules,
    }
    script = (
        "const api=require(process.argv[1]);const input=JSON.parse(process.argv[2]);"
        "try{process.stdout.write(JSON.stringify({value:api.calculateIncomeTax(input.profile,input.residence,input.rules)}));}"
        "catch(error){process.stdout.write(JSON.stringify({error:error.name,message:error.message}));}"
    )
    completed = subprocess.run(
        ["node", "-e", script, str(ENGINE), json.dumps(payload)],
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


def by_category(results: list[dict]) -> dict[str, dict]:
    return {result["category"]: result for result in results}


class FireTaxIncomeTests(unittest.TestCase):
    def test_fixture_is_a_valid_task_one_rule_graph(self):
        self.assertEqual(
            [],
            validate_fire_tax_rules(fixture()["rules"], as_of=date(2026, 9, 1)),
        )

    def test_calculates_every_supported_fire_income_category(self):
        results = by_category(calculate())
        self.assertEqual(
            {
                "private_pension",
                "government_pension",
                "social_security",
                "dividends",
                "interest",
                "realized_gains",
                "retirement_account_withdrawal",
                "rental_income",
                "employment_consulting",
            },
            set(results),
        )
        self.assertEqual(1200, results["private_pension"]["domesticTax"])
        self.assertEqual(600, results["government_pension"]["domesticTax"])
        self.assertEqual(0, results["social_security"]["domesticTax"])
        self.assertTrue(results["social_security"]["exempt"])
        self.assertEqual(10000, results["realized_gains"]["taxableBase"])
        self.assertEqual(1800, results["realized_gains"]["domesticTax"])
        self.assertEqual(2000, results["retirement_account_withdrawal"]["domesticTax"])
        self.assertEqual(2000, results["employment_consulting"]["domesticTax"])

    def test_allowances_reduce_taxable_base_and_progressive_boundary_is_exact(self):
        data = fixture()
        for gross, expected_tax in ((11000, 1000), (11001, 1000.2), (500, 0)):
            profile = {**data["profile"], "privatePension": gross}
            with self.subTest(gross=gross):
                result = by_category(calculate(profile=profile))["private_pension"]
                self.assertEqual(min(gross, 1000), result["deductions"])
                self.assertEqual(max(gross - 1000, 0), result["taxableBase"])
                self.assertAlmostEqual(expected_tax, result["domesticTax"], places=8)

    def test_source_withholding_and_pre_credit_net_tax_remain_separate(self):
        results = by_category(calculate())
        dividend = results["dividends"]
        self.assertEqual(5000, dividend["grossIncome"])
        self.assertEqual(500, dividend["deductions"])
        self.assertEqual(4500, dividend["taxableBase"])
        self.assertEqual(900, dividend["domesticTax"])
        self.assertEqual(750, dividend["sourceWithholding"])
        self.assertEqual(1650, dividend["netTax"])
        self.assertEqual(600, results["rental_income"]["sourceWithholding"])

    def test_unsupported_retirement_account_classification_is_rejected(self):
        data = fixture()
        profile = {
            **data["profile"],
            "retirementAccountClassification": "unsupported_offshore",
        }
        result = calculate(profile=profile, expect_error=True)
        self.assertEqual("FireTaxIncomeInputError", result["error"])
        self.assertIn("retirementAccountClassification", result["message"])
        self.assertIn("unsupported", result["message"])

    def test_nonresident_source_scope_excludes_nonlocal_income_without_zero_tax_claim(self):
        data = fixture()
        residence = {
            "status": "likely_home_resident",
            "scopes": {"destination": "source_income", "home": "worldwide_income"},
            "unresolvedFacts": [],
        }
        results = by_category(calculate(residence=residence))
        dividend = results["dividends"]
        self.assertEqual("out_of_scope", dividend["status"])
        self.assertEqual(5000, dividend["grossIncome"])
        self.assertIsNone(dividend["taxableBase"])
        self.assertIsNone(dividend["domesticTax"])
        self.assertIn("income source", dividend["explanations"][0].lower())
        self.assertEqual("calculated", results["employment_consulting"]["status"])

    def test_conditional_residence_returns_calculated_ranges_not_a_guessed_status(self):
        residence = {
            "status": "conditional",
            "scopes": {"destination": "conditional", "home": "conditional"},
            "unresolvedFacts": ["daysInDestination"],
            "branches": [
                {"status": "likely_home_resident", "scopes": {"destination": "source_income", "home": "worldwide_income"}, "assumedValue": 100},
                {"status": "likely_destination_resident", "scopes": {"destination": "worldwide_income", "home": "source_income"}, "assumedValue": 200},
            ],
        }
        result = by_category(calculate(residence=residence))["dividends"]
        self.assertEqual("conditional", result["status"])
        self.assertEqual({"minimum": 5000, "maximum": 5000}, result["grossIncome"])
        self.assertEqual({"minimum": 0, "maximum": 900}, result["domesticTax"])
        self.assertEqual(2, len(result["branches"]))
        self.assertEqual(["daysInDestination"], result["unresolvedFacts"])

    def test_split_year_without_income_timing_returns_a_conservative_scope_range(self):
        residence = {
            "status": "likely_destination_resident",
            "scopes": {"destination": "worldwide_income", "home": "source_income"},
            "unresolvedFacts": [],
            "periods": [
                {"start": "2026-01-01", "end": "2026-06-30", "status": "likely_home_resident", "scopes": {"destination": "source_income", "home": "worldwide_income"}},
                {"start": "2026-07-01", "end": "2026-12-31", "status": "likely_destination_resident", "scopes": {"destination": "worldwide_income", "home": "source_income"}},
            ],
        }
        result = by_category(calculate(residence=residence))["dividends"]
        self.assertEqual("conditional", result["status"])
        self.assertEqual({"minimum": 0, "maximum": 900}, result["domesticTax"])
        self.assertEqual(
            ["incomeTimingAcrossResidencePeriods"], result["unresolvedFacts"]
        )
        self.assertIn("timing", result["explanations"][0].lower())

    def test_invalid_profile_is_a_total_error_instead_of_a_partial_estimate(self):
        data = fixture()
        invalid_profiles = (
            {**data["profile"], "dividends": -1},
            {**data["profile"], "interest": "2000"},
            {**data["profile"], "rentalIncome": True},
            {**data["profile"], "currency": "USD"},
        )
        for profile in invalid_profiles:
            with self.subTest(profile=profile):
                result = calculate(profile=profile, expect_error=True)
                self.assertEqual("FireTaxIncomeInputError", result["error"])

    def test_each_calculated_amount_has_rule_source_formula_and_scope_audit(self):
        result = by_category(calculate())["private_pension"]
        self.assertEqual(2026, result["taxYear"])
        self.assertEqual("EUR", result["currency"])
        self.assertEqual("resident", result["taxpayerScope"])
        self.assertEqual("high", result["confidence"])
        self.assertEqual(
            ["synthetic-private-pension-2026", "synthetic-private-pension-allowance-2026"],
            result["ruleIds"],
        )
        self.assertEqual(["synthetic-income-authority-2026"], result["sourceIds"])
        self.assertIn("progressive", result["formula"])
        self.assertIn("allowance", result["formula"])
        self.assertTrue(result["assumptions"])

    def test_malformed_or_unvalidated_rule_projection_is_rejected(self):
        data = fixture()
        rules = copy.deepcopy(data["rules"])
        rules["jurisdictions"]["synthetic-destination"]["rules"][0]["bands"][1]["from"] = 9000
        result = calculate(rules=rules, expect_error=True)
        self.assertEqual("FireTaxIncomeRuleError", result["error"])
        self.assertIn("bands", result["message"])


if __name__ == "__main__":
    unittest.main()
