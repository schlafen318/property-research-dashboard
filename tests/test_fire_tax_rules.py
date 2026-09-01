import copy
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from src.fire_tax_rules import load_fire_tax_rules, validate_fire_tax_rules


ROOT = Path(__file__).resolve().parents[1]


class FireTaxRuleContractTests(unittest.TestCase):
    def setUp(self):
        self.payload = load_fire_tax_rules()

    def validate(self, payload):
        return validate_fire_tax_rules(payload, as_of=date(2026, 9, 1))

    def assert_path_error(self, errors, path):
        self.assertTrue(
            any(error.startswith(path) for error in errors),
            f"Expected an error at {path!r}; got {errors!r}",
        )

    def test_packaged_synthetic_rules_are_complete_but_not_site_enabled(self):
        self.assertEqual([], self.validate(self.payload))
        jurisdiction = self.payload["jurisdictions"]["synthetic-example"]
        self.assertTrue(jurisdiction["synthetic"])
        self.assertFalse(jurisdiction["detailed_enabled"])
        self.assertEqual(
            {"residence_test", "branch", "rate_band"},
            {rule["type"] for rule in jurisdiction["rules"]},
        )

    def test_loader_reads_an_explicit_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rules.json"
            path.write_text(json.dumps(self.payload), encoding="utf-8")
            self.assertEqual(self.payload, load_fire_tax_rules(path))

    def test_loader_rejects_a_non_object_root(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rules.json"
            path.write_text("[]", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "root must be an object"):
                load_fire_tax_rules(path)

    def test_loader_rejects_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rules.json"
            path.write_text(
                '{"schema_version": 1, "schema_version": 2}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "duplicate JSON key.*schema_version"):
                load_fire_tax_rules(path)

    def test_loader_rejects_non_finite_json_constants(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rules.json"
            path.write_text('{"schema_version": NaN}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-finite JSON constant.*NaN"):
                load_fire_tax_rules(path)

    def test_enablement_contract_is_required(self):
        payload = copy.deepcopy(self.payload)
        payload.pop("enablement_contract", None)
        errors = self.validate(payload)
        self.assert_path_error(errors, "enablement_contract")

    def test_enablement_contract_requires_category_capabilities(self):
        payload = copy.deepcopy(self.payload)
        payload["enablement_contract"].pop("category_capabilities", None)
        errors = self.validate(payload)
        self.assert_path_error(
            errors, "enablement_contract.category_capabilities"
        )

    def test_synthetic_jurisdiction_cannot_be_enabled(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-example"]["detailed_enabled"] = True
        errors = self.validate(payload)
        self.assert_path_error(
            errors, "jurisdictions.synthetic-example.detailed_enabled"
        )

    def test_enabled_jurisdiction_rejects_non_official_referenced_sources(self):
        payload = copy.deepcopy(self.payload)
        jurisdiction = payload["jurisdictions"]["synthetic-example"]
        jurisdiction["synthetic"] = False
        jurisdiction["detailed_enabled"] = True
        errors = self.validate(payload)
        self.assertTrue(
            any(
                error.startswith("jurisdictions.synthetic-example.detailed_enabled")
                and "official" in error
                for error in errors
            ),
            errors,
        )

    def test_partial_rule_set_cannot_be_enabled_even_with_official_source(self):
        payload = copy.deepcopy(self.payload)
        jurisdiction = payload["jurisdictions"]["synthetic-example"]
        jurisdiction["synthetic"] = False
        jurisdiction["detailed_enabled"] = True
        payload["sources"][0]["source_kind"] = "official"
        errors = self.validate(payload)
        self.assertTrue(
            any(
                error.startswith("jurisdictions.synthetic-example.detailed_enabled")
                and "missing" in error
                for error in errors
            ),
            errors,
        )

    def test_unrelated_rules_cannot_satisfy_enabled_category_capabilities(self):
        payload = copy.deepcopy(self.payload)
        jurisdiction = payload["jurisdictions"]["synthetic-example"]
        jurisdiction["synthetic"] = False
        jurisdiction["detailed_enabled"] = True
        payload["sources"][0]["source_kind"] = "official"
        branch_id = jurisdiction["rules"][1]["id"]
        jurisdiction["category_coverage"] = {
            category: {"treatment": "supported", "rule_ids": [branch_id]}
            for category in payload["enablement_contract"]["required_categories"]
        }
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.category_coverage.private_pension.rule_ids[0]",
        )

    def test_no_tax_category_coverage_requires_an_explicit_no_tax_rule(self):
        payload = copy.deepcopy(self.payload)
        jurisdiction = payload["jurisdictions"]["synthetic-example"]
        jurisdiction["synthetic"] = False
        jurisdiction["detailed_enabled"] = True
        payload["sources"][0]["source_kind"] = "official"
        income_id = jurisdiction["rules"][2]["id"]
        jurisdiction["category_coverage"] = {
            category: {"treatment": "supported", "rule_ids": [income_id]}
            for category in payload["enablement_contract"]["required_categories"]
        }
        jurisdiction["category_coverage"]["private_pension"] = {
            "treatment": "no_tax",
            "rule_ids": [income_id],
        }
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.category_coverage.private_pension.rule_ids[0]",
        )

    def test_no_tax_category_rule_must_encode_a_zero_tax_formula(self):
        payload = copy.deepcopy(self.payload)
        jurisdiction = payload["jurisdictions"]["synthetic-example"]
        jurisdiction["synthetic"] = False
        jurisdiction["detailed_enabled"] = True
        payload["sources"][0]["source_kind"] = "official"
        income_rule = jurisdiction["rules"][2]
        income_rule["category"] = "private_pension"
        income_rule["no_tax"] = True
        income_id = income_rule["id"]
        jurisdiction["category_coverage"] = {
            category: {"treatment": "supported", "rule_ids": [income_id]}
            for category in payload["enablement_contract"]["required_categories"]
        }
        jurisdiction["category_coverage"]["private_pension"] = {
            "treatment": "no_tax",
            "rule_ids": [income_id],
        }
        errors = self.validate(payload)
        self.assertTrue(
            any(
                error.startswith(
                    "jurisdictions.synthetic-example.category_coverage.private_pension.rule_ids[0]"
                )
                and "zero-tax" in error
                for error in errors
            ),
            errors,
        )

    def test_malformed_nested_values_return_exact_paths_instead_of_crashing(self):
        cases = (
            (
                lambda payload: payload["operand_catalog"].__setitem__(
                    "days_in_jurisdiction", []
                ),
                "operand_catalog.days_in_jurisdiction",
            ),
            (
                lambda payload: payload["jurisdictions"]["synthetic-example"]["rules"][
                    0
                ].__setitem__(
                    "formula", {"operation": [], "operands": [["not-an-id"]]}
                ),
                "jurisdictions.synthetic-example.rules[0].formula.operation",
            ),
            (
                lambda payload: payload["jurisdictions"]["synthetic-example"]["rules"][
                    1
                ]["branches"][0]["when"].__setitem__("operand", []),
                "jurisdictions.synthetic-example.rules[1].branches[0].when.operand",
            ),
            (
                lambda payload: payload["jurisdictions"]["synthetic-example"]["rules"][
                    0
                ].__setitem__("type", []),
                "jurisdictions.synthetic-example.rules[0].type",
            ),
            (
                lambda payload: payload["sources"][0].__setitem__("source_kind", []),
                "sources[0].source_kind",
            ),
        )
        for mutate, expected_path in cases:
            with self.subTest(path=expected_path):
                payload = copy.deepcopy(self.payload)
                mutate(payload)
                errors = self.validate(payload)
                self.assert_path_error(errors, expected_path)

    def test_missing_source_reference_reports_exact_rule_path(self):
        payload = copy.deepcopy(self.payload)
        del payload["jurisdictions"]["synthetic-example"]["rules"][0]["source_ids"]
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[0].source_ids",
        )

    def test_missing_effective_date_reports_exact_rule_path(self):
        payload = copy.deepcopy(self.payload)
        del payload["jurisdictions"]["synthetic-example"]["rules"][0]["effective_from"]
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[0].effective_from",
        )

    def test_missing_formula_operand_reports_exact_rule_path(self):
        payload = copy.deepcopy(self.payload)
        del payload["jurisdictions"]["synthetic-example"]["rules"][0]["formula"]["operands"]
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[0].formula.operands",
        )

    def test_comparison_formula_rejects_one_removed_operand(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-example"]["rules"][0]["formula"][
            "operands"
        ].pop()
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[0].formula.operands",
        )

    def test_missing_taxpayer_scope_reports_exact_rule_path(self):
        payload = copy.deepcopy(self.payload)
        del payload["jurisdictions"]["synthetic-example"]["rules"][0]["taxpayer_scope"]
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[0].taxpayer_scope",
        )

    def test_missing_branch_target_reports_exact_branch_path(self):
        payload = copy.deepcopy(self.payload)
        branch = payload["jurisdictions"]["synthetic-example"]["rules"][1]
        del branch["branches"][0]["target_rule_id"]
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[1].branches[0].target_rule_id",
        )

    def test_unknown_source_id_is_rejected_at_reference(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-example"]["rules"][0]["source_ids"] = [
            "missing-authority"
        ]
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[0].source_ids[0]",
        )

    def test_unknown_formula_operand_is_rejected_at_operand(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-example"]["rules"][2]["formula"][
            "operands"
        ].append("undeclared_income")
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[2].formula.operands[1]",
        )

    def test_constant_value_must_match_declared_value_type(self):
        payload = copy.deepcopy(self.payload)
        payload["operand_catalog"]["residence_day_threshold"]["value"] = "183"
        errors = self.validate(payload)
        self.assert_path_error(
            errors, "operand_catalog.residence_day_threshold.value"
        )

    def test_derived_operand_requires_a_derivation_formula(self):
        payload = copy.deepcopy(self.payload)
        payload["operand_catalog"]["ordinary_income"]["kind"] = "derived"
        errors = self.validate(payload)
        self.assert_path_error(errors, "operand_catalog.ordinary_income.derivation")

    def test_derived_operand_type_must_match_its_derivation_result(self):
        payload = copy.deepcopy(self.payload)
        payload["operand_catalog"]["ordinary_income"].update(
            {
                "kind": "derived",
                "derivation": {
                    "operation": "greater_than_or_equal",
                    "operands": [
                        "days_in_jurisdiction",
                        "residence_day_threshold",
                    ],
                },
            }
        )
        errors = self.validate(payload)
        self.assert_path_error(errors, "operand_catalog.ordinary_income.derivation")

    def test_indirect_derived_operand_cycles_are_rejected_at_the_closing_edge(self):
        payload = copy.deepcopy(self.payload)
        payload["operand_catalog"].update(
            {
                "derived_a": {
                    "kind": "derived",
                    "value_type": "number",
                    "derivation": {
                        "operation": "add",
                        "operands": ["derived_b", "residence_day_threshold"],
                    },
                },
                "derived_b": {
                    "kind": "derived",
                    "value_type": "number",
                    "derivation": {
                        "operation": "add",
                        "operands": ["derived_a", "residence_day_threshold"],
                    },
                },
            }
        )
        errors = self.validate(payload)
        self.assertTrue(
            any(
                error.startswith("operand_catalog.derived_b.derivation.operands[0]")
                and "circular" in error
                for error in errors
            ),
            errors,
        )

    def test_comparison_operands_must_have_compatible_types_and_currency(self):
        payload = copy.deepcopy(self.payload)
        days = payload["operand_catalog"]["days_in_jurisdiction"]
        days["value_type"] = "money"
        days["currency"] = "EUR"
        threshold = payload["operand_catalog"]["residence_day_threshold"]
        threshold["value_type"] = "money"
        threshold["currency"] = "USD"
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[0].formula.operands[1]",
        )

    def test_rule_currency_must_match_money_formula_output(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-example"]["rules"][2]["currency"] = "USD"
        errors = self.validate(payload)
        self.assert_path_error(
            errors, "jurisdictions.synthetic-example.rules[2].currency"
        )

    def test_multiply_is_exactly_binary_and_rejects_boolean_operands(self):
        payload = copy.deepcopy(self.payload)
        payload["operand_catalog"]["boolean_flag"] = {
            "kind": "profile",
            "value_type": "boolean",
        }
        formula = payload["jurisdictions"]["synthetic-example"]["rules"][2]["formula"]
        formula["operation"] = "multiply"
        formula["operands"] = [
            "ordinary_income",
            "residence_day_threshold",
            "boolean_flag",
        ]
        errors = self.validate(payload)
        self.assert_path_error(
            errors, "jurisdictions.synthetic-example.rules[2].formula.operands"
        )
        formula["operands"] = ["ordinary_income", "boolean_flag"]
        errors = self.validate(payload)
        self.assert_path_error(
            errors, "jurisdictions.synthetic-example.rules[2].formula.operands"
        )

    def test_allowance_amount_must_match_its_linked_formula_constant(self):
        payload = copy.deepcopy(self.payload)
        payload["operand_catalog"]["allowance_amount"] = {
            "kind": "constant",
            "value_type": "money",
            "currency": "EUR",
            "value": 1000,
        }
        rule = payload["jurisdictions"]["synthetic-example"]["rules"][2]
        rule.pop("bands")
        rule.update(
            {
                "type": "allowance",
                "formula": {
                    "operation": "minimum",
                    "operands": ["ordinary_income", "allowance_amount"],
                },
                "amount": 2000,
                "amount_operand": "allowance_amount",
            }
        )
        errors = self.validate(payload)
        self.assert_path_error(
            errors, "jurisdictions.synthetic-example.rules[2].amount"
        )
        rule["amount"] = 1000
        self.assertEqual([], self.validate(payload))

    def test_withholding_rate_must_match_its_linked_formula_constant(self):
        payload = copy.deepcopy(self.payload)
        payload["operand_catalog"]["withholding_rate"] = {
            "kind": "constant",
            "value_type": "number",
            "value": 0.1,
        }
        rule = payload["jurisdictions"]["synthetic-example"]["rules"][2]
        rule.pop("bands")
        rule.update(
            {
                "type": "withholding",
                "formula": {
                    "operation": "multiply",
                    "operands": ["ordinary_income", "withholding_rate"],
                },
                "rate": 0.2,
                "rate_operand": "withholding_rate",
            }
        )
        errors = self.validate(payload)
        self.assert_path_error(
            errors, "jurisdictions.synthetic-example.rules[2].rate"
        )
        rule["rate"] = 0.1
        self.assertEqual([], self.validate(payload))

    def test_branch_comparison_value_must_match_operand_type(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-example"]["rules"][1]["branches"][0][
            "when"
        ]["value"] = "183"
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[1].branches[0].when.value",
        )

    def test_explanation_rejects_unknown_placeholders(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-example"]["rules"][2][
            "explanation"
        ] = "Tax on {secret_account}."
        errors = self.validate(payload)
        self.assert_path_error(
            errors, "jurisdictions.synthetic-example.rules[2].explanation"
        )

    def test_each_advertised_rule_type_has_a_specific_schema(self):
        cases = (
            (0, "rate_band", ".bands"),
            (2, "residence_test", ".resident_when"),
            (2, "allowance", ".amount"),
            (2, "withholding", ".rate"),
            (2, "credit_limit", ".applies_to_categories"),
            (2, "property_charge", ".lifecycle_stage"),
            (2, "reporting_flag", ".reporting_code"),
            (2, "branch", ".branches"),
        )
        for rule_index, changed_type, expected_suffix in cases:
            with self.subTest(rule_type=changed_type):
                payload = copy.deepcopy(self.payload)
                payload["jurisdictions"]["synthetic-example"]["rules"][rule_index][
                    "type"
                ] = changed_type
                errors = self.validate(payload)
                self.assert_path_error(
                    errors,
                    f"jurisdictions.synthetic-example.rules[{rule_index}]{expected_suffix}",
                )

    def test_progressive_bands_cannot_overlap(self):
        payload = copy.deepcopy(self.payload)
        bands = payload["jurisdictions"]["synthetic-example"]["rules"][2]["bands"]
        bands[1]["from"] = 9000
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[2].bands[1].from",
        )

    def test_progressive_band_rate_must_be_bounded(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-example"]["rules"][2]["bands"][0][
            "rate"
        ] = 1.01
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[2].bands[0].rate",
        )

    def test_non_finite_numeric_values_are_rejected(self):
        for invalid in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=invalid):
                payload = copy.deepcopy(self.payload)
                payload["jurisdictions"]["synthetic-example"]["rules"][2]["bands"][0][
                    "rate"
                ] = invalid
                errors = self.validate(payload)
                self.assert_path_error(
                    errors,
                    "jurisdictions.synthetic-example.rules[2].bands[0].rate",
                )

    def test_only_final_progressive_band_may_be_unbounded(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-example"]["rules"][2]["bands"][0][
            "up_to"
        ] = None
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[2].bands[0].up_to",
        )

    def test_branch_cycles_are_rejected_at_the_closing_edge(self):
        payload = copy.deepcopy(self.payload)
        branch = payload["jurisdictions"]["synthetic-example"]["rules"][1]
        branch["branches"][0]["target_rule_id"] = branch["id"]
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[1].branches[0].target_rule_id",
        )

    def test_unknown_branch_target_is_rejected_at_target(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-example"]["rules"][1]["branches"][0][
            "target_rule_id"
        ] = "missing-rule-2026"
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[1].branches[0].target_rule_id",
        )

    def test_stale_source_is_rejected_using_its_review_interval(self):
        payload = copy.deepcopy(self.payload)
        payload["sources"][0]["checked_on"] = "2024-01-01"
        payload["sources"][0]["review_interval_days"] = 365
        errors = self.validate(payload)
        self.assert_path_error(errors, "sources[0].checked_on")

    def test_source_must_be_effective_by_validation_date(self):
        payload = copy.deepcopy(self.payload)
        payload["sources"][0]["effective_from"] = "2026-09-02"
        errors = self.validate(payload)
        self.assert_path_error(errors, "sources[0].effective_from")

    def test_source_check_cannot_predate_its_effective_date(self):
        payload = copy.deepcopy(self.payload)
        payload["sources"][0]["checked_on"] = "2025-12-31"
        errors = self.validate(payload)
        self.assert_path_error(errors, "sources[0].checked_on")

    def test_rule_must_be_effective_by_validation_date(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-example"]["rules"][0][
            "effective_from"
        ] = "2026-09-02"
        errors = self.validate(payload)
        self.assert_path_error(
            errors, "jurisdictions.synthetic-example.rules[0].effective_from"
        )

    def test_rule_check_cannot_predate_its_effective_date(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-example"]["rules"][0][
            "checked_on"
        ] = "2025-12-31"
        errors = self.validate(payload)
        self.assert_path_error(
            errors, "jurisdictions.synthetic-example.rules[0].checked_on"
        )

    def test_rule_tax_year_must_match_dataset_tax_year(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-example"]["rules"][0]["tax_year"] = 2025
        payload["jurisdictions"]["synthetic-example"]["rules"][0][
            "id"
        ] = "example-residence-days-2025"
        errors = self.validate(payload)
        self.assert_path_error(
            errors, "jurisdictions.synthetic-example.rules[0].tax_year"
        )

    def test_rule_without_explanation_template_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-example"]["rules"][2]["explanation"] = ""
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[2].explanation",
        )

    def test_currency_is_explicit_and_iso_formatted(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-example"]["rules"][2]["currency"] = "euro"
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[2].currency",
        )

    def test_rule_ids_are_unique_within_a_jurisdiction(self):
        payload = copy.deepcopy(self.payload)
        rules = payload["jurisdictions"]["synthetic-example"]["rules"]
        rules[2]["id"] = rules[0]["id"]
        errors = self.validate(payload)
        self.assert_path_error(errors, "jurisdictions.synthetic-example.rules[2].id")

    def test_rule_id_version_year_matches_tax_year(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-example"]["rules"][2]["tax_year"] = 2025
        errors = self.validate(payload)
        self.assert_path_error(errors, "jurisdictions.synthetic-example.rules[2].id")


if __name__ == "__main__":
    unittest.main()
