#!/bin/bash

# =============================================================================
# Face Recognition Attendance System - Environment Setup Script
# =============================================================================

echo "🔧 Face Recognition Attendance System - Environment Setup"
echo "=========================================================="

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Expected structure: Face-Recognition-Attendance-System/"
    echo "                      ├── backend/"
    echo "                      ├── frontend/"
    echo "                      └── setup_env.sh (this script)"
    exit 1
fi

echo "✅ Project structure verified"

# Navigate to backend directory
cd backend

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " overwrite
    if [[ ! $overwrite =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled. Existing .env file preserved."
        exit 0
    fi
    echo "🗑️  Backing up existing .env to .env.backup"
    cp .env .env.backup
fi

# Copy .env.example to .env
if [ -f ".env.example" ]; then
    cp .env.example .env
    echo "✅ Created .env from template"
else
    echo "❌ Error: .env.example not found in backend directory"
    exit 1
fi

echo ""
echo "🔑 REQUIRED: You must set these environment variables:"
echo "=============================================="

# Generate a secure secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32 2>/dev/null || echo "GENERATE_YOUR_OWN_SECRET_KEY_HERE")

echo ""
echo "1. DATABASE PASSWORD:"
echo "   Edit the DB_PASSWORD in .env file"
echo "   Current: DB_PASSWORD=your_secure_database_password_here"
echo ""

echo "2. JWT SECRET KEY:"
echo "   Generated secure key for you:"
echo "   SECRET_KEY=$SECRET_KEY"
echo ""

# Update the .env file with the generated secret key
if [[ "$SECRET_KEY" != "GENERATE_YOUR_OWN_SECRET_KEY_HERE" ]]; then
    # Use different sed syntax for macOS and Linux
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/SECRET_KEY=your_super_secure_secret_key_here_minimum_32_characters/SECRET_KEY=$SECRET_KEY/" .env
    else
        sed -i "s/SECRET_KEY=your_super_secure_secret_key_here_minimum_32_characters/SECRET_KEY=$SECRET_KEY/" .env
    fi
    echo "✅ Secret key automatically updated in .env file"
else
    echo "⚠️  Could not generate secret key automatically. Please set it manually."
fi

echo ""
echo "📝 NEXT STEPS:"
echo "=============="
echo "1. Edit backend/.env file:"
echo "   - Set your PostgreSQL password for DB_PASSWORD"
echo "   - Review other settings as needed"
echo ""
echo "2. Install dependencies:"
echo "   cd backend"
echo "   pip install -r requirements.txt"
echo ""
echo "3. Setup database:"
echo "   python3 init_db.py"
echo ""
echo "4. Start the server:"
echo "   uvicorn app.main:app --reload"
echo ""

# Open .env file in default editor (optional)
read -p "Do you want to open the .env file for editing now? (y/N): " edit_now
if [[ $edit_now =~ ^[Yy]$ ]]; then
    if command -v code &> /dev/null; then
        code .env
    elif command -v nano &> /dev/null; then
        nano .env
    elif command -v vim &> /dev/null; then
        vim .env
    else
        echo "📝 Please edit backend/.env file manually"
    fi
fi

echo ""
echo "🎉 Environment setup complete!"
echo "📍 Configuration file: backend/.env"
echo "📖 Full guide: ENV_SETUP_GUIDE.md"