@echo off
REM Argo Aviation Referral Portal - Windows Startup Script

echo ========================================
echo Starting Argo Aviation Referral Portal
echo ========================================
echo.

REM Check if virtual environment exists
if not exist venv\Scripts\activate.bat (
    echo ERROR: Virtual environment not found
    echo Please run deploy_windows.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist .env (
    echo WARNING: .env file not found
    echo Creating default .env file...
    echo FLASK_APP=run.py > .env
    echo FLASK_ENV=development >> .env
    echo SECRET_KEY=dev-secret-key-change-in-production >> .env
    echo DATABASE_URL=sqlite:///instance/app.db >> .env
)

REM Create instance directory if it doesn't exist
if not exist instance mkdir instance

REM Start the application
echo.
echo Starting application on http://localhost:5001
echo Press Ctrl+C to stop the server
echo.
python run.py
