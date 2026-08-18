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
        "portfolioCashYield": 0.02,
    }


class RetirementCalculatorEngineTests(unittest.TestCase):
    def test_guided_withdrawal_rate_tiers(self) -> None:
        expected = {25: 0.04, 26: 0.035, 30: 0.035, 31: 0.0325, 35: 0.0325, 36: 0.03}
        for horizon, rate in expected.items():
            self.assertEqual(rate, run_engine("guidedWithdrawalRate", horizon))

    def test_projects_expenses_and_indexed_income(self) -> None:
        result = calculate(base_payload())
        factor = 1.026**10
        self.assertAlmostEqual(100000 * factor, result["firstYearExpenses"], places=4)
        self.assertAlmostEqual(20000 * factor + 10000, result["outsideIncome"], places=4)
        self.assertAlmostEqual(result["firstYearExpenses"] - result["outsideIncome"], result["fundingGap"], places=4)
        self.assertEqual(0.035, result["withdrawalRate"])

    def test_portfolio_income_is_part_of_the_withdrawal(self) -> None:
        result = calculate(base_payload())
        self.assertAlmostEqual(result["fundingGap"], result["portfolioCashIncome"] + result["assetSales"], places=4)
        self.assertAlmostEqual(result["fundingGap"] / 0.035, result["liquidPortfolio"], places=4)

    def test_property_capital_only_applies_to_buy(self) -> None:
        rent_result = calculate(base_payload())
        buy = base_payload()
        buy["housingPlan"] = "buy"
        buy_result = calculate(buy)
        projected_property = 500000 * 1.026**10
        self.assertEqual(0, rent_result["propertyCapital"])
        self.assertAlmostEqual(projected_property * 1.1, buy_result["propertyCapital"], places=4)

    def test_income_can_cover_all_spending_without_negative_portfolio(self) -> None:
        payload = base_payload()
        payload["incomeStreams"] = [{"amount": 200000, "indexed": True, "inflationRate": 0.026}]
        result = calculate(payload)
        self.assertEqual(0, result["fundingGap"])
        self.assertEqual(0, result["liquidPortfolio"])
        self.assertEqual(0, result["assetSales"])

    def test_override_and_invalid_inputs(self) -> None:
        payload = base_payload()
        payload["withdrawalRateOverride"] = 0.04
        self.assertEqual(0.04, calculate(payload)["withdrawalRate"])

        for key, value in (("retirementAge", 49), ("generalInflation", -0.01), ("withdrawalRateOverride", 0.05)):
            invalid = base_payload()
            invalid[key] = value
            with self.assertRaises(subprocess.CalledProcessError):
                calculate(invalid)


if __name__ == "__main__":
    unittest.main()
