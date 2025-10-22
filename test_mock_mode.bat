@echo off
echo ============================================
echo Testing QuestAI in Mock Mode
echo ============================================
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
)

REM Set mock mode
echo Setting MOCK_MODE=true in .env...
powershell -Command "(Get-Content .env) -replace 'MOCK_MODE=false', 'MOCK_MODE=true' | Set-Content .env"

echo.
echo ============================================
echo Starting Backend (Mock Mode)
echo ============================================
start cmd /k "cd /d %~dp0 && uvicorn app.main:app --reload"

timeout /t 3 /nobreak

echo.
echo ============================================
echo Starting Frontend
echo ============================================
start cmd /k "cd /d %~dp0frontend && streamlit run Home.py"

echo.
echo ============================================
echo Both servers started in Mock Mode!
echo ============================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8501
echo.
echo Press any key to exit...
pause