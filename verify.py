#!/usr/bin/env python3
"""Verify results.jsonl against expected values.

Independent verifier – reads manifest and results.jsonl,
asserts status, headers, body, canonical bytes.
"""

import json
import sys
import pathlib

from api_contract import adapter

ROOT = pathlib.Path(__file__).parent
cases_dir = ROOT / "cases"

with open(cases_dir / "manifest.json", "r", encoding="utf-8") as f:
    manifest = json.load(f)

expected = {c["id"]: c for c in manifest["cases"]}

# Manifest sanity checks (independent of run_all.py)
assert len(expected) == 26, f"expected 26 cases, got {len(expected)}"
from collections import Counter
class_counts = Counter(c["classification"] for c in expected.values())
assert class_counts == {
    "success": 6,
    "json_parse": 3,
    "body_validation": 9,
    "query_validation": 5,
    "routing": 3,
}, f"classification distribution mismatch: {class_counts}"

expected_ids = {
    "ok_01", "ok_02", "ok_03", "ok_limit0", "ok_score_int", "ok_dup_labels",
    "bad_json_01", "bad_json_02", "bad_nan_01",
    "bad_shape_01", "bad_shape_02", "bad_missing_01", "bad_null_01",
    "bad_type_01", "bad_unknown_01", "bad_item_unknown_01",
    "bad_bool_limit_01", "bad_bool_score_01",
    "q_repeat_01", "q_blank_01", "q_type_01", "q_range_01", "limit_conflict_01",
    "m_get_01", "p_404_01", "ct_01",
}
assert set(expected.keys()) == expected_ids, f"case ID set mismatch"

results_path = ROOT / "results.jsonl"
if not results_path.exists():
    print("results.jsonl not found – run run_all.py first", file=sys.stderr)
    sys.exit(2)

failures = []
passed = 0
seen_ids = set()

with open(results_path, "r", encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        case_id = r["case_id"]
        seen_ids.add(case_id)
        exp = expected.get(case_id)
        if not exp:
            failures.append(f"{case_id}: no expected entry in manifest")
            continue

        # classification must match manifest
        if r.get("classification") != exp["classification"]:
            failures.append(f"{case_id}: classification mismatch: got {r.get('classification')!r} expected {exp['classification']!r}")
            continue

        # status
        if r["status"] != exp["expected_status"]:
            failures.append(f"{case_id}: status {r['status']} != {exp['expected_status']}")
            continue

        # body (decoded)
        if r["response_body"] != exp["expected_body"]:
            failures.append(f"{case_id}: body mismatch\n  got: {r['response_body']}\n  exp: {exp['expected_body']}")
            continue

        # headers – must include Content-Type: application/json
        resp_headers = {k.lower(): v for k, v in r["response_headers"].items()}
        if resp_headers.get("content-type") != "application/json":
            failures.append(f"{case_id}: Content-Type = {resp_headers.get('content-type')!r}, expected 'application/json'")
            continue

        # content_type_ok flag must be true
        if not r.get("content_type_ok", False):
            failures.append(f"{case_id}: content_type_ok is false")
            continue

        # canonical byte-for-byte check via flag
        if not r.get("canonical_ok", False):
            failures.append(f"{case_id}: canonical_ok is false")
            continue

        # overall passed flag
        if not r.get("passed", False):
            failures.append(f"{case_id}: passed flag is false")
            continue

        passed += 1

# Ensure we saw every expected case exactly once
if seen_ids != expected_ids:
    missing = sorted(expected_ids - seen_ids)
    extra = sorted(seen_ids - expected_ids)
    print(f"ERROR: results case ID set mismatch. missing={missing} extra={extra}", file=sys.stderr)
    sys.exit(2)

if failures:
    print(f"{passed} passed, {len(failures)} failed:")
    for msg in failures:
        print("  ", msg)
    sys.exit(1)

print(f"All {passed} cases PASS")
print(f"Classification distribution verified: {dict(class_counts)}")
sys.exit(0)
