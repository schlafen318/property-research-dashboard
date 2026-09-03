from __future__ import annotations

import json
import math
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

from src import build_unified_app
from src.acquisition_costs import calculate_acquisition_costs


ROOT = Path(__file__).resolve().parents[1]


class AppDataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.capture = False
        self.chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "script" and attributes.get("id") == "app-data":
            self.capture = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.capture:
            self.capture = False

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.chunks.append(data)


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def load_app_data(path: Path) -> dict:
    parser = AppDataParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return json.loads("".join(parser.chunks))


class AcquisitionCostArtifactReconciliationTests(unittest.TestCase):
    def test_all_37_records_recalculate_from_sources_and_match_a_fresh_build(self) -> None:
        source_destinations = load_json(ROOT / "data" / "destinations.json")
        acquisition_dataset = load_json(ROOT / "data" / "acquisition_costs.json")
        fx = load_json(ROOT / "data" / "fx_rates.json")
        methodology = load_json(ROOT / "data" / "property_comparison_methodology.json")
        self.assertIsInstance(source_destinations, list)
        self.assertIsInstance(acquisition_dataset, dict)
        self.assertIsInstance(fx, dict)
        self.assertIsInstance(methodology, dict)

        records = acquisition_dataset["destinations"]
        self.assertTrue(
            all("benchmark_calculability" in record for record in records),
            "every source record must declare benchmark_calculability",
        )

        checked_dashboard = ROOT / "artifacts" / "dashboard" / "index.html"
        app_data = load_app_data(checked_dashboard)
        embedded = app_data["destinations"]

        expected_ids = {item["id"] for item in source_destinations}
        acquisition_ids = {item["destination_id"] for item in records}
        embedded_ids = {item["id"] for item in embedded}
        self.assertEqual(len(embedded), 37)
        self.assertEqual(expected_ids, acquisition_ids)
        self.assertEqual(expected_ids, embedded_ids)
        self.assertEqual(app_data["acquisition_cost_methodology"], acquisition_dataset)

        with tempfile.TemporaryDirectory() as directory:
            fresh_artifacts = Path(directory) / "artifacts"
            with (
                patch.object(build_unified_app, "ARTIFACTS", fresh_artifacts),
                patch.object(
                    build_unified_app,
                    "PUBLIC_ASSETS",
                    fresh_artifacts / "assets",
                ),
            ):
                build_unified_app.build()

            fresh_files = sorted(
                path.relative_to(fresh_artifacts)
                for path in fresh_artifacts.rglob("*")
                if path.is_file()
            )
            self.assertTrue(fresh_files)
            for relative_path in fresh_files:
                with self.subTest(fresh_artifact=str(relative_path)):
                    tracked_path = ROOT / "artifacts" / relative_path
                    self.assertTrue(tracked_path.is_file(), relative_path)
                    self.assertEqual(
                        (fresh_artifacts / relative_path).read_bytes(),
                        tracked_path.read_bytes(),
                    )

        sources_by_id = {item["id"]: item for item in source_destinations}
        records_by_id = {item["destination_id"]: item for item in records}
        embedded_by_id = {item["id"]: item for item in embedded}
        fx_rates = fx["rates_to_usd"]
        area_m2 = methodology["internal_area_m2"]

        for destination_id in sorted(expected_ids):
            with self.subTest(destination=destination_id):
                source_destination = sources_by_id[destination_id]
                record = records_by_id[destination_id]
                destination = embedded_by_id[destination_id]
                property_price_usd = source_destination["usd_per_m2"] * area_m2
                recalculated = calculate_acquisition_costs(
                    record,
                    property_price_usd,
                    fx_rates,
                )

                self.assertTrue(math.isfinite(property_price_usd))
                self.assertGreater(property_price_usd, 0)
                self.assertEqual(destination["comparison_home_usd"], property_price_usd)
                self.assertEqual(destination["comparison_home_area_m2"], area_m2)
                self.assertEqual(destination["purchase_route"], record["purchase_route"])
                self.assertEqual(
                    destination["acquisition_jurisdiction_basis"],
                    record["jurisdiction_basis"],
                )
                self.assertEqual(
                    destination["acquisition_cost_reviewed_on"],
                    record["reviewed_on"],
                )
                self.assertEqual(
                    destination["acquisition_benchmark_status"],
                    record["benchmark_calculability"]["status"],
                )
                self.assertEqual(
                    destination["acquisition_benchmark_reason"],
                    record["benchmark_calculability"]["reason"],
                )
                self.assertEqual(
                    recalculated["benchmark_calculability"],
                    record["benchmark_calculability"],
                )

                mapped_fields = {
                    "base_cost_low_usd": "acquisition_cost_low_usd",
                    "base_cost_estimate_usd": "acquisition_cost_estimate_usd",
                    "base_cost_high_usd": "acquisition_cost_high_usd",
                    "base_cost_rate": "acquisition_cost_rate",
                    "all_in_low_usd": "all_in_acquisition_low_usd",
                    "all_in_estimate_usd": "all_in_acquisition_estimate_usd",
                    "all_in_high_usd": "all_in_acquisition_high_usd",
                    "all_in_usd_per_m2": "all_in_acquisition_usd_per_m2",
                }
                for result_field, embedded_field in mapped_fields.items():
                    self.assertEqual(
                        destination[embedded_field],
                        recalculated[result_field],
                        embedded_field,
                    )

                self.assertEqual(
                    destination["acquisition_components"],
                    recalculated["components"],
                )
                self.assertEqual(
                    destination["conditional_acquisition_components"],
                    recalculated["conditional_components"],
                )

                components = [
                    *recalculated["components"],
                    *recalculated["conditional_components"],
                ]
                complete = True
                source_ids = {source["id"] for source in record["sources"]}
                self.assertTrue(source_ids)
                self.assertTrue(
                    all(source["url"].startswith("https://") for source in record["sources"])
                )
                for component in components:
                    self.assertTrue(component["source_ids"])
                    self.assertLessEqual(set(component["source_ids"]), source_ids)
                    amount_fields = (
                        "low_local",
                        "estimate_local",
                        "high_local",
                        "low_usd",
                        "estimate_usd",
                        "high_usd",
                    )
                    if component["calculation"] is None:
                        complete = False
                        for field in amount_fields:
                            self.assertIsNone(component[field], field)
                    else:
                        for field in amount_fields:
                            self.assertTrue(math.isfinite(component[field]), field)
                        self.assertLessEqual(component["low_local"], component["estimate_local"])
                        self.assertLessEqual(component["estimate_local"], component["high_local"])
                        self.assertLessEqual(component["low_usd"], component["estimate_usd"])
                        self.assertLessEqual(component["estimate_usd"], component["high_usd"])

                self.assertIs(destination["acquisition_cost_complete"], complete)
                self.assertEqual(
                    destination["acquisition_cost_completeness"],
                    "complete" if complete else "known-base/incomplete",
                )

                benchmark_status = record["benchmark_calculability"]["status"]
                route_status = record["purchase_route"]["status"]
                if benchmark_status == "not_calculable":
                    for field in mapped_fields.values():
                        self.assertIsNone(destination[field], field)
                else:
                    for field in (
                        "acquisition_cost_low_usd",
                        "acquisition_cost_estimate_usd",
                        "acquisition_cost_high_usd",
                        "acquisition_cost_rate",
                    ):
                        self.assertTrue(math.isfinite(destination[field]), field)
                    self.assertLessEqual(
                        destination["acquisition_cost_low_usd"],
                        destination["acquisition_cost_estimate_usd"],
                    )
                    self.assertLessEqual(
                        destination["acquisition_cost_estimate_usd"],
                        destination["acquisition_cost_high_usd"],
                    )
                    if route_status == "unavailable":
                        for field in (
                            "all_in_acquisition_low_usd",
                            "all_in_acquisition_estimate_usd",
                            "all_in_acquisition_high_usd",
                            "all_in_acquisition_usd_per_m2",
                        ):
                            self.assertIsNone(destination[field], field)
                    else:
                        for suffix in ("low", "estimate", "high"):
                            self.assertAlmostEqual(
                                property_price_usd
                                + destination[f"acquisition_cost_{suffix}_usd"],
                                destination[f"all_in_acquisition_{suffix}_usd"],
                            )
                        self.assertLessEqual(
                            destination["all_in_acquisition_low_usd"],
                            destination["all_in_acquisition_estimate_usd"],
                        )
                        self.assertLessEqual(
                            destination["all_in_acquisition_estimate_usd"],
                            destination["all_in_acquisition_high_usd"],
                        )
                        self.assertAlmostEqual(
                            destination["all_in_acquisition_usd_per_m2"],
                            destination["all_in_acquisition_estimate_usd"] / area_m2,
                        )

        self.assertEqual(
            embedded_by_id["bali"]["purchase_route"]["status"],
            "unavailable",
        )
        self.assertEqual(
            embedded_by_id["phuket-koh-samui"]["purchase_route"]["status"],
            "conditional",
        )
        for destination_id in ("bali", "phuket-koh-samui"):
            self.assertEqual(
                embedded_by_id[destination_id]["acquisition_benchmark_status"],
                "not_calculable",
            )


if __name__ == "__main__":
    unittest.main()
