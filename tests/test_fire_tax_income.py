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
RESIDENCE_ENGINE = ROOT / "src" / "fire_tax_residence.js"
FIXTURE = ROOT / "tests" / "fixtures" / "fire_tax_income.json"
RESIDENCE_FIXTURE = ROOT / "tests" / "fixtures" / "fire_tax_residence.json"


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


def rule_by_id(rules: dict, rule_id: str) -> dict:
    return next(
        rule
        for rule in rules["jurisdictions"]["synthetic-destination"]["rules"]
        if rule["id"] == rule_id
    )


def calculate_with_task_two_unknown_split() -> list[dict]:
    income = fixture()
    residence_data = json.loads(RESIDENCE_FIXTURE.read_text(encoding="utf-8"))
    destination = copy.deepcopy(residence_data["rules"])
    home = copy.deepcopy(residence_data["rules"])
    destination["active_jurisdiction_id"] = residence_data["destinationId"]
    home["active_jurisdiction_id"] = residence_data["homeId"]
    residence_profile = {
        "taxYear": 2026,
        "daysInDestination": 200,
        "destinationAvailableHome": False,
        "daysInHome": 100,
        "homeAvailableHome": False,
        "familyTies": "neither",
        "economicTies": "neither",
        "moveDate": "2026-07-01",
    }
    script = (
        "const residenceApi=require(process.argv[1]);"
        "const incomeApi=require(process.argv[2]);"
        "const input=JSON.parse(process.argv[3]);"
        "const residence=residenceApi.evaluateResidence(input.residenceProfile,input.destination,input.home);"
        "process.stdout.write(JSON.stringify({residence:residence,value:incomeApi.calculateIncomeTax(input.profile,residence,input.incomeRules)}));"
    )
    completed = subprocess.run(
        [
            "node",
            "-e",
            script,
            str(RESIDENCE_ENGINE),
            str(ENGINE),
            json.dumps(
                {
                    "residenceProfile": residence_profile,
                    "destination": destination,
                    "home": home,
                    "profile": income["profile"],
                    "incomeRules": income["rules"],
                }
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


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

    def test_selects_one_rate_and_accessory_set_for_the_active_taxpayer_scope(self):
        data = fixture()
        rules = copy.deepcopy(data["rules"])
        jurisdiction_rules = rules["jurisdictions"]["synthetic-destination"]["rules"]
        resident_rate = rule_by_id(rules, "synthetic-private-pension-2026")
        resident_rate["taxpayer_scope"] = ["resident"]
        nonresident_rate = copy.deepcopy(resident_rate)
        nonresident_rate.update(
            {
                "id": "synthetic-private-pension-nonresident-2026",
                "taxpayer_scope": ["nonresident"],
                "bands": [{"from": 0, "up_to": None, "rate": 0.5}],
            }
        )
        resident_allowance = rule_by_id(
            rules, "synthetic-private-pension-allowance-2026"
        )
        resident_allowance["taxpayer_scope"] = ["resident"]
        rules["operand_catalog"]["nonresident_pension_allowance"] = {
            "kind": "constant",
            "value_type": "money",
            "currency": "EUR",
            "value": 2000,
        }
        nonresident_allowance = copy.deepcopy(resident_allowance)
        nonresident_allowance.update(
            {
                "id": "synthetic-private-pension-nonresident-allowance-2026",
                "taxpayer_scope": ["nonresident"],
                "formula": {
                    "operation": "minimum",
                    "operands": ["private_pension", "nonresident_pension_allowance"],
                },
                "amount": 2000,
                "amount_operand": "nonresident_pension_allowance",
            }
        )
        jurisdiction_rules.extend([nonresident_rate, nonresident_allowance])

        resident = by_category(calculate(rules=rules))["private_pension"]
        self.assertEqual(1200, resident["domesticTax"])
        self.assertEqual(
            ["synthetic-private-pension-2026", "synthetic-private-pension-allowance-2026"],
            resident["ruleIds"],
        )

        profile = copy.deepcopy(data["profile"])
        profile["incomeSourceJurisdictions"]["private_pension"] = (
            "synthetic-destination"
        )
        nonresident = by_category(
            calculate(
                profile=profile,
                residence={
                    "status": "likely_home_resident",
                    "scopes": {
                        "destination": "source_income",
                        "home": "worldwide_income",
                    },
                },
                rules=rules,
            )
        )["private_pension"]
        self.assertEqual(2000, nonresident["deductions"])
        self.assertEqual(5000, nonresident["domesticTax"])
        self.assertEqual(
            [
                "synthetic-private-pension-nonresident-2026",
                "synthetic-private-pension-nonresident-allowance-2026",
            ],
            nonresident["ruleIds"],
        )

    def test_rejects_only_true_same_scope_rate_ambiguity(self):
        data = fixture()
        rules = copy.deepcopy(data["rules"])
        duplicate = copy.deepcopy(rule_by_id(rules, "synthetic-private-pension-2026"))
        duplicate["id"] = "synthetic-private-pension-duplicate-2026"
        rules["jurisdictions"]["synthetic-destination"]["rules"].append(duplicate)
        result = calculate(rules=rules, expect_error=True)
        self.assertEqual("FireTaxIncomeRuleError", result["error"])
        self.assertIn("multiple resident rate rules", result["message"])

    def test_withholding_accessories_are_filtered_to_the_active_scope(self):
        data = fixture()
        rules = copy.deepcopy(data["rules"])
        resident = rule_by_id(rules, "synthetic-dividend-withholding-2026")
        resident["taxpayer_scope"] = ["resident"]
        rules["operand_catalog"]["nonresident_dividend_withholding_rate"] = {
            "kind": "constant",
            "value_type": "number",
            "value": 0.4,
        }
        nonresident = copy.deepcopy(resident)
        nonresident.update(
            {
                "id": "synthetic-dividend-nonresident-withholding-2026",
                "taxpayer_scope": ["nonresident"],
                "formula": {
                    "operation": "multiply",
                    "operands": [
                        "dividends",
                        "nonresident_dividend_withholding_rate",
                    ],
                },
                "rate": 0.4,
                "rate_operand": "nonresident_dividend_withholding_rate",
            }
        )
        rules["jurisdictions"]["synthetic-destination"]["rules"].append(
            nonresident
        )
        profile = copy.deepcopy(data["profile"])
        profile["incomeSourceJurisdictions"]["dividends"] = "synthetic-destination"
        result = by_category(
            calculate(
                profile=profile,
                residence={
                    "status": "likely_home_resident",
                    "scopes": {
                        "destination": "source_income",
                        "home": "worldwide_income",
                    },
                },
                rules=rules,
            )
        )["dividends"]
        self.assertEqual(2000, result["sourceWithholding"])
        self.assertIn(
            "synthetic-dividend-nonresident-withholding-2026", result["ruleIds"]
        )
        self.assertNotIn("synthetic-dividend-withholding-2026", result["ruleIds"])

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

    def test_task_two_unknown_split_keeps_nested_period_alternative_material(self):
        integration = calculate_with_task_two_unknown_split()
        self.assertEqual("conditional", integration["residence"]["status"])
        self.assertEqual("splitYear", integration["residence"]["controllingFact"])
        dividend = by_category(integration["value"])["dividends"]
        self.assertEqual({"minimum": 0, "maximum": 900}, dividend["domesticTax"])
        split_branch = next(
            branch for branch in dividend["branches"] if branch["assumedValue"] is True
        )
        self.assertEqual("conditional", split_branch["status"])
        self.assertEqual(
            ["incomeTimingAcrossResidencePeriods"], split_branch["unresolvedFacts"]
        )

    def test_no_tax_rule_cannot_report_exempt_with_positive_tax(self):
        data = fixture()
        rules = copy.deepcopy(data["rules"])
        social = rule_by_id(rules, "synthetic-social-security-exemption-2026")
        social["bands"][0]["rate"] = 0.1
        result = calculate(rules=rules, expect_error=True)
        self.assertEqual("FireTaxIncomeRuleError", result["error"])
        self.assertIn("no_tax", result["message"])

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
