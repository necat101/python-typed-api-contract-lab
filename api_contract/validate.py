"""Validation helpers for /v1/rank.

All validation is explicit and stdlib-only.
"""

import json
import math
import urllib.parse


def json_load_strict(s: str) -> tuple[object | None, str | None]:
    """Parse JSON, rejecting non-finite constants.

    Returns (value, None) on success, (None, error_detail) on failure.
    error_detail is the raw JSONDecodeError message, for observation only.
    """
    def reject_constant(const: str) -> None:
        raise ValueError(f"non-finite constant not allowed: {const}")

    try:
        value = json.loads(s, parse_constant=reject_constant)
        return value, None
    except json.JSONDecodeError as e:
        return None, str(e)
    except ValueError as e:
        # from parse_constant rejecting NaN/Infinity
        return None, str(e)


def _is_int_not_bool(x: object) -> bool:
    """Return True iff x is exactly int (not bool, bool is subclass of int)."""
    return type(x) is int


def _is_number_not_bool(x: object) -> bool:
    """Return True iff x is int or float (not bool), and finite."""
    if type(x) is bool:
        return False
    if type(x) is int:
        return True
    if type(x) is float:
        return math.isfinite(x)
    return False


def validate_rank_request_body(obj: object) -> tuple[dict | None, str | None]:
    """Validate the request body object.

    Returns (validated_dict, None) on success,
            (None, error_detail) on failure.

    Policy:
    - top-level must be dict
    - allowed fields: {"items", "limit"}
    - unknown fields rejected at top level AND item level
    - "items" required, must be list
    - each item: dict with exactly {"label", "score"}
    - label: must be str
    - score: int or float, not bool, must be finite; ints coerced to float
    - limit (optional): int, not bool, >= 0
    - duplicate labels: ALLOWED
    """
    if not isinstance(obj, dict):
        return None, "top_level must be object"

    allowed_top = {"items", "limit"}
    for k in obj.keys():
        if k not in allowed_top:
            return None, f"unknown field: {k}"

    if "items" not in obj:
        return None, "missing field: items"

    items_raw = obj["items"]
    if not isinstance(items_raw, list):
        return None, "items must be list"

    items_validated = []
    for item in items_raw:
        if not isinstance(item, dict):
            return None, "item must be object"
        allowed_item = {"label", "score"}
        for k in item.keys():
            if k not in allowed_item:
                return None, f"unknown field in item: {k}"
        if "label" not in item:
            return None, "item missing field: label"
        if "score" not in item:
            return None, "item missing field: score"
        label = item["label"]
        score = item["score"]
        if not isinstance(label, str):
            return None, "item.label must be str"
        if not _is_number_not_bool(score):
            return None, "item.score must be finite number"
        items_validated.append({"label": label, "score": float(score)})

    body_limit = None
    if "limit" in obj:
        lim = obj["limit"]
        if not _is_int_not_bool(lim):
            return None, "limit must be integer"
        if lim < 0:
            return None, "limit must be >= 0"
        body_limit = lim

    return {"items": items_validated, "limit": body_limit}, None


def validate_query_limit(query_string: str) -> tuple[int | None, str | None]:
    """Validate ?limit= query parameter.

    Policy:
    - limit may appear 0 or 1 times
    - repeated → error
    - blank → error (requires keep_blank_values=True to even see blank)
    - must parse as int >= 0, reject bool
    - absent → None (means no limit, i.e. all items)

    Returns (limit_or_None, None) on success,
            (None, error_detail) on failure.
    """
    qs = urllib.parse.parse_qs(query_string, keep_blank_values=True)
    if "limit" not in qs:
        return None, None

    values = qs["limit"]
    if len(values) != 1:
        return None, "limit: repeated parameter"

    raw = values[0]
    if raw == "":
        return None, "limit: blank value"

    try:
        n = int(raw)
    except ValueError:
        return None, "limit: not an integer"

    if n < 0:
        return None, "limit: must be >= 0"

    return n, None


def parse_qs_default_behavior_demo(query_string: str) -> dict:
    """Demonstrate parse_qs default vs keep_blank_values=True.

    Default keep_blank_values=False drops blank values entirely.
    """
    default = urllib.parse.parse_qs(query_string, keep_blank_values=False)
    kept = urllib.parse.parse_qs(query_string, keep_blank_values=True)
    return {"default": default, "keep_blank_values_true": kept}
