# VERIFY — python-typed-api-contract-lab

This file supersedes the previous `VERIFY.md` at commit `f7f366213ecbd19b6a3b43284302161efcc3fbea`.

The implementation under test is commit **`a65f0281780cde30fafbf6853770b38635538b09`**:
> Fix API contract lab evidence pipeline
>
> - Add explicit 'classification' field to every case in manifest.json
>   success:6 json_parse:3 body_validation:9 query_validation:5 routing:3
>   (bad_nan_01 correctly classified as json_parse)
>
> - run_all.py now generates both terminal summary AND RESULTS.md
>   from a single row collection; exits non-zero on any failure
>
> - verify.py checks classification matches manifest, plus all
>   status/body/header/canonical assertions
>
> - test_api_contract.py: add TestManifest with 5 tests checking:
>   case count, case IDs unique, exact case-ID set,
>   classification distribution, every case has valid classification
>
> - RESULTS.md regenerated from structured rows with correct
>   6-column header matching 6 data columns

The API implementation itself (`api_contract/models.py`, `validate.py`, `adapter.py`) is **unchanged** from the original implementation commit `9f2afecd51f84cde5703e68c1cf8cfad2b07eb96`. The changes between `9f2afec` and `a65f028` repair the evidence pipeline only:
- `cases/manifest.json` – added `classification` field to all 26 cases
- `run_all.py` – now generates `RESULTS.md` from structured rows, asserts case ID set / uniqueness / classification distribution / row count = 26
- `verify.py` – asserts classification matches manifest, case ID set, headers, canonical bytes
- `test_api_contract.py` – added `TestManifest` (5 tests)
- `RESULTS.md` – regenerated from structured rows

---

## Clean-clone verification transcript

Clone and checkout exact implementation revision:

```
$ git clone https://github.com/necat101/python-typed-api-contract-lab.git /tmp/verify-clone2
Cloning into '/tmp/verify-clone2'...

$ cd /tmp/verify-clone2
$ git checkout --detach a65f0281780cde30fafbf6853770b38635538b09
HEAD is now at a65f028 Add manifest test suite + regenerated RESULTS.md
$ echo $?
0

$ git rev-parse HEAD
a65f0281780cde30fafbf6853770b38635538b09
```

Environment:

```
$ python --version
Python 3.12.3
exit=0
```

Compile:

```
$ python -m py_compile api_contract/*.py run_all.py verify.py test_api_contract.py
exit=0
```

Run all cases (generates `results.jsonl` and `RESULTS.md`):

```
$ python run_all.py
PASS  ok_01: 200 (expected 200) [success]
PASS  ok_02: 200 (expected 200) [success]
PASS  ok_03: 200 (expected 200) [success]
PASS  ok_limit0: 200 (expected 200) [success]
PASS  ok_score_int: 200 (expected 200) [success]
PASS  ok_dup_labels: 200 (expected 200) [success]
PASS  bad_json_01: 400 (expected 400) [json_parse]
PASS  bad_json_02: 400 (expected 400) [json_parse]
PASS  bad_nan_01: 400 (expected 400) [json_parse]
PASS  bad_shape_01: 422 (expected 422) [body_validation]
PASS  bad_shape_02: 422 (expected 422) [body_validation]
PASS  bad_missing_01: 422 (expected 422) [body_validation]
PASS  bad_null_01: 422 (expected 422) [body_validation]
PASS  bad_type_01: 422 (expected 422) [body_validation]
PASS  bad_unknown_01: 422 (expected 422) [body_validation]
PASS  bad_item_unknown_01: 422 (expected 422) [body_validation]
PASS  bad_bool_limit_01: 422 (expected 422) [body_validation]
PASS  bad_bool_score_01: 422 (expected 422) [body_validation]
PASS  q_repeat_01: 422 (expected 422) [query_validation]
PASS  q_blank_01: 422 (expected 422) [query_validation]
PASS  q_type_01: 422 (expected 422) [query_validation]
PASS  q_range_01: 422 (expected 422) [query_validation]
PASS  limit_conflict_01: 422 (expected 422) [query_validation]
PASS  m_get_01: 405 (expected 405) [routing]
PASS  p_404_01: 404 (expected 404) [routing]
PASS  ct_01: 415 (expected 415) [routing]

26/26 cases passed
Wrote /tmp/verify-clone2/results.jsonl and RESULTS.md
exit=0
```

Verify results:

```
$ python verify.py
All 26 cases PASS
Classification distribution verified: {'success': 6, 'json_parse': 3, 'body_validation': 9, 'query_validation': 5, 'routing': 3}
exit=0
```

Unittest suite:

```
$ python -m unittest test_api_contract -v
test_canonical_bytes (test_api_contract.TestAdapter.test_canonical_bytes) ... ok
test_duplicate_labels_allowed (test_api_contract.TestAdapter.test_duplicate_labels_allowed) ... ok
test_limit_conflict_query_and_body (test_api_contract.TestAdapter.test_limit_conflict_query_and_body) ... ok
test_limit_zero_valid (test_api_contract.TestAdapter.test_limit_zero_valid) ... ok
test_ok_tiebreak (test_api_contract.TestAdapter.test_ok_tiebreak) ... ok
test_routing_precedence_content_type_before_body (test_api_contract.TestAdapter.test_routing_precedence_content_type_before_body) ... ok
test_routing_precedence_method_before_path (test_api_contract.TestAdapter.test_routing_precedence_method_before_path) ... ok
test_routing_precedence_path_before_content_type (test_api_contract.TestAdapter.test_routing_precedence_path_before_content_type) ... ok
test_manifest_case_count (test_api_contract.TestManifest.test_manifest_case_count) ... ok
test_manifest_case_id_set (test_api_contract.TestManifest.test_manifest_case_id_set) ... ok
test_manifest_case_ids_unique (test_api_contract.TestManifest.test_manifest_case_ids_unique) ... ok
test_manifest_classification_distribution (test_api_contract.TestManifest.test_manifest_classification_distribution) ... ok
test_manifest_every_case_has_classification (test_api_contract.TestManifest.test_manifest_every_case_has_classification) ... ok
test_bool_is_rejected_for_limit (test_api_contract.TestValidate.test_bool_is_rejected_for_limit) ... ok
test_bool_is_rejected_for_score (test_api_contract.TestValidate.test_bool_is_rejected_for_score) ... ok
test_nan_rejected_at_json_layer (test_api_contract.TestValidate.test_nan_rejected_at_json_layer) ... ok
test_parse_qs_blank_default_drops (test_api_contract.TestValidate.test_parse_qs_blank_default_drops) ... ok
test_query_limit_repeated_rejected (test_api_contract.TestValidate.test_query_limit_repeated_rejected) ... ok
test_score_int_accepted (test_api_contract.TestValidate.test_score_int_accepted) ... ok
test_unknown_field_item_rejected (test_api_contract.TestValidate.test_unknown_field_item_rejected) ... ok
test_unknown_field_top_rejected (test_api_contract.TestValidate.test_unknown_field_top_rejected) ... ok

----------------------------------------------------------------------
Ran 21 tests in 0.011s

OK
exit=0
```

Results file comparison:

```
$ git diff --exit-code -- RESULTS.md
exit=0
```

Working tree:

```
$ git status --short
(exit=0, no output)
```

## Summary

- **Implementation commit tested:** `a65f0281780cde30fafbf6853770b38635538b09`
- **Python:** 3.12.3, stdlib only
- **OS:** Linux 6.17.0-1009-aws x86_64
- **Contract cases:** 26/26 PASS
  - success: 6
  - json_parse: 3
  - body_validation: 9
  - query_validation: 5
  - routing: 3
- **Unittest suite:** 21/21 PASS (16 adapter/validate tests + 5 manifest integrity tests)
- **RESULTS.md:** regenerated from structured rows, matches committed version byte-for-byte
- **Classification:** `bad_nan_01` is correctly recorded as `json_parse` (rejected by `json.loads(parse_constant=…)`, returns `invalid_json`)
- **RESULTS.md columns:** 6 columns declared, 6 columns populated (header/data mismatch fixed)

All evidence pipeline issues identified in the review have been repaired.
