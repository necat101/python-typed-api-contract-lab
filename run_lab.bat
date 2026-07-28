@echo off
REM run_lab.bat — run the full python-typed-api-contract-lab test suite on Windows
setlocal EnableDelayedExpansion

cd /d "%~dp0"

REM Find a usable python interpreter
set PYTHON=
for %%P in (py python python3) do (
    where %%P >nul 2>nul
    if !errorlevel! equ 0 (
        %%P -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)" >nul 2>nul
        if !errorlevel! equ 0 (
            set PYTHON=%%P
            goto :found_python
        )
    )
)
:found_python

if "%PYTHON%"=="" (
    echo ERROR: Python 3.11+ not found. Tried: py, python, python3
    echo Install Python from https://python.org
    echo Make sure "Add Python to PATH" is checked during install.
    pause
    exit /b 1
)

echo ==^> python-typed-api-contract-lab
for /f "delims=" %%v in ('%PYTHON% --version 2^>^&1') do echo     Python: %%v
echo.

echo ==^> Step 1/5: compile check
%PYTHON% -m py_compile api_contract\*.py run_all.py verify.py test_api_contract.py
if %errorlevel% neq 0 goto :failed
echo     OK
echo.

echo ==^> Step 2/5: contract cases ^(26 cases^)
%PYTHON% run_all.py
if %errorlevel% neq 0 goto :failed
echo.

echo ==^> Step 3/5: verify results
%PYTHON% verify.py
if %errorlevel% neq 0 goto :failed
echo.

echo ==^> Step 4/5: unittest suite ^(21 tests^)
%PYTHON% -m unittest test_api_contract -v
if %errorlevel% neq 0 goto :failed
echo.

echo ==^> Step 5/5: demos
echo   -- demo_annotations_dont_validate.py --
%PYTHON% demo_annotations_dont_validate.py
echo.
echo   -- demo_parse_qs_blank.py --
%PYTHON% demo_parse_qs_blank.py
echo.
echo   -- demo_json_error_stability.py --
%PYTHON% demo_json_error_stability.py
echo.

echo ==^> All done! 26 contract cases PASS, 21 unittest cases PASS
pause
exit /b 0

:failed
echo.
echo FAILED at step %errorlevel%
pause
exit /b %errorlevel%
