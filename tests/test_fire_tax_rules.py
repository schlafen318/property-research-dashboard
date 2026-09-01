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
