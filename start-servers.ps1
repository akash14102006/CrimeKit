Start-Process python -ArgumentList "-m uvicorn backend.app.main:app --host 0.0.0.0 --port 8002" -WorkingDirectory "C:\Users\akash\Downloads\Enterprise grade - CrimeKit - front error" -WindowStyle Normal
Start-Sleep -Seconds 8
Start-Process npm -ArgumentList "run dev" -WorkingDirectory "C:\Users\akash\Downloads\Enterprise grade - CrimeKit - front error\frontend" -WindowStyle Normal
Write-Host "Both servers started. Backend: http://localhost:8002 | Frontend: http://localhost:3000"
