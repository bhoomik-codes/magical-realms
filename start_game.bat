@echo off
REM Change console to white background with black text for better readability
color F0
echo ========================================
echo RPG Game Setup (Windows)
echo ========================================
echo.

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b
)

REM Check Python version
python --version

echo.
echo ========================================
echo Database Configuration
echo ========================================
echo.
echo You'll need PostgreSQL installed and running.
echo.

set /p PGUSER=Enter database username (default: postgres): 
if "%PGUSER%"=="" set PGUSER=postgres

set /p PGPASSWORD=Enter database password: 

set /p PGHOST=Enter database host (default: localhost): 
if "%PGHOST%"=="" set PGHOST=localhost

set /p PGPORT=Enter database port (default: 5432): 
if "%PGPORT%"=="" set PGPORT=5432

set /p PGDATABASE=Enter database name (default: rpg_game): 
if "%PGDATABASE%"=="" set PGDATABASE=rpg_game

REM Set the full DATABASE_URL environment variable
set DATABASE_URL=postgresql://%PGUSER%:%PGPASSWORD%@%PGHOST%:%PGPORT%/%PGDATABASE%

echo.
echo Database connection string set to: postgresql://%PGUSER%:******@%PGHOST%:%PGPORT%/%PGDATABASE%
echo.

echo ========================================
echo Starting RPG Game...
echo ========================================
echo.

python rpg_game.py

echo.
pause
