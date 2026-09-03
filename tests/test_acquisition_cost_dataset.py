from __future__ import annotations

import json
import math
import unittest
from copy import deepcopy
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from src.acquisition_costs import (
    AcquisitionCostDataError,
    CONFIDENCE_LEVELS,
    ROUTE_STATUSES,
    calculate_acquisition_costs,
    validate_acquisition_dataset,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "acquisition_cost_record.json"

ADDED_DESTINATION_IDS = {
    "dubai",
    "gold-coast-sunshine-coast",
    "los-angeles-orange-county",
    "miami-fort-lauderdale",
    "perth-margaret-river",
    "sydney-melbourne",
    "vancouver",
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


class AcquisitionCostDatasetContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.destinations = load_json(DATA_DIR / "destinations.json")
        cls.fx_rates = load_json(DATA_DIR / "fx_rates.json")
        cls.dataset = load_json(DATA_DIR / "acquisition_costs.json")
        cls.fixture = load_json(FIXTURE_PATH)
        cls.fx_rates_to_usd = cls.fx_rates["rates_to_usd"]
        cls.destinations_by_id = {
            destination["id"]: destination for destination in cls.destinations
        }

    def test_synthetic_fixture_validates_and_calculates_hand_derived_costs(self) -> None:
        validate_acquisition_dataset(
            {
                "as_of": "2026-08-19",
                "reporting_currency": "USD",
                "buyer_profile": {
                    "residency": "nonresident",
                    "buyer_type": "individual",
                    "use": "second_home",
                    "financing": "cash",
                    "property_market": "resale",
                    "reliefs": "none",
                },
                "destinations": [self.fixture],
            },
            expected_destination_ids={"fixture-destination"},
            fx_rates_to_usd=self.fx_rates_to_usd,
        )

        result = calculate_acquisition_costs(
            self.fixture,
            property_price_usd=200_000,
            fx_rates_to_usd=self.fx_rates_to_usd,
        )

        self.assertEqual(result["base_cost_low_usd"], 10_000)
        self.assertEqual(result["base_cost_estimate_usd"], 10_000)
        self.assertEqual(result["base_cost_high_usd"], 10_000)
        self.assertEqual(result["all_in_low_usd"], 210_000)
        self.assertEqual(result["all_in_estimate_usd"], 210_000)
        self.assertEqual(result["all_in_high_usd"], 210_000)
        self.assertEqual(result["all_in_usd_per_m2"], 2_100)
        self.assertEqual(result["conditional_components"][0]["estimate_usd"], 750)

    def test_top_level_metadata_matches_approved_baseline(self) -> None:
        self.assertEqual(self.dataset["reporting_currency"], "USD")
        self.assertEqual(
            self.dataset["buyer_profile"],
            {
                "residency": "nonresident",
                "buyer_type": "individual",
                "use": "second_home",
                "financing": "cash",
                "property_market": "resale",
                "reliefs": "none",
            },
        )
        date.fromisoformat(self.dataset["as_of"])

    def test_present_records_are_complete_and_validate(self) -> None:
        records = self.dataset["destinations"]
        validate_acquisition_dataset(
            self.dataset,
            expected_destination_ids={record["destination_id"] for record in records},
            fx_rates_to_usd=self.fx_rates_to_usd,
        )

        for record in records:
            with self.subTest(destination_id=record["destination_id"]):
                self.assertTrue(record["jurisdiction_basis"].strip())
                self.assertIn(record["purchase_route"]["status"], ROUTE_STATUSES)
                benchmark = record.get("benchmark_calculability")
                self.assertIsInstance(benchmark, dict)
                if not isinstance(benchmark, dict):
                    continue
                self.assertIn(
                    benchmark.get("status"),
                    {"calculable", "not_calculable"},
                )
                if benchmark.get("status") == "not_calculable":
                    self.assertTrue(str(benchmark.get("reason") or "").strip())
                self.assertIn(record["confidence"], CONFIDENCE_LEVELS)
                date.fromisoformat(record["reviewed_on"])
                self.assertIn(record["local_currency"], self.fx_rates_to_usd)

                sources_by_id = {source["id"]: source for source in record["sources"]}
                self.assertTrue(sources_by_id)
                for source in sources_by_id.values():
                    parsed_url = urlparse(source["url"])
                    self.assertEqual(parsed_url.scheme, "https")
                    self.assertTrue(parsed_url.netloc)
                    date.fromisoformat(source["source_date"])
                    date.fromisoformat(source["accessed_on"])

                for component in record["components"]:
                    self.assertTrue(component["source_ids"])
                    self.assertTrue(
                        set(component["source_ids"]).issubset(sources_by_id),
                        "every component source ID must resolve to record sources",
                    )

    def test_present_records_calculate_against_unrounded_100_m2_price(self) -> None:
        for record in self.dataset["destinations"]:
            with self.subTest(destination_id=record["destination_id"]):
                destination = self.destinations_by_id[record["destination_id"]]
                property_price_usd = destination["usd_per_m2"] * 100
                benchmark = record.get("benchmark_calculability")
                self.assertIsInstance(benchmark, dict)
                if not isinstance(benchmark, dict):
                    continue
                result = calculate_acquisition_costs(
                    record,
                    property_price_usd=property_price_usd,
                    fx_rates_to_usd=self.fx_rates_to_usd,
                )

                self.assertEqual(result["property_price_usd"], property_price_usd)
                self.assertTrue(math.isfinite(result["property_price_usd"]))
                for component in result["components"] + result["conditional_components"]:
                    amount_keys = (
                        "low_local",
                        "estimate_local",
                        "high_local",
                        "low_usd",
                        "estimate_usd",
                        "high_usd",
                    )
                    if component["calculation"] is None:
                        self.assertEqual(component["inclusion"], "conditional")
                        for key in amount_keys:
                            self.assertIsNone(component[key], key)
                        continue
                    for key in amount_keys:
                        self.assertTrue(math.isfinite(component[key]), key)
                    self.assertLessEqual(component["low_usd"], component["estimate_usd"])
                    self.assertLessEqual(component["estimate_usd"], component["high_usd"])

                if benchmark.get("status") == "not_calculable":
                    for key in (
                        "base_cost_low_usd",
                        "base_cost_estimate_usd",
                        "base_cost_high_usd",
                        "base_cost_rate",
                        "all_in_low_usd",
                        "all_in_estimate_usd",
                        "all_in_high_usd",
                        "all_in_usd_per_m2",
                    ):
                        self.assertIsNone(result[key], key)
                else:
                    for key in (
                        "base_cost_low_usd",
                        "base_cost_estimate_usd",
                        "base_cost_high_usd",
                        "base_cost_rate",
                    ):
                        self.assertTrue(math.isfinite(result[key]), key)
                    self.assertLessEqual(result["base_cost_low_usd"], result["base_cost_estimate_usd"])
                    self.assertLessEqual(result["base_cost_estimate_usd"], result["base_cost_high_usd"])

                if (
                    benchmark.get("status") == "calculable"
                    and record["purchase_route"]["status"] == "unavailable"
                ):
                    for key in (
                        "all_in_low_usd",
                        "all_in_estimate_usd",
                        "all_in_high_usd",
                        "all_in_usd_per_m2",
                    ):
                        self.assertIsNone(result[key])
                elif benchmark.get("status") == "calculable":
                    for key in (
                        "all_in_low_usd",
                        "all_in_estimate_usd",
                        "all_in_high_usd",
                        "all_in_usd_per_m2",
                    ):
                        self.assertTrue(math.isfinite(result[key]), key)
                    self.assertAlmostEqual(
                        result["all_in_low_usd"],
                        property_price_usd + result["base_cost_low_usd"],
                    )
                    self.assertAlmostEqual(
                        result["all_in_estimate_usd"],
                        property_price_usd + result["base_cost_estimate_usd"],
                    )
                    self.assertAlmostEqual(
                        result["all_in_high_usd"],
                        property_price_usd + result["base_cost_high_usd"],
                    )
                    self.assertAlmostEqual(
                        result["all_in_usd_per_m2"],
                        result["all_in_estimate_usd"] / 100,
                    )

    def test_bali_and_phuket_have_no_numeric_acquisition_result_for_route_misaligned_benchmarks(self) -> None:
        records = {
            record["destination_id"]: record
            for record in self.dataset["destinations"]
        }

        self.assertEqual(records["bali"]["purchase_route"]["status"], "unavailable")
        self.assertEqual(records["phuket-koh-samui"]["purchase_route"]["status"], "conditional")
        for destination_id in ("bali", "phuket-koh-samui"):
            with self.subTest(destination_id=destination_id):
                record = records[destination_id]
                self.assertIsInstance(record.get("benchmark_calculability"), dict)
                if not isinstance(record.get("benchmark_calculability"), dict):
                    continue
                self.assertEqual(
                    record["benchmark_calculability"]["status"],
                    "not_calculable",
                )
                self.assertTrue(record["benchmark_calculability"]["reason"].strip())
                destination = self.destinations_by_id[destination_id]
                result = calculate_acquisition_costs(
                    record,
                    destination["usd_per_m2"] * 100,
                    self.fx_rates_to_usd,
                )
                for field in (
                    "base_cost_low_usd",
                    "base_cost_estimate_usd",
                    "base_cost_high_usd",
                    "base_cost_rate",
                    "all_in_low_usd",
                    "all_in_estimate_usd",
                    "all_in_high_usd",
                    "all_in_usd_per_m2",
                ):
                    self.assertIsNone(result[field], field)

    def test_final_review_research_metadata_and_formula_corrections(self) -> None:
        records = {
            record["destination_id"]: record
            for record in self.dataset["destinations"]
        }

        for destination_id in (
            "fukuoka-itoshima",
            "hakone-izu",
            "hakuba",
            "niseko",
        ):
            with self.subTest(destination_id=destination_id, correction="Karma date"):
                karma = next(
                    source
                    for source in records[destination_id]["sources"]
                    if source["id"] == "jp-karma-costs"
                )
                self.assertEqual(karma["source_date"], "2025-06-08")

        annecy_components = {
            component["id"]: component
            for component in records["annecy"]["components"]
        }
        chamonix_components = {
            component["id"]: component
            for component in records["chamonix"]["components"]
        }
        for component_id in (
            "property-security-contribution",
            "notary-emolument",
            "sale-publication-formalities-forfait",
        ):
            with self.subTest(component_id=component_id):
                self.assertIn(component_id, annecy_components)
                if component_id not in annecy_components:
                    continue
                self.assertEqual(
                    annecy_components[component_id]["calculation"],
                    chamonix_components[component_id]["calculation"],
                )
        annecy_result = calculate_acquisition_costs(
            records["annecy"],
            self.destinations_by_id["annecy"]["usd_per_m2"] * 100,
            self.fx_rates_to_usd,
        )
        self.assertAlmostEqual(annecy_result["base_cost_estimate_usd"], 65_344.976128)

        summit = records["park-city-deer-valley"]
        deed = next(
            component
            for component in summit["components"]
            if component["id"] == "summit-county-deed-recording"
        )
        self.assertIn("third-class county", summit["jurisdiction_basis"])
        self.assertIn("third-class county", deed["notes"])
        self.assertNotIn("a second-class county", summit["jurisdiction_basis"])
        self.assertNotIn("a second-class county", deed["notes"])

    def test_benchmark_manual_components_reject_changed_local_prices(self) -> None:
        benchmark_components = (
            ("swiss-valais-vaud-alps", "representative-government-charges"),
            ("lake-tahoe", "representative-transfer-and-recording-range"),
            ("aspen-snowmass", "municipal-transfer-tax-range"),
            ("aspen-snowmass", "colorado-documentary-fee"),
        )
        records_by_id = {
            record["destination_id"]: record
            for record in self.dataset["destinations"]
        }

        for destination_id, component_id in benchmark_components:
            with self.subTest(destination_id=destination_id, component_id=component_id):
                record = deepcopy(records_by_id[destination_id])
                record["components"] = [
                    component
                    for component in record["components"]
                    if component["id"] == component_id
                ]
                destination = self.destinations_by_id[destination_id]
                property_price_usd = destination["usd_per_m2"] * 100
                local_delta_usd = 0.001 * self.fx_rates_to_usd[record["local_currency"]]

                calculate_acquisition_costs(
                    record,
                    property_price_usd=property_price_usd,
                    fx_rates_to_usd=self.fx_rates_to_usd,
                )
                with self.assertRaisesRegex(
                    AcquisitionCostDataError,
                    rf"{destination_id}.*components\[0\]\.calculation\.valid_price_local.*outside",
                ):
                    calculate_acquisition_costs(
                        record,
                        property_price_usd=property_price_usd + local_delta_usd,
                        fx_rates_to_usd=self.fx_rates_to_usd,
                    )

    def test_final_destination_parity(self) -> None:
        records = self.dataset["destinations"]
        destinations = self.destinations
        acquisition_ids = [record["destination_id"] for record in records]
        self.assertEqual(len(records), 37)
        self.assertEqual(len(set(acquisition_ids)), 37)
        self.assertTrue(ADDED_DESTINATION_IDS.issubset(acquisition_ids))
        self.assertNotIn("m-laga-costa-del-sol", acquisition_ids)
        self.assertEqual(acquisition_ids.count("malaga-costa-del-sol"), 1)
        self.assertEqual(
            set(acquisition_ids),
            {destination["id"] for destination in destinations},
        )
