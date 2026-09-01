from __future__ import annotations

import json
import math
import re
import string
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
    "multiply": (2, 2),
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
RULE_TYPE_OPERATIONS = {
    "residence_test": frozenset(
        {"greater_than", "greater_than_or_equal", "less_than", "less_than_or_equal"}
    ),
    "rate_band": frozenset({"progressive_rate"}),
    "allowance": frozenset({"minimum", "maximum"}),
    "withholding": frozenset({"multiply"}),
    "credit_limit": frozenset({"minimum"}),
    "property_charge": frozenset({"add", "multiply", "progressive_rate"}),
    "reporting_flag": frozenset({"flag"}),
    "branch": frozenset({"conditional"}),
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
PROPERTY_LIFECYCLE_STAGES = frozenset(
    {"purchase", "annual", "rental", "sale", "inheritance", "gift"}
)
MINIMUM_ENABLEMENT_CATEGORIES = frozenset(
    {
        "tax_residence",
        "private_pension",
        "government_pension",
        "social_security",
        "dividends",
        "interest",
        "realized_gains",
        "retirement_account_withdrawal",
        "rental_income",
        "employment_consulting",
        "property_purchase",
        "property_annual",
        "property_rental",
        "property_sale",
        "property_inheritance",
        "property_gift",
        "tax_reporting",
    }
)
MINIMUM_CATEGORY_CAPABILITIES = {
    "tax_residence": frozenset({"residence_test", "branch"}),
    "private_pension": frozenset({"rate_band"}),
    "government_pension": frozenset({"rate_band"}),
    "social_security": frozenset({"rate_band"}),
    "dividends": frozenset({"rate_band"}),
    "interest": frozenset({"rate_band"}),
    "realized_gains": frozenset({"rate_band"}),
    "retirement_account_withdrawal": frozenset({"rate_band"}),
    "rental_income": frozenset({"rate_band"}),
    "employment_consulting": frozenset({"rate_band"}),
    "property_purchase": frozenset({"property_charge"}),
    "property_annual": frozenset({"property_charge"}),
    "property_rental": frozenset({"property_charge"}),
    "property_sale": frozenset({"property_charge"}),
    "property_inheritance": frozenset({"property_charge"}),
    "property_gift": frozenset({"property_charge"}),
    "tax_reporting": frozenset({"reporting_flag"}),
}


def load_fire_tax_rules(path: Path = RULES_PATH) -> dict[str, Any]:
    """Load a strict JSON detailed-tax rule object without mutating it."""

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON constant {value!r}")

    payload = json.loads(
        Path(path).read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_constant,
    )
    if not isinstance(payload, dict):
        raise ValueError("fire tax rules root must be an object")
    return payload


def _is_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return not isinstance(value, float) or math.isfinite(value)


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


def _validate_effective_dates(
    record: dict[str, Any], path: str, as_of: date, errors: list[str]
) -> tuple[date | None, date | None]:
    effective = _require_date(record, "effective_from", path, errors)
    checked = _require_date(record, "checked_on", path, errors)
    if effective is not None and effective > as_of:
        errors.append(f"{path}.effective_from must be effective by the validation date")
    if effective is not None and checked is not None and checked < effective:
        errors.append(f"{path}.checked_on cannot predate effective_from")
    _validate_review_freshness(record, path, checked, as_of, errors)
    return effective, checked


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

    _validate_effective_dates(source, path, as_of, errors)
    source_kind = source.get("source_kind")
    if not isinstance(source_kind, str) or source_kind not in {
        "official",
        "primary",
        "synthetic",
    }:
        errors.append(f"{path}.source_kind must be official, primary or synthetic")
    return source_id


def _validate_enablement_contract(
    payload: dict[str, Any], errors: list[str]
) -> tuple[set[str], set[str], dict[str, set[str]]]:
    contract = payload.get("enablement_contract")
    if not isinstance(contract, dict):
        errors.append("enablement_contract must be an object")
        return (
            set(RULE_TYPES),
            set(MINIMUM_ENABLEMENT_CATEGORIES),
            {key: set(value) for key, value in MINIMUM_CATEGORY_CAPABILITIES.items()},
        )

    required_types = contract.get("required_rule_types")
    if (
        not isinstance(required_types, list)
        or not all(isinstance(rule_type, str) for rule_type in required_types)
        or set(required_types) != set(RULE_TYPES)
    ):
        errors.append(
            "enablement_contract.required_rule_types must contain every supported rule type"
        )
        type_set = set(RULE_TYPES)
    else:
        type_set = set(required_types)

    required_categories = contract.get("required_categories")
    if (
        not isinstance(required_categories, list)
        or not all(isinstance(category, str) and category for category in required_categories)
        or set(required_categories) != set(MINIMUM_ENABLEMENT_CATEGORIES)
    ):
        errors.append(
            "enablement_contract.required_categories must contain the complete executable category set"
        )
        category_set = set(MINIMUM_ENABLEMENT_CATEGORIES)
    else:
        category_set = set(required_categories)

    capabilities = contract.get("category_capabilities")
    capability_set: dict[str, set[str]] = {}
    capabilities_valid = isinstance(capabilities, dict) and set(capabilities) == set(
        MINIMUM_CATEGORY_CAPABILITIES
    )
    if capabilities_valid:
        for category, required in MINIMUM_CATEGORY_CAPABILITIES.items():
            declared = capabilities.get(category)
            if (
                not isinstance(declared, list)
                or not all(isinstance(rule_type, str) for rule_type in declared)
                or set(declared) != set(required)
            ):
                errors.append(
                    f"enablement_contract.category_capabilities.{category} must declare its executable rule types"
                )
                capabilities_valid = False
            else:
                capability_set[category] = set(declared)
    if not capabilities_valid:
        errors.append(
            "enablement_contract.category_capabilities must cover every required category"
        )
        capability_set = {
            key: set(value) for key, value in MINIMUM_CATEGORY_CAPABILITIES.items()
        }
    return type_set, category_set, capability_set


def _value_matches_type(value: Any, value_type: Any) -> bool:
    if not isinstance(value_type, str):
        return False
    if value_type in {"number", "money"}:
        return _is_number(value)
    if value_type == "boolean":
        return isinstance(value, bool)
    if value_type == "string":
        return isinstance(value, str)
    if value_type == "date":
        return _parse_date(value) is not None
    return False


def _validate_operand_catalog(
    payload: dict[str, Any], errors: list[str]
) -> dict[str, dict[str, Any]]:
    catalog = payload.get("operand_catalog")
    if not isinstance(catalog, dict) or not catalog:
        errors.append("operand_catalog must be a non-empty object")
        return {}

    for operand_id, operand in catalog.items():
        path = f"operand_catalog.{operand_id}"
        if not isinstance(operand_id, str) or not OPERAND_ID_PATTERN.fullmatch(operand_id):
            errors.append(f"{path} must use a stable snake_case operand ID")
        if not isinstance(operand, dict):
            errors.append(f"{path} must be an object")
            continue
        kind = operand.get("kind")
        value_type = operand.get("value_type")
        if not isinstance(kind, str) or kind not in {"profile", "constant", "derived"}:
            errors.append(f"{path}.kind must be profile, constant or derived")
        if not isinstance(value_type, str) or value_type not in {
            "number",
            "money",
            "boolean",
            "string",
            "date",
        }:
            errors.append(f"{path}.value_type is unsupported")
        if kind == "constant" and "value" not in operand:
            errors.append(f"{path}.value is required for a constant operand")
        elif kind == "constant" and not _value_matches_type(
            operand.get("value"), value_type
        ):
            errors.append(f"{path}.value must match value_type")
        if value_type == "money":
            currency = operand.get("currency")
            if not isinstance(currency, str) or not CURRENCY_PATTERN.fullmatch(currency):
                errors.append(f"{path}.currency must be an ISO 4217-style code")
    valid_catalog = {
        operand_id: operand
        for operand_id, operand in catalog.items()
        if isinstance(operand_id, str) and isinstance(operand, dict)
    }
    for operand_id, operand in valid_catalog.items():
        if not isinstance(operand, dict) or operand.get("kind") != "derived":
            continue
        derivation_path = f"operand_catalog.{operand_id}.derivation"
        derivation = operand.get("derivation")
        _validate_formula(derivation, derivation_path, valid_catalog, errors)
        result_signature = _formula_result_signature(derivation, valid_catalog)
        if result_signature is not None:
            result_type, result_currency = result_signature
            if operand.get("value_type") != result_type or (
                result_type == "money" and operand.get("currency") != result_currency
            ):
                errors.append(
                    f"{derivation_path} result type and currency must match the derived operand"
                )
    _validate_derived_operand_graph(valid_catalog, errors)
    return valid_catalog


def _same_currency(operands: list[dict[str, Any]]) -> bool:
    currencies = {
        operand.get("currency")
        for operand in operands
        if operand.get("value_type") == "money"
    }
    return len(currencies) <= 1


def _validate_formula_operand_compatibility(
    operation: str,
    operand_ids: list[str],
    catalog: dict[str, dict[str, Any]],
    path: str,
    errors: list[str],
) -> None:
    if not operand_ids or any(
        not isinstance(operand_id, str) or operand_id not in catalog
        for operand_id in operand_ids
    ):
        return
    operands = [catalog[operand_id] for operand_id in operand_ids]
    types = [operand.get("value_type") for operand in operands]
    if not all(isinstance(value_type, str) for value_type in types):
        return
    comparison_ops = {
        "greater_than",
        "greater_than_or_equal",
        "less_than",
        "less_than_or_equal",
    }
    same_type_ops = {"add", "subtract", "minimum", "maximum"}

    if operation in comparison_ops:
        valid = len(types) == 2 and types[0] == types[1] and types[0] in {
            "number",
            "money",
            "date",
        }
        if not valid or not _same_currency(operands):
            errors.append(f"{path}.operands[1] is incompatible with the comparison operand")
    elif operation in same_type_ops:
        valid = all(value_type == types[0] for value_type in types) and types[0] in {
            "number",
            "money",
        }
        if not valid or not _same_currency(operands):
            errors.append(f"{path}.operands must use compatible numeric types and currency")
    elif operation == "multiply" and len(types) == 2:
        valid = types in (["number", "number"], ["money", "number"], ["number", "money"])
        if not valid:
            errors.append(f"{path}.operands must multiply a number or money by a number")
    elif operation == "divide" and len(types) == 2:
        valid = types in (["number", "number"], ["money", "number"], ["money", "money"])
        if not valid or (types == ["money", "money"] and not _same_currency(operands)):
            errors.append(f"{path}.operands must use compatible division types and currency")
    elif operation == "progressive_rate" and types[0] not in {"number", "money"}:
        errors.append(f"{path}.operands[0] must be numeric or money")
    elif operation == "flag" and types[0] != "boolean":
        errors.append(f"{path}.operands[0] must be boolean for flag")


def _formula_result_signature(
    formula: Any, catalog: dict[str, dict[str, Any]]
) -> tuple[str, Any] | None:
    if not isinstance(formula, dict):
        return None
    operation = formula.get("operation")
    if not isinstance(operation, str):
        return None
    operand_ids = formula.get("operands")
    if (
        not isinstance(operand_ids, list)
        or not operand_ids
        or any(
            not isinstance(operand_id, str) or operand_id not in catalog
            for operand_id in operand_ids
        )
    ):
        return None
    operands = [catalog[operand_id] for operand_id in operand_ids]
    operand_types = [operand.get("value_type") for operand in operands]
    if operation in {
        "greater_than",
        "greater_than_or_equal",
        "less_than",
        "less_than_or_equal",
        "flag",
    }:
        return ("boolean", None)
    if operation in {"add", "subtract", "minimum", "maximum", "progressive_rate"}:
        first = operands[0]
        return (first.get("value_type"), first.get("currency"))
    if operation == "multiply":
        money = next(
            (operand for operand in operands if operand.get("value_type") == "money"),
            None,
        )
        return ("money", money.get("currency")) if money is not None else ("number", None)
    if operation == "divide":
        first = operands[0]
        if operand_types == ["money", "number"]:
            return ("money", first.get("currency"))
        return ("number", None)
    return None


def _validate_derived_operand_graph(
    catalog: dict[str, dict[str, Any]], errors: list[str]
) -> None:
    derived_ids = {
        operand_id
        for operand_id, operand in catalog.items()
        if operand.get("kind") == "derived"
    }
    edges: dict[str, list[tuple[str, str]]] = {}
    for operand_id in sorted(derived_ids):
        derivation = catalog[operand_id].get("derivation")
        operands = derivation.get("operands") if isinstance(derivation, dict) else None
        if not isinstance(operands, list):
            edges[operand_id] = []
            continue
        edges[operand_id] = [
            (
                dependency,
                f"operand_catalog.{operand_id}.derivation.operands[{index}]",
            )
            for index, dependency in enumerate(operands)
            if isinstance(dependency, str) and dependency in derived_ids
        ]

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(operand_id: str) -> None:
        visiting.add(operand_id)
        for dependency, dependency_path in edges.get(operand_id, []):
            if dependency in visiting:
                errors.append(f"{dependency_path} creates a circular derived dependency")
            elif dependency not in visited:
                visit(dependency)
        visiting.remove(operand_id)
        visited.add(operand_id)

    for operand_id in sorted(edges):
        if operand_id not in visited:
            visit(operand_id)


def _validate_formula(
    formula: Any,
    path: str,
    operand_catalog: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    if not isinstance(formula, dict):
        errors.append(f"{path} must be an object")
        return
    operation = formula.get("operation")
    if not isinstance(operation, str) or operation not in FORMULA_OPERATIONS:
        errors.append(f"{path}.operation is unsupported")
    operands = formula.get("operands")
    if not isinstance(operands, list) or not operands:
        errors.append(f"{path}.operands must contain at least one operand")
        return
    if isinstance(operation, str) and operation in FORMULA_ARITY:
        minimum, maximum = FORMULA_ARITY[operation]
        if len(operands) < minimum or (maximum is not None and len(operands) > maximum):
            expected = str(minimum) if minimum == maximum else f"at least {minimum}"
            errors.append(f"{path}.operands must contain {expected} operands for {operation}")
    for operand_index, operand_id in enumerate(operands):
        operand_path = f"{path}.operands[{operand_index}]"
        if not isinstance(operand_id, str) or not operand_id:
            errors.append(f"{operand_path} must be an operand ID")
        elif operand_id not in operand_catalog:
            errors.append(f"{operand_path} references unknown operand {operand_id}")
    if isinstance(operation, str) and all(
        isinstance(operand_id, str) for operand_id in operands
    ):
        _validate_formula_operand_compatibility(
            operation, operands, operand_catalog, path, errors
        )


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
    rule: dict[str, Any],
    path: str,
    operand_catalog: dict[str, dict[str, Any]],
    errors: list[str],
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
        operand = operand_catalog.get(operand_id) if isinstance(operand_id, str) else None
        if operand is None:
            errors.append(f"{branch_path}.when.operand references unknown operand {operand_id}")
        operator = condition.get("operator")
        if not isinstance(operator, str) or operator not in BRANCH_OPERATORS:
            errors.append(f"{branch_path}.when.operator is unsupported")
        if "value" not in condition:
            errors.append(f"{branch_path}.when.value is required")
        elif operand is not None:
            value = condition["value"]
            value_type = operand.get("value_type")
            if operator == "in":
                valid_value = isinstance(value, list) and bool(value) and all(
                    _value_matches_type(item, value_type) for item in value
                )
            else:
                valid_value = _value_matches_type(value, value_type)
            if not valid_value:
                errors.append(f"{branch_path}.when.value must match operand value_type")
            if (
                isinstance(operator, str)
                and isinstance(value_type, str)
                and operator not in {
                "equals",
                "not_equals",
                "in",
                }
                and value_type not in {"number", "money", "date"}
            ):
                errors.append(
                    f"{branch_path}.when.operator is incompatible with operand value_type"
                )
    return edges


def _validate_explanation(
    rule: dict[str, Any], path: str, operand_catalog: dict[str, dict[str, Any]], errors: list[str]
) -> None:
    explanation = rule.get("explanation")
    if not isinstance(explanation, str) or not explanation.strip():
        errors.append(f"{path}.explanation must be a non-empty explanation template")
        return
    allowed_fields = set(operand_catalog) | {
        "amount",
        "category",
        "currency",
        "lifecycle_stage",
        "rate",
        "reporting_code",
        "tax_year",
    }
    try:
        fields = [
            field_name
            for _, field_name, _, _ in string.Formatter().parse(explanation)
            if field_name is not None
        ]
    except ValueError:
        errors.append(f"{path}.explanation contains malformed placeholders")
        return
    for field_name in fields:
        if field_name not in allowed_fields:
            errors.append(f"{path}.explanation contains unknown placeholder {field_name}")


def _validate_linked_constant(
    rule: dict[str, Any],
    path: str,
    operand_catalog: dict[str, dict[str, Any]],
    value_field: str,
    operand_field: str,
    value_type: str,
    errors: list[str],
) -> None:
    operand_id = rule.get(operand_field)
    if not isinstance(operand_id, str) or not operand_id:
        errors.append(f"{path}.{operand_field} must identify the formula constant")
        return
    formula = rule.get("formula")
    formula_operands = formula.get("operands") if isinstance(formula, dict) else None
    if not isinstance(formula_operands, list) or operand_id not in formula_operands:
        errors.append(f"{path}.{operand_field} must appear in formula.operands")
        return
    operand = operand_catalog.get(operand_id)
    if (
        operand is None
        or operand.get("kind") != "constant"
        or operand.get("value_type") != value_type
    ):
        errors.append(f"{path}.{operand_field} must reference a {value_type} constant")
        return
    if value_type == "money" and operand.get("currency") != rule.get("currency"):
        errors.append(f"{path}.{operand_field} currency must match the rule currency")
    if operand.get("value") != rule.get(value_field):
        errors.append(f"{path}.{value_field} must match its linked formula constant")


def _validate_rule_type_fields(
    rule: dict[str, Any],
    path: str,
    operand_catalog: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    rule_type = rule.get("type")
    operation = rule.get("formula", {}).get("operation") if isinstance(rule.get("formula"), dict) else None
    allowed_operations = RULE_TYPE_OPERATIONS.get(rule_type) if isinstance(rule_type, str) else None
    if allowed_operations is not None and (
        not isinstance(operation, str) or operation not in allowed_operations
    ):
        errors.append(f"{path}.formula.operation is incompatible with {rule_type}")

    if rule_type == "residence_test":
        if not isinstance(rule.get("resident_when"), bool):
            errors.append(f"{path}.resident_when must be a boolean")
    elif rule_type == "rate_band":
        _validate_rate_bands(rule.get("bands"), f"{path}.bands", errors)
    elif rule_type == "allowance":
        if not _is_number(rule.get("amount")) or rule["amount"] < 0:
            errors.append(f"{path}.amount must be a non-negative finite number")
        else:
            _validate_linked_constant(
                rule,
                path,
                operand_catalog,
                "amount",
                "amount_operand",
                "money",
                errors,
            )
    elif rule_type == "withholding":
        rate = rule.get("rate")
        if not _is_number(rate) or not 0 <= rate <= 1:
            errors.append(f"{path}.rate must be between 0 and 1")
        else:
            _validate_linked_constant(
                rule,
                path,
                operand_catalog,
                "rate",
                "rate_operand",
                "number",
                errors,
            )
    elif rule_type == "credit_limit":
        categories = rule.get("applies_to_categories")
        if not isinstance(categories, list) or not categories or not all(
            isinstance(category, str) and category for category in categories
        ):
            errors.append(f"{path}.applies_to_categories must contain income categories")
    elif rule_type == "property_charge":
        lifecycle_stage = rule.get("lifecycle_stage")
        if not isinstance(lifecycle_stage, str) or lifecycle_stage not in PROPERTY_LIFECYCLE_STAGES:
            errors.append(f"{path}.lifecycle_stage must be a supported property stage")
        if operation == "multiply":
            rate = rule.get("rate")
            if not _is_number(rate) or not 0 <= rate <= 1:
                errors.append(f"{path}.rate must be between 0 and 1")
            else:
                _validate_linked_constant(
                    rule,
                    path,
                    operand_catalog,
                    "rate",
                    "rate_operand",
                    "number",
                    errors,
                )
        elif operation == "add":
            amount = rule.get("amount")
            if not _is_number(amount) or amount < 0:
                errors.append(f"{path}.amount must be a non-negative finite number")
            else:
                _validate_linked_constant(
                    rule,
                    path,
                    operand_catalog,
                    "amount",
                    "amount_operand",
                    "money",
                    errors,
                )
        elif operation == "progressive_rate":
            _validate_rate_bands(rule.get("bands"), f"{path}.bands", errors)
    elif rule_type == "reporting_flag":
        if not isinstance(rule.get("reporting_code"), str) or not rule["reporting_code"].strip():
            errors.append(f"{path}.reporting_code is required")
    elif rule_type == "branch":
        if not isinstance(rule.get("branches"), list) or not rule["branches"]:
            errors.append(f"{path}.branches must contain at least one branch")


def _validate_rule(
    rule: Any,
    path: str,
    known_source_ids: set[str],
    operand_catalog: dict[str, dict[str, Any]],
    dataset_tax_year: Any,
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
    if not isinstance(rule_type, str) or rule_type not in RULE_TYPES:
        errors.append(f"{path}.type must be a supported rule type")
    tax_year = rule.get("tax_year")
    if not isinstance(tax_year, int) or isinstance(tax_year, bool) or tax_year < 2000:
        errors.append(f"{path}.tax_year must be a four-digit year")
    else:
        if rule_id is not None and not rule_id.endswith(f"-{tax_year}"):
            errors.append(f"{path}.id version year must match tax_year")
        if tax_year != dataset_tax_year:
            errors.append(f"{path}.tax_year must match dataset tax_year")

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

    formula = rule.get("formula")
    _validate_formula(formula, f"{path}.formula", operand_catalog, errors)
    result_signature = _formula_result_signature(formula, operand_catalog)
    if (
        result_signature is not None
        and result_signature[0] == "money"
        and currency != result_signature[1]
    ):
        errors.append(f"{path}.currency must match formula output currency")

    source_ids = rule.get("source_ids")
    if not isinstance(source_ids, list) or not source_ids:
        errors.append(f"{path}.source_ids must contain at least one source ID")
    else:
        for index, source_id in enumerate(source_ids):
            if not isinstance(source_id, str) or not source_id:
                errors.append(f"{path}.source_ids[{index}] must be a source ID")
            elif source_id not in known_source_ids:
                errors.append(
                    f"{path}.source_ids[{index}] references unknown source {source_id}"
                )

    _validate_effective_dates(rule, path, as_of, errors)
    confidence = rule.get("confidence")
    if not isinstance(confidence, str) or confidence not in CONFIDENCE_LEVELS:
        errors.append(f"{path}.confidence must be a supported confidence level")
    if not isinstance(rule.get("recheck_trigger"), str) or not rule["recheck_trigger"].strip():
        errors.append(f"{path}.recheck_trigger is required")
    _validate_explanation(rule, path, operand_catalog, errors)
    _validate_rule_type_fields(rule, path, operand_catalog, errors)
    edges = (
        _validate_branch_rule(rule, path, operand_catalog, errors)
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

    for rule_id in sorted(branch_edges):
        if rule_id not in visited:
            visit(rule_id)


def _validate_category_coverage(
    jurisdiction: dict[str, Any],
    jurisdiction_path: str,
    rules_by_id: dict[str, dict[str, Any]],
    category_capabilities: dict[str, set[str]],
    errors: list[str],
) -> None:
    coverage = jurisdiction.get("category_coverage")
    coverage_path = f"{jurisdiction_path}.category_coverage"
    if not isinstance(coverage, dict):
        errors.append(f"{coverage_path} must explicitly cover every calculation category")
        return

    for category, required_types in category_capabilities.items():
        category_path = f"{coverage_path}.{category}"
        entry = coverage.get(category)
        if not isinstance(entry, dict):
            errors.append(f"{category_path} must declare supported or no_tax treatment")
            continue
        treatment = entry.get("treatment")
        if not isinstance(treatment, str) or treatment not in {"supported", "no_tax"}:
            errors.append(f"{category_path}.treatment must be supported or no_tax")
        elif treatment == "no_tax" and category in {"tax_residence", "tax_reporting"}:
            errors.append(f"{category_path}.treatment must be supported for this category")
        rule_ids = entry.get("rule_ids")
        if not isinstance(rule_ids, list) or not rule_ids:
            errors.append(f"{category_path}.rule_ids must contain executable rules")
            continue

        covered_types: set[str] = set()
        for index, rule_id in enumerate(rule_ids):
            rule_path = f"{category_path}.rule_ids[{index}]"
            if not isinstance(rule_id, str) or rule_id not in rules_by_id:
                errors.append(f"{rule_path} must reference a rule in this jurisdiction")
                continue
            rule = rules_by_id[rule_id]
            if rule.get("category") != category:
                errors.append(f"{rule_path} references a rule for another category")
            rule_type = rule.get("type")
            if isinstance(rule_type, str):
                covered_types.add(rule_type)
            if treatment == "no_tax" and rule.get("no_tax") is not True:
                errors.append(f"{rule_path} must reference an explicit no_tax rule")
            elif treatment == "no_tax" and not _rule_encodes_zero_tax(rule):
                errors.append(f"{rule_path} no_tax rule must encode a zero-tax formula")
        missing_types = sorted(required_types - covered_types)
        if missing_types:
            errors.append(
                f"{category_path}.rule_ids must include executable "
                + ", ".join(missing_types)
            )


def _rule_encodes_zero_tax(rule: dict[str, Any]) -> bool:
    rule_type = rule.get("type")
    if rule_type == "rate_band":
        bands = rule.get("bands")
        return isinstance(bands, list) and bool(bands) and all(
            isinstance(band, dict) and band.get("rate") == 0 for band in bands
        )
    if rule_type in {"withholding", "property_charge"}:
        operation = rule.get("formula", {}).get("operation") if isinstance(rule.get("formula"), dict) else None
        if operation == "multiply":
            return rule.get("rate") == 0
        if operation == "progressive_rate":
            bands = rule.get("bands")
            return isinstance(bands, list) and bool(bands) and all(
                isinstance(band, dict) and band.get("rate") == 0 for band in bands
            )
    return False


def validate_fire_tax_rules(payload: dict[str, Any], as_of: date) -> list[str]:
    """Return path-addressed validation errors for detailed FIRE tax rules."""

    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["payload must be an object"]
    if payload.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    if not isinstance(payload.get("dataset_id"), str) or not payload["dataset_id"].strip():
        errors.append("dataset_id is required")
    dataset_tax_year = payload.get("tax_year")
    if (
        not isinstance(dataset_tax_year, int)
        or isinstance(dataset_tax_year, bool)
        or not 2000 <= dataset_tax_year <= 9999
    ):
        errors.append("tax_year must be a four-digit year")
    payload_checked = _require_date(payload, "checked_on", "payload", errors)
    if payload_checked is not None and payload_checked > as_of:
        errors.append("payload.checked_on cannot be after the validation date")

    required_rule_types, required_categories, category_capabilities = (
        _validate_enablement_contract(payload, errors)
    )

    operand_catalog = _validate_operand_catalog(payload, errors)

    sources = payload.get("sources")
    known_source_ids: set[str] = set()
    source_kinds: dict[str, Any] = {}
    if not isinstance(sources, list) or not sources:
        errors.append("sources must contain at least one source")
    else:
        for index, source in enumerate(sources):
            source_id = _validate_source(source, index, as_of, errors)
            if source_id is not None:
                if source_id in known_source_ids:
                    errors.append(f"sources[{index}].id duplicates source ID {source_id}")
                known_source_ids.add(source_id)
                if isinstance(source, dict):
                    source_kinds[source_id] = source.get("source_kind")

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

        rules = jurisdiction.get("rules")
        if not isinstance(rules, list) or not rules:
            errors.append(f"{jurisdiction_path}.rules must contain at least one rule")
            continue

        rule_ids: set[str] = set()
        rules_by_id: dict[str, dict[str, Any]] = {}
        branch_edges: dict[str, list[tuple[str, str]]] = {}
        jurisdiction_rule_types: set[str] = set()
        jurisdiction_categories: set[str] = set()
        jurisdiction_source_ids: set[str] = set()
        for index, rule in enumerate(rules):
            rule_path = f"{jurisdiction_path}.rules[{index}]"
            rule_id, edges = _validate_rule(
                rule,
                rule_path,
                known_source_ids,
                operand_catalog,
                dataset_tax_year,
                as_of,
                errors,
            )
            if isinstance(rule, dict):
                rule_type = rule.get("type")
                category = rule.get("category")
                if isinstance(rule_type, str):
                    jurisdiction_rule_types.add(rule_type)
                if isinstance(category, str):
                    jurisdiction_categories.add(category)
                source_ids = rule.get("source_ids")
                if isinstance(source_ids, list):
                    jurisdiction_source_ids.update(
                        source_id for source_id in source_ids if isinstance(source_id, str)
                    )
            if rule_id is None:
                continue
            if rule_id in rule_ids:
                errors.append(f"{rule_path}.id duplicates rule ID {rule_id}")
            rule_ids.add(rule_id)
            if isinstance(rule, dict):
                rules_by_id.setdefault(rule_id, rule)
            if isinstance(rule, dict) and rule.get("type") == "branch":
                branch_edges[rule_id] = edges
        _validate_branch_graph(rule_ids, branch_edges, errors)

        if jurisdiction.get("detailed_enabled"):
            enablement_path = f"{jurisdiction_path}.detailed_enabled"
            if jurisdiction.get("synthetic"):
                errors.append(f"{enablement_path} cannot enable synthetic rules")
            non_official_sources = sorted(
                source_id
                for source_id in jurisdiction_source_ids
                if source_kinds.get(source_id) != "official"
            )
            if non_official_sources:
                errors.append(
                    f"{enablement_path} requires all referenced sources to be official; "
                    f"non-official: {', '.join(non_official_sources)}"
                )
            missing_types = sorted(required_rule_types - jurisdiction_rule_types)
            missing_categories = sorted(required_categories - jurisdiction_categories)
            if missing_types or missing_categories:
                missing = []
                if missing_types:
                    missing.append(f"rule types {', '.join(missing_types)}")
                if missing_categories:
                    missing.append(f"categories {', '.join(missing_categories)}")
                errors.append(
                    f"{enablement_path} has an incomplete executable rule set; missing "
                    + "; ".join(missing)
                )
            _validate_category_coverage(
                jurisdiction,
                jurisdiction_path,
                rules_by_id,
                category_capabilities,
                errors,
            )

    return errors
