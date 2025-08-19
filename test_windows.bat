@echo off
setlocal enabledelayedexpansion

REM ==============================================================================
REM UE5 Documentation Scraper - Test Script
REM This script runs comprehensive tests to validate the installation and setup
REM ==============================================================================

echo.
echo  ██╗   ██╗███████╗███████╗    ████████╗███████╗███████╗████████╗
echo  ██║   ██║██╔════╝██╔════╝    ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝
echo  ██║   ██║█████╗  ███████╗       ██║   █████╗  ███████╗   ██║   
echo  ██║   ██║██╔══╝  ╚════██║       ██║   ██╔══╝  ╚════██║   ██║   
echo  ╚██████╔╝███████╗███████║       ██║   ███████╗███████║   ██║   
echo   ╚═════╝ ╚══════╝╚══════╝       ╚═╝   ╚══════╝╚══════╝   ╚═╝   
echo.
echo                    TESTING INSTALLATION
echo ================================================================
echo.

REM Set error handling and variables
set "SCRIPT_DIR=%~dp0"
set "VENV_ACTIVATE=%SCRIPT_DIR%venv\Scripts\activate.bat"
set "LOG_FILE=%SCRIPT_DIR%test_results.log"
set "TESTS_PASSED=0"
set "TESTS_FAILED=0"
set "TOTAL_EXIT_CODE=0"

REM Initialize test log
echo [%date% %time%] Starting UE5 Documentation Scraper Tests > "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"

REM Change to script directory
cd /d "%SCRIPT_DIR%"
if errorlevel 1 (
    echo ERROR: Failed to change to script directory
    echo Script directory: %SCRIPT_DIR%
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "%VENV_ACTIVATE%" (
    echo ERROR: Virtual environment not found!
    echo Expected location: %VENV_ACTIVATE%
    echo.
    echo Please run setup_windows.bat first to set up the environment.
    echo [%date% %time%] ERROR: Virtual environment not found >> "%LOG_FILE%"
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_ACTIVATE%"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo [%date% %time%] ERROR: Failed to activate virtual environment >> "%LOG_FILE%"
    pause
    exit /b 1
)

REM Verify Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not available in virtual environment
    echo [%date% %time%] ERROR: Python not available >> "%LOG_FILE%"
    pause
    exit /b 1
)

echo Virtual environment activated successfully
echo Python version:
python --version
echo.

REM Test 1: Check if test_setup.py exists and run it
echo [1/3] Running installation tests...
echo [%date% %time%] Starting installation tests >> "%LOG_FILE%"

if not exist "test_setup.py" (
    echo WARNING: test_setup.py not found, skipping installation tests
    echo [%date% %time%] WARNING: test_setup.py not found >> "%LOG_FILE%"
) else (
    python test_setup.py
    set "SETUP_TEST_EXIT=%errorlevel%"
    if !SETUP_TEST_EXIT! equ 0 (
        echo Installation tests: PASSED
        echo [%date% %time%] Installation tests: PASSED >> "%LOG_FILE%"
        set /a TESTS_PASSED+=1
    ) else (
        echo Installation tests: FAILED (Exit code: !SETUP_TEST_EXIT!)
        echo [%date% %time%] Installation tests: FAILED (Exit code: !SETUP_TEST_EXIT!) >> "%LOG_FILE%"
        set /a TESTS_FAILED+=1
        set "TOTAL_EXIT_CODE=1"
    )
)

echo.

REM Test 2: Check if test_scraper.py exists and run it
echo [2/3] Running scraper functionality tests...
echo [%date% %time%] Starting scraper functionality tests >> "%LOG_FILE%"

if not exist "test_scraper.py" (
    echo WARNING: test_scraper.py not found, skipping scraper tests
    echo [%date% %time%] WARNING: test_scraper.py not found >> "%LOG_FILE%"
) else (
    python test_scraper.py
    set "SCRAPER_TEST_EXIT=%errorlevel%"
    if !SCRAPER_TEST_EXIT! equ 0 (
        echo Scraper functionality tests: PASSED
        echo [%date% %time%] Scraper functionality tests: PASSED >> "%LOG_FILE%"
        set /a TESTS_PASSED+=1
    ) else (
        echo Scraper functionality tests: FAILED (Exit code: !SCRAPER_TEST_EXIT!)
        echo [%date% %time%] Scraper functionality tests: FAILED (Exit code: !SCRAPER_TEST_EXIT!) >> "%LOG_FILE%"
        set /a TESTS_FAILED+=1
        set "TOTAL_EXIT_CODE=1"
    )
)

echo.

REM Test 3: Basic dependency validation
echo [3/3] Running dependency validation...
echo [%date% %time%] Starting dependency validation >> "%LOG_FILE%"

echo Checking required Python packages...
set "DEPS_OK=1"

REM Check individual dependencies
for %%d in (requests beautifulsoup4 selenium lxml aiohttp) do (
    python -c "import %%d" >nul 2>&1
    if errorlevel 1 (
        echo   - %%d: MISSING
        echo [%date% %time%] Dependency %%d: MISSING >> "%LOG_FILE%"
        set "DEPS_OK=0"
    ) else (
        echo   - %%d: OK
    )
)

if !DEPS_OK! equ 1 (
    echo Dependency validation: PASSED
    echo [%date% %time%] Dependency validation: PASSED >> "%LOG_FILE%"
    set /a TESTS_PASSED+=1
) else (
    echo Dependency validation: FAILED
    echo [%date% %time%] Dependency validation: FAILED >> "%LOG_FILE%"
    set /a TESTS_FAILED+=1
    set "TOTAL_EXIT_CODE=1"
)

REM Display final results
echo.
echo ================================================================
if %TOTAL_EXIT_CODE% equ 0 (
    echo                   TESTING COMPLETED SUCCESSFULLY
) else (
    echo                   TESTING COMPLETED WITH FAILURES
)
echo ================================================================
echo.
echo Test Summary:
echo   Tests Passed: !TESTS_PASSED!
echo   Tests Failed: !TESTS_FAILED!
set /a TOTAL_TESTS=!TESTS_PASSED!+!TESTS_FAILED!
echo   Total Tests:  !TOTAL_TESTS!
echo.
echo Log file: %LOG_FILE%
echo.

REM Log final summary
echo [%date% %time%] Test Summary: !TESTS_PASSED! passed, !TESTS_FAILED! failed >> "%LOG_FILE%"
echo [%date% %time%] Testing completed with exit code: %TOTAL_EXIT_CODE% >> "%LOG_FILE%"

if %TOTAL_EXIT_CODE% neq 0 (
    echo RECOMMENDATION: Run setup_windows.bat to fix any missing dependencies
    echo.
)

pause
exit /b %TOTAL_EXIT_CODE%