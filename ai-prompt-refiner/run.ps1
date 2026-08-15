Set-Location -Path "$PSScriptRoot\backend"
Write-Host "Starting AI Prompt Refiner backend on http://localhost:8000 ..." -ForegroundColor Cyan
& ".\.venv\Scripts\python.exe" -m uvicorn main:app --reload --port 8000
