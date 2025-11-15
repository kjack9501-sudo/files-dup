@echo off
echo ========================================
echo  Document Knowledge Assistant
echo  Starting Flask API Server...
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo ⚠️  WARNING: .env file not found!
    echo.
    echo Please create a .env file with:
    echo GEMINI_API_KEY=your_api_key_here
    echo.
    pause
    exit /b 1
)

REM Start Flask API
echo Starting Flask API on http://localhost:5000...
echo.
cd backend
python api.py

