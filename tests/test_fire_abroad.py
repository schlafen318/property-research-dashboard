from __future__ import annotations

import copy
import unittest
import json
import math
from pathlib import Path

from src.fire_abroad import (
    annual_cost_score,
    build_resilience_budget,
    eligibility_for_mode,
    normalize_fire_profile,
    active_life_score,
    load_fire_abroad,
    rank_fire_abroad_destinations,
    resolve_country_record,
)


ROOT = Path(__file__).resolve().parents[1]


class FireProfileTests(unittest.TestCase):
    """The change that should break these tests is incorrect profile/route handling."""

    def country_fixture(self, full_relocation_status: str = "eligible") -> dict:
        def route(status: str, *, minimum_age: int | None = None, max_days: int | None = None) -> dict:
            score = 4.0 if status not in {"needs_verification", "not_eligible"} else None
            return {
                "status": status,
                "base_score": score,
                "max_days": max_days,
                "minimum_age": minimum_age,
                "summary": "A documented route is available.",
                "work_permission": "remote_permitted",
                "mobility_rights": {
                    "local_free_movement": {
                        "status": "eligible",
                        "base_score": 5.0,
                        "max_days": None,
                        "work_permission": "local_permitted",
                    },
                    "general_nonlocal": {
                        "status": status,
                        "base_score": score,
                        "max_days": max_days,
                        "work_permission": "remote_permitted",
                    },
                    "prefer_not_to_say": {
                        "status": "needs_verification" if status in {"needs_verification", "not_eligible"} else status,
                        "base_score": score,
                        "max_days": max_days,
                        "work_permission": "remote_permitted",
                    },
                },
            }

        return {
            "stay_routes": {
                "seasonal": route("conditional", max_days=90),
                "part_year": route("conditional", minimum_age=50),
                "full_relocation": route(full_relocation_status),
            }
        }

    def test_profile_defaults_are_the_static_page_defaults(self) -> None:
        self.assertEqual(
            {
                "stay_mode": "part_year", "age": 50, "household": "single",
                "housing": "rent", "mobility_rights": "prefer_not_to_say",
                "home_tax_context": "prefer_not_to_say", "annual_days": None,
                "income_type": "prefer_not_to_say", "activity_priority": "balanced",
            },
            normalize_fire_profile({}),
        )

    def test_profile_normalizes_invalid_values_and_age_boundaries(self) -> None:
        self.assertEqual(
            {
                "stay_mode": "part_year", "age": 100, "household": "single",
                "housing": "rent", "mobility_rights": "prefer_not_to_say",
                "home_tax_context": "prefer_not_to_say", "annual_days": None,
                "income_type": "prefer_not_to_say", "activity_priority": "balanced",
            },
            normalize_fire_profile(
                {"stay_mode": "invalid", "age": 120, "annual_days": 0, "housing": "shed"}
            ),
        )
        self.assertEqual(18, normalize_fire_profile({"age": -1})["age"])
        self.assertEqual(366, normalize_fire_profile({"annual_days": 366})["annual_days"])

    def test_every_stay_mode_uses_its_matching_route(self) -> None:
        country = self.country_fixture()
        self.assertEqual(
            "conditional",
            eligibility_for_mode(country, normalize_fire_profile({"stay_mode": "seasonal"}))["status"],
        )
        self.assertEqual(
            "conditional",
            eligibility_for_mode(country, normalize_fire_profile({"stay_mode": "part_year"}))["status"],
        )
        self.assertEqual(
            "eligible",
            eligibility_for_mode(country, normalize_fire_profile({"stay_mode": "full_relocation"}))["status"],
        )

    def test_missing_mobility_rights_are_never_promoted_to_eligibility(self) -> None:
        country = self.country_fixture()
        country["stay_routes"]["seasonal"]["mobility_rights"] = {
            "local_free_movement": {
                "status": "eligible", "base_score": 5.0, "max_days": None,
                "work_permission": "local_permitted",
            },
            "general_nonlocal": {
                "status": "conditional", "base_score": 4.0, "max_days": 90,
                "work_permission": "remote_permitted",
            },
        }
        result = eligibility_for_mode(country, normalize_fire_profile({"stay_mode": "seasonal"}))
        self.assertEqual("needs_verification", result["status"])

    def test_minimum_age_is_inclusive(self) -> None:
        country = self.country_fixture()
        at_minimum = eligibility_for_mode(country, normalize_fire_profile({"age": 50}))
        below_minimum = eligibility_for_mode(country, normalize_fire_profile({"age": 49}))
        self.assertEqual("conditional", at_minimum["status"])
        self.assertEqual("not_eligible", below_minimum["status"])

    def test_no_long_term_route_blocks_full_relocation_only(self) -> None:
        country = self.country_fixture(full_relocation_status="not_eligible")
        seasonal = eligibility_for_mode(country, normalize_fire_profile({
            "stay_mode": "seasonal", "mobility_rights": "general_nonlocal",
        }))
        relocation = eligibility_for_mode(country, normalize_fire_profile({
            "stay_mode": "full_relocation", "mobility_rights": "general_nonlocal",
        }))
        self.assertEqual("conditional", seasonal["status"])
        self.assertEqual("not_eligible", relocation["status"])

    def test_route_day_cap_is_inclusive_and_fails_closed_by_mobility_profile(self) -> None:
        country = self.country_fixture()
        at_cap = eligibility_for_mode(
            country,
            normalize_fire_profile({
                "stay_mode": "seasonal", "mobility_rights": "general_nonlocal", "annual_days": 90,
            }),
        )
        over_cap = eligibility_for_mode(
            country,
            normalize_fire_profile({
                "stay_mode": "seasonal", "mobility_rights": "general_nonlocal", "annual_days": 91,
            }),
        )
        unknown_over_cap = eligibility_for_mode(
            country,
            normalize_fire_profile({
                "stay_mode": "seasonal", "mobility_rights": "prefer_not_to_say", "annual_days": 91,
            }),
        )
        local_over_cap = eligibility_for_mode(
            country,
            normalize_fire_profile({
                "stay_mode": "seasonal", "mobility_rights": "local_free_movement", "annual_days": 365,
            }),
        )

        self.assertEqual(("conditional", 90), (at_cap["status"], at_cap["max_days"]))
        self.assertEqual(("not_eligible", None), (over_cap["status"], over_cap["stay_score"]))
        self.assertIn("91", over_cap["reason"])
        self.assertEqual("needs_verification", unknown_over_cap["status"])
        self.assertEqual(("eligible", "local_permitted", None), (
            local_over_cap["status"], local_over_cap["work_permission"], local_over_cap["max_days"],
        ))

    def test_actual_eu_and_nonlocal_profiles_select_different_portugal_routes(self) -> None:
        country = load_fire_abroad()["countries"]["Portugal"]
        local = eligibility_for_mode(country, normalize_fire_profile({
            "stay_mode": "seasonal", "mobility_rights": "local_free_movement", "annual_days": 120,
        }))
        nonlocal_profile = eligibility_for_mode(country, normalize_fire_profile({
            "stay_mode": "seasonal", "mobility_rights": "general_nonlocal", "annual_days": 120,
        }))

        self.assertEqual("eligible", local["status"])
        self.assertEqual("local_permitted", local["work_permission"])
        self.assertEqual("not_eligible", nonlocal_profile["status"])


class ResilienceBudgetTests(unittest.TestCase):
    """The change that should break these tests is a double-counted or omitted budget item."""

    def cost_fixture(self) -> dict:
        return {
            "profiles": {
                "single": {
                    "categories_usd": {
                        "food_household": 10000,
                        "utilities_communications": 0,
                        "private_healthcare": 1000,
                        "transport": 0,
                        "dining_leisure": 0,
                        "travel": 600,
                        "visa_admin": 200,
                        "contingency": 1400,
                    },
                    "annual_rent_usd": 12000,
                    "annual_owner_costs_usd": 1800,
                }
            },
            "property": {
                "representative_price_usd": 200000,
                "acquisition_cost_rate": 0.08,
            },
        }

    def test_resilience_budget_does_not_double_count_shared_categories(self) -> None:
        budget = build_resilience_budget(self.cost_fixture(), normalize_fire_profile({"housing": "rent"}))
        self.assertEqual(1000, budget["categories"]["private_healthcare"])
        self.assertEqual(600, budget["categories"]["travel"])
        self.assertEqual(200, budget["categories"]["visa_admin"])
        recurring_without_contingency = sum(
            value for key, value in budget["categories"].items() if key != "contingency"
        )
        self.assertEqual(round(recurring_without_contingency * 0.10), budget["currency_inflation_buffer"])
        self.assertEqual(27580, budget["annual_total_usd"])

    def test_owner_budget_replaces_rent_with_owner_costs(self) -> None:
        budget = build_resilience_budget(self.cost_fixture(), normalize_fire_profile({"housing": "own"}))
        self.assertEqual(1800, budget["categories"]["owner_costs"])
        self.assertNotIn("rent", budget["categories"])
        self.assertEqual(16360, budget["annual_total_usd"])
        self.assertEqual(0, budget["property_capital_usd"])

    def test_buy_now_budget_includes_acquisition_capital_separately(self) -> None:
        budget = build_resilience_budget(self.cost_fixture(), normalize_fire_profile({"housing": "buy_now"}))
        self.assertEqual(216000, budget["property_capital_usd"])
        self.assertEqual(16360, budget["annual_total_usd"])

    def test_buy_at_retirement_uses_rent_for_screening_budget(self) -> None:
        budget = build_resilience_budget(self.cost_fixture(), normalize_fire_profile({"housing": "buy_retirement"}))
        self.assertEqual(12000, budget["categories"]["rent"])
        self.assertEqual(216000, budget["property_capital_usd"])
        self.assertEqual(27580, budget["annual_total_usd"])

    def test_relocation_cost_comes_from_the_destination_override(self) -> None:
        budget = build_resilience_budget(
            self.cost_fixture(), normalize_fire_profile({}), {"one_time_relocation_usd": 7500}
        )
        self.assertEqual(7500, budget["one_time_relocation_usd"])

    def test_cost_score_uses_fixed_household_anchors(self) -> None:
        self.assertEqual(5.0, annual_cost_score(30000, "single"))
        self.assertEqual(2.5, annual_cost_score(60000, "single"))
        self.assertEqual(0.0, annual_cost_score(90000, "single"))
        self.assertEqual(5.0, annual_cost_score(45000, "couple"))

    def test_two_decimal_ties_use_half_up_rounding(self) -> None:
        ties = json.loads((ROOT / "tests/fixtures/fire_abroad_contract.json").read_text())[
            "rounding_ties"
        ]
        self.assertEqual(
            ties["annual_cost_score"]["expected"],
            annual_cost_score(ties["annual_cost_score"]["annual_total_usd"], "single"),
        )
        self.assertEqual(
            ties["active_life_score"]["expected"],
            active_life_score({
                key: {"score": ties["active_life_score"]["component_score"]}
                for key in (
                    "everyday_movement", "active_pursuits", "year_round_continuity", "activity_ecosystem",
                )
            }),
        )


class FireRankingTests(unittest.TestCase):
    """The changes that should break these tests are wrong score composition or ordering."""

    def route(self, status: str = "eligible", score: float | None = 4.0) -> dict:
        return {
            "status": status,
            "base_score": score,
            "summary": "The documented route fits the selected stay.",
            "work_permission": "remote_permitted",
            "max_days": None,
            "confidence": "high",
            "last_reviewed": "2026-08-25",
            "mobility_rights": {
                mobility: {
                    "status": status if mobility != "prefer_not_to_say" else (
                        "needs_verification" if status in {"needs_verification", "not_eligible"} else status
                    ),
                    "base_score": score,
                    "max_days": None,
                    "work_permission": "remote_permitted",
                }
                for mobility in ("local_free_movement", "general_nonlocal", "prefer_not_to_say")
            },
        }

    def country(self, *, tax_score: float | None = 2.0, health_score: float | None = 3.0) -> dict:
        return {
            "stay_routes": {mode: self.route() for mode in ("seasonal", "part_year", "full_relocation")},
            "tax": {
                "standard_day_threshold": 183,
                "non_day_tests": "A permanent home can trigger a separate residence test.",
                "scope_if_resident": "Residents generally enter worldwide-income scope.",
                "category_flags": {
                    "pensions": "Pension treatment needs treaty review.",
                    "dividends": "Dividend treatment needs treaty review.",
                    "capital_gains": "Capital-gains treatment depends on asset and source.",
                    "property_income": "Local property income can remain taxable while nonresident.",
                    "wealth": "Wealth-related rules need review.",
                    "inheritance": "Inheritance rules need review.",
                },
                "treaty_reporting_note": "Treaty relief and reporting depend on the other jurisdiction.",
                "confidence": "medium_high",
                "last_reviewed": "2026-08-24",
                "by_mode": {
                    mode: {
                        "status": "eligible" if tax_score is not None else "needs_verification",
                        "rankable": tax_score is not None,
                        "compatibility_score": tax_score,
                        "summary": "Selected-mode tax residence needs a separate review.",
                    }
                    for mode in ("seasonal", "part_year", "full_relocation")
                },
            },
            "healthcare": {
                "by_mode": {
                    mode: {
                        "eligibility": "eligible" if health_score is not None else "needs_verification",
                        "bridge_score": health_score,
                        "waiting_period_summary": "Private cover is needed during any wait.",
                        "age_limit_summary": "Policy entry ages vary.",
                        "pre_existing_condition_summary": "Written coverage terms are required.",
                        "evacuation_summary": "Confirm evacuation cover.",
                        "confidence": "medium",
                        "last_reviewed": "2026-08-23",
                    }
                    for mode in ("seasonal", "part_year", "full_relocation")
                }
            },
            "financial_infrastructure": {
                "bank_account_opening": "Banks require identity and address evidence.",
                "tax_id_dependency": "A tax identifier may be required.",
                "international_transfer_friction": "Transfers can require supporting documents.",
                "international_payments": "International cards are generally available.",
                "brokerage_access": "Broker access must be reconfirmed after a tax-home change.",
                "confidence": "high",
                "last_reviewed": "2026-08-22",
            },
        }

    def destination(self, destination_id: str, name: str, country: str = "Example") -> dict:
        return {
            "id": destination_id,
            "name": name,
            "country": country,
            "decision_dimensions": [
                {"key": "global_access", "score": 4.0},
                {"key": "foreigner_fit", "score": 3.0},
            ],
            "scores": {
                "exit_liquidity": {"score": 4.0},
                "ownership_clarity": {"score": 2.0},
            },
        }

    def override(self, country: str = "Example", confidence: str = "high") -> dict:
        return {
            "country": country,
            "active_life": {
                "everyday_movement": {"score": 4.0, "summary": "Daily cycling and year-round park access.", "confidence": "high"},
                "active_pursuits": {"score": 4.0, "summary": "Trails support regular outdoor pursuits.", "confidence": "medium_high"},
                "year_round_continuity": {"score": 4.0, "summary": "The climate supports activity through the year.", "confidence": "medium"},
                "activity_ecosystem": {"score": 4.0, "summary": "Local clubs create a social activity base.", "confidence": "high"},
            },
            "activity_tags": ["walking", "cycling"],
            "rent_flexibility_score": 3.0,
            "one_time_relocation_usd": 5000,
            "risk_warnings": ["Heat plans matter in midsummer."],
            "confidence": confidence,
            "last_reviewed": "2026-08-29",
        }

    def cost(self, destination_id: str) -> dict:
        return {
            "destination_id": destination_id,
            "profiles": {
                "single": {
                    "categories_usd": {
                        "food_household": 50000,
                        "utilities_communications": 0,
                        "private_healthcare": 0,
                        "transport": 0,
                        "dining_leisure": 0,
                        "travel": 0,
                        "visa_admin": 0,
                        "contingency": 0,
                    },
                    "annual_rent_usd": 4545,
                    "annual_owner_costs_usd": 1000,
                }
            },
            "property": {"representative_price_usd": 100000, "acquisition_cost_rate": 0.1},
            "confidence": {"overall": "medium_high"},
            "sources": [{"accessed_on": "2026-08-21"}],
        }

    def payload(self, countries: dict | None = None, overrides: dict | None = None) -> dict:
        return {
            "countries": countries or {"Example": self.country()},
            "destination_overrides": overrides or {"alpha": self.override()},
        }

    def test_resolve_country_record_uses_the_destination_override_country(self) -> None:
        country = self.country()
        payload = self.payload({"Example": country}, {"alpha": self.override()})
        self.assertIs(country, resolve_country_record(self.destination("alpha", "Alpha"), payload))

    def test_active_life_score_uses_the_published_component_weights(self) -> None:
        record = {
            "everyday_movement": {"score": 5},
            "active_pursuits": {"score": 4},
            "year_round_continuity": {"score": 3},
            "activity_ecosystem": {"score": 2},
        }
        self.assertEqual(3.75, active_life_score(record))

    def test_missing_active_life_returns_none_and_unranks_the_destination(self) -> None:
        override = self.override()
        override["active_life"].pop("year_round_continuity")
        self.assertIsNone(active_life_score(override))
        result = rank_fire_abroad_destinations(
            [self.destination("alpha", "Alpha")],
            {"alpha": self.cost("alpha")},
            self.payload(overrides={"alpha": override}),
            normalize_fire_profile({}),
        )[0]
        self.assertEqual("needs_verification", result["status"])
        self.assertIsNone(result["score"])
        self.assertIsNone(result["components"]["active_life"])

    def test_ranking_composes_each_documented_dimension_and_weight(self) -> None:
        result = rank_fire_abroad_destinations(
            [self.destination("alpha", "Alpha")],
            {"alpha": self.cost("alpha")}, self.payload(), normalize_fire_profile({})
        )[0]
        self.assertEqual("eligible", result["status"])
        self.assertEqual(
            {
                "active_life": 4.0, "sustainable_annual_cost": 2.5,
                "healthcare_bridge": 3.0, "stay_flexibility": 4.0,
                "tax_compatibility": 2.0, "global_access": 4.0,
                "community_fit": 3.0, "property_exit_flexibility": 3.0,
            },
            result["components"],
        )
        self.assertEqual(3.23, result["score"])
        self.assertEqual(60000, result["resilience_budget"]["annual_total_usd"])
        self.assertEqual("Daily cycling and year-round park access.", result["strongest_activity_reason"])
        self.assertEqual(["walking", "cycling"], result["activity_tags"])

    def test_selected_evidence_facts_and_conservative_review_metadata_are_attached(self) -> None:
        profile = normalize_fire_profile({"income_type": "portfolio"})
        result = rank_fire_abroad_destinations(
            [self.destination("alpha", "Alpha")],
            {"alpha": self.cost("alpha")}, self.payload(), profile,
        )[0]

        self.assertEqual("The documented route fits the selected stay.", result["stay_facts"]["summary"])
        self.assertEqual("Remote work permitted", result["stay_facts"]["work_permission"])
        self.assertEqual("Residents generally enter worldwide-income scope.", result["tax_facts"]["scope_if_resident"])
        self.assertIn("Dividend treatment", result["tax_facts"]["income_category"])
        self.assertIn("Capital-gains treatment", result["tax_facts"]["income_category"])
        self.assertIn("Treaty relief", result["tax_facts"]["treaty_reporting"])
        self.assertEqual("Private cover is needed during any wait.", result["healthcare_facts"]["waiting_period"])
        self.assertEqual("Policy entry ages vary.", result["healthcare_facts"]["age_limits"])
        self.assertEqual("Written coverage terms are required.", result["healthcare_facts"]["pre_existing_conditions"])
        self.assertEqual("Confirm evacuation cover.", result["healthcare_facts"]["evacuation"])
        self.assertIn("identity and address", result["financial_infrastructure_facts"]["banking"])
        self.assertIn("supporting documents", result["financial_infrastructure_facts"]["transfers"])
        self.assertIn("Broker access", result["financial_infrastructure_facts"]["brokerage"])
        self.assertEqual("medium", result["confidence"])
        self.assertEqual("2026-08-21", result["last_reviewed"])

    def test_missing_consolidated_dimension_is_unranked_without_a_legacy_fallback(self) -> None:
        destination = self.destination("alpha", "Alpha")
        destination["decision_dimensions"] = [
            {"key": "foreigner_fit", "score": 3.0},
        ]
        result = rank_fire_abroad_destinations(
            [destination], {"alpha": self.cost("alpha")}, self.payload(), normalize_fire_profile({})
        )[0]
        self.assertEqual("needs_verification", result["status"])
        self.assertIsNone(result["score"])
        self.assertIsNone(result["components"]["global_access"])

    def test_missing_tax_or_health_evidence_remains_unranked(self) -> None:
        missing_tax = self.country(tax_score=None)
        result = rank_fire_abroad_destinations(
            [self.destination("alpha", "Alpha")], {"alpha": self.cost("alpha")},
            self.payload({"Example": missing_tax}, {"alpha": self.override()}), normalize_fire_profile({})
        )[0]
        self.assertEqual("needs_verification", result["status"])
        self.assertIsNone(result["score"])
        self.assertIsNone(result["components"]["tax_compatibility"])

    def test_malformed_cost_records_remain_unranked_without_zero_cost_substitution(self) -> None:
        complete = self.cost("alpha")
        malformed_costs = {
            "empty_record": {},
            "empty_profiles": {"profiles": {}},
            "missing_selected_household": {"profiles": {"couple": {"categories_usd": {}, "annual_rent_usd": 1}}},
            "missing_required_housing_cost": {"profiles": {"single": {"categories_usd": {"living": 50000}}}},
            "missing_required_category": copy.deepcopy(complete),
            "empty_categories": copy.deepcopy(complete),
            "negative_category": copy.deepcopy(complete),
            "nan_category": copy.deepcopy(complete),
            "infinite_housing": copy.deepcopy(complete),
            "missing_buy_property": copy.deepcopy(complete),
            "negative_buy_property_rate": copy.deepcopy(complete),
        }
        malformed_costs["missing_required_category"]["profiles"]["single"]["categories_usd"].pop("travel")
        malformed_costs["empty_categories"]["profiles"]["single"]["categories_usd"] = {}
        malformed_costs["negative_category"]["profiles"]["single"]["categories_usd"]["travel"] = -1
        malformed_costs["nan_category"]["profiles"]["single"]["categories_usd"]["travel"] = math.nan
        malformed_costs["infinite_housing"]["profiles"]["single"]["annual_rent_usd"] = math.inf
        malformed_costs["missing_buy_property"].pop("property")
        malformed_costs["negative_buy_property_rate"]["property"]["acquisition_cost_rate"] = -0.1
        for name, cost in malformed_costs.items():
            with self.subTest(cost=name):
                profile = normalize_fire_profile({
                    "housing": "buy_now" if name in {"missing_buy_property", "negative_buy_property_rate"} else "rent",
                })
                result = rank_fire_abroad_destinations(
                    [self.destination("alpha", "Alpha")], {"alpha": cost}, self.payload(), profile
                )[0]
                self.assertEqual("needs_verification", result["status"])
                self.assertIsNone(result["score"])
                self.assertIsNone(result["components"]["sustainable_annual_cost"])
                self.assertIsNone(result["resilience_budget"]["annual_total_usd"])

    def test_overall_score_uses_half_up_on_a_point_zero_zero_five_tie(self) -> None:
        country = self.country(tax_score=4.0, health_score=4.0)
        country["stay_routes"]["part_year"] = self.route("eligible", 4.0)
        destination = self.destination("alpha", "Alpha")
        destination["decision_dimensions"] = [
            {"key": "global_access", "score": 4.0},
            {"key": "foreigner_fit", "score": 4.0},
        ]
        destination["scores"]["exit_liquidity"]["score"] = 4.1
        destination["scores"]["ownership_clarity"]["score"] = 4.1
        override = self.override()
        override["rent_flexibility_score"] = 4.1
        cost = self.cost("alpha")
        categories = cost["profiles"]["single"]["categories_usd"]
        for key in categories:
            categories[key] = 0
        categories["food_household"] = 28000
        categories["contingency"] = 200
        cost["profiles"]["single"]["annual_rent_usd"] = 10000

        result = rank_fire_abroad_destinations(
            [destination], {"alpha": cost},
            self.payload({"Example": country}, {"alpha": override}), normalize_fire_profile({}),
        )[0]

        self.assertEqual(42000, result["resilience_budget"]["annual_total_usd"])
        self.assertEqual(4.1, result["components"]["property_exit_flexibility"])
        self.assertEqual(4.01, result["score"])

    def test_rank_orders_status_score_confidence_then_name(self) -> None:
        countries = {"Example": self.country(), "Conditional": self.country()}
        countries["Conditional"]["stay_routes"]["part_year"] = self.route("conditional")
        overrides = {
            "alpha": self.override("Example", "low"),
            "beta": self.override("Example", "high"),
            "able": self.override("Example", "high"),
            "conditional": self.override("Conditional", "high"),
        }
        destinations = [
            self.destination("alpha", "Alpha"), self.destination("beta", "Beta"),
            self.destination("able", "Able"), self.destination("conditional", "Conditional", "Conditional"),
        ]
        costs = {item["id"]: self.cost(item["id"]) for item in destinations}
        results = rank_fire_abroad_destinations(destinations, costs, self.payload(countries, overrides), normalize_fire_profile({}))
        self.assertEqual(["able", "beta", "alpha", "conditional"], [item["destination_id"] for item in results])

    def test_rank_adds_us_and_tax_day_warnings_without_changing_tax_score(self) -> None:
        profile = normalize_fire_profile({"home_tax_context": "us_person", "annual_days": 183})
        result = rank_fire_abroad_destinations(
            [self.destination("alpha", "Alpha")], {"alpha": self.cost("alpha")}, self.payload(), profile
        )[0]
        warnings = " ".join(result["warnings"])
        self.assertIn("worldwide filing", warnings)
        self.assertIn("Tax residence likely", warnings)
        self.assertIn("permanent home", warnings)
        self.assertEqual(2.0, result["components"]["tax_compatibility"])

    def test_shared_contract_cases_hold_normalized_inputs_and_expected_outputs(self) -> None:
        contract = json.loads((ROOT / "tests/fixtures/fire_abroad_contract.json").read_text())
        self.assertGreaterEqual(len(contract["cases"]), 6)
        for case in contract["cases"]:
            self.assertEqual(case["normalized_profile"], normalize_fire_profile(case["raw_profile"]))
            country = self.country()
            if case["name"] == "exact_minimum_age":
                country["stay_routes"]["part_year"] = self.route("conditional")
                country["stay_routes"]["part_year"]["minimum_age"] = 50
            elif case["name"] == "full_relocation_unavailable":
                country["stay_routes"]["full_relocation"] = self.route("not_eligible")
            elif case["name"] == "consulting_passive_only":
                country["stay_routes"]["part_year"]["work_permission"] = "passive_only"
                for mapping in country["stay_routes"]["part_year"]["mobility_rights"].values():
                    mapping["work_permission"] = "passive_only"
            result = rank_fire_abroad_destinations(
                [self.destination("alpha", "Alpha")], {"alpha": self.cost("alpha")},
                self.payload({"Example": country}, {"alpha": self.override()}), case["normalized_profile"],
            )
            expected = case["expected"]
            self.assertEqual(expected["ordered_ids"], [item["destination_id"] for item in result])
            self.assertEqual(expected["statuses"], [item["status"] for item in result])
            self.assertEqual(expected["scores"], [item["score"] for item in result])
            self.assertEqual(
                expected["annual_budgets"], [item["resilience_budget"]["annual_total_usd"] for item in result]
            )
            warnings = " ".join(result[0]["warnings"])
            for warning in expected["warning_substrings"]:
                self.assertIn(warning, warnings)
