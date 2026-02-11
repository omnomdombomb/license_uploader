@echo off
REM License Uploader - Windows Diagnostic Tool Launcher
REM Run comprehensive diagnostics to identify Windows deployment issues

title License Uploader - Diagnostics

echo.
echo ================================================================
echo    License Uploader - Windows Diagnostic Tool
echo ================================================================
echo.

cd /d "%~dp0"

REM Try to find Python
set PYTHON_CMD=
set PYTHON_FOUND=0

REM Method 1: Try 'python' command
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    set PYTHON_FOUND=1
    goto :run_diagnostic
)

REM Method 2: Try 'py' launcher
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    set PYTHON_FOUND=1
    goto :run_diagnostic
)

REM Method 3: Try 'python3' command
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    set PYTHON_FOUND=1
    goto :run_diagnostic
)

REM Method 4: Check if venv exists
if exist "venv\Scripts\python.exe" (
    set PYTHON_CMD=venv\Scripts\python.exe
    set PYTHON_FOUND=1
    goto :run_diagnostic
)

:python_not_found
echo ERROR: Python not found on this system!
echo.
echo The diagnostic tool requires Python to run.
echo.
echo Please install Python 3.11 or higher from:
echo   https://www.python.org/downloads/
echo.
echo Make sure to check "Add Python to PATH" during installation.
echo.
pause
exit /b 1

:run_diagnostic
echo Found Python: %PYTHON_CMD%
echo.

REM Check if diagnostic script exists
if not exist "diagnose_windows.py" (
    echo ERROR: diagnose_windows.py not found!
    echo.
    echo Make sure you're running this from the License Uploader directory.
    echo.
    pause
    exit /b 1
)

REM Ask user if they want to attempt automatic fixes
echo.
echo Do you want to attempt automatic fixes for detected issues?
echo   [Y] Yes - Run diagnostics and attempt fixes
echo   [N] No  - Just run diagnostics (default)
echo.
choice /C YN /N /M "Your choice (Y/N): "
set CHOICE_RESULT=%errorlevel%

echo.
echo ================================================================
echo Running diagnostics...
echo ================================================================
echo.

if %CHOICE_RESULT% equ 1 (
    REM User chose Yes - run with --fix flag
    %PYTHON_CMD% diagnose_windows.py --fix
) else (
    REM User chose No - run without --fix
    %PYTHON_CMD% diagnose_windows.py
)

set DIAGNOSTIC_EXIT_CODE=%errorlevel%

echo.
echo ================================================================
echo.

if %DIAGNOSTIC_EXIT_CODE% equ 0 (
    echo Diagnostics completed successfully!
) else (
    echo Diagnostics completed with issues detected.
    echo Review the report above for details.
)

echo.
echo A detailed report has been saved to: diagnostic_report.txt
echo.
echo ================================================================
echo.

pause
exit /b %DIAGNOSTIC_EXIT_CODE%
