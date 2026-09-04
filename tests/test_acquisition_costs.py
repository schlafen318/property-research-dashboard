from __future__ import annotations

import copy
import unittest

from src.acquisition_costs import (
    AcquisitionCostDataError,
    calculate_acquisition_costs,
    validate_acquisition_dataset,
)


FX = {"USD": 1.0, "EUR": 1.25}


def source(source_id: str = "official-tax") -> dict:
    return {
        "id": source_id,
        "name": "Official Tax Authority",
        "url": "https://tax.example.gov/rule",
        "source_type": "official",
        "metric_supported": "Transfer tax rate",
        "source_date": "2026-01-01",
        "accessed_on": "2026-08-19",
        "notes": "Statutory schedule.",
    }


def destination(
    *components: dict,
    currency: str = "USD",
    status: str = "available",
    benchmark_status: str = "calculable",
    benchmark_reason: str = "",
) -> dict:
    return {
        "destination_id": "example",
        "local_currency": currency,
        "jurisdiction_basis": "Example jurisdiction",
        "purchase_route": {
            "status": status,
            "label": "Direct individual ownership",
            "notes": "Local eligibility verification required." if status != "available" else "",
        },
        "benchmark_calculability": {
            "status": benchmark_status,
            "reason": benchmark_reason,
        },
        "components": list(components),
        "sources": [source()],
        "confidence": "high",
        "reviewed_on": "2026-08-19",
        "review_notes": "",
    }


def dataset(*records: dict) -> dict:
    return {
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
        "destinations": list(records),
    }


def component(
    calculation: dict | None,
    *,
    inclusion: str = "base",
    estimate_strategy: str = "statutory",
    applicability: str | None = None,
    source_ids: list[str] | None = None,
) -> dict:
    record = {
        "id": "transfer_tax",
        "label": "Property transfer tax",
        "category": "tax",
        "inclusion": inclusion,
        "calculation": calculation,
        "estimate_strategy": estimate_strategy,
        "source_ids": ["official-tax"] if source_ids is None else source_ids,
        "notes": "",
    }
    if applicability is not None:
        record["applicability"] = applicability
    return record


def rate_component(rate: float = 0.05, **kwargs: object) -> dict:
    return component({"type": "rate", "tax_base": "purchase_price", "rate": rate}, **kwargs)


class AcquisitionCostCalculationTests(unittest.TestCase):
    def calculate(self, record: dict, price: float = 200_000) -> dict:
        return calculate_acquisition_costs(record, price, FX)

    def assert_component_amounts(self, result: dict, low: float, estimate: float, high: float) -> None:
        calculated = result["components"][0]
        self.assertAlmostEqual(calculated["low_usd"], low)
        self.assertAlmostEqual(calculated["estimate_usd"], estimate)
        self.assertAlmostEqual(calculated["high_usd"], high)

    def assert_reconciled(self, result: dict) -> None:
        self.assertAlmostEqual(result["all_in_low_usd"], result["property_price_usd"] + result["base_cost_low_usd"])
        self.assertAlmostEqual(result["all_in_estimate_usd"], result["property_price_usd"] + result["base_cost_estimate_usd"])
        self.assertAlmostEqual(result["all_in_high_usd"], result["property_price_usd"] + result["base_cost_high_usd"])
        self.assertAlmostEqual(result["base_cost_rate"], result["base_cost_estimate_usd"] / result["property_price_usd"])
        self.assertAlmostEqual(result["all_in_usd_per_m2"], result["all_in_estimate_usd"] / 100)

    def test_rate_calculates_a_single_statutory_amount(self) -> None:
        result = self.calculate(destination(rate_component()))
        self.assert_component_amounts(result, 10_000, 10_000, 10_000)
        self.assert_reconciled(result)

    def test_fixed_calculates_a_single_statutory_amount(self) -> None:
        result = self.calculate(destination(component({"type": "fixed", "amount": 800})))
        self.assert_component_amounts(result, 800, 800, 800)

    def test_fixed_plus_rate_calculates_both_parts(self) -> None:
        result = self.calculate(destination(component({"type": "fixed_plus_rate", "tax_base": "purchase_price", "fixed_amount": 500, "rate": 0.01})))
        self.assert_component_amounts(result, 2_500, 2_500, 2_500)

    def test_range_rate_uses_midpoint_for_its_estimate(self) -> None:
        result = self.calculate(destination(component({"type": "range_rate", "tax_base": "purchase_price", "minimum_rate": 0.01, "maximum_rate": 0.03}, estimate_strategy="midpoint")))
        self.assert_component_amounts(result, 2_000, 4_000, 6_000)

    def test_range_fixed_uses_midpoint_for_its_estimate(self) -> None:
        result = self.calculate(destination(component({"type": "range_fixed", "minimum_amount": 400, "maximum_amount": 800}, estimate_strategy="midpoint")))
        self.assert_component_amounts(result, 400, 600, 800)

    def test_lower_and_upper_bound_strategies_select_the_exact_declared_bound(self) -> None:
        calculation = {
            "type": "range_fixed",
            "minimum_amount": 400,
            "maximum_amount": 800,
        }
        lower = self.calculate(
            destination(
                component(calculation, estimate_strategy="lower_bound")
            )
        )
        upper = self.calculate(
            destination(
                component(calculation, estimate_strategy="upper_bound")
            )
        )

        self.assertEqual(lower["components"][0]["estimate_usd"], 400)
        self.assertEqual(lower["base_cost_estimate_usd"], 400)
        self.assertEqual(upper["components"][0]["estimate_usd"], 800)
        self.assertEqual(upper["base_cost_estimate_usd"], 800)

    def test_manual_preserves_sourced_range(self) -> None:
        result = self.calculate(destination(component({"type": "manual", "low_amount": 900, "estimate_amount": 1_000, "high_amount": 1_300}, estimate_strategy="manual")))
        self.assert_component_amounts(result, 900, 1_000, 1_300)

    def test_progressive_brackets_tax_slices_at_and_around_boundary(self) -> None:
        progressive = component({"type": "progressive", "tax_base": "purchase_price", "brackets": [{"up_to": 100_000, "rate": 0.05}, {"up_to": None, "rate": 0.08}]})
        for price, expected in ((99_999, 4_999.95), (100_000, 5_000), (150_000, 9_000)):
            with self.subTest(price=price):
                result = self.calculate(destination(progressive), price)
                self.assert_component_amounts(result, expected, expected, expected)

    def test_eur_converts_before_local_calculation_and_back_without_rounding(self) -> None:
        progressive = component({"type": "progressive", "tax_base": "purchase_price", "brackets": [{"up_to": 100_000, "rate": 0.05}, {"up_to": None, "rate": 0.08}]})
        fixed = component({"type": "fixed", "amount": 1_000})
        fixed["id"] = "registration"
        result = self.calculate(destination(progressive, fixed, currency="EUR"), 250_000)
        self.assertEqual(result["components"][0]["estimate_local"], 13_000)
        self.assertEqual(result["components"][1]["estimate_local"], 1_000)
        self.assertEqual(result["base_cost_estimate_usd"], 17_500)

    def test_base_components_enter_totals_but_conditional_components_do_not(self) -> None:
        base = rate_component(0.02)
        base["label"] = "Universal foreign buyer surcharge"
        conditional = rate_component(0.03, inclusion="conditional", applicability="conditional")
        conditional["id"] = "nationality_surcharge"
        conditional["label"] = "Nationality-dependent surcharge"
        result = self.calculate(destination(base, conditional))
        self.assertEqual(result["base_cost_estimate_usd"], 4_000)
        self.assertEqual(len(result["conditional_components"]), 1)
        self.assertEqual(result["conditional_components"][0]["estimate_usd"], 6_000)
        self.assert_reconciled(result)

    def test_unknown_conditional_amounts_remain_null_and_do_not_enter_base_totals(self) -> None:
        base = rate_component(0.02)
        unknown = component(
            None,
            inclusion="conditional",
            applicability="Only when the selected asset requires an assessed-value tax.",
        )
        unknown["id"] = "assessed_value_tax"

        result = self.calculate(destination(base, unknown))

        self.assertEqual(result["base_cost_estimate_usd"], 4_000)
        calculated = result["conditional_components"][0]
        for key in (
            "low_local",
            "estimate_local",
            "high_local",
            "low_usd",
            "estimate_usd",
            "high_usd",
        ):
            self.assertIsNone(calculated[key], key)
        self.assert_reconciled(result)

    def test_price_bounds_allow_only_the_declared_local_bracket(self) -> None:
        calculation_types = (
            ({"type": "fixed", "amount": 800}, "statutory"),
            (
                {
                    "type": "rate",
                    "tax_base": "purchase_price",
                    "rate": 0.01,
                },
                "statutory",
            ),
            (
                {
                    "type": "progressive",
                    "tax_base": "purchase_price",
                    "brackets": [
                        {"up_to": 100_000, "rate": 0.01},
                        {"up_to": None, "rate": 0.02},
                    ],
                },
                "statutory",
            ),
            (
                {
                    "type": "fixed_plus_rate",
                    "tax_base": "purchase_price",
                    "fixed_amount": 500,
                    "rate": 0.01,
                },
                "statutory",
            ),
            (
                {
                    "type": "range_rate",
                    "tax_base": "purchase_price",
                    "minimum_rate": 0.01,
                    "maximum_rate": 0.02,
                },
                "midpoint",
            ),
            (
                {
                    "type": "range_fixed",
                    "minimum_amount": 700,
                    "maximum_amount": 900,
                },
                "midpoint",
            ),
            (
                {
                    "type": "manual",
                    "low_amount": 700,
                    "estimate_amount": 800,
                    "high_amount": 900,
                },
                "manual",
            ),
        )
        bounds = {
            "minimum": 100_000,
            "minimum_inclusive": False,
            "maximum": 200_000,
            "maximum_inclusive": True,
        }

        for calculation, strategy in calculation_types:
            bounded = copy.deepcopy(calculation)
            bounded["valid_price_local"] = bounds
            record = destination(component(bounded, estimate_strategy=strategy))
            with self.subTest(calculation_type=calculation["type"], price="inside"):
                self.calculate(record, 150_000)
            with self.subTest(calculation_type=calculation["type"], price="maximum"):
                self.calculate(record, 200_000)
            for price in (100_000, 200_001):
                with self.subTest(calculation_type=calculation["type"], price=price):
                    with self.assertRaisesRegex(
                        AcquisitionCostDataError,
                        r"example.*components\[0\]\.calculation\.valid_price_local.*outside",
                    ):
                        self.calculate(record, price)

    def test_manual_exact_price_guard_accepts_only_prices_within_documented_tolerance(self) -> None:
        calculation = {
            "type": "manual",
            "low_amount": 700,
            "estimate_amount": 800,
            "high_amount": 900,
            "valid_price_local": {
                "exact": 200_000,
                "tolerance": 0.000001,
            },
        }
        record = destination(component(calculation, estimate_strategy="manual"))

        self.calculate(record, 200_000)
        self.calculate(record, 200_000.0000005)

        with self.assertRaisesRegex(
            AcquisitionCostDataError,
            r"example.*components\[0\]\.calculation\.valid_price_local.*outside",
        ):
            self.calculate(record, 200_000.000002)

    def test_unavailable_route_keeps_research_but_omits_all_in_totals(self) -> None:
        record = destination(rate_component(), status="unavailable")
        result = self.calculate(record)
        self.assertIsNone(result["all_in_low_usd"])
        self.assertIsNone(result["all_in_estimate_usd"])
        self.assertIsNone(result["all_in_high_usd"])
        self.assertIsNone(result["all_in_usd_per_m2"])
        self.assertEqual(result["components"][0]["estimate_usd"], 10_000)
        self.assertEqual(result["purchase_route"]["notes"], "Local eligibility verification required.")

    def test_uncalculable_benchmark_never_turns_an_empty_base_into_zero(self) -> None:
        reason = "The market benchmark does not represent an asset eligible for this route."
        record = destination(
            status="conditional",
            benchmark_status="not_calculable",
            benchmark_reason=reason,
        )

        result = self.calculate(record)

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
        self.assertEqual(result["purchase_route"]["status"], "conditional")
        self.assertEqual(
            result["benchmark_calculability"],
            {"status": "not_calculable", "reason": reason},
        )

    def test_calculation_does_not_mutate_source_record(self) -> None:
        record = destination(rate_component())
        original = copy.deepcopy(record)
        self.calculate(record)
        self.assertEqual(record, original)


class AcquisitionCostValidationTests(unittest.TestCase):
    def assert_invalid(self, record: dict, path: str, *, expected_ids: set[str] | None = None, fx: dict = FX) -> None:
        acquisition_dataset = dataset(record)
        with self.assertRaisesRegex(AcquisitionCostDataError, rf"example.*{path}"):
            validate_acquisition_dataset(acquisition_dataset, {"example"} if expected_ids is None else expected_ids, fx)

    def test_rejects_missing_and_duplicate_destination_records(self) -> None:
        with self.assertRaisesRegex(AcquisitionCostDataError, "missing destination_id example"):
            validate_acquisition_dataset(dataset(), {"example"}, FX)
        record = destination(rate_component())
        with self.assertRaisesRegex(AcquisitionCostDataError, "duplicate destination_id example"):
            validate_acquisition_dataset(dataset(record, copy.deepcopy(record)), {"example"}, FX)

    def test_rejects_base_component_without_source(self) -> None:
        self.assert_invalid(destination(component({"type": "fixed", "amount": 1}, source_ids=[])), "components\\[0\\]\\.source_ids")

    def test_rejects_null_calculation_for_base_component(self) -> None:
        record = destination(component(None))
        with self.assertRaisesRegex(
            AcquisitionCostDataError,
            r"example: components\[0\]\.calculation cannot be null for a base component",
        ):
            validate_acquisition_dataset(
                dataset(record),
                expected_destination_ids={"example"},
                fx_rates_to_usd=FX,
            )

    def test_rejects_missing_calculation_even_for_conditional_component(self) -> None:
        unknown = component(
            None,
            inclusion="conditional",
            applicability="Only when the selected asset requires it.",
        )
        unknown.pop("calculation")
        self.assert_invalid(
            destination(unknown),
            r"components\[0\]\.calculation.*is required",
        )

    def test_rejects_invalid_local_price_bounds(self) -> None:
        cases = (
            (
                {"minimum": 100_000, "minimum_inclusive": True},
                r"maximum",
            ),
            (
                {
                    "minimum": 200_000,
                    "minimum_inclusive": True,
                    "maximum": 100_000,
                    "maximum_inclusive": True,
                },
                r"inverted",
            ),
            (
                {
                    "minimum": 100_000,
                    "minimum_inclusive": "yes",
                    "maximum": 200_000,
                    "maximum_inclusive": True,
                },
                r"minimum_inclusive",
            ),
        )
        for bounds, path in cases:
            with self.subTest(bounds=bounds):
                calculation = {
                    "type": "fixed",
                    "amount": 800,
                    "valid_price_local": bounds,
                }
                self.assert_invalid(
                    destination(component(calculation)),
                    rf"components\[0\]\.calculation\.valid_price_local.*{path}",
                )

    def test_rejects_mixed_or_incomplete_exact_price_guards(self) -> None:
        cases = (
            (
                {
                    "exact": 200_000,
                    "tolerance": 0.000001,
                    "minimum": 199_999,
                    "minimum_inclusive": True,
                    "maximum": 200_001,
                    "maximum_inclusive": True,
                },
                r"mutually exclusive",
            ),
            ({"exact": 200_000}, r"tolerance"),
            ({"tolerance": 0.000001}, r"exact"),
        )
        for bounds, path in cases:
            with self.subTest(bounds=bounds):
                calculation = {
                    "type": "manual",
                    "low_amount": 700,
                    "estimate_amount": 800,
                    "high_amount": 900,
                    "valid_price_local": bounds,
                }
                self.assert_invalid(
                    destination(component(calculation, estimate_strategy="manual")),
                    rf"components\[0\]\.calculation\.valid_price_local.*{path}",
                )

    def test_rejects_exact_price_guard_for_nonmanual_calculation(self) -> None:
        calculation = {
            "type": "rate",
            "tax_base": "purchase_price",
            "rate": 0.01,
            "valid_price_local": {
                "exact": 200_000,
                "tolerance": 0.000001,
            },
        }
        self.assert_invalid(
            destination(component(calculation)),
            r"components\[0\]\.calculation\.valid_price_local.*manual",
        )

    def test_rejects_missing_source_reference(self) -> None:
        self.assert_invalid(destination(component({"type": "fixed", "amount": 1}, source_ids=["missing"])), "components\\[0\\]\\.source_ids\\[0\\]")

    def test_rejects_unsourced_conditional_component(self) -> None:
        conditional = component(
            {"type": "fixed", "amount": 1},
            inclusion="conditional",
            applicability="Only when selected.",
            source_ids=[],
        )
        self.assert_invalid(
            destination(conditional),
            r"components\[0\]\.source_ids",
        )

    def test_rejects_empty_destination_source_list(self) -> None:
        record = destination()
        record["sources"] = []
        self.assert_invalid(record, r"sources")

    def test_rejects_nonstring_source_reference_with_a_data_error(self) -> None:
        self.assert_invalid(destination(component({"type": "fixed", "amount": 1}, source_ids=[{}])), "components\\[0\\]\\.source_ids\\[0\\]")

    def test_rejects_non_https_source_url(self) -> None:
        record = destination(rate_component())
        record["sources"][0]["url"] = "http://tax.example.gov/rule"
        self.assert_invalid(record, "sources\\[0\\]\\.url")

    def test_rejects_unsupported_calculation_type(self) -> None:
        self.assert_invalid(destination(component({"type": "formula"})), "components\\[0\\]\\.calculation.type")

    def test_rejects_negative_amount_or_rate(self) -> None:
        self.assert_invalid(destination(component({"type": "fixed", "amount": -1})), "components\\[0\\]\\.calculation.amount")
        self.assert_invalid(destination(rate_component(-0.01)), "components\\[0\\]\\.calculation.rate")

    def test_rejects_inverted_ranges(self) -> None:
        self.assert_invalid(destination(component({"type": "range_rate", "tax_base": "purchase_price", "minimum_rate": 0.03, "maximum_rate": 0.01}, estimate_strategy="midpoint")), "components\\[0\\]\\.calculation")
        self.assert_invalid(destination(component({"type": "range_fixed", "minimum_amount": 800, "maximum_amount": 400}, estimate_strategy="midpoint")), "components\\[0\\]\\.calculation")

    def test_rejects_statutory_strategy_for_a_nonidentical_range(self) -> None:
        record = destination(component({"type": "range_rate", "tax_base": "purchase_price", "minimum_rate": 0.01, "maximum_rate": 0.03}))
        self.assert_invalid(record, "components\\[0\\]\\.estimate_strategy")

    def test_rejects_invalid_progressive_brackets(self) -> None:
        cases = (
            ([], "brackets"),
            ([{"up_to": 200_000, "rate": 0.05}, {"up_to": 100_000, "rate": 0.08}, {"up_to": None, "rate": 0.1}], "brackets\\[1\\]"),
            ([{"up_to": 100_000, "rate": 0.05}, {"up_to": 100_000, "rate": 0.08}, {"up_to": None, "rate": 0.1}], "brackets\\[1\\]"),
            ([{"up_to": 100_000, "rate": 0.05}], "brackets"),
        )
        for brackets, path in cases:
            with self.subTest(brackets=brackets):
                self.assert_invalid(destination(component({"type": "progressive", "tax_base": "purchase_price", "brackets": brackets})), f"components\\[0\\]\\.calculation.{path}")

    def test_rejects_missing_local_currency_fx_rate(self) -> None:
        self.assert_invalid(destination(rate_component(), currency="EUR"), "local_currency", fx={"USD": 1.0})

    def test_rejects_buyer_specific_base_component(self) -> None:
        self.assert_invalid(destination(rate_component(applicability="conditional")), "components\\[0\\]\\.applicability")

    def test_rejects_conditional_or_unavailable_route_without_notes(self) -> None:
        for status in ("conditional", "unavailable"):
            with self.subTest(status=status):
                record = destination(rate_component(), status=status)
                record["purchase_route"]["notes"] = ""
                self.assert_invalid(record, "purchase_route.notes")

    def test_rejects_invalid_benchmark_calculability(self) -> None:
        cases = (
            (lambda record: record.pop("benchmark_calculability"), "benchmark_calculability"),
            (
                lambda record: record["benchmark_calculability"].pop("reason"),
                "benchmark_calculability.reason",
            ),
            (
                lambda record: record["benchmark_calculability"].update(status="unknown"),
                "benchmark_calculability.status",
            ),
            (
                lambda record: record["benchmark_calculability"].update(
                    status="not_calculable",
                    reason="",
                ),
                "benchmark_calculability.reason",
            ),
        )
        for mutate, path in cases:
            with self.subTest(path=path):
                record = destination(rate_component())
                mutate(record)
                self.assert_invalid(record, path)

    def test_rejects_manual_strategy_with_null_calculation(self) -> None:
        conditional = component(
            None,
            inclusion="conditional",
            estimate_strategy="manual",
            applicability="Only when selected.",
        )
        self.assert_invalid(
            destination(conditional),
            r"components\[0\]\.estimate_strategy",
        )

    def test_rejects_unsupported_enumerations(self) -> None:
        cases = (
            (lambda record: record["purchase_route"].update(status="blocked"), "purchase_route.status"),
            (lambda record: record.update(confidence="certain"), "confidence"),
            (lambda record: record["components"][0].update(inclusion="optional"), "components\\[0\\]\\.inclusion"),
            (lambda record: record["components"][0].update(estimate_strategy="average"), "components\\[0\\]\\.estimate_strategy"),
            (lambda record: record["components"][0]["calculation"].update(tax_base="market_value"), "components\\[0\\]\\.calculation.tax_base"),
            (lambda record: record["sources"][0].update(source_type="blog"), "sources\\[0\\]\\.source_type"),
        )
        for mutate, path in cases:
            with self.subTest(path=path):
                record = destination(rate_component())
                mutate(record)
                self.assert_invalid(record, path)

    def test_rejects_nonpositive_property_price(self) -> None:
        for price in (0, -1):
            with self.subTest(price=price):
                with self.assertRaisesRegex(AcquisitionCostDataError, "example.*property_price_usd"):
                    calculate_acquisition_costs(destination(rate_component()), price, FX)

    def test_rejects_required_metadata_gaps(self) -> None:
        cases = (
            (lambda record: record.pop("jurisdiction_basis"), "jurisdiction_basis"),
            (lambda record: record.pop("reviewed_on"), "reviewed_on"),
            (lambda record: record["sources"][0].pop("source_date"), "sources\\[0\\]\\.source_date"),
            (lambda record: record["sources"][0].pop("accessed_on"), "sources\\[0\\]\\.accessed_on"),
            (lambda record: record["sources"][0].pop("metric_supported"), "sources\\[0\\]\\.metric_supported"),
        )
        for mutate, path in cases:
            with self.subTest(path=path):
                record = destination(rate_component())
                mutate(record)
                self.assert_invalid(record, path)

    def test_rejects_non_iso_record_and_source_dates(self) -> None:
        cases = (
            (lambda record: record.update(reviewed_on="19/08/2026"), "reviewed_on"),
            (
                lambda record: record["sources"][0].update(source_date="2026-02-30"),
                r"sources\[0\]\.source_date",
            ),
            (
                lambda record: record["sources"][0].update(accessed_on="20260819"),
                r"sources\[0\]\.accessed_on",
            ),
        )
        for mutate, path in cases:
            with self.subTest(path=path):
                record = destination(rate_component())
                mutate(record)
                self.assert_invalid(record, path)

    def test_rejects_invalid_top_level_metadata(self) -> None:
        cases = (
            (lambda value: value.pop("as_of"), "as_of"),
            (lambda value: value.update(as_of="2026-13-01"), "as_of"),
            (lambda value: value.pop("reporting_currency"), "reporting_currency"),
            (lambda value: value.update(reporting_currency="EUR"), "reporting_currency"),
            (lambda value: value.pop("buyer_profile"), "buyer_profile"),
            (lambda value: value.update(buyer_profile=[]), "buyer_profile"),
            (
                lambda value: value["buyer_profile"].update(financing=""),
                "buyer_profile.financing",
            ),
        )
        for mutate, path in cases:
            with self.subTest(path=path):
                acquisition_dataset = dataset(destination(rate_component()))
                mutate(acquisition_dataset)
                with self.assertRaisesRegex(
                    AcquisitionCostDataError,
                    rf"dataset.*{path}",
                ):
                    validate_acquisition_dataset(
                        acquisition_dataset,
                        {"example"},
                        FX,
                    )


if __name__ == "__main__":
    unittest.main()
