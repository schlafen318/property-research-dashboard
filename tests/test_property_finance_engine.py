from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "property_finance.js"


def run_engine(function_name: str, payload: object) -> object:
    script = (
        "const engine = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        f"process.stdout.write(JSON.stringify(engine.{function_name}(input)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(ENGINE), json.dumps(payload)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def buy_now_payload(**overrides: object) -> dict:
    payload = {
        "currentAge": 50,
        "retirementAge": 60,
        "totalLiquidCapital": 400000,
        "maximumPropertyAllocation": 300000,
        "monthlyPortfolioContribution": 1500,
        "contributionInflationLinked": True,
        "generalInflation": 0.02,
        "expectedPortfolioReturn": 0.05,
        "propertyPrice": 500000,
        "acquisitionCostRate": 0.04,
        "propertyInflation": 0.02,
        "annualOwnerCosts": 6000,
        "ownerCostInflation": 0.02,
        "useBeforeRetirement": "rental",
        "grossRentalYield": 0.05,
        "vacancyRate": 0.10,
        "operatingCostRate": 0.20,
        "requestedLtv": 0.70,
        "annualMortgageRate": 0.04,
        "mortgageTermYears": 20,
        "mortgageTreatment": "payoff",
        "mortgageProfile": {
            "availability": "likely_available",
            "maximum_ltv": 0.60,
            "maximum_term_years": 30,
            "maximum_age_at_maturity": 75,
            "conditions": [],
        },
    }
    payload.update(overrides)
    return payload


class PropertyFinanceEngineTests(unittest.TestCase):
    def test_zero_rate_mortgage_divides_principal_evenly(self) -> None:
        result = run_engine(
            "monthlyMortgagePayment",
            {"principal": 120000, "annualRate": 0, "termMonths": 120},
        )
        self.assertEqual(1000, result)

    def test_standard_mortgage_payment(self) -> None:
        result = run_engine(
            "monthlyMortgagePayment",
            {"principal": 100000, "annualRate": 0.06, "termMonths": 360},
        )
        self.assertAlmostEqual(599.5505, result, places=3)

    def test_supported_ltv_caps_user_request_and_preserves_remainder(self) -> None:
        result = run_engine("evaluateBuyNow", buy_now_payload())
        self.assertEqual(0.60, result["effectiveLtv"])
        self.assertEqual(220000, result["cashRequiredToday"])
        self.assertEqual(180000, result["startingPortfolio"])
        self.assertIn("limited to 60%", " ".join(result["reasons"]))

    def test_property_cash_requirement_cannot_exceed_user_allocation(self) -> None:
        result = run_engine(
            "evaluateBuyNow",
            buy_now_payload(maximumPropertyAllocation=200000),
        )
        self.assertFalse(result["supported"])
        self.assertIn("property allocation", " ".join(result["reasons"]))

    def test_personal_use_has_no_rent_and_reduces_monthly_investing(self) -> None:
        result = run_engine(
            "evaluateBuyNow",
            buy_now_payload(useBeforeRetirement="personal"),
        )
        first_year = result["annualProjection"][1]
        self.assertEqual(0, first_year["grossRent"])
        self.assertLess(first_year["netPropertyCashFlow"], 0)
        self.assertLess(first_year["netPortfolioContributions"], 1500 * 12)

    def test_rental_surplus_is_added_to_portfolio_contributions(self) -> None:
        result = run_engine(
            "evaluateBuyNow",
            buy_now_payload(
                requestedLtv=0.20,
                annualMortgageRate=0,
                grossRentalYield=0.12,
                vacancyRate=0,
                operatingCostRate=0.10,
                maximumPropertyAllocation=500000,
                totalLiquidCapital=600000,
            ),
        )
        first_year = result["annualProjection"][1]
        self.assertGreater(first_year["netPropertyCashFlow"], 0)
        self.assertGreater(first_year["netPortfolioContributions"], 1500 * 12)

    def test_negative_cash_flow_can_exhaust_portfolio(self) -> None:
        result = run_engine(
            "evaluateBuyNow",
            buy_now_payload(
                totalLiquidCapital=225000,
                maximumPropertyAllocation=225000,
                monthlyPortfolioContribution=0,
                useBeforeRetirement="personal",
                annualMortgageRate=0.15,
            ),
        )
        self.assertIsNotNone(result["exhaustedMonth"])
        self.assertFalse(result["supported"])

    def test_property_equity_is_separate_from_liquid_portfolio(self) -> None:
        result = run_engine("evaluateBuyNow", buy_now_payload())
        self.assertAlmostEqual(
            result["propertyValueAtRetirement"] - result["mortgageBalanceAtRetirement"],
            result["propertyEquityAtRetirement"],
            places=6,
        )
        self.assertNotEqual(result["portfolioAtRetirement"], result["propertyEquityAtRetirement"])

    def test_payoff_deducts_remaining_balance_but_continue_does_not(self) -> None:
        payoff = run_engine("evaluateBuyNow", buy_now_payload(mortgageTreatment="payoff"))
        continued = run_engine("evaluateBuyNow", buy_now_payload(mortgageTreatment="continue"))
        self.assertAlmostEqual(
            continued["portfolioAtRetirement"] - payoff["portfolioAtRetirement"],
            continued["mortgageBalanceAtRetirement"],
            places=4,
        )
        self.assertGreater(continued["remainingMortgagePayments"], 0)


if __name__ == "__main__":
    unittest.main()
