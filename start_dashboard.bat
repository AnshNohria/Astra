@echo off
echo ========================================================================
echo   ASTRA - Interactive Web Dashboard Launcher
echo ========================================================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if Flask is installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Installing Flask...
    pip install flask flask-cors
)

echo.
echo ========================================================================
echo   Starting Astra Web Server
echo ========================================================================
echo.
echo   Open your browser to: http://localhost:5000
echo.
echo   Press Ctrl+C to stop the server
echo ========================================================================
echo.

REM Start the web server
python web_server.py

pause
