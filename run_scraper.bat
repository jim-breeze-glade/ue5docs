@echo off
setlocal enabledelayedexpansion

REM ==============================================================================
REM UE5 Documentation Scraper - Run Script
REM This script activates the virtual environment and runs the UE5 docs scraper
REM ==============================================================================

echo.
echo  ██╗   ██╗███████╗███████╗    ██████╗  ██████╗  ██████╗███████╗
echo  ██║   ██║██╔════╝██╔════╝    ██╔══██╗██╔═══██╗██╔════╝██╔════╝
echo  ██║   ██║█████╗  ███████╗    ██║  ██║██║   ██║██║     ███████╗
echo  ██║   ██║██╔══╝  ╚════██║    ██║  ██║██║   ██║██║     ╚════██║
echo  ╚██████╔╝███████╗███████║    ██████╔╝╚██████╔╝╚██████╗███████║
echo   ╚═════╝ ╚══════╝╚══════╝    ╚═════╝  ╚═════╝  ╚═════╝╚══════╝
echo.
echo                      SCRAPER - Starting...
echo ================================================================
echo.

REM Set error handling
set "SCRIPT_DIR=%~dp0"
set "VENV_ACTIVATE=%SCRIPT_DIR%venv\Scripts\activate.bat"
set "MAIN_SCRIPT=%SCRIPT_DIR%ue5_docs_scraper.py"
set "LOG_FILE=%SCRIPT_DIR%scraper.log"

REM Log start time
echo [%date% %time%] Starting UE5 Documentation Scraper >> "%LOG_FILE%"

REM Check if script is running from correct directory
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
    echo Please run setup_windows.bat first to set up the scraper.
    echo [%date% %time%] ERROR: Virtual environment not found >> "%LOG_FILE%"
    pause
    exit /b 1
)

REM Check if main script exists
if not exist "%MAIN_SCRIPT%" (
    echo ERROR: ue5_docs_scraper.py not found!
    echo Expected location: %MAIN_SCRIPT%
    echo Please ensure all files are in the correct directory.
    echo [%date% %time%] ERROR: Main script not found >> "%LOG_FILE%"
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

REM Verify Python is available in virtual environment
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not available in virtual environment
    echo [%date% %time%] ERROR: Python not available in virtual environment >> "%LOG_FILE%"
    pause
    exit /b 1
)

REM Check if required dependencies are installed
echo Checking dependencies...
python -c "import requests, beautifulsoup4, selenium, lxml, aiohttp" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Some dependencies may be missing
    echo Run setup_windows.bat to reinstall dependencies
    echo [%date% %time%] WARNING: Dependencies check failed >> "%LOG_FILE%"
)

REM Run the scraper
echo.
echo Starting UE5 Documentation Scraper...
echo Press Ctrl+C to stop the scraper at any time.
echo Script location: %MAIN_SCRIPT%
echo Log file: %LOG_FILE%
echo.

python "%MAIN_SCRIPT%"
set "SCRAPER_EXIT_CODE=%errorlevel%"

REM Log completion status
if %SCRAPER_EXIT_CODE% equ 0 (
    echo [%date% %time%] Scraper completed successfully >> "%LOG_FILE%"
) else (
    echo [%date% %time%] Scraper exited with error code %SCRAPER_EXIT_CODE% >> "%LOG_FILE%"
)

REM Display results
echo.
echo ================================================================
if %SCRAPER_EXIT_CODE% equ 0 (
    echo                   SCRAPING COMPLETED SUCCESSFULLY
) else (
    echo                   SCRAPING COMPLETED WITH ERRORS
    echo                   Exit Code: %SCRAPER_EXIT_CODE%
)
echo ================================================================
echo.
echo Output locations:
echo - Downloaded PDFs: ue5_docs folder
echo - Detailed logs: scraper.log
echo - Script directory: %SCRIPT_DIR%
echo.

REM Check if output directory exists and show file count
if exist "ue5_docs" (
    for /f %%i in ('dir /b /a-d "ue5_docs\*.pdf" 2^>nul ^| find /c /v ""') do set "PDF_COUNT=%%i"
    if defined PDF_COUNT (
        echo Downloaded PDF files: !PDF_COUNT!
    ) else (
        echo Downloaded PDF files: 0
    )
) else (
    echo Note: ue5_docs folder not found - no PDFs were downloaded
)

echo.
pause
exit /b %SCRAPER_EXIT_CODE%