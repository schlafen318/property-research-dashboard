from __future__ import annotations

import base64
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "src" / "retirement_finder_scenario.js"


def destination_ids() -> list[str]:
    return ["fukuoka", "valencia", "madeira"]


def scenario_input() -> dict:
    return {
        "currency": "USD",
        "projectedCapitalUsd": 1_250_000,
        "dataReviewed": "2026-08-27",
        "user": {
            "currentAge": 48,
            "totalLiquidCapital": 600_000,
            "monthlyPortfolioContribution": 2_500,
            "incomeStreams": [{"amount": 30_000}],
            "household": "couple",
            "horizonYears": 30,
            "housingPlan": "rent",
            "preferences": {"region": "Asia", "climate": "coast", "healthcare": "high"},
        },
        "result": {
            "recommendations": [
                {
                    "destinationId": "fukuoka",
                    "retirementTarget": 1_000_000,
                    "surplusGap": 250_000,
                    "fundingRatio": 1.25,
                    "tier": "within_reach",
                    "preferenceMatches": ["Preferred region", "Stronger healthcare signal"],
                },
                {
                    "destinationId": "valencia",
                    "retirementTarget": 1_300_000,
                    "surplusGap": -50_000,
                    "fundingRatio": 0.961538,
                    "tier": "close",
                    "preferenceMatches": ["Preferred setting"],
                },
                {
                    "destinationId": "madeira",
                    "retirementTarget": 1_600_000,
                    "surplusGap": -350_000,
                    "fundingRatio": 0.78125,
                    "tier": "stretch",
                    "preferenceMatches": [],
                },
            ]
        },
    }


def run_scenario(function_name: str, payload: object) -> object:
    script = (
        "const api = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        f"const output = input && input.__args ? api.{function_name}.apply(null, input.__args) : api.{function_name}(input);"
        "process.stdout.write(JSON.stringify(output));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(SCENARIO), json.dumps(payload)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def run_scenario_failure(function_name: str, payload: object) -> str:
    script = (
        "const api = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        f"if (input && input.__args) api.{function_name}.apply(null, input.__args); else api.{function_name}(input);"
    )
    result = subprocess.run(
        ["node", "-e", script, str(SCENARIO), json.dumps(payload)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        raise AssertionError("Expected scenario operation to fail")
    return result.stderr


def encode_unchecked(payload: object) -> str:
    raw = json.dumps(payload, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


class RetirementFinderScenarioTests(unittest.TestCase):
    def test_build_scenario_keeps_outcomes_and_drops_raw_financial_inputs(self) -> None:
        scenario = run_scenario("buildScenario", scenario_input())

        self.assertEqual(1, scenario["v"])
        self.assertEqual(1_250_000, scenario["projectedCapitalUsd"])
        self.assertEqual(["fukuoka", "valencia", "madeira"], scenario["comparisonIds"])
        serialized = json.dumps(scenario)
        for forbidden in ("currentAge", "totalLiquidCapital", "monthlyPortfolioContribution", "incomeStreams"):
            self.assertNotIn(forbidden, serialized)

    def test_codec_round_trips_url_safe_payload(self) -> None:
        scenario = run_scenario("buildScenario", scenario_input())
        encoded = run_scenario("encodeScenario", scenario)

        self.assertRegex(encoded, r"^[A-Za-z0-9_-]+$")
        self.assertEqual(
            scenario,
            run_scenario("decodeScenario", {"value": encoded, "destinationIds": destination_ids()}),
        )

    def test_decode_rejects_unknown_version_and_duplicate_destinations(self) -> None:
        valid = run_scenario("buildScenario", scenario_input())
        valid["v"] = 2
        encoded = encode_unchecked(valid)
        self.assertIn(
            "Unsupported results-link version",
            run_scenario_failure("decodeScenario", {"value": encoded, "destinationIds": destination_ids()}),
        )

        duplicate = run_scenario("buildScenario", scenario_input())
        duplicate["results"][1]["destinationId"] = "fukuoka"
        encoded = encode_unchecked(duplicate)
        self.assertIn(
            "Destination IDs must be unique",
            run_scenario_failure("decodeScenario", {"value": encoded, "destinationIds": destination_ids()}),
        )

    def test_decode_rejects_oversized_payload_before_parsing(self) -> None:
        self.assertIn(
            "Results link is too large",
            run_scenario_failure(
                "decodeScenario",
                {"value": "a" * 17_000, "destinationIds": destination_ids()},
            ),
        )

    def test_validation_rejects_unknown_destination_and_non_finite_numbers(self) -> None:
        scenario = run_scenario("buildScenario", scenario_input())
        scenario["results"][0]["destinationId"] = "unknown"
        self.assertIn(
            "Unknown destination",
            run_scenario_failure(
                "validateScenario",
                {"__args": [scenario, destination_ids()]},
            ),
        )

        scenario = run_scenario("buildScenario", scenario_input())
        scenario["projectedCapitalUsd"] = None
        self.assertIn(
            "Projected capital must be finite",
            run_scenario_failure(
                "validateScenario",
                {"__args": [scenario, destination_ids()]},
            ),
        )

    def test_decode_omits_destinations_removed_since_link_creation(self) -> None:
        scenario = run_scenario("buildScenario", scenario_input())
        encoded = run_scenario("encodeScenario", scenario)
        decoded = run_scenario(
            "decodeScenario",
            {"value": encoded, "destinationIds": ["fukuoka", "valencia"]},
        )
        self.assertEqual(["fukuoka", "valencia"], [item["destinationId"] for item in decoded["results"]])
        self.assertEqual(["fukuoka", "valencia"], decoded["comparisonIds"])

    def test_validation_rejects_impossible_review_date(self) -> None:
        scenario = run_scenario("buildScenario", scenario_input())
        scenario["dataReviewed"] = "2026-99-99"
        self.assertIn(
            "Data review date is invalid",
            run_scenario_failure("validateScenario", {"__args": [scenario, destination_ids()]}),
        )


if __name__ == "__main__":
    unittest.main()
