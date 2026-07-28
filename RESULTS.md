# RESULTS — python-typed-api-contract-lab

Total cases: 26

| case_id | classification | status | expected | pass | observation |
|---------|----------------|--------|----------|------|-------------|
| ok_01 | success | 200 | 200 | ✓ |  |
| ok_02 | success | 200 | 200 | ✓ |  |
| ok_03 | success | 200 | 200 | ✓ |  |
| ok_limit0 | success | 200 | 200 | ✓ |  |
| ok_score_int | success | 200 | 200 | ✓ |  |
| ok_dup_labels | success | 200 | 200 | ✓ |  |
| bad_json_01 | json_parse | 400 | 400 | ✓ | request body is not valid json |
| bad_json_02 | json_parse | 400 | 400 | ✓ | request body is not valid json |
| bad_nan_01 | json_parse | 400 | 400 | ✓ | request body is not valid json |
| bad_shape_01 | body_validation | 422 | 422 | ✓ | top_level must be object |
| bad_shape_02 | body_validation | 422 | 422 | ✓ | items must be list |
| bad_missing_01 | body_validation | 422 | 422 | ✓ | missing field: items |
| bad_null_01 | body_validation | 422 | 422 | ✓ | items must be list |
| bad_type_01 | body_validation | 422 | 422 | ✓ | item.label must be str |
| bad_unknown_01 | body_validation | 422 | 422 | ✓ | unknown field: extra |
| bad_item_unknown_01 | body_validation | 422 | 422 | ✓ | unknown field in item: extra |
| bad_bool_limit_01 | body_validation | 422 | 422 | ✓ | limit must be integer |
| bad_bool_score_01 | body_validation | 422 | 422 | ✓ | item.score must be finite number |
| q_repeat_01 | query_validation | 422 | 422 | ✓ | limit: repeated parameter |
| q_blank_01 | query_validation | 422 | 422 | ✓ | limit: blank value |
| q_type_01 | query_validation | 422 | 422 | ✓ | limit: not an integer |
| q_range_01 | query_validation | 422 | 422 | ✓ | limit: must be >= 0 |
| limit_conflict_01 | query_validation | 422 | 422 | ✓ | limit present in both query and body |
| m_get_01 | routing | 405 | 405 | ✓ | method_not_allowed |
| p_404_01 | routing | 404 | 404 | ✓ | not_found |
| ct_01 | routing | 415 | 415 | ✓ | unsupported_media_type |

Passed: 26 / 26

Distribution:
- success: 6
- json_parse: 3
- body_validation: 9
- query_validation: 5
- routing: 3
