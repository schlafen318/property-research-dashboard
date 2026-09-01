import copy
import json
import subprocess
import unittest
from datetime import date
from pathlib import Path

from src.fire_tax_rules import validate_fire_tax_rules


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "fire_tax_property.json"
MODULE_PATH = ROOT / "src" / "fire_tax_property.js"


def fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def calculate(profile=None, residence=None, rules=None, expect_error=False):
    data = fixture()
    payload = {
        "profile": data["profile"] if profile is None else profile,
        "residence": data["residence"] if residence is None else residence,
        "rules": data["rules"] if rules is None else rules,
    }
    script = """
const engine = require(process.argv[1]);
const payload = JSON.parse(process.argv[2]);
try {
  const result = engine.calculatePropertyTaxes(payload.profile, payload.residence, payload.rules);
  process.stdout.write(JSON.stringify({ok: true, result}));
} catch (error) {
  process.stdout.write(JSON.stringify({ok: false, error: error.name, message: error.message}));
}
"""
    completed = subprocess.run(
        ["node", "-e", script, str(MODULE_PATH), json.dumps(payload)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    response = json.loads(completed.stdout)
    if expect_error:
        return response
    if not response["ok"]:
        raise AssertionError(response)
    return response["result"]


class FireTaxPropertyTests(unittest.TestCase):
    def test_fixture_passes_the_shared_rule_validator(self):
        errors = validate_fire_tax_rules(fixture()["rules"], date(2026, 9, 1))
        self.assertEqual([], errors)

    def test_full_lifecycle_keeps_tax_costs_and_prepayments_separate(self):
        result = calculate()
        self.assertEqual("calculated", result["status"])
        self.assertEqual(20000, result["stages"]["purchase"]["taxTotal"])
        self.assertEqual(1400, result["stages"]["purchase"]["nonTaxTotal"])
        self.assertEqual(2250, result["stages"]["annual"]["taxTotal"])
        self.assertEqual(250, result["stages"]["annual"]["nonTaxTotal"])
        self.assertEqual(5000, result["stages"]["rental"]["taxTotal"])
        self.assertEqual(3000, result["stages"]["rental"]["prepaymentTotal"])
        self.assertEqual(22000, result["stages"]["sale"]["taxTotal"])
        self.assertEqual(9000, result["stages"]["sale"]["prepaymentTotal"])
        self.assertEqual(15000, result["stages"]["inheritance"]["taxTotal"])
        self.assertEqual(64250, result["totals"]["allTax"])
        self.assertEqual(12000, result["totals"]["prepayments"])
        self.assertEqual(1650, result["totals"]["nonTax"])

    def test_annual_rules_cover_imputed_income_vacancy_and_compliance(self):
        data = fixture()
        profile = {**data["profile"], "activeStages": ["annual"], "propertyUse": "vacant"}
        result = calculate(profile=profile)
        annual = result["stages"]["annual"]
        self.assertEqual(6050, annual["taxTotal"])
        self.assertEqual(250, annual["nonTaxTotal"])
        self.assertEqual(
            ["property_tax", "wealth_tax", "imputed_income_tax", "vacancy_tax", "tax_compliance_charge"],
            [line["chargeKind"] for line in annual["lines"]],
        )

    def test_rental_deductions_do_not_turn_a_loss_into_negative_tax(self):
        data = fixture()
        profile = {
            **data["profile"],
            "activeStages": ["rental"],
            "annualRent": 5000,
            "deductibleExpenses": 7000,
        }
        result = calculate(profile=profile)
        self.assertEqual(0, result["stages"]["rental"]["taxTotal"])
        self.assertEqual(500, result["stages"]["rental"]["prepaymentTotal"])

    def test_sale_loss_is_floored_while_withholding_remains_visible(self):
        data = fixture()
        profile = {
            **data["profile"],
            "activeStages": ["sale"],
            "salePrice": 300000,
            "holdingPeriodYears": 8,
        }
        result = calculate(profile=profile)
        self.assertEqual(0, result["stages"]["sale"]["taxTotal"])
        self.assertEqual(4500, result["stages"]["sale"]["prepaymentTotal"])

    def test_unknown_assessment_returns_supported_branches_not_zero(self):
        data = fixture()
        profile = {
            **data["profile"],
            "activeStages": ["annual"],
            "propertyUse": "personal",
            "officialAssessmentBase": "unknown",
        }
        result = calculate(profile=profile)
        self.assertEqual("conditional", result["status"])
        self.assertEqual(["officialAssessmentBase"], result["unresolvedFacts"])
        self.assertEqual({"minimum": 3750, "maximum": 6000}, result["totals"]["annualTax"])
        self.assertEqual(2, len(result["branches"]))
        self.assertIn("synthetic-resident-property-tax-2026", result["controllingRuleIds"])

    def test_unknown_heir_relationship_returns_allowance_branches(self):
        data = fixture()
        profile = {
            **data["profile"],
            "activeStages": ["inheritance"],
            "heirRelationship": "unknown",
        }
        result = calculate(profile=profile)
        self.assertEqual("conditional", result["status"])
        self.assertEqual(["heirRelationship"], result["unresolvedFacts"])
        self.assertEqual({"minimum": 15000, "maximum": 24000}, result["totals"]["allTax"])
        self.assertEqual({"child", "unrelated"}, {branch["assumedFacts"]["heirRelationship"] for branch in result["branches"]})

    def test_gift_allowance_is_selected_by_transfer_type(self):
        data = fixture()
        profile = {
            **data["profile"],
            "activeStages": ["gift"],
            "transferType": "gift",
            "heirRelationship": "unrelated",
        }
        result = calculate(profile=profile)
        self.assertEqual(23000, result["stages"]["gift"]["taxTotal"])
        self.assertEqual(["synthetic-gift-tax-2026"], result["stages"]["gift"]["lines"][0]["ruleIds"])

    def test_false_transfer_condition_does_not_request_heir_relationship(self):
        data = fixture()
        profile = {
            **data["profile"],
            "activeStages": ["inheritance"],
            "transferType": "gift",
        }
        profile.pop("heirRelationship")
        result = calculate(profile=profile)
        self.assertEqual("calculated", result["status"])
        self.assertEqual(0, result["stages"]["inheritance"]["taxTotal"])

    def test_dormant_stages_do_not_require_irrelevant_facts(self):
        data = fixture()
        profile = {
            "taxYear": 2026,
            "currency": "EUR",
            "activeStages": ["purchase"],
            "purchasePrice": 500000,
            "ownershipShare": 0.5,
            "financingBalance": 0,
        }
        result = calculate(profile=profile)
        self.assertEqual(20000, result["stages"]["purchase"]["taxTotal"])
        self.assertNotIn("sale", result["stages"])

    def test_conditional_residence_keeps_resident_and_nonresident_property_rates(self):
        data = fixture()
        residence = {
            "status": "conditional",
            "scopes": {"destination": "conditional", "home": "conditional"},
            "unresolvedFacts": ["daysInDestination"],
            "branches": [
                {"status": "likely_destination_resident", "scopes": {"destination": "worldwide_income", "home": "source_income"}},
                {"status": "likely_home_resident", "scopes": {"destination": "source_income", "home": "worldwide_income"}},
            ],
        }
        profile = {**data["profile"], "activeStages": ["annual"], "propertyUse": "rental"}
        result = calculate(profile=profile, residence=residence)
        self.assertEqual("conditional", result["status"])
        self.assertEqual({"minimum": 2250, "maximum": 2550}, result["totals"]["annualTax"])
        self.assertIn("daysInDestination", result["unresolvedFacts"])

    def test_each_amount_has_formula_scope_year_confidence_and_sources(self):
        data = fixture()
        formula_operands = {
            rule["id"]: rule["formula"]["operands"]
            for rule in data["rules"]["jurisdictions"]["synthetic-destination"]["rules"]
        }
        result = calculate()
        for stage in result["stages"].values():
            for line in stage["lines"]:
                with self.subTest(rule=line["ruleIds"][0]):
                    self.assertTrue(line["formula"])
                    for operand_id in formula_operands[line["ruleIds"][0]]:
                        self.assertIn(operand_id, line["formula"])
                    self.assertTrue(line["assumptions"])
                    self.assertEqual(2026, line["taxYear"])
                    self.assertIn(line["taxpayerScope"], {"resident", "nonresident"})
                    self.assertIn(line["confidence"], {"low", "medium", "medium_high", "high"})
                    self.assertEqual(["synthetic-property-authority-2026"], line["sourceIds"])

    def test_retirement_boundary_excludes_owner_property_tax_from_added_annual_tax(self):
        result = calculate()
        boundary = result["retirementIntegration"]
        self.assertEqual(7250, boundary["annualTaxBeforeBoundary"])
        self.assertEqual(1500, boundary["ownerPropertyTaxAlreadyInLivingCosts"])
        self.assertEqual(5750, boundary["additionalAnnualTaxExpense"])
        self.assertIn("double", boundary["explanation"].lower())

    def test_invalid_currency_and_nonfinite_inputs_are_rejected(self):
        data = fixture()
        wrong_currency = calculate(profile={**data["profile"], "currency": "USD"}, expect_error=True)
        self.assertEqual("FireTaxPropertyInputError", wrong_currency["error"])
        self.assertIn("currency", wrong_currency["message"])
        invalid_share = calculate(profile={**data["profile"], "ownershipShare": 1.5}, expect_error=True)
        self.assertEqual("FireTaxPropertyInputError", invalid_share["error"])
        self.assertIn("ownershipShare", invalid_share["message"])

    def test_unvalidated_property_rule_metadata_is_rejected(self):
        data = fixture()
        rules = copy.deepcopy(data["rules"])
        rules["jurisdictions"]["synthetic-destination"]["rules"][0].pop("source_ids")
        response = calculate(rules=rules, expect_error=True)
        self.assertEqual("FireTaxPropertyRuleError", response["error"])
        self.assertIn("source", response["message"].lower())


if __name__ == "__main__":
    unittest.main()
