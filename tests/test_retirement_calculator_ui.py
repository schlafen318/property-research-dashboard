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

    def test_owner_plans_use_owner_costs(self) -> None:
        profile = {
            "categories_usd": {"food": 20_000, "healthcare": 5_000},
            "annual_rent_usd": 24_000,
            "annual_owner_costs_usd": 8_000,
        }
        self.assertEqual(49_000, run_ui("annualBenchmark", {"profile": profile, "plan": "rent"}))
        for plan in ("own", "buy_now", "buy_retirement"):
            self.assertEqual(33_000, run_ui("annualBenchmark", {"profile": profile, "plan": plan}))

    def test_only_purchase_plans_use_property_budget(self) -> None:
        self.assertFalse(run_ui("usesPropertyBudget", "rent"))
        self.assertFalse(run_ui("usesPropertyBudget", "own"))
        self.assertTrue(run_ui("usesPropertyBudget", "buy_now"))
        self.assertTrue(run_ui("usesPropertyBudget", "buy_retirement"))

    def test_disabled_hidden_number_does_not_block_calculation(self) -> None:
        self.assertFalse(
            run_ui(
                "isInvalidNumericControl",
                {"disabled": True, "value": "", "valid": False},
            )
        )
        self.assertTrue(
            run_ui(
                "isInvalidNumericControl",
                {"disabled": False, "value": "", "valid": False},
            )
        )

    def test_negative_net_return_is_flagged(self) -> None:
        self.assertTrue(run_ui("isNegativeRate", -0.001))
        self.assertFalse(run_ui("isNegativeRate", 0))
        self.assertFalse(run_ui("isNegativeRate", 0.001))

    def test_housing_guidance_distinguishes_rent_owner_costs_and_purchase_budget(self) -> None:
        self.assertEqual(
            "Monthly retirement living expenses, including rent.",
            run_ui("housingGuidance", "rent"),
        )
        self.assertEqual(
            "Monthly retirement living expenses, including owner running costs; no new home purchase.",
            run_ui("housingGuidance", "own"),
        )
        self.assertEqual(
            "Monthly retirement living expenses after purchase, including owner running costs but not the home purchase.",
            run_ui("housingGuidance", "buy_now"),
        )
        self.assertEqual(
            "Monthly retirement living expenses after purchase, including owner running costs but not the home purchase at retirement.",
            run_ui("housingGuidance", "buy_retirement"),
        )


if __name__ == "__main__":
    unittest.main()
