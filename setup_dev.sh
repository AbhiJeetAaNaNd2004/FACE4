#!/bin/bash

echo "🎯 Face Recognition Attendance System - Development Setup"
echo "========================================================="

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✅ Python and Node.js detected"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install backend dependencies"
    exit 1
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi

cd ..

echo "✅ All dependencies installed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Set up your PostgreSQL database"
echo "2. Configure backend/.env with your database credentials"
echo "3. Initialize the database: python start_unified_server.py --init-db"
echo "4. Start the development servers:"
echo "   - Backend only: python start_unified_server.py --reload"
echo "   - Frontend only: cd frontend && npm start"
echo "   - Both together: npm run dev (requires concurrently)"
echo ""
echo "🌐 Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "👥 Default login credentials:"
echo "   - Super Admin: superadmin / admin123"
echo "   - Admin: admin / admin123"
echo "   - Employee: employee / employee123"