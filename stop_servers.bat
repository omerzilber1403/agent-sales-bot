@echo off
echo Stopping AGENT Development Servers...
echo.

REM Kill processes on ports 8080 and 5173
echo Stopping Backend Server (Port 8080)...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8080"') do taskkill /f /pid %%a 2>nul

echo Stopping Frontend Server (Port 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5173"') do taskkill /f /pid %%a 2>nul

echo.
echo Servers stopped.
echo Press any key to exit...
pause >nul
