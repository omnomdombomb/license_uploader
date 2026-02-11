@echo off
REM License Uploader - Windows Launcher
REM Double-click this file to start the application
REM
REM This script is now a simple wrapper around the unified Python launcher

title License Uploader

cd /d "%~dp0"

REM Try to find Python
if exist "venv\Scripts\python.exe" (
    REM Use virtual environment Python
    venv\Scripts\python.exe launcher.py
) else (
    REM Try system Python as fallback
    python launcher.py
    if errorlevel 1 (
        REM Try py launcher
        py launcher.py
        if errorlevel 1 (
            echo.
            echo ERROR: Could not find Python!
            echo Please install Python or run INSTALL_WINDOWS.bat first.
            pause
            exit /b 1
        )
    )
)

REM Pause if launched by double-click (not from command line)
if "%1"=="" pause
