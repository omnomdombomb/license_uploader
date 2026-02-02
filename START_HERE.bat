@echo off
REM License Uploader - Windows Launcher
REM Double-click this file to start the application

title License Uploader

echo.
echo ========================================
echo    License Uploader
echo    Starting Application...
echo ========================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run installation first:
    echo   1. Open Command Prompt
    echo   2. Navigate to this folder
    echo   3. Run: python -m venv venv
    echo   4. Run: venv\Scripts\activate
    echo   5. Run: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Start the GUI launcher
venv\Scripts\python.exe start_license_uploader_gui.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start application
    echo.
    pause
)
