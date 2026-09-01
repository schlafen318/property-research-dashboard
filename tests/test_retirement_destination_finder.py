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


def destination(destination_id: str, preference: float = 3, country: str = "Example") -> dict:
    return {
        "id": destination_id,
        "name": destination_id.title(),
        "country": country,
        "continent": "Europe",
        "category": "Coast",
        "recommendable": True,
        "scores": {
            "retirement_suitability": {"score": preference},
            "healthcare": {"score": preference},
            "scenery": {"score": preference},
        },
    }


def tax_country(
    favorable_rate: float = 0,
    central_rate: float = 0,
    adverse_rate: float = 0,
    *,
    last_reviewed: str = "2026-09-01",
) -> dict:
    return {
        "tax_screen": {
            "status": "complete",
            "last_reviewed": last_reviewed,
            "confidence": "medium_high",
            "planning_bands": {
                mode: {
                    "favorable_rate": favorable_rate,
                    "central_rate": central_rate,
                    "adverse_rate": adverse_rate,
                }
                for mode in ("seasonal", "part_year", "full_relocation")
            },
            "planning_band_basis_source_ids": ["tax-bands"],
            "gain_intensity_modifiers": {"low": 1, "moderate": 1, "high": 1},
            "gain_intensity_source_ids": ["gain-intensity"],
            "annual_allowances": {
                "property_tax": {
                    "label": "Annual property tax allowance",
                    "favorable_usd": 0,
                    "central_usd": 0,
                    "adverse_usd": 0,
                    "applies_to_property_uses": ["personal", "rental", "mixed"],
                    "source_ids": ["property-tax"],
                },
                "wealth_tax": {
                    "label": "Annual wealth tax allowance",
                    "favorable_usd": 0,
                    "central_usd": 0,
                    "adverse_usd": 0,
                    "applies_to_wealth_bands": ["above_threshold"],
                    "source_ids": ["wealth-tax"],
                },
                "compliance": {
                    "label": "Annual compliance allowance",
                    "favorable_usd": 0,
                    "central_usd": 0,
                    "adverse_usd": 0,
                    "source_ids": ["compliance"],
                },
            },
        }
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
        "taxMode": "user_after_tax",
        "returnBasis": "after_fees_and_tax",
        "taxProfile": {
            "dependableIncome": 0,
            "portfolioWithdrawals": 0,
            "realizedGainIntensity": "moderate",
            "propertyUse": "none",
            "wealthBand": "unknown",
        },
        "preferences": {"region": "any", "climate": "any", "healthcare": "normal"},
    }
    user.update(overrides)
    return user


class RetirementDestinationFinderTests(unittest.TestCase):
    def test_tax_adjusted_central_target_can_change_tier_and_ranking(self) -> None:
        high_tax = destination("high-tax", 5, "High Tax")
        low_tax = destination("low-tax", 1, "Low Tax")
        common = {
            "destinations": [high_tax, low_tax],
            "retirementCosts": [cost_record(item["id"], 100_000) for item in (high_tax, low_tax)],
            "mortgageProfiles": {item["id"]: mortgage_profile() for item in (high_tax, low_tax)},
            "taxPlanning": {
                "asOf": "2026-09-01",
                "reviewedOn": "2026-09-01",
                "countries": {
                    "High Tax": tax_country(0.1, 0.2, 0.3),
                    "Low Tax": tax_country(),
                },
            },
        }
        before_tax = run_finder(
            "recommendDestinations",
            {
                **common,
                "user": user_payload(
                    preferences={"region": "Europe", "climate": "Coast", "healthcare": "high"}
                ),
            },
        )
        after_tax = run_finder(
            "recommendDestinations",
            {
                **common,
                "user": user_payload(
                    taxMode="destination_estimate",
                    taxProfile={
                        "dependableIncome": 0,
                        "portfolioWithdrawals": 100_000,
                        "realizedGainIntensity": "moderate",
                        "propertyUse": "none",
                        "wealthBand": "unknown",
                    },
                    preferences={"region": "Europe", "climate": "Coast", "healthcare": "high"},
                ),
            },
        )

        self.assertEqual("high-tax", before_tax["recommendations"][0]["destinationId"])
        self.assertEqual("low-tax", after_tax["recommendations"][0]["destinationId"])
        high_tax_result = next(
            item for item in after_tax["recommendations"] if item["destinationId"] == "high-tax"
        )
        self.assertEqual("stretch", high_tax_result["tier"])
        self.assertEqual(120_000, high_tax_result["retirementTarget"])
        self.assertEqual([110_000, 130_000], high_tax_result["retirementTargetRange"])
        self.assertEqual(-10_000, high_tax_result["favorableGap"])
        self.assertEqual(-20_000, high_tax_result["surplusGap"])
        self.assertEqual(-30_000, high_tax_result["adverseGap"])

    def test_stale_or_invalid_tax_evidence_is_conditional_not_zero_tax(self) -> None:
        stale = destination("stale", country="Stale")
        invalid = destination("invalid", country="Invalid")
        invalid_country = tax_country()
        del invalid_country["tax_screen"]["annual_allowances"]["property_tax"]
        payload = {
            "user": user_payload(
                taxMode="destination_estimate",
                taxProfile={
                    "dependableIncome": 20_000,
                    "portfolioWithdrawals": 20_000,
                    "realizedGainIntensity": "moderate",
                    "propertyUse": "none",
                    "wealthBand": "unknown",
                },
            ),
            "destinations": [stale, invalid],
            "retirementCosts": [cost_record(item["id"], 90_000) for item in (stale, invalid)],
            "mortgageProfiles": {item["id"]: mortgage_profile() for item in (stale, invalid)},
            "taxPlanning": {
                "asOf": "2026-09-01",
                "reviewedOn": "2026-09-01",
                "countries": {
                    "Stale": tax_country(last_reviewed="2024-01-01"),
                    "Invalid": invalid_country,
                },
            },
        }

        result = run_finder("recommendDestinations", payload)

        self.assertEqual(2, result["summary"]["conditionalCount"])
        for item in result["recommendations"]:
            with self.subTest(destination=item["destinationId"]):
                self.assertEqual("conditional", item["tier"])
                self.assertEqual("unavailable", item["taxStatus"])
                self.assertTrue(item["conditional"])
                self.assertIsNone(item["fundingRatio"])
                self.assertIsNone(item["retirementTarget"])
                self.assertIsNone(item["surplusGap"])

    def test_user_after_tax_bypass_is_one_zero_added_tax_target(self) -> None:
        place = destination("after-tax")
        result = run_finder(
            "recommendDestinations",
            {
                "user": user_payload(),
                "destinations": [place],
                "retirementCosts": [cost_record(place["id"], 100_000)],
                "mortgageProfiles": {place["id"]: mortgage_profile()},
                "taxPlanning": {"reviewedOn": "2026-09-01", "countries": {}},
            },
        )

        item = result["recommendations"][0]
        self.assertEqual("user_after_tax", item["taxStatus"])
        self.assertEqual("after_fees_and_tax", item["returnBasis"])
        self.assertEqual(0, item["annualTaxReserve"])
        self.assertEqual(100_000, item["retirementTarget"])
        self.assertEqual(0, item["surplusGap"])
        self.assertNotIn("retirementTargetRange", item)
        self.assertNotIn("favorableGap", item)
        self.assertNotIn("adverseGap", item)
        self.assertNotIn("detailHref", item)

    def test_tax_freshness_crosses_from_available_to_conditional_after_366_days(self) -> None:
        place = destination("threshold", country="Threshold")
        common = {
            "user": user_payload(
                taxMode="destination_estimate",
                taxProfile={
                    "dependableIncome": 0,
                    "portfolioWithdrawals": 10_000,
                    "realizedGainIntensity": "moderate",
                    "propertyUse": "none",
                    "wealthBand": "unknown",
                },
            ),
            "destinations": [place],
            "retirementCosts": [cost_record(place["id"], 100_000)],
            "mortgageProfiles": {place["id"]: mortgage_profile()},
        }

        boundary = run_finder(
            "recommendDestinations",
            {
                **common,
                "taxPlanning": {
                    "asOf": "2027-09-02",
                    "reviewedOn": "2026-09-01",
                    "countries": {"Threshold": tax_country(last_reviewed="2026-09-01")},
                },
            },
        )["recommendations"][0]
        crossed = run_finder(
            "recommendDestinations",
            {
                **common,
                "taxPlanning": {
                    "asOf": "2027-09-03",
                    "reviewedOn": "2026-09-01",
                    "countries": {"Threshold": tax_country(last_reviewed="2026-09-01")},
                },
            },
        )["recommendations"][0]

        self.assertNotEqual("unavailable", boundary["taxStatus"])
        self.assertEqual("unavailable", crossed["taxStatus"])
        self.assertEqual("conditional", crossed["tier"])
        self.assertIn("stale", crossed["taxReason"].lower())

    def test_owner_costs_exclude_property_tax_from_the_integrated_tax_target(self) -> None:
        place = destination("owner-tax", country="Owner Tax")
        country = tax_country()
        property_allowance = country["tax_screen"]["annual_allowances"]["property_tax"]
        property_allowance.update(
            {"favorable_usd": 2_500, "central_usd": 5_000, "adverse_usd": 8_000}
        )
        result = run_finder(
            "recommendDestinations",
            {
                "user": user_payload(
                    housingPlan="buy_retirement",
                    taxMode="destination_estimate",
                    taxProfile={
                        "dependableIncome": 0,
                        "portfolioWithdrawals": 0,
                        "realizedGainIntensity": "moderate",
                        "propertyUse": "personal",
                        "wealthBand": "unknown",
                    },
                ),
                "destinations": [place],
                "retirementCosts": [cost_record(place["id"], 100_000)],
                "mortgageProfiles": {place["id"]: mortgage_profile()},
                "taxPlanning": {
                    "asOf": "2026-09-01",
                    "reviewedOn": "2026-09-01",
                    "countries": {"Owner Tax": country},
                },
            },
        )

        item = result["recommendations"][0]
        self.assertEqual(0, item["annualTaxReserve"])
        self.assertEqual(100_000, item["retirementTarget"])

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
