@echo off
setlocal enabledelayedexpansion

echo =========================================
echo Starting Spotify BCI Setup and Launcher...
echo =========================================

REM Check for Python 3
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3 from https://www.python.org/downloads/
    echo Make sure to check the box "Add Python to PATH" during installation!
    pause
    exit /b 1
)

for /f "tokens=*" %%a in ('python --version') do set PYTHON_VER=%%a
echo Found: %PYTHON_VER%

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found in the current directory.
    pause
    exit /b 1
)

REM Install requirements
echo.
echo Checking and installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies. Please check your internet connection.
    pause
    exit /b 1
)

REM Start the application
echo.
echo Dependencies verified. Starting Spotify BCI...
python spotify_bci.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The application crashed unexpectedly.
    pause
)
