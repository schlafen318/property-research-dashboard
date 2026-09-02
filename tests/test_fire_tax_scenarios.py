from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "fire_tax_scenarios.js"


def run_scenario(payload: object) -> object:
    script = (
        "const scenarios = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        "process.stdout.write(JSON.stringify("
        "scenarios.estimateTaxScenario(input.input, input.country)"
        "));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(ENGINE), json.dumps(payload)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def portugal_rule() -> dict:
    return {
        "country": "Portugal",
        "tax_year": 2026,
        "checked_on": "2026-09-01",
        "review_interval_days": 90,
        "currency": "EUR",
        "residence_assumption": "full_year_resident",
        "portfolio_scope": "personal_taxable_listed_securities",
        "capital_gains": {"base": "gain", "calculation": "flat_rate", "rate": 0.28},
        "source_ids": ["portugal-securities-gains-2026"],
    }


class FireTaxScenarioTests(unittest.TestCase):
    def test_adapter_maps_zero_half_and_full_gain_cases_to_existing_target_contract(self) -> None:
        result = run_scenario({
            "input": {
                "taxMode": "destination_estimate",
                "dependableIncome": 20_000,
                "portfolioWithdrawals": 60_000,
                "gainShares": [0, 0.5, 1],
                "fxToUsd": 1.2,
                "asOf": "2026-09-02",
            },
            "country": {"statutory_screening": portugal_rule()},
        })

        self.assertEqual("available", result["status"])
        self.assertEqual(0, result["cases"]["favorable"]["total"])
        self.assertEqual(8_400, result["cases"]["central"]["total"])
        self.assertEqual(16_800, result["cases"]["adverse"]["total"])
        self.assertEqual(30_000, result["cases"]["central"]["realizedGain"])
        self.assertEqual(60_000, result["planningBase"])
        self.assertEqual("2026", result["taxYear"])
        self.assertTrue(result["statutory"])

    def test_missing_or_stale_statutory_rule_is_unavailable_without_generic_fallback(self) -> None:
        missing = run_scenario({
            "input": {"taxMode": "destination_estimate", "asOf": "2026-09-02"},
            "country": {},
        })
        stale_rule = portugal_rule()
        stale_rule["checked_on"] = "2025-01-01"
        stale = run_scenario({
            "input": {
                "taxMode": "destination_estimate",
                "portfolioWithdrawals": 20_000,
                "gainShares": [0, 0.5, 1],
                "fxToUsd": 1.2,
                "asOf": "2026-09-02",
            },
            "country": {"statutory_screening": stale_rule},
        })

        self.assertEqual("unavailable", missing["status"])
        self.assertEqual("unavailable", stale["status"])
        self.assertTrue(stale["conditional"])

    def test_user_after_tax_mode_keeps_one_zero_case(self) -> None:
        result = run_scenario({"input": {"taxMode": "user_after_tax"}, "country": {}})

        self.assertEqual("user_after_tax", result["status"])
        self.assertEqual(["user_after_tax"], list(result["cases"]))
        self.assertEqual(0, result["cases"]["user_after_tax"]["total"])


if __name__ == "__main__":
    unittest.main()
