from __future__ import annotations

import copy
import json
import subprocess
import unittest
from datetime import date
from pathlib import Path

from src.fire_tax_rules import validate_fire_tax_rules


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "fire_tax_residence.js"
FIXTURE = ROOT / "tests" / "fixtures" / "fire_tax_residence.json"


def fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def bundles(mutate=None) -> tuple[dict, dict]:
    data = fixture()
    destination = copy.deepcopy(data["rules"])
    home = copy.deepcopy(data["rules"])
    destination["active_jurisdiction_id"] = data["destinationId"]
    home["active_jurisdiction_id"] = data["homeId"]
    if mutate:
        mutate(destination, home)
    return destination, home


def run_residence(profile: object, *, mutate=None) -> object:
    destination, home = bundles(mutate)
    script = (
        "const api = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        "process.stdout.write(JSON.stringify(api.evaluateResidence("
        "input.profile, input.destinationRules, input.homeRules)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(ENGINE), json.dumps({
            "profile": profile,
            "destinationRules": destination,
            "homeRules": home,
        })],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


BASE = {
    "taxYear": 2026,
    "daysInDestination": 100,
    "destinationAvailableHome": False,
    "daysInHome": 200,
    "homeAvailableHome": False,
    "familyTies": "neither",
    "economicTies": "neither",
    "splitYear": False,
}


def destination_rule(payload: dict, rule_id: str) -> dict:
    return next(
        rule
        for rule in payload["jurisdictions"]["synthetic-destination"]["rules"]
        if rule["id"] == rule_id
    )


class FireTaxResidenceTests(unittest.TestCase):
    def test_synthetic_fixture_is_a_valid_task_one_rule_payload(self):
        payload = fixture()["rules"]
        self.assertEqual([], validate_fire_tax_rules(payload, as_of=date(2026, 9, 1)))
        rule_ids = {
            rule["id"]
            for rule in payload["jurisdictions"]["synthetic-destination"]["rules"]
        }
        self.assertIn("synthetic-treaty-tie-breaker-2026", rule_ids)
        self.assertIn("synthetic-split-year-2026", rule_ids)

    def test_day_threshold_is_inclusive_and_uses_validated_formula_operands(self):
        result = run_residence({**BASE, "daysInDestination": 183, "daysInHome": 100})
        self.assertEqual("likely_destination_resident", result["status"])
        self.assertTrue(result["domesticResidence"]["destination"])
        self.assertEqual("worldwide_income", result["scopes"]["destination"])
        self.assertEqual("source_income", result["scopes"]["home"])

    def test_all_supported_day_comparison_operators_honor_boundaries(self):
        cases = (
            ("greater_than", 183, False),
            ("greater_than", 184, True),
            ("less_than", 182, True),
            ("less_than", 183, False),
            ("less_than_or_equal", 183, True),
            ("less_than_or_equal", 184, False),
        )
        for operator, value, expected in cases:
            def mutate(destination, _home, operation=operator):
                destination_rule(destination, "synthetic-destination-days-2026")["formula"]["operation"] = operation

            with self.subTest(operator=operator, value=value):
                result = run_residence({**BASE, "daysInDestination": value}, mutate=mutate)
                self.assertEqual(expected, result["domesticResidence"]["destination"])

    def test_fractional_negative_excess_and_nonleap_day_366_are_unresolved(self):
        for value in (182.5, -1, 366, 367, "183", "not-a-day"):
            with self.subTest(value=value):
                result = run_residence({**BASE, "daysInDestination": value})
                self.assertEqual("conditional", result["status"])
                self.assertIn("daysInDestination", result["unresolvedFacts"])
                self.assertEqual("conditional", result["scopes"]["destination"])

        boolean_string = run_residence({**BASE, "destinationAvailableHome": "true"})
        self.assertEqual("conditional", boolean_string["status"])
        self.assertIn("destinationAvailableHome", boolean_string["unresolvedFacts"])

    def test_destination_and_home_available_home_rules_are_executed(self):
        destination = run_residence({**BASE, "daysInHome": 100, "destinationAvailableHome": True})
        home = run_residence({**BASE, "daysInHome": 100, "homeAvailableHome": True})
        self.assertTrue(destination["domesticResidence"]["destination"])
        self.assertTrue(home["domesticResidence"]["home"])
        self.assertIn("synthetic-destination-home-2026", destination["ruleIds"])
        self.assertIn("synthetic-home-home-2026", home["ruleIds"])

    def test_family_and_economic_tie_formulas_can_create_dual_residence(self):
        neutral_treaty = {"treatyPermanentHome": "both", "treatyCentreOfVitalInterests": "both"}
        family = run_residence({**BASE, **neutral_treaty, "familyTies": "destination"})
        economic = run_residence({**BASE, **neutral_treaty, "economicTies": "both"})
        self.assertEqual("possible_dual_resident", family["status"])
        self.assertEqual("possible_dual_resident", economic["status"])

    def test_validated_treaty_branches_execute_in_declared_order(self):
        result = run_residence({
            **BASE,
            "destinationAvailableHome": True,
            "treatyPermanentHome": "both",
            "treatyCentreOfVitalInterests": "destination",
        })
        self.assertEqual("likely_destination_resident", result["status"])
        self.assertEqual("destination", result["treatyResidence"])
        self.assertIn("synthetic-treaty-tie-breaker-2026", result["ruleIds"])
        self.assertIn("synthetic-treaty-2026", result["sourceIds"])

    def test_unknown_earlier_treaty_operand_stops_before_later_decision(self):
        result = run_residence({
            **BASE,
            "destinationAvailableHome": True,
            "treatyCentreOfVitalInterests": "destination",
        })
        self.assertEqual("conditional", result["status"])
        self.assertIn("treatyPermanentHome", result["unresolvedFacts"])
        self.assertEqual(
            {
                "likely_home_resident",
                "likely_destination_resident",
                "possible_dual_resident",
            },
            {branch["status"] for branch in result["branches"]},
        )

    def test_removing_supported_treaty_rule_preserves_possible_dual_residence(self):
        def mutate(destination, _home):
            rules = destination["jurisdictions"]["synthetic-destination"]["rules"]
            rules[:] = [rule for rule in rules if rule.get("branch_kind") != "treaty_tie_breaker"]

        result = run_residence(
            {**BASE, "destinationAvailableHome": True},
            mutate=mutate,
        )
        self.assertEqual("possible_dual_resident", result["status"])

    def test_split_year_uses_explicit_validated_period_statuses_and_scopes(self):
        result = run_residence({
            **BASE,
            "daysInDestination": 200,
            "daysInHome": 100,
            "splitYear": True,
            "moveDate": "2026-07-01",
        })
        self.assertEqual("likely_destination_resident", result["status"])
        self.assertEqual(
            [
                {"start": "2026-01-01", "end": "2026-06-30", "status": "likely_home_resident", "scopes": {"destination": "source_income", "home": "worldwide_income"}},
                {"start": "2026-07-01", "end": "2026-12-31", "status": "likely_destination_resident", "scopes": {"destination": "worldwide_income", "home": "source_income"}},
            ],
            result["periods"],
        )
        self.assertIn("synthetic-split-year-2026", result["ruleIds"])

    def test_unanswered_split_activation_retains_rule_and_source_audit(self):
        profile = {**BASE, "daysInDestination": 200, "daysInHome": 100}
        profile.pop("splitYear")

        result = run_residence(profile)

        self.assertEqual("conditional", result["status"])
        self.assertIn("splitYear", result["unresolvedFacts"])
        self.assertIn("synthetic-split-year-2026", result["ruleIds"])
        self.assertIn("synthetic-destination-authority-2026", result["sourceIds"])
        self.assertEqual("splitYear", result["controllingFact"])
        self.assertEqual(["synthetic-split-year-2026"], result["controllingRuleIds"])
        self.assertEqual(["synthetic-destination-authority-2026"], result["controllingSourceIds"])
        self.assertIn(False, [branch.get("assumedValue") for branch in result["branches"]])
        self.assertIn(True, [branch.get("assumedValue") for branch in result["branches"]])
        self.assertTrue(any(len(branch.get("periods", [])) == 2 for branch in result["branches"]))

    def test_unknown_split_activation_returns_full_year_and_calculated_split_alternatives(self):
        cases = (
            (
                "likely_destination_resident",
                {**BASE, "daysInDestination": 200, "daysInHome": 100},
            ),
            (
                "likely_home_resident",
                {**BASE, "daysInDestination": 100, "daysInHome": 200},
            ),
            (
                "possible_dual_resident",
                {
                    **BASE,
                    "daysInDestination": 200,
                    "daysInHome": 200,
                    "treatyPermanentHome": "both",
                    "treatyCentreOfVitalInterests": "both",
                },
            ),
        )
        for base_status, profile in cases:
            profile.pop("splitYear")
            profile["moveDate"] = "2026-07-01"

            def mutate(destination, _home, supported_status=base_status):
                split = destination_rule(destination, "synthetic-split-year-2026")
                split["applies_to_statuses"] = [supported_status]

            with self.subTest(base_status=base_status):
                result = run_residence(profile, mutate=mutate)
                self.assertEqual("conditional", result["status"])
                self.assertEqual("splitYear", result["controllingFact"])
                self.assertIn("synthetic-split-year-2026", result["ruleIds"])
                self.assertEqual(["synthetic-split-year-2026"], result["controllingRuleIds"])
                self.assertEqual(["synthetic-destination-authority-2026"], result["controllingSourceIds"])
                alternatives = {
                    branch["assumedValue"]: branch
                    for branch in result["branches"]
                    if branch.get("controllingFact") == "splitYear"
                }
                self.assertEqual({False, True}, set(alternatives))
                self.assertEqual(base_status, alternatives[False]["status"])
                self.assertEqual(1, len(alternatives[False]["periods"]))
                self.assertEqual(2, len(alternatives[True]["periods"]))
                self.assertNotEqual(alternatives[False]["periods"], alternatives[True]["periods"])
                for branch in alternatives.values():
                    self.assertEqual(["synthetic-split-year-2026"], branch["ruleIds"])
                    self.assertEqual(["synthetic-destination-authority-2026"], branch["sourceIds"])

    def test_python_and_js_executable_residence_projection_have_mutation_parity(self):
        cases = []
        for confidence in ("low", "medium", "medium_high", "high", "medium-ish"):
            cases.append((
                f"confidence:{confidence}",
                lambda destination, value=confidence: destination_rule(
                    destination, "synthetic-destination-days-2026"
                ).update({"confidence": value}),
                confidence in {"low", "medium", "medium_high", "high"},
            ))
        for operation in (
            "greater_than",
            "greater_than_or_equal",
            "less_than",
            "less_than_or_equal",
            "equals",
            "not_equals",
            "approximately",
        ):
            cases.append((
                f"operation:{operation}",
                lambda destination, value=operation: destination_rule(
                    destination, "synthetic-destination-days-2026"
                )["formula"].update({"operation": value}),
                operation != "approximately",
            ))

        def valid_flag_operation(destination):
            destination_rule(destination, "synthetic-destination-days-2026")["formula"].update(
                {"operation": "flag", "operands": ["destination_available_home"]}
            )
            questions = destination["jurisdictions"]["synthetic-destination"]["questions"]
            questions[:] = [question for question in questions if question["id"] != "fire-tax-days-destination"]

        cases.extend(
            [
                (
                    "operation:flag",
                    valid_flag_operation,
                    True,
                ),
                (
                    "operation:flag-invalid-arity",
                    lambda destination: destination_rule(
                        destination, "synthetic-destination-days-2026"
                    )["formula"].update(
                        {
                            "operation": "flag",
                            "operands": ["destination_available_home", "home_available_home"],
                        }
                    ),
                    False,
                ),
                (
                    "operation:missing",
                    lambda destination: destination_rule(
                        destination, "synthetic-destination-days-2026"
                    )["formula"].pop("operation"),
                    False,
                ),
            ]
        )
        for value, expected in ((183, True), (183.5, True), ("183", False), (True, False), (None, False)):
            def mutate_value(destination, candidate=value):
                operand = destination["operand_catalog"]["residence_day_threshold"]
                if candidate is None:
                    operand.pop("value", None)
                else:
                    operand["value"] = candidate

            cases.append((f"constant:{value!r}", mutate_value, expected))

        for label, mutation, expected in cases:
            destination, home = bundles(lambda destination, _home, change=mutation: change(destination))
            python_accepts = validate_fire_tax_rules(destination, as_of=date(2026, 9, 1)) == []
            result = run_residence(BASE, mutate=lambda destination, _home, change=mutation: change(destination))
            javascript_accepts = result["availability"] != "unavailable"
            with self.subTest(case=label):
                self.assertEqual(expected, python_accepts)
                self.assertEqual(python_accepts, javascript_accepts)

    def test_split_year_does_not_apply_outside_its_validated_base_status(self):
        result = run_residence({**BASE, "splitYear": True, "moveDate": "2026-07-01"})
        self.assertEqual("likely_home_resident", result["status"])
        self.assertEqual(1, len(result["periods"]))
        self.assertEqual("likely_home_resident", result["periods"][0]["status"])
        self.assertNotIn("synthetic-split-year-2026", result["ruleIds"])

    def test_split_year_never_invents_pre_period_status_or_scope(self):
        def mutate(destination, _home):
            rule = destination_rule(destination, "synthetic-split-year-2026")
            before = next(period for period in rule["periods"] if period["position"] == "before")
            before["status"] = "conditional"
            before["scopes"] = {"destination": "conditional", "home": "conditional"}

        result = run_residence(
            {**BASE, "daysInDestination": 200, "daysInHome": 100, "splitYear": True, "moveDate": "2026-07-01"},
            mutate=mutate,
        )
        self.assertEqual("conditional", result["periods"][0]["status"])
        self.assertEqual({"destination": "conditional", "home": "conditional"}, result["periods"][0]["scopes"])

    def test_invalid_or_out_of_year_move_date_is_conditional(self):
        for move_date in ("2026-02-30", "2025-12-31", "bad"):
            with self.subTest(move_date=move_date):
                result = run_residence({
                    **BASE,
                    "daysInDestination": 200,
                    "daysInHome": 100,
                    "splitYear": True,
                    "moveDate": move_date,
                })
                self.assertEqual("conditional", result["status"])
                self.assertIn("moveDate", result["unresolvedFacts"])

    def test_malformed_missing_or_unknown_rule_operations_fail_closed(self):
        mutations = (
            lambda rule: rule["formula"].pop("operation"),
            lambda rule: rule["formula"].update({"operation": "approximately"}),
            lambda rule: rule.pop("formula"),
        )
        for mutation in mutations:
            def mutate(destination, _home, change=mutation):
                change(destination_rule(destination, "synthetic-destination-days-2026"))

            with self.subTest(mutation=mutation):
                result = run_residence(BASE, mutate=mutate)
                self.assertEqual("conditional", result["status"])
                self.assertEqual({"destination": "conditional", "home": "conditional"}, result["scopes"])
                self.assertEqual([], result["branches"])

    def test_missing_scope_and_malformed_treaty_decision_fail_closed(self):
        def missing_scope(destination, _home):
            destination["jurisdictions"]["synthetic-destination"].pop("resident_scope")

        scope_result = run_residence(BASE, mutate=missing_scope)
        self.assertEqual("conditional", scope_result["status"])
        self.assertEqual([], scope_result["branches"])

        def bad_treaty(destination, _home):
            rule = destination_rule(destination, "synthetic-treaty-tie-breaker-2026")
            rule["branches"][0].pop("residence_decision")

        treaty_result = run_residence({**BASE, "destinationAvailableHome": True, "treatyPermanentHome": "destination"}, mutate=bad_treaty)
        self.assertEqual("conditional", treaty_result["status"])
        self.assertEqual([], treaty_result["branches"])

    def test_treaty_condition_operand_must_be_declared_by_validated_formula(self):
        def mutate(destination, _home):
            treaty = destination_rule(destination, "synthetic-treaty-tie-breaker-2026")
            treaty["formula"]["operands"] = ["treaty_permanent_home"]

        result = run_residence(
            {**BASE, "destinationAvailableHome": True},
            mutate=mutate,
        )

        self.assertEqual("unavailable", result["availability"])
        self.assertEqual([], result["branches"])

    def test_missing_constant_or_rule_audit_metadata_is_unavailable(self):
        mutations = (
            lambda destination: destination["operand_catalog"]["residence_day_threshold"].pop("value"),
            lambda destination: destination_rule(destination, "synthetic-destination-days-2026").pop("tax_year"),
            lambda destination: destination_rule(destination, "synthetic-destination-days-2026").pop("explanation"),
            lambda destination: destination["sources"][0].pop("publisher"),
        )
        for mutation in mutations:
            def mutate(destination, _home, change=mutation):
                change(destination)

            with self.subTest(mutation=mutation):
                result = run_residence(
                    {**BASE, "daysInDestination": 200, "daysInHome": 100},
                    mutate=mutate,
                )
                self.assertEqual("unavailable", result["availability"])
                self.assertEqual({"destination": "conditional", "home": "conditional"}, result["scopes"])
                self.assertEqual([], result["periods"])
                self.assertEqual([], result["branches"])

    def test_invalid_string_domains_remain_unresolved_and_do_not_fall_through_treaty(self):
        for fact in ("familyTies", "economicTies"):
            with self.subTest(fact=fact):
                profile = {**BASE, "daysInDestination": 100, "daysInHome": 100, fact: "banana"}
                result = run_residence(profile)
                self.assertEqual("conditional", result["status"])
                self.assertIn(fact, result["unresolvedFacts"])

        treaty = run_residence(
            {
                **BASE,
                "destinationAvailableHome": True,
                "treatyPermanentHome": "banana",
                "treatyCentreOfVitalInterests": "destination",
            }
        )
        self.assertEqual("conditional", treaty["status"])
        self.assertIsNone(treaty["treatyResidence"])
        self.assertIn("treatyPermanentHome", treaty["unresolvedFacts"])

    def test_conditional_split_activation_and_duplicate_special_rules_are_unavailable(self):
        def conditional_split(destination, _home):
            split = destination_rule(destination, "synthetic-split-year-2026")
            split["applies_to_statuses"] = ["conditional"]

        conditional = run_residence(
            {**BASE, "daysInDestination": None, "splitYear": True, "moveDate": "2026-07-01"},
            mutate=conditional_split,
        )
        self.assertEqual("unavailable", conditional["availability"])
        self.assertEqual([], conditional["periods"])

        def duplicate_split(destination, _home):
            split = copy.deepcopy(destination_rule(destination, "synthetic-split-year-2026"))
            split["id"] = "synthetic-second-split-year-2026"
            destination["jurisdictions"]["synthetic-destination"]["rules"].append(split)

        duplicate = run_residence(BASE, mutate=duplicate_split)
        self.assertEqual("unavailable", duplicate["availability"])

    def test_single_jurisdiction_packaged_payload_selects_without_runtime_mutation(self):
        packaged = json.loads((ROOT / "data" / "fire_tax_rules.json").read_text(encoding="utf-8"))
        script = (
            "const api = require(process.argv[1]);"
            "const rules = JSON.parse(process.argv[2]);"
            "process.stdout.write(JSON.stringify(api.evaluateResidence("
            "{taxYear: 2026, daysInJurisdiction: 183}, rules, rules)));"
        )
        completed = subprocess.run(
            ["node", "-e", script, str(ENGINE), json.dumps(packaged)],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertNotEqual("unavailable", result["availability"])

    def test_unknown_domestic_fact_preserves_supported_possible_branches(self):
        profile = {**BASE, "treatyPermanentHome": "destination"}
        profile.pop("daysInDestination")
        result = run_residence(profile)
        self.assertEqual("conditional", result["status"])
        self.assertIn("daysInDestination", result["unresolvedFacts"])
        self.assertEqual(
            {"likely_home_resident", "likely_destination_resident"},
            {branch["status"] for branch in result["branches"]},
        )

    def test_result_is_total_over_invalid_inputs_without_defaulting_scopes(self):
        for invalid in (None, [], "bad", {"daysInDestination": -1}):
            with self.subTest(profile=invalid):
                result = run_residence(invalid)
                self.assertEqual("conditional", result["status"])
                self.assertIsInstance(result["periods"], list)
                self.assertEqual({"destination": "conditional", "home": "conditional"}, result["scopes"])
                self.assertIsInstance(result["unresolvedFacts"], list)


if __name__ == "__main__":
    unittest.main()
