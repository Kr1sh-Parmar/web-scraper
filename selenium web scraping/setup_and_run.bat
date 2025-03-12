@echo off
echo ===================================================
echo MOSDAC Soil Wetness Index Data Scraper - Setup
echo ===================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b
)

echo Python is installed. Setting up environment...
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment.
    echo Please try running this script as administrator.
    pause
    exit /b
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing required packages...
echo This may take a few minutes...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install requirements.
    echo Please check your internet connection and try again.
    pause
    exit /b
)

echo.
echo ===================================================
echo Setup complete! Running the scraper...
echo ===================================================
echo.

REM Run the scraper
python scrape_mosdac.py

REM Keep the window open
echo.
echo ===================================================
pause 