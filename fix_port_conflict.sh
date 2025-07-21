#!/bin/bash

echo "🔧 Face Recognition Attendance System - Port Conflict Fix"
echo "======================================================="

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

echo "🔍 Checking and cleaning port 8000..."

# Run the port cleanup utility
$PYTHON_CMD cleanup_port.py 8000

echo ""
echo "💡 You can now try running the server again with:"
echo "   npm start"
echo "   or"
echo "   npm run start:force (to automatically kill any conflicting processes)"
echo ""
echo "🚀 To start with automatic port cleanup:"
echo "   $PYTHON_CMD start_unified_server.py --force"