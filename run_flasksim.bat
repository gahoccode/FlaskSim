@echo off
chcp 65001 >nul

:MENU
echo ===============================
echo   FlaskSim Automation Script
 echo ===============================
echo 1. Activate venv and run app
 echo 2. Install dependencies with uv sync
 echo 3. Exit
set /p choice="Select an option (1-3): "

if "%choice%"=="1" goto ACTIVATE_RUN
if "%choice%"=="2" goto UVSYNC
if "%choice%"=="3" exit

echo Invalid selection.
goto MENU

:ACTIVATE_RUN
if exist .venv\Scripts\activate (
    call .venv\Scripts\activate
    echo Virtual environment activated.
    echo Starting Flask app...
    python app.py
) else (
    echo Virtual environment not found. Please install dependencies first.
)
goto MENU

:UVSYNC
if exist .venv\Scripts\activate (
    call .venv\Scripts\activate
)
echo Running uv sync...
uv sync
goto MENU
