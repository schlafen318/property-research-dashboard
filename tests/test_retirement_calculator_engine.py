from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "retirement_calculator.js"


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


def calculate(payload: dict) -> dict:
    return run_engine("calculateRetirement", payload)  # type: ignore[return-value]


def base_payload() -> dict:
    return {
        "currentAge": 50,
        "retirementAge": 60,
        "horizonYears": 30,
        "expenseCategories": [{"amount": 100000, "inflationRate": 0.026}],
        "incomeStreams": [
            {"amount": 20000, "indexed": True, "inflationRate": 0.026},
            {"amount": 10000, "indexed": False, "inflationRate": 0.026},
        ],
        "housingPlan": "rent",
        "propertyPrice": 500000,
        "propertyInflation": 0.026,
        "acquisitionCostRate": 0.1,
        "generalInflation": 0.026,
        "emergencyReserveMonths": 12,
        "expectedPortfolioReturn": 0.05,
        "monthlyIncomeBeforeRetirement": 0,
        "incomeInvestedRate": 0,
    }


def level_cash_flow_payload() -> dict:
    return {
        "currentAge": 59,
        "retirementAge": 60,
        "horizonYears": 3,
        "expenseCategories": [{"amount": 12000, "inflationRate": 0}],
        "incomeStreams": [{"amount": 2000, "indexed": False, "inflationRate": 0}],
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


class RetirementCalculatorEngineTests(unittest.TestCase):
    def test_retirement_can_begin_now_for_static_scenario_pages(self) -> None:
        payload = level_cash_flow_payload()
        payload.update({"currentAge": 60, "retirementAge": 60, "retirementBeginsNow": True})
        result = calculate(payload)
        self.assertEqual(0, result["yearsToRetirement"])
        self.assertEqual(12000, result["firstYearExpenses"])

    def test_projects_expenses_and_indexed_income(self) -> None:
        result = calculate(base_payload())
        factor = 1.026**10
        self.assertAlmostEqual(100000 * factor, result["firstYearExpenses"], places=4)
        self.assertAlmostEqual(20000 * factor + 10000, result["outsideIncome"], places=4)
        self.assertAlmostEqual(result["firstYearExpenses"] - result["outsideIncome"], result["fundingGap"], places=4)
        self.assertEqual(0.05, result["expectedPortfolioReturn"])

    def test_zero_return_sums_annual_funding_gaps(self) -> None:
        result = calculate(level_cash_flow_payload())
        self.assertEqual([10000, 10000, 10000], result["annualFundingGaps"])
        self.assertEqual(30000, result["liquidPortfolio"])
        self.assertEqual(30000, result["retirementCapital"])
        self.assertAlmostEqual(1 / 3, result["impliedFirstYearWithdrawal"], places=8)

    def test_higher_return_reduces_required_capital(self) -> None:
        payload = level_cash_flow_payload()
        payload["expectedPortfolioReturn"] = 0.10
        result = calculate(payload)
        self.assertAlmostEqual(27355.371900826444, result["liquidPortfolio"], places=6)

    def test_net_return_after_withdrawal_subtracts_first_year_withdrawal_rate(self) -> None:
        payload = level_cash_flow_payload()
        payload["expectedPortfolioReturn"] = 0.05
        result = calculate(payload)
        expected = result["expectedPortfolioReturn"] - result["impliedFirstYearWithdrawal"]
        self.assertAlmostEqual(expected, result["netReturnAfterWithdrawal"], places=8)
        self.assertLess(result["netReturnAfterWithdrawal"], 0)

    def test_retirement_capital_is_discounted_to_investment_needed_today(self) -> None:
        payload = level_cash_flow_payload()
        payload.update({"currentAge": 50, "retirementAge": 60, "expectedPortfolioReturn": 0.05})
        result = calculate(payload)
        expected_today = result["retirementCapital"] / 1.05**10
        self.assertAlmostEqual(expected_today, result["investmentNeededToday"], places=6)
        self.assertEqual(0, result["homePurchaseNeededToday"])
        self.assertAlmostEqual(expected_today, result["totalNeededToday"], places=6)
        self.assertEqual(result["retirementCapital"], result["totalCapitalAtRetirement"])

    def test_monthly_contributions_reduce_the_lump_sum_needed_today(self) -> None:
        payload = level_cash_flow_payload()
        payload.update(
            {
                "monthlyIncomeBeforeRetirement": 1000,
                "incomeInvestedRate": 0.5,
            }
        )
        result = calculate(payload)
        self.assertEqual(6000, result["contributionValueAtRetirement"])
        self.assertEqual(24000, result["investmentNeededToday"])
        self.assertEqual(
            [
                {"year": 0, "lumpSumValue": 24000, "contributionValue": 0, "totalValue": 24000},
                {"year": 1, "lumpSumValue": 24000, "contributionValue": 6000, "totalValue": 30000},
            ],
            result["annualAccumulation"],
        )

    def test_monthly_income_rises_annually_with_general_inflation(self) -> None:
        payload = level_cash_flow_payload()
        payload.update(
            {
                "currentAge": 58,
                "retirementAge": 60,
                "monthlyIncomeBeforeRetirement": 1000,
                "incomeInvestedRate": 0.5,
                "generalInflation": 0.10,
            }
        )
        result = calculate(payload)
        self.assertEqual(12600, result["contributionValueAtRetirement"])
        self.assertEqual(17400, result["investmentNeededToday"])
        self.assertEqual(6000, result["annualAccumulation"][1]["contributionValue"])
        self.assertEqual(12600, result["annualAccumulation"][2]["contributionValue"])

    def test_monthly_contributions_use_the_equivalent_monthly_return(self) -> None:
        payload = level_cash_flow_payload()
        payload.update(
            {
                "expectedPortfolioReturn": 0.12,
                "monthlyIncomeBeforeRetirement": 1000,
                "incomeInvestedRate": 0.1,
            }
        )
        result = calculate(payload)
        self.assertAlmostEqual(1264.6497908353188, result["contributionValueAtRetirement"], places=6)
        self.assertAlmostEqual(22889.161083255633, result["investmentNeededToday"], places=6)

    def test_contributions_above_the_target_floor_the_lump_sum_at_zero(self) -> None:
        payload = level_cash_flow_payload()
        payload.update(
            {
                "monthlyIncomeBeforeRetirement": 10000,
                "incomeInvestedRate": 1,
            }
        )
        result = calculate(payload)
        self.assertEqual(0, result["investmentNeededToday"])
        self.assertEqual(120000, result["contributionValueAtRetirement"])

    def test_inflation_projects_every_retirement_year(self) -> None:
        payload = level_cash_flow_payload()
        payload.update(
            {
                "horizonYears": 2,
                "expenseCategories": [{"amount": 12000, "inflationRate": 0.10}],
                "incomeStreams": [],
            }
        )
        result = calculate(payload)
        self.assertEqual([13200, 14520], result["annualFundingGaps"])
        self.assertEqual(27720, result["liquidPortfolio"])

    def test_annual_tax_expenses_are_inflated_with_general_expenses(self) -> None:
        payload = level_cash_flow_payload()
        payload.update(
            {
                "horizonYears": 2,
                "expenseCategories": [{"amount": 10_000, "inflationRate": 0}],
                "incomeStreams": [],
                "annualTaxExpenses": 2_000,
                "taxMode": "destination_estimate",
                "returnBasis": "after_fees_and_tax",
                "generalInflation": 0.10,
            }
        )
        result = calculate(payload)
        self.assertEqual([12200, 12420], result["annualFundingGaps"])
        self.assertEqual(24620, result["liquidPortfolio"])
        self.assertEqual(2200, result["annualTaxExpenses"])

    def test_omitted_tax_mode_is_not_labeled_after_tax_without_return_basis(self) -> None:
        result = calculate(level_cash_flow_payload())
        self.assertEqual("unspecified", result["taxMode"])
        self.assertEqual("unspecified", result["returnBasis"])
        self.assertEqual(0, result["annualTaxExpenses"])

    def test_omitted_tax_mode_defaults_after_tax_only_with_compatible_return_basis(self) -> None:
        payload = level_cash_flow_payload()
        payload["returnBasis"] = "after_fees_and_tax"
        result = calculate(payload)
        self.assertEqual("user_after_tax", result["taxMode"])
        self.assertEqual("after_fees_and_tax", result["returnBasis"])

    def test_destination_estimate_requires_scenario_expenses(self) -> None:
        payload = level_cash_flow_payload()
        payload["taxMode"] = "destination_estimate"
        payload["returnBasis"] = "after_fees_and_tax"
        with self.assertRaises(subprocess.CalledProcessError):
            calculate(payload)

    def test_tax_adjusted_expenses_require_after_tax_return_basis(self) -> None:
        payload = level_cash_flow_payload()
        payload.update({"annualTaxExpenses": 1_000, "returnBasis": "gross"})
        with self.assertRaises(subprocess.CalledProcessError):
            calculate(payload)

    def test_fixed_and_indexed_income_follow_different_paths(self) -> None:
        payload = level_cash_flow_payload()
        payload.update(
            {
                "horizonYears": 2,
                "expenseCategories": [{"amount": 10000, "inflationRate": 0}],
                "incomeStreams": [
                    {"amount": 1000, "indexed": True, "inflationRate": 0.10},
                    {"amount": 1000, "indexed": False, "inflationRate": 0.10},
                ],
            }
        )
        result = calculate(payload)
        self.assertEqual([7900, 7790], result["annualFundingGaps"])
        self.assertEqual(15690, result["liquidPortfolio"])

    def test_each_annual_gap_floors_at_zero_independently(self) -> None:
        payload = level_cash_flow_payload()
        payload.update(
            {
                "horizonYears": 2,
                "expenseCategories": [{"amount": 10000, "inflationRate": 0.10}],
                "incomeStreams": [{"amount": 11500, "indexed": False, "inflationRate": 0}],
            }
        )
        result = calculate(payload)
        self.assertEqual([0, 600], result["annualFundingGaps"])
        self.assertEqual(600, result["liquidPortfolio"])

    def test_buy_now_uses_today_price_without_mixing_dates(self) -> None:
        payload = level_cash_flow_payload()
        payload.update(
            {
                "housingPlan": "buy_now",
                "propertyPrice": 500000,
                "propertyInflation": 0.10,
                "acquisitionCostRate": 0.10,
            }
        )
        result = calculate(payload)
        self.assertEqual(550000, result["propertyCapital"])
        self.assertEqual("today", result["propertyTiming"])
        self.assertIsNone(result["combinedRetirementCapital"])
        self.assertEqual(550000, result["homePurchaseNeededToday"])
        self.assertEqual(result["retirementCapital"], result["totalCapitalAtRetirement"])
        self.assertEqual(
            result["investmentNeededToday"] + 550000,
            result["totalNeededToday"],
        )
        self.assertNotIn("totalCapital", result)
        self.assertNotIn("todayDollarTotal", result)

    def test_buy_at_retirement_projects_property(self) -> None:
        payload = level_cash_flow_payload()
        payload.update(
            {
                "currentAge": 58,
                "retirementAge": 60,
                "housingPlan": "buy_retirement",
                "propertyPrice": 500000,
                "propertyInflation": 0.10,
                "acquisitionCostRate": 0.10,
            }
        )
        result = calculate(payload)
        self.assertAlmostEqual(665500, result["propertyCapital"], places=6)
        self.assertEqual("retirement", result["propertyTiming"])
        self.assertAlmostEqual(result["retirementCapital"] + 665500, result["combinedRetirementCapital"], places=6)
        self.assertEqual(0, result["homePurchaseNeededToday"])
        self.assertAlmostEqual(result["combinedRetirementCapital"], result["totalCapitalAtRetirement"], places=6)
        self.assertAlmostEqual(
            result["combinedRetirementCapital"],
            result["investmentNeededToday"],
            places=6,
        )

    def test_rent_and_already_own_do_not_add_property_capital(self) -> None:
        for plan in ("rent", "own"):
            payload = level_cash_flow_payload()
            payload.update({"housingPlan": plan, "propertyPrice": 500000})
            result = calculate(payload)
            self.assertEqual(0, result["propertyCapital"])
            self.assertEqual("none", result["propertyTiming"])
            self.assertEqual(result["retirementCapital"], result["combinedRetirementCapital"])

    def test_income_can_cover_all_spending_without_negative_portfolio(self) -> None:
        payload = base_payload()
        payload["incomeStreams"] = [{"amount": 200000, "indexed": True, "inflationRate": 0.026}]
        result = calculate(payload)
        self.assertEqual(0, result["fundingGap"])
        self.assertEqual(0, result["liquidPortfolio"])
        self.assertIsNone(result["impliedFirstYearWithdrawal"])
        self.assertIsNone(result["netReturnAfterWithdrawal"])

    def test_expected_return_is_required_and_bounded(self) -> None:
        for value in (None, -0.051, 0.151):
            invalid = level_cash_flow_payload()
            invalid["expectedPortfolioReturn"] = value
            with self.assertRaises(subprocess.CalledProcessError):
                calculate(invalid)

    def test_invalid_age_and_inflation_inputs(self) -> None:
        for key, value in (("retirementAge", 49), ("generalInflation", -0.01)):
            invalid = base_payload()
            invalid[key] = value
            with self.assertRaises(subprocess.CalledProcessError):
                calculate(invalid)


if __name__ == "__main__":
    unittest.main()
