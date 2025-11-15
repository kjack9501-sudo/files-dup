@echo off
echo ========================================
echo  Document Knowledge Assistant
echo  Starting React Frontend...
echo ========================================
echo.

REM Check if node_modules exists
if not exist frontend_react\node_modules (
    echo Installing React dependencies...
    cd frontend_react
    call npm install
    cd ..
    echo.
)

echo Starting React app on http://localhost:3000...
echo.
cd frontend_react
npm run dev

