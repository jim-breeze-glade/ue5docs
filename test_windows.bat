@echo off
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

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup_windows.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Run tests
echo.
echo Running installation tests...
echo.
python test_setup.py

echo.
echo Running scraper functionality test...
echo.
python test_scraper.py

echo.
echo ================================================================
echo                     TESTING COMPLETE
echo ================================================================
echo.
pause