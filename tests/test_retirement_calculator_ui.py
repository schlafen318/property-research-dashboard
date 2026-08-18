from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI_MODULE = ROOT / "src" / "retirement_calculator_ui.js"


def run_ui(function_name: str, payload: object) -> object:
    script = (
        "const ui = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        f"process.stdout.write(JSON.stringify(ui.{function_name}(input)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(UI_MODULE), json.dumps(payload)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class RetirementCalculatorUITests(unittest.TestCase):
    def test_converts_monthly_spending_to_annual_for_the_engine(self) -> None:
        self.assertEqual(64_596, run_ui("annualSpendingFromMonthly", 5_383))

    def test_buying_uses_owner_costs_instead_of_rent(self) -> None:
        profile = {
            "categories_usd": {"food": 20_000, "healthcare": 5_000},
            "annual_rent_usd": 24_000,
            "annual_owner_costs_usd": 8_000,
        }
        self.assertEqual(49_000, run_ui("annualBenchmark", {"profile": profile, "plan": "rent"}))
        self.assertEqual(33_000, run_ui("annualBenchmark", {"profile": profile, "plan": "buy"}))

    def test_housing_guidance_distinguishes_rent_owner_costs_and_purchase_budget(self) -> None:
        self.assertEqual(
            "Includes rent and other living costs.",
            run_ui("housingGuidance", "rent"),
        )
        self.assertEqual(
            "Includes owner running costs after purchase, not rent. Enter the home purchase budget separately.",
            run_ui("housingGuidance", "buy"),
        )


if __name__ == "__main__":
    unittest.main()
