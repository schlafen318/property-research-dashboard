from __future__ import annotations

import copy
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DETAILED_MODULE = ROOT / "src" / "fire_tax_detailed.js"
EXPLAIN_MODULE = ROOT / "src" / "fire_tax_explain.js"


def load_fixture(name: str) -> dict:
    return json.loads((ROOT / "tests" / "fixtures" / name).read_text(encoding="utf-8"))


def active_credit_rules(payload: dict) -> list[dict]:
    jurisdiction = payload["jurisdictions"][payload.get("active_jurisdiction_id", "synthetic-destination")]
    return [rule for rule in jurisdiction["rules"] if rule["type"] == "credit_limit"]


def as_home_rule_graph(payload: dict) -> dict:
    graph = copy.deepcopy(payload)
    old_id = graph.get("active_jurisdiction_id", next(iter(graph["jurisdictions"])))
    jurisdiction = graph["jurisdictions"].pop(old_id)
    jurisdiction["id"] = "synthetic-home"
    jurisdiction["label"] = "Synthetic home"
    jurisdiction["calculation_side"] = "home"
    graph["jurisdictions"]["synthetic-home"] = jurisdiction
    graph["active_jurisdiction_id"] = "synthetic-home"
    return graph


def calculator_input() -> dict:
    return {
        "currentAge": 59,
        "retirementAge": 60,
        "horizonYears": 2,
        "expenseCategories": [{"amount": 40_000, "inflationRate": 0}],
        "incomeStreams": [{"amount": 999_999, "indexed": False, "inflationRate": 0}],
        "housingPlan": "rent",
        "propertyPrice": 0,
        "propertyInflation": 0,
        "acquisitionCostRate": 0,
        "generalInflation": 0,
        "emergencyReserveMonths": 0,
        "expectedPortfolioReturn": 0,
        "monthlyIncomeBeforeRetirement": 0,
        "incomeInvestedRate": 0,
    }


def detailed_payload(*, continuing_home: bool = True) -> dict:
    residence = load_fixture("fire_tax_residence.json")
    income = load_fixture("fire_tax_income.json")
    property_data = load_fixture("fire_tax_property.json")

    destination_residence = copy.deepcopy(residence["rules"])
    destination_residence["active_jurisdiction_id"] = residence["destinationId"]
    home_residence = copy.deepcopy(residence["rules"])
    home_residence["active_jurisdiction_id"] = residence["homeId"]

    profile = {
        "residence": {
            "taxYear": 2026,
            "daysInDestination": 200,
            "destinationAvailableHome": False,
            "daysInHome": 100,
            "homeAvailableHome": False,
            "familyTies": "neither",
            "economicTies": "neither",
            "splitYear": False,
        },
        "destination": {
            "income": copy.deepcopy(income["profile"]),
            "property": copy.deepcopy(property_data["profile"]),
        },
        "continuingHome": {
            "enabled": continuing_home,
            "income": copy.deepcopy(income["profile"]),
            "property": copy.deepcopy(property_data["profile"]),
        },
        "retirement": {
            "baseInput": calculator_input(),
            "selectedAfterTaxReturn": 0.03,
            "returnBasis": "after_fees_and_tax",
            "dependableIncomeCategories": [
                "private_pension",
                "government_pension",
                "social_security",
                "rental_income",
                "employment_consulting",
            ],
            "returnCoveredCategories": [
                "dividends",
                "interest",
                "realized_gains",
                "retirement_account_withdrawal",
            ],
            "annualExpenseCategories": [],
            "dependableIncomeIndexed": False,
            "dependableIncomeInflationRate": 0,
            "propertyRentalTaxTreatment": "included_in_income_tax",
            "planningRange": {"minimum": 500_000, "maximum": 700_000},
        },
    }

    rules = {
        "residence": {"destination": destination_residence, "home": home_residence},
        "destination": {
            "income": copy.deepcopy(income["rules"]),
            "credits": active_credit_rules(income["rules"]),
            "property": copy.deepcopy(property_data["rules"]),
        },
        "continuingHome": {
            "income": as_home_rule_graph(income["rules"]),
            "credits": active_credit_rules(income["rules"]),
            "property": as_home_rule_graph(property_data["rules"]),
        },
    }
    return {"profile": profile, "rules": rules}


def add_home_only_income_category(payload: dict, amount: int = 1_000) -> None:
    home_profile = payload["profile"]["continuingHome"]["income"]
    home_profile["homeAnnuity"] = amount
    home_profile["incomeSourceJurisdictions"]["home_annuity"] = "home"
    income_rules = payload["rules"]["continuingHome"]["income"]
    income_rules["operand_catalog"]["home_annuity"] = {
        "kind": "profile",
        "profile_key": "homeAnnuity",
        "value_type": "money",
        "currency": "EUR",
    }
    jurisdiction = income_rules["jurisdictions"]["synthetic-home"]
    jurisdiction["rules"].append(
        {
            "id": "synthetic-home-annuity-2026",
            "type": "rate_band",
            "tax_year": 2026,
            "taxpayer_scope": ["resident", "nonresident"],
            "category": "home_annuity",
            "currency": "EUR",
            "formula": {"operation": "progressive_rate", "operands": ["home_annuity"]},
            "bands": [{"from": 0, "up_to": None, "rate": 0.1}],
            "source_ids": ["synthetic-income-authority-2026"],
            "effective_from": "2026-01-01",
            "checked_on": "2026-09-01",
            "review_interval_days": 365,
            "confidence": "high",
            "recheck_trigger": "Replace before enabling a real jurisdiction.",
            "explanation": "Apply a synthetic rate to the home-only annuity.",
        }
    )


def set_dependable_tax_liability_to_58_000(payload: dict) -> None:
    dependable = {
        "private_pension",
        "government_pension",
        "social_security",
        "rental_income",
        "employment_consulting",
    }
    for side in ("destination", "continuingHome"):
        income_rules = payload["rules"][side]["income"]
        income_rules["operand_catalog"]["private_pension_allowance"]["value"] = 0
        for jurisdiction in income_rules["jurisdictions"].values():
            for rule in jurisdiction["rules"]:
                if rule.get("id") == "synthetic-private-pension-allowance-2026":
                    rule["amount"] = 0
                if rule.get("type") == "rate_band" and rule.get("category") in dependable:
                    for band in rule["bands"]:
                        band["rate"] = 1
                    rule["no_tax"] = False
        payload["rules"][side]["credits"] = []


def share_official_assessment(payload: dict, shared_id: str = "shared.official-assessment-base") -> None:
    for side in ("destination", "continuingHome"):
        payload["profile"][side]["property"]["sharedFactIds"] = {
            "officialAssessmentBase": shared_id
        }


def run_detailed(payload: dict, *, expect_error: bool = False) -> dict:
    script = (
        "const api=require(process.argv[1]);const input=JSON.parse(process.argv[2]);"
        "try{process.stdout.write(JSON.stringify({ok:true,value:api.calculateDetailedTax(input.profile,input.rules)}));}"
        "catch(error){process.stdout.write(JSON.stringify({ok:false,error:error.name,message:error.message}));}"
    )
    completed = subprocess.run(
        ["node", "-e", script, str(DETAILED_MODULE), json.dumps(payload)],
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
    return response["value"]


def explain(result: dict) -> list[dict]:
    script = (
        "const api=require(process.argv[1]);const result=JSON.parse(process.argv[2]);"
        "process.stdout.write(JSON.stringify(api.explainCalculation(result)));"
    )
    completed = subprocess.run(
        ["node", "-e", script, str(EXPLAIN_MODULE), json.dumps(result)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


class DetailedFireTaxTests(unittest.TestCase):
    def test_composes_all_validated_engines_and_reconciles_exact_totals(self):
        result = run_detailed(detailed_payload())

        self.assertEqual("likely_destination_resident", result["residence"]["status"])
        self.assertEqual(9, len(result["destination"]["incomeCategories"]))
        self.assertEqual(9_850, result["destination"]["credits"]["totalNetTax"])
        self.assertEqual(64_250, result["destination"]["property"]["totals"]["allTax"])
        self.assertTrue(result["continuingHome"]["enabled"])
        self.assertEqual(7_850, result["continuingHome"]["credits"]["totalNetTax"])
        self.assertEqual(64_550, result["continuingHome"]["property"]["totals"]["allTax"])

        self.assertEqual(21_150, result["totals"]["annualTax"])
        self.assertEqual(114_000, result["totals"]["oneTimeTaxes"])
        self.assertEqual(33_000, result["totals"]["grossDependableIncome"])
        self.assertEqual(7_400, result["retirementIntegration"]["dependableIncomeTax"])
        self.assertEqual(25_600, result["totals"]["afterTaxDependableIncome"])
        self.assertEqual(3_300, result["retirementIntegration"]["livingCostCoveredTax"])
        self.assertEqual(1_500, result["retirementIntegration"]["annualTaxExpense"])
        self.assertEqual(
            result["totals"]["annualTax"],
            result["retirementIntegration"]["dependableIncomeTax"]
            + result["retirementIntegration"]["returnCoveredTax"]
            + result["retirementIntegration"]["livingCostCoveredTax"]
            + result["retirementIntegration"]["annualTaxExpense"],
        )

    def test_refined_retirement_input_uses_after_tax_values_and_preserves_planning_range(self):
        result = run_detailed(detailed_payload())
        capital_input = result["taxAdjustedCapitalInput"]
        projection = result["retirementProjection"]

        self.assertEqual("destination_estimate", capital_input["taxMode"])
        self.assertEqual("after_fees_and_tax", capital_input["returnBasis"])
        self.assertEqual(0.03, capital_input["expectedPortfolioReturn"])
        self.assertEqual(1_500, capital_input["annualTaxExpenses"])
        self.assertEqual(
            [{"amount": 25_600, "indexed": False, "inflationRate": 0}],
            capital_input["incomeStreams"],
        )
        self.assertEqual("after_fees_and_tax", projection["refined"]["returnBasis"])
        self.assertEqual(25_600, projection["refined"]["outsideIncome"])
        self.assertEqual(1_500, projection["refined"]["annualTaxExpenses"])
        self.assertEqual(0.03, projection["refined"]["expectedPortfolioReturn"])
        self.assertEqual({"minimum": 500_000, "maximum": 700_000}, projection["planningRange"])
        self.assertEqual(0, projection["refined"]["propertyCapital"])
        self.assertEqual(0, projection["refined"]["homePurchaseNeededToday"])

    def test_explanation_lines_are_complete_and_totals_are_not_rounded_away(self):
        result = run_detailed(detailed_payload())
        sections = explain(result)
        required = {
            "label",
            "formula",
            "assumptions",
            "exclusions",
            "confidence",
            "ruleIds",
            "sourceIds",
            "taxYear",
            "branchIds",
        }

        self.assertGreaterEqual(len(sections), 5)
        lines = [line for section in sections for line in section["lines"]]
        self.assertTrue(lines)
        for line in lines:
            with self.subTest(label=line.get("label")):
                self.assertTrue(required.issubset(line))
                self.assertNotEqual(bool("amount" in line), bool("amountRange" in line))
                self.assertTrue(line["formula"])
                self.assertTrue(line["assumptions"])
                self.assertTrue(line["exclusions"])
                self.assertTrue(line["ruleIds"])
                self.assertTrue(line["sourceIds"])
                self.assertTrue(line["branchIds"])
                if "amountRange" in line:
                    self.assertEqual(
                        {"minimum", "maximum"},
                        set(line["endpointScenarioIds"]),
                    )
                    for scenario_ids in line["endpointScenarioIds"].values():
                        self.assertTrue(scenario_ids)
                        self.assertTrue(set(scenario_ids).issubset(line["branchIds"]))

        totals = next(section for section in sections if section["id"] == "reconciled_totals")
        amounts = {line["key"]: line["amount"] for line in totals["lines"]}
        self.assertEqual(21_150, amounts["annual_tax"])
        self.assertEqual(114_000, amounts["one_time_taxes"])
        self.assertEqual(25_600, amounts["after_tax_dependable_income"])

    def test_conditional_property_result_retains_calculated_range_and_branches(self):
        payload = detailed_payload(continuing_home=False)
        payload["profile"]["destination"]["property"].update(
            {
                "activeStages": ["inheritance"],
                "heirRelationship": "unknown",
            }
        )
        result = run_detailed(payload)

        self.assertEqual("conditional", result["destination"]["property"]["status"])
        self.assertEqual(2, len(result["destination"]["property"]["branches"]))
        self.assertEqual(
            {"minimum": 15_000, "maximum": 24_000},
            result["totals"]["oneTimeTaxes"],
        )
        one_time_line = next(
            line
            for section in explain(result)
            for line in section["lines"]
            if line.get("key") == "one_time_taxes"
        )
        self.assertEqual(
            {"minimum": 15_000, "maximum": 24_000},
            one_time_line["amountRange"],
        )

    def test_unresolved_split_year_keeps_calculated_tax_and_capital_ranges(self):
        payload = detailed_payload(continuing_home=False)
        del payload["profile"]["residence"]["splitYear"]
        result = run_detailed(payload)

        self.assertEqual("conditional", result["residence"]["status"])
        self.assertIn("splitYear", result["residence"]["unresolvedFacts"])
        self.assertEqual(
            {"minimum": 4_550, "maximum": 12_100},
            result["totals"]["annualTax"],
        )
        self.assertEqual(
            {"minimum": 28_000, "maximum": 31_000},
            result["totals"]["afterTaxDependableIncome"],
        )
        self.assertEqual("conditional", result["retirementProjection"]["status"])
        self.assertEqual(
            {"favorable", "adverse"},
            set(result["retirementProjection"]["cases"]),
        )
        self.assertGreater(
            result["retirementProjection"]["capitalRange"]["maximum"],
            result["retirementProjection"]["capitalRange"]["minimum"],
        )

    def test_active_rental_tax_requires_an_explicit_non_duplication_boundary(self):
        payload = detailed_payload()
        del payload["profile"]["retirement"]["propertyRentalTaxTreatment"]
        response = run_detailed(payload, expect_error=True)

        self.assertFalse(response["ok"])
        self.assertEqual("DetailedFireTaxInputError", response["error"])
        self.assertIn("propertyRentalTaxTreatment", response["message"])

    def test_income_categories_must_have_one_exhaustive_retirement_treatment(self):
        payload = detailed_payload()
        payload["profile"]["retirement"]["returnCoveredCategories"].remove("dividends")
        response = run_detailed(payload, expect_error=True)
        self.assertFalse(response["ok"])
        self.assertEqual("DetailedFireTaxInputError", response["error"])
        self.assertIn("dividends", response["message"])

        payload = detailed_payload()
        payload["profile"]["retirement"]["annualExpenseCategories"].append("dividends")
        response = run_detailed(payload, expect_error=True)
        self.assertFalse(response["ok"])
        self.assertIn("exactly one", response["message"])

    def test_selected_return_must_be_explicitly_after_fees_and_tax(self):
        payload = detailed_payload()
        payload["profile"]["retirement"]["returnBasis"] = "after_fees"
        response = run_detailed(payload, expect_error=True)

        self.assertFalse(response["ok"])
        self.assertEqual("DetailedFireTaxInputError", response["error"])
        self.assertIn("after_fees_and_tax", response["message"])

    def test_cross_component_currency_mismatch_is_rejected_before_totalling(self):
        payload = detailed_payload(continuing_home=False)
        payload["profile"]["destination"]["property"]["currency"] = "USD"
        property_rules = payload["rules"]["destination"]["property"]
        for operand in property_rules["operand_catalog"].values():
            if operand.get("value_type") == "money":
                operand["currency"] = "USD"
        for jurisdiction in property_rules["jurisdictions"].values():
            for rule in jurisdiction["rules"]:
                if rule["type"] == "property_charge":
                    rule["currency"] = "USD"

        response = run_detailed(payload, expect_error=True)
        self.assertFalse(response["ok"])
        self.assertEqual("DetailedFireTaxInputError", response["error"])
        self.assertIn("currency", response["message"].lower())

    def test_likely_home_scope_does_not_erase_canonical_dependable_income(self):
        payload = detailed_payload()
        payload["profile"]["residence"].update(
            {"daysInDestination": 100, "daysInHome": 200}
        )
        result = run_detailed(payload)

        self.assertEqual("likely_home_resident", result["residence"]["status"])
        self.assertEqual(33_000, result["totals"]["grossDependableIncome"])
        self.assertEqual(
            33_000,
            sum(
                item["grossAmount"]
                for item in result["canonicalIncome"]["categories"]
                if item["treatment"] == "dependable_income"
            ),
        )

    def test_treaty_alternatives_are_composed_as_aligned_leaf_scenarios(self):
        payload = detailed_payload()
        payload["profile"]["residence"].update(
            {
                "daysInDestination": 200,
                "daysInHome": 200,
                "treatyPermanentHome": "unknown",
                "treatyCentreOfVitalInterests": "unknown",
            }
        )
        result = run_detailed(payload)

        self.assertEqual("conditional", result["status"])
        self.assertGreaterEqual(len(result["scenarios"]), 2)
        self.assertEqual(
            len(result["scenarios"]),
            len({scenario["id"] for scenario in result["scenarios"]}),
        )
        for scenario in result["scenarios"]:
            with self.subTest(scenario=scenario["id"]):
                self.assertEqual(scenario["id"], scenario["destination"]["branchId"])
                self.assertEqual(scenario["id"], scenario["continuingHome"]["branchId"])
                self.assertEqual(scenario["id"], scenario["retirementProjection"]["branchId"])
                self.assertNotEqual("conditional", scenario["residence"]["status"])
        annual_values = [scenario["totals"]["annualTax"] for scenario in result["scenarios"]]
        self.assertEqual(
            {"minimum": min(annual_values), "maximum": max(annual_values)},
            result["totals"]["annualTax"],
        )

    def test_shared_withholding_is_counted_once_and_credits_share_one_global_pool(self):
        result = run_detailed(detailed_payload())
        reconciliation = result["globalReconciliation"]

        self.assertEqual(17_700, reconciliation["totalDomesticLiability"])
        self.assertEqual(1_350, reconciliation["totalTaxPayments"])
        self.assertEqual(1_350, reconciliation["totalUniqueWithholding"])
        self.assertEqual(1_350, reconciliation["totalCreditClaimed"])
        self.assertEqual(1_350, reconciliation["totalCreditApplied"])
        self.assertEqual(16_350, reconciliation["totalAnnualIncomeTaxLiability"])
        self.assertEqual(15_000, reconciliation["totalRemainingBalanceDue"])
        self.assertEqual(16_350, reconciliation["totalNetIncomeTax"])
        for payment in reconciliation["payments"]:
            with self.subTest(identity=payment["identity"]):
                self.assertEqual(payment["amount"], payment["appliedAmount"])
                self.assertEqual(len(payment["observedBy"]), 2)
                self.assertTrue(payment["countedOnce"])
                self.assertTrue(payment["liabilityId"].startswith("continuing_home|"))
        for credit in reconciliation["credits"]:
            with self.subTest(target=credit["targetLiabilityId"]):
                self.assertTrue(credit["sourceLiabilityId"].startswith("continuing_home|"))
                self.assertTrue(credit["targetLiabilityId"].startswith("destination|"))
                self.assertGreater(credit["appliedAmount"], 0)

    def test_known_split_year_is_outer_conditional_with_aligned_period_scenarios(self):
        payload = detailed_payload(continuing_home=False)
        payload["profile"]["residence"].update(
            {"splitYear": True, "moveDate": "2026-07-01"}
        )
        result = run_detailed(payload)

        self.assertEqual("likely_destination_resident", result["residence"]["status"])
        self.assertEqual("conditional", result["status"])
        self.assertEqual(2, len(result["scenarios"]))
        self.assertEqual(
            {"likely_home_resident", "likely_destination_resident"},
            {scenario["residence"]["status"] for scenario in result["scenarios"]},
        )
        self.assertEqual("conditional", result["retirementProjection"]["status"])

    def test_home_only_category_is_included_once_when_it_has_a_treatment(self):
        payload = detailed_payload()
        add_home_only_income_category(payload)
        payload["profile"]["retirement"]["dependableIncomeCategories"].append(
            "home_annuity"
        )
        result = run_detailed(payload)

        annuity = next(
            category
            for category in result["canonicalIncome"]["categories"]
            if category["category"] == "home_annuity"
        )
        self.assertEqual(1_000, annuity["grossAmount"])
        self.assertEqual("dependable_income", annuity["treatment"])
        self.assertEqual(34_000, result["totals"]["grossDependableIncome"])

    def test_home_only_category_without_treatment_is_rejected(self):
        payload = detailed_payload()
        add_home_only_income_category(payload)
        response = run_detailed(payload, expect_error=True)

        self.assertFalse(response["ok"])
        self.assertEqual("DetailedFireTaxInputError", response["error"])
        self.assertIn("home_annuity", response["message"])

    def test_duplicate_profile_category_amounts_must_match(self):
        payload = detailed_payload()
        payload["profile"]["continuingHome"]["income"]["privatePension"] = 13_000
        response = run_detailed(payload, expect_error=True)

        self.assertFalse(response["ok"])
        self.assertEqual("DetailedFireTaxInputError", response["error"])
        self.assertIn("private_pension", response["message"])
        self.assertIn("canonical", response["message"].lower())

    def test_profile_income_category_without_rule_coverage_is_rejected(self):
        payload = detailed_payload()
        payload["profile"]["continuingHome"]["income"]["homeBonus"] = 2_000
        payload["profile"]["continuingHome"]["income"]["incomeSourceJurisdictions"][
            "home_bonus"
        ] = "home"
        response = run_detailed(payload, expect_error=True)

        self.assertFalse(response["ok"])
        self.assertEqual("DetailedFireTaxInputError", response["error"])
        self.assertIn("home_bonus", response["message"])
        self.assertIn("coverage", response["message"].lower())

    def test_source_withholding_is_payment_toward_source_liability_not_extra_tax(self):
        payload = detailed_payload()
        payload["rules"]["destination"]["credits"] = []
        payload["rules"]["continuingHome"]["credits"] = []
        result = run_detailed(payload)

        dividends = next(
            item
            for item in result["globalReconciliation"]["categories"]
            if item["category"] == "dividends"
        )
        self.assertEqual(1_800, dividends["domesticLiability"])
        self.assertIn("taxPayments", dividends)
        self.assertEqual(750, dividends.get("taxPayments"))
        self.assertEqual(0, dividends["creditApplied"])
        self.assertEqual(1_800, dividends["annualTaxLiability"])
        self.assertEqual(1_050, dividends["remainingBalanceDue"])
        payment = next(
            item
            for item in result["globalReconciliation"]["payments"]
            if item["category"] == "dividends"
        )
        self.assertEqual("continuing_home|dividends|2026", payment["liabilityId"])
        self.assertEqual(750, payment["appliedAmount"])

    def test_property_unknown_facts_are_independent_without_shared_fact_id(self):
        payload = detailed_payload()
        payload["profile"]["destination"]["property"]["officialAssessmentBase"] = "unknown"
        payload["profile"]["continuingHome"]["property"]["officialAssessmentBase"] = "unknown"
        result = run_detailed(payload)

        self.assertEqual(4, len(result["scenarios"]))
        combinations = {
            (
                scenario["branchIdentity"]["destinationPropertyFacts"][
                    "destination.property.officialAssessmentBase"
                ],
                scenario["branchIdentity"]["continuingHomePropertyFacts"][
                    "continuing_home.property.officialAssessmentBase"
                ],
            )
            for scenario in result["scenarios"]
        }
        self.assertEqual(4, len(combinations))

    def test_valid_shared_fact_id_correlates_property_branches(self):
        payload = detailed_payload()
        for key in ("destination", "continuingHome"):
            payload["profile"][key]["property"]["officialAssessmentBase"] = "unknown"
            payload["profile"][key]["property"]["sharedFactIds"] = {
                "officialAssessmentBase": "shared.official-assessment-base"
            }
        result = run_detailed(payload)

        self.assertEqual(2, len(result["scenarios"]))
        for scenario in result["scenarios"]:
            self.assertIn("sharedPropertyFacts", scenario["branchIdentity"])
            shared = scenario["branchIdentity"].get("sharedPropertyFacts")
            self.assertEqual(
                {"shared.official-assessment-base": shared["shared.official-assessment-base"]},
                shared,
            )

    def test_invalid_shared_fact_id_is_rejected(self):
        payload = detailed_payload()
        payload["profile"]["destination"]["property"]["sharedFactIds"] = {
            "officialAssessmentBase": "not valid spaces"
        }
        response = run_detailed(payload, expect_error=True)

        self.assertFalse(response["ok"])
        self.assertEqual("DetailedFireTaxInputError", response["error"])
        self.assertIn("sharedFactIds", response["message"])

    def test_conditional_explanations_reconcile_coherent_scenario_endpoints(self):
        payload = detailed_payload(continuing_home=False)
        payload["profile"]["destination"]["property"].update(
            {"activeStages": ["inheritance"], "heirRelationship": "unknown"}
        )
        result = run_detailed(payload)
        sections = explain(result)

        self.assertIn("scenarioTuples", result)
        self.assertEqual(
            {scenario["id"] for scenario in result["scenarios"]},
            {item["scenarioId"] for item in result.get("scenarioTuples", [])},
        )
        for item in result["scenarioTuples"]:
            self.assertIn("annualTaxComponents", item)
            self.assertEqual(
                item["annualTax"],
                item.get("annualTaxComponents", {}).get("incomeTaxLiability", 0)
                + item.get("annualTaxComponents", {}).get("propertyTaxLiability", 0),
            )
        reconciliation = next(
            section for section in sections if section["id"] == "global_reconciliation"
        )
        self.assertEqual(
            {
                "annual_income_tax_liability",
                "tax_payments_already_withheld",
                "foreign_tax_credits_applied",
                "remaining_income_tax_balance",
            },
            {line["key"].rsplit("_scenario_", 1)[0] for line in reconciliation["lines"]},
        )
        one_time = next(
            line
            for section in sections
            for line in section["lines"]
            if line["key"] == "one_time_taxes"
        )
        self.assertEqual(
            set(result["totals"]["oneTimeTaxes"].keys()),
            set(one_time["endpointScenarioIds"].keys()),
        )
        tuples = {item["scenarioId"]: item for item in result["scenarioTuples"]}
        for endpoint, scenario_ids in one_time["endpointScenarioIds"].items():
            for scenario_id in scenario_ids:
                self.assertEqual(
                    result["totals"]["oneTimeTaxes"][endpoint],
                    tuples[scenario_id]["oneTimeTaxes"],
                )

    def test_excess_dependable_tax_is_added_once_to_annual_expenses(self):
        payload = detailed_payload()
        set_dependable_tax_liability_to_58_000(payload)
        result = run_detailed(payload)

        integration = result["retirementIntegration"]
        self.assertEqual(33_000, result["totals"]["grossDependableIncome"])
        self.assertEqual(58_000, integration["dependableIncomeTax"])
        self.assertIn("dependableIncomeTaxNetted", integration)
        self.assertEqual(33_000, integration.get("dependableIncomeTaxNetted"))
        self.assertEqual(25_000, integration.get("excessDependableIncomeTax"))
        self.assertEqual(0, result["totals"]["afterTaxDependableIncome"])
        self.assertEqual(1_500, integration["nonDependableAnnualTaxExpense"])
        self.assertEqual(26_500, integration["annualTaxExpense"])
        self.assertEqual(26_500, result["taxAdjustedCapitalInput"]["annualTaxExpenses"])
        self.assertEqual(72_500, result["totals"]["annualTax"])
        scenario = result["scenarioTuples"][0]
        self.assertEqual(
            scenario["dependableIncomeTax"],
            scenario["dependableIncomeTaxNetted"]
            + scenario["excessDependableIncomeTax"],
        )
        self.assertEqual(
            scenario["annualTax"],
            scenario["dependableIncomeTaxNetted"]
            + scenario["returnCoveredTax"]
            + scenario["livingCostCoveredTax"]
            + scenario["annualTaxExpense"],
        )
        retirement_lines = {
            line["key"]: line
            for section in explain(result)
            if section["id"] == "retirement_integration"
            for line in section["lines"]
        }
        self.assertEqual(25_000, retirement_lines["excess_dependable_tax_expense"]["amount"])

    def test_shared_fact_known_and_assumed_values_must_match(self):
        payload = detailed_payload()
        share_official_assessment(payload)
        payload["profile"]["destination"]["property"]["officialAssessmentBase"] = 200_000
        payload["profile"]["continuingHome"]["property"]["officialAssessmentBase"] = "unknown"
        result = run_detailed(payload)

        self.assertEqual(1, len(result["scenarios"]))
        self.assertEqual(
            {"shared.official-assessment-base": 200_000},
            result["scenarios"][0]["branchIdentity"]["sharedPropertyFacts"],
        )

    def test_shared_fact_known_value_without_matching_assumption_fails_closed(self):
        payload = detailed_payload()
        share_official_assessment(payload)
        payload["profile"]["destination"]["property"]["officialAssessmentBase"] = 300_000
        payload["profile"]["continuingHome"]["property"]["officialAssessmentBase"] = "unknown"
        response = run_detailed(payload, expect_error=True)

        self.assertFalse(response["ok"])
        self.assertIn("shared.official-assessment-base", response["message"])
        self.assertNotIn("300000", response["message"])
        self.assertNotIn("200000", response["message"])
        self.assertNotIn("350000", response["message"])

    def test_shared_fact_both_known_values_must_be_equal(self):
        payload = detailed_payload()
        share_official_assessment(payload)
        result = run_detailed(payload)
        self.assertEqual(1, len(result["scenarios"]))

        payload = detailed_payload()
        share_official_assessment(payload)
        payload["profile"]["continuingHome"]["property"]["officialAssessmentBase"] = 350_000
        response = run_detailed(payload, expect_error=True)
        self.assertFalse(response["ok"])
        self.assertIn("shared.official-assessment-base", response["message"])

    def test_shared_fact_declarations_must_be_paired(self):
        payload = detailed_payload()
        payload["profile"]["destination"]["property"]["sharedFactIds"] = {
            "officialAssessmentBase": "shared.orphan"
        }
        response = run_detailed(payload, expect_error=True)
        self.assertFalse(response["ok"])
        self.assertIn("shared.orphan", response["message"])

    def test_shared_fact_declarations_must_have_consistent_mapping(self):
        payload = detailed_payload()
        payload["profile"]["destination"]["property"]["sharedFactIds"] = {
            "officialAssessmentBase": "shared.incompatible-schema"
        }
        payload["profile"]["continuingHome"]["property"]["sharedFactIds"] = {
            "heirRelationship": "shared.incompatible-schema"
        }
        response = run_detailed(payload, expect_error=True)
        self.assertFalse(response["ok"])
        self.assertIn("shared.incompatible-schema", response["message"])

    def test_shared_fact_declarations_must_have_compatible_schema(self):
        payload = detailed_payload()
        share_official_assessment(payload, "shared.schema")
        payload["rules"]["continuingHome"]["property"]["operand_catalog"][
            "official_assessment_base"
        ]["currency"] = "USD"
        response = run_detailed(payload, expect_error=True)

        self.assertFalse(response["ok"])
        self.assertIn("shared.schema", response["message"])


if __name__ == "__main__":
    unittest.main()
