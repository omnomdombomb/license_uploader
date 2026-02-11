@echo off
REM Build script for Windows - Creates standalone executable

title License Uploader - Build Process

echo ====================================
echo License Uploader - Windows Build
echo ====================================
echo.

REM Detect Python
set PYTHON_CMD=
for %%P in (python py python3) do (
    %%P --version >nul 2>&1
    if !errorlevel! equ 0 (
        set PYTHON_CMD=%%P
        goto :python_found
    )
)

echo ERROR: Python is not installed or not in PATH
echo.
echo Please install Python 3.11+ from https://www.python.org/
echo.
echo Make sure to check "Add Python to PATH" during installation.
pause
exit /b 1

:python_found
echo Using Python command: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        echo.
        echo Troubleshooting:
        echo   1. Run: DIAGNOSE_WINDOWS.bat
        echo   2. Check if venv module is available
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo.
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Install PyInstaller
echo.
echo Installing PyInstaller...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist "build\" rmdir /s /q build
if exist "dist\" rmdir /s /q dist

REM Build executable
echo.
echo Building executable...
echo This may take several minutes...
pyinstaller license_uploader.spec
if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

REM Copy .env.example if .env doesn't exist in dist
if not exist "dist\license_uploader\.env" (
    if exist ".env.example" (
        echo.
        echo Copying .env.example to dist folder...
        copy .env.example dist\license_uploader\.env.example
    )
)

REM Create necessary directories in dist
echo.
echo Creating required directories...
if not exist "dist\license_uploader\logs\" mkdir dist\license_uploader\logs
if not exist "dist\license_uploader\uploads\" mkdir dist\license_uploader\uploads

echo.
echo ====================================
echo Build completed successfully!
echo ====================================
echo.
echo The executable is located in: dist\license_uploader\
echo.
echo Before running:
echo 1. Copy .env.example to .env in the dist\license_uploader\ folder
echo 2. Edit .env with your API keys and configuration
echo 3. Run license_uploader.exe
echo.
pause
