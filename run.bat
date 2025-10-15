@echo off
REM AI Security System Dashboard Launcher for Windows

echo.
echo =========================================
echo   AI Security System Dashboard
echo =========================================
echo.
echo Starting dashboard...
echo.
echo Dashboard will open in your browser at:
echo   http://localhost:8501
echo.
echo Click 'Start Camera' to begin monitoring
echo.
echo Press Ctrl+C to stop the dashboard
echo.

streamlit run dashboard.py

