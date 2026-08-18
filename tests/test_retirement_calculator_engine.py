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
    }


class RetirementCalculatorEngineTests(unittest.TestCase):
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
