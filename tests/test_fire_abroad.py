import json
import unittest
from pathlib import Path

from src.fire_abroad import (
    build_resilience_budget,
    normalize_fire_profile,
    rank_fire_abroad_destinations,
    screen_eligibility,
    screen_tax,
)


ROOT = Path(__file__).resolve().parents[1]


def complete_tax_screen(*, central=0.12, readiness_score=3.0):
    return {
        "status": "complete",
        "residence": {"summary": "Residence depends on days and non-day tests."},
        "scope_if_resident": "worldwide_income",
        "funding_source_notes": {"portfolio": "Portfolio income may be taxable."},
        "tax_readiness": "moderate",
        "tax_readiness_score": readiness_score,
        "planning_bands": {
            "seasonal": {"favorable_rate": 0.0, "central_rate": 0.02, "adverse_rate": 0.05},
            "part_year": {"favorable_rate": 0.03, "central_rate": central, "adverse_rate": 0.22},
            "full_relocation": {"favorable_rate": 0.12, "central_rate": 0.22, "adverse_rate": 0.35},
        },
        "included_categories": ["income_tax_reserve", "compliance_reserve"],
        "material_flags": ["wealth_tax"],
        "source_ids": ["tax-source"],
        "confidence": "medium_high",
    }


def eligibility_screen():
    return {
        "status": "complete",
        "short_stay_source_ids": ["stay-source"],
        "long_stay_source_ids": ["residence-source"],
    }


def cost_record(destination_id, annual_rent):
    return {
        "destination_id": destination_id,
        "profiles": {
            "single": {
                "categories_usd": {"food": 12000, "travel": 4000},
                "annual_rent_usd": annual_rent,
                "annual_owner_costs_usd": 6000,
            },
            "couple": {
                "categories_usd": {"food": 18000, "travel": 6000},
                "annual_rent_usd": annual_rent + 4000,
                "annual_owner_costs_usd": 6000,
            },
        },
    }


class FireAbroadModelTests(unittest.TestCase):
    def test_quick_profile_defaults_do_not_require_financial_values(self):
        profile = normalize_fire_profile({})
        self.assertEqual("part_year", profile["stay_mode"])
        self.assertEqual("single", profile["household"])
        self.assertEqual("rent", profile["housing"])
        self.assertEqual("destination_estimate", profile["tax_mode"])
        self.assertIsNone(profile["planning_base"])

    def test_tax_reserve_uses_central_band_and_after_tax_mode_adds_nothing(self):
        country = {"tax_screen": complete_tax_screen()}
        estimated = screen_tax(
            country,
            normalize_fire_profile({"planning_base": 100000}),
        )
        supplied = screen_tax(
            country,
            normalize_fire_profile({"planning_base": 100000, "tax_mode": "user_after_tax"}),
        )
        self.assertEqual(3000, estimated["favorable_reserve"])
        self.assertEqual(12000, estimated["central_reserve"])
        self.assertEqual(22000, estimated["adverse_reserve"])
        self.assertEqual(0, supplied["central_reserve"])

    def test_day_band_funding_property_use_and_home_context_change_tax_screen(self):
        country = {"tax_screen": complete_tax_screen()}
        resident = screen_tax(country, normalize_fire_profile({
            "annual_day_band": "183_plus",
            "funding_source": "portfolio",
            "housing": "buy_now",
            "property_use": "rental",
            "home_tax_context": "citizenship_based_worldwide",
        }))
        visitor = screen_tax(country, normalize_fire_profile({
            "annual_day_band": "under_90",
            "funding_source": "pension",
            "housing": "rent",
            "home_tax_context": "residence_based",
        }))
        self.assertEqual("likely_resident", resident["residence_outcome"])
        self.assertEqual("residence_depends_on_days_and_ties", visitor["residence_outcome"])
        self.assertIn("Portfolio income", resident["scope_summary"])
        self.assertIn("property_rental_tax", resident["material_flags"])
        self.assertIn("continuing_home_country_tax", resident["material_flags"])
        self.assertNotEqual(resident["scope_summary"], visitor["scope_summary"])

    def test_each_visible_tax_control_changes_a_relevant_output(self):
        country = {"tax_screen": complete_tax_screen()}
        base = normalize_fire_profile({"planning_base": 100000, "annual_day_band": "unsure"})
        seasonal = screen_tax(country, {**base, "stay_mode": "seasonal"})
        relocated = screen_tax(country, {**base, "stay_mode": "full_relocation"})
        self.assertNotEqual(seasonal["central_reserve"], relocated["central_reserve"])
        under_90 = screen_tax(country, {**base, "annual_day_band": "under_90"})
        over_183 = screen_tax(country, {**base, "annual_day_band": "183_plus"})
        self.assertNotEqual(under_90["rates"], over_183["rates"])
        pension = screen_tax(country, {**base, "funding_source": "pension"})
        self.assertNotEqual(seasonal["scope_summary"], pension["scope_summary"])
        rental = screen_tax(country, {**base, "housing": "buy_now", "property_use": "rental"})
        self.assertTrue(any("Rental" in warning for warning in rental["warnings"]))
        territorial = screen_tax(country, {**base, "home_tax_context": "territorial"})
        residence_based = screen_tax(country, {**base, "home_tax_context": "residence_based"})
        self.assertNotEqual(territorial["warnings"], residence_based["warnings"])

    def test_eligibility_must_be_supported_before_ranking(self):
        country = {"eligibility": eligibility_screen()}
        free_movement = screen_eligibility(country, normalize_fire_profile({
            "mobility_rights": "local_free_movement",
            "annual_day_band": "183_plus",
        }))
        unknown = screen_eligibility(country, normalize_fire_profile({
            "mobility_rights": "prefer_not_to_say",
        }))
        self.assertEqual("likely_eligible", free_movement["status"])
        self.assertEqual("eligibility_depends_on_profile", unknown["status"])
        self.assertFalse(unknown["rankable"])

    def test_pending_tax_research_is_conditional_not_zero_tax(self):
        result = screen_tax(
            {"tax_screen": {"status": "research_pending"}},
            normalize_fire_profile({"planning_base": 100000}),
        )
        self.assertEqual("tax_impact_unavailable", result["status"])
        self.assertIsNone(result["central_reserve"])
        self.assertTrue(result["conditional"])

    def test_resilience_budget_adds_tax_only_in_destination_estimate_mode(self):
        cost = cost_record("alpha", 10000)
        estimated_profile = normalize_fire_profile({"planning_base": 50000})
        estimated_tax = screen_tax({"tax_screen": complete_tax_screen(central=0.10)}, estimated_profile)
        estimated = build_resilience_budget(cost, estimated_profile, estimated_tax)
        after_tax_profile = normalize_fire_profile({"tax_mode": "user_after_tax"})
        supplied_tax = screen_tax({"tax_screen": complete_tax_screen(central=0.10)}, after_tax_profile)
        supplied = build_resilience_budget(cost, after_tax_profile, supplied_tax)
        self.assertEqual(26000, supplied["central_annual_cost"])
        self.assertEqual(31000, estimated["central_annual_cost"])

    def test_ranking_keeps_pending_evidence_unranked(self):
        destinations = [
            {"id": "alpha", "name": "Alpha", "country": "Spain"},
            {"id": "beta", "name": "Beta", "country": "Portugal"},
        ]
        payload = {
            "countries": {
                "Spain": {"tax_screen": complete_tax_screen(), "eligibility": eligibility_screen()},
                "Portugal": {"tax_screen": {"status": "research_pending"}},
            },
            "destination_overrides": {
                "alpha": {
                    "country": "Spain",
                    "scores": {
                        "active_life": 4.0,
                        "healthcare_bridge": 4.0,
                        "stay_flexibility": 3.5,
                        "global_access": 4.0,
                        "community_fit": 4.0,
                        "property_exit_flexibility": 3.5,
                    },
                },
                "beta": {
                    "country": "Portugal",
                    "scores": {
                        "active_life": 4.5,
                        "healthcare_bridge": 4.0,
                        "stay_flexibility": 4.0,
                        "global_access": 4.0,
                        "community_fit": 4.0,
                        "property_exit_flexibility": 4.0,
                    },
                },
            },
        }
        costs = {"alpha": cost_record("alpha", 10000), "beta": cost_record("beta", 8000)}
        rows = rank_fire_abroad_destinations(
            destinations,
            costs,
            payload,
            {"mobility_rights": "local_free_movement"},
        )
        self.assertEqual("alpha", rows[0]["destination_id"])
        self.assertTrue(rows[0]["rankable"])
        self.assertFalse(rows[1]["rankable"])
        self.assertIsNone(rows[1]["overall_score"])

    def test_shared_screen_fixture_matches_python_contract(self):
        fixture = json.loads(
            (ROOT / "tests" / "fixtures" / "fire_abroad_screen_contract.json").read_text(encoding="utf-8")
        )
        for case in fixture["cases"]:
            result = screen_tax(
                {"tax_screen": case["tax_screen"]},
                normalize_fire_profile(case["profile"]),
            )
            self.assertEqual(case["expected"], {
                "status": result["status"],
                "residence_outcome": result["residence_outcome"],
                "favorable_reserve": result["favorable_reserve"],
                "central_reserve": result["central_reserve"],
                "adverse_reserve": result["adverse_reserve"],
            })


if __name__ == "__main__":
    unittest.main()
