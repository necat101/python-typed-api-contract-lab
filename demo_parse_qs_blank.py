"""Demonstrate parse_qs default blank-value behavior."""
import urllib.parse

qs = "limit="
default = urllib.parse.parse_qs(qs, keep_blank_values=False)
kept = urllib.parse.parse_qs(qs, keep_blank_values=True)

print(f"query_string = {qs!r}")
print(f"parse_qs(..., keep_blank_values=False) = {default!r}")
print(f"parse_qs(..., keep_blank_values=True)  = {kept!r}")
print()
print("Default drops blank values entirely – limit= disappears.")
print("The endpoint uses keep_blank_values=True and explicitly rejects blank limit.")
