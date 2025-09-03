@echo off
echo Starting AGENT Development Servers...
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start backend server in background
echo Starting Backend Server (Port 8080)...
start "Backend Server" cmd /k "cd /d %~dp0 && .venv\Scripts\activate.bat && set PYTHONPATH=%CD% && python -m uvicorn backend.main:app --reload --port 8080"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server in background
echo Starting Frontend Server (Port 5173)...
start "Frontend Server" cmd /k "cd /d %~dp0\frontend\tests && npm run dev"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8080
echo Frontend: http://localhost:5173
echo.
echo Press any key to exit this launcher...
pause >nul
