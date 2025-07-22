#!/bin/bash

echo "🐘 PostgreSQL Installation Script"
echo "================================"

# Detect OS
if command -v apt-get &> /dev/null; then
    echo "📦 Detected: Ubuntu/Debian system"
    echo "🔄 Installing PostgreSQL..."
    
    # Update package list
    sudo apt update
    
    # Install PostgreSQL
    sudo apt install -y postgresql postgresql-contrib postgresql-client
    
    # Start and enable PostgreSQL service
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    echo "✅ PostgreSQL installation completed"
    
elif command -v yum &> /dev/null; then
    echo "📦 Detected: CentOS/RHEL system"
    echo "🔄 Installing PostgreSQL..."
    
    # Install PostgreSQL
    sudo yum install -y postgresql-server postgresql-contrib
    
    # Initialize database
    sudo postgresql-setup initdb
    
    # Start and enable PostgreSQL service
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    echo "✅ PostgreSQL installation completed"
    
elif command -v dnf &> /dev/null; then
    echo "📦 Detected: Fedora/newer RHEL system"
    echo "🔄 Installing PostgreSQL..."
    
    # Install PostgreSQL
    sudo dnf install -y postgresql-server postgresql-contrib
    
    # Initialize database
    sudo postgresql-setup initdb
    
    # Start and enable PostgreSQL service
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    echo "✅ PostgreSQL installation completed"
    
else
    echo "❌ Unsupported operating system"
    echo "Please install PostgreSQL manually:"
    echo "- Windows: Download from https://www.postgresql.org/download/windows/"
    echo "- macOS: brew install postgresql"
    exit 1
fi

# Test installation
echo "🔍 Testing PostgreSQL installation..."
if systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL service is running"
    
    # Get PostgreSQL version
    sudo -u postgres psql -c "SELECT version();" 2>/dev/null && echo "✅ PostgreSQL is accessible"
    
    echo ""
    echo "🎉 PostgreSQL installation successful!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Run: python3 setup_postgresql.py"
    echo "2. Run: python3 backend/init_db.py"
    echo "3. Start system: python3 start_unified_server.py --enable-fts"
    
else
    echo "❌ PostgreSQL service is not running"
    echo "Try: sudo systemctl start postgresql"
fi
