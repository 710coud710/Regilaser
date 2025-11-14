@echo off
echo ========================================
echo   Hot Reload Development Mode
echo ========================================
echo.
echo Installing dependencies...
pip install -r requirements.txt -q
echo.
echo Starting application with hot reload...
echo Press Ctrl+C to stop
echo.
python main_dev.py

