@echo off
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

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup_windows.bat first to set up the scraper.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if main script exists
if not exist "ue5_docs_scraper.py" (
    echo ERROR: ue5_docs_scraper.py not found!
    echo Please ensure all files are in the correct directory.
    pause
    exit /b 1
)

REM Run the scraper
echo.
echo Starting UE5 Documentation Scraper...
echo Press Ctrl+C to stop the scraper at any time.
echo.
python ue5_docs_scraper.py

REM Keep window open to show results
echo.
echo ================================================================
echo                   SCRAPING COMPLETED
echo ================================================================
echo Check the 'ue5_docs' folder for your downloaded PDFs
echo Check 'scraper.log' for detailed logs
echo.
pause