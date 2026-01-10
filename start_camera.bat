@echo off
setlocal

:: Navigate to the project root directory
cd /d "%~dp0"

:: Check if .venv exists and activate it
if exist ".venv" (
    echo Activating virtual environment...
    call .venv\Scripts\activate
) else (
    echo Warning: .venv not found. Running with global python.
)

:: Set python path
set PYTHONPATH=%PYTHONPATH%;.

echo Starting Local Camera Service...
python -m backend.services.camera.main

pause
