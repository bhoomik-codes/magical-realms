@echo off
REM Change console to white background with black text for better readability
color F0
REM Set console code page to UTF-8 for proper emoji display
chcp 65001
echo ========================================
echo RPG Game Improved GUI Setup (Windows)
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

REM Check if tkinter is available
python -c "import tkinter" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Tkinter is not available.
    echo Please ensure you have tkinter installed with Python.
    echo This is usually included with standard Python installations.
    echo When installing Python, make sure to check "tcl/tk and IDLE" option.
    pause
    exit /b
)

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
echo Starting RPG Game with Improved GUI...
echo ========================================
echo.

REM Set UTF-8 encoding for better display of special characters
SET PYTHONIOENCODING=utf-8
python -X utf8 rpg_game_improved_gui.py

echo.
pause
