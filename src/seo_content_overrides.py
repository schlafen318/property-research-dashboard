from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "data" / "seo_content_overrides.json"
ALLOWED_CONTENT_FIELDS = {
    "title",
    "meta_description",
    "intro",
    "faq_question",
    "faq_answer",
    "internal_link_target",
    "internal_link_anchor",
}
REQUIRED_TOP_LEVEL_FIELDS = {
    "target_url",
    "finding_fingerprint",
    "base_content_hash",
    "generated_at",
    "model",
    "signal",
    "lifecycle",
    "cooldown_until",
    "content",
}
ALLOWED_LIFECYCLES = {"proposed", "active", "reverted"}
SUPPORTED_GUIDE_SLUGS = {
    "best-places-to-buy-property-abroad-for-retirement", "best-places-to-buy-vacation-home-abroad",
    "best-countries-for-expats-to-buy-property", "best-countries-to-buy-property-as-a-foreigner",
    "buy-property-abroad", "buying-property-abroad-for-retirement", "best-places-to-buy-a-second-home-abroad",
    "overseas-property-investment", "foreign-property-investment-risks", "portugal-vs-spain-retirement-property",
    "greece-vs-portugal-retirement-property", "japan-retirement-property-foreign-buyers",
    "thailand-villa-ownership-foreigners", "best-places-to-buy-property-in-europe",
    "where-can-foreigners-buy-property",
}


def _is_site_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and parsed.netloc == "globalhomeatlas.com" and not parsed.query and not parsed.fragment


def _is_supported_target(value: str) -> bool:
    parsed = urlparse(value)
    path = parsed.path
    if path == "/":
        return True
    if path.startswith("/countries/") or path.startswith("/destinations/"):
        parts = [part for part in path.split("/") if part]
        return len(parts) == 2 and (ROOT / "artifacts" / parts[0] / parts[1] / "index.html").exists()
    return path.strip("/") in SUPPORTED_GUIDE_SLUGS


def _valid_timestamp(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def validate_runtime_entry(entry: dict) -> None:
    target = entry.get("target_url")
    if not isinstance(target, str) or not _is_site_url(target):
        raise ValueError(f"Invalid SEO content target URL: {target}")
    if not _is_supported_target(target):
        raise ValueError(f"Unsupported SEO content target URL: {target}")
    if not re.fullmatch(r"gha-[a-z0-9-]+", str(entry.get("finding_fingerprint") or "")):
        raise ValueError(f"Invalid SEO content fingerprint: {target}")
    if not re.fullmatch(r"[a-f0-9]{64}", str(entry.get("base_content_hash") or "")):
        raise ValueError(f"Invalid SEO content hash: {target}")
    if entry.get("lifecycle") not in ALLOWED_LIFECYCLES:
        raise ValueError(f"Invalid SEO content lifecycle: {target}")
    if not _valid_timestamp(entry.get("generated_at")) or not _valid_timestamp(entry.get("cooldown_until")):
        raise ValueError(f"Invalid SEO content timestamp: {target}")
    if not isinstance(entry.get("signal"), dict):
        raise ValueError(f"Invalid SEO content signal: {target}")
    content = entry.get("content")
    if not isinstance(content, dict):
        raise ValueError(f"Invalid SEO content mapping: {target}")
    if any(value is not None and not isinstance(value, str) for value in content.values()):
        raise ValueError(f"SEO content values must be strings or null: {target}")
    if (content["faq_question"] is None) != (content["faq_answer"] is None):
        raise ValueError(f"SEO content FAQ fields must be paired: {target}")
    if (content["internal_link_target"] is None) != (content["internal_link_anchor"] is None):
        raise ValueError(f"SEO content link fields must be paired: {target}")
    if content["internal_link_target"] is not None and not _is_site_url(content["internal_link_target"]):
        raise ValueError(f"Invalid SEO content internal link: {target}")


def load_content_overrides(path: Path = DEFAULT_PATH) -> list[dict]:
    if not path.exists():
        return []
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("SEO content overrides must be a list")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != REQUIRED_TOP_LEVEL_FIELDS:
            raise ValueError("SEO content override has unknown or missing top-level fields")
        target = row["target_url"]
        if target in seen:
            raise ValueError(f"Duplicate SEO content target: {target}")
        seen.add(target)
        if not isinstance(row["content"], dict) or set(row["content"]) != ALLOWED_CONTENT_FIELDS:
            raise ValueError(f"SEO content override has unknown or missing content fields: {target}")
        validate_runtime_entry(row)
    return rows


def apply_content_override(base: dict, canonical: str, entries: list[dict]) -> dict:
    result = deepcopy(base)
    entry = next((row for row in entries if row["target_url"] == canonical), None)
    if not entry or entry.get("lifecycle") == "reverted":
        return result
    content = entry["content"]
    if content["title"] is not None:
        result["title"] = content["title"]
    if content["meta_description"] is not None:
        result["description"] = content["meta_description"]
    if content["intro"] is not None:
        result["generated_intro"] = content["intro"]
    if content["faq_question"] is not None:
        result.setdefault("faqs", []).append((content["faq_question"], content["faq_answer"]))
    if content["internal_link_target"] is not None:
        result["generated_internal_link"] = {
            "target": content["internal_link_target"],
            "anchor": content["internal_link_anchor"],
        }
    return result
