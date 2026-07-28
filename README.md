# python-typed-api-contract-lab

A tiny, deterministic, stdlib-only correctness lab for Python HTTP API contracts. Inspired by a Hacker News discussion about type annotations in Python web APIs.

**This is NOT a production API. It does NOT validate an ML system. It is a request-boundary contract lab.**

## What it does

Models a tiny ML-adjacent ranking endpoint `POST /v1/rank` as a pure request adapter:

```python
handle_request(method, path, query_string, headers, body_bytes)
  -> (status_code, response_headers, response_body_bytes)
```

No sockets. No networking. No Flask/Django/FastAPI/Pydantic/requests. Just `dataclasses`, `typing`, `json`, `urllib.parse`, `http.HTTPStatus`.

The ranking itself is trivial: sort items by `score DESC`, alphabetical `label` tie-break, apply optional limit. The subject is the **request boundary**, not model behavior.

## Four contract questions

1. **Why does `@dataclass` document a type but not reject wrong runtime values?**
   Annotations in `RankItem(label: str, score: float)` are documentation only. `RankItem(label=123, score="nope")` constructs successfully. See `demo_annotations_dont_validate.py`.

2. **Malformed JSON vs valid JSON with wrong shape**
   - Malformed JSON → `400 invalid_json`
   - Valid JSON with wrong top-level shape, missing fields, explicit nulls, unknown fields, or incorrect field types → `422 invalid_body`
   - JSON decoder messages are NOT frozen into the contract – the endpoint returns a deterministic `{"error":"invalid_json","detail":"request body is not valid json"}`

3. **Repeated and blank query parameters**
   `urllib.parse.parse_qs()` returns `dict[str, list[str]]`. By default `keep_blank_values=False`, so `limit=` disappears entirely. The endpoint uses `keep_blank_values=True` and explicitly rejects repeated or blank `limit`. See `demo_parse_qs_blank.py`.

4. **Deterministic success/error responses**
   All responses: UTF-8 bytes, `Content-Type: application/json`, canonical JSON with `sort_keys=True, separators=(',',':')`. Exact status codes from `http.HTTPStatus`.

## Validation policy

**Body (`RankRequest`):**
- Top-level must be `dict`, allowed fields: `{"items", "limit"}` only – unknown fields rejected at top level AND item level
- `"items"` required, must be `list`
- Each item: `dict` with exactly `{"label", "score"}`
- `label`: must be `str`
- `score`: `int` or `float`, NOT `bool`, must be finite (`math.isfinite`); `int` scores coerced to `float`
- `limit` (optional): `int`, NOT `bool`, `>= 0`
- Duplicate labels: **allowed**
- Non-finite JSON constants (`NaN`, `Infinity`, `-Infinity`) rejected at the `json.loads(parse_constant=…)` layer

**Query string:**
- `limit` may appear 0 or 1 times; repeated → 422
- Blank value (`limit=`) → 422 (requires `keep_blank_values=True` to even detect)
- Must parse as int `>= 0`
- Query `limit` and body `limit` are **mutually exclusive** – if both present → 422 conflict
- Absent limit → rank all items
- `limit=0` is **valid** → returns empty ranked list

**Routing precedence (first failure wins):**
1. method must be POST → else 405
2. path must be `/v1/rank` → else 404
3. Content-Type must be `application/json` → else 415
4. body must be valid JSON with valid shape → else 400/422

**Numeric gotchas:**
- In Python, `bool` is a subclass of `int` (`isinstance(True, int)` is `True`). We check `type(x) is int`, not `isinstance`.
- `json.loads()` accepts `NaN`/`Infinity` by default – we use `parse_constant` to reject them explicitly.
- Score accepts both `int` and `float` (finite only), rejects `bool`.

## Running

```bash
python -m py_compile api_contract/*.py run_all.py verify.py
python run_all.py          # writes results.jsonl and regenerates RESULTS.md from the same rows, 26 cases
python verify.py           # asserts status, headers, body, canonical bytes
python -m unittest test_api_contract -v   # independent unittest suite, 21 tests
```

## Demos

```bash
python demo_annotations_dont_validate.py  # dataclass accepts wrong types, adapter rejects them
python demo_parse_qs_blank.py             # parse_qs default drops blank values
python demo_json_error_stability.py       # JSONDecodeError messages vary, endpoint error is stable
```

## Cases (26)

| class | count | examples |
|-------|-------|----------|
| success | 6 | ok tie-break, query limit, empty items, limit=0, int score, duplicate labels |
| json_parse | 3 | malformed JSON, non-json body, NaN rejected |
| body_validation | 9 | wrong shape, missing/null fields, wrong types, unknown fields (top/item), bool limit, bool score |
| query_validation | 5 | repeated limit, blank limit, non-int, negative, query/body limit conflict |
| routing | 3 | GET→405, wrong path→404, wrong Content-Type→415 |

See [RESULTS.md](RESULTS.md) for the full table.

## Source material

**Hacker News discussion:** https://news.ycombinator.com/item?id=20965119 – "Types for Python HTTP APIs" – discussion of marshmallow, FastAPI, Pydantic, and the fact that Python type annotations do not enforce runtime validation.

**Instagram Engineering article:** https://instagram-engineering.com/types-for-python-http-apis-an-instagram-story-d3c3a207fdb7 – **could not be retrieved** (timed out via both web_fetch and browser automation). No claims from that article are included here; only the HN discussion summary and local observations.

**Python stdlib documentation consulted:**
- `dataclasses` – https://docs.python.org/3/library/dataclasses.html – *"nothing in @dataclass examines the type specified in the variable annotation"*
- `json` – https://docs.python.org/3/library/json.html – `json.loads`, `parse_constant`
- `urllib.parse` – https://docs.python.org/3/library/urllib.parse.html – `parse_qs`, `keep_blank_values` defaults to `False`
- `http.HTTPStatus` – https://docs.python.org/3/library/http.html

## Hacker News opinions vs stdlib docs vs local observations

**HN opinions (from thread 20965119):**
- Python type hints do NOT enforce at runtime – you can assign wrong types and code still runs
- marshmallow / FastAPI / Pydantic bridge the gap between annotations and runtime validation
- Instagram built tooling to generate OpenAPI schemas from type annotations
- mypy / static analysis can catch type errors before runtime, but is opt-in

**Stdlib documentation:**
- `@dataclass` ignores type annotations at runtime except for generating method signatures
- `urllib.parse.parse_qs(keep_blank_values=False)` drops blank values – `limit=` disappears by default
- `json.loads()` accepts `NaN`/`Infinity` unless `parse_constant` rejects them
- `bool` is a subclass of `int` in Python
- `http.HTTPStatus` provides enum names for all IANA-registered codes

**Local observations (this lab):**
- Direct `RankItem(label=123, score="nope")` construction succeeds – annotations are not checked
- The same bad data sent through `adapter.handle_request()` is rejected with `422 invalid_body`
- `parse_qs("limit=", keep_blank_values=False)` → `{}`; with `keep_blank_values=True` → `{"limit": [""]}`
- `json.loads('{"x": NaN}')` succeeds by default; with `parse_constant` hook it raises `ValueError`
- All 26 contract cases pass with deterministic canonical JSON output
- Routing precedence is observable: wrong method beats wrong path beats wrong Content-Type beats bad body

## License

MIT
