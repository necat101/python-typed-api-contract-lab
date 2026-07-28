# VERIFY — python-typed-api-contract-lab

Fresh-clone verification transcript.

## Source commit

- Repository: https://github.com/necat101/python-typed-api-contract-lab
- Commit: `9f2afecd51f84cde5703e68c1cf8cfad2b07eb96`
- Date: 2026-07-28

## Fresh clone

```
$ git clone --depth 1 https://github.com/necat101/python-typed-api-contract-lab.git verify-clone
Cloning into 'verify-clone'...
```

## Compile check

```
$ cd verify-clone
$ python -m py_compile api_contract/*.py run_all.py verify.py test_api_contract.py
$
(no errors)
```

## Run all 26 cases

```
$ python run_all.py
Wrote 26 results to /tmp/verify-clone/results.jsonl
PASS  ok_01: 200 (expected 200)
PASS  ok_02: 200 (expected 200)
PASS  ok_03: 200 (expected 200)
PASS  ok_limit0: 200 (expected 200)
PASS  ok_score_int: 200 (expected 200)
PASS  ok_dup_labels: 200 (expected 200)
PASS  bad_json_01: 400 (expected 400)
PASS  bad_shape_01: 422 (expected 422)
PASS  bad_shape_02: 422 (expected 422)
PASS  bad_missing_01: 422 (expected 422)
PASS  bad_null_01: 422 (expected 422)
PASS  bad_type_01: 422 (expected 422)
PASS  bad_unknown_01: 422 (expected 422)
PASS  bad_item_unknown_01: 422 (expected 422)
PASS  bad_bool_limit_01: 422 (expected 422)
PASS  bad_bool_score_01: 422 (expected 422)
PASS  bad_nan_01: 400 (expected 400)
PASS  q_repeat_01: 422 (expected 422)
PASS  q_blank_01: 422 (expected 422)
PASS  q_type_01: 422 (expected 422)
PASS  q_range_01: 422 (expected 422)
PASS  limit_conflict_01: 422 (expected 422)
PASS  m_get_01: 405 (expected 405)
PASS  p_404_01: 404 (expected 404)
PASS  ct_01: 415 (expected 415)
PASS  bad_json_02: 400 (expected 400)
```

## Verify

```
$ python verify.py
All 26 cases PASS
```

Verification checks:
- status code matches expected
- response body JSON matches expected (decoded)
- `Content-Type: application/json` header present
- response body bytes match canonical `json.dumps(sort_keys=True, separators=(',',':'))` output byte-for-byte

## Unittest suite

```
$ python -m unittest test_api_contract -q
----------------------------------------------------------------------
Ran 16 tests in 0.001s

OK
```

16 independent unittest cases covering:
- bool rejection for limit/score
- int score accepted and coerced to float
- NaN rejected at JSON layer
- unknown fields rejected (top level and item level)
- parse_qs blank-value default behavior
- query limit repeated rejection
- tie-break ordering
- limit conflict (query vs body)
- limit=0 valid
- duplicate labels allowed
- canonical JSON bytes
- routing precedence: method → path → content-type → body

## Demos

```
$ python demo_annotations_dont_validate.py
=== Dataclass annotations do NOT validate at runtime ===

1. Constructing RankItem(label=123, score="nope") ...
   SUCCESS (this is the footgun): RankItem(label=123, score='nope')
   bad.label = 123, type = int
   bad.score = 'nope', type = str

2. Sending the same bad data through the adapter ...
   status = 422
   body   = {"detail":"item.label must be str","error":"invalid_body"}

Conclusion: @dataclass gives you __init__/__repr__/__eq__, not runtime type checking.
To enforce API contracts you need explicit validation (manual, marshmallow, pydantic, etc.)
```

```
$ python demo_parse_qs_blank.py
query_string = 'limit='
parse_qs(..., keep_blank_values=False) = {}
parse_qs(..., keep_blank_values=True)  = {'limit': ['']}

Default drops blank values entirely – limit= disappears.
The endpoint uses keep_blank_values=True and explicitly rejects blank limit.
```

```
$ python demo_json_error_stability.py
JSONDecodeError messages are NOT frozen into pass conditions.
The endpoint always returns a deterministic error body.

input: '{"items":[}'
  json_load_strict error_detail (observation only): 'Expecting value: line 1 column 11 (char 10)'
  adapter response: 400 {"error":"invalid_json","detail":"request body is not valid json"}

input: 'not json at all'
  json_load_strict error_detail (observation only): 'Expecting value: line 1 column 1 (char 0)'
  adapter response: 400 {"error":"invalid_json","detail":"request body is not valid json"}

input: '{"items": [{"label": "a", "score": NaN}]}'
  json_load_strict error_detail (observation only): 'non-finite constant not allowed: NaN'
  adapter response: 400 {"error":"invalid_json","detail":"request body is not valid json"}
```

## Environment

- Python 3.12.3
- No third-party packages (stdlib only)
- OS: Linux 6.17.0-1009-aws x86_64

## Result

**All 26 contract cases PASS, 16 unittest cases PASS, clean-clone reproducible.**
