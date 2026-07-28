"""Verify results.jsonl against expected values."""
import json
import sys
import pathlib

from api_contract import adapter

ROOT = pathlib.Path(__file__).parent
cases_dir = ROOT / "cases"

with open(cases_dir / "manifest.json", "r", encoding="utf-8") as f:
    manifest = json.load(f)

expected = {c["id"]: c for c in manifest["cases"]}

results_path = ROOT / "results.jsonl"
if not results_path.exists():
    print("results.jsonl not found – run run_all.py first", file=sys.stderr)
    sys.exit(2)

failures = []
passed = 0
with open(results_path, "r", encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        case_id = r["case_id"]
        exp = expected.get(case_id)
        if not exp:
            failures.append(f"{case_id}: no expected entry")
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

        # canonical byte-for-byte check
        canonical = adapter.dumps_canonical(exp["expected_body"])
        actual_bytes = r["response_body_bytes"].encode("utf-8")
        if actual_bytes != canonical:
            failures.append(f"{case_id}: body bytes not canonical\n  got: {actual_bytes!r}\n  exp: {canonical!r}")
            continue

        passed += 1

if failures:
    print(f"{passed} passed, {len(failures)} failed:")
    for msg in failures:
        print("  ", msg)
    sys.exit(1)

print(f"All {passed} cases PASS")
sys.exit(0)
