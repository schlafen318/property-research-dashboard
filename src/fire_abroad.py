from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIRE_ABROAD_PATH = ROOT / "data" / "fire_abroad.json"

FIRE_WEIGHTS = {
    "active_life": 0.25,
    "sustainable_annual_cost": 0.20,
    "healthcare_bridge": 0.15,
    "stay_flexibility": 0.10,
    "tax_readiness": 0.10,
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
LAUNCH_DESTINATION_IDS = (
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
)
VALID_STAY_MODES = frozenset({"seasonal", "part_year", "full_relocation"})
VALID_TAX_READINESS = frozenset(
    {"straightforward", "moderate", "complex", "highly_profile_dependent"}
)
VALID_CONFIDENCE = frozenset({"low", "medium", "medium_high", "high"})
PROPERTY_LIFECYCLE_STAGES = ("purchase", "annual", "rental", "sale", "succession")


def load_fire_abroad(path: Path = FIRE_ABROAD_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _iso_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def _validate_source(source: Any, path: str, errors: list[str]) -> None:
    if not isinstance(source, dict):
        errors.append(f"{path} must be an object")
        return
    for key in ("id", "publisher", "url", "metric_supported", "accessed_on"):
        if not source.get(key):
            errors.append(f"{path}.{key} is required")
    if source.get("url") and not str(source["url"]).startswith("https://"):
        errors.append(f"{path}.url must use HTTPS")
    if source.get("accessed_on") and not _iso_date(source["accessed_on"]):
        errors.append(f"{path}.accessed_on must be YYYY-MM-DD")


def _validate_complete_tax_screen(
    screen: dict[str, Any], path: str, source_ids: set[str], errors: list[str]
) -> None:
    readiness = screen.get("tax_readiness")
    if readiness not in VALID_TAX_READINESS:
        errors.append(f"{path}.tax_readiness must be a supported value")
    score = screen.get("tax_readiness_score")
    if not isinstance(score, (int, float)) or not 0 <= score <= 5:
        errors.append(f"{path}.tax_readiness_score must be between 0 and 5")
    if screen.get("confidence") not in VALID_CONFIDENCE:
        errors.append(f"{path}.confidence must be a supported value")
    if not _iso_date(screen.get("last_reviewed")):
        errors.append(f"{path}.last_reviewed must be YYYY-MM-DD")

    references = screen.get("source_ids")
    if not isinstance(references, list) or not references:
        errors.append(f"{path}.source_ids must contain at least one source")
    else:
        for source_id in references:
            if source_id not in source_ids:
                errors.append(f"{path}.source_ids contains unknown source {source_id}")

    bands = screen.get("planning_bands")
    if not isinstance(bands, dict):
        errors.append(f"{path}.planning_bands must be an object")
    else:
        for mode in VALID_STAY_MODES:
            band_path = f"{path}.planning_bands.{mode}"
            band = bands.get(mode)
            if not isinstance(band, dict):
                errors.append(f"{band_path} is required")
                continue
            values = [band.get(key) for key in ("favorable_rate", "central_rate", "adverse_rate")]
            if not all(isinstance(value, (int, float)) and 0 <= value <= 1 for value in values):
                errors.append(f"{band_path} rates must be between 0 and 1")
            elif not values[0] <= values[1] <= values[2]:
                errors.append(f"{band_path} rates must be ordered favorable, central, adverse")

    included = screen.get("included_categories")
    if not isinstance(included, list) or not included:
        errors.append(f"{path}.included_categories must be non-empty")

    lifecycle = screen.get("property_lifecycle")
    if not isinstance(lifecycle, dict):
        errors.append(f"{path}.property_lifecycle must be an object")
    else:
        for stage in PROPERTY_LIFECYCLE_STAGES:
            if stage not in lifecycle:
                errors.append(f"{path}.property_lifecycle.{stage} is required")


def validate_fire_abroad_payload(
    payload: dict[str, Any],
    *,
    destination_ids: set[str],
    retirement_ids: set[str],
    as_of: date,
) -> list[str]:
    del as_of  # Freshness intervals are enforced as complete evidence is added.
    errors: list[str] = []
    if set(payload.get("launch_destination_ids", [])) != set(LAUNCH_DESTINATION_IDS):
        errors.append("launch_destination_ids must match the approved launch set")
    for destination_id in payload.get("launch_destination_ids", []):
        if destination_id not in destination_ids:
            errors.append(f"launch_destination_ids contains unknown destination {destination_id}")
        if destination_id not in retirement_ids:
            errors.append(f"launch_destination_ids lacks retirement costs for {destination_id}")

    sources = payload.get("sources", [])
    if not isinstance(sources, list):
        errors.append("sources must be an array")
        sources = []
    seen_sources: set[str] = set()
    for index, source in enumerate(sources):
        path = f"sources[{index}]"
        _validate_source(source, path, errors)
        source_id = source.get("id") if isinstance(source, dict) else None
        if source_id in seen_sources:
            errors.append(f"{path}.id must be unique")
        if source_id:
            seen_sources.add(source_id)

    countries = payload.get("countries")
    if not isinstance(countries, dict) or not countries:
        errors.append("countries must be a non-empty object")
        return errors
    for country_name, country in countries.items():
        path = f"countries.{country_name}.tax_screen"
        screen = country.get("tax_screen") if isinstance(country, dict) else None
        if not isinstance(screen, dict):
            errors.append(f"{path} must be an object")
            continue
        status = screen.get("status")
        if status == "research_pending":
            if "planning_bands" in screen:
                errors.append(f"{path}.planning_bands cannot be claimed while research is pending")
            continue
        if status != "complete":
            errors.append(f"{path}.status must be complete or research_pending")
            continue
        _validate_complete_tax_screen(screen, path, seen_sources, errors)

    return errors


VALID_HOUSEHOLDS = frozenset({"single", "couple"})
VALID_HOUSING = frozenset({"rent", "own", "buy_now", "buy_retirement"})
VALID_TAX_MODES = frozenset({"destination_estimate", "user_after_tax"})
VALID_FUNDING_SOURCES = frozenset(
    {"portfolio", "pension", "property", "work_business", "mixed"}
)
VALID_PROPERTY_USES = frozenset({"personal", "rental", "mixed"})


def _enum(value: Any, allowed: frozenset[str], default: str, label: str) -> str:
    selected = default if value in (None, "") else str(value)
    if selected not in allowed:
        raise ValueError(f"{label} must be one of {', '.join(sorted(allowed))}")
    return selected


def normalize_fire_profile(raw: dict[str, Any] | None) -> dict[str, Any]:
    raw = raw or {}
    planning_base = raw.get("planning_base")
    if planning_base in (None, ""):
        planning_base = None
    else:
        planning_base = float(planning_base)
        if planning_base < 0:
            raise ValueError("planning_base must be non-negative")
    age = float(raw.get("age", 50))
    if age < 18 or age > 100:
        raise ValueError("age must be between 18 and 100")
    return {
        "stay_mode": _enum(raw.get("stay_mode"), VALID_STAY_MODES, "part_year", "stay_mode"),
        "age": age,
        "household": _enum(raw.get("household"), VALID_HOUSEHOLDS, "single", "household"),
        "housing": _enum(raw.get("housing"), VALID_HOUSING, "rent", "housing"),
        "tax_mode": _enum(raw.get("tax_mode"), VALID_TAX_MODES, "destination_estimate", "tax_mode"),
        "funding_source": _enum(
            raw.get("funding_source"), VALID_FUNDING_SOURCES, "portfolio", "funding_source"
        ),
        "property_use": _enum(
            raw.get("property_use"), VALID_PROPERTY_USES, "personal", "property_use"
        ),
        "annual_day_band": str(raw.get("annual_day_band") or "unsure"),
        "home_tax_context": str(raw.get("home_tax_context") or "prefer_not_to_say"),
        "planning_base": planning_base,
    }


def screen_tax(country: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    screen = country.get("tax_screen", {})
    if screen.get("status") != "complete":
        return {
            "status": "tax_impact_unavailable",
            "conditional": True,
            "residence_outcome": "needs_evidence",
            "scope_summary": "Tax-impact research is not complete for this destination.",
            "readiness": "highly_profile_dependent",
            "readiness_score": None,
            "favorable_reserve": None,
            "central_reserve": None,
            "adverse_reserve": None,
            "rates": None,
            "included_categories": [],
            "material_flags": [],
            "source_ids": [],
            "confidence": "low",
        }

    band = screen["planning_bands"][profile["stay_mode"]]
    rates = {
        "favorable": float(band["favorable_rate"]),
        "central": float(band["central_rate"]),
        "adverse": float(band["adverse_rate"]),
    }
    planning_base = profile.get("planning_base")
    bypass = profile["tax_mode"] == "user_after_tax"

    def reserve(key: str) -> int | None:
        if bypass:
            return 0
        if planning_base is None:
            return None
        return round(planning_base * rates[key])

    residence_outcome = {
        "seasonal": "likely_nonresident",
        "part_year": "residence_depends_on_days_and_ties",
        "full_relocation": "likely_resident",
    }[profile["stay_mode"]]
    scope = screen.get("scope_if_resident", "unknown")
    return {
        "status": "user_after_tax" if bypass else "planning_estimate",
        "conditional": residence_outcome == "residence_depends_on_days_and_ties",
        "residence_outcome": residence_outcome,
        "scope_summary": (
            "Worldwide income may enter scope if destination tax residence applies."
            if scope == "worldwide_income"
            else "Local-source income may remain taxable."
        ),
        "readiness": screen["tax_readiness"],
        "readiness_score": float(screen["tax_readiness_score"]),
        "favorable_reserve": reserve("favorable"),
        "central_reserve": reserve("central"),
        "adverse_reserve": reserve("adverse"),
        "rates": rates,
        "included_categories": list(screen.get("included_categories", [])),
        "material_flags": list(screen.get("material_flags", [])),
        "source_ids": list(screen.get("source_ids", [])),
        "confidence": screen.get("confidence", "low"),
    }


def _profile_cost(cost: dict[str, Any], profile: dict[str, Any]) -> tuple[dict[str, Any], float]:
    household = cost.get("profiles", {}).get(profile["household"])
    if not household:
        raise ValueError(f"Missing {profile['household']} retirement-cost profile")
    categories = household.get("categories_usd", {})
    recurring = sum(float(value) for value in categories.values())
    housing = (
        float(household.get("annual_rent_usd", 0))
        if profile["housing"] == "rent"
        else float(household.get("annual_owner_costs_usd", 0))
    )
    return household, recurring + housing


def build_resilience_budget(
    cost: dict[str, Any], profile: dict[str, Any], tax_screen: dict[str, Any]
) -> dict[str, Any]:
    _, base_annual_cost = _profile_cost(cost, profile)
    rates = tax_screen.get("rates")
    if tax_screen.get("status") == "tax_impact_unavailable":
        return {
            "base_annual_cost": round(base_annual_cost),
            "favorable_annual_cost": None,
            "central_annual_cost": None,
            "adverse_annual_cost": None,
            "conditional": True,
        }

    planning_base = profile.get("planning_base")
    reserve_base = base_annual_cost if planning_base is None else planning_base
    if profile["tax_mode"] == "user_after_tax":
        reserves = {"favorable": 0, "central": 0, "adverse": 0}
    else:
        reserves = {key: round(reserve_base * rates[key]) for key in rates}
    return {
        "base_annual_cost": round(base_annual_cost),
        "favorable_tax_reserve": reserves["favorable"],
        "central_tax_reserve": reserves["central"],
        "adverse_tax_reserve": reserves["adverse"],
        "favorable_annual_cost": round(base_annual_cost + reserves["favorable"]),
        "central_annual_cost": round(base_annual_cost + reserves["central"]),
        "adverse_annual_cost": round(base_annual_cost + reserves["adverse"]),
        "conditional": bool(tax_screen.get("conditional")),
    }


def _cost_scores(rows: list[dict[str, Any]]) -> dict[str, float]:
    ranked_costs = [row["budget"]["central_annual_cost"] for row in rows if row["rankable"]]
    if not ranked_costs:
        return {}
    low, high = min(ranked_costs), max(ranked_costs)
    if low == high:
        return {row["destination_id"]: 3.0 for row in rows if row["rankable"]}
    return {
        row["destination_id"]: 5.0 - 4.0 * (row["budget"]["central_annual_cost"] - low) / (high - low)
        for row in rows
        if row["rankable"]
    }


def rank_fire_abroad_destinations(
    destinations: list[dict[str, Any]],
    retirement_costs: dict[str, dict[str, Any]],
    fire_payload: dict[str, Any],
    profile: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    normalized = normalize_fire_profile(profile)
    countries = fire_payload.get("countries", {})
    overrides = fire_payload.get("destination_overrides", {})
    rows: list[dict[str, Any]] = []
    for destination in destinations:
        destination_id = destination["id"]
        override = overrides.get(destination_id, {})
        country_name = override.get("country", destination.get("country"))
        country = countries.get(country_name, {"tax_screen": {"status": "research_pending"}})
        tax_result = screen_tax(country, normalized)
        cost = retirement_costs.get(destination_id)
        scores = override.get("scores")
        rankable = bool(cost and scores and tax_result["status"] != "tax_impact_unavailable")
        budget = (
            build_resilience_budget(cost, normalized, tax_result)
            if cost
            else {
                "base_annual_cost": None,
                "central_annual_cost": None,
                "conditional": True,
            }
        )
        rows.append(
            {
                "destination_id": destination_id,
                "name": destination.get("name", destination_id),
                "country": country_name,
                "rankable": rankable,
                "overall_score": None,
                "tax": tax_result,
                "budget": budget,
                "scores": scores or {},
            }
        )

    cost_scores = _cost_scores(rows)
    for row in rows:
        if not row["rankable"]:
            continue
        scores = row["scores"]
        dimension_scores = {
            "active_life": float(scores["active_life"]),
            "sustainable_annual_cost": cost_scores[row["destination_id"]],
            "healthcare_bridge": float(scores["healthcare_bridge"]),
            "stay_flexibility": float(scores["stay_flexibility"]),
            "tax_readiness": float(row["tax"]["readiness_score"]),
            "global_access": float(scores["global_access"]),
            "community_fit": float(scores["community_fit"]),
            "property_exit_flexibility": float(scores["property_exit_flexibility"]),
        }
        row["overall_score"] = round(
            sum(dimension_scores[key] * FIRE_WEIGHTS[key] for key in FIRE_WEIGHTS), 2
        )
        row["dimension_scores"] = dimension_scores

    return sorted(
        rows,
        key=lambda row: (
            0 if row["rankable"] else 1,
            -(row["overall_score"] or 0),
            row["name"],
        ),
    )
