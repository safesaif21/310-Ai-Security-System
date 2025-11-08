@echo off
REM AI Security System - Tkinter Frontend Launcher for Windows

echo.
echo =========================================
echo   AI Security System - Tkinter
echo =========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

REM Start Backend Server in new window
echo Starting Backend Server...
start "Backend Server" cmd /k "cd /d %SCRIPT_DIR% && echo Starting Backend Server... && python backend.py"

REM Wait for backend to start
timeout /t 3 /nobreak > nul

REM Start Frontend
echo Starting Tkinter Frontend...
python frontend.py

pause

