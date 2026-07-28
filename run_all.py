#!/usr/bin/env python3
"""Run all manifest cases through the adapter.

Generates both terminal summary and RESULTS.md from the same row collection.
Exits non-zero if any case fails.
"""

import json
import pathlib
import sys

from api_contract import adapter

ROOT = pathlib.Path(__file__).parent
cases_dir = ROOT / "cases"

ALLOWED_CLASSIFICATIONS = {"success", "json_parse", "body_validation", "query_validation", "routing"}

with open(cases_dir / "manifest.json", "r", encoding="utf-8") as f:
    manifest = json.load(f)

cases = manifest["cases"]

# --- Manifest validation ---
case_ids = [c["id"] for c in cases]
if len(case_ids) != len(set(case_ids)):
    print("ERROR: duplicate case_id in manifest", file=sys.stderr)
    sys.exit(2)

expected_ids = {
    "ok_01", "ok_02", "ok_03", "ok_limit0", "ok_score_int", "ok_dup_labels",
    "bad_json_01", "bad_json_02", "bad_nan_01",
    "bad_shape_01", "bad_shape_02", "bad_missing_01", "bad_null_01",
    "bad_type_01", "bad_unknown_01", "bad_item_unknown_01",
    "bad_bool_limit_01", "bad_bool_score_01",
    "q_repeat_01", "q_blank_01", "q_type_01", "q_range_01", "limit_conflict_01",
    "m_get_01", "p_404_01", "ct_01",
}
actual_ids = set(case_ids)
if actual_ids != expected_ids:
    missing = sorted(expected_ids - actual_ids)
    extra = sorted(actual_ids - expected_ids)
    print(f"ERROR: case ID set mismatch. missing={missing} extra={extra}", file=sys.stderr)
    sys.exit(2)

# Classification checks
for c in cases:
    cls = c.get("classification")
    if cls not in ALLOWED_CLASSIFICATIONS:
        print(f"ERROR: case {c['id']} has invalid/missing classification: {cls!r}", file=sys.stderr)
        sys.exit(2)

from collections import Counter
class_counts = Counter(c["classification"] for c in cases)
expected_counts = {
    "success": 6,
    "json_parse": 3,
    "body_validation": 9,
    "query_validation": 5,
    "routing": 3,
}
if dict(class_counts) != expected_counts:
    print(f"ERROR: classification distribution mismatch. got={dict(class_counts)} expected={expected_counts}", file=sys.stderr)
    sys.exit(2)

if len(cases) != 26:
    print(f"ERROR: expected 26 cases, got {len(cases)}", file=sys.stderr)
    sys.exit(2)

# --- Run cases ---
rows = []
for case in cases:
    case_id = case["id"]
    classification = case["classification"]
    method = case["method"]
    path = case["path"]
    query = case.get("query", "")
    headers = case["headers"]

    if "inline_body" in case:
        body_bytes = case["inline_body"].encode("utf-8")
    else:
        body_path = cases_dir / case["body_file"]
        body_bytes = body_path.read_bytes()

    status, resp_headers, resp_body_bytes = adapter.handle_request(
        method, path, query, headers, body_bytes
    )

    try:
        resp_body = json.loads(resp_body_bytes.decode("utf-8"))
    except Exception:
        resp_body = None

    expected_status = case["expected_status"]
    expected_body = case["expected_body"]

    # Header check
    resp_headers_lower = {k.lower(): v for k, v in resp_headers.items()}
    content_type_ok = resp_headers_lower.get("content-type") == "application/json"

    # Canonical bytes check
    canonical_bytes = adapter.dumps_canonical(expected_body)
    canonical_ok = resp_body_bytes == canonical_bytes

    # Overall pass
    body_match = resp_body == expected_body
    status_match = status == expected_status
    passed = status_match and body_match and content_type_ok and canonical_ok

    rows.append({
        "case_id": case_id,
        "classification": classification,
        "status": status,
        "expected_status": expected_status,
        "status_match": status_match,
        "response_body": resp_body,
        "expected_body": expected_body,
        "body_match": body_match,
        "response_headers": resp_headers,
        "content_type_ok": content_type_ok,
        "canonical_ok": canonical_ok,
        "passed": passed,
    })

# --- Terminal summary ---
failed = [r for r in rows if not r["passed"]]
for r in rows:
    mark = "PASS" if r["passed"] else "FAIL"
    print(f"{mark}  {r['case_id']}: {r['status']} (expected {r['expected_status']}) [{r['classification']}]")

print(f"\n{len(rows) - len(failed)}/{len(rows)} cases passed")
if failed:
    print("\nFailures:")
    for r in failed:
        print(f"  {r['case_id']}: status_match={r['status_match']} body_match={r['body_match']} "
              f"content_type_ok={r['content_type_ok']} canonical_ok={r['canonical_ok']}")
        if not r["body_match"]:
            print(f"    got : {r['response_body']}")
            print(f"    exp : {r['expected_body']}")

# --- Write results.jsonl ---
out_path = ROOT / "results.jsonl"
with open(out_path, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, sort_keys=True) + "\n")

# --- Generate RESULTS.md ---
results_md = []
results_md.append("# RESULTS — python-typed-api-contract-lab")
results_md.append("")
results_md.append(f"Total cases: {len(rows)}")
results_md.append("")
results_md.append("| case_id | classification | status | expected | pass | observation |")
results_md.append("|---------|----------------|--------|----------|------|-------------|")

for r in rows:
    cid = r["case_id"]
    cls = r["classification"]
    status = r["status"]
    exp = r["expected_status"]
    passed = "✓" if r["passed"] else "✗"
    body = r["response_body"] or {}
    detail = body.get("detail", body.get("error", ""))
    detail = str(detail).replace("|", "\\|")
    results_md.append(f"| {cid} | {cls} | {status} | {exp} | {passed} | {detail} |")

results_md.append("")
results_md.append(f"Passed: {len(rows) - len(failed)} / {len(rows)}")
results_md.append("")
results_md.append("Distribution:")
for cls in ["success", "json_parse", "body_validation", "query_validation", "routing"]:
    n = class_counts.get(cls, 0)
    results_md.append(f"- {cls}: {n}")
results_md.append("")

(ROOT / "RESULTS.md").write_text("\n".join(results_md), encoding="utf-8")
print(f"Wrote {out_path} and RESULTS.md")

sys.exit(0 if not failed else 1)
