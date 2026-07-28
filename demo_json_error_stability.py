"""Observe that JSONDecodeError messages are not a stable API contract."""
import json
from api_contract import validate, adapter

bad_inputs = [
    '{"items":[}',
    'not json at all',
    '{"items": [{"label": "a", "score": NaN}]}',
]

print("JSONDecodeError messages are NOT frozen into pass conditions.")
print("The endpoint always returns a deterministic error body.\n")

for s in bad_inputs:
    print(f"input: {s!r}")
    val, err = validate.json_load_strict(s)
    print(f"  json_load_strict error_detail (observation only): {err!r}")
    status, _, body = adapter.handle_request(
        "POST", "/v1/rank", "", {"Content-Type": "application/json"},
        s.encode("utf-8")
    )
    print(f"  adapter response: {status} {body.decode('utf-8')}")
    print()
