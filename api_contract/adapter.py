"""Request adapter for POST /v1/rank.

Pure function: (method, path, query_string, headers, body_bytes)
  -> (status_code, response_headers, response_body_bytes)

No sockets, no networking, no concurrency.
"""

import json
import urllib.parse
from http import HTTPStatus

from . import validate


def dumps_canonical(obj: object) -> bytes:
    """Canonical JSON: UTF-8, sort_keys, compact separators."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def error_response(status: HTTPStatus, error_code: str, detail: str | None = None) -> tuple[int, dict[str, str], bytes]:
    body_obj = {"error": error_code}
    if detail is not None:
        body_obj["detail"] = detail
    body = dumps_canonical(body_obj)
    headers = {"Content-Type": "application/json"}
    return status.value, headers, body


def success_response(obj: object) -> tuple[int, dict[str, str], bytes]:
    body = dumps_canonical(obj)
    headers = {"Content-Type": "application/json"}
    return HTTPStatus.OK.value, headers, body


def handle_request(
    method: str,
    path: str,
    query_string: str,
    headers: dict[str, str],
    body_bytes: bytes,
) -> tuple[int, dict[str, str], bytes]:
    """Handle a single ranking request.

    Routing precedence (first failure wins):
    1. method must be POST
    2. path must be /v1/rank
    3. Content-Type must be application/json
    4. body must be valid JSON, valid shape

    Validation policy:
    - query limit and body limit are MUTUALLY EXCLUSIVE
      if both present → 422 conflict
    - absent limit → rank all items
    - limit=0 is VALID → returns empty ranked list
    - duplicate labels: ALLOWED
    - unknown fields rejected at top level AND item level
    """

    # 1. Method
    if method != "POST":
        return error_response(HTTPStatus.METHOD_NOT_ALLOWED, "method_not_allowed")

    # 2. Path
    if path != "/v1/rank":
        return error_response(HTTPStatus.NOT_FOUND, "not_found")

    # 3. Content-Type
    content_type = ""
    for k, v in headers.items():
        if k.lower() == "content-type":
            content_type = v.split(";")[0].strip().lower()
            break
    if content_type != "application/json":
        return error_response(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "unsupported_media_type")

    # 4. JSON body
    try:
        body_str = body_bytes.decode("utf-8")
    except Exception:
        return error_response(HTTPStatus.BAD_REQUEST, "invalid_json", "request body is not valid json")

    body_obj, json_err = validate.json_load_strict(body_str)
    if json_err is not None:
        # Do NOT leak decoder wording into the contract response
        return error_response(HTTPStatus.BAD_REQUEST, "invalid_json", "request body is not valid json")

    req, body_err = validate.validate_rank_request_body(body_obj)
    if body_err is not None:
        return error_response(HTTPStatus.UNPROCESSABLE_ENTITY, "invalid_body", body_err)

    # 5. Query limit
    query_limit, query_err = validate.validate_query_limit(query_string)
    if query_err is not None:
        return error_response(HTTPStatus.UNPROCESSABLE_ENTITY, "invalid_query", query_err)

    body_limit = req["limit"]

    # Query limit and body limit are mutually exclusive
    if query_limit is not None and body_limit is not None:
        return error_response(HTTPStatus.UNPROCESSABLE_ENTITY, "invalid_query", "limit present in both query and body")

    limit = query_limit if query_limit is not None else body_limit

    # 6. Rank
    items = req["items"]
    ranked = sorted(items, key=lambda x: (-x["score"], x["label"]))
    if limit is not None:
        ranked = ranked[:limit]

    return success_response({"ranked": ranked, "count": len(ranked)})
