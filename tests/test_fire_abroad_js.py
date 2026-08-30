from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "fire_abroad.js"
UI = ROOT / "src" / "fire_abroad_ui.js"
CONTRACT = ROOT / "tests" / "fixtures" / "fire_abroad_contract.json"


def run_js(module: Path, function_name: str, payload: object) -> object:
    script = (
        "const mod=require(process.argv[1]);"
        "const value=JSON.parse(process.argv[2]);"
        f"process.stdout.write(JSON.stringify(mod.{function_name}(value)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(module), json.dumps(payload)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def run_js_call(module: Path, function_name: str, *arguments: object) -> object:
    script = (
        "const mod=require(process.argv[1]);"
        "const args=JSON.parse(process.argv[2]);"
        f"process.stdout.write(JSON.stringify(mod.{function_name}(...args)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(module), json.dumps(arguments)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


class FireAbroadJavaScriptParityTests(unittest.TestCase):
    """These fail if browser scoring diverges from the reviewed Python contract."""

    @staticmethod
    def route(status: str = "eligible", score: float | None = 4.0) -> dict:
        return {
            "status": status,
            "base_score": score,
            "summary": "The documented route fits the selected stay.",
            "work_permission": "remote_permitted",
        }

    def country(self) -> dict:
        return {
            "stay_routes": {
                mode: self.route() for mode in ("seasonal", "part_year", "full_relocation")
            },
            "tax": {
                "standard_day_threshold": 183,
                "non_day_tests": "A permanent home can trigger a separate residence test.",
                "by_mode": {
                    mode: {"status": "eligible", "rankable": True, "compatibility_score": 2.0}
                    for mode in ("seasonal", "part_year", "full_relocation")
                },
            },
            "healthcare": {
                "by_mode": {
                    mode: {"eligibility": "eligible", "bridge_score": 3.0}
                    for mode in ("seasonal", "part_year", "full_relocation")
                }
            },
        }

    @staticmethod
    def destination() -> dict:
        return {
            "id": "alpha",
            "name": "Alpha",
            "decision_dimensions": [
                {"key": "global_access", "score": 4.0},
                {"key": "foreigner_fit", "score": 3.0},
            ],
            "scores": {
                "exit_liquidity": {"score": 4.0},
                "ownership_clarity": {"score": 2.0},
            },
        }

    @staticmethod
    def cost() -> dict:
        return {
            "destination_id": "alpha",
            "profiles": {
                "single": {
                    "categories_usd": {"living": 50000, "contingency": 0},
                    "annual_rent_usd": 4545,
                    "annual_owner_costs_usd": 1000,
                }
            },
            "property": {"representative_price_usd": 100000, "acquisition_cost_rate": 0.1},
        }

    @staticmethod
    def override() -> dict:
        return {
            "country": "Example",
            "active_life": {
                "everyday_movement": {"score": 4.0, "summary": "Daily cycling and year-round park access."},
                "active_pursuits": {"score": 4.0, "summary": "Trails support regular outdoor pursuits."},
                "year_round_continuity": {"score": 4.0, "summary": "The climate supports activity through the year."},
                "activity_ecosystem": {"score": 4.0, "summary": "Local clubs create a social activity base."},
            },
            "rent_flexibility_score": 3.0,
            "one_time_relocation_usd": 5000,
            "risk_warnings": ["Heat plans matter in midsummer."],
            "confidence": "high",
            "last_reviewed": "2026-08-29",
        }

    def payload_for(self, case: dict) -> dict:
        country = self.country()
        if case["name"] == "exact_minimum_age":
            country["stay_routes"]["part_year"] = self.route("conditional")
            country["stay_routes"]["part_year"]["minimum_age"] = 50
        elif case["name"] == "full_relocation_unavailable":
            country["stay_routes"]["full_relocation"] = self.route("not_eligible")
        elif case["name"] == "consulting_passive_only":
            country["stay_routes"]["part_year"]["work_permission"] = "passive_only"
        return {
            "destinations": [self.destination()],
            "retirement_costs": {"alpha": self.cost()},
            "countries": {"Example": country},
            "destination_overrides": {"alpha": self.override()},
            "profile": case["raw_profile"],
        }

    def test_contract_cases_match_normalization_and_ranked_result_fields(self) -> None:
        cases = json.loads(CONTRACT.read_text(encoding="utf-8"))["cases"]
        self.assertGreaterEqual(len(cases), 6)
        for case in cases:
            with self.subTest(case=case["name"]):
                self.assertEqual(
                    case["normalized_profile"], run_js(ENGINE, "normalizeProfile", case["raw_profile"])
                )
                results = run_js(ENGINE, "rankDestinations", self.payload_for(case))
                expected = case["expected"]
                self.assertEqual(expected["ordered_ids"], [item["destination_id"] for item in results])
                self.assertEqual(expected["statuses"], [item["status"] for item in results])
                self.assertEqual(expected["scores"], [item["score"] for item in results])
                self.assertEqual(
                    expected["annual_budgets"],
                    [item["resilience_budget"]["annual_total_usd"] for item in results],
                )
                warnings = " ".join(results[0]["warnings"])
                for warning in expected["warning_substrings"]:
                    self.assertIn(warning, warnings)

    def test_budget_uses_the_destination_relocation_override(self) -> None:
        profile = run_js(ENGINE, "normalizeProfile", {})
        budget = run_js_call(
            ENGINE,
            "buildResilienceBudget",
            self.cost(),
            profile,
            {"one_time_relocation_usd": 7500},
        )
        self.assertEqual(7500, budget["one_time_relocation_usd"])
        self.assertEqual(60000, budget["annual_total_usd"])

    def test_missing_consolidated_score_stays_unranked(self) -> None:
        payload = self.payload_for({"name": "default", "raw_profile": {}})
        payload["destinations"][0]["decision_dimensions"] = [{"key": "foreigner_fit", "score": 3.0}]
        result = run_js(ENGINE, "rankDestinations", payload)[0]
        self.assertEqual("needs_verification", result["status"])
        self.assertIsNone(result["score"])
        self.assertIsNone(result["components"]["global_access"])


class FireAbroadJavaScriptPrivacyTests(unittest.TestCase):
    """These fail if private profile data can leave the browser or reach a URL."""

    def test_calculator_href_excludes_fire_profile_and_financial_details(self) -> None:
        href = run_js(UI, "safeCalculatorHref", {
            "destinationId": "valencia",
            "profile": {
                "household": "couple", "housing": "buy_now", "age": 52,
                "homeTaxContext": "us_person", "annualDays": 190,
                "incomeType": "business_consulting", "netWorth": 2500000,
            },
        })
        self.assertEqual(
            "/retirement-abroad-calculator/?destination=valencia&household=couple&housing=buy_now",
            href,
        )

    def test_calculator_href_falls_back_for_invalid_slug_or_categories(self) -> None:
        self.assertEqual(
            "/retirement-abroad-calculator/?destination=&household=single&housing=rent",
            run_js(UI, "safeCalculatorHref", {
                "destinationId": "../contact",
                "profile": {"household": "invalid", "housing": "own_now"},
            }),
        )

    def test_analytics_payload_is_allowlisted_and_drops_sensitive_details(self) -> None:
        safe = run_js_call(UI, "safeAnalyticsPayload", "calculator_handoff", {
            "destinationId": "valencia", "stayMode": "part_year", "activityPriority": "cycling",
            "age": 52, "mobilityRights": "local_free_movement", "homeTaxContext": "us_person",
            "annualDays": 190, "incomeType": "business_consulting", "annual_total_usd": 64000,
            "score": 4.2,
        })
        self.assertEqual(
            {"eventName": "calculator_handoff", "destinationId": "valencia"}, safe
        )
        self.assertIsNone(run_js_call(UI, "safeAnalyticsPayload", "profile_submit", {"destinationId": "valencia"}))

    def test_result_rows_keep_unranked_items_after_ranked_activity_matches(self) -> None:
        rows = run_js_call(UI, "resultRowsForDisplay", [
            {"destination_id": "ranked", "score": 4.0, "status": "eligible", "activity_tags": ["cycling"]},
            {"destination_id": "conditional", "score": None, "status": "needs_verification", "activity_tags": ["cycling"]},
            {"destination_id": "other", "score": 3.0, "status": "eligible", "activity_tags": ["walking"]},
        ], "cycling")
        self.assertEqual(["ranked", "conditional"], [row["destination_id"] for row in rows])

    def test_ui_source_has_no_network_storage_or_sensitive_analytics_fields(self) -> None:
        source = UI.read_text(encoding="utf-8")
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage", "innerHTML"):
            self.assertNotIn(forbidden, source)
        analytics_source = source.split("function safeAnalyticsPayload", 1)[1].split(
            "function resultRowsForDisplay", 1
        )[0]
        for sensitive_key in (
            "age", "mobilityRights", "homeTaxContext", "annualDays", "incomeType",
            "annual_total_usd", "property_capital_usd", "score",
        ):
            self.assertNotIn(sensitive_key, analytics_source)


if __name__ == "__main__":
    unittest.main()
