@echo off
REM License Uploader - One-Click Windows Installer
REM Handles complete installation with error detection and recovery

title License Uploader - Installation

setlocal EnableDelayedExpansion

REM Set colors (Windows 10+)
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "RESET=[0m"

echo.
echo %BLUE%================================================================%RESET%
echo %BLUE%   License Uploader - Windows Installer%RESET%
echo %BLUE%================================================================%RESET%
echo.
echo This installer will:
echo   1. Detect Python installation
echo   2. Create virtual environment
echo   3. Install all dependencies
echo   4. Configure environment file
echo   5. Validate installation
echo.

cd /d "%~dp0"

REM Step 1: Detect Python
echo.
echo %BLUE%[1/5] Detecting Python installation...%RESET%
echo.

set PYTHON_CMD=
set PYTHON_VERSION=
set PYTHON_FOUND=0

REM Try different Python commands
for %%P in (python py python3) do (
    %%P --version >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=2" %%V in ('%%P --version 2^>^&1') do set PYTHON_VERSION=%%V
        set PYTHON_CMD=%%P
        set PYTHON_FOUND=1
        goto :python_detected
    )
)

:python_not_found
echo %RED%ERROR: Python not found!%RESET%
echo.
echo Python 3.11 or higher is required to run License Uploader.
echo.
echo %YELLOW%Please install Python:%RESET%
echo   1. Visit: https://www.python.org/downloads/windows/
echo   2. Download: Python 3.11 or higher (64-bit)
echo   3. Run installer and CHECK "Add Python to PATH"
echo   4. Restart this installer
echo.
pause
exit /b 1

:python_detected
echo %GREEN%✓ Found: Python %PYTHON_VERSION%!%RESET%
echo   Command: %PYTHON_CMD%

REM Check Python version
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if %MAJOR% LSS 3 (
    echo %RED%ERROR: Python version too old!%RESET%
    echo   Current: %PYTHON_VERSION%
    echo   Required: 3.11 or higher
    echo.
    echo Please upgrade Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

if %MAJOR% EQU 3 if %MINOR% LSS 11 (
    echo %YELLOW%WARNING: Python %PYTHON_VERSION% detected.%RESET%
    echo   Recommended: Python 3.11 or higher
    echo   Current version may work but is not fully tested.
    echo.
    choice /C YN /M "Continue anyway (Y/N)?"
    if errorlevel 2 exit /b 1
)

REM Step 2: Create Virtual Environment
echo.
echo %BLUE%[2/5] Creating virtual environment...%RESET%
echo.

if exist "venv\" (
    echo Virtual environment directory already exists.
    echo.
    choice /C YN /M "Delete and recreate (Y/N)?"
    if errorlevel 2 (
        echo Skipping virtual environment creation.
        goto :install_deps
    )
    echo Removing old virtual environment...
    rmdir /s /q venv 2>nul
)

echo Creating virtual environment...
%PYTHON_CMD% -m venv venv

if errorlevel 1 (
    echo %RED%ERROR: Failed to create virtual environment!%RESET%
    echo.
    echo Possible causes:
    echo   - venv module not available
    echo   - Insufficient permissions
    echo   - Disk space full
    echo.
    echo Try running as Administrator or check Python installation.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo %RED%ERROR: Virtual environment created but python.exe not found!%RESET%
    pause
    exit /b 1
)

echo %GREEN%✓ Virtual environment created successfully!%RESET%

REM Step 3: Install Dependencies
:install_deps
echo.
echo %BLUE%[3/5] Installing dependencies...%RESET%
echo.

REM Check PowerShell execution policy
echo Checking PowerShell execution policy...
powershell -Command "Get-ExecutionPolicy -Scope CurrentUser" | findstr /I "Restricted AllSigned" >nul
if %errorlevel% equ 0 (
    echo %YELLOW%PowerShell execution policy is restrictive.%RESET%
    echo Setting policy to RemoteSigned for current user...
    powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"
    if errorlevel 1 (
        echo %YELLOW%Warning: Could not change execution policy.%RESET%
        echo Using fallback activation method...
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo %RED%ERROR: Failed to activate virtual environment!%RESET%
    echo Attempting to continue with direct path...
    set VENV_PYTHON=venv\Scripts\python.exe
) else (
    echo %GREEN%✓ Virtual environment activated!%RESET%
    set VENV_PYTHON=python
)

REM Upgrade pip first
echo.
echo Upgrading pip (this may take a moment)...
%VENV_PYTHON% -m pip install --upgrade pip --quiet

if errorlevel 1 (
    echo %YELLOW%Warning: pip upgrade failed, continuing anyway...%RESET%
)

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo %RED%ERROR: requirements.txt not found!%RESET%
    echo.
    echo Make sure you're running this from the License Uploader directory.
    pause
    exit /b 1
)

REM Install requirements
echo.
echo Installing Python packages (this may take 2-5 minutes)...
echo Please be patient, downloading and installing dependencies...
echo.

%VENV_PYTHON% -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo %RED%ERROR: Failed to install dependencies!%RESET%
    echo.
    echo Possible causes:
    echo   - Network connection issues
    echo   - Missing Visual C++ Build Tools (for cryptography package)
    echo   - Antivirus blocking pip
    echo.
    echo Troubleshooting:
    echo   1. Check your internet connection
    echo   2. Temporarily disable antivirus
    echo   3. Install Visual C++ Build Tools:
    echo      https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo   4. Try running: DIAGNOSE_WINDOWS.bat
    echo.
    pause
    exit /b 1
)

echo.
echo %GREEN%✓ All dependencies installed successfully!%RESET%

REM Step 4: Configure Environment
echo.
echo %BLUE%[4/5] Configuring environment...%RESET%
echo.

if exist ".env" (
    echo .env file already exists.
    echo.
    choice /C YN /M "Keep existing configuration (Y/N)?"
    if errorlevel 2 (
        echo Creating new .env from template...
        copy /Y .env.example .env >nul
    ) else (
        echo Keeping existing .env file.
    )
) else (
    if exist ".env.example" (
        echo Creating .env from template...
        copy .env.example .env >nul
        echo %GREEN%✓ Created .env file!%RESET%
        echo.
        echo %YELLOW%IMPORTANT: You must edit .env and add your API keys!%RESET%
        echo.
        echo Required configuration:
        echo   - ALMA_API_KEY: Your Alma API key
        echo   - LITELLM_API_KEY: Your LiteLLM API key
        echo   - SECRET_KEY: Generate with: python -c "import secrets; print(secrets.token_hex(32))"
        echo.
        choice /C YN /M "Open .env file in Notepad now (Y/N)?"
        if errorlevel 2 (
            echo.
            echo Remember to edit .env before running the application!
        ) else (
            start notepad .env
            echo.
            echo %YELLOW%Waiting for you to finish editing .env...%RESET%
            pause
        )
    ) else (
        echo %YELLOW%Warning: .env.example not found!%RESET%
        echo You'll need to create .env manually.
    )
)

REM Step 5: Validate Installation
echo.
echo %BLUE%[5/5] Validating installation...%RESET%
echo.

echo Running diagnostics...
echo.

REM Run diagnostic tool
%VENV_PYTHON% diagnose_windows.py

set DIAG_EXIT_CODE=!errorlevel!

echo.

if %DIAG_EXIT_CODE% equ 0 (
    echo %GREEN%================================================================%RESET%
    echo %GREEN%   ✓ INSTALLATION SUCCESSFUL!%RESET%
    echo %GREEN%================================================================%RESET%
    echo.
    echo License Uploader is ready to use!
    echo.
    echo %BLUE%Next steps:%RESET%
    echo   1. Edit .env file with your API keys (if you haven't already)
    echo   2. Double-click START_HERE.bat to launch the application
    echo   3. Your browser will open automatically
    echo   4. Start uploading license documents!
    echo.
    echo %BLUE%Documentation:%RESET%
    echo   - USER_GUIDE.md: How to use the application
    echo   - TROUBLESHOOTING_GUIDE.md: If you encounter problems
    echo   - GET_STARTED.md: Quick start guide
    echo.
) else (
    echo %YELLOW%================================================================%RESET%
    echo %YELLOW%   ⚠ INSTALLATION COMPLETED WITH WARNINGS%RESET%
    echo %YELLOW%================================================================%RESET%
    echo.
    echo Installation finished but some issues were detected.
    echo.
    echo Review the diagnostic report above.
    echo.
    echo The application may still work, but you should:
    echo   1. Review warnings in diagnostic_report.txt
    echo   2. Fix any critical issues
    echo   3. Run DIAGNOSE_WINDOWS.bat --fix to attempt automatic fixes
    echo.
)

echo.
echo Installation log saved to: diagnostic_report.txt
echo.
pause
exit /b 0
