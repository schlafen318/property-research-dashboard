from __future__ import annotations

from copy import deepcopy
from datetime import date
from math import isfinite
from numbers import Real
import re
from urllib.parse import urlparse


CALCULATION_TYPES = {
    "fixed", "rate", "progressive", "fixed_plus_rate",
    "range_rate", "range_fixed", "manual",
}
ESTIMATE_STRATEGIES = {"statutory", "midpoint", "lower_bound", "upper_bound", "manual"}
ROUTE_STATUSES = {"available", "conditional", "unavailable"}
BENCHMARK_CALCULABILITY_STATUSES = {"calculable", "not_calculable"}
CONFIDENCE_LEVELS = {"low", "medium", "medium-high", "high"}
SOURCE_TYPES = {"official", "registry", "statute", "accounting", "law_firm", "research"}
PRICE_BOUNDED_CALCULATION_TYPES = CALCULATION_TYPES


class AcquisitionCostDataError(ValueError):
    pass


def _error(destination_id: str, path: str, message: str) -> None:
    raise AcquisitionCostDataError(f"{destination_id}: {path} {message}")


def _require_finite_nonnegative(destination_id: str, path: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, Real) or not isfinite(value) or value < 0:
        _error(destination_id, path, "must be a finite nonnegative number")
    return float(value)


def _require_nonempty_text(destination_id: str, path: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        _error(destination_id, path, "is required")
    return value


def _require_iso_date(destination_id: str, path: str, value: object) -> str:
    text = _require_nonempty_text(destination_id, path, value)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        _error(destination_id, path, "must be an ISO date in YYYY-MM-DD format")
    try:
        date.fromisoformat(text)
    except ValueError:
        _error(destination_id, path, "must be a valid ISO date")
    return text


def _validate_source(destination_id: str, source: object, path: str) -> None:
    if not isinstance(source, dict):
        _error(destination_id, path, "must be an object")
    for key in ("id", "name", "metric_supported"):
        _require_nonempty_text(destination_id, f"{path}.{key}", source.get(key))
    for key in ("source_date", "accessed_on"):
        _require_iso_date(destination_id, f"{path}.{key}", source.get(key))
    url = _require_nonempty_text(destination_id, f"{path}.url", source.get("url"))
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        _error(destination_id, f"{path}.url", "must be an HTTPS URL")
    source_type = source.get("source_type")
    if source_type not in SOURCE_TYPES:
        _error(destination_id, f"{path}.source_type", "is unsupported")


def _validate_calculation(destination_id: str, calculation: object, path: str) -> None:
    if not isinstance(calculation, dict):
        _error(destination_id, path, "must be an object")
    calculation_type = calculation.get("type")
    if calculation_type not in CALCULATION_TYPES:
        _error(destination_id, f"{path}.type", "is unsupported")

    price_bounds = calculation.get("valid_price_local")
    if price_bounds is not None:
        bounds_path = f"{path}.valid_price_local"
        if calculation_type not in PRICE_BOUNDED_CALCULATION_TYPES:
            _error(destination_id, bounds_path, "is unsupported for this calculation type")
        if not isinstance(price_bounds, dict):
            _error(destination_id, bounds_path, "must be an object")
        exact_keys = {"exact", "tolerance"}
        range_keys = {"minimum", "minimum_inclusive", "maximum", "maximum_inclusive"}
        has_exact_form = bool(exact_keys.intersection(price_bounds))
        has_range_form = bool(range_keys.intersection(price_bounds))
        if has_exact_form and has_range_form:
            _error(destination_id, bounds_path, "exact and range forms are mutually exclusive")
        if has_exact_form:
            if calculation_type != "manual":
                _error(destination_id, bounds_path, "exact form is supported only for manual calculations")
            _require_finite_nonnegative(
                destination_id,
                f"{bounds_path}.exact",
                price_bounds.get("exact"),
            )
            tolerance = _require_finite_nonnegative(
                destination_id,
                f"{bounds_path}.tolerance",
                price_bounds.get("tolerance"),
            )
            if tolerance <= 0:
                _error(destination_id, f"{bounds_path}.tolerance", "must be positive")
        else:
            minimum = _require_finite_nonnegative(
                destination_id,
                f"{bounds_path}.minimum",
                price_bounds.get("minimum"),
            )
            maximum = _require_finite_nonnegative(
                destination_id,
                f"{bounds_path}.maximum",
                price_bounds.get("maximum"),
            )
            if minimum >= maximum:
                _error(destination_id, bounds_path, "has an inverted or empty range")
            for key in ("minimum_inclusive", "maximum_inclusive"):
                if not isinstance(price_bounds.get(key), bool):
                    _error(destination_id, f"{bounds_path}.{key}", "must be a boolean")

    if calculation_type in {"rate", "fixed_plus_rate", "progressive", "range_rate"}:
        if calculation.get("tax_base") != "purchase_price":
            _error(destination_id, f"{path}.tax_base", "must be purchase_price")

    if calculation_type == "fixed":
        _require_finite_nonnegative(destination_id, f"{path}.amount", calculation.get("amount"))
    elif calculation_type == "rate":
        _require_finite_nonnegative(destination_id, f"{path}.rate", calculation.get("rate"))
    elif calculation_type == "fixed_plus_rate":
        _require_finite_nonnegative(destination_id, f"{path}.fixed_amount", calculation.get("fixed_amount"))
        _require_finite_nonnegative(destination_id, f"{path}.rate", calculation.get("rate"))
    elif calculation_type in {"range_rate", "range_fixed"}:
        minimum_key, maximum_key = (
            ("minimum_rate", "maximum_rate")
            if calculation_type == "range_rate"
            else ("minimum_amount", "maximum_amount")
        )
        minimum = _require_finite_nonnegative(destination_id, f"{path}.{minimum_key}", calculation.get(minimum_key))
        maximum = _require_finite_nonnegative(destination_id, f"{path}.{maximum_key}", calculation.get(maximum_key))
        if minimum > maximum:
            _error(destination_id, path, "has an inverted range")
    elif calculation_type == "manual":
        low = _require_finite_nonnegative(destination_id, f"{path}.low_amount", calculation.get("low_amount"))
        estimate = _require_finite_nonnegative(destination_id, f"{path}.estimate_amount", calculation.get("estimate_amount"))
        high = _require_finite_nonnegative(destination_id, f"{path}.high_amount", calculation.get("high_amount"))
        if low > estimate or estimate > high:
            _error(destination_id, path, "has an inverted manual range")
    elif calculation_type == "progressive":
        brackets = calculation.get("brackets")
        if not isinstance(brackets, list) or not brackets:
            _error(destination_id, f"{path}.brackets", "must be a nonempty list")
        previous_up_to = 0.0
        for index, bracket in enumerate(brackets):
            bracket_path = f"{path}.brackets[{index}]"
            if not isinstance(bracket, dict):
                _error(destination_id, bracket_path, "must be an object")
            _require_finite_nonnegative(destination_id, f"{bracket_path}.rate", bracket.get("rate"))
            up_to = bracket.get("up_to")
            if up_to is None:
                if index != len(brackets) - 1:
                    _error(destination_id, bracket_path, "must be the final open-ended bracket")
                continue
            upper = _require_finite_nonnegative(destination_id, f"{bracket_path}.up_to", up_to)
            if upper <= previous_up_to:
                _error(destination_id, bracket_path, "must be ordered and non-overlapping")
            if index == len(brackets) - 1:
                _error(destination_id, f"{path}.brackets", "must end with an open-ended bracket")
            previous_up_to = upper


def _progressive_amount(brackets: list[dict], property_price_local: float) -> float:
    total = 0.0
    lower = 0.0
    for bracket in brackets:
        up_to = bracket["up_to"]
        taxable = property_price_local - lower if up_to is None else min(property_price_local, up_to) - lower
        if taxable > 0:
            total += taxable * bracket["rate"]
        if up_to is None or property_price_local <= up_to:
            break
        lower = up_to
    return total


def _component_amounts(
    component: dict,
    property_price_local: float,
    destination_id: str,
    path: str,
    *,
    enforce_price_bounds: bool = True,
) -> tuple[float | None, float | None, float | None]:
    calculation = component["calculation"]
    if calculation is None:
        return None, None, None

    price_bounds = calculation.get("valid_price_local")
    if price_bounds is not None and enforce_price_bounds:
        if "exact" in price_bounds:
            unsupported_price = abs(property_price_local - price_bounds["exact"]) > price_bounds["tolerance"]
        else:
            below_minimum = property_price_local < price_bounds["minimum"] or (
                property_price_local == price_bounds["minimum"]
                and not price_bounds["minimum_inclusive"]
            )
            above_maximum = property_price_local > price_bounds["maximum"] or (
                property_price_local == price_bounds["maximum"]
                and not price_bounds["maximum_inclusive"]
            )
            unsupported_price = below_minimum or above_maximum
        if unsupported_price:
            _error(
                destination_id,
                f"{path}.calculation.valid_price_local",
                f"property price {property_price_local:g} is outside supported local-price bounds",
            )

    calculation_type = calculation["type"]
    if calculation_type == "fixed":
        low = high = calculation["amount"]
    elif calculation_type == "rate":
        low = high = property_price_local * calculation["rate"]
    elif calculation_type == "fixed_plus_rate":
        low = high = calculation["fixed_amount"] + property_price_local * calculation["rate"]
    elif calculation_type == "progressive":
        low = high = _progressive_amount(calculation["brackets"], property_price_local)
    elif calculation_type == "range_rate":
        low = property_price_local * calculation["minimum_rate"]
        high = property_price_local * calculation["maximum_rate"]
    elif calculation_type == "range_fixed":
        low = calculation["minimum_amount"]
        high = calculation["maximum_amount"]
    else:
        low = calculation["low_amount"]
        estimate = calculation["estimate_amount"]
        high = calculation["high_amount"]

    strategy = component["estimate_strategy"]
    if strategy == "statutory":
        if low != high:
            _error(destination_id, f"{path}.estimate_strategy", "requires identical low and high amounts")
        estimate = low
    elif strategy == "midpoint":
        estimate = (low + high) / 2
    elif strategy == "lower_bound":
        estimate = low
    elif strategy == "upper_bound":
        estimate = high
    elif calculation_type != "manual":
        _error(destination_id, f"{path}.estimate_strategy", "manual is allowed only for manual calculations")
    return float(low), float(estimate), float(high)


def _validate_destination(destination: object, fx_rates_to_usd: dict[str, float]) -> str:
    if not isinstance(destination, dict):
        _error("<missing destination_id>", "destination", "must be an object")
    destination_id = destination.get("destination_id")
    if not isinstance(destination_id, str) or not destination_id.strip():
        _error("<missing destination_id>", "destination_id", "is required")
    _require_nonempty_text(destination_id, "jurisdiction_basis", destination.get("jurisdiction_basis"))
    _require_iso_date(destination_id, "reviewed_on", destination.get("reviewed_on"))
    currency = _require_nonempty_text(destination_id, "local_currency", destination.get("local_currency"))
    exchange_rate = fx_rates_to_usd.get(currency) if isinstance(fx_rates_to_usd, dict) else None
    if exchange_rate is None:
        _error(destination_id, "local_currency", "has no USD FX rate")
    _require_finite_nonnegative(destination_id, f"fx_rates_to_usd.{currency}", exchange_rate)
    if exchange_rate <= 0:
        _error(destination_id, f"fx_rates_to_usd.{currency}", "must be positive")

    route = destination.get("purchase_route")
    if not isinstance(route, dict):
        _error(destination_id, "purchase_route", "must be an object")
    status = route.get("status")
    if status not in ROUTE_STATUSES:
        _error(destination_id, "purchase_route.status", "is unsupported")
    _require_nonempty_text(destination_id, "purchase_route.label", route.get("label"))
    if status in {"conditional", "unavailable"}:
        _require_nonempty_text(destination_id, "purchase_route.notes", route.get("notes"))

    benchmark = destination.get("benchmark_calculability")
    if not isinstance(benchmark, dict):
        _error(destination_id, "benchmark_calculability", "must be an object")
    benchmark_status = benchmark.get("status")
    if benchmark_status not in BENCHMARK_CALCULABILITY_STATUSES:
        _error(destination_id, "benchmark_calculability.status", "is unsupported")
    reason = benchmark.get("reason")
    if not isinstance(reason, str):
        _error(destination_id, "benchmark_calculability.reason", "must be text")
    if benchmark_status == "not_calculable":
        _require_nonempty_text(
            destination_id,
            "benchmark_calculability.reason",
            reason,
        )

    if destination.get("confidence") not in CONFIDENCE_LEVELS:
        _error(destination_id, "confidence", "is unsupported")
    sources = destination.get("sources")
    if not isinstance(sources, list) or not sources:
        _error(destination_id, "sources", "must be a nonempty list")
    source_ids: set[str] = set()
    for index, source in enumerate(sources):
        path = f"sources[{index}]"
        _validate_source(destination_id, source, path)
        source_id = source["id"]
        if source_id in source_ids:
            _error(destination_id, f"{path}.id", "is duplicated")
        source_ids.add(source_id)

    components = destination.get("components")
    if not isinstance(components, list):
        _error(destination_id, "components", "must be a list")
    component_ids: set[str] = set()
    for index, component in enumerate(components):
        path = f"components[{index}]"
        if not isinstance(component, dict):
            _error(destination_id, path, "must be an object")
        component_id = _require_nonempty_text(destination_id, f"{path}.id", component.get("id"))
        if component_id in component_ids:
            _error(destination_id, f"{path}.id", "is duplicated")
        component_ids.add(component_id)
        _require_nonempty_text(destination_id, f"{path}.label", component.get("label"))
        _require_nonempty_text(destination_id, f"{path}.category", component.get("category"))
        inclusion = component.get("inclusion")
        if inclusion not in {"base", "conditional"}:
            _error(destination_id, f"{path}.inclusion", "is unsupported")
        if inclusion == "base" and component.get("applicability") == "conditional":
            _error(destination_id, f"{path}.applicability", "cannot be conditional for a base component")
        strategy = component.get("estimate_strategy")
        if strategy not in ESTIMATE_STRATEGIES:
            _error(destination_id, f"{path}.estimate_strategy", "is unsupported")
        if "calculation" not in component:
            _error(destination_id, f"{path}.calculation", "is required")
        calculation = component["calculation"]
        if calculation is None:
            if inclusion == "base":
                _error(destination_id, f"{path}.calculation", "cannot be null for a base component")
            if strategy == "manual":
                _error(
                    destination_id,
                    f"{path}.estimate_strategy",
                    "manual requires a manual calculation",
                )
        else:
            _validate_calculation(destination_id, calculation, f"{path}.calculation")
        if strategy == "manual" and calculation is not None and calculation["type"] != "manual":
            _error(destination_id, f"{path}.estimate_strategy", "manual is allowed only for manual calculations")
        references = component.get("source_ids")
        if not isinstance(references, list):
            _error(destination_id, f"{path}.source_ids", "must be a list")
        if not references:
            _error(destination_id, f"{path}.source_ids", "is required")
        for source_index, source_id in enumerate(references):
            source_id = _require_nonempty_text(destination_id, f"{path}.source_ids[{source_index}]", source_id)
            if source_id not in source_ids:
                _error(destination_id, f"{path}.source_ids[{source_index}]", "does not reference a source")
        _component_amounts(
            component,
            1.0,
            destination_id,
            path,
            enforce_price_bounds=False,
        )
    return destination_id


def validate_acquisition_dataset(
    dataset: dict,
    expected_destination_ids: set[str],
    fx_rates_to_usd: dict[str, float],
) -> None:
    """Raise AcquisitionCostDataError when the dataset is not build-safe."""
    if not isinstance(dataset, dict):
        raise AcquisitionCostDataError("dataset: must be an object")
    _require_iso_date("dataset", "as_of", dataset.get("as_of"))
    if dataset.get("reporting_currency") != "USD":
        _error("dataset", "reporting_currency", "must be USD")
    buyer_profile = dataset.get("buyer_profile")
    if not isinstance(buyer_profile, dict):
        _error("dataset", "buyer_profile", "must be an object")
    for field in (
        "residency",
        "buyer_type",
        "use",
        "financing",
        "property_market",
        "reliefs",
    ):
        _require_nonempty_text(
            "dataset",
            f"buyer_profile.{field}",
            buyer_profile.get(field),
        )
    if not isinstance(dataset.get("destinations"), list):
        raise AcquisitionCostDataError("dataset: destinations must be a list")
    actual_ids: set[str] = set()
    for record in dataset["destinations"]:
        destination_id = _validate_destination(record, fx_rates_to_usd)
        if destination_id in actual_ids:
            _error(destination_id, "destination_id", f"duplicate destination_id {destination_id}")
        actual_ids.add(destination_id)
    missing = expected_destination_ids - actual_ids
    if missing:
        missing_id = sorted(missing)[0]
        raise AcquisitionCostDataError(f"{missing_id}: missing destination_id {missing_id}")
    unexpected = actual_ids - expected_destination_ids
    if unexpected:
        unexpected_id = sorted(unexpected)[0]
        raise AcquisitionCostDataError(f"{unexpected_id}: unexpected destination_id {unexpected_id}")


def calculate_acquisition_costs(
    destination: dict,
    property_price_usd: float,
    fx_rates_to_usd: dict[str, float],
) -> dict:
    """Calculate buyer-side costs for the fixed 100 m² comparison archetype."""
    destination_id = _validate_destination(destination, fx_rates_to_usd)
    if isinstance(property_price_usd, bool) or not isinstance(property_price_usd, Real) or not isfinite(property_price_usd) or property_price_usd <= 0:
        _error(destination_id, "property_price_usd", "must be a finite positive number")
    currency = destination["local_currency"]
    exchange_rate = float(fx_rates_to_usd[currency])
    property_price_local = float(property_price_usd) / exchange_rate
    base_components: list[dict] = []
    conditional_components: list[dict] = []
    for index, original_component in enumerate(destination["components"]):
        component = deepcopy(original_component)
        low, estimate, high = _component_amounts(component, property_price_local, destination_id, f"components[{index}]")
        component.update({
            "low_local": low,
            "estimate_local": estimate,
            "high_local": high,
            "low_usd": None if low is None else low * exchange_rate,
            "estimate_usd": None if estimate is None else estimate * exchange_rate,
            "high_usd": None if high is None else high * exchange_rate,
        })
        if component["inclusion"] == "base":
            base_components.append(component)
        else:
            conditional_components.append(component)
    benchmark_calculable = (
        destination["benchmark_calculability"]["status"] == "calculable"
    )
    base_low = (
        sum(component["low_usd"] for component in base_components)
        if benchmark_calculable
        else None
    )
    base_estimate = (
        sum(component["estimate_usd"] for component in base_components)
        if benchmark_calculable
        else None
    )
    base_high = (
        sum(component["high_usd"] for component in base_components)
        if benchmark_calculable
        else None
    )
    unavailable = destination["purchase_route"]["status"] == "unavailable"
    result = {
        "property_price_usd": float(property_price_usd),
        "base_cost_low_usd": base_low,
        "base_cost_estimate_usd": base_estimate,
        "base_cost_high_usd": base_high,
        "base_cost_rate": (
            base_estimate / float(property_price_usd)
            if benchmark_calculable
            else None
        ),
        "all_in_low_usd": (
            None
            if unavailable or not benchmark_calculable
            else float(property_price_usd) + base_low
        ),
        "all_in_estimate_usd": (
            None
            if unavailable or not benchmark_calculable
            else float(property_price_usd) + base_estimate
        ),
        "all_in_high_usd": (
            None
            if unavailable or not benchmark_calculable
            else float(property_price_usd) + base_high
        ),
        "all_in_usd_per_m2": (
            None
            if unavailable or not benchmark_calculable
            else (float(property_price_usd) + base_estimate) / 100
        ),
        "components": base_components,
        "conditional_components": conditional_components,
        "purchase_route": deepcopy(destination["purchase_route"]),
        "benchmark_calculability": deepcopy(destination["benchmark_calculability"]),
        "confidence": destination["confidence"],
        "acquisition_cost_confidence": destination["confidence"],
        "jurisdiction_basis": destination["jurisdiction_basis"],
        "reviewed_on": destination["reviewed_on"],
    }
    return result
