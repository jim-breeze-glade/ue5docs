@echo off
setlocal enabledelayedexpansion

REM ==============================================================================
REM UE5 Documentation Scraper - Windows 11 Compatibility Test
REM This script runs comprehensive compatibility checks for Windows 11
REM ==============================================================================

echo.
echo  ██╗    ██╗██╗███╗   ██╗██████╗  ██████╗ ██╗    ██╗███████╗    ██╗ ██╗
echo  ██║    ██║██║████╗  ██║██╔══██╗██╔═══██╗██║    ██║██╔════╝    ╚═╝███║
echo  ██║ █╗ ██║██║██╔██╗ ██║██║  ██║██║   ██║██║ █╗ ██║███████╗       ╚██║
echo  ██║███╗██║██║██║╚██╗██║██║  ██║██║   ██║██║███╗██║╚════██║        ██║
echo  ╚███╔███╔╝██║██║ ╚████║██████╔╝╚██████╔╝╚███╔███╔╝███████║        ██║
echo   ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝        ╚═╝
echo.
echo              COMPATIBILITY CHECKER - Windows 11
echo ================================================================
echo.

REM Set variables
set "SCRIPT_DIR=%~dp0"
set "LOG_FILE=%SCRIPT_DIR%windows11_compatibility.log"
set "VENV_DIR=%SCRIPT_DIR%venv"

REM Initialize log
echo [%date% %time%] Starting Windows 11 Compatibility Check > "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"

REM Change to script directory
cd /d "%SCRIPT_DIR%"

echo [1/6] Checking Windows version...
echo [%date% %time%] Checking Windows version >> "%LOG_FILE%"

REM Check Windows version
for /f "tokens=4-7 delims=[.] " %%i in ('ver') do (
    set "WINDOWS_VERSION=%%i.%%j.%%k"
)
echo Windows version: %WINDOWS_VERSION%
echo [%date% %time%] Windows version: %WINDOWS_VERSION% >> "%LOG_FILE%"

REM Check if Windows 11 (build 22000+)
for /f "tokens=3" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v CurrentBuild 2^>nul') do set "BUILD_NUMBER=%%a"
if defined BUILD_NUMBER (
    echo Windows build: %BUILD_NUMBER%
    echo [%date% %time%] Windows build: %BUILD_NUMBER% >> "%LOG_FILE%"
    
    if %BUILD_NUMBER% GEQ 22000 (
        echo ✓ Windows 11 detected
        echo [%date% %time%] Windows 11 detected >> "%LOG_FILE%"
    ) else (
        echo ! Windows 10 detected - Windows 11 recommended
        echo [%date% %time%] Windows 10 detected >> "%LOG_FILE%"
    )
) else (
    echo ! Could not determine Windows build number
    echo [%date% %time%] Could not determine Windows build >> "%LOG_FILE%"
)

echo.
echo [2/6] Checking Python installation...
echo [%date% %time%] Checking Python installation >> "%LOG_FILE%"

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python is not installed or not in PATH
    echo [%date% %time%] ERROR: Python not found >> "%LOG_FILE%"
    goto :error_python
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo ✓ Python found: %PYTHON_VERSION%
    echo [%date% %time%] Python found: %PYTHON_VERSION% >> "%LOG_FILE%"
)

REM Check Python version (basic check)
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ! Python version may be too old (3.8+ required)
    echo [%date% %time%] WARNING: Python version too old >> "%LOG_FILE%"
)

echo.
echo [3/6] Checking Firefox installation...
echo [%date% %time%] Checking Firefox installation >> "%LOG_FILE%"

set "FIREFOX_FOUND=0"
if exist "C:\Program Files\Mozilla Firefox\firefox.exe" (
    echo ✓ Firefox found at: C:\Program Files\Mozilla Firefox\firefox.exe
    echo [%date% %time%] Firefox found (64-bit) >> "%LOG_FILE%"
    set "FIREFOX_FOUND=1"
    set "FIREFOX_PATH=C:\Program Files\Mozilla Firefox\firefox.exe"
) else if exist "C:\Program Files (x86)\Mozilla Firefox\firefox.exe" (
    echo ✓ Firefox found at: C:\Program Files (x86)\Mozilla Firefox\firefox.exe
    echo [%date% %time%] Firefox found (32-bit) >> "%LOG_FILE%"
    set "FIREFOX_FOUND=1"
    set "FIREFOX_PATH=C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
) else (
    echo ✗ Firefox not found in standard locations
    echo [%date% %time%] ERROR: Firefox not found >> "%LOG_FILE%"
)

REM Get Firefox version if found
if !FIREFOX_FOUND! equ 1 (
    for /f "tokens=3" %%v in ('"%FIREFOX_PATH%" --version 2^>^&1') do (
        echo   Firefox version: %%v
        echo [%date% %time%] Firefox version: %%v >> "%LOG_FILE%"
    )
)

echo.
echo [4/6] Checking virtual environment...
echo [%date% %time%] Checking virtual environment >> "%LOG_FILE%"

if exist "%VENV_DIR%" (
    echo ✓ Virtual environment found
    echo [%date% %time%] Virtual environment found >> "%LOG_FILE%"
    
    REM Activate and check dependencies
    call "%VENV_DIR%\Scripts\activate.bat"
    if errorlevel 1 (
        echo ✗ Could not activate virtual environment
        echo [%date% %time%] ERROR: Could not activate venv >> "%LOG_FILE%"
    ) else (
        echo ✓ Virtual environment activated
        echo [%date% %time%] Virtual environment activated >> "%LOG_FILE%"
        
        REM Check key dependencies
        echo   Checking dependencies...
        python -c "import requests, bs4, selenium, fake_useragent" >nul 2>&1
        if errorlevel 1 (
            echo ✗ Some required dependencies are missing
            echo [%date% %time%] ERROR: Dependencies missing >> "%LOG_FILE%"
        ) else (
            echo ✓ Core dependencies found
            echo [%date% %time%] Core dependencies found >> "%LOG_FILE%"
        )
    )
) else (
    echo ! Virtual environment not found
    echo [%date% %time%] WARNING: Virtual environment not found >> "%LOG_FILE%"
    echo   Run setup_windows.bat first to create the environment
)

echo.
echo [5/6] Running comprehensive compatibility check...
echo [%date% %time%] Running comprehensive compatibility check >> "%LOG_FILE%"

if exist "windows11_compatibility.py" (
    python windows11_compatibility.py
    set "COMPAT_EXIT_CODE=%errorlevel%"
    if !COMPAT_EXIT_CODE! equ 0 (
        echo ✓ Comprehensive compatibility check passed
        echo [%date% %time%] Comprehensive compatibility check passed >> "%LOG_FILE%"
    ) else (
        echo ! Comprehensive compatibility check found issues
        echo [%date% %time%] Comprehensive compatibility check found issues >> "%LOG_FILE%"
    )
) else (
    echo ! windows11_compatibility.py not found, skipping detailed check
    echo [%date% %time%] Detailed compatibility checker not found >> "%LOG_FILE%"
)

echo.
echo [6/6] Testing basic scraper functionality...
echo [%date% %time%] Testing basic scraper functionality >> "%LOG_FILE%"

if exist "test_setup.py" (
    python test_setup.py
    set "TEST_EXIT_CODE=%errorlevel%"
    if !TEST_EXIT_CODE! equ 0 (
        echo ✓ Basic functionality test passed
        echo [%date% %time%] Basic functionality test passed >> "%LOG_FILE%"
    ) else (
        echo ✗ Basic functionality test failed
        echo [%date% %time%] Basic functionality test failed >> "%LOG_FILE%"
    )
) else (
    echo ! test_setup.py not found, skipping functionality test
    echo [%date% %time%] Functionality test script not found >> "%LOG_FILE%"
)

echo.
echo ================================================================
echo                    COMPATIBILITY CHECK COMPLETE
echo ================================================================
echo [%date% %time%] Compatibility check complete >> "%LOG_FILE%"

REM Summary
echo.
echo SUMMARY:
if !FIREFOX_FOUND! equ 0 (
    echo ✗ Firefox installation needs attention
)
if exist "%VENV_DIR%" (
    echo ✓ Virtual environment ready
) else (
    echo ! Virtual environment needs setup
)

echo.
echo NEXT STEPS:
if !FIREFOX_FOUND! equ 0 (
    echo 1. Install Firefox from https://firefox.com
)
if not exist "%VENV_DIR%" (
    echo 2. Run setup_windows.bat to create virtual environment
)
echo 3. Check the generated compatibility report for detailed information
echo 4. If all checks pass, run: run_scraper.bat

echo.
echo Log file: %LOG_FILE%
if exist "windows11_compatibility_report.txt" (
    echo Detailed report: windows11_compatibility_report.txt
)

echo.
pause
exit /b 0

:error_python
echo.
echo ERROR: Python is required but not found
echo.
echo REQUIRED ACTION:
echo 1. Download Python 3.8 or later from https://python.org
echo 2. During installation, check "Add Python to PATH"
echo 3. Restart Command Prompt and run this script again
echo.
pause
exit /b 1