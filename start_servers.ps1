Write-Host "Starting AGENT Development Servers..." -ForegroundColor Green
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Start backend server in new window
Write-Host "Starting Backend Server (Port 8080)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\Activate.ps1; python -m uvicorn backend.main:app --reload --port 8080"

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend server in new window
Write-Host "Starting Frontend Server (Port 5173)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend\tests'; npm run dev"

Write-Host ""
Write-Host "Both servers are starting..." -ForegroundColor Green
Write-Host "Backend: http://localhost:8080" -ForegroundColor White
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit this launcher..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
