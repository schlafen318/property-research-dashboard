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

    def test_unknown_assessment_is_expanded_only_inside_applicable_relationship_branch(self):
        data = fixture()
        rules = copy.deepcopy(data["rules"])
        jurisdiction = rules["jurisdictions"]["synthetic-destination"]
        property_rule = jurisdiction["rules"][3]
        property_rule.pop("unknown_operand_range")
        property_rule["formula"]["operands"][0] = "owned_purchase_value"
        imputed_rule = jurisdiction["rules"][6]
        imputed_rule["applies_when"].append(
            {"operand": "heir_relationship", "operator": "equals", "value": "child"}
        )
        rules["operand_catalog"]["zero_rate"] = {
            "kind": "constant",
            "value_type": "number",
            "value": 0,
        }
        unrelated_rule = copy.deepcopy(imputed_rule)
        unrelated_rule.update(
            {
                "id": "synthetic-unrelated-imputed-no-tax-2026",
                "no_tax": True,
                "rate": 0,
                "rate_operand": "zero_rate",
                "unknown_operand_range": None,
                "formula": {
                    "operation": "multiply",
                    "operands": ["owned_purchase_value", "zero_rate"],
                },
                "explanation": "Explicit synthetic no-tax imputed-income branch for an unrelated successor.",
            }
        )
        unrelated_rule.pop("unknown_operand_range")
        unrelated_rule["applies_when"][-1] = {
            "operand": "heir_relationship",
            "operator": "equals",
            "value": "unrelated",
        }
        jurisdiction["rules"].append(unrelated_rule)
        for scope in ("resident", "nonresident"):
            jurisdiction["property_coverage"]["annual"][scope]["rule_ids"].append(
                unrelated_rule["id"]
            )
        profile = {
            **data["profile"],
            "activeStages": ["annual"],
            "propertyUse": "personal",
            "heirRelationship": "unknown",
            "officialAssessmentBase": "unknown",
        }
        result = calculate(profile=profile, rules=rules)
        self.assertEqual("conditional", result["status"])
        self.assertEqual(3, len(result["branches"]))
        unrelated = next(
            branch
            for branch in result["branches"]
            if branch["assumedFacts"]["heirRelationship"] == "unrelated"
        )
        self.assertNotIn("officialAssessmentBase", unrelated["assumedFacts"])

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

    def test_conditional_stage_lines_preserve_branch_identity_and_reconcile(self):
        data = fixture()
        profile = {
            **data["profile"],
            "activeStages": ["inheritance"],
            "heirRelationship": "unknown",
        }
        result = calculate(profile=profile)
        stage = result["stages"]["inheritance"]
        self.assertNotIn("lines", stage)
        self.assertEqual(2, len(stage["branchBreakdown"]))
        for total_key in ("taxTotal", "nonTaxTotal", "prepaymentTotal"):
            branch_values = [branch[total_key] for branch in stage["branchBreakdown"]]
            self.assertEqual(
                {"minimum": min(branch_values), "maximum": max(branch_values)},
                stage[total_key],
            )
        for branch in stage["branchBreakdown"]:
            with self.subTest(branch=branch["assumedFacts"]):
                liability = sum(
                    line["amount"]
                    for line in branch["lines"]
                    if line["classification"] == "tax"
                )
                self.assertEqual(branch["taxTotal"], liability)
                self.assertIn("heirRelationship", branch["assumedFacts"])

    def test_unknown_relationship_uses_full_validated_domain_for_not_equals(self):
        data = fixture()
        rules = copy.deepcopy(data["rules"])
        child_rule = rules["jurisdictions"]["synthetic-destination"]["rules"][14]
        child_rule["applies_when"][1] = {
            "operand": "heir_relationship",
            "operator": "not_equals",
            "value": "unrelated",
        }
        profile = {
            **data["profile"],
            "activeStages": ["inheritance"],
            "heirRelationship": "unknown",
        }
        result = calculate(profile=profile, rules=rules)
        self.assertEqual("conditional", result["status"])
        self.assertEqual(
            {"child", "unrelated"},
            {branch["assumedFacts"]["heirRelationship"] for branch in result["branches"]},
        )

    def test_missing_relationship_domain_is_a_typed_rule_error(self):
        data = fixture()
        rules = copy.deepcopy(data["rules"])
        rules["operand_catalog"]["heir_relationship"].pop("allowed_values")
        profile = {
            **data["profile"],
            "activeStages": ["inheritance"],
            "heirRelationship": "unknown",
        }
        response = calculate(profile=profile, rules=rules, expect_error=True)
        self.assertFalse(response["ok"])
        self.assertEqual("FireTaxPropertyRuleError", response.get("error"))
        self.assertIn("allowed", response.get("message", "").lower())

    def test_malformed_relationship_domains_are_typed_rule_errors(self):
        data = fixture()
        cases = (
            ["child", "unrelated", 7],
            ["child", "unrelated", ""],
            ["child", "unrelated", "unknown"],
            ["child", "child"],
        )
        for domain in cases:
            with self.subTest(domain=domain):
                rules = copy.deepcopy(data["rules"])
                rules["operand_catalog"]["heir_relationship"]["allowed_values"] = domain
                rules["jurisdictions"]["synthetic-destination"]["rules"][15]["applies_when"][1] = {
                    "operand": "heir_relationship",
                    "operator": "not_equals",
                    "value": "child",
                }
                profile = {
                    **data["profile"],
                    "activeStages": ["inheritance"],
                    "heirRelationship": "unknown",
                }
                response = calculate(profile=profile, rules=rules, expect_error=True)
                self.assertFalse(response["ok"])
                self.assertEqual("FireTaxPropertyRuleError", response.get("error"))
                self.assertIn("allowed", response.get("message", "").lower())

        rules = copy.deepcopy(data["rules"])
        jurisdiction = rules["jurisdictions"]["synthetic-destination"]
        rules["operand_catalog"]["heir_relationship"]["allowed_values"] = ["child"]
        jurisdiction["rules"] = [
            rule for rule in jurisdiction["rules"]
            if rule["id"] != "synthetic-unrelated-inheritance-tax-2026"
        ]
        for scope in ("resident", "nonresident"):
            jurisdiction["property_coverage"]["inheritance"][scope]["rule_ids"].remove(
                "synthetic-unrelated-inheritance-tax-2026"
            )
        profile = {
            **data["profile"],
            "activeStages": ["inheritance"],
            "heirRelationship": "unknown",
        }
        response = calculate(profile=profile, rules=rules, expect_error=True)
        self.assertFalse(response["ok"])
        self.assertEqual("FireTaxPropertyRuleError", response.get("error"))
        self.assertIn("allowed", response.get("message", "").lower())

    def test_malformed_relationship_conditions_fail_with_a_typed_rule_error(self):
        data = fixture()
        rules = copy.deepcopy(data["rules"])
        rules["jurisdictions"]["synthetic-destination"]["rules"][14][
            "applies_when"
        ] = {}
        response = calculate(rules=rules, expect_error=True)
        self.assertFalse(response["ok"])
        self.assertEqual("FireTaxPropertyRuleError", response.get("error"))
        self.assertIn("applies_when", response.get("message", ""))

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
        line = result["stages"]["gift"]["lines"][0]
        self.assertEqual(["synthetic-gift-tax-2026"], line["ruleIds"])
        self.assertEqual(
            [{"operandId": "gift_relief", "amount": 20000, "currency": "EUR"}],
            line.get("allowances"),
        )
        self.assertEqual("subtract", (line.get("operandAudit") or [{}])[0].get("operation"))

    def test_false_transfer_condition_does_not_request_heir_relationship(self):
        data = fixture()
        profile = {
            **data["profile"],
            "activeStages": ["inheritance"],
            "transferType": "gift",
        }
        profile.pop("heirRelationship")
        response = calculate(profile=profile, expect_error=True)
        self.assertFalse(response["ok"])
        self.assertEqual("FireTaxPropertyRuleError", response.get("error"))
        self.assertIn("inheritance.resident", response.get("message", ""))
        self.assertNotIn("heirRelationship", response.get("message", ""))

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
        branch_rules = [set(branch["ruleIds"]) for branch in result["branches"]]
        self.assertTrue(any("synthetic-resident-property-tax-2026" in ids for ids in branch_rules))
        self.assertTrue(any("synthetic-nonresident-property-tax-2026" in ids for ids in branch_rules))
        self.assertFalse(any({"synthetic-resident-property-tax-2026", "synthetic-nonresident-property-tax-2026"}.issubset(ids) for ids in branch_rules))

    def test_missing_selected_scope_coverage_is_a_typed_error_not_zero(self):
        data = fixture()
        rules = copy.deepcopy(data["rules"])
        rules["jurisdictions"]["synthetic-destination"]["property_coverage"]["annual"].pop("resident")
        profile = {**data["profile"], "activeStages": ["annual"]}
        response = calculate(profile=profile, rules=rules, expect_error=True)
        self.assertFalse(response["ok"])
        self.assertEqual("FireTaxPropertyRuleError", response.get("error"))
        self.assertIn("annual.resident", response.get("message", ""))

    def test_coverage_cannot_omit_an_applicable_scope_rule(self):
        data = fixture()
        rules = copy.deepcopy(data["rules"])
        coverage = rules["jurisdictions"]["synthetic-destination"]["property_coverage"]["annual"]["resident"]["rule_ids"]
        coverage.remove("synthetic-resident-property-tax-2026")
        profile = {**data["profile"], "activeStages": ["annual"]}
        response = calculate(profile=profile, rules=rules, expect_error=True)
        self.assertFalse(response["ok"])
        self.assertEqual("FireTaxPropertyRuleError", response.get("error"))
        self.assertIn("coverage", response.get("message", "").lower())

    def test_explicit_executable_no_tax_coverage_returns_a_zero_line(self):
        data = fixture()
        rules = copy.deepcopy(data["rules"])
        jurisdiction = rules["jurisdictions"]["synthetic-destination"]
        gift_rule = jurisdiction["rules"][16]
        gift_rule["no_tax"] = True
        gift_rule["rate"] = 0
        rules["operand_catalog"]["gift_rate"]["value"] = 0
        for scope in ("resident", "nonresident"):
            jurisdiction["property_coverage"]["gift"][scope]["treatment"] = "no_tax"
        profile = {
            **data["profile"],
            "activeStages": ["gift"],
            "transferType": "gift",
        }
        result = calculate(profile=profile, rules=rules)
        self.assertEqual(0, result["stages"]["gift"]["taxTotal"])
        self.assertEqual(1, len(result["stages"]["gift"]["lines"]))
        self.assertEqual("synthetic-gift-tax-2026", result["stages"]["gift"]["lines"][0]["ruleIds"][0])

    def test_invalid_allowance_audit_role_is_a_typed_rule_error(self):
        data = fixture()
        rules = copy.deepcopy(data["rules"])
        rules["operand_catalog"]["gift_relief"]["audit_role"] = "guess"
        response = calculate(rules=rules, expect_error=True)
        self.assertFalse(response["ok"])
        self.assertEqual("FireTaxPropertyRuleError", response.get("error"))
        self.assertIn("audit role", response.get("message", ""))

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
