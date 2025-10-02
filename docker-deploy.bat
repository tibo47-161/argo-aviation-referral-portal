@echo off
REM Argo Aviation Referral Portal - Docker Deployment Script (Windows)

echo.
echo ========================================
echo  Argo Aviation Referral Portal
echo  Docker Deployment for Windows
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://docs.docker.com/desktop/windows/
    pause
    exit /b 1
)

echo [INFO] Docker found, proceeding with deployment...

REM Stop any existing containers
echo [INFO] Stopping any existing containers...
docker-compose down 2>nul

REM Build the Docker image
echo [INFO] Building Docker image...
docker-compose build
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build Docker image
    pause
    exit /b 1
)

REM Start the containers
echo [INFO] Starting containers...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start containers
    pause
    exit /b 1
)

REM Wait for application to start
echo [INFO] Waiting for application to start...
timeout /t 15 /nobreak >nul

REM Check if application is running
curl -f http://localhost:8000/ >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Argo Aviation Referral Portal is running!
    echo.
    echo ========================================
    echo  APPLICATION READY
    echo ========================================
    echo.
    echo  URL: http://localhost:8000
    echo.
    echo  Admin Login:
    echo    Email: admin@argo-aviation.com
    echo    Password: admin123
    echo.
    echo ========================================
    echo.
    echo Opening application in browser...
    start http://localhost:8000
) else (
    echo [WARNING] Application might still be starting up...
    echo Check logs with: docker-compose logs -f
)

echo.
echo Container Status:
docker-compose ps

echo.
echo Commands:
echo  - View logs: docker-compose logs -f
echo  - Stop app: docker-compose down
echo  - Restart: docker-compose restart
echo.

pause
