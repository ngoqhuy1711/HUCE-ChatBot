@echo off
cd /d "%~dp0"
echo ========================================
echo  Reflex Frontend
echo  - Frontend (React): http://localhost:3000
echo  - Backend (WebSocket): http://localhost:8001
echo ========================================

REM Kill processes on port 3000 and 8001 (previous frontend)
echo Stopping previous frontend processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do taskkill /F /PID %%a >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo Syncing dependencies...
uv sync

echo.
echo Starting Reflex...
uv run reflex run
pause

