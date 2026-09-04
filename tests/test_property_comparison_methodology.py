from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import build_unified_app


ROOT = Path(__file__).resolve().parents[1]


class PropertyComparisonMethodologyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.methodology = build_unified_app.load_comparison_methodology()

    def test_methodology_defines_one_retirement_home_archetype(self) -> None:
        self.assertEqual(self.methodology["id"], "retirement-couple-home-v1")
        self.assertEqual(self.methodology["internal_area_m2"], 100)
        self.assertEqual(self.methodology["bedrooms"], 2)
        self.assertEqual(self.methodology["condition"], "move-in ready")
        self.assertEqual(self.methodology["market_segment"], "upper-middle")
        self.assertEqual(self.methodology["ownership"], "foreigner-purchasable")
        self.assertNotIn("acquisition taxes", self.methodology["included_costs"])
        self.assertIn("acquisition taxes", self.methodology["excluded_costs"])

    def test_destination_estimate_uses_unrounded_benchmark_times_area(self) -> None:
        methodology = dict(self.methodology)
        methodology["evidence_by_destination"] = {
            "example": {"status": "aligned benchmark", "reason": "Reviewed residential benchmark."}
        }
        destination = {
            "id": "example",
            "usd_per_m2": 2620.25,
            "price_basis": "Built residential benchmark.",
        }

        enriched = build_unified_app.add_comparison_home_estimate(destination, methodology)

        self.assertEqual(enriched["comparison_home_usd"], 262025)
        self.assertEqual(enriched["comparison_home_area_m2"], 100)
        self.assertEqual(enriched["comparison_home_archetype_id"], "retirement-couple-home-v1")
        self.assertEqual(enriched["comparison_home_evidence"], "aligned benchmark")
        self.assertEqual(enriched["comparison_home_evidence_reason"], "Reviewed residential benchmark.")

    def test_non_comparable_market_input_is_disclosed_as_proxy(self) -> None:
        destination = {
            "id": "example",
            "usd_per_m2": 4200,
            "price_basis": "Improved-property/build-cost proxy rather than clean market equivalent.",
        }

        enriched = build_unified_app.add_comparison_home_estimate(destination, self.methodology)

        self.assertEqual(enriched["comparison_home_evidence"], "proxy")
        self.assertIn("not a direct quote", enriched["comparison_home_disclosure"])

    def test_unknown_destination_defaults_to_proxy(self) -> None:
        destination = {"id": "unknown", "usd_per_m2": 4200, "price_basis": "Residential benchmark."}

        enriched = build_unified_app.add_comparison_home_estimate(destination, self.methodology)

        self.assertEqual(enriched["comparison_home_evidence"], "proxy")
        self.assertIn("not reviewed", enriched["comparison_home_evidence_reason"].lower())

    def test_zero_benchmark_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive usd_per_m2"):
            build_unified_app.add_comparison_home_estimate(
                {"id": "unknown", "usd_per_m2": 0, "price_basis": "Missing."},
                self.methodology,
            )

    def test_mixed_house_and_apartment_input_is_disclosed_as_proxy(self) -> None:
        destination = {
            "id": "example",
            "usd_per_m2": 6100,
            "price_basis": "Built-property benchmark. References show houses and apartments at different prices.",
        }

        enriched = build_unified_app.add_comparison_home_estimate(destination, self.methodology)

        self.assertEqual(enriched["comparison_home_evidence"], "proxy")

    def test_all_destinations_can_be_enriched_with_the_same_archetype(self) -> None:
        destinations = json.loads((ROOT / "data" / "destinations.json").read_text(encoding="utf-8"))
        reviews = self.methodology["evidence_by_destination"]

        enriched = [
            build_unified_app.add_comparison_home_estimate(item, self.methodology)
            for item in destinations
        ]

        self.assertEqual(len(enriched), 37)
        self.assertEqual(set(reviews), {item["id"] for item in destinations})
        self.assertTrue(all(review["status"] in {"aligned benchmark", "proxy"} for review in reviews.values()))
        self.assertTrue(all(review["reason"].strip() for review in reviews.values()))
        self.assertEqual({item["comparison_home_area_m2"] for item in enriched}, {100})
        self.assertTrue(all(item["comparison_home_usd"] > 0 for item in enriched))

    def test_country_entry_averages_standardized_home_prices(self) -> None:
        hub = {"destination_ids": ["one", "two"]}
        destinations = [
            {
                "id": "one",
                "name": "One",
                "comparison_home_usd": 300000,
                "comparison_home_evidence": "aligned benchmark",
                "acquisition_cost_estimate_usd": 15000,
                "all_in_acquisition_estimate_usd": 315000,
                "purchase_route": {"status": "available"},
                "acquisition_benchmark_status": "calculable",
                "acquisition_benchmark_reason": "",
                "acquisition_cost_confidence": "high",
                "acquisition_cost_complete": True,
                "acquisition_cost_completeness": "complete",
                "decision_score": 4,
                "decision_dimensions": [],
            },
            {
                "id": "two",
                "name": "Two",
                "comparison_home_usd": 500000,
                "comparison_home_evidence": "proxy",
                "acquisition_cost_estimate_usd": 25000,
                "all_in_acquisition_estimate_usd": 525000,
                "purchase_route": {"status": "available"},
                "acquisition_benchmark_status": "calculable",
                "acquisition_benchmark_reason": "",
                "acquisition_cost_confidence": "medium-high",
                "acquisition_cost_complete": True,
                "acquisition_cost_completeness": "complete",
                "decision_score": 4,
                "decision_dimensions": [],
            },
        ]

        metrics = build_unified_app.country_summary_metrics(hub, destinations)

        self.assertEqual(metrics["entry"], 400000)
        self.assertEqual(metrics["evidence"], "mixed/proxy")
        self.assertEqual(metrics["acquisition_evidence"], "aligned")

    def test_built_dashboard_explains_the_standardized_estimate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory) / "artifacts"
            with (
                patch.object(build_unified_app, "ARTIFACTS", artifacts),
                patch.object(build_unified_app, "PUBLIC_ASSETS", artifacts / "assets"),
            ):
                output = build_unified_app.build()
                html = output.read_text(encoding="utf-8")
                country_html = (artifacts / "country-comparison" / "index.html").read_text(encoding="utf-8")
                destination_html = (artifacts / "destinations" / "fukuoka-itoshima" / "index.html").read_text(encoding="utf-8")
                guide_html = (artifacts / "best-places-to-buy-property-abroad-for-retirement" / "index.html").read_text(encoding="utf-8")

        self.assertIn("Indicative 100 m² retirement home", html)
        self.assertIn(
            "Modeled base acquisition costs are shown separately from the property-price figure. Unquantified and conditional items remain outside comparable totals",
            html,
        )
        self.assertNotIn("acquisition costs excluded", html.lower())
        self.assertIn('"comparison_home_area_m2": 100.0', html)
        self.assertIn('"comparison_home_usd": 262000.0', html)
        self.assertNotRegex(country_html, re.compile(r"\$[\d,]+/m2"))
        self.assertRegex(country_html, re.compile(r"\$471,000<br><small>mixed/proxy"))
        for rendered in (country_html, destination_html, guide_html):
            self.assertIn("all-in", rendered.lower())
            self.assertNotIn("acquisition costs excluded", rendered.lower())
            self.assertRegex(rendered.lower(), r"aligned benchmark|proxy")


if __name__ == "__main__":
    unittest.main()
