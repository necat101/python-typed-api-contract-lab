# RESULTS — python-typed-api-contract-lab

Total cases: 26

| case_id | status | expected | class | observation |
|---------|--------|----------|-------|-------------|
| ok_01 | 200 | 200 | success |  | ✓ |
| ok_02 | 200 | 200 | success |  | ✓ |
| ok_03 | 200 | 200 | success |  | ✓ |
| ok_limit0 | 200 | 200 | success |  | ✓ |
| ok_score_int | 200 | 200 | success |  | ✓ |
| ok_dup_labels | 200 | 200 | success |  | ✓ |
| bad_json_01 | 400 | 400 | json_parse | request body is not valid json | ✓ |
| bad_shape_01 | 422 | 422 | body_validation | top_level must be object | ✓ |
| bad_shape_02 | 422 | 422 | body_validation | items must be list | ✓ |
| bad_missing_01 | 422 | 422 | body_validation | missing field: items | ✓ |
| bad_null_01 | 422 | 422 | body_validation | items must be list | ✓ |
| bad_type_01 | 422 | 422 | body_validation | item.label must be str | ✓ |
| bad_unknown_01 | 422 | 422 | body_validation | unknown field: extra | ✓ |
| bad_item_unknown_01 | 422 | 422 | body_validation | unknown field in item: extra | ✓ |
| bad_bool_limit_01 | 422 | 422 | body_validation | limit must be integer | ✓ |
| bad_bool_score_01 | 422 | 422 | body_validation | item.score must be finite number | ✓ |
| bad_nan_01 | 400 | 400 | body_validation | request body is not valid json | ✓ |
| q_repeat_01 | 422 | 422 | query_validation | limit: repeated parameter | ✓ |
| q_blank_01 | 422 | 422 | query_validation | limit: blank value | ✓ |
| q_type_01 | 422 | 422 | query_validation | limit: not an integer | ✓ |
| q_range_01 | 422 | 422 | query_validation | limit: must be >= 0 | ✓ |
| limit_conflict_01 | 422 | 422 | query_validation | limit present in both query and body | ✓ |
| m_get_01 | 405 | 405 | routing | method_not_allowed | ✓ |
| p_404_01 | 404 | 404 | routing | not_found | ✓ |
| ct_01 | 415 | 415 | routing | unsupported_media_type | ✓ |
| bad_json_02 | 400 | 400 | json_parse | request body is not valid json | ✓ |

Passed: 26 / 26
