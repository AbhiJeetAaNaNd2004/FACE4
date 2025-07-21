@echo off
echo 🔧 Face Recognition Attendance System - Port Conflict Fix
echo =======================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

echo 🔍 Checking and cleaning port 8000...

REM Run the port cleanup utility
python cleanup_port.py 8000

echo.
echo 💡 You can now try running the server again with:
echo    npm start
echo    or
echo    npm run start:force (to automatically kill any conflicting processes)
echo.
echo 🚀 To start with automatic port cleanup:
echo    python start_unified_server.py --force

pause