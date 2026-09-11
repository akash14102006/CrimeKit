@echo off
echo ==========================================
echo   CrimeKit Enterprise - Starting Servers
echo ==========================================
echo.
echo Starting Backend on port 8002...
start "CrimeKit-Backend" cmd /k "cd /d C:\Users\akash\Downloads\Enterprise grade - CrimeKit - front error && py -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8002"
timeout /t 5 /nobreak >nul
echo Starting Frontend on port 3000...
start "CrimeKit-Frontend" cmd /k "cd /d C:\Users\akash\Downloads\Enterprise grade - CrimeKit - front error\frontend && npm run dev"
echo.
echo ==========================================
echo   Backend:  http://localhost:8002
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8002/docs
echo ==========================================
echo.
echo Press any key to exit this launcher...
pause >nul
