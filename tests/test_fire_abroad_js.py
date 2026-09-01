from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "fire_abroad.js"
UI = ROOT / "src" / "fire_abroad_ui.js"
FIXTURE = ROOT / "tests" / "fixtures" / "fire_abroad_screen_contract.json"


def run_js(module: Path, function_name: str, payload: object) -> object:
    script = (
        "const api = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        f"process.stdout.write(JSON.stringify(api.{function_name}(input)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(module), json.dumps(payload)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


class FireAbroadJavaScriptTests(unittest.TestCase):
    def test_destination_tax_freshness_crosses_after_366_days_but_after_tax_mode_is_exempt(self):
        complete = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"][0]["tax_screen"]
        complete["last_reviewed"] = "2026-09-01"

        boundary = run_js(
            ENGINE,
            "screenTax",
            {"country": {"tax_screen": complete}, "profile": {"planning_base": 100000}, "asOf": "2027-09-02"},
        )
        crossed = run_js(
            ENGINE,
            "screenTax",
            {"country": {"tax_screen": complete}, "profile": {"planning_base": 100000}, "asOf": "2027-09-03"},
        )
        supplied = run_js(
            ENGINE,
            "screenTax",
            {
                "country": {"tax_screen": complete},
                "profile": {"planning_base": 100000, "tax_mode": "user_after_tax"},
                "asOf": "2027-09-03",
            },
        )

        self.assertEqual("planning_estimate", boundary["status"])
        self.assertEqual(12000, boundary["central_reserve"])
        self.assertEqual("tax_impact_unavailable", crossed["status"])
        self.assertTrue(crossed["conditional"])
        self.assertIsNone(crossed["central_reserve"])
        self.assertIsNone(crossed["readiness_score"])
        self.assertEqual("low", crossed["confidence"])
        self.assertIn("stale", crossed["scope_summary"].lower())
        self.assertEqual("user_after_tax", supplied["status"])
        self.assertEqual(0, supplied["central_reserve"])

    def test_stale_destination_remains_visible_but_is_unranked(self):
        complete = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"][0]["tax_screen"]
        complete["last_reviewed"] = "2026-09-01"
        result = run_js(
            ENGINE,
            "rankDestinations",
            {
                "asOf": "2027-09-03",
                "destinations": [{"id": "alpha", "name": "Alpha", "country": "Spain"}],
                "retirementCosts": {
                    "alpha": {"profiles": {"single": {"categories_usd": {"living": 16000}, "annual_rent_usd": 10000, "annual_owner_costs_usd": 6000}}}
                },
                "firePayload": {
                    "countries": {
                        "Spain": {"tax_screen": complete, "eligibility": {"status": "complete", "short_stay_source_ids": ["stay"], "long_stay_source_ids": ["residence"]}}
                    },
                    "destination_overrides": {
                        "alpha": {"country": "Spain", "scores": {"active_life": 4, "healthcare_bridge": 4, "stay_flexibility": 4, "global_access": 4, "community_fit": 4, "property_exit_flexibility": 4}}
                    },
                },
                "profile": {"mobility_rights": "local_free_movement"},
            },
        )
        supplied = run_js(
            ENGINE,
            "rankDestinations",
            {
                "asOf": "2027-09-03",
                "destinations": [{"id": "alpha", "name": "Alpha", "country": "Spain"}],
                "retirementCosts": {
                    "alpha": {"profiles": {"single": {"categories_usd": {"living": 16000}, "annual_rent_usd": 10000, "annual_owner_costs_usd": 6000}}}
                },
                "firePayload": {
                    "countries": {
                        "Spain": {"tax_screen": complete, "eligibility": {"status": "complete", "short_stay_source_ids": ["stay"], "long_stay_source_ids": ["residence"]}}
                    },
                    "destination_overrides": {
                        "alpha": {"country": "Spain", "scores": {"active_life": 4, "healthcare_bridge": 4, "stay_flexibility": 4, "global_access": 4, "community_fit": 4, "property_exit_flexibility": 4}}
                    },
                },
                "profile": {"mobility_rights": "local_free_movement", "tax_mode": "user_after_tax"},
            },
        )

        self.assertEqual(1, len(result))
        self.assertEqual("alpha", result[0]["destination_id"])
        self.assertFalse(result[0]["rankable"])
        self.assertIsNone(result[0]["overall_score"])
        self.assertIsNone(result[0]["budget"]["central_annual_cost"])
        self.assertEqual("tax_impact_unavailable", result[0]["tax"]["status"])
        self.assertTrue(supplied[0]["rankable"])
        self.assertEqual("user_after_tax", supplied[0]["tax"]["status"])

    def test_profile_defaults_match_python_contract(self):
        profile = run_js(ENGINE, "normalizeProfile", {})
        self.assertEqual("part_year", profile["stay_mode"])
        self.assertEqual("single", profile["household"])
        self.assertEqual("rent", profile["housing"])
        self.assertEqual("destination_estimate", profile["tax_mode"])
        self.assertIsNone(profile["planning_base"])

    def test_screen_tax_matches_shared_python_fixture(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        for case in fixture["cases"]:
            result = run_js(
                ENGINE,
                "screenTax",
                {"country": {"tax_screen": case["tax_screen"]}, "profile": case["profile"], "asOf": "2026-09-01"},
            )
            self.assertEqual(case["expected"], {
                "status": result["status"],
                "residence_outcome": result["residence_outcome"],
                "favorable_reserve": result["favorable_reserve"],
                "central_reserve": result["central_reserve"],
                "adverse_reserve": result["adverse_reserve"],
            })

    def test_tax_control_visibility_is_progressive(self):
        personal_renter = run_js(
            UI,
            "taxControlVisibility",
            {"housing": "rent", "taxMode": "destination_estimate", "wealthTaxRelevant": False},
        )
        self.assertEqual(
            {"propertyUse": False, "wealthBand": False, "planningInputs": True},
            personal_renter,
        )
        buyer = run_js(
            UI,
            "taxControlVisibility",
            {"housing": "buy_now", "taxMode": "destination_estimate", "wealthTaxRelevant": True},
        )
        self.assertEqual(
            {"propertyUse": True, "wealthBand": True, "planningInputs": True},
            buyer,
        )

    def test_resilience_budget_uses_central_reserve_once(self):
        result = run_js(
            ENGINE,
            "buildResilienceBudget",
            {
                "cost": {
                    "profiles": {
                        "single": {
                            "categories_usd": {"living": 16000},
                            "annual_rent_usd": 10000,
                            "annual_owner_costs_usd": 6000
                        }
                    }
                },
                "profile": {"planning_base": 50000},
                "taxScreen": {
                    "status": "planning_estimate",
                    "conditional": False,
                    "rates": {"favorable": 0.03, "central": 0.10, "adverse": 0.20}
                }
            },
        )
        self.assertEqual(26000, result["base_annual_cost"])
        self.assertEqual(31000, result["central_annual_cost"])

    def test_ranking_keeps_pending_tax_evidence_unranked(self):
        complete = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"][0]["tax_screen"]
        result = run_js(
            ENGINE,
            "rankDestinations",
            {
                "asOf": "2026-09-01",
                "destinations": [
                    {"id": "alpha", "name": "Alpha", "country": "Spain"},
                    {"id": "beta", "name": "Beta", "country": "Portugal"}
                ],
                "retirementCosts": {
                    "alpha": {"profiles": {"single": {"categories_usd": {"living": 16000}, "annual_rent_usd": 10000, "annual_owner_costs_usd": 6000}}},
                    "beta": {"profiles": {"single": {"categories_usd": {"living": 16000}, "annual_rent_usd": 8000, "annual_owner_costs_usd": 6000}}}
                },
                "firePayload": {
                    "countries": {
                        "Spain": {"tax_screen": complete, "eligibility": {"status": "complete", "short_stay_source_ids": ["stay"], "long_stay_source_ids": ["residence"]}},
                        "Portugal": {"tax_screen": {"status": "research_pending"}}
                    },
                    "destination_overrides": {
                        "alpha": {"country": "Spain", "scores": {"active_life": 4, "healthcare_bridge": 4, "stay_flexibility": 4, "global_access": 4, "community_fit": 4, "property_exit_flexibility": 4}},
                        "beta": {"country": "Portugal", "scores": {"active_life": 4, "healthcare_bridge": 4, "stay_flexibility": 4, "global_access": 4, "community_fit": 4, "property_exit_flexibility": 4}}
                    }
                },
                "profile": {"mobility_rights": "local_free_movement"}
            },
        )
        self.assertEqual("alpha", result[0]["destination_id"])
        self.assertTrue(result[0]["rankable"])
        self.assertFalse(result[1]["rankable"])

    def test_all_visible_tax_inputs_change_or_gate_the_result(self):
        complete = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"][0]["tax_screen"]
        baseline = run_js(ENGINE, "screenTax", {"country": {"tax_screen": complete}, "profile": {"annual_day_band": "under_90"}, "asOf": "2026-09-01"})
        changed = run_js(ENGINE, "screenTax", {"country": {"tax_screen": complete}, "profile": {
            "annual_day_band": "183_plus", "funding_source": "property", "housing": "buy_now",
            "property_use": "rental", "home_tax_context": "citizenship_based_worldwide"
        }, "asOf": "2026-09-01"})
        self.assertNotEqual(baseline["residence_outcome"], changed["residence_outcome"])
        self.assertNotEqual(baseline["scope_summary"], changed["scope_summary"])
        self.assertIn("property_rental_tax", changed["material_flags"])
        self.assertIn("continuing_home_country_tax", changed["material_flags"])

    def test_calculator_link_contains_only_existing_allowlisted_values(self):
        href = run_js(
            UI,
            "safeCalculatorHref",
            {
                "destinationId": "valencia",
                "household": "couple",
                "housing": "buy_now",
                "taxHome": "HK",
                "planningBase": 900000,
            },
        )
        self.assertEqual(
            "/retirement-abroad-calculator/?destination=valencia&household=couple&housing=buy_now",
            href,
        )

    def test_ui_does_not_persist_or_transmit_tax_inputs(self):
        source = UI.read_text(encoding="utf-8")
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage"):
            self.assertNotIn(forbidden, source)
        for sensitive_key in (
            "tax_home:",
            "annual_days:",
            "wealth_band:",
            "planning_base:",
            "tax_result:",
        ):
            self.assertNotIn(sensitive_key, source)

    def test_ui_reranks_in_memory_when_quick_controls_change(self):
        source = UI.read_text(encoding="utf-8")
        self.assertIn('addEventListener("change"', source)
        self.assertIn("GHAFireAbroad.rankDestinations", source)
        self.assertIn("replaceChildren", source)
        self.assertNotIn("innerHTML", source)

    def test_ui_ranking_input_forwards_serialized_freshness_anchor(self):
        result = run_js(
            UI,
            "rankingInput",
            {
                "payload": {
                    "asOf": "2027-09-03",
                    "destinations": [{"id": "alpha"}],
                    "retirementCosts": {"alpha": {}},
                    "fire": {"countries": {}},
                },
                "profile": {"tax_mode": "destination_estimate"},
            },
        )

        self.assertEqual("2027-09-03", result["asOf"])
        self.assertEqual([{"id": "alpha"}], result["destinations"])
        self.assertEqual("destination_estimate", result["profile"]["tax_mode"])


if __name__ == "__main__":
    unittest.main()
