from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from tests.test_retirement_calculator_engine import base_payload, run_engine as run_retirement_engine


ROOT = Path(__file__).resolve().parents[1]
FINDER = ROOT / "src" / "retirement_destination_finder.js"


def run_finder(function_name: str, payload: object) -> object:
    script = (
        "const engine = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        f"process.stdout.write(JSON.stringify(engine.{function_name}(input)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(FINDER), json.dumps(payload)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def cost_record(destination_id: str, annual_cost: float, property_price: float = 0) -> dict:
    return {
        "destination_id": destination_id,
        "inflation": {"general": 0, "healthcare": 0, "property": 0},
        "profiles": {
            "single": {
                "categories_usd": {"living": annual_cost},
                "annual_rent_usd": 0,
                "annual_owner_costs_usd": 0,
            }
        },
        "property": {
            "representative_price_usd": property_price,
            "acquisition_cost_rate": 0,
        },
    }


def destination(destination_id: str, preference: float = 3) -> dict:
    return {
        "id": destination_id,
        "name": destination_id.title(),
        "country": "Example",
        "continent": "Europe",
        "category": "Coast",
        "recommendable": True,
        "scores": {
            "retirement_suitability": {"score": preference},
            "healthcare": {"score": preference},
            "scenery": {"score": preference},
        },
    }


def mortgage_profile(availability: str = "likely_available", maximum_ltv: float | None = 0.7) -> dict:
    return {
        "availability": availability,
        "maximum_ltv": maximum_ltv,
        "maximum_term_years": 30,
        "maximum_age_at_maturity": 80,
        "conditions": [],
        "eligible_residency": ["non_resident"],
        "eligible_income_sources": ["overseas"],
        "confidence": "high" if availability != "research_incomplete" else "low",
        "evidence_date": "2026-08-20",
        "sources": [],
    }


def user_payload(**overrides: object) -> dict:
    user = {
        "currentAge": 59,
        "retirementAge": 60,
        "horizonYears": 1,
        "household": "single",
        "housingPlan": "rent",
        "totalLiquidCapital": 100000,
        "monthlyPortfolioContribution": 0,
        "contributionInflationLinked": False,
        "expectedPortfolioReturn": 0,
        "generalInflation": 0,
        "emergencyReserveMonths": 0,
        "incomeStreams": [],
        "preferences": {"region": "any", "climate": "any", "healthcare": "normal"},
    }
    user.update(overrides)
    return user


class RetirementDestinationFinderTests(unittest.TestCase):
    def test_destination_setting_taxonomy_is_explicit_and_complete(self) -> None:
        destinations = json.loads((ROOT / "data" / "destinations.json").read_text())
        allowed = {"City", "Coast", "Island", "Mountain", "Lake"}
        covered = set()

        for item in destinations:
            with self.subTest(destination=item["id"]):
                self.assertIsInstance(item.get("settings"), list)
                self.assertTrue(item["settings"])
                self.assertEqual(len(item["settings"]), len(set(item["settings"])))
                self.assertTrue(set(item["settings"]).issubset(allowed))
                covered.update(item["settings"])

        self.assertEqual(allowed, covered)

    def test_conditional_mortgage_requires_matching_residency_and_income_profile(self) -> None:
        profile = mortgage_profile("conditional", 0.6)
        profile["eligible_residency"] = ["resident"]
        profile["eligible_income_sources"] = ["documented_overseas_income"]
        self.assertFalse(
            run_finder(
                "profileMatchesBuyer",
                {"user": {"residency": "non_resident", "incomeSource": "overseas"}, "profile": profile},
            )
        )
        self.assertTrue(
            run_finder(
                "profileMatchesBuyer",
                {
                    "user": {"residency": "resident", "incomeSource": "documented_overseas_income"},
                    "profile": profile,
                },
            )
        )

    def test_retirement_engine_exposes_target_alias_without_changing_result(self) -> None:
        payload = base_payload()
        self.assertEqual(
            run_retirement_engine("calculateRetirement", payload),
            run_retirement_engine("calculateRetirementTarget", payload),
        )

    def test_project_portfolio_invests_monthly_contributions(self) -> None:
        result = run_finder(
            "projectPortfolio",
            {
                "currentAge": 50,
                "retirementAge": 60,
                "startingPortfolio": 100000,
                "monthlyContribution": 1200,
                "contributionInflationLinked": False,
                "generalInflation": 0,
                "expectedPortfolioReturn": 0,
            },
        )
        self.assertEqual(244000, result["portfolioAtRetirement"])
        self.assertEqual(11, len(result["annualProjection"]))

    def test_funding_tiers_use_liquid_ratio_boundaries(self) -> None:
        destinations = [destination("within"), destination("close"), destination("stretch")]
        payload = {
            "user": user_payload(),
            "destinations": destinations,
            "retirementCosts": [
                cost_record("within", 100000),
                cost_record("close", 100000 / 0.85),
                cost_record("stretch", 100000 / 0.849),
            ],
            "mortgageProfiles": {item["id"]: mortgage_profile() for item in destinations},
        }
        result = run_finder("recommendDestinations", payload)
        self.assertEqual(
            ["within_reach", "close", "stretch"],
            [item["tier"] for item in result["recommendations"]],
        )

    def test_preference_cannot_promote_stretch_above_within_reach(self) -> None:
        destinations = [destination("affordable", 1), destination("preferred", 5)]
        payload = {
            "user": user_payload(preferences={"region": "Europe", "climate": "Coast", "healthcare": "high"}),
            "destinations": destinations,
            "retirementCosts": [cost_record("affordable", 90000), cost_record("preferred", 200000)],
            "mortgageProfiles": {item["id"]: mortgage_profile() for item in destinations},
        }
        result = run_finder("recommendDestinations", payload)
        self.assertEqual("affordable", result["recommendations"][0]["destinationId"])
        self.assertEqual("within_reach", result["recommendations"][0]["tier"])

    def test_region_preference_filters_destinations_case_insensitively(self) -> None:
        asia = destination("asia-place")
        asia["continent"] = "Asia"
        europe = destination("europe-place")
        payload = {
            "user": user_payload(
                preferences={"region": "asia", "climate": "any", "healthcare": "normal"}
            ),
            "destinations": [asia, europe],
            "retirementCosts": [cost_record(asia["id"], 90_000), cost_record(europe["id"], 80_000)],
            "mortgageProfiles": {
                asia["id"]: mortgage_profile(),
                europe["id"]: mortgage_profile(),
            },
        }

        result = run_finder("recommendDestinations", payload)

        self.assertEqual(["asia-place"], [item["destinationId"] for item in result["recommendations"]])
        self.assertEqual(1, result["summary"]["evaluatedCount"])
        self.assertEqual([], result["excluded"])

    def test_setting_preference_filters_destinations(self) -> None:
        coast = destination("coast-place")
        coast["category"] = "Water"
        mountain = destination("mountain-place")
        mountain["category"] = "Mountain"
        payload = {
            "user": user_payload(
                preferences={"region": "any", "climate": "Mountain", "healthcare": "normal"}
            ),
            "destinations": [coast, mountain],
            "retirementCosts": [cost_record(coast["id"], 80_000), cost_record(mountain["id"], 90_000)],
            "mortgageProfiles": {
                coast["id"]: mortgage_profile(),
                mountain["id"]: mortgage_profile(),
            },
        }

        result = run_finder("recommendDestinations", payload)

        self.assertEqual(
            ["mountain-place"],
            [item["destinationId"] for item in result["recommendations"]],
        )

    def test_multiple_setting_preferences_match_any_selected_setting(self) -> None:
        coast = destination("coast-place")
        coast["settings"] = ["Coast"]
        mountain = destination("mountain-place")
        mountain["settings"] = ["Mountain"]
        city = destination("city-place")
        city["settings"] = ["City"]
        destinations = [coast, mountain, city]
        payload = {
            "user": user_payload(
                preferences={
                    "region": "any",
                    "settings": ["CoastOrIsland", "Mountain"],
                    "healthcare": "normal",
                }
            ),
            "destinations": destinations,
            "retirementCosts": [cost_record(item["id"], 90_000) for item in destinations],
            "mortgageProfiles": {item["id"]: mortgage_profile() for item in destinations},
        }

        result = run_finder("recommendDestinations", payload)

        self.assertEqual(
            {"coast-place", "mountain-place"},
            {item["destinationId"] for item in result["recommendations"]},
        )

    def test_lake_filter_uses_explicit_tags_not_legacy_category_text(self) -> None:
        lake = destination("lake-place")
        lake["category"] = "Mountain + Water"
        lake["settings"] = ["Mountain", "Lake"]
        coast = destination("coast-place")
        coast["category"] = "Mountain + Water"
        coast["settings"] = ["Mountain", "Coast"]
        destinations = [lake, coast]
        payload = {
            "user": user_payload(
                preferences={"region": "any", "settings": ["Lake"], "healthcare": "normal"}
            ),
            "destinations": destinations,
            "retirementCosts": [cost_record(item["id"], 90_000) for item in destinations],
            "mortgageProfiles": {item["id"]: mortgage_profile() for item in destinations},
        }

        result = run_finder("recommendDestinations", payload)

        self.assertEqual(
            ["lake-place"],
            [item["destinationId"] for item in result["recommendations"]],
        )

    def test_incomplete_mortgage_research_cannot_be_recommended(self) -> None:
        place = destination("unknown-financing")
        payload = {
            "user": user_payload(
                housingPlan="buy_now",
                totalLiquidCapital=200000,
                maximumPropertyAllocation=150000,
                monthlyPortfolioContribution=1000,
                purchaseMethod="mortgage",
                requestedLtv=0.7,
                annualMortgageRate=0.04,
                mortgageTermYears=20,
                mortgageTreatment="payoff",
                useBeforeRetirement="personal",
                grossRentalYield=0,
                vacancyRate=0,
                operatingCostRate=0,
            ),
            "destinations": [place],
            "retirementCosts": [cost_record(place["id"], 20000, 200000)],
            "mortgageProfiles": {place["id"]: mortgage_profile("research_incomplete", None)},
        }
        result = run_finder("recommendDestinations", payload)
        self.assertEqual([], result["recommendations"])
        self.assertEqual("financing_unverified", result["excluded"][0]["reasonCode"])

    def test_property_equity_does_not_fund_liquid_retirement_target(self) -> None:
        place = destination("equity-rich")
        payload = {
            "user": user_payload(
                housingPlan="buy_now",
                totalLiquidCapital=600000,
                maximumPropertyAllocation=550000,
                purchaseMethod="cash",
                requestedLtv=0,
                annualMortgageRate=0,
                mortgageTermYears=20,
                mortgageTreatment="payoff",
                useBeforeRetirement="personal",
                grossRentalYield=0,
                vacancyRate=0,
                operatingCostRate=0,
            ),
            "destinations": [place],
            "retirementCosts": [cost_record(place["id"], 150000, 500000)],
            "mortgageProfiles": {place["id"]: mortgage_profile("research_incomplete", None)},
        }
        result = run_finder("recommendDestinations", payload)
        item = result["recommendations"][0]
        self.assertEqual("stretch", item["tier"])
        self.assertGreater(item["propertyEquity"], item["portfolioAtRetirement"])
        self.assertLess(item["fundingRatio"], 0.85)

    def test_rent_recommendations_use_shared_annual_projection(self) -> None:
        destinations = [destination("rent-a"), destination("rent-b")]
        payload = {
            "user": user_payload(),
            "destinations": destinations,
            "retirementCosts": [cost_record(item["id"], 50000) for item in destinations],
            "mortgageProfiles": {item["id"]: mortgage_profile() for item in destinations},
        }
        result = run_finder("recommendDestinations", payload)

        for item in result["recommendations"]:
            self.assertEqual(result["sharedProjection"]["annualProjection"], item["annualProjection"])
            self.assertEqual(
                item["portfolioAtRetirement"],
                item["annualProjection"][-1]["portfolio"],
            )

    def test_buy_now_recommendations_use_destination_specific_projections(self) -> None:
        destinations = [destination("buy-a"), destination("buy-b")]
        payload = {
            "user": user_payload(
                housingPlan="buy_now",
                totalLiquidCapital=1000000,
                maximumPropertyAllocation=500000,
                purchaseMethod="cash",
                requestedLtv=0,
                annualMortgageRate=0,
                mortgageTermYears=20,
                mortgageTreatment="payoff",
                useBeforeRetirement="personal",
                grossRentalYield=0,
                vacancyRate=0,
                operatingCostRate=0,
            ),
            "destinations": destinations,
            "retirementCosts": [
                cost_record("buy-a", 50000, 200000),
                cost_record("buy-b", 50000, 300000),
            ],
            "mortgageProfiles": {item["id"]: mortgage_profile("research_incomplete", None) for item in destinations},
        }
        result = run_finder("recommendDestinations", payload)
        recommendations = {item["destinationId"]: item for item in result["recommendations"]}

        self.assertEqual(2, len(recommendations))
        self.assertNotEqual(
            recommendations["buy-a"]["annualProjection"],
            recommendations["buy-b"]["annualProjection"],
        )
        for item in recommendations.values():
            self.assertEqual(
                item["portfolioAtRetirement"],
                item["annualProjection"][-1]["portfolio"],
            )

    def test_buy_now_payoff_projection_ends_after_remaining_mortgage_is_paid(self) -> None:
        place = destination("payoff-projection")
        payload = {
            "user": user_payload(
                housingPlan="buy_now",
                currentAge=50,
                retirementAge=60,
                horizonYears=30,
                totalLiquidCapital=700000,
                maximumPropertyAllocation=400000,
                monthlyPortfolioContribution=3000,
                purchaseMethod="mortgage",
                requestedLtv=0.6,
                annualMortgageRate=0.04,
                mortgageTermYears=20,
                mortgageTreatment="payoff",
                useBeforeRetirement="rental",
                grossRentalYield=0.05,
                vacancyRate=0.1,
                operatingCostRate=0.2,
            ),
            "destinations": [place],
            "retirementCosts": [cost_record(place["id"], 30000, 400000)],
            "mortgageProfiles": {place["id"]: mortgage_profile()},
        }

        result = run_finder("recommendDestinations", payload)
        item = result["recommendations"][0]

        self.assertGreater(item["annualProjection"][-2]["mortgageBalance"], 0)
        self.assertEqual(0, item["annualProjection"][-1]["mortgageBalance"])
        self.assertEqual(
            item["portfolioAtRetirement"],
            item["annualProjection"][-1]["portfolio"],
        )

    def test_every_input_destination_is_accounted_for(self) -> None:
        destinations = [destination("a"), destination("b"), destination("c")]
        payload = {
            "user": user_payload(),
            "destinations": destinations,
            "retirementCosts": [cost_record(item["id"], 50000) for item in destinations],
            "mortgageProfiles": {item["id"]: mortgage_profile() for item in destinations},
        }
        result = run_finder("recommendDestinations", payload)
        self.assertEqual(3, result["summary"]["evaluatedCount"])
        self.assertEqual(3, len(result["recommendations"]) + len(result["excluded"]))

    def test_projected_capital_entry_point_reuses_existing_targets_and_ordering(self) -> None:
        destinations = [destination("low", 3), destination("preferred", 5), destination("high", 2)]
        payload = {
            "user": user_payload(
                currentAge=50,
                retirementAge=60,
                horizonYears=30,
                totalLiquidCapital=500_000,
                monthlyPortfolioContribution=1_500,
                expectedPortfolioReturn=0.04,
            ),
            "destinations": destinations,
            "retirementCosts": [
                cost_record("low", 25_000),
                cost_record("preferred", 32_000),
                cost_record("high", 45_000),
            ],
            "mortgageProfiles": {item["id"]: mortgage_profile() for item in destinations},
        }
        accumulated = run_finder("recommendDestinations", payload)
        direct = run_finder(
            "recommendProjectedCapital",
            {
                **payload,
                "projectedCapitalUsd": accumulated["sharedProjection"]["portfolioAtRetirement"],
            },
        )

        self.assertEqual(
            [
                (item["destinationId"], item["tier"], item["retirementTarget"])
                for item in accumulated["recommendations"]
            ],
            [
                (item["destinationId"], item["tier"], item["retirementTarget"])
                for item in direct["recommendations"]
            ],
        )
        self.assertEqual(
            accumulated["sharedProjection"]["portfolioAtRetirement"],
            direct["sharedProjection"]["portfolioAtRetirement"],
        )

    def test_projected_capital_entry_point_rejects_buy_now(self) -> None:
        place = destination("buy-now")
        payload = {
            "projectedCapitalUsd": 1_000_000,
            "user": user_payload(housingPlan="buy_now"),
            "destinations": [place],
            "retirementCosts": [cost_record(place["id"], 30_000)],
            "mortgageProfiles": {place["id"]: mortgage_profile()},
        }

        with self.assertRaises(subprocess.CalledProcessError) as caught:
            run_finder("recommendProjectedCapital", payload)
        self.assertIn("buy now", caught.exception.stderr.lower())


if __name__ == "__main__":
    unittest.main()
