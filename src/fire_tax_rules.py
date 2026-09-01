from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "data" / "fire_tax_rules.json"

RULE_TYPES = frozenset(
    {
        "residence_test",
        "rate_band",
        "allowance",
        "withholding",
        "credit_limit",
        "property_charge",
        "reporting_flag",
        "branch",
    }
)
CONFIDENCE_LEVELS = frozenset({"low", "medium", "medium_high", "high"})
FORMULA_OPERATIONS = frozenset(
    {
        "add",
        "subtract",
        "multiply",
        "divide",
        "minimum",
        "maximum",
        "greater_than",
        "greater_than_or_equal",
        "less_than",
        "less_than_or_equal",
        "progressive_rate",
        "conditional",
        "flag",
    }
)
FORMULA_ARITY = {
    "add": (2, None),
    "subtract": (2, 2),
    "multiply": (2, None),
    "divide": (2, 2),
    "minimum": (2, None),
    "maximum": (2, None),
    "greater_than": (2, 2),
    "greater_than_or_equal": (2, 2),
    "less_than": (2, 2),
    "less_than_or_equal": (2, 2),
    "progressive_rate": (1, 1),
    "conditional": (1, None),
    "flag": (1, 1),
}
BRANCH_OPERATORS = frozenset(
    {
        "equals",
        "not_equals",
        "greater_than",
        "greater_than_or_equal",
        "less_than",
        "less_than_or_equal",
        "in",
    }
)
RULE_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*-[0-9]{4}$")
CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")
OPERAND_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def load_fire_tax_rules(path: Path = RULES_PATH) -> dict[str, Any]:
    """Load the versioned detailed-tax rule dataset without mutating it."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _parse_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _require_date(record: dict[str, Any], key: str, path: str, errors: list[str]) -> date | None:
    value = record.get(key)
    parsed = _parse_date(value)
    if parsed is None:
        errors.append(f"{path}.{key} must be a YYYY-MM-DD date")
    return parsed


def _validate_review_freshness(
    record: dict[str, Any], path: str, checked_on: date | None, as_of: date, errors: list[str]
) -> None:
    interval = record.get("review_interval_days")
    if not isinstance(interval, int) or isinstance(interval, bool) or interval <= 0:
        errors.append(f"{path}.review_interval_days must be a positive integer")
        return
    if checked_on is None:
        return
    if checked_on > as_of:
        errors.append(f"{path}.checked_on cannot be after the validation date")
    elif (as_of - checked_on).days > interval:
        errors.append(
            f"{path}.checked_on is stale by its {interval}-day review interval"
        )


def _validate_source(source: Any, index: int, as_of: date, errors: list[str]) -> str | None:
    path = f"sources[{index}]"
    if not isinstance(source, dict):
        errors.append(f"{path} must be an object")
        return None

    source_id = source.get("id")
    if not isinstance(source_id, str) or not source_id:
        errors.append(f"{path}.id is required")
        source_id = None
    for key in ("publisher", "scope", "recheck_trigger"):
        if not isinstance(source.get(key), str) or not source[key].strip():
            errors.append(f"{path}.{key} is required")

    url = source.get("url")
    parsed_url = urlparse(url) if isinstance(url, str) else None
    if parsed_url is None or parsed_url.scheme != "https" or not parsed_url.netloc:
        errors.append(f"{path}.url must be an absolute HTTPS URL")

    _require_date(source, "effective_from", path, errors)
    checked = _require_date(source, "checked_on", path, errors)
    _validate_review_freshness(source, path, checked, as_of, errors)
    if source.get("source_kind") not in {"official", "primary", "synthetic"}:
        errors.append(f"{path}.source_kind must be official, primary or synthetic")
    return source_id


def _validate_operand_catalog(payload: dict[str, Any], errors: list[str]) -> set[str]:
    catalog = payload.get("operand_catalog")
    if not isinstance(catalog, dict) or not catalog:
        errors.append("operand_catalog must be a non-empty object")
        return set()

    for operand_id, operand in catalog.items():
        path = f"operand_catalog.{operand_id}"
        if not isinstance(operand_id, str) or not OPERAND_ID_PATTERN.fullmatch(operand_id):
            errors.append(f"{path} must use a stable snake_case operand ID")
        if not isinstance(operand, dict):
            errors.append(f"{path} must be an object")
            continue
        if operand.get("kind") not in {"profile", "constant", "derived"}:
            errors.append(f"{path}.kind must be profile, constant or derived")
        if operand.get("value_type") not in {"number", "money", "boolean", "string", "date"}:
            errors.append(f"{path}.value_type is unsupported")
        if operand.get("kind") == "constant" and "value" not in operand:
            errors.append(f"{path}.value is required for a constant operand")
        if operand.get("value_type") == "money":
            currency = operand.get("currency")
            if not isinstance(currency, str) or not CURRENCY_PATTERN.fullmatch(currency):
                errors.append(f"{path}.currency must be an ISO 4217-style code")
    return set(catalog)


def _validate_formula(
    formula: Any, path: str, known_operands: set[str], errors: list[str]
) -> None:
    if not isinstance(formula, dict):
        errors.append(f"{path} must be an object")
        return
    operation = formula.get("operation")
    if operation not in FORMULA_OPERATIONS:
        errors.append(f"{path}.operation is unsupported")
    operands = formula.get("operands")
    if not isinstance(operands, list) or not operands:
        errors.append(f"{path}.operands must contain at least one operand")
        return
    if operation in FORMULA_ARITY:
        minimum, maximum = FORMULA_ARITY[operation]
        if len(operands) < minimum or (maximum is not None and len(operands) > maximum):
            expected = str(minimum) if minimum == maximum else f"at least {minimum}"
            errors.append(f"{path}.operands must contain {expected} operands for {operation}")
    for operand_index, operand_id in enumerate(operands):
        operand_path = f"{path}.operands[{operand_index}]"
        if not isinstance(operand_id, str) or not operand_id:
            errors.append(f"{operand_path} must be an operand ID")
        elif operand_id not in known_operands:
            errors.append(f"{operand_path} references unknown operand {operand_id}")


def _validate_rate_bands(bands: Any, path: str, errors: list[str]) -> None:
    if not isinstance(bands, list) or not bands:
        errors.append(f"{path} must contain at least one band")
        return

    previous_upper: float | int | None = 0
    for index, band in enumerate(bands):
        band_path = f"{path}[{index}]"
        if not isinstance(band, dict):
            errors.append(f"{band_path} must be an object")
            continue

        lower = band.get("from")
        upper = band.get("up_to")
        rate = band.get("rate")
        if not _is_number(lower) or lower < 0:
            errors.append(f"{band_path}.from must be a non-negative number")
        elif previous_upper is not None:
            if lower < previous_upper:
                errors.append(f"{band_path}.from overlaps the previous band")
            elif lower > previous_upper:
                errors.append(f"{band_path}.from leaves a gap after the previous band")

        if not _is_number(rate) or not 0 <= rate <= 1:
            errors.append(f"{band_path}.rate must be between 0 and 1")

        if upper is None:
            if index != len(bands) - 1:
                errors.append(f"{band_path}.up_to may be unbounded only on the final band")
        elif not _is_number(upper):
            errors.append(f"{band_path}.up_to must be a number or null")
        elif _is_number(lower) and upper <= lower:
            errors.append(f"{band_path}.up_to must be greater than from")
        previous_upper = upper if _is_number(upper) else None

    if isinstance(bands[-1], dict) and bands[-1].get("up_to") is not None:
        errors.append(f"{path}[{len(bands) - 1}].up_to must be null for the final band")


def _validate_branch_rule(
    rule: dict[str, Any], path: str, known_operands: set[str], errors: list[str]
) -> list[tuple[str, str]]:
    branches = rule.get("branches")
    edges: list[tuple[str, str]] = []
    if not isinstance(branches, list) or not branches:
        errors.append(f"{path}.branches must contain at least one branch")
        return edges

    for index, branch in enumerate(branches):
        branch_path = f"{path}.branches[{index}]"
        if not isinstance(branch, dict):
            errors.append(f"{branch_path} must be an object")
            continue
        target = branch.get("target_rule_id")
        if not isinstance(target, str) or not target:
            errors.append(f"{branch_path}.target_rule_id is required")
        else:
            edges.append((target, f"{branch_path}.target_rule_id"))

        condition = branch.get("when")
        if not isinstance(condition, dict):
            errors.append(f"{branch_path}.when must be an object")
            continue
        operand_id = condition.get("operand")
        if operand_id not in known_operands:
            errors.append(f"{branch_path}.when.operand references unknown operand {operand_id}")
        if condition.get("operator") not in BRANCH_OPERATORS:
            errors.append(f"{branch_path}.when.operator is unsupported")
        if "value" not in condition:
            errors.append(f"{branch_path}.when.value is required")
    return edges


def _validate_rule(
    rule: Any,
    path: str,
    known_source_ids: set[str],
    known_operands: set[str],
    as_of: date,
    errors: list[str],
) -> tuple[str | None, list[tuple[str, str]]]:
    if not isinstance(rule, dict):
        errors.append(f"{path} must be an object")
        return None, []

    rule_id = rule.get("id")
    if not isinstance(rule_id, str) or not RULE_ID_PATTERN.fullmatch(rule_id):
        errors.append(f"{path}.id must be a stable kebab-case ID ending in a four-digit year")
        rule_id = None
    rule_type = rule.get("type")
    if rule_type not in RULE_TYPES:
        errors.append(f"{path}.type must be a supported rule type")
    tax_year = rule.get("tax_year")
    if not isinstance(tax_year, int) or isinstance(tax_year, bool) or tax_year < 2000:
        errors.append(f"{path}.tax_year must be a four-digit year")
    elif rule_id is not None and not rule_id.endswith(f"-{tax_year}"):
        errors.append(f"{path}.id version year must match tax_year")

    scope = rule.get("taxpayer_scope")
    if not isinstance(scope, list) or not scope or not all(
        isinstance(value, str) and value for value in scope
    ):
        errors.append(f"{path}.taxpayer_scope must contain at least one scope")
    if not isinstance(rule.get("category"), str) or not rule["category"].strip():
        errors.append(f"{path}.category is required")
    currency = rule.get("currency")
    if not isinstance(currency, str) or not CURRENCY_PATTERN.fullmatch(currency):
        errors.append(f"{path}.currency must be an ISO 4217-style code")

    _validate_formula(rule.get("formula"), f"{path}.formula", known_operands, errors)

    source_ids = rule.get("source_ids")
    if not isinstance(source_ids, list) or not source_ids:
        errors.append(f"{path}.source_ids must contain at least one source ID")
    else:
        for index, source_id in enumerate(source_ids):
            if source_id not in known_source_ids:
                errors.append(
                    f"{path}.source_ids[{index}] references unknown source {source_id}"
                )

    _require_date(rule, "effective_from", path, errors)
    checked = _require_date(rule, "checked_on", path, errors)
    _validate_review_freshness(rule, path, checked, as_of, errors)
    if rule.get("confidence") not in CONFIDENCE_LEVELS:
        errors.append(f"{path}.confidence must be a supported confidence level")
    if not isinstance(rule.get("recheck_trigger"), str) or not rule["recheck_trigger"].strip():
        errors.append(f"{path}.recheck_trigger is required")
    if not isinstance(rule.get("explanation"), str) or not rule["explanation"].strip():
        errors.append(f"{path}.explanation must be a non-empty explanation template")

    if rule_type == "rate_band":
        _validate_rate_bands(rule.get("bands"), f"{path}.bands", errors)
    edges = (
        _validate_branch_rule(rule, path, known_operands, errors)
        if rule_type == "branch"
        else []
    )
    return rule_id, edges


def _validate_branch_graph(
    rule_ids: set[str],
    branch_edges: dict[str, list[tuple[str, str]]],
    errors: list[str],
) -> None:
    for edges in branch_edges.values():
        for target, target_path in edges:
            if target not in rule_ids:
                errors.append(f"{target_path} references unknown rule {target}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(rule_id: str) -> None:
        if rule_id in visited:
            return
        visiting.add(rule_id)
        for target, target_path in branch_edges.get(rule_id, []):
            if target not in branch_edges:
                continue
            if target in visiting:
                errors.append(f"{target_path} creates a circular branch")
            else:
                visit(target)
        visiting.remove(rule_id)
        visited.add(rule_id)

    for rule_id in branch_edges:
        if rule_id not in visited:
            visit(rule_id)


def validate_fire_tax_rules(payload: dict[str, Any], as_of: date) -> list[str]:
    """Return path-addressed validation errors for detailed FIRE tax rules."""

    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["payload must be an object"]
    if payload.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    if not isinstance(payload.get("dataset_id"), str) or not payload["dataset_id"].strip():
        errors.append("dataset_id is required")
    if not isinstance(payload.get("tax_year"), int) or isinstance(payload.get("tax_year"), bool):
        errors.append("tax_year must be a four-digit year")
    _require_date(payload, "checked_on", "payload", errors)

    known_operands = _validate_operand_catalog(payload, errors)

    sources = payload.get("sources")
    known_source_ids: set[str] = set()
    if not isinstance(sources, list) or not sources:
        errors.append("sources must contain at least one source")
    else:
        for index, source in enumerate(sources):
            source_id = _validate_source(source, index, as_of, errors)
            if source_id is not None:
                if source_id in known_source_ids:
                    errors.append(f"sources[{index}].id duplicates source ID {source_id}")
                known_source_ids.add(source_id)

    jurisdictions = payload.get("jurisdictions")
    if not isinstance(jurisdictions, dict) or not jurisdictions:
        errors.append("jurisdictions must be a non-empty object")
        return errors

    for jurisdiction_key, jurisdiction in jurisdictions.items():
        jurisdiction_path = f"jurisdictions.{jurisdiction_key}"
        if not isinstance(jurisdiction, dict):
            errors.append(f"{jurisdiction_path} must be an object")
            continue
        if jurisdiction.get("id") != jurisdiction_key:
            errors.append(f"{jurisdiction_path}.id must match its jurisdiction key")
        if not isinstance(jurisdiction.get("label"), str) or not jurisdiction["label"].strip():
            errors.append(f"{jurisdiction_path}.label is required")
        if not isinstance(jurisdiction.get("synthetic"), bool):
            errors.append(f"{jurisdiction_path}.synthetic must be a boolean")
        if not isinstance(jurisdiction.get("detailed_enabled"), bool):
            errors.append(f"{jurisdiction_path}.detailed_enabled must be a boolean")
        if jurisdiction.get("synthetic") and jurisdiction.get("detailed_enabled"):
            errors.append(f"{jurisdiction_path}.detailed_enabled cannot enable synthetic rules")

        rules = jurisdiction.get("rules")
        if not isinstance(rules, list) or not rules:
            errors.append(f"{jurisdiction_path}.rules must contain at least one rule")
            continue

        rule_ids: set[str] = set()
        branch_edges: dict[str, list[tuple[str, str]]] = {}
        for index, rule in enumerate(rules):
            rule_path = f"{jurisdiction_path}.rules[{index}]"
            rule_id, edges = _validate_rule(
                rule,
                rule_path,
                known_source_ids,
                known_operands,
                as_of,
                errors,
            )
            if rule_id is None:
                continue
            if rule_id in rule_ids:
                errors.append(f"{rule_path}.id duplicates rule ID {rule_id}")
            rule_ids.add(rule_id)
            if isinstance(rule, dict) and rule.get("type") == "branch":
                branch_edges[rule_id] = edges
        _validate_branch_graph(rule_ids, branch_edges, errors)

    return errors
