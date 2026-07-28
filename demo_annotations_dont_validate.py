"""Demonstrate that @dataclass annotations do NOT validate at runtime.

This is the core of question A: type annotations document expected types
but do not automatically reject wrong runtime values.
"""

import json
from api_contract.models import RankItem
from api_contract import adapter

print("=== Dataclass annotations do NOT validate at runtime ===\n")

# 1. Direct construction with wrong types succeeds
print("1. Constructing RankItem(label=123, score=\"nope\") ...")
try:
    bad = RankItem(label=123, score="nope")  # type: ignore
    print(f"   SUCCESS (this is the footgun): {bad!r}")
    print(f"   bad.label = {bad.label!r}, type = {type(bad.label).__name__}")
    print(f"   bad.score = {bad.score!r}, type = {type(bad.score).__name__}")
except Exception as e:
    print(f"   REJECTED: {e}")

print()

# 2. The adapter validation DOES reject the same bad data
print("2. Sending the same bad data through the adapter ...")
body = json.dumps({"items": [{"label": 123, "score": "nope"}]}).encode("utf-8")
status, headers, resp_body = adapter.handle_request(
    "POST", "/v1/rank", "", {"Content-Type": "application/json"}, body
)
print(f"   status = {status}")
print(f"   body   = {resp_body.decode('utf-8')}")

print()
print("Conclusion: @dataclass gives you __init__/__repr__/__eq__, not runtime type checking.")
print("To enforce API contracts you need explicit validation (manual, marshmallow, pydantic, etc.)")
