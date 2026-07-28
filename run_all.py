"""Run all manifest cases through the adapter."""
import json
import pathlib

from api_contract import adapter

ROOT = pathlib.Path(__file__).parent
cases_dir = ROOT / "cases"

with open(cases_dir / "manifest.json", "r", encoding="utf-8") as f:
    manifest = json.load(f)

results = []
for case in manifest["cases"]:
    case_id = case["id"]
    method = case["method"]
    path = case["path"]
    query = case.get("query", "")
    headers = case["headers"]

    if "inline_body" in case:
        body_bytes = case["inline_body"].encode("utf-8")
    else:
        body_path = cases_dir / case["body_file"]
        body_bytes = body_path.read_bytes()

    status, resp_headers, resp_body = adapter.handle_request(
        method, path, query, headers, body_bytes
    )

    try:
        resp_json = json.loads(resp_body.decode("utf-8"))
    except Exception:
        resp_json = None

    results.append({
        "case_id": case_id,
        "status": status,
        "expected_status": case["expected_status"],
        "response_headers": resp_headers,
        "response_body": resp_json,
        "response_body_bytes": resp_body.decode("utf-8"),
        "expected_body": case["expected_body"],
    })

out_path = ROOT / "results.jsonl"
with open(out_path, "w", encoding="utf-8") as f:
    for r in results:
        f.write(json.dumps(r, sort_keys=True) + "\n")

print(f"Wrote {len(results)} results to {out_path}")
for r in results:
    ok = (r["status"] == r["expected_status"] and r["response_body"] == r["expected_body"])
    mark = "PASS" if ok else "FAIL"
    print(f"{mark}  {r['case_id']}: {r['status']} (expected {r['expected_status']})")
