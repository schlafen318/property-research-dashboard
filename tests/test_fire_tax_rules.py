import copy
import json
import os
import subprocess
import sys
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

    def test_packaged_rules_enable_a_real_hong_kong_to_dubai_profile(self):
        self.assertEqual([], self.validate(self.payload))
        profile = self.payload["supported_profiles"]["hong-kong-to-dubai"]
        self.assertTrue(profile["detailed_enabled"])
        self.assertFalse(profile["synthetic"])
        self.assertEqual("hong-kong", profile["home_jurisdiction_id"])
        self.assertEqual("dubai", profile["destination_id"])
        self.assertEqual([], profile["property_lifecycle"])
        self.assertIn("runtime_rule_graph", profile)
        self.assertNotIn("profile", profile["runtime_definition"])
        self.assertNotIn("personalized_amounts", profile["runtime_definition"])

    def test_enabled_profile_rejects_missing_official_sources_and_lifecycle(self):
        payload = copy.deepcopy(self.payload)
        profile = payload["supported_profiles"]["hong-kong-to-dubai"]
        profile["source_ids"] = ["synthetic-example-authority-2026"]
        profile["property_lifecycle"].append("purchase")

        errors = self.validate(payload)

        self.assert_path_error(errors, "supported_profiles.hong-kong-to-dubai.source_ids")
        self.assert_path_error(errors, "supported_profiles.hong-kong-to-dubai.property_lifecycle")

    def test_enabled_profile_rejects_runtime_graph_source_and_formula_mutations(self):
        missing_profile_source = copy.deepcopy(self.payload)
        missing_profile_source["supported_profiles"]["hong-kong-to-dubai"]["source_ids"].remove("uae-individual-tax-2026")
        missing_rule_source = copy.deepcopy(self.payload)
        destination_income = missing_rule_source["supported_profiles"]["hong-kong-to-dubai"]["runtime_rule_graph"]["income"]["destination"]
        destination_income["source_ids"] = []
        broken_formula = copy.deepcopy(self.payload)
        broken_formula["supported_profiles"]["hong-kong-to-dubai"]["runtime_rule_graph"]["income"]["destination"]["formula"] = {"operation": "invented", "operands": []}
        broken_profile_key = copy.deepcopy(self.payload)
        broken_profile_key["supported_profiles"]["hong-kong-to-dubai"]["runtime_rule_graph"]["income"]["destination"]["profile_keys"].pop("interest")
        broken_rule_id = copy.deepcopy(self.payload)
        broken_rule_id["supported_profiles"]["hong-kong-to-dubai"]["runtime_rule_graph"]["income"]["destination"]["rule_ids"]["interest"] = "invented"

        self.assert_path_error(self.validate(missing_profile_source), "supported_profiles.hong-kong-to-dubai.source_ids")
        self.assert_path_error(self.validate(missing_rule_source), "supported_profiles.hong-kong-to-dubai.runtime_rule_graph.income.destination.source_ids")
        self.assert_path_error(self.validate(broken_formula), "supported_profiles.hong-kong-to-dubai.runtime_rule_graph.income.destination.formula")
        self.assert_path_error(self.validate(broken_profile_key), "supported_profiles.hong-kong-to-dubai.runtime_rule_graph.income.destination.profile_keys")
        self.assert_path_error(self.validate(broken_rule_id), "supported_profiles.hong-kong-to-dubai.runtime_rule_graph.income.destination.rule_ids")

    def test_enabled_profile_rejects_canned_personal_amounts(self):
        payload = copy.deepcopy(self.payload)
        payload["supported_profiles"]["hong-kong-to-dubai"]["runtime_definition"]["annualPension"] = 12000

        errors = self.validate(payload)

        self.assert_path_error(errors, "supported_profiles.hong-kong-to-dubai.runtime_definition.annualPension")

    def test_enabled_profile_rejects_missing_and_unknown_capabilities(self):
        payload = copy.deepcopy(self.payload)
        runtime = payload["supported_profiles"]["hong-kong-to-dubai"]["runtime_definition"]
        del runtime["supported_housing_plans"]
        runtime["supported_activity_types"] = ["teleport"]

        errors = self.validate(payload)

        self.assert_path_error(errors, "supported_profiles.hong-kong-to-dubai.runtime_definition.supported_housing_plans")
        self.assert_path_error(errors, "supported_profiles.hong-kong-to-dubai.runtime_definition.supported_activity_types")

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

    def test_undeclared_extension_categories_are_rejected_at_the_contract(self):
        payload = copy.deepcopy(self.payload)
        payload["enablement_contract"]["required_categories"].append(
            "future_extension"
        )
        errors = self.validate(payload)
        self.assert_path_error(errors, "enablement_contract.required_categories")

    def test_synthetic_jurisdiction_cannot_be_enabled(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-example"]["detailed_enabled"] = True
        errors = self.validate(payload)
        self.assert_path_error(
            errors, "jurisdictions.synthetic-example.detailed_enabled"
        )

    def test_residence_jurisdiction_requires_explicit_logic_and_scopes(self):
        payload = copy.deepcopy(self.payload)
        jurisdiction = payload["jurisdictions"]["synthetic-example"]
        jurisdiction.pop("resident_scope", None)
        jurisdiction.pop("nonresident_scope", None)
        jurisdiction.pop("residence_logic", None)

        errors = self.validate(payload)

        self.assert_path_error(errors, "jurisdictions.synthetic-example.resident_scope")
        self.assert_path_error(errors, "jurisdictions.synthetic-example.nonresident_scope")
        self.assert_path_error(errors, "jurisdictions.synthetic-example.residence_logic")

    def test_residence_questions_use_control_specific_validated_values_and_rules(self):
        payload = copy.deepcopy(self.payload)
        jurisdiction = payload["jurisdictions"]["synthetic-example"]
        jurisdiction["questions"] = [
            {
                "id": "example-days-question",
                "operand_id": "days_in_jurisdiction",
                "control": "number",
                "label": "How many days will you spend there?",
                "reason": "The validated day test can change residence.",
                "accepted_values": {"min": 0, "max": 366, "step": 1, "integer": True},
                "materiality_values": [0, 183, 366],
                "affects_rule_ids": ["example-residence-days-2026"],
            }
        ]
        question = jurisdiction["questions"][0]
        question["accepted_values"] = ["not", "a", "number", "range"]
        question["affects_rule_ids"] = ["missing-residence-rule-2026"]

        errors = self.validate(payload)

        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.questions[0].accepted_values",
        )
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.questions[0].affects_rule_ids[0]",
        )

    def test_runtime_jurisdiction_selector_must_reference_validated_jurisdiction(self):
        payload = copy.deepcopy(self.payload)
        payload["active_jurisdiction_id"] = "missing-jurisdiction"

        errors = self.validate(payload)

        self.assert_path_error(errors, "active_jurisdiction_id")

    def test_question_ranges_and_materiality_values_stay_within_native_control(self):
        payload = copy.deepcopy(self.payload)
        question = payload["jurisdictions"]["synthetic-example"]["questions"][0]
        question["accepted_values"] = {
            "min": 1,
            "max": 366,
            "step": 0.5,
            "integer": False,
        }
        question["materiality_values"] = [0, 183, 366]

        errors = self.validate(payload)

        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.questions[0].accepted_values",
        )
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.questions[0].materiality_values",
        )

    def test_question_labels_are_plain_text_and_branch_conditions_are_declared(self):
        payload = copy.deepcopy(self.payload)
        jurisdiction = payload["jurisdictions"]["synthetic-example"]
        jurisdiction["questions"][0]["label"] = "<strong>Days?</strong>"
        branch = jurisdiction["rules"][1]
        branch["formula"]["operands"] = ["ordinary_income"]

        errors = self.validate(payload)

        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.questions[0].label",
        )
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[1].branches[0].when.operand",
        )

    def test_questions_reference_only_active_residence_graph_rules(self):
        payload = copy.deepcopy(self.payload)
        jurisdiction = payload["jurisdictions"]["synthetic-example"]
        dormant = copy.deepcopy(jurisdiction["rules"][0])
        dormant["id"] = "example-dormant-days-2026"
        jurisdiction["rules"].append(dormant)
        jurisdiction["questions"][0]["affects_rule_ids"] = [dormant["id"]]

        errors = self.validate(payload)

        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.questions[0].affects_rule_ids[0]",
        )

    def test_string_residence_operands_require_validated_allowed_values(self):
        payload = copy.deepcopy(self.payload)
        operand = payload["operand_catalog"]["days_in_jurisdiction"]
        operand.update(
            {
                "value_type": "string",
                "allowed_values": ["home", "destination"],
            }
        )
        operand.pop("minimum", None)
        operand.pop("maximum", None)
        operand.pop("integer", None)
        operand.pop("day_count", None)
        payload["operand_catalog"]["residence_day_threshold"].update(
            {"value_type": "string", "value": "destination"}
        )
        payload["jurisdictions"]["synthetic-example"]["questions"][0].update(
            {
                "control": "select",
                "accepted_values": ["home", "destination", "banana"],
                "materiality_values": ["home", "destination"],
            }
        )

        errors = self.validate(payload)

        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.questions[0].accepted_values",
        )

        operand.pop("allowed_values")
        errors = self.validate(payload)
        self.assert_path_error(errors, "operand_catalog.days_in_jurisdiction.allowed_values")

    def test_special_residence_rules_have_single_cardinality_and_definite_split_base(self):
        payload = copy.deepcopy(self.payload)
        jurisdiction = payload["jurisdictions"]["synthetic-example"]
        split = copy.deepcopy(jurisdiction["rules"][1])
        split.update(
            {
                "id": "example-split-year-2026",
                "branch_kind": "split_year",
                "date_operand": "example_move_date",
                "activation_operand": "example_split_requested",
                "applies_to_statuses": ["conditional"],
                "periods": [
                    {
                        "position": "before",
                        "status": "likely_home_resident",
                        "scopes": {"destination": "worldwide_income", "home": "source_income"},
                    },
                    {
                        "position": "from",
                        "status": "likely_destination_resident",
                        "scopes": {"destination": "worldwide_income", "home": "source_income"},
                    },
                ],
                "formula": {
                    "operation": "conditional",
                    "operands": ["example_split_requested", "example_move_date"],
                },
            }
        )
        payload["operand_catalog"].update(
            {
                "example_move_date": {
                    "kind": "profile",
                    "profile_key": "moveDate",
                    "value_type": "date",
                },
                "example_split_requested": {
                    "kind": "profile",
                    "profile_key": "splitYear",
                    "value_type": "boolean",
                },
            }
        )
        jurisdiction["rules"].extend([split, {**copy.deepcopy(split), "id": "example-second-split-2026"}])

        errors = self.validate(payload)

        self.assert_path_error(errors, "jurisdictions.synthetic-example.rules")
        self.assertTrue(any("applies_to_statuses" in error for error in errors))
        self.assertTrue(any("periods[0].scopes" in error for error in errors))

    def test_split_date_question_values_are_real_and_inside_tax_year(self):
        payload = copy.deepcopy(self.payload)
        question = payload["jurisdictions"]["synthetic-example"]["questions"][0]
        payload["operand_catalog"]["days_in_jurisdiction"].update(
            {"value_type": "date", "profile_key": "moveDate"}
        )
        for field in ("minimum", "maximum", "integer", "day_count"):
            payload["operand_catalog"]["days_in_jurisdiction"].pop(field, None)
        payload["operand_catalog"]["residence_day_threshold"].update(
            {"value_type": "date", "value": "2026-07-01"}
        )
        question.update(
            {
                "control": "date",
                "accepted_values": {"min": "2026-02-30", "max": "2027-01-01"},
                "materiality_values": ["2026-02-30", "2027-01-01"],
            }
        )

        errors = self.validate(payload)

        self.assert_path_error(errors, "jurisdictions.synthetic-example.questions[0].accepted_values")
        self.assert_path_error(errors, "jurisdictions.synthetic-example.questions[0].materiality_values")

    def test_executable_residence_operands_reject_unsupported_derived_values(self):
        payload = copy.deepcopy(self.payload)
        payload["operand_catalog"]["base_residence_threshold"] = {
            "kind": "constant",
            "value_type": "number",
            "value": 183,
        }
        payload["operand_catalog"]["residence_day_threshold"] = {
            "kind": "derived",
            "value_type": "number",
            "derivation": {
                "operation": "add",
                "operands": ["base_residence_threshold"],
            },
        }

        errors = self.validate(payload)

        self.assert_path_error(
            errors,
            "operand_catalog.residence_day_threshold",
        )

    def test_treaty_branch_uses_validated_ordered_residence_decisions(self):
        payload = copy.deepcopy(self.payload)
        jurisdiction = payload["jurisdictions"]["synthetic-example"]
        branch = copy.deepcopy(jurisdiction["rules"][1])
        branch.update(
            {
                "id": "example-treaty-tie-breaker-2026",
                "branch_kind": "treaty_tie_breaker",
                "branches": [
                    {
                        "when": {
                            "operand": "days_in_jurisdiction",
                            "operator": "greater_than_or_equal",
                            "value": 183,
                        },
                        "residence_decision": "destination",
                    }
                ],
            }
        )
        jurisdiction["rules"].append(branch)

        self.assertEqual([], self.validate(payload))
        branch["branches"][0].pop("residence_decision")
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[3].branches[0].residence_decision",
        )

    def test_split_year_branch_requires_explicit_period_status_and_scopes(self):
        payload = copy.deepcopy(self.payload)
        jurisdiction = payload["jurisdictions"]["synthetic-example"]
        branch = copy.deepcopy(jurisdiction["rules"][1])
        branch.update(
            {
                "id": "example-split-year-2026",
                "branch_kind": "split_year",
                "formula": {
                    "operation": "conditional",
                    "operands": ["days_in_jurisdiction"],
                },
                "date_operand": "days_in_jurisdiction",
                "activation_operand": "days_in_jurisdiction",
                "applies_to_statuses": ["likely_destination_resident"],
                "periods": [
                    {
                        "position": "before",
                        "status": "likely_home_resident",
                        "scopes": {
                            "destination": "source_income",
                            "home": "worldwide_income",
                        },
                    },
                    {
                        "position": "from",
                        "status": "likely_destination_resident",
                        "scopes": {
                            "destination": "worldwide_income",
                            "home": "source_income",
                        },
                    },
                ],
            }
        )
        branch.pop("branches")
        jurisdiction["rules"].append(branch)

        errors = self.validate(payload)
        self.assertTrue(
            any(error.startswith("jurisdictions.synthetic-example.rules[3].date_operand") for error in errors),
            errors,
        )
        branch["date_operand"] = "move_date"
        payload["operand_catalog"]["move_date"] = {
            "kind": "profile",
            "profile_key": "moveDate",
            "value_type": "date",
        }
        branch["activation_operand"] = "split_year_requested"
        payload["operand_catalog"]["split_year_requested"] = {
            "kind": "profile",
            "profile_key": "splitYear",
            "value_type": "boolean",
        }
        branch["formula"]["operands"] = ["split_year_requested", "move_date"]

        self.assertEqual([], self.validate(payload))
        branch["periods"][0].pop("scopes")
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[3].periods[0].scopes",
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

    def test_property_value_plus_zero_is_not_proof_of_zero_tax(self):
        payload = copy.deepcopy(self.payload)
        payload["operand_catalog"].update(
            {
                "property_value": {
                    "kind": "profile",
                    "value_type": "money",
                    "currency": "EUR",
                },
                "zero_charge": {
                    "kind": "constant",
                    "value_type": "money",
                    "currency": "EUR",
                    "value": 0,
                },
            }
        )
        jurisdiction = payload["jurisdictions"]["synthetic-example"]
        jurisdiction["synthetic"] = False
        jurisdiction["detailed_enabled"] = True
        payload["sources"][0]["source_kind"] = "official"
        rule = jurisdiction["rules"][2]
        rule.pop("bands")
        rule.update(
            {
                "type": "property_charge",
                "category": "property_purchase",
                "formula": {
                    "operation": "add",
                    "operands": ["property_value", "zero_charge"],
                },
                "lifecycle_stage": "purchase",
                "amount": 0,
                "amount_operand": "zero_charge",
                "no_tax": True,
            }
        )
        rule_id = rule["id"]
        jurisdiction["category_coverage"] = {
            category: {"treatment": "supported", "rule_ids": [rule_id]}
            for category in payload["enablement_contract"]["required_categories"]
        }
        jurisdiction["category_coverage"]["property_purchase"] = {
            "treatment": "no_tax",
            "rule_ids": [rule_id],
        }
        errors = self.validate(payload)
        self.assertTrue(
            any(
                error.startswith(
                    "jurisdictions.synthetic-example.category_coverage.property_purchase.rule_ids[0]"
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

    def test_derived_cycle_diagnostics_are_stable_across_python_hash_seeds(self):
        payload = copy.deepcopy(self.payload)
        for left, right in (("derived_a", "derived_b"), ("derived_c", "derived_d")):
            payload["operand_catalog"][left] = {
                "kind": "derived",
                "value_type": "number",
                "derivation": {
                    "operation": "add",
                    "operands": [right, "residence_day_threshold"],
                },
            }
            payload["operand_catalog"][right] = {
                "kind": "derived",
                "value_type": "number",
                "derivation": {
                    "operation": "add",
                    "operands": [left, "residence_day_threshold"],
                },
            }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cyclic-rules.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            script = (
                "import json,sys; from datetime import date; "
                "from src.fire_tax_rules import load_fire_tax_rules,validate_fire_tax_rules; "
                "errors=validate_fire_tax_rules(load_fire_tax_rules(sys.argv[1]),date(2026,9,1)); "
                "print(json.dumps([e for e in errors if 'circular derived' in e]))"
            )
            outputs = []
            for seed in ("1", "7", "42"):
                environment = dict(os.environ)
                environment["PYTHONHASHSEED"] = seed
                result = subprocess.run(
                    [sys.executable, "-c", script, str(path)],
                    cwd=ROOT,
                    env=environment,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                outputs.append(result.stdout.strip())
        self.assertEqual(1, len(set(outputs)), outputs)
        self.assertEqual(
            [
                "operand_catalog.derived_b.derivation.operands[0] creates a circular derived dependency",
                "operand_catalog.derived_d.derivation.operands[0] creates a circular derived dependency",
            ],
            json.loads(outputs[0]),
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

    def test_credit_limit_requires_executable_ordered_category_semantics(self):
        payload = copy.deepcopy(self.payload)
        payload["operand_catalog"].update(
            {
                "foreign_tax_paid": {
                    "kind": "profile",
                    "profile_key": "foreignTaxPaid",
                    "value_type": "money",
                    "currency": "EUR",
                },
                "domestic_tax_limit": {
                    "kind": "profile",
                    "profile_key": "domesticTaxLimit",
                    "value_type": "money",
                    "currency": "EUR",
                },
            }
        )
        rule = payload["jurisdictions"]["synthetic-example"]["rules"][2]
        rule.pop("bands")
        rule.update(
            {
                "type": "credit_limit",
                "category": "foreign_tax_credit",
                "formula": {
                    "operation": "minimum",
                    "operands": ["foreign_tax_paid", "domestic_tax_limit"],
                },
                "credit_operand": "foreign_tax_paid",
                "limit_operand": "domestic_tax_limit",
                "credit_basis": "source_withholding",
                "order": 1,
                "applies_to_categories": ["dividends"],
                "assumptions": ["Synthetic category matching assumption."],
            }
        )
        self.assertEqual([], self.validate(payload))

        for field, invalid in (
            ("credit_basis", "worldwide_income"),
            ("order", 0),
            ("applies_to_categories", []),
            ("credit_operand", "ordinary_income"),
        ):
            with self.subTest(field=field):
                mutation = copy.deepcopy(payload)
                mutation["jurisdictions"]["synthetic-example"]["rules"][2][field] = invalid
                errors = self.validate(mutation)
                self.assert_path_error(
                    errors,
                    f"jurisdictions.synthetic-example.rules[2].{field}",
                )

    def test_retirement_withdrawal_rule_requires_validated_classification_allowlist(self):
        payload = copy.deepcopy(self.payload)
        payload["operand_catalog"]["retirement_classification"] = {
            "kind": "profile",
            "profile_key": "retirementAccountClassification",
            "value_type": "string",
            "allowed_values": ["traditional", "unsupported"],
        }
        rule = payload["jurisdictions"]["synthetic-example"]["rules"][2]
        rule.update(
            {
                "category": "retirement_account_withdrawal",
                "account_classification_operand": "retirement_classification",
                "supported_account_classifications": ["traditional"],
            }
        )
        self.assertEqual([], self.validate(payload))

        rule["supported_account_classifications"] = ["not-declared"]
        errors = self.validate(payload)
        self.assert_path_error(
            errors,
            "jurisdictions.synthetic-example.rules[2].supported_account_classifications",
        )

    def test_optional_income_calculation_side_is_validated_when_declared(self):
        payload = copy.deepcopy(self.payload)
        jurisdiction = payload["jurisdictions"]["synthetic-example"]
        jurisdiction["calculation_side"] = "destination"
        self.assertEqual([], self.validate(payload))

        jurisdiction["calculation_side"] = "elsewhere"
        errors = self.validate(payload)
        self.assert_path_error(
            errors, "jurisdictions.synthetic-example.calculation_side"
        )

    def test_allowance_execution_is_deliberately_minimum_only(self):
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
                    "operation": "maximum",
                    "operands": ["ordinary_income", "allowance_amount"],
                },
                "amount": 1000,
                "amount_operand": "allowance_amount",
            }
        )
        errors = self.validate(payload)
        self.assert_path_error(
            errors, "jurisdictions.synthetic-example.rules[2].formula.operation"
        )

    def test_no_tax_rate_rule_must_encode_zero_tax_even_before_enablement(self):
        payload = copy.deepcopy(self.payload)
        rule = payload["jurisdictions"]["synthetic-example"]["rules"][2]
        rule["no_tax"] = True
        rule["bands"][0]["rate"] = 0.1
        errors = self.validate(payload)
        self.assert_path_error(
            errors, "jurisdictions.synthetic-example.rules[2].no_tax"
        )

    def test_credit_limit_requires_auditable_assumptions(self):
        payload = copy.deepcopy(self.payload)
        payload["operand_catalog"].update(
            {
                "foreign_tax_paid": {"kind": "profile", "profile_key": "foreignTaxPaid", "value_type": "money", "currency": "EUR"},
                "domestic_tax_limit": {"kind": "profile", "profile_key": "domesticTaxLimit", "value_type": "money", "currency": "EUR"},
            }
        )
        rule = payload["jurisdictions"]["synthetic-example"]["rules"][2]
        rule.pop("bands")
        rule.update(
            {
                "type": "credit_limit",
                "category": "foreign_tax_credit",
                "formula": {"operation": "minimum", "operands": ["foreign_tax_paid", "domestic_tax_limit"]},
                "credit_operand": "foreign_tax_paid",
                "limit_operand": "domestic_tax_limit",
                "credit_basis": "source_withholding",
                "order": 1,
                "applies_to_categories": ["dividends"],
                "assumptions": [],
            }
        )
        errors = self.validate(payload)
        self.assert_path_error(
            errors, "jurisdictions.synthetic-example.rules[2].assumptions"
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


class FireTaxPropertyRuleSchemaTests(unittest.TestCase):
    def setUp(self):
        fixture_path = ROOT / "tests" / "fixtures" / "fire_tax_property.json"
        self.payload = json.loads(fixture_path.read_text(encoding="utf-8"))["rules"]

    def validate(self, payload):
        return validate_fire_tax_rules(payload, as_of=date(2026, 9, 1))

    def assert_path_error(self, errors, path):
        self.assertTrue(
            any(error.startswith(path) for error in errors),
            f"Expected an error at {path!r}; got {errors!r}",
        )

    def test_property_execution_metadata_is_part_of_the_shared_contract(self):
        self.assertEqual([], self.validate(self.payload))
        rule_path = "jurisdictions.synthetic-destination.rules[0]"
        for field in ("charge_kind", "tax_or_non_tax", "payment_treatment"):
            with self.subTest(field=field):
                payload = copy.deepcopy(self.payload)
                payload["jurisdictions"]["synthetic-destination"]["rules"][0].pop(field)
                self.assert_path_error(self.validate(payload), f"{rule_path}.{field}")

    def test_property_conditions_ranges_and_retirement_boundary_are_validated(self):
        cases = (
            (7, lambda rule: rule["applies_when"][0].update({"operand": "missing"}), ".applies_when[0].operand"),
            (3, lambda rule: rule["unknown_operand_range"].update({"maximum_ratio": 2}), ".unknown_operand_range.maximum_ratio"),
            (3, lambda rule: rule.update({"retirement_cost_boundary": "anything"}), ".retirement_cost_boundary"),
        )
        for rule_index, mutate, suffix in cases:
            with self.subTest(rule_index=rule_index, suffix=suffix):
                payload = copy.deepcopy(self.payload)
                mutate(payload["jurisdictions"]["synthetic-destination"]["rules"][rule_index])
                self.assert_path_error(
                    self.validate(payload),
                    f"jurisdictions.synthetic-destination.rules[{rule_index}]{suffix}",
                )

    def test_property_coverage_requires_every_stage_scope_and_exact_rules(self):
        base_path = "jurisdictions.synthetic-destination.property_coverage"
        cases = (
            (lambda jurisdiction: jurisdiction["property_coverage"]["annual"].pop("resident"), f"{base_path}.annual.resident"),
            (lambda jurisdiction: jurisdiction["property_coverage"]["annual"]["resident"]["rule_ids"].remove("synthetic-resident-property-tax-2026"), f"{base_path}.annual.resident.rule_ids"),
            (lambda jurisdiction: jurisdiction["property_coverage"]["annual"]["resident"].update({"treatment": "no_tax"}), f"{base_path}.annual.resident.rule_ids"),
            (lambda jurisdiction: jurisdiction["property_coverage"]["annual"]["resident"].update({"treatment": []}), f"{base_path}.annual.resident.treatment"),
            (lambda jurisdiction: jurisdiction["property_coverage"]["annual"]["resident"].update({"treatment": {}}), f"{base_path}.annual.resident.treatment"),
        )
        for mutate, expected_path in cases:
            with self.subTest(path=expected_path):
                payload = copy.deepcopy(self.payload)
                mutate(payload["jurisdictions"]["synthetic-destination"])
                self.assert_path_error(self.validate(payload), expected_path)

    def test_relationship_branching_requires_a_complete_validated_domain(self):
        cases = (
            (
                lambda payload: payload["operand_catalog"]["heir_relationship"].pop("allowed_values"),
                "operand_catalog.heir_relationship.allowed_values",
            ),
            (
                lambda payload: payload["operand_catalog"]["heir_relationship"]["allowed_values"].append("spouse"),
                "operand_catalog.heir_relationship.allowed_values",
            ),
            (
                lambda payload: (
                    payload["operand_catalog"]["heir_relationship"]["allowed_values"].append("unknown"),
                    payload["jurisdictions"]["synthetic-destination"]["rules"][15]["applies_when"][1].update(
                        {"operator": "not_equals", "value": "child"}
                    ),
                ),
                "operand_catalog.heir_relationship.allowed_values",
            ),
            (
                lambda payload: payload["jurisdictions"]["synthetic-destination"]["rules"][14]["applies_when"][1].update({"value": "spouse"}),
                "jurisdictions.synthetic-destination.rules[14].applies_when[1].value",
            ),
        )
        for mutate, expected_path in cases:
            with self.subTest(path=expected_path):
                payload = copy.deepcopy(self.payload)
                mutate(payload)
                self.assert_path_error(self.validate(payload), expected_path)

    def test_property_allowance_audit_must_come_from_formula_operands(self):
        payload = copy.deepcopy(self.payload)
        payload["jurisdictions"]["synthetic-destination"]["rules"][14][
            "allowance_amount"
        ] = 99999
        self.assert_path_error(
            self.validate(payload),
            "jurisdictions.synthetic-destination.rules[14].allowance_amount",
        )
        payload = copy.deepcopy(self.payload)
        payload["operand_catalog"]["gift_relief"]["audit_role"] = "guess"
        self.assert_path_error(
            self.validate(payload),
            "operand_catalog.gift_relief.audit_role",
        )

    def test_malformed_relationship_condition_is_path_error_not_validator_crash(self):
        cases = (
            (
                lambda payload: payload["jurisdictions"]["synthetic-destination"]["rules"][14].update({"applies_when": {}}),
                "jurisdictions.synthetic-destination.rules[14].applies_when",
            ),
            (
                lambda payload: payload["jurisdictions"]["synthetic-destination"]["rules"][14].update({"applies_when": None}),
                "jurisdictions.synthetic-destination.rules[14].applies_when",
            ),
            (
                lambda payload: payload["jurisdictions"]["synthetic-destination"]["rules"][14].update({"applies_when": 7}),
                "jurisdictions.synthetic-destination.rules[14].applies_when",
            ),
            (
                lambda payload: payload["jurisdictions"]["synthetic-destination"]["rules"][0].update({"taxpayer_scope": None}),
                "jurisdictions.synthetic-destination.rules[0].taxpayer_scope",
            ),
        )
        for mutate, expected_path in cases:
            with self.subTest(path=expected_path):
                payload = copy.deepcopy(self.payload)
                mutate(payload)
                try:
                    errors = self.validate(payload)
                except Exception as error:  # pragma: no cover - failure explains totality regression
                    self.fail(f"validator crashed instead of returning path errors: {error!r}")
                self.assert_path_error(errors, expected_path)


if __name__ == "__main__":
    unittest.main()
