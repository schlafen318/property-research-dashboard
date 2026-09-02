from __future__ import annotations

import json
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIRE_ABROAD_PATH = ROOT / "data" / "fire_abroad.json"

FIRE_WEIGHTS = {
    "active_life": 0.25,
    "sustainable_annual_cost": 0.20,
    "healthcare_bridge": 0.15,
    "stay_flexibility": 0.10,
    "tax_compatibility": 0.10,
    "global_access": 0.08,
    "community_fit": 0.07,
    "property_exit_flexibility": 0.05,
}
ACTIVE_LIFE_WEIGHTS = {
    "everyday_movement": 0.30,
    "active_pursuits": 0.30,
    "year_round_continuity": 0.25,
    "activity_ecosystem": 0.15,
}
VALID_STAY_MODES = frozenset({"seasonal", "part_year", "full_relocation"})
VALID_ELIGIBILITY = frozenset(
    {"eligible", "conditional", "needs_verification", "not_eligible"}
)
VALID_WORK_PERMISSIONS = frozenset(
    {"passive_only", "remote_permitted", "local_permitted", "unclear"}
)
VALID_CONFIDENCE = frozenset({"low", "medium", "medium_high", "high"})
VALID_ACTIVITY_TAGS = frozenset(
    {"walking", "cycling", "hiking", "water", "winter_sports", "fitness_social"}
)
VALID_TAX_READINESS = frozenset(
    {"straightforward", "moderate", "complex", "highly_profile_dependent"}
)
CANONICAL_LAUNCH_IDS = frozenset(
    {
        "algarve-cascais",
        "bali",
        "croatia-istria-dalmatia",
        "crete",
        "da-nang-hoi-an",
        "fukuoka-itoshima",
        "madeira",
        "malaga-costa-del-sol",
        "phuket-koh-samui",
        "valencia",
    }
)

_UNRANKED_STATUSES = frozenset({"needs_verification", "not_eligible"})

PROFILE_DEFAULTS = {
    "stay_mode": "part_year",
    "age": 50,
    "household": "single",
    "housing": "rent",
    "mobility_rights": "prefer_not_to_say",
    "home_tax_context": "prefer_not_to_say",
    "annual_days": None,
    "income_type": "prefer_not_to_say",
    "activity_priority": "balanced",
}
PROFILE_ALLOWLISTS = {
    "stay_mode": VALID_STAY_MODES,
    "household": frozenset({"single", "couple"}),
    "housing": frozenset({"rent", "own", "buy_now", "buy_retirement"}),
    "mobility_rights": frozenset(
        {"local_free_movement", "general_nonlocal", "prefer_not_to_say"}
    ),
    "home_tax_context": frozenset({"us_person", "other", "prefer_not_to_say"}),
    "income_type": frozenset(
        {"portfolio", "pension", "property", "business_consulting", "mixed", "prefer_not_to_say"}
    ),
    "activity_priority": frozenset(
        {"balanced", "walking", "cycling", "hiking", "water", "winter_sports", "fitness_social"}
    ),
}
COST_SCORE_ANCHORS = {
    "single": {"five": 30_000, "zero": 90_000},
    "couple": {"five": 45_000, "zero": 135_000},
}
REQUIRED_RETIREMENT_CATEGORIES = frozenset(
    {
        "food_household",
        "utilities_communications",
        "private_healthcare",
        "transport",
        "dining_leisure",
        "travel",
        "visa_admin",
        "contingency",
    }
)
_CONFIDENCE_PRIORITY = {"low": 0, "medium": 1, "medium_high": 2, "high": 3}

_REVIEW_POLICY_KEYS = frozenset(
    {
        "immigration_days",
        "tax_days",
        "healthcare_days",
        "financial_infrastructure_days",
        "active_life_days",
    }
)
_SOURCE_FIELDS = (
    "id",
    "metric_supported",
    "url",
    "publisher",
    "source_date",
    "accessed_date",
    "jurisdiction_level",
    "notes",
)
_TAX_CATEGORY_FLAGS = (
    "pensions",
    "dividends",
    "capital_gains",
    "property_income",
    "wealth",
    "inheritance",
)
_HEALTHCARE_SUMMARIES = (
    "waiting_period_summary",
    "age_limit_summary",
    "pre_existing_condition_summary",
    "evacuation_summary",
)


def load_fire_abroad(path: Path = FIRE_ABROAD_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_fire_profile(raw: dict) -> dict:
    """Return the fixed, safe FIRE Abroad profile contract for a user input."""

    raw = raw if isinstance(raw, dict) else {}
    normalized = dict(PROFILE_DEFAULTS)
    for key, allowed in PROFILE_ALLOWLISTS.items():
        value = raw.get(key)
        if isinstance(value, str) and value in allowed:
            normalized[key] = value

    age = raw.get("age")
    if isinstance(age, (int, float)) and not isinstance(age, bool):
        normalized["age"] = max(18, min(100, int(age)))

    annual_days = raw.get("annual_days")
    if isinstance(annual_days, int) and not isinstance(annual_days, bool) and 1 <= annual_days <= 366:
        normalized["annual_days"] = annual_days
    return normalized


def _round_half_up(value: float) -> float:
    """Round a finite score or amount to two decimals in both runtimes."""

    return float(
        Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    )


def _finite_nonnegative(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and value >= 0
    )


def _work_permission_label(value: object) -> str:
    return {
        "passive_only": "Passive income only",
        "remote_permitted": "Remote work permitted",
        "local_permitted": "Local work permitted",
        "unclear": "Work permission needs professional review",
    }.get(str(value), "Work permission needs professional review")


def _eligibility_label(value: object) -> str:
    return {
        "eligible": "Eligible",
        "conditional": "Conditional",
        "needs_verification": "Needs verification",
        "not_eligible": "Not currently eligible",
    }.get(str(value), "Needs verification")


def eligibility_for_mode(country: dict, profile: dict) -> dict:
    """Evaluate the selected stay route without guessing nationality-specific rights."""

    mode = profile["stay_mode"]
    routes = country.get("stay_routes", {}) if isinstance(country, dict) else {}
    route = routes.get(mode) if isinstance(routes, dict) else None
    if not isinstance(route, dict):
        return {
            "status": "needs_verification",
            "reason": "No documented route is available for this stay mode.",
            "work_permission": "unclear",
            "stay_score": None,
            "max_days": None,
            "confidence": "low",
            "last_reviewed": None,
            "source_ids": [],
            "day_warning": None,
        }

    rights = route.get("mobility_rights")
    selected = rights.get(profile["mobility_rights"]) if isinstance(rights, dict) else None
    if not isinstance(selected, dict):
        return {
            "status": "needs_verification",
            "reason": "Nationality-dependent mobility rights must be confirmed.",
            "work_permission": "unclear",
            "stay_score": None,
            "max_days": None,
            "confidence": route.get("confidence", "low"),
            "last_reviewed": route.get("last_reviewed"),
            "source_ids": [],
            "day_warning": None,
        }
    status = selected.get("status")
    base_score = selected.get("base_score")
    max_days = selected.get("max_days")
    summary = selected.get("summary")
    summary = (
        summary
        if isinstance(summary, str) and summary
        else "Mobility-rights-specific route conditions require confirmation."
    )
    source_ids = selected.get("source_ids")
    source_ids = (
        list(source_ids)
        if isinstance(source_ids, list)
        and all(isinstance(item, str) and item for item in source_ids)
        else []
    )
    selected_work_permission = selected.get("work_permission")
    work_permission = (
        selected_work_permission
        if selected_work_permission in VALID_WORK_PERMISSIONS
        else "unclear"
    )

    minimum_age = selected.get("minimum_age")
    if (
        isinstance(minimum_age, int)
        and not isinstance(minimum_age, bool)
        and profile["age"] < minimum_age
    ):
        return {
            "status": "not_eligible",
            "reason": f"This route requires an age of at least {minimum_age}.",
            "work_permission": work_permission,
            "stay_score": 0.0,
            "max_days": max_days,
            "confidence": selected.get("confidence", "low"),
            "last_reviewed": selected.get("last_reviewed"),
            "source_ids": source_ids,
            "day_warning": None,
        }

    annual_days = profile.get("annual_days")
    day_warning = None
    if (
        isinstance(annual_days, int)
        and isinstance(max_days, int)
        and annual_days > max_days
    ):
        day_warning = (
            f"The approximate {annual_days}-day annual total exceeds this route's documented "
            f"{max_days}-day stay limit. The annual total alone cannot determine compliance "
            "with a per-stay or rolling-window rule; confirm the intended travel pattern."
        )

    if status not in VALID_ELIGIBILITY:
        status = "needs_verification"
    if (
        status in _UNRANKED_STATUSES
        or not isinstance(base_score, (int, float))
        or isinstance(base_score, bool)
        or not math.isfinite(float(base_score))
    ):
        score = None
    else:
        score = float(base_score)
        if profile["income_type"] == "business_consulting":
            if work_permission == "passive_only":
                score -= 0.5
            elif work_permission == "unclear":
                score -= 1.0
        score = _round_half_up(max(0.0, min(5.0, score)))
    return {
        "status": status,
        "reason": summary,
        "work_permission": work_permission,
        "stay_score": score,
        "max_days": max_days,
        "confidence": selected.get("confidence", "low"),
        "last_reviewed": selected.get("last_reviewed"),
        "source_ids": source_ids,
        "day_warning": day_warning,
    }


def annual_cost_score(annual_total_usd: float, household: str) -> float:
    anchors = COST_SCORE_ANCHORS[household]
    total = Decimal(str(annual_total_usd))
    five = Decimal(str(anchors["five"]))
    zero = Decimal(str(anchors["zero"]))
    score = Decimal("5") * (Decimal("1") - ((total - five) / (zero - five)))
    return _round_half_up(max(Decimal("0"), min(Decimal("5"), score)))


def build_resilience_budget(
    cost: dict, profile: dict, destination_override: dict | None = None
) -> dict:
    """Build an annual screening budget without mixing recurring and one-time costs."""

    cost = cost if isinstance(cost, dict) else {}
    usable = _has_usable_cost(cost, profile)
    profiles = cost.get("profiles", {})
    household_cost = profiles.get(profile["household"], {}) if isinstance(profiles, dict) else {}
    raw_categories = household_cost.get("categories_usd", {}) if isinstance(household_cost, dict) else {}
    categories = {
        key: value
        for key, value in raw_categories.items()
        if key in REQUIRED_RETIREMENT_CATEGORIES and _finite_nonnegative(value)
    } if usable and isinstance(raw_categories, dict) else {}

    housing = profile["housing"]
    if housing in {"rent", "buy_retirement"}:
        housing_cost = household_cost.get("annual_rent_usd")
        housing_key = "rent"
    else:
        housing_cost = household_cost.get("annual_owner_costs_usd")
        housing_key = "owner_costs"
    if usable and _finite_nonnegative(housing_cost):
        categories[housing_key] = housing_cost

    property_record = cost.get("property", {}) if isinstance(cost.get("property"), dict) else {}
    property_capital: float | int | None = 0
    if housing in {"buy_now", "buy_retirement"}:
        price = property_record.get("representative_price_usd")
        rate = property_record.get("acquisition_cost_rate")
        property_capital = (
            _round_half_up(
                Decimal(str(price)) * (Decimal("1") + Decimal(str(rate)))
            )
            if usable
            and _finite_nonnegative(price)
            and price > 0
            and _finite_nonnegative(rate)
            else None
        )

    if usable:
        recurring_without_contingency = sum(
            (Decimal(str(value)) for key, value in categories.items() if key != "contingency"),
            Decimal("0"),
        )
        currency_inflation_buffer = int(
            (recurring_without_contingency * Decimal("0.10")).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        )
        annual_total = _round_half_up(
            sum((Decimal(str(value)) for value in categories.values()), Decimal("0"))
            + Decimal(currency_inflation_buffer)
        )
    else:
        currency_inflation_buffer = None
        annual_total = None
    override = destination_override if isinstance(destination_override, dict) else {}
    relocation = override.get("one_time_relocation_usd", 0)
    if not _finite_nonnegative(relocation):
        relocation = 0
    return {
        "annual_total_usd": annual_total,
        "categories": categories,
        "currency_inflation_buffer": currency_inflation_buffer,
        "property_capital_usd": property_capital,
        "one_time_relocation_usd": relocation,
    }


def resolve_country_record(destination: dict, payload: dict) -> dict:
    """Find the country overlay named by a destination's validated override."""

    destination_id = destination.get("id") if isinstance(destination, dict) else None
    overrides = payload.get("destination_overrides", {}) if isinstance(payload, dict) else {}
    override = overrides.get(destination_id, {}) if isinstance(overrides, dict) else {}
    country_id = override.get("country") if isinstance(override, dict) else None
    countries = payload.get("countries", {}) if isinstance(payload, dict) else {}
    country = countries.get(country_id, {}) if isinstance(countries, dict) else {}
    return country if isinstance(country, dict) else {}


def _numeric_score(value: Any) -> float | None:
    if isinstance(value, dict):
        value = value.get("score")
    if (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and 0 <= value <= 5
    ):
        return float(value)
    return None


def active_life_score(record: dict) -> float | None:
    """Calculate the published Active Life composite from its four evidence components."""

    active_life = record.get("active_life", record) if isinstance(record, dict) else {}
    if not isinstance(active_life, dict):
        return None
    total = Decimal("0")
    for component, weight in ACTIVE_LIFE_WEIGHTS.items():
        score = _numeric_score(active_life.get(component))
        if score is None:
            return None
        total += Decimal(str(score)) * Decimal(str(weight))
    return _round_half_up(total)


def _destination_score(destination: dict, dimension: str) -> float | None:
    decision_dimensions = destination.get("decision_dimensions")
    if isinstance(decision_dimensions, list):
        for item in decision_dimensions:
            if isinstance(item, dict) and item.get("key") == dimension:
                return _numeric_score(item)
    value = _numeric_score(destination.get(dimension))
    if value is not None:
        return value
    scores = destination.get("scores")
    return _numeric_score(scores.get(dimension)) if isinstance(scores, dict) else None


def _status_priority(status: str) -> int:
    return {"eligible": 0, "conditional": 1, "needs_verification": 2, "not_eligible": 3}.get(status, 2)


def _worst_status(*statuses: str) -> str:
    return max(statuses, key=_status_priority)


def _retirement_cost_for(destination_id: str, retirement_costs: dict[str, dict]) -> dict | None:
    if isinstance(retirement_costs, dict):
        direct = retirement_costs.get(destination_id)
        if isinstance(direct, dict):
            return direct
        rows = retirement_costs.get("destinations")
        if isinstance(rows, list):
            return next((row for row in rows if isinstance(row, dict) and row.get("destination_id") == destination_id), None)
    return None


def _has_usable_cost(cost: object, profile: dict) -> bool:
    """Require the selected household's recurring evidence before scoring cost."""

    if not isinstance(cost, dict):
        return False
    profiles = cost.get("profiles")
    if not isinstance(profiles, dict):
        return False
    household_cost = profiles.get(profile["household"])
    if not isinstance(household_cost, dict):
        return False
    categories = household_cost.get("categories_usd")
    if not isinstance(categories, dict):
        return False
    if not REQUIRED_RETIREMENT_CATEGORIES.issubset(categories):
        return False
    if any(
        not _finite_nonnegative(categories.get(category))
        for category in REQUIRED_RETIREMENT_CATEGORIES
    ):
        return False
    housing_key = "annual_rent_usd" if profile["housing"] in {"rent", "buy_retirement"} else "annual_owner_costs_usd"
    housing_cost = household_cost.get(housing_key)
    if not _finite_nonnegative(housing_cost):
        return False
    if profile["housing"] in {"buy_now", "buy_retirement"}:
        property_record = cost.get("property")
        if not isinstance(property_record, dict):
            return False
        price = property_record.get("representative_price_usd")
        rate = property_record.get("acquisition_cost_rate")
        if not _finite_nonnegative(price) or price <= 0 or not _finite_nonnegative(rate):
            return False
    return True


def _normalize_confidence(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    return normalized if normalized in VALID_CONFIDENCE else None


def _conservative_confidence(values: list[object]) -> str:
    normalized = [_normalize_confidence(value) for value in values]
    if not normalized or any(value is None for value in normalized):
        return "low"
    return min(normalized, key=lambda value: _CONFIDENCE_PRIORITY[value])


def _earliest_review_date(values: list[object]) -> str | None:
    if not values:
        return None
    parsed: list[date] = []
    for value in values:
        if not isinstance(value, str):
            return None
        try:
            parsed.append(date.fromisoformat(value))
        except ValueError:
            return None
    return min(parsed).isoformat() if parsed else None


def _tax_income_category(flags: dict, income_type: str) -> str:
    if not isinstance(flags, dict):
        return "Income-category treatment needs jurisdiction-specific review."
    keys = {
        "portfolio": ("dividends", "capital_gains"),
        "pension": ("pensions",),
        "property": ("property_income",),
        "mixed": ("pensions", "dividends", "capital_gains", "property_income"),
    }.get(income_type)
    if keys is None:
        if income_type == "business_consulting":
            return (
                "Business or consulting income, work location, and permanent-establishment "
                "questions need professional review."
            )
        return "Income-category treatment depends on the selected income mix."
    selected = [flags.get(key) for key in keys]
    return " ".join(value for value in selected if isinstance(value, str) and value) or (
        "Income-category treatment needs jurisdiction-specific review."
    )


def _selected_evidence(
    *,
    eligibility: dict,
    tax: dict,
    tax_mode: dict,
    health_mode: dict,
    financial: dict,
    override: dict,
    cost: dict | None,
    profile: dict,
) -> dict:
    flags = tax.get("category_flags", {}) if isinstance(tax, dict) else {}
    cost_confidence = cost.get("confidence", {}) if isinstance(cost, dict) else {}
    cost_confidence = (
        cost_confidence.get("overall")
        if isinstance(cost_confidence, dict)
        else cost_confidence
    )
    active_life = (
        override.get("active_life", {})
        if isinstance(override.get("active_life"), dict)
        else {}
    )
    confidences: list[object] = [
        override.get("confidence"),
        eligibility.get("confidence"),
        tax.get("confidence"),
        health_mode.get("confidence"),
        financial.get("confidence"),
        cost_confidence,
        *[
            active_life.get(component, {}).get("confidence")
            if isinstance(active_life.get(component), dict)
            else None
            for component in ACTIVE_LIFE_WEIGHTS
        ],
    ]
    cost_dates: list[object] = []
    if isinstance(cost, dict) and isinstance(cost.get("sources"), list):
        cost_dates = [
            source.get("accessed_on")
            for source in cost["sources"]
            if isinstance(source, dict)
        ]
    if not cost_dates:
        cost_dates = [None]
    review_dates = [
        override.get("last_reviewed"),
        eligibility.get("last_reviewed"),
        tax.get("last_reviewed"),
        health_mode.get("last_reviewed"),
        financial.get("last_reviewed"),
        *cost_dates,
    ]
    banking_parts = [
        financial.get("bank_account_opening"),
        financial.get("tax_id_dependency"),
    ]
    transfer_parts = [
        financial.get("international_transfer_friction"),
        financial.get("international_payments"),
    ]
    return {
        "stay_facts": {
            "summary": eligibility.get("reason") or "Route conditions require confirmation.",
            "max_days": eligibility.get("max_days"),
            "work_permission": _work_permission_label(eligibility.get("work_permission")),
            "source_ids": list(eligibility.get("source_ids", [])),
        },
        "tax_facts": {
            "summary": tax_mode.get("summary")
            or "Selected-mode tax residence needs a separate review.",
            "scope_if_resident": tax.get("scope_if_resident")
            or "Resident scope needs jurisdiction-specific review.",
            "income_category": _tax_income_category(flags, profile["income_type"]),
            "treaty_reporting": tax.get("treaty_reporting_note")
            or "Treaty relief and reporting need professional review.",
        },
        "healthcare_facts": {
            "eligibility": _eligibility_label(health_mode.get("eligibility")),
            "waiting_period": health_mode.get("waiting_period_summary")
            or "Waiting-period and access rules need verification.",
            "age_limits": health_mode.get("age_limit_summary")
            or "Age limits need verification.",
            "pre_existing_conditions": health_mode.get(
                "pre_existing_condition_summary"
            )
            or "Pre-existing-condition terms need verification.",
            "evacuation": health_mode.get("evacuation_summary")
            or "Evacuation and repatriation cover need verification.",
        },
        "financial_infrastructure_facts": {
            "banking": " ".join(
                part for part in banking_parts if isinstance(part, str) and part
            )
            or "Bank-account access needs verification.",
            "transfers": " ".join(
                part for part in transfer_parts if isinstance(part, str) and part
            )
            or "International transfer access needs verification.",
            "brokerage": financial.get("brokerage_access")
            or "Brokerage access needs verification after a tax-home change.",
        },
        "confidence": _conservative_confidence(confidences),
        "last_reviewed": _earliest_review_date(review_dates),
    }


def rank_fire_abroad_destinations(
    destinations: list[dict],
    retirement_costs: dict[str, dict],
    fire_payload: dict,
    profile: dict,
) -> list[dict]:
    """Return stable FIRE Abroad destination view models for the selected profile."""

    profile = normalize_fire_profile(profile)
    overrides = fire_payload.get("destination_overrides", {}) if isinstance(fire_payload, dict) else {}
    results: list[dict] = []
    for destination in destinations:
        if not isinstance(destination, dict):
            continue
        destination_id = destination.get("id")
        if not isinstance(destination_id, str):
            continue
        override = overrides.get(destination_id, {}) if isinstance(overrides, dict) else {}
        override = override if isinstance(override, dict) else {}
        country = resolve_country_record(destination, fire_payload)
        eligibility = eligibility_for_mode(country, profile)
        mode = profile["stay_mode"]
        tax = country.get("tax", {}) if isinstance(country.get("tax"), dict) else {}
        tax_modes = tax.get("by_mode", {}) if isinstance(tax.get("by_mode"), dict) else {}
        tax_mode = tax_modes.get(mode, {}) if isinstance(tax_modes.get(mode), dict) else {}
        healthcare = country.get("healthcare", {}) if isinstance(country.get("healthcare"), dict) else {}
        health_modes = healthcare.get("by_mode", {}) if isinstance(healthcare.get("by_mode"), dict) else {}
        health_mode = health_modes.get(mode, {}) if isinstance(health_modes.get(mode), dict) else {}
        financial = (
            country.get("financial_infrastructure", {})
            if isinstance(country.get("financial_infrastructure"), dict)
            else {}
        )

        tax_score = _numeric_score(tax_mode.get("compatibility_score"))
        health_score = _numeric_score(health_mode.get("bridge_score"))
        tax_status = tax_mode.get("status") if isinstance(tax_mode.get("status"), str) else "needs_verification"
        health_status = health_mode.get("eligibility") if isinstance(health_mode.get("eligibility"), str) else "needs_verification"
        evidence_missing = (
            tax_mode.get("rankable") is not True
            or tax_score is None
            or health_score is None
            or tax_status in _UNRANKED_STATUSES
            or health_status in _UNRANKED_STATUSES
        )
        status = _worst_status(eligibility["status"], tax_status, health_status)
        if evidence_missing and status != "not_eligible":
            status = "needs_verification"

        cost = _retirement_cost_for(destination_id, retirement_costs)
        budget = build_resilience_budget(cost or {}, profile, override)
        active = active_life_score(override)
        global_access = _destination_score(destination, "global_access")
        community_fit = _destination_score(destination, "foreigner_fit")
        exit_liquidity = _destination_score(destination, "exit_liquidity")
        ownership_clarity = _destination_score(destination, "ownership_clarity")
        rent_flexibility = _numeric_score(override.get("rent_flexibility_score"))
        property_exit = None
        if None not in (exit_liquidity, ownership_clarity, rent_flexibility):
            property_exit = _round_half_up(
                (
                    Decimal(str(exit_liquidity))
                    + Decimal(str(ownership_clarity))
                    + Decimal(str(rent_flexibility))
                )
                / Decimal("3")
            )
        cost_score = (
            annual_cost_score(budget["annual_total_usd"], profile["household"])
            if _has_usable_cost(cost, profile)
            and budget["annual_total_usd"] is not None
            else None
        )
        components = {
            "active_life": active,
            "sustainable_annual_cost": cost_score,
            "healthcare_bridge": health_score,
            "stay_flexibility": eligibility["stay_score"],
            "tax_compatibility": tax_score,
            "global_access": global_access,
            "community_fit": community_fit,
            "property_exit_flexibility": property_exit,
        }
        components = {
            key: _round_half_up(value) if value is not None else None
            for key, value in components.items()
        }
        if any(value is None for value in components.values()) and status != "not_eligible":
            status = "needs_verification"
        score = None
        if status in {"eligible", "conditional"}:
            raw_score = sum(
                Decimal(str(components[key])) * Decimal(str(FIRE_WEIGHTS[key]))
                for key in FIRE_WEIGHTS
            )
            score = _round_half_up(raw_score)

        warnings = list(override.get("risk_warnings", [])) if isinstance(override.get("risk_warnings"), list) else []
        if isinstance(eligibility.get("day_warning"), str):
            warnings.append(eligibility["day_warning"])
        if profile["home_tax_context"] == "us_person":
            warnings.append("US persons generally remain subject to U.S. worldwide filing and reporting obligations.")
        threshold = tax.get("standard_day_threshold")
        if isinstance(threshold, int) and profile["annual_days"] is not None and profile["annual_days"] >= threshold:
            warnings.append("Tax residence likely at the selected day count.")
        non_day_tests = tax.get("non_day_tests")
        if isinstance(non_day_tests, str) and non_day_tests:
            warnings.append(non_day_tests)

        active_life = override.get("active_life", {}) if isinstance(override.get("active_life"), dict) else {}
        strongest = max(
            active_life.values(), key=lambda item: _numeric_score(item) or 0, default={}
        )
        strongest_reason = strongest.get("summary", "") if isinstance(strongest, dict) else ""
        status_reason = eligibility["reason"]
        if status == "needs_verification" and evidence_missing:
            status_reason = "Tax or healthcare evidence for this stay mode needs verification."
        evidence = _selected_evidence(
            eligibility=eligibility,
            tax=tax,
            tax_mode=tax_mode,
            health_mode=health_mode,
            financial=financial,
            override=override,
            cost=cost,
            profile=profile,
        )
        results.append({
            "destination_id": destination_id,
            "name": destination.get("name", destination_id),
            "status": status,
            "status_reason": status_reason,
            "score": score,
            "components": components,
            "resilience_budget": budget,
            "work_permission": eligibility["work_permission"],
            "warnings": warnings,
            "strongest_activity_reason": strongest_reason,
            "activity_tags": list(override.get("activity_tags", []))
            if isinstance(override.get("activity_tags"), list)
            else [],
            **evidence,
        })

    confidence_rank = {"high": 0, "medium_high": 1, "medium": 2, "low": 3}
    results.sort(key=lambda item: (
        _status_priority(item["status"]),
        -(item["score"] if item["score"] is not None else -1),
        confidence_rank.get(item["confidence"], 4),
        item["name"],
    ))
    return results


def validate_fire_abroad_payload(
    payload: dict,
    *,
    destination_ids: set[str],
    retirement_ids: set[str],
    as_of: date,
) -> list[str]:
    """Return every structural, referential, and freshness error in the overlay."""

    errors: list[str] = []

    scenario_sources = payload.get("sources", []) if isinstance(payload, dict) else []
    scenario_source_ids = {
        item.get("id")
        for item in scenario_sources
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item.get("id")
    }

    def validate_scenario_refs(value: object, owner: str) -> None:
        if not isinstance(value, list) or not value:
            errors.append(f"{owner} must contain at least one source")
            return
        for source_id in value:
            if source_id not in scenario_source_ids:
                errors.append(f"{owner} contains unknown source {source_id}")

    def validate_tax_screen(country_name: str, country: object) -> None:
        owner = f"countries.{country_name}.tax_screen"
        screen = country.get("tax_screen") if isinstance(country, dict) else None
        if not isinstance(screen, dict):
            errors.append(f"{owner} must be an object")
            return
        if screen.get("status") == "research_pending":
            return
        if screen.get("status") != "complete":
            errors.append(f"{owner}.status must be complete or research_pending")
            return
        if screen.get("tax_readiness") not in VALID_TAX_READINESS:
            errors.append(f"{owner}.tax_readiness must be a supported value")
        readiness_score = screen.get("tax_readiness_score")
        if isinstance(readiness_score, bool) or not isinstance(readiness_score, (int, float)) or not 0 <= readiness_score <= 5:
            errors.append(f"{owner}.tax_readiness_score must be between 0 and 5")
        validate_scenario_refs(screen.get("source_ids"), f"{owner}.source_ids")

    def add(owner: str, path: str, message: str) -> None:
        errors.append(f"{owner} {path}: {message}")

    def mapping(value: Any, owner: str, path: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            add(owner, path, "must be an object")
            return {}
        return value

    def nonempty_text(value: Any, owner: str, path: str) -> None:
        if not isinstance(value, str) or not value.strip():
            add(owner, path, "must be non-empty text")

    def score(value: Any, owner: str, path: str) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            add(owner, path, "must be a number from 0 through 5")
        elif not math.isfinite(float(value)) or not 0 <= value <= 5:
            add(owner, path, "must be from 0 through 5")

    def score_for_status(value: Any, status: Any, owner: str, path: str) -> None:
        if isinstance(status, str) and status in _UNRANKED_STATUSES:
            if value is not None:
                add(owner, path, f"must be null when status is {status!r}")
            return
        score(value, owner, path)

    def enum(value: Any, allowed: frozenset[str], owner: str, path: str) -> None:
        if not isinstance(value, str) or value not in allowed:
            add(owner, path, f"must be one of {sorted(allowed)}")

    def iso_date(value: Any, owner: str, path: str) -> date | None:
        if not isinstance(value, str):
            add(owner, path, "must be an ISO YYYY-MM-DD date")
            return None
        try:
            parsed = date.fromisoformat(value)
        except ValueError:
            add(owner, path, "must be an ISO YYYY-MM-DD date")
            return None
        if parsed.isoformat() != value:
            add(owner, path, "must be an ISO YYYY-MM-DD date")
            return None
        return parsed

    def freshness(
        value: Any, owner: str, path: str, interval: Any
    ) -> None:
        parsed = iso_date(value, owner, path)
        if parsed is None:
            return
        if parsed > as_of:
            add(owner, path, f"cannot be after evidence date {as_of.isoformat()}")
        if isinstance(interval, int) and interval > 0 and (as_of - parsed).days > interval:
            add(owner, path, f"is stale; review interval is {interval} days")

    def source_refs(
        value: Any, owner: str, path: str, available: set[str], *, allow_empty: bool = False
    ) -> None:
        if not isinstance(value, list) or (not value and not allow_empty):
            add(owner, path, "must contain at least one source ID")
            return
        seen: set[str] = set()
        for index, source_id in enumerate(value):
            item_path = f"{path}[{index}]"
            if not isinstance(source_id, str) or not source_id:
                add(owner, item_path, "must be a non-empty source ID")
                continue
            elif source_id in seen:
                add(owner, item_path, f"duplicates source ID {source_id!r}")
            elif source_id not in available:
                add(owner, item_path, f"references missing source ID {source_id!r}")
            seen.add(source_id)

    if not isinstance(payload, dict):
        return ["payload root: must be an object"]

    if payload.get("schema_version") != 1:
        add("payload", "schema_version", "must equal 1")
    reviewed_on = iso_date(payload.get("reviewed_on"), "payload", "reviewed_on")
    if reviewed_on and reviewed_on > as_of:
        add("payload", "reviewed_on", f"cannot be after {as_of.isoformat()}")

    review_policy = mapping(payload.get("review_policy"), "payload", "review_policy")
    if set(review_policy) != _REVIEW_POLICY_KEYS:
        add(
            "payload",
            "review_policy",
            f"must contain exactly {sorted(_REVIEW_POLICY_KEYS)}",
        )
    for key in _REVIEW_POLICY_KEYS:
        interval = review_policy.get(key)
        if isinstance(interval, bool) or not isinstance(interval, int) or interval <= 0:
            add("payload", f"review_policy.{key}", "must be a positive integer")

    weights = mapping(payload.get("weights"), "payload", "weights")
    if weights != FIRE_WEIGHTS:
        add("payload", "weights", "must match FIRE_WEIGHTS exactly")
    active_weights = mapping(
        payload.get("active_life_weights"), "payload", "active_life_weights"
    )
    if active_weights != ACTIVE_LIFE_WEIGHTS:
        add(
            "payload",
            "active_life_weights",
            "must match ACTIVE_LIFE_WEIGHTS exactly",
        )

    launch_ids_value = payload.get("launch_destination_ids")
    if not isinstance(launch_ids_value, list):
        add("payload", "launch_destination_ids", "must be a list")
        launch_ids: list[str] = []
    else:
        launch_ids = []
        seen_launch_ids: set[str] = set()
        for index, destination_id in enumerate(launch_ids_value):
            if not isinstance(destination_id, str) or not destination_id:
                add(
                    "payload",
                    f"launch_destination_ids[{index}]",
                    "must be a non-empty destination ID",
                )
                continue
            launch_ids.append(destination_id)
            if destination_id in seen_launch_ids:
                add(
                    "payload",
                    f"launch_destination_ids[{index}]",
                    f"duplicates destination ID {destination_id!r}",
                )
            seen_launch_ids.add(destination_id)
            if destination_id not in destination_ids:
                add(
                    destination_id,
                    "launch_destination_ids",
                    "is absent from data/destinations.json",
                )
            if destination_id not in retirement_ids:
                add(
                    destination_id,
                    "launch_destination_ids",
                    "is absent from data/retirement_costs.json",
                )
        if seen_launch_ids != CANONICAL_LAUNCH_IDS or len(launch_ids) != len(
            CANONICAL_LAUNCH_IDS
        ):
            add(
                "payload",
                "launch_destination_ids",
                f"must contain exactly {sorted(CANONICAL_LAUNCH_IDS)}",
            )

    countries = mapping(payload.get("countries"), "payload", "countries")
    overrides = mapping(
        payload.get("destination_overrides"), "payload", "destination_overrides"
    )
    launch_set = {item for item in launch_ids if isinstance(item, str)}
    unsupported_overrides = set(overrides) - launch_set
    for destination_id in sorted(unsupported_overrides):
        add(destination_id, "destination_overrides", "is not a launch destination")
    for destination_id in sorted(launch_set - set(overrides)):
        add(destination_id, "destination_overrides", "record is required")

    all_source_ids: set[str] = set()
    country_source_ids: dict[str, set[str]] = {}
    for country_id, country_value in countries.items():
        country = mapping(country_value, country_id, "record")
        validate_tax_screen(country_id, country)
        sources = country.get("sources")
        if not isinstance(sources, list) or not sources:
            add(country_id, "sources", "must contain source records")
            sources = []
        available: set[str] = set()
        for index, source_value in enumerate(sources):
            source_path = f"sources[{index}]"
            source = mapping(source_value, country_id, source_path)
            for field in _SOURCE_FIELDS:
                if field not in source:
                    add(country_id, f"{source_path}.{field}", "is required")
            source_id = source.get("id")
            nonempty_text(source_id, country_id, f"{source_path}.id")
            if isinstance(source_id, str) and source_id:
                if source_id in all_source_ids:
                    add(
                        country_id,
                        f"{source_path}.id",
                        f"source ID {source_id!r} is not globally unique",
                    )
                available.add(source_id)
                all_source_ids.add(source_id)
            for field in (
                "metric_supported",
                "publisher",
                "jurisdiction_level",
                "notes",
            ):
                nonempty_text(source.get(field), country_id, f"{source_path}.{field}")
            url = source.get("url")
            if not isinstance(url, str) or not url.startswith("https://"):
                add(country_id, f"{source_path}.url", "must use HTTPS")
            source_date = iso_date(
                source.get("source_date"),
                country_id,
                f"{source_path}.source_date",
            )
            accessed = iso_date(
                source.get("accessed_date"), country_id, f"{source_path}.accessed_date"
            )
            if source_date and source_date > as_of:
                add(
                    country_id,
                    f"{source_path}.source_date",
                    f"cannot be after {as_of.isoformat()}",
                )
            if accessed and accessed > as_of:
                add(
                    country_id,
                    f"{source_path}.accessed_date",
                    f"cannot be after {as_of.isoformat()}",
                )
            if source_date and accessed and source_date > accessed:
                add(
                    country_id,
                    f"{source_path}.source_date",
                    f"cannot be after {source_path}.accessed_date",
                )
        country_source_ids[country_id] = available

        routes = mapping(country.get("stay_routes"), country_id, "stay_routes")
        if set(routes) != VALID_STAY_MODES:
            add(
                country_id,
                "stay_routes",
                f"must contain exactly {sorted(VALID_STAY_MODES)}",
            )
        for mode in VALID_STAY_MODES:
            route = mapping(routes.get(mode), country_id, f"stay_routes.{mode}")
            route_status = route.get("status")
            enum(
                route_status,
                VALID_ELIGIBILITY,
                country_id,
                f"stay_routes.{mode}.status",
            )
            score_for_status(
                route.get("base_score"),
                route_status,
                country_id,
                f"stay_routes.{mode}.base_score",
            )
            max_days = route.get("max_days")
            if max_days is not None and (
                isinstance(max_days, bool)
                or not isinstance(max_days, int)
                or max_days <= 0
            ):
                add(
                    country_id,
                    f"stay_routes.{mode}.max_days",
                    "must be a positive integer or null",
                )
            minimum_age = route.get("minimum_age")
            if minimum_age is not None and (
                isinstance(minimum_age, bool)
                or not isinstance(minimum_age, int)
                or minimum_age < 0
            ):
                add(
                    country_id,
                    f"stay_routes.{mode}.minimum_age",
                    "must be a non-negative integer or null",
                )
            nonempty_text(
                route.get("summary"), country_id, f"stay_routes.{mode}.summary"
            )
            enum(
                route.get("work_permission"),
                VALID_WORK_PERMISSIONS,
                country_id,
                f"stay_routes.{mode}.work_permission",
            )
            mobility = mapping(
                route.get("mobility_rights"),
                country_id,
                f"stay_routes.{mode}.mobility_rights",
            )
            expected_mobility = PROFILE_ALLOWLISTS["mobility_rights"]
            if set(mobility) != expected_mobility:
                add(
                    country_id,
                    f"stay_routes.{mode}.mobility_rights",
                    f"must contain exactly {sorted(expected_mobility)}",
                )
            for mobility_profile in expected_mobility:
                selected = mapping(
                    mobility.get(mobility_profile),
                    country_id,
                    f"stay_routes.{mode}.mobility_rights.{mobility_profile}",
                )
                expected_fields = {
                    "status", "base_score", "max_days", "minimum_age",
                    "work_permission", "summary", "source_ids",
                    "confidence", "last_reviewed",
                }
                if set(selected) != expected_fields:
                    add(
                        country_id,
                        f"stay_routes.{mode}.mobility_rights.{mobility_profile}",
                        f"must contain exactly {sorted(expected_fields)}",
                    )
                selected_status = selected.get("status")
                enum(
                    selected_status,
                    VALID_ELIGIBILITY,
                    country_id,
                    f"stay_routes.{mode}.mobility_rights.{mobility_profile}.status",
                )
                score_for_status(
                    selected.get("base_score"),
                    selected_status,
                    country_id,
                    f"stay_routes.{mode}.mobility_rights.{mobility_profile}.base_score",
                )
                selected_max_days = selected.get("max_days")
                if selected_max_days is not None and (
                    isinstance(selected_max_days, bool)
                    or not isinstance(selected_max_days, int)
                    or selected_max_days <= 0
                ):
                    add(
                        country_id,
                        f"stay_routes.{mode}.mobility_rights.{mobility_profile}.max_days",
                        "must be a positive integer or null",
                    )
                selected_minimum_age = selected.get("minimum_age")
                if selected_minimum_age is not None and (
                    isinstance(selected_minimum_age, bool)
                    or not isinstance(selected_minimum_age, int)
                    or selected_minimum_age < 0
                ):
                    add(
                        country_id,
                        f"stay_routes.{mode}.mobility_rights.{mobility_profile}.minimum_age",
                        "must be a non-negative integer or null",
                    )
                enum(
                    selected.get("work_permission"),
                    VALID_WORK_PERMISSIONS,
                    country_id,
                    f"stay_routes.{mode}.mobility_rights.{mobility_profile}.work_permission",
                )
                nonempty_text(
                    selected.get("summary"),
                    country_id,
                    f"stay_routes.{mode}.mobility_rights.{mobility_profile}.summary",
                )
                source_refs(
                    selected.get("source_ids"),
                    country_id,
                    f"stay_routes.{mode}.mobility_rights.{mobility_profile}.source_ids",
                    available,
                    allow_empty=selected_status in _UNRANKED_STATUSES,
                )
                enum(
                    selected.get("confidence"),
                    VALID_CONFIDENCE,
                    country_id,
                    f"stay_routes.{mode}.mobility_rights.{mobility_profile}.confidence",
                )
                freshness(
                    selected.get("last_reviewed"),
                    country_id,
                    f"stay_routes.{mode}.mobility_rights.{mobility_profile}.last_reviewed",
                    review_policy.get("immigration_days"),
                )
            source_refs(
                route.get("source_ids"),
                country_id,
                f"stay_routes.{mode}.source_ids",
                available,
            )
            freshness(
                route.get("last_reviewed"),
                country_id,
                f"stay_routes.{mode}.last_reviewed",
                review_policy.get("immigration_days"),
            )
            enum(
                route.get("confidence"),
                VALID_CONFIDENCE,
                country_id,
                f"stay_routes.{mode}.confidence",
            )

        tax = mapping(country.get("tax"), country_id, "tax")
        threshold = tax.get("standard_day_threshold")
        if threshold is not None and (
            isinstance(threshold, bool)
            or not isinstance(threshold, int)
            or threshold <= 0
        ):
            add(
                country_id,
                "tax.standard_day_threshold",
                "must be a positive integer or null",
            )
        for field in ("non_day_tests", "scope_if_resident", "treaty_reporting_note"):
            nonempty_text(tax.get(field), country_id, f"tax.{field}")
        flags = mapping(tax.get("category_flags"), country_id, "tax.category_flags")
        for flag in _TAX_CATEGORY_FLAGS:
            nonempty_text(flags.get(flag), country_id, f"tax.category_flags.{flag}")
        source_refs(tax.get("source_ids"), country_id, "tax.source_ids", available)
        freshness(
            tax.get("last_reviewed"),
            country_id,
            "tax.last_reviewed",
            review_policy.get("tax_days"),
        )
        enum(tax.get("confidence"), VALID_CONFIDENCE, country_id, "tax.confidence")
        tax_by_mode = mapping(tax.get("by_mode"), country_id, "tax.by_mode")
        if set(tax_by_mode) != VALID_STAY_MODES:
            add(
                country_id,
                "tax.by_mode",
                f"must contain exactly {sorted(VALID_STAY_MODES)}",
            )
        for mode in VALID_STAY_MODES:
            mode_tax = mapping(tax_by_mode.get(mode), country_id, f"tax.by_mode.{mode}")
            mode_tax_status = mode_tax.get("status")
            enum(
                mode_tax_status,
                VALID_ELIGIBILITY,
                country_id,
                f"tax.by_mode.{mode}.status",
            )
            rankable = mode_tax.get("rankable")
            if not isinstance(rankable, bool):
                add(
                    country_id,
                    f"tax.by_mode.{mode}.rankable",
                    "must be a boolean",
                )
            elif (
                isinstance(mode_tax_status, str)
                and mode_tax_status in VALID_ELIGIBILITY
            ):
                should_rank = mode_tax_status not in _UNRANKED_STATUSES
                if rankable is not should_rank:
                    add(
                        country_id,
                        f"tax.by_mode.{mode}.rankable",
                        "must be "
                        f"{str(should_rank).lower()} when status is {mode_tax_status!r}",
                    )
            score_for_status(
                mode_tax.get("compatibility_score"),
                mode_tax_status,
                country_id,
                f"tax.by_mode.{mode}.compatibility_score",
            )
            nonempty_text(
                mode_tax.get("summary"),
                country_id,
                f"tax.by_mode.{mode}.summary",
            )
            source_refs(
                mode_tax.get("source_ids"),
                country_id,
                f"tax.by_mode.{mode}.source_ids",
                available,
            )

        healthcare = mapping(country.get("healthcare"), country_id, "healthcare")
        healthcare_by_mode = mapping(
            healthcare.get("by_mode"), country_id, "healthcare.by_mode"
        )
        if set(healthcare_by_mode) != VALID_STAY_MODES:
            add(
                country_id,
                "healthcare.by_mode",
                f"must contain exactly {sorted(VALID_STAY_MODES)}",
            )
        for mode in VALID_STAY_MODES:
            bridge = mapping(
                healthcare_by_mode.get(mode),
                country_id,
                f"healthcare.by_mode.{mode}",
            )
            bridge_eligibility = bridge.get("eligibility")
            score_for_status(
                bridge.get("bridge_score"),
                bridge_eligibility,
                country_id,
                f"healthcare.by_mode.{mode}.bridge_score",
            )
            enum(
                bridge_eligibility,
                VALID_ELIGIBILITY,
                country_id,
                f"healthcare.by_mode.{mode}.eligibility",
            )
            for field in _HEALTHCARE_SUMMARIES:
                nonempty_text(
                    bridge.get(field),
                    country_id,
                    f"healthcare.by_mode.{mode}.{field}",
                )
            source_refs(
                bridge.get("source_ids"),
                country_id,
                f"healthcare.by_mode.{mode}.source_ids",
                available,
            )
            freshness(
                bridge.get("last_reviewed"),
                country_id,
                f"healthcare.by_mode.{mode}.last_reviewed",
                review_policy.get("healthcare_days"),
            )
            enum(
                bridge.get("confidence"),
                VALID_CONFIDENCE,
                country_id,
                f"healthcare.by_mode.{mode}.confidence",
            )

        financial = mapping(
            country.get("financial_infrastructure"),
            country_id,
            "financial_infrastructure",
        )
        for field in (
            "bank_account_opening",
            "tax_id_dependency",
            "international_transfer_friction",
            "international_payments",
            "brokerage_access",
        ):
            nonempty_text(
                financial.get(field),
                country_id,
                f"financial_infrastructure.{field}",
            )
        source_refs(
            financial.get("source_ids"),
            country_id,
            "financial_infrastructure.source_ids",
            available,
        )
        freshness(
            financial.get("last_reviewed"),
            country_id,
            "financial_infrastructure.last_reviewed",
            review_policy.get("financial_infrastructure_days"),
        )
        enum(
            financial.get("confidence"),
            VALID_CONFIDENCE,
            country_id,
            "financial_infrastructure.confidence",
        )

    used_countries: set[str] = set()
    for destination_id, destination_value in overrides.items():
        destination = mapping(destination_value, destination_id, "record")
        country_id = destination.get("country")
        nonempty_text(country_id, destination_id, "country")
        if isinstance(country_id, str):
            used_countries.add(country_id)
        if not isinstance(country_id, str):
            available = set()
        elif country_id not in countries:
            add(destination_id, "country", f"references missing country {country_id!r}")
            available = set()
        else:
            available = country_source_ids.get(country_id, set())

        active_life = mapping(
            destination.get("active_life"), destination_id, "active_life"
        )
        for component in ACTIVE_LIFE_WEIGHTS:
            component_value = mapping(
                active_life.get(component),
                destination_id,
                f"active_life.{component}",
            )
            score(
                component_value.get("score"),
                destination_id,
                f"active_life.{component}.score",
            )
            nonempty_text(
                component_value.get("summary"),
                destination_id,
                f"active_life.{component}.summary",
            )
            source_refs(
                component_value.get("source_ids"),
                destination_id,
                f"active_life.{component}.source_ids",
                available,
            )
            enum(
                component_value.get("confidence"),
                VALID_CONFIDENCE,
                destination_id,
                f"active_life.{component}.confidence",
            )

        tags = destination.get("activity_tags")
        if not isinstance(tags, list) or not tags:
            add(destination_id, "activity_tags", "must be a non-empty list")
        else:
            seen_tags: set[str] = set()
            for index, tag in enumerate(tags):
                tag_path = f"activity_tags[{index}]"
                if not isinstance(tag, str):
                    add(destination_id, tag_path, "must be a string")
                elif tag not in VALID_ACTIVITY_TAGS:
                    add(destination_id, tag_path, f"unsupported value {tag!r}")
                elif tag in seen_tags:
                    add(destination_id, tag_path, f"duplicates activity tag {tag!r}")
                else:
                    seen_tags.add(tag)
        score(
            destination.get("rent_flexibility_score"),
            destination_id,
            "rent_flexibility_score",
        )
        relocation = destination.get("one_time_relocation_usd")
        if (
            isinstance(relocation, bool)
            or not isinstance(relocation, (int, float))
            or not math.isfinite(float(relocation))
        ):
            add(destination_id, "one_time_relocation_usd", "must be a non-negative number")
        elif relocation < 0:
            add(destination_id, "one_time_relocation_usd", "must be non-negative")
        risks = destination.get("risk_warnings")
        if not isinstance(risks, list) or not risks:
            add(destination_id, "risk_warnings", "must contain at least one warning")
        else:
            for index, warning in enumerate(risks):
                nonempty_text(warning, destination_id, f"risk_warnings[{index}]")
        source_refs(
            destination.get("source_ids"), destination_id, "source_ids", available
        )
        enum(
            destination.get("confidence"),
            VALID_CONFIDENCE,
            destination_id,
            "confidence",
        )
        freshness(
            destination.get("last_reviewed"),
            destination_id,
            "last_reviewed",
            review_policy.get("active_life_days"),
        )

    for country_id in sorted(set(countries) - used_countries):
        add(country_id, "countries", "is not referenced by a launch destination")

    return errors
