@echo off
REM Argo Aviation Referral Portal - Windows Deployment Script
REM This script sets up the application on Windows systems

echo ========================================
echo Argo Aviation Referral Portal Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo Python found. Checking version...
python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"

REM Check Python version (minimum 3.8)
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.8 or higher is required
    pause
    exit /b 1
)

echo.
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

echo.
echo Setting up environment variables...
if not exist .env (
    copy .env.example .env
    echo Please edit .env file with your configuration
)

echo.
echo Initializing database...
flask db upgrade
if errorlevel 1 (
    echo Warning: Database migration failed. This might be normal for first setup.
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To start the application:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Run the application: python run.py
echo.
echo The application will be available at: http://localhost:5001
echo.
pause
