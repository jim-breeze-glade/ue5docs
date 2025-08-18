@echo off
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

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/6] Python found! Checking version...
python --version

REM Check if Firefox is installed
echo.
echo [2/6] Checking for Firefox installation...
if exist "C:\Program Files\Mozilla Firefox\firefox.exe" (
    echo Firefox found at: C:\Program Files\Mozilla Firefox\firefox.exe
) else if exist "C:\Program Files (x86)\Mozilla Firefox\firefox.exe" (
    echo Firefox found at: C:\Program Files (x86)Mozilla Firefox\firefox.exe
) else (
    echo WARNING: Firefox not found in standard locations
    echo Please install Firefox from https://firefox.com
    echo The scraper requires Firefox to work properly
)

REM Create virtual environment
echo.
echo [3/6] Creating Python virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment and upgrade pip
echo.
echo [4/6] Activating virtual environment and upgrading pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo [5/6] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

REM Run tests
echo.
echo [6/6] Testing installation...
python test_setup.py
if %errorlevel% neq 0 (
    echo WARNING: Some tests failed. Check the output above.
) else (
    echo SUCCESS: All tests passed!
)

echo.
echo ================================================================
echo                    SETUP COMPLETE!
echo ================================================================
echo.
echo To run the UE5 Documentation Scraper:
echo   1. Open Command Prompt in this directory
echo   2. Run: venv\Scripts\activate.bat
echo   3. Run: python ue5_docs_scraper.py
echo.
echo Or simply double-click: run_scraper.bat
echo.
pause