@echo off
title Job Market Analytics

echo ========================================
echo   Job Market Analytics
echo ========================================
echo.

cd /d "%~dp0"

echo Starting Backend...
start "FastAPI Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Frontend...
start "React Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo Application Started
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000/docs
echo.
start http://localhost:3000

pause