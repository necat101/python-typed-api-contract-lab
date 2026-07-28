#!/usr/bin/env fish
# run_lab.fish — run the full python-typed-api-contract-lab test suite
# Works with fish shell (https://fishshell.com)

cd (path dirname (status -f))

# Find a usable python interpreter
set -l PYTHON ""
for cmd in python3 python py
    if command -v $cmd >/dev/null 2>&1
        if $cmd -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)" 2>/dev/null
            set PYTHON $cmd
            break
        end
    end
end

if test -z "$PYTHON"
    echo "ERROR: Python 3.11+ not found. Tried: python3, python, py" >&2
    echo "Install Python from https://python.org" >&2
    exit 1
end

echo "==> python-typed-api-contract-lab"
echo "    Python: "$PYTHON --version
echo

echo "==> Step 1/5: compile check"
$PYTHON -m py_compile api_contract/*.py run_all.py verify.py test_api_contract.py
or exit $status
echo "    OK"
echo

echo "==> Step 2/5: contract cases (26 cases)"
$PYTHON run_all.py
or exit $status
echo

echo "==> Step 3/5: verify results"
$PYTHON verify.py
or exit $status
echo

echo "==> Step 4/5: unittest suite (21 tests)"
$PYTHON -m unittest test_api_contract -v
or exit $status
echo

echo "==> Step 5/5: demos"
echo "  -- demo_annotations_dont_validate.py --"
$PYTHON demo_annotations_dont_validate.py
echo
echo "  -- demo_parse_qs_blank.py --"
$PYTHON demo_parse_qs_blank.py
echo
echo "  -- demo_json_error_stability.py --"
$PYTHON demo_json_error_stability.py
echo

echo "==> All done! 26 contract cases PASS, 21 unittest cases PASS"
