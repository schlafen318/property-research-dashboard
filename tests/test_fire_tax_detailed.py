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

        self.assertEqual(22_500, result["totals"]["annualTax"])
        self.assertEqual(114_000, result["totals"]["oneTimeTaxes"])
        self.assertEqual(33_000, result["totals"]["grossDependableIncome"])
        self.assertEqual(8_000, result["retirementIntegration"]["dependableIncomeTax"])
        self.assertEqual(25_000, result["totals"]["afterTaxDependableIncome"])
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
            [{"amount": 25_000, "indexed": False, "inflationRate": 0}],
            capital_input["incomeStreams"],
        )
        self.assertEqual("after_fees_and_tax", projection["refined"]["returnBasis"])
        self.assertEqual(25_000, projection["refined"]["outsideIncome"])
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

        totals = next(section for section in sections if section["id"] == "reconciled_totals")
        amounts = {line["key"]: line["amount"] for line in totals["lines"]}
        self.assertEqual(22_500, amounts["annual_tax"])
        self.assertEqual(114_000, amounts["one_time_taxes"])
        self.assertEqual(25_000, amounts["after_tax_dependable_income"])

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
            {"minimum": 4_250, "maximum": 12_100},
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


if __name__ == "__main__":
    unittest.main()
