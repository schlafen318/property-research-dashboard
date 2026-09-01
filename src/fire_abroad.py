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
