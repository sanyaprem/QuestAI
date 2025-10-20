@echo off
REM QuestAI Startup Script for Windows
REM This script starts both backend and frontend servers

echo ==================================
echo QuestAI - Starting Application
echo ==================================
echo.

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found
    echo Please copy .env.example to .env and add your API keys
    pause
    exit /b 1
)

REM Create logs directory
if not exist logs mkdir logs
echo [OK] Logs directory created

REM Start backend server
echo Starting Backend Server...
start /B uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > logs\backend_server.log 2>&1

REM Wait for backend to start
timeout /t 3 /nobreak > nul

echo [OK] Backend running on http://localhost:8000

REM Start frontend server
echo Starting Frontend Server...
cd frontend
start /B streamlit run Home.py --server.port 8501 --server.address localhost > ..\logs\frontend_server.log 2>&1
cd ..

REM Wait for frontend to start
timeout /t 3 /nobreak > nul

echo [OK] Frontend running on http://localhost:8501

echo.
echo ==================================
echo QuestAI is now running!
echo ==================================
echo.
echo Backend API:  http://localhost:8000
echo Frontend UI:  http://localhost:8501
echo API Docs:     http://localhost:8000/docs
echo.
echo Logs:
echo   Backend:    logs\backend_server.log
echo   Frontend:   logs\frontend_server.log
echo   App:        logs\quest_ai.log
echo.
echo Press Ctrl+C to stop all servers
echo.

pause