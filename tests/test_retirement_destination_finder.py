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


if __name__ == "__main__":
    unittest.main()
