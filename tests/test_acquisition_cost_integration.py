from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

from src import build_unified_app
from src.acquisition_costs import AcquisitionCostDataError


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "acquisition_cost_record.json"


class ElementCaptureParser(HTMLParser):
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def __init__(self, tag: str, required_attributes: dict[str, str]) -> None:
        super().__init__(convert_charrefs=True)
        self.tag = tag
        self.required_attributes = required_attributes
        self.matches: list[dict] = []
        self._depth = 0
        self._current: dict | None = None

    def _matches_target(self, tag: str, attributes: dict[str, str | None]) -> bool:
        if tag != self.tag:
            return False
        for name, expected in self.required_attributes.items():
            actual = attributes.get(name)
            if name == "class":
                if expected not in (actual or "").split():
                    return False
            elif actual != expected:
                return False
        return True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if self._current is None:
            if not self._matches_target(tag, attributes):
                return
            self._current = {"text": [], "attributes": [(tag, attributes)]}
            self._depth = 1
            return
        self._current["attributes"].append((tag, attributes))
        if tag not in self.VOID_TAGS:
            self._depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self._current is None:
            return
        self._depth -= 1
        if self._depth == 0:
            self._current["text"] = " ".join(" ".join(self._current["text"]).split())
            self.matches.append(self._current)
            self._current = None

    def handle_data(self, data: str) -> None:
        if self._current is not None:
            self._current["text"].append(data)


def capture_elements(document: str, tag: str, **attributes: str) -> list[dict]:
    parser = ElementCaptureParser(tag, attributes)
    parser.feed(document)
    return parser.matches


def extract_javascript_function(document: str, name: str) -> str:
    marker = f"function {name}("
    start = document.find(marker)
    if start < 0:
        return ""
    opening_brace = document.find("{", start)
    depth = 0
    for index in range(opening_brace, len(document)):
        character = document[index]
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return document[start:index + 1]
    return ""


class AcquisitionCostEnrichmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.acquisition_record = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_enrichment_adds_calculated_cost_fields(self) -> None:
        destination = {
            "id": "example",
            "comparison_home_usd": 200000,
            "comparison_home_area_m2": 100,
            "comparison_home_evidence": "proxy",
        }

        enriched = build_unified_app.add_acquisition_cost_estimate(
            destination,
            self.acquisition_record,
            {"USD": 1.0},
        )

        self.assertEqual(enriched["acquisition_cost_low_usd"], 10000)
        self.assertEqual(enriched["acquisition_cost_estimate_usd"], 10000)
        self.assertEqual(enriched["acquisition_cost_high_usd"], 10000)
        self.assertEqual(enriched["all_in_acquisition_low_usd"], 210000)
        self.assertEqual(enriched["all_in_acquisition_estimate_usd"], 210000)
        self.assertEqual(enriched["all_in_acquisition_high_usd"], 210000)
        self.assertEqual(enriched["all_in_acquisition_usd_per_m2"], 2100)
        self.assertEqual(enriched["acquisition_cost_rate"], 0.05)
        self.assertEqual(enriched["acquisition_cost_confidence"], "high")
        self.assertIs(enriched["acquisition_cost_complete"], True)
        self.assertEqual(enriched["acquisition_cost_completeness"], "complete")
        self.assertEqual(
            enriched["purchase_route"],
            {
                "status": "available",
                "label": "Synthetic direct individual ownership",
                "notes": "Example-only route used to exercise the dataset contract.",
            },
        )
        self.assertEqual(
            enriched["acquisition_jurisdiction_basis"],
            "Synthetic example jurisdiction for schema testing only; not a real jurisdictional rule.",
        )
        self.assertEqual(enriched["acquisition_cost_reviewed_on"], "2026-08-19")
        self.assertEqual(enriched["acquisition_benchmark_status"], "calculable")
        self.assertEqual(enriched["acquisition_benchmark_reason"], "")
        self.assertEqual(enriched["comparison_home_evidence"], "proxy")

    def test_enrichment_suppresses_totals_for_an_uncalculable_benchmark_independently(self) -> None:
        acquisition_record = deepcopy(self.acquisition_record)
        acquisition_record["purchase_route"]["status"] = "conditional"
        acquisition_record["purchase_route"]["notes"] = "The route needs an eligible asset."
        acquisition_record["benchmark_calculability"] = {
            "status": "not_calculable",
            "reason": "The benchmark is not aligned to the eligible asset route.",
        }

        enriched = build_unified_app.add_acquisition_cost_estimate(
            {
                "id": "example",
                "comparison_home_usd": 200000,
                "comparison_home_area_m2": 100,
            },
            acquisition_record,
            {"USD": 1.0},
        )

        for field in (
            "acquisition_cost_low_usd",
            "acquisition_cost_estimate_usd",
            "acquisition_cost_high_usd",
            "acquisition_cost_rate",
            "all_in_acquisition_low_usd",
            "all_in_acquisition_estimate_usd",
            "all_in_acquisition_high_usd",
            "all_in_acquisition_usd_per_m2",
        ):
            self.assertIsNone(enriched[field], field)
        self.assertEqual(enriched["purchase_route"]["status"], "conditional")
        self.assertIs(enriched["acquisition_cost_complete"], True)
        self.assertEqual(enriched["acquisition_benchmark_status"], "not_calculable")

    def test_enrichment_preserves_conditional_null_amounts_and_component_records(self) -> None:
        acquisition_record = deepcopy(self.acquisition_record)
        conditional = acquisition_record["components"][1]
        conditional["calculation"] = None
        conditional["estimate_strategy"] = "statutory"

        enriched = build_unified_app.add_acquisition_cost_estimate(
            {"id": "example", "comparison_home_usd": 200000, "comparison_home_area_m2": 100},
            acquisition_record,
            {"USD": 1.0},
        )

        self.assertEqual(enriched["acquisition_components"][0]["id"], "example-transfer-tax")
        self.assertEqual(enriched["conditional_acquisition_components"][0]["id"], "example-optional-counsel")
        self.assertIsNone(enriched["conditional_acquisition_components"][0]["low_usd"])
        self.assertIsNone(enriched["conditional_acquisition_components"][0]["estimate_usd"])
        self.assertIsNone(enriched["conditional_acquisition_components"][0]["high_usd"])
        self.assertIs(enriched["acquisition_cost_complete"], False)
        self.assertEqual(
            enriched["acquisition_cost_completeness"],
            "known-base/incomplete",
        )

    def test_enrichment_rejects_invalid_archetype_areas_before_calculation(self) -> None:
        for area in (0, -1, 99):
            with self.subTest(area=area):
                with self.assertRaisesRegex(ValueError, "example.*100 m²"):
                    build_unified_app.add_acquisition_cost_estimate(
                        {
                            "id": "example",
                            "comparison_home_usd": 200000,
                            "comparison_home_area_m2": area,
                        },
                        {},
                        {},
                    )


class AcquisitionCostCountrySummaryTests(unittest.TestCase):
    @staticmethod
    def destination(
        destination_id: str,
        price: float,
        cost: float | None,
        all_in: float | None,
        route_status: str,
        confidence: str,
    ) -> dict:
        return {
            "id": destination_id,
            "name": destination_id.title(),
            "comparison_home_usd": price,
            "comparison_home_evidence": "aligned benchmark",
            "acquisition_cost_low_usd": cost,
            "acquisition_cost_estimate_usd": cost,
            "acquisition_cost_high_usd": cost,
            "acquisition_cost_rate": cost / price if cost is not None else None,
            "all_in_acquisition_low_usd": all_in,
            "all_in_acquisition_estimate_usd": all_in,
            "all_in_acquisition_high_usd": all_in,
            "purchase_route": {"status": route_status},
            "acquisition_benchmark_status": "calculable",
            "acquisition_benchmark_reason": "",
            "acquisition_cost_confidence": confidence,
            "acquisition_cost_complete": True,
            "acquisition_cost_completeness": "complete",
            "decision_score": 4,
            "decision_dimensions": [],
        }

    def malformed_route_destinations(self) -> tuple[tuple[str, dict], ...]:
        base = self.destination("one", 200000, 10000, 210000, "available", "high")
        base.update(
            {
                "acquisition_cost_low_usd": 10000,
                "acquisition_cost_high_usd": 10000,
                "all_in_acquisition_low_usd": 210000,
                "all_in_acquisition_high_usd": 210000,
            }
        )
        variants = []
        for label, route in (
            ("null route", None),
            ("malformed route", "available"),
            ("missing status", {"label": "Candidate route"}),
            ("null status", {"status": None, "label": "Candidate route"}),
            ("unknown status", {"status": "pending", "label": "Candidate route"}),
            ("malformed status", {"status": 1, "label": "Candidate route"}),
        ):
            destination = deepcopy(base)
            destination["purchase_route"] = route
            variants.append((label, destination))
        missing = deepcopy(base)
        missing.pop("purchase_route")
        variants.insert(0, ("missing route", missing))
        return tuple(variants)

    def test_malformed_routes_fail_closed_in_static_formatters(self) -> None:
        for variant, destination in self.malformed_route_destinations():
            with self.subTest(variant=variant):
                try:
                    route_text = build_unified_app.acquisition_route_text(destination)
                    all_in_text = build_unified_app.all_in_acquisition_text(destination)
                except (AttributeError, TypeError) as error:
                    self.fail(f"{variant} route formatter raised {error!r}")

                self.assertTrue(route_text.startswith("Unavailable:"), route_text)
                self.assertEqual(all_in_text, "Not presented")
                self.assertNotIn("$210,000", all_in_text)

    def test_malformed_routes_are_unavailable_noncontributors_in_country_summary(self) -> None:
        for variant, destination in self.malformed_route_destinations():
            with self.subTest(variant=variant):
                try:
                    metrics = build_unified_app.country_summary_metrics(
                        {"destination_ids": ["one"]},
                        [destination],
                    )
                except (AttributeError, TypeError) as error:
                    self.fail(f"{variant} country summary raised {error!r}")

                self.assertIsNone(metrics["all_in_entry"])
                self.assertEqual(metrics["acquisition_contributors"], 0)
                self.assertEqual(metrics["acquisition_unavailable_excluded"], 1)
                self.assertEqual(metrics["acquisition_evidence"], "mixed/proxy")

    def test_available_high_confidence_routes_are_aligned(self) -> None:
        destinations = [
            self.destination("one", 200000, 10000, 210000, "available", "high"),
            self.destination("two", 300000.0, 30000.0, 330000.0, "available", "medium-high"),
        ]

        metrics = build_unified_app.country_summary_metrics(
            {"destination_ids": ["one", "two"]},
            destinations,
        )

        self.assertEqual(metrics["all_in_entry"], 270000)
        self.assertEqual(metrics["acquisition_cost"], 20000)
        self.assertEqual(metrics["acquisition_rate"], 0.08)
        self.assertEqual(metrics["acquisition_evidence"], "aligned")
        self.assertIs(metrics["acquisition_cost_complete"], True)
        self.assertEqual(metrics["acquisition_cost_completeness"], "complete")
        self.assertEqual(metrics["acquisition_contributors"], 2)
        self.assertEqual(metrics["acquisition_excluded"], 0)

    def test_available_incomplete_contributor_makes_country_average_known_base(self) -> None:
        complete = self.destination(
            "one", 200000, 10000, 210000, "available", "high"
        )
        incomplete = self.destination(
            "two", 300000, 30000, 330000, "available", "high"
        )
        incomplete["acquisition_cost_complete"] = False
        incomplete["acquisition_cost_completeness"] = "known-base/incomplete"

        metrics = build_unified_app.country_summary_metrics(
            {"destination_ids": ["one", "two"]},
            [complete, incomplete],
        )

        self.assertEqual(metrics["all_in_entry"], 270000)
        self.assertEqual(metrics["acquisition_rate"], 0.08)
        self.assertIs(metrics["acquisition_cost_complete"], False)
        self.assertEqual(
            metrics["acquisition_cost_completeness"],
            "known-base/incomplete",
        )
        self.assertEqual(metrics["acquisition_evidence"], "mixed/proxy")

    def test_completeness_is_independent_from_purchase_route(self) -> None:
        available_incomplete = self.destination(
            "available", 200000, 10000, 210000, "available", "high"
        )
        available_incomplete.update(
            {
                "acquisition_cost_complete": False,
                "acquisition_cost_completeness": "known-base/incomplete",
            }
        )
        conditional_complete = self.destination(
            "conditional", 200000, 10000, 210000, "conditional", "high"
        )

        self.assertEqual(
            build_unified_app.acquisition_cost_text(available_incomplete),
            "$10,000; known-base/incomplete",
        )
        self.assertEqual(
            build_unified_app.all_in_acquisition_text(available_incomplete),
            "$210,000; known-base/incomplete",
        )
        self.assertEqual(
            build_unified_app.acquisition_rate_text(available_incomplete),
            "5.0%; known-base/incomplete",
        )
        self.assertEqual(
            build_unified_app.all_in_acquisition_text(conditional_complete),
            "$210,000; conditional route",
        )
        self.assertEqual(
            build_unified_app.acquisition_rate_text(conditional_complete),
            "5.0%",
        )

    def test_uncalculable_benchmark_is_independent_and_excluded_from_country_average(self) -> None:
        contributor = self.destination(
            "one", 200000, 10000, 210000, "available", "high"
        )
        uncalculable = self.destination(
            "two", 300000, None, None, "conditional", "high"
        )
        uncalculable.update(
            {
                "acquisition_benchmark_status": "not_calculable",
                "acquisition_benchmark_reason": "The benchmark is not route-aligned.",
                "acquisition_cost_complete": True,
                "acquisition_cost_completeness": "complete",
            }
        )

        self.assertEqual(
            build_unified_app.acquisition_cost_text(uncalculable),
            "Not quantified",
        )
        self.assertEqual(
            build_unified_app.all_in_acquisition_text(uncalculable),
            "Not presented",
        )
        self.assertEqual(
            build_unified_app.acquisition_rate_text(uncalculable),
            "Not quantified",
        )

        metrics = build_unified_app.country_summary_metrics(
            {"destination_ids": ["one", "two"]},
            [contributor, uncalculable],
        )
        self.assertEqual(metrics["all_in_entry"], 210000)
        self.assertEqual(metrics["acquisition_contributors"], 1)
        self.assertEqual(metrics["acquisition_excluded"], 1)
        self.assertEqual(metrics["acquisition_uncalculable_excluded"], 1)

    def test_nonnumeric_or_nonfinite_acquisition_values_are_excluded(self) -> None:
        fields = (
            "comparison_home_usd",
            "acquisition_cost_estimate_usd",
            "all_in_acquisition_estimate_usd",
        )
        invalid_values = (
            ("numeric string", "200000"),
            ("malformed string", "not-a-number"),
            ("true boolean", True),
            ("false boolean", False),
            ("NaN", float("nan")),
            ("positive infinity", float("inf")),
            ("negative infinity", float("-inf")),
        )
        for route_status in ("available", "conditional"):
            for field in fields:
                for value_label, value in invalid_values:
                    with self.subTest(
                        route_status=route_status,
                        field=field,
                        value=value_label,
                    ):
                        destination = self.destination(
                            "one",
                            200000,
                            10000,
                            210000,
                            route_status,
                            "high",
                        )
                        destination[field] = value

                        metrics = build_unified_app.country_summary_metrics(
                            {"destination_ids": ["one"]},
                            [destination],
                        )

                        self.assertIsNone(metrics["all_in_entry"])
                        self.assertIsNone(metrics["acquisition_cost"])
                        self.assertIsNone(metrics["acquisition_rate"])
                        self.assertEqual(metrics["acquisition_contributors"], 0)
                        self.assertEqual(metrics["acquisition_excluded"], 1)
                        self.assertEqual(metrics["acquisition_unavailable_excluded"], 0)

    def test_low_medium_or_conditional_contributor_is_mixed_proxy(self) -> None:
        variants = (
            ("available", "low"),
            ("available", "medium"),
            ("conditional", "high"),
        )
        for route_status, confidence in variants:
            with self.subTest(route_status=route_status, confidence=confidence):
                destinations = [
                    self.destination("one", 200000, 10000, 210000, "available", "high"),
                    self.destination("two", 300000, 30000, 330000, route_status, confidence),
                ]

                metrics = build_unified_app.country_summary_metrics(
                    {"destination_ids": ["one", "two"]},
                    destinations,
                )

                self.assertEqual(metrics["acquisition_evidence"], "mixed/proxy")
                self.assertEqual(metrics["acquisition_contributors"], 2)
                self.assertEqual(metrics["acquisition_excluded"], 0)

    def test_unavailable_routes_are_excluded_from_acquisition_averages(self) -> None:
        destinations = [
            self.destination("one", 200000, 10000, 210000, "available", "high"),
            self.destination("two", 900000, 90000, 990000, "unavailable", "high"),
        ]

        metrics = build_unified_app.country_summary_metrics(
            {"destination_ids": ["one", "two"]},
            destinations,
        )

        self.assertEqual(metrics["all_in_entry"], 210000)
        self.assertEqual(metrics["acquisition_cost"], 10000)
        self.assertEqual(metrics["acquisition_rate"], 0.05)
        self.assertEqual(metrics["acquisition_contributors"], 1)
        self.assertEqual(metrics["acquisition_excluded"], 1)
        self.assertEqual(metrics["acquisition_unavailable_excluded"], 1)

    def test_no_contributors_returns_null_numeric_acquisition_metrics(self) -> None:
        destinations = [
            self.destination("one", 200000, 10000, None, "unavailable", "high"),
            self.destination("two", 300000, 30000, None, "unavailable", "medium-high"),
        ]

        metrics = build_unified_app.country_summary_metrics(
            {"destination_ids": ["one", "two"]},
            destinations,
        )

        self.assertIsNone(metrics["all_in_entry"])
        self.assertIsNone(metrics["acquisition_cost"])
        self.assertIsNone(metrics["acquisition_rate"])
        self.assertEqual(metrics["acquisition_contributors"], 0)
        self.assertEqual(metrics["acquisition_excluded"], 2)


class AcquisitionDatasetBuildIntegrationTests(unittest.TestCase):
    def test_builder_loads_in_documented_direct_script_mode(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                "import runpy; runpy.run_path('build_unified_app.py', run_name='script_import_test')",
            ],
            cwd=build_unified_app.ROOT / "src",
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_invalid_acquisition_dataset_fails_before_artifact_creation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory) / "artifacts"
            with (
                patch.object(build_unified_app, "ARTIFACTS", artifacts),
                patch.object(build_unified_app, "PUBLIC_ASSETS", artifacts / "assets"),
                patch.object(build_unified_app, "load_acquisition_costs", return_value={"destinations": []}),
            ):
                with self.assertRaises(AcquisitionCostDataError):
                    build_unified_app.build()

            self.assertFalse(artifacts.exists())


class AcquisitionCostRenderingIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls._temporary.cleanup)
        cls.artifacts = Path(cls._temporary.name) / "artifacts"
        acquisition_dataset = deepcopy(build_unified_app.load_acquisition_costs())
        cls.acquisition_dataset = acquisition_dataset
        algarve = next(
            item
            for item in acquisition_dataset["destinations"]
            if item["destination_id"] == "algarve-cascais"
        )
        algarve["sources"][0].update(
            {
                "name": "Source <script>alert('cost')</script> & reference",
                "url": 'https://example.test/cost?a=1&b="quoted"',
            }
        )
        with (
            patch.object(build_unified_app, "ARTIFACTS", cls.artifacts),
            patch.object(build_unified_app, "PUBLIC_ASSETS", cls.artifacts / "assets"),
            patch.object(
                build_unified_app,
                "load_acquisition_costs",
                return_value=acquisition_dataset,
            ),
        ):
            build_unified_app.build()

        cls.dashboard = (cls.artifacts / "dashboard" / "index.html").read_text(
            encoding="utf-8"
        )
        cls.algarve = (
            cls.artifacts / "destinations" / "algarve-cascais" / "index.html"
        ).read_text(encoding="utf-8")
        cls.fukuoka = (
            cls.artifacts / "destinations" / "fukuoka-itoshima" / "index.html"
        ).read_text(encoding="utf-8")
        cls.phuket = (
            cls.artifacts / "destinations" / "phuket-koh-samui" / "index.html"
        ).read_text(encoding="utf-8")
        cls.bali = (
            cls.artifacts / "destinations" / "bali" / "index.html"
        ).read_text(encoding="utf-8")
        cls.da_nang = (
            cls.artifacts / "destinations" / "da-nang-hoi-an" / "index.html"
        ).read_text(encoding="utf-8")
        cls.queenstown = (
            cls.artifacts / "destinations" / "queenstown" / "index.html"
        ).read_text(encoding="utf-8")
        cls.country_comparison = (
            cls.artifacts / "country-comparison" / "index.html"
        ).read_text(encoding="utf-8")
        cls.portugal_country = (
            cls.artifacts / "countries" / "portugal-property" / "index.html"
        ).read_text(encoding="utf-8")
        cls.thailand_country = (
            cls.artifacts / "countries" / "thailand-property" / "index.html"
        ).read_text(encoding="utf-8")
        cls.canada_country = (
            cls.artifacts / "countries" / "canada-property" / "index.html"
        ).read_text(encoding="utf-8")
        cls.vacation_guide = (
            cls.artifacts / "best-places-to-buy-vacation-home-abroad" / "index.html"
        ).read_text(encoding="utf-8")
        cls.second_home_guide = (
            cls.artifacts / "best-places-to-buy-a-second-home-abroad" / "index.html"
        ).read_text(encoding="utf-8")
        cls.methodology = (cls.artifacts / "methodology" / "index.html").read_text(
            encoding="utf-8"
        )
        cls.research_standards = (
            cls.artifacts / "research-standards" / "index.html"
        ).read_text(encoding="utf-8")

    def test_trust_pages_render_the_acquisition_comparison_standard(self) -> None:
        expected_content = (
            "nonresident foreign individual",
            "cash · second home · completed resale · no reliefs",
            "direct personal ownership where the purchase route is legally plausible",
            "fixed 100 m² retirement-home archetype",
            "base total includes only buyer-side costs marked base",
            "Conditional overlays sit outside the base total",
            "not treated as zero",
            "seller taxes, financing, furnishing, renovation, insurance, and recurring ownership costs",
            "Midpoints are used for bounded fee ranges",
            "no intermediate rounding",
            "fixed FX snapshot dated 2026-07",
            "not live exchange rates",
            "representative jurisdiction",
            "grouped destination range",
            "No ordinary all-in total is presented when the route is unavailable",
            "Completeness is independent from purchase-route status",
            "Benchmark calculability is independent from both purchase-route status and cost completeness",
            "No acquisition-cost or all-in figure is calculated when the standardized price benchmark does not represent an eligible asset for the modeled route",
            "known-base/incomplete",
            "country average is labelled as a known-base average",
            "Source hierarchy",
            "Acquisition data as of 2026-09-04",
            "its own review date",
            "Property-price evidence and acquisition-cost confidence are separate",
            "comparative research, not individualized tax or legal advice",
            "nationality, residence, ownership structure, asset type, municipality, and current law",
            "local counsel",
        )
        for page_name, document in (
            ("methodology", self.methodology),
            ("research standards", self.research_standards),
        ):
            article = capture_elements(document, "article", **{"class": "page-article"})
            self.assertEqual(len(article), 1, page_name)
            for expected in expected_content:
                with self.subTest(page=page_name, expected=expected):
                    self.assertIn(expected, article[0]["text"])

    def test_trust_pages_use_injected_acquisition_profile_and_snapshot_dates(self) -> None:
        acquisition_dataset = deepcopy(self.acquisition_dataset)
        acquisition_dataset["as_of"] = "2031-02-03"
        acquisition_dataset["buyer_profile"]["residency"] = "temporary_nonresident"
        acquisition_dataset["buyer_profile"]["financing"] = "bridge_loan"
        fx = deepcopy(build_unified_app.load_json("fx_rates.json"))
        fx["as_of"] = "2031-01-02"
        comparison_methodology = deepcopy(build_unified_app.load_comparison_methodology())
        comparison_methodology["label"] = "Injected retirement-home archetype"
        original_load_json = build_unified_app.load_json

        def load_json_with_test_fx(name: str):
            return fx if name == "fx_rates.json" else original_load_json(name)

        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory) / "artifacts"
            with (
                patch.object(build_unified_app, "ARTIFACTS", artifacts),
                patch.object(build_unified_app, "PUBLIC_ASSETS", artifacts / "assets"),
                patch.object(
                    build_unified_app,
                    "load_acquisition_costs",
                    return_value=acquisition_dataset,
                ),
                patch.object(
                    build_unified_app,
                    "load_comparison_methodology",
                    return_value=comparison_methodology,
                ),
                patch.object(build_unified_app, "load_json", side_effect=load_json_with_test_fx),
            ):
                build_unified_app.build()

            for slug in ("methodology", "research-standards"):
                document = (artifacts / slug / "index.html").read_text(encoding="utf-8")
                article = capture_elements(document, "article", **{"class": "page-article"})
                self.assertEqual(len(article), 1, slug)
                self.assertIn("temporary nonresident foreign individual", article[0]["text"])
                self.assertIn("bridge loan", article[0]["text"])
                self.assertIn("Injected retirement-home archetype", article[0]["text"])
                self.assertIn("Acquisition data as of 2031-02-03", article[0]["text"])
                self.assertIn("fixed FX snapshot dated 2031-01-02", article[0]["text"])

    def test_dashboard_card_renders_its_own_acquisition_decision_fields(self) -> None:
        cards = capture_elements(
            self.dashboard,
            "details",
            **{"class": "destination-card", "data-id": "algarve-cascais"},
        )
        self.assertEqual(len(cards), 1)
        card = cards[0]["text"]
        for expected in (
            "Acquisition costs $38,610; known-base/incomplete 8.4%; known-base/incomplete effective · medium-high confidence",
            "All-in acquisition capital $498,610; known-base/incomplete",
            "Available: Direct individual acquisition",
            "proxy property price evidence",
            "unquantified conditional items",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, card)
        self.assertNotIn("$38,610–$38,610", card)
        self.assertNotIn("medium-high acquisition evidence", card)
        self.assertEqual(card.count("medium-high confidence"), 1)

    def test_dashboard_cards_suppress_uncalculable_benchmark_totals_with_reasons(self) -> None:
        for destination_id, forbidden in (
            ("bali", "$220,000"),
            ("phuket-koh-samui", "$290,000"),
        ):
            with self.subTest(destination_id=destination_id):
                cards = capture_elements(
                    self.dashboard,
                    "details",
                    **{"class": "destination-card", "data-id": destination_id},
                )
                self.assertEqual(len(cards), 1)
                card = cards[0]["text"]
                self.assertIn("Acquisition costs Not quantified", card)
                self.assertIn("Not quantified effective", card)
                self.assertIn("All-in acquisition capital Not presented", card)
                self.assertIn("Benchmark not calculable", card)
                self.assertNotIn(
                    f"All-in acquisition capital {forbidden}",
                    card,
                )

    def test_available_quick_decision_includes_all_in_and_route_status(self) -> None:
        panels = capture_elements(
            self.algarve,
            "section",
            **{"aria-label": "Quick destination decision"},
        )
        self.assertEqual(len(panels), 1)
        budget_signal = panels[0]["text"]
        self.assertIn(
            "Budget signal $498,610; known-base/incomplete all-in acquisition capital",
            budget_signal,
        )
        self.assertIn("Available: Direct individual acquisition", budget_signal)

    def test_conditional_quick_decision_suppresses_an_uncalculable_benchmark(self) -> None:
        panels = capture_elements(
            self.phuket,
            "section",
            **{"aria-label": "Quick destination decision"},
        )
        self.assertEqual(len(panels), 1)
        budget_signal = panels[0]["text"]
        self.assertIn("Not presented all-in acquisition capital", budget_signal)
        self.assertIn("Conditional: Foreign-quota freehold condominium only", budget_signal)
        self.assertIn("benchmark blends villas and condominiums", budget_signal)
        self.assertNotIn("$290,000", budget_signal)

    def test_available_hero_renders_route_qualified_all_in_capital(self) -> None:
        heroes = capture_elements(self.algarve, "header", **{"class": "page-hero"})
        self.assertEqual(len(heroes), 1)
        hero = heroes[0]["text"]
        self.assertIn(
            "All-in acquisition capital $498,610; known-base/incomplete",
            hero,
        )
        self.assertIn("Available: Direct individual acquisition", hero)
        self.assertIn("Property price evidence proxy", hero)

    def test_acquisition_section_renders_only_its_cost_basis_and_source_details(self) -> None:
        sections = capture_elements(self.algarve, "details", id="acquisition-costs")
        self.assertEqual(len(sections), 1)
        section = sections[0]
        section_text = section["text"]
        for expected in (
            "Acquisition Costs",
            "All-in acquisition capital $498,610; known-base/incomplete",
            "Effective rate 8.4%; known-base/incomplete",
            "Nonresident residential IMT tax $34,500",
            "Stamp duty on acquisition tax $3,680",
            "Casa Pronta execution and one-property registration registration $430",
            "Conditional items outside the base total",
            "IMT and stamp-duty uplift to taxable patrimonial value",
            "Not quantified",
            "Cascais municipality and a representative Algarve municipality",
            "Nonresident individual · second home · cash · resale · no reliefs",
            "Reviewed: 2026-08-19",
            "Portuguese Tax Authority - IMT Code Article 12",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, section_text)
        hrefs = {
            attributes.get("href")
            for tag, attributes in section["attributes"]
            if tag == "a"
        }
        self.assertIn(
            "https://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/codigos_tributarios/cimt/Pages/cimt12.aspx",
            hrefs,
        )

    def test_conditional_acquisition_section_preserves_null_amounts(self) -> None:
        sections = capture_elements(self.phuket, "details", id="acquisition-costs")
        self.assertEqual(len(sections), 1)
        section = sections[0]["text"]
        self.assertIn("Acquisition costs Not quantified", section)
        self.assertIn("Effective rate Not quantified", section)
        self.assertIn("All-in acquisition capital Not presented", section)
        self.assertIn("Acquisition benchmark Not calculable", section)
        self.assertIn("benchmark blends villas and condominiums", section)
        self.assertIn("unquantified conditional items", section)
        self.assertIn("Buyer share of condominium transfer fee (amount unquantified)", section)
        self.assertIn("Lease registration fee and stamp duty", section)
        self.assertGreaterEqual(section.count("Not quantified"), 2)
        self.assertNotIn("$0", section)

    def test_bali_is_unavailable_and_uncalculable_across_destination_surfaces(self) -> None:
        hero = capture_elements(self.bali, "header", **{"class": "page-hero"})[0]["text"]
        self.assertIn("Unavailable:", hero)
        self.assertIn("Acquisition benchmark Not calculable", hero)
        self.assertIn("below Bali&#x27;s IDR5 billion", self.bali)
        self.assertNotIn("All-in acquisition capital $220,000", self.bali)

        section = capture_elements(self.bali, "details", id="acquisition-costs")[0]["text"]
        self.assertIn("Acquisition costs Not quantified", section)
        self.assertIn("Effective rate Not quantified", section)
        self.assertIn("All-in acquisition capital Not presented", section)

    def test_destination_without_conditional_items_has_one_no_items_message(self) -> None:
        section = capture_elements(self.da_nang, "details", id="acquisition-costs")[0]["text"]
        self.assertEqual(section.count("No conditional acquisition items identified."), 1)
        self.assertNotIn("No conditional items identified.", section)

    def test_peer_card_renders_its_own_all_in_and_route_status(self) -> None:
        cards = capture_elements(self.algarve, "article", **{"class": "comparison-card"})
        fukuoka = next(card["text"] for card in cards if "Fukuoka / Itoshima" in card["text"])
        self.assertIn(
            "All-in capital $271,737 ($271,427–$272,047); known-base/incomplete",
            fukuoka,
        )
        self.assertIn("Available: Direct individual freehold or condominium ownership", fukuoka)

        app_data = json.loads(capture_elements(self.dashboard, "script", id="app-data")[0]["text"])
        phuket = next(
            item for item in app_data["destinations"]
            if item["id"] == "phuket-koh-samui"
        )
        peer_html = build_unified_app.destination_compare_html(phuket, [phuket])
        peer = capture_elements(peer_html, "article", **{"class": "comparison-card"})[0]["text"]
        self.assertIn("All-in capital Not presented", peer)
        self.assertIn("Benchmark not calculable", peer)
        self.assertIn("benchmark blends villas and condominiums", peer)

    def test_unavailable_route_omits_ordinary_hero_all_in_total(self) -> None:
        heroes = capture_elements(self.queenstown, "header", **{"class": "page-hero"})
        self.assertEqual(len(heroes), 1)
        hero = heroes[0]["text"]
        self.assertIn("Unavailable: Generic nonresident second-home purchase unavailable", hero)
        self.assertNotIn("All-in acquisition capital", hero)
        hero_hrefs = {
            attributes.get("href")
            for tag, attributes in heroes[0]["attributes"]
            if tag == "a"
        }
        self.assertIn("#acquisition-costs", hero_hrefs)
        sections = capture_elements(self.queenstown, "details", id="acquisition-costs")
        self.assertEqual(len(sections), 1)
        self.assertIn("No ordinary all-in total is presented", sections[0]["text"])

    def test_malformed_routes_fail_closed_in_all_destination_route_branches(self) -> None:
        app_data = json.loads(capture_elements(self.dashboard, "script", id="app-data")[0]["text"])
        algarve = next(item for item in app_data["destinations"] if item["id"] == "algarve-cascais")
        for variant, route in (
            ("missing route", ...),
            ("null route", None),
            ("malformed route", "available"),
            ("missing status", {"label": "Candidate route"}),
            ("null status", {"status": None, "label": "Candidate route"}),
            ("unknown status", {"status": "pending", "label": "Candidate route"}),
            ("malformed status", {"status": 1, "label": "Candidate route"}),
        ):
            with self.subTest(variant=variant):
                destination = deepcopy(algarve)
                if route is ...:
                    destination.pop("purchase_route")
                else:
                    destination["purchase_route"] = route
                try:
                    quick = build_unified_app.destination_quick_decision_html(destination)
                    acquisition = build_unified_app.destination_acquisition_cost_html(destination)
                    page = build_unified_app.build_destination_page(
                        destination,
                        [],
                        [destination],
                        build_unified_app.SEO_PAGES,
                    )
                except (AttributeError, TypeError) as error:
                    self.fail(f"{variant} destination route branch raised {error!r}")

                quick_panels = capture_elements(
                    quick,
                    "section",
                    **{"aria-label": "Quick destination decision"},
                )
                self.assertEqual(len(quick_panels), 1)
                self.assertIn("Unavailable:", quick_panels[0]["text"])
                self.assertIn("no ordinary all-in total", quick_panels[0]["text"])
                self.assertNotIn("$498,610 all-in acquisition capital", quick_panels[0]["text"])

                acquisition_sections = capture_elements(acquisition, "details", id="acquisition-costs")
                self.assertEqual(len(acquisition_sections), 1)
                self.assertIn("No ordinary all-in total is presented", acquisition_sections[0]["text"])
                self.assertIn("Unavailable:", acquisition_sections[0]["text"])

                heroes = capture_elements(page, "header", **{"class": "page-hero"})
                self.assertEqual(len(heroes), 1)
                self.assertIn("Unavailable:", heroes[0]["text"])
                self.assertNotIn("All-in acquisition capital", heroes[0]["text"])

    def test_generated_comparison_behavior_never_coerces_null_to_zero(self) -> None:
        function_names = (
            "destinationMetric",
            "escapeHtml",
            "usd",
            "usdRange",
            "acquisitionCompleteness",
            "benchmarkCell",
            "acquisitionCostCell",
            "allInCell",
            "routeCell",
            "acquisitionRateCell",
            "selectedCompareDestinations",
            "renderCompare",
        )
        functions = [
            extract_javascript_function(self.dashboard, name)
            for name in function_names
        ]
        missing = [name for name, function in zip(function_names, functions) if not function]
        self.assertEqual(missing, [], f"generated JavaScript functions missing: {missing}")
        if missing:
            return

        fixture = [
            {
                "id": "null-costs",
                "name": "Null costs",
                "country": "Test",
                "custom_score": 4.0,
                "comparison_home_usd": 100000,
                "comparison_home_evidence": "proxy",
                "acquisition_cost_estimate_usd": None,
                "all_in_acquisition_estimate_usd": None,
                "acquisition_cost_rate": None,
                "conditional_acquisition_components": [],
                "purchase_route": {"status": "available", "label": "Direct route"},
                "acquisition_benchmark_status": "calculable",
                "acquisition_benchmark_reason": "",
                "acquisition_cost_confidence": "low",
                "acquisition_cost_complete": True,
                "acquisition_cost_completeness": "complete",
                "net_yield_estimate": "n/a",
                "decision_dimensions": [],
                "profit_driver": "Null behavior fixture",
            },
            {
                "id": "known-costs",
                "name": "Known costs",
                "country": "Test",
                "custom_score": 3.5,
                "comparison_home_usd": 10000,
                "comparison_home_evidence": "aligned benchmark",
                "acquisition_cost_estimate_usd": 1000,
                "all_in_acquisition_estimate_usd": 11000,
                "acquisition_cost_rate": 0.1,
                "conditional_acquisition_components": [],
                "purchase_route": {"status": "available", "label": "Known route"},
                "acquisition_benchmark_status": "calculable",
                "acquisition_benchmark_reason": "",
                "acquisition_cost_confidence": "high",
                "acquisition_cost_complete": True,
                "acquisition_cost_completeness": "complete",
                "net_yield_estimate": "4%",
                "decision_dimensions": [],
                "profit_driver": "Known behavior fixture",
            },
        ]
        node_script = "\n".join(functions) + f"""
const fixture = {json.dumps(fixture)};
fixture.push({{...fixture[0], id: "undefined-costs", name: "Undefined costs", acquisition_cost_estimate_usd: undefined, all_in_acquisition_estimate_usd: undefined, acquisition_cost_rate: undefined}});
fixture.push({{...fixture[0], id: "nonfinite-costs", name: "Nonfinite costs", acquisition_cost_estimate_usd: Number.NaN, all_in_acquisition_estimate_usd: Number.POSITIVE_INFINITY, acquisition_cost_rate: Number.NaN}});
const compareSelected = new Set(fixture.map((item) => item.id));
const destinationsById = new Map(fixture.map((item) => [item.id, item]));
const compareOutput = {{ className: "", textContent: "", innerHTML: "" }};
const conditionalNull = {{
  all_in_acquisition_estimate_usd: null,
  purchase_route: {{status: "conditional"}},
  acquisition_benchmark_status: "calculable",
  acquisition_benchmark_reason: "",
  conditional_acquisition_components: [{{estimate_usd: null}}],
  acquisition_cost_complete: false,
  acquisition_cost_completeness: "known-base/incomplete"
}};
const unavailable = {{
  all_in_acquisition_estimate_usd: null,
  purchase_route: {{status: "unavailable"}},
  acquisition_benchmark_status: "calculable",
  acquisition_benchmark_reason: "",
  conditional_acquisition_components: []
}};
const uncalculable = {{
  acquisition_cost_low_usd: 1000,
  acquisition_cost_estimate_usd: 1000,
  acquisition_cost_high_usd: 1000,
  acquisition_cost_rate: 0.01,
  all_in_acquisition_low_usd: 101000,
  all_in_acquisition_estimate_usd: 101000,
  all_in_acquisition_high_usd: 101000,
  purchase_route: {{status: "conditional"}},
  acquisition_benchmark_status: "not_calculable",
  acquisition_benchmark_reason: "The benchmark is not route-aligned.",
  conditional_acquisition_components: [],
  acquisition_cost_complete: true,
  acquisition_cost_completeness: "complete"
}};
renderCompare();
process.stdout.write(JSON.stringify({{
  usdNull: usd(null),
  usdUndefined: usd(undefined),
  usdNonFinite: usd(Number.NaN),
  acquisitionNull: acquisitionCostCell(fixture[0]),
  allInNull: allInCell(fixture[0]),
  allInConditionalNull: allInCell(conditionalNull),
  allInUnavailable: allInCell(unavailable),
  acquisitionUncalculable: acquisitionCostCell(uncalculable),
  allInUncalculable: allInCell(uncalculable),
  rateUncalculable: acquisitionRateCell(uncalculable),
  benchmarkUncalculable: benchmarkCell(uncalculable),
  html: compareOutput.innerHTML
}}));
"""
        completed = subprocess.run(
            ["node", "-e", node_script],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["usdNull"], "Not quantified")
        self.assertEqual(result["usdUndefined"], "Not quantified")
        self.assertEqual(result["usdNonFinite"], "Not quantified")
        self.assertEqual(result["acquisitionNull"], "Not quantified")
        self.assertEqual(result["allInNull"], "Not quantified")
        self.assertEqual(
            result["allInConditionalNull"],
            "Not quantified; known-base/incomplete",
        )
        self.assertEqual(result["allInUnavailable"], "Not presented")
        self.assertEqual(result["acquisitionUncalculable"], "Not quantified")
        self.assertEqual(result["allInUncalculable"], "Not presented")
        self.assertEqual(result["rateUncalculable"], "Not quantified")
        self.assertEqual(
            result["benchmarkUncalculable"],
            "Not calculable: The benchmark is not route-aligned.",
        )
        self.assertGreaterEqual(result["html"].count("<td>Not quantified</td>"), 9)
        self.assertNotIn("<td>$0</td>", result["html"])
        self.assertNotIn("<td>0.0%</td>", result["html"])

    def test_acquisition_source_content_and_url_are_html_safe(self) -> None:
        self.assertNotIn("<script>alert('cost')</script>", self.dashboard)
        sections = capture_elements(self.algarve, "details", id="acquisition-costs")
        self.assertEqual(len(sections), 1)
        self.assertIn(
            "Source &lt;script&gt;alert(&#x27;cost&#x27;)&lt;/script&gt; &amp; reference",
            self.algarve,
        )
        hrefs = {
            attributes.get("href")
            for tag, attributes in sections[0]["attributes"]
            if tag == "a"
        }
        self.assertIn('https://example.test/cost?a=1&b="quoted"', hrefs)

    def test_country_comparison_rows_show_all_in_contributors_exclusions_and_evidence(self) -> None:
        rows = capture_elements(self.country_comparison, "tr")
        portugal = next(row["text"] for row in rows if "Portugal" in row["text"])
        canada = next(row["text"] for row in rows if "Canada" in row["text"])
        thailand = next(row["text"] for row in rows if "Thailand" in row["text"])

        self.assertIn("Known-base avg all-in $466,120", portugal)
        self.assertIn("known-base/incomplete", portugal)
        self.assertIn("2 contributors", portugal)
        self.assertIn("0 unavailable exclusions", portugal)
        self.assertIn("mixed/proxy", portugal)
        self.assertIn("Known-base avg all-in $1,345,047", canada)
        self.assertIn("known-base/incomplete", canada)
        self.assertIn("1 contributor", canada)
        self.assertIn("2 unavailable exclusions", canada)
        self.assertIn("mixed/proxy", canada)
        self.assertIn("Avg all-in Not quantified", thailand)
        self.assertIn("0 contributors", thailand)
        self.assertIn("1 uncalculable benchmark exclusion", thailand)
        self.assertNotRegex(thailand, r"Avg all-in \$[\d,]+")

    def test_country_comparison_without_contributors_has_no_numeric_average(self) -> None:
        unavailable = {
            "id": "blocked",
            "name": "Blocked",
            "country": "Test",
            "category": "Test",
            "comparison_home_usd": 200000,
            "comparison_home_evidence": "proxy",
            "purchase_route": {"status": "unavailable", "label": "No route"},
            "acquisition_benchmark_status": "calculable",
            "acquisition_benchmark_reason": "",
            "acquisition_cost_confidence": "high",
            "acquisition_cost_estimate_usd": 10000,
            "all_in_acquisition_estimate_usd": None,
            "decision_score": 4,
            "decision_dimensions": [],
        }
        hub = {
            "slug": "test-property",
            "country": "Test Country",
            "description": "Test route",
            "destination_ids": ["blocked"],
        }
        with patch.object(build_unified_app, "COUNTRY_HUBS", [hub]):
            document = build_unified_app.build_country_comparison_page([unavailable], [])

        rows = capture_elements(document, "tr")
        row = next(item["text"] for item in rows if "Test Country" in item["text"])
        self.assertIn("Avg all-in Not quantified", row)
        self.assertIn("0 contributors", row)
        self.assertIn("1 unavailable exclusion", row)
        self.assertIn("0 uncalculable benchmark exclusions", row)
        self.assertIn("mixed/proxy", row)
        self.assertNotRegex(row, r"Avg all-in \$[\d,]+")

    def test_country_hub_table_and_mobile_cards_show_route_aware_all_in(self) -> None:
        portugal_rows = capture_elements(self.portugal_country, "tr")
        algarve_row = next(row["text"] for row in portugal_rows if "Algarve / Cascais" in row["text"])
        self.assertIn("All-in $498,610; known-base/incomplete", algarve_row)
        self.assertIn("Available: Direct individual acquisition", algarve_row)
        self.assertIn("medium-high confidence", algarve_row)

        thailand_cards = capture_elements(
            self.thailand_country,
            "article",
            **{"class": "comparison-card"},
        )
        phuket_card = next(card["text"] for card in thailand_cards if "Phuket / Koh Samui" in card["text"])
        self.assertIn(
            "All-in Not presented",
            phuket_card,
        )
        self.assertIn("Conditional: Foreign-quota freehold condominium only", phuket_card)
        self.assertIn("low confidence", phuket_card)
        self.assertIn("Benchmark not calculable", phuket_card)
        self.assertIn("benchmark blends villas and condominiums", phuket_card)
        self.assertNotIn("All-in $290,000", phuket_card)

        canada_rows = capture_elements(self.canada_country, "tr")
        victoria_row = next(row["text"] for row in canada_rows if "Vancouver Island / Victoria" in row["text"])
        self.assertIn("All-in Not presented", victoria_row)
        self.assertIn("Unavailable: Generic non-Canadian direct residential purchase unavailable through 1 January 2027", victoria_row)
        self.assertNotRegex(victoria_row, r"All-in \$[\d,]+")

    def test_guide_table_cards_summary_and_quick_answer_show_route_aware_all_in(self) -> None:
        guide_summary = capture_elements(
            self.vacation_guide,
            "aside",
            **{"class": "seo-hero-card"},
        )
        self.assertEqual(len(guide_summary), 1)
        self.assertIn(
            "Top all-in $271,737 ($271,427–$272,047); known-base/incomplete",
            guide_summary[0]["text"],
        )
        self.assertIn("Available: Direct individual freehold or condominium ownership", guide_summary[0]["text"])

        rows = capture_elements(self.vacation_guide, "tr")
        algarve_row = next(row["text"] for row in rows if "Algarve / Cascais" in row["text"])
        self.assertIn("All-in $498,610; known-base/incomplete", algarve_row)
        self.assertIn("Available: Direct individual acquisition", algarve_row)

        cards = capture_elements(
            self.vacation_guide,
            "article",
            **{"class": "seo-destination-card"},
        )
        algarve_card = next(card["text"] for card in cards if "Algarve / Cascais" in card["text"])
        self.assertIn("All-in $498,610; known-base/incomplete", algarve_card)
        self.assertIn("Available: Direct individual acquisition", algarve_card)

        quick_answers = capture_elements(
            self.vacation_guide,
            "section",
            **{"class": "quick-answer"},
        )
        self.assertEqual(len(quick_answers), 1)
        quick_cards = capture_elements(self.vacation_guide, "article")
        phuket = next(card["text"] for card in quick_cards if "vacation-home candidate Phuket / Koh Samui" in card["text"])
        self.assertIn(
            "All-in Not presented",
            phuket,
        )
        self.assertIn("Conditional: Foreign-quota freehold condominium only", phuket)
        self.assertIn("Benchmark not calculable", phuket)
        self.assertIn("benchmark blends villas and condominiums", phuket)
        self.assertNotIn("All-in $290,000", phuket)

        second_home_rows = capture_elements(self.second_home_guide, "tr")
        queenstown = next(row["text"] for row in second_home_rows if "Queenstown" in row["text"])
        self.assertIn("All-in Not presented", queenstown)
        self.assertIn("Unavailable: Generic nonresident second-home purchase unavailable", queenstown)
        self.assertNotRegex(queenstown, r"All-in \$[\d,]+")

    def test_total_all_in_displays_never_use_per_square_metre_units(self) -> None:
        surfaces = (
            ("country comparison rows", capture_elements(self.country_comparison, "tr")),
            ("country hub rows", capture_elements(self.portugal_country, "tr")),
            ("country hub cards", capture_elements(self.thailand_country, "article", **{"class": "comparison-card"})),
            ("guide rows", capture_elements(self.vacation_guide, "tr")),
            ("guide cards", capture_elements(self.vacation_guide, "article", **{"class": "seo-destination-card"})),
            ("quick answer", capture_elements(self.vacation_guide, "section", **{"class": "quick-answer"})),
        )
        for surface_name, elements in surfaces:
            with self.subTest(surface=surface_name):
                all_in_elements = [item["text"] for item in elements if "all-in" in item["text"].lower()]
                self.assertTrue(all_in_elements)
                for text in all_in_elements:
                    self.assertNotRegex(text, r"(?i)all-in.*?/(?:m2|m²)")

        app_data = json.loads(capture_elements(self.dashboard, "script", id="app-data")[0]["text"])
        fukuoka = next(item for item in app_data["destinations"] if item["id"] == "fukuoka-itoshima")
        self.assertIsInstance(fukuoka["all_in_acquisition_usd_per_m2"], (int, float))

    def test_embedded_json_contains_complete_methodology_sources_and_calculated_components(self) -> None:
        scripts = capture_elements(self.dashboard, "script", id="app-data")
        self.assertEqual(len(scripts), 1)
        app_data = json.loads(scripts[0]["text"])

        self.assertEqual(
            app_data["acquisition_cost_methodology"],
            self.acquisition_dataset,
        )
        algarve = next(item for item in app_data["destinations"] if item["id"] == "algarve-cascais")
        self.assertEqual(algarve["all_in_acquisition_estimate_usd"], 498610.44)
        self.assertIs(algarve["acquisition_cost_complete"], False)
        self.assertEqual(
            algarve["acquisition_cost_completeness"],
            "known-base/incomplete",
        )
        da_nang = next(
            item for item in app_data["destinations"] if item["id"] == "da-nang-hoi-an"
        )
        self.assertEqual(da_nang["purchase_route"]["status"], "conditional")
        self.assertIs(da_nang["acquisition_cost_complete"], True)
        self.assertEqual(da_nang["acquisition_cost_completeness"], "complete")
        self.assertEqual(algarve["acquisition_components"][0]["label"], "Nonresident residential IMT")
        self.assertEqual(algarve["acquisition_components"][0]["estimate_usd"], 34500.0)
        self.assertEqual(algarve["acquisition_sources"][0]["id"], "pt-imt-article-17")
        for destination_id, route_status in (
            ("bali", "unavailable"),
            ("phuket-koh-samui", "conditional"),
        ):
            with self.subTest(destination_id=destination_id):
                destination = next(
                    item for item in app_data["destinations"]
                    if item["id"] == destination_id
                )
                self.assertEqual(destination["purchase_route"]["status"], route_status)
                self.assertEqual(
                    destination["acquisition_benchmark_status"],
                    "not_calculable",
                )
                self.assertTrue(destination["acquisition_benchmark_reason"])
                for field in (
                    "acquisition_cost_low_usd",
                    "acquisition_cost_estimate_usd",
                    "acquisition_cost_high_usd",
                    "acquisition_cost_rate",
                    "all_in_acquisition_low_usd",
                    "all_in_acquisition_estimate_usd",
                    "all_in_acquisition_high_usd",
                    "all_in_acquisition_usd_per_m2",
                ):
                    self.assertIsNone(destination[field], field)

    def test_generated_json_csv_and_memo_execute_with_route_aware_null_safe_outputs(self) -> None:
        function_names = (
            "destinationMetric",
            "escapeHtml",
            "usd",
            "usdRange",
            "acquisitionCompleteness",
            "benchmarkCell",
            "acquisitionCostCell",
            "allInCell",
            "routeCell",
            "acquisitionRateCell",
            "baseComponentSummary",
            "conditionalAcquisitionWarning",
            "buildJsonExport",
            "csvValue",
            "buildCsv",
            "selectedCompareDestinations",
            "memoDestinations",
            "buildMemoHtml",
        )
        functions = [extract_javascript_function(self.dashboard, name) for name in function_names]
        missing = [name for name, function in zip(function_names, functions) if not function]
        self.assertEqual(missing, [], f"generated JavaScript functions missing: {missing}")
        if missing:
            return

        app_data = json.loads(capture_elements(self.dashboard, "script", id="app-data")[0]["text"])
        node_script = "\n".join(functions) + f"""
const data = {json.dumps(app_data)};
const source = data.destinations;
const nullRow = {{
  ...source.find((item) => item.id === "algarve-cascais"),
  id: "null-export",
  name: "Null export",
  comparison_home_usd: null,
  acquisition_cost_low_usd: null,
  acquisition_cost_estimate_usd: null,
  acquisition_cost_high_usd: null,
  acquisition_cost_rate: null,
  all_in_acquisition_low_usd: null,
  all_in_acquisition_estimate_usd: null,
  all_in_acquisition_high_usd: null,
  acquisition_jurisdiction_basis: null,
  acquisition_cost_reviewed_on: null
}};
data.destinations = [
  source.find((item) => item.id === "fukuoka-itoshima"),
  source.find((item) => item.id === "algarve-cascais"),
  source.find((item) => item.id === "phuket-koh-samui"),
  source.find((item) => item.id === "queenstown"),
  nullRow
];
data.destinations.forEach((item) => item.custom_score = item.decision_score);
const destinationsById = new Map(data.destinations.map((item) => [item.id, item]));
const compareSelected = new Set(["fukuoka-itoshima", "algarve-cascais", "phuket-koh-samui", "queenstown", "null-export"]);
const memoShortlist = new Set();
const exported = JSON.parse(buildJsonExport());
const csv = buildCsv();
const memo = buildMemoHtml();
process.stdout.write(JSON.stringify({{
  methodologyDestinationCount: exported.acquisition_cost_methodology.destinations.length,
  exportedAllIn: exported.destinations.find((item) => item.id === "algarve-cascais").all_in_acquisition_estimate_usd,
  csv,
  memo
}}));
"""
        completed = subprocess.run(
            ["node", "-e", node_script],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(
            result["methodologyDestinationCount"],
            len(self.acquisition_dataset["destinations"]),
        )
        self.assertEqual(result["exportedAllIn"], 498610.44)

        csv_rows = list(csv.reader(io.StringIO(result["csv"])))
        headers = csv_rows[0]
        insertion = headers.index("comparison_home_evidence") + 1
        self.assertEqual(
            headers[insertion:insertion + 15],
            [
                "acquisition_cost_low_usd",
                "acquisition_cost_estimate_usd",
                "acquisition_cost_high_usd",
                "acquisition_cost_rate",
                "all_in_acquisition_low_usd",
                "all_in_acquisition_estimate_usd",
                "all_in_acquisition_high_usd",
                "purchase_route_status",
                "acquisition_cost_confidence",
                "acquisition_jurisdiction_basis",
                "acquisition_cost_reviewed_on",
                "acquisition_benchmark_status",
                "acquisition_benchmark_reason",
                "acquisition_cost_complete",
                "acquisition_cost_completeness",
            ],
        )
        null_csv_row = next(row for row in csv_rows if "Null export" in row)
        self.assertEqual(null_csv_row[headers.index("comparison_home_usd")], "")
        for header in (
            "acquisition_cost_low_usd",
            "acquisition_cost_estimate_usd",
            "acquisition_cost_high_usd",
            "acquisition_cost_rate",
            "all_in_acquisition_low_usd",
            "all_in_acquisition_estimate_usd",
            "all_in_acquisition_high_usd",
            "acquisition_jurisdiction_basis",
            "acquisition_cost_reviewed_on",
        ):
            self.assertEqual(null_csv_row[headers.index(header)], "", header)

        phuket_csv_row = next(row for row in csv_rows if "Phuket / Koh Samui" in row)
        for header in (
            "acquisition_cost_low_usd",
            "acquisition_cost_estimate_usd",
            "acquisition_cost_high_usd",
            "acquisition_cost_rate",
            "all_in_acquisition_low_usd",
            "all_in_acquisition_estimate_usd",
            "all_in_acquisition_high_usd",
        ):
            self.assertEqual(phuket_csv_row[headers.index(header)], "", header)
        self.assertEqual(
            phuket_csv_row[headers.index("acquisition_benchmark_status")],
            "not_calculable",
        )
        self.assertIn(
            "benchmark blends villas and condominiums",
            phuket_csv_row[headers.index("acquisition_benchmark_reason")],
        )

        memo = result["memo"]
        for expected in (
            "Property price</dt><dd>$460,000",
            "Acquisition costs</dt><dd>$9,737 ($9,427–$10,047); known-base/incomplete",
            "All-in capital</dt><dd>$271,737 ($271,427–$272,047); known-base/incomplete",
            "Acquisition costs</dt><dd>$38,610; known-base/incomplete",
            "All-in capital</dt><dd>$498,610; known-base/incomplete",
            "Effective rate</dt><dd>8.4%; known-base/incomplete",
            "Cost completeness</dt><dd>known-base/incomplete",
            "Purchase route</dt><dd>Available: Direct individual acquisition",
            "Acquisition confidence</dt><dd>medium-high",
            "Acquisition benchmark</dt><dd>Calculable",
            "Nonresident residential IMT — $34,500",
            "Known-base/incomplete; 2 unquantified conditional items remain outside comparable totals.",
            "All-in capital</dt><dd>Not presented",
            "Acquisition costs</dt><dd>Not quantified",
            "Effective rate</dt><dd>Not quantified",
            "Acquisition benchmark</dt><dd>Not calculable: The $290,000 benchmark blends villas and condominiums",
            "Property price</dt><dd>Not quantified",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, memo)
        self.assertNotIn("All-in capital</dt><dd>$0", memo)
        self.assertNotRegex(memo, r"All-in capital</dt><dd>[^<]*/m2")
        phuket_section = memo.split("<h2>Phuket / Koh Samui", 1)[1].split("</section>", 1)[0]
        self.assertNotIn("Acquisition costs</dt><dd>$0", phuket_section)
        self.assertNotIn("All-in capital</dt><dd>$290,000", phuket_section)
        null_section = memo.split("<h2>Null export", 1)[1].split("</section>", 1)[0]
        self.assertIn("Cost completeness</dt><dd>known-base/incomplete", null_section)
        self.assertIn(
            "Effective rate</dt><dd>Not quantified; known-base/incomplete",
            null_section,
        )


if __name__ == "__main__":
    unittest.main()
