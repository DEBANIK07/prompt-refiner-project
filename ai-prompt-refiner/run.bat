@echo off
cd /d "%~dp0backend"
echo Starting AI Prompt Refiner backend on http://localhost:8000 ...
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
