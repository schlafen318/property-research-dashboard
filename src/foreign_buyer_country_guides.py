"""Structured content and validation for migrated foreign-buyer country guides."""

from __future__ import annotations

from copy import deepcopy


REQUIRED_GUIDE_KEYS = {
    "country",
    "title",
    "description",
    "h1",
    "summary",
    "date_published",
    "date_reviewed",
    "hero_image",
    "direct_answers",
    "eligibility_sections",
    "purchase_steps",
    "cost_rows",
    "ownership_rules",
    "destination_reads",
    "buyer_checklist",
    "faqs",
    "primary_sources",
    "retirement_guide_slug",
}
REQUIRED_DIRECT_ANSWERS = {"ownership", "residency", "financing", "short_rentals"}

FOREIGN_BUYER_COUNTRY_GUIDES: dict[str, dict] = {
    "japan-property": {"country": "Japan"},
}


def get_foreign_buyer_country_guide(country_hub_slug: str) -> dict | None:
    guide = FOREIGN_BUYER_COUNTRY_GUIDES.get(country_hub_slug)
    return deepcopy(guide) if guide else None


def validate_foreign_buyer_country_guide(
    country_hub_slug: str,
    guide: dict,
    expected_destination_ids: list[str],
) -> None:
    missing = sorted(REQUIRED_GUIDE_KEYS - set(guide))
    if missing:
        raise ValueError(f"{country_hub_slug}: missing {', '.join(missing)}")
    missing_answers = sorted(REQUIRED_DIRECT_ANSWERS - set(guide["direct_answers"]))
    if missing_answers:
        raise ValueError(
            f"{country_hub_slug}: direct_answers missing {', '.join(missing_answers)}"
        )
    missing_destinations = sorted(
        set(expected_destination_ids) - set(guide["destination_reads"])
    )
    if missing_destinations:
        raise ValueError(
            f"{country_hub_slug}: destination_reads missing {', '.join(missing_destinations)}"
        )
    if set(guide["destination_reads"]) != set(expected_destination_ids):
        raise ValueError(f"{country_hub_slug}: destination_reads must match destination_ids")
    if len(guide["purchase_steps"]) < 5:
        raise ValueError(f"{country_hub_slug}: purchase_steps requires at least five steps")
    if len(guide["cost_rows"]) < 4:
        raise ValueError(f"{country_hub_slug}: cost_rows requires at least four rows")
    if len(guide["faqs"]) < 3:
        raise ValueError(f"{country_hub_slug}: faqs requires at least three questions")
    if not guide["primary_sources"]:
        raise ValueError(f"{country_hub_slug}: primary_sources is required")
