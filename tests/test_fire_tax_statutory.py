from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src" / "fire_tax_statutory.js"


def run_engine(function_name: str, payload: dict) -> dict:
    script = (
        "const engine=require(process.argv[1]);"
        "const payload=JSON.parse(process.argv[2]);"
        "process.stdout.write(JSON.stringify(engine[process.argv[3]](payload.input,payload.rule)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(MODULE), json.dumps(payload), function_name],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


def base_rule(capital_gains: dict) -> dict:
    return {
        "country": "Example",
        "tax_year": 2026,
        "checked_on": "2026-09-01",
        "review_interval_days": 90,
        "currency": "USD",
        "residence_assumption": "full_year_resident",
        "portfolio_scope": "personal_taxable_listed_securities",
        "capital_gains": capital_gains,
        "source_ids": ["official-example-2026"],
    }


class FireTaxStatutoryTests(unittest.TestCase):
    def test_flat_gain_rule_returns_disclosed_zero_half_and_full_gain_cases(self):
        result = run_engine(
            "estimateStatutoryTaxRange",
            {
                "input": {
                    "portfolioWithdrawals": 40_000,
                    "dependableIncome": 0,
                    "gainShares": [0, 0.5, 1],
                    "fxToUsd": 1,
                    "asOf": "2026-09-01",
                },
                "rule": base_rule(
                    {"base": "gain", "calculation": "flat_rate", "rate": 0.2}
                ),
            },
        )

        self.assertEqual("available", result["status"])
        self.assertEqual([0, 4_000, 8_000], [case["capitalGainsTax"] for case in result["cases"]])
        self.assertEqual(4_000, result["estimate"])
        self.assertEqual(0, result["minimum"])
        self.assertEqual(8_000, result["maximum"])
        self.assertEqual([0, 0.5, 1], [case["gainShare"] for case in result["cases"]])

    def test_progressive_rule_applies_each_marginal_band_in_rule_currency(self):
        result = run_engine(
            "estimateStatutoryTaxRange",
            {
                "input": {
                    "portfolioWithdrawals": 30_000,
                    "dependableIncome": 0,
                    "gainShares": [0, 0.5, 1],
                    "fxToUsd": 1,
                    "asOf": "2026-09-01",
                },
                "rule": base_rule(
                    {
                        "base": "gain",
                        "calculation": "progressive_rate",
                        "bands": [
                            {"up_to": 10_000, "rate": 0.1},
                            {"up_to": None, "rate": 0.2},
                        ],
                    }
                ),
            },
        )

        self.assertEqual([0, 2_000, 5_000], [case["capitalGainsTax"] for case in result["cases"]])

    def test_proceeds_rule_taxes_withdrawal_not_assumed_gain(self):
        result = run_engine(
            "estimateStatutoryTaxRange",
            {
                "input": {
                    "portfolioWithdrawals": 40_000,
                    "gainShares": [0, 0.5, 1],
                    "fxToUsd": 1,
                    "asOf": "2026-09-01",
                },
                "rule": base_rule(
                    {"base": "proceeds", "calculation": "proceeds_rate", "rate": 0.001}
                ),
            },
        )

        self.assertEqual([40, 40, 40], [case["capitalGainsTax"] for case in result["cases"]])
        self.assertEqual(40, result["minimum"])
        self.assertEqual(40, result["maximum"])

    def test_holding_period_exemption_uses_only_a_disclosed_rule_assumption(self):
        rule = base_rule(
            {
                "base": "gain",
                "calculation": "holding_period_exemption",
                "rate": 0.12,
                "exemption_after_years": 2,
                "holding_period_assumption_years": 3,
            }
        )
        result = run_engine(
            "estimateStatutoryTaxRange",
            {
                "input": {
                    "portfolioWithdrawals": 40_000,
                    "gainShares": [0, 0.5, 1],
                    "fxToUsd": 1,
                    "asOf": "2026-09-01",
                },
                "rule": rule,
            },
        )

        self.assertEqual([0, 0, 0], [case["capitalGainsTax"] for case in result["cases"]])
        self.assertIn("holding-period exemption", result["explanations"][0]["reason"])

    def test_stale_rule_is_unavailable_instead_of_falling_back(self):
        rule = base_rule({"base": "gain", "calculation": "flat_rate", "rate": 0.2})
        rule["checked_on"] = "2025-01-01"
        result = run_engine(
            "estimateStatutoryTaxRange",
            {
                "input": {
                    "portfolioWithdrawals": 40_000,
                    "gainShares": [0, 0.5, 1],
                    "fxToUsd": 1,
                    "asOf": "2026-09-01",
                },
                "rule": rule,
            },
        )

        self.assertEqual("unavailable", result["status"])
        self.assertNotIn("estimate", result)


if __name__ == "__main__":
    unittest.main()
