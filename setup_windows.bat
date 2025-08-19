@echo off
setlocal enabledelayedexpansion

REM ==============================================================================
REM UE5 Documentation Scraper - Windows Setup Script
REM This script sets up the complete environment for the UE5 documentation scraper
REM ==============================================================================

echo.
echo  ██╗   ██╗███████╗███████╗    ██████╗  ██████╗  ██████╗███████╗
echo  ██║   ██║██╔════╝██╔════╝    ██╔══██╗██╔═══██╗██╔════╝██╔════╝
echo  ██║   ██║█████╗  ███████╗    ██║  ██║██║   ██║██║     ███████╗
echo  ██║   ██║██╔══╝  ╚════██║    ██║  ██║██║   ██║██║     ╚════██║
echo  ╚██████╔╝███████╗███████║    ██████╔╝╚██████╔╝╚██████╗███████║
echo   ╚═════╝ ╚══════╝╚══════╝    ╚═════╝  ╚═════╝  ╚═════╝╚══════╝
echo.
echo               SCRAPER - Windows Setup Script
echo ================================================================
echo.

REM Set variables and error handling
set "SCRIPT_DIR=%~dp0"
set "LOG_FILE=%SCRIPT_DIR%setup.log"
set "REQUIREMENTS_FILE=%SCRIPT_DIR%requirements-windows.txt"
set "VENV_DIR=%SCRIPT_DIR%venv"
set "SETUP_FAILED=0"

REM Initialize setup log
echo [%date% %time%] Starting UE5 Documentation Scraper Setup > "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"

REM Change to script directory
cd /d "%SCRIPT_DIR%"
if errorlevel 1 (
    echo ERROR: Failed to change to script directory
    echo Script directory: %SCRIPT_DIR%
    pause
    exit /b 1
)

REM Step 1: Check Python installation and version
echo [1/7] Checking Python installation...
echo [%date% %time%] Checking Python installation >> "%LOG_FILE%"

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo REQUIRED ACTION:
    echo 1. Download Python 3.8 or later from https://python.org
    echo 2. During installation, check "Add Python to PATH"
    echo 3. Restart Command Prompt and run this script again
    echo [%date% %time%] ERROR: Python not found >> "%LOG_FILE%"
    pause
    exit /b 1
)

echo Python found! Checking version...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo Python version: %PYTHON_VERSION%
echo [%date% %time%] Python version: %PYTHON_VERSION% >> "%LOG_FILE%"

REM Validate Python version (basic check for 3.x)
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Python version may be too old. Python 3.8+ is recommended.
    echo [%date% %time%] WARNING: Python version may be too old >> "%LOG_FILE%"
)

REM Step 2: Check for required external tools
echo.
echo [2/7] Checking for external tools...
echo [%date% %time%] Checking for external tools >> "%LOG_FILE%"

REM Check for Firefox
set "FIREFOX_FOUND=0"
if exist "C:\Program Files\Mozilla Firefox\firefox.exe" (
    echo Firefox found at: C:\Program Files\Mozilla Firefox\firefox.exe
    echo [%date% %time%] Firefox found at: C:\Program Files\Mozilla Firefox\firefox.exe >> "%LOG_FILE%"
    set "FIREFOX_FOUND=1"
) else if exist "C:\Program Files (x86)\Mozilla Firefox\firefox.exe" (
    echo Firefox found at: C:\Program Files (x86)\Mozilla Firefox\firefox.exe
    echo [%date% %time%] Firefox found at: C:\Program Files (x86)\Mozilla Firefox\firefox.exe >> "%LOG_FILE%"
    set "FIREFOX_FOUND=1"
) else (
    echo WARNING: Firefox not found in standard locations
    echo Please install Firefox from https://firefox.com
    echo The scraper requires a web browser to work properly
    echo [%date% %time%] WARNING: Firefox not found >> "%LOG_FILE%"
)

REM Check for Google Chrome as alternative
if !FIREFOX_FOUND! equ 0 (
    if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
        echo Google Chrome found - can be used as alternative browser
        echo [%date% %time%] Google Chrome found as alternative >> "%LOG_FILE%"
    ) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
        echo Google Chrome found - can be used as alternative browser
        echo [%date% %time%] Google Chrome found as alternative >> "%LOG_FILE%"
    )
)

REM Step 3: Check requirements file
echo.
echo [3/7] Checking requirements file...
echo [%date% %time%] Checking requirements file >> "%LOG_FILE%"

if not exist "%REQUIREMENTS_FILE%" (
    echo ERROR: requirements-windows.txt not found
    echo Expected location: %REQUIREMENTS_FILE%
    echo [%date% %time%] ERROR: requirements-windows.txt not found >> "%LOG_FILE%"
    set "SETUP_FAILED=1"
    goto :cleanup
)

echo Requirements file found: %REQUIREMENTS_FILE%

REM Step 4: Handle existing virtual environment
echo.
echo [4/7] Checking virtual environment...
echo [%date% %time%] Checking virtual environment >> "%LOG_FILE%"

if exist "%VENV_DIR%" (
    echo Existing virtual environment found
    choice /c YN /m "Remove existing virtual environment and create new one? (Y/N)"
    if errorlevel 2 (
        echo Keeping existing virtual environment
        echo [%date% %time%] Keeping existing virtual environment >> "%LOG_FILE%"
        goto :activate_venv
    ) else (
        echo Removing existing virtual environment...
        echo [%date% %time%] Removing existing virtual environment >> "%LOG_FILE%"
        rmdir /s /q "%VENV_DIR%"
        if exist "%VENV_DIR%" (
            echo ERROR: Failed to remove existing virtual environment
            echo [%date% %time%] ERROR: Failed to remove existing virtual environment >> "%LOG_FILE%"
            set "SETUP_FAILED=1"
            goto :cleanup
        )
    )
)

REM Step 5: Create virtual environment
echo.
echo [5/7] Creating Python virtual environment...
echo [%date% %time%] Creating virtual environment >> "%LOG_FILE%"

python -m venv "%VENV_DIR%"
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo This may indicate:
    echo   - Insufficient disk space
    echo   - Permission issues
    echo   - Python installation problems
    echo [%date% %time%] ERROR: Failed to create virtual environment >> "%LOG_FILE%"
    set "SETUP_FAILED=1"
    goto :cleanup
)

echo Virtual environment created successfully

:activate_venv
REM Step 6: Activate virtual environment and upgrade pip
echo.
echo [6/7] Activating virtual environment and upgrading pip...
echo [%date% %time%] Activating virtual environment >> "%LOG_FILE%"

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo [%date% %time%] ERROR: Failed to activate virtual environment >> "%LOG_FILE%"
    set "SETUP_FAILED=1"
    goto :cleanup
)

echo Upgrading pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing with current version
    echo [%date% %time%] WARNING: Failed to upgrade pip >> "%LOG_FILE%"
)

REM Display pip version
for /f "tokens=2" %%i in ('pip --version 2^>^&1') do set "PIP_VERSION=%%i"
echo Pip version: %PIP_VERSION%

REM Step 7: Install dependencies
echo.
echo [7/7] Installing Python dependencies...
echo [%date% %time%] Installing dependencies >> "%LOG_FILE%"

echo Installing from: %REQUIREMENTS_FILE%
pip install -r "%REQUIREMENTS_FILE%"
set "PIP_EXIT_CODE=%errorlevel%"

if %PIP_EXIT_CODE% neq 0 (
    echo ERROR: Failed to install dependencies (Exit code: %PIP_EXIT_CODE%)
    echo.
    echo TROUBLESHOOTING:
    echo 1. Check your internet connection
    echo 2. Try running as Administrator
    echo 3. Check if antivirus is blocking the installation
    echo 4. Manually install packages: pip install requests beautifulsoup4 selenium
    echo [%date% %time%] ERROR: Failed to install dependencies >> "%LOG_FILE%"
    set "SETUP_FAILED=1"
    goto :cleanup
)

echo Dependencies installed successfully

REM Optional: Run setup tests if available
echo.
echo Running installation validation...
echo [%date% %time%] Running installation validation >> "%LOG_FILE%"

if exist "test_setup.py" (
    python test_setup.py
    set "TEST_EXIT_CODE=%errorlevel%"
    if !TEST_EXIT_CODE! equ 0 (
        echo Installation validation: PASSED
        echo [%date% %time%] Installation validation: PASSED >> "%LOG_FILE%"
    ) else (
        echo Installation validation: FAILED (Exit code: !TEST_EXIT_CODE!)
        echo [%date% %time%] Installation validation: FAILED >> "%LOG_FILE%"
        echo WARNING: Some tests failed. The setup may still work.
    )
) else (
    echo test_setup.py not found, skipping validation tests
    echo [%date% %time%] test_setup.py not found >> "%LOG_FILE%"
)

:cleanup
REM Display final results
echo.
echo ================================================================
if %SETUP_FAILED% equ 0 (
    echo                    SETUP COMPLETED SUCCESSFULLY!
    echo [%date% %time%] Setup completed successfully >> "%LOG_FILE%"
) else (
    echo                    SETUP FAILED - SEE ERRORS ABOVE
    echo [%date% %time%] Setup failed >> "%LOG_FILE%"
)
echo ================================================================
echo.

if %SETUP_FAILED% equ 0 (
    echo NEXT STEPS:
    echo.
    echo To run the UE5 Documentation Scraper:
    echo   Option 1 - Use the convenience script:
    echo     Double-click: run_scraper.bat
    echo.
    echo   Option 2 - Manual command line:
    echo     1. Open Command Prompt in this directory
    echo     2. Run: %VENV_DIR%\Scripts\activate.bat
    echo     3. Run: python ue5_docs_scraper.py
    echo.
    echo To test the installation:
    echo     Double-click: test_windows.bat
    echo.
    echo Log file: %LOG_FILE%
) else (
    echo Please review the errors above and the log file: %LOG_FILE%
    echo You may need to:
    echo   - Check internet connection
    echo   - Run as Administrator
    echo   - Install missing system dependencies
    echo   - Update Python version
)

echo.
pause
exit /b %SETUP_FAILED%