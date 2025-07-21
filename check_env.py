#!/usr/bin/env python3
"""
Environment Configuration Checker for Face Recognition Attendance System
Validates and displays all environment variables
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def load_all_env_files():
    """Load all .env files in the project"""
    project_root = Path(__file__).parent
    
    env_files = [
        project_root / '.env',
        project_root / 'backend' / '.env',
        project_root / 'frontend' / '.env'
    ]
    
    print("🔍 Loading environment files...")
    for env_file in env_files:
        if env_file.exists():
            load_dotenv(env_file)
            print(f"✅ Loaded: {env_file}")
        else:
            print(f"⚠️ Missing: {env_file}")
    print()

def check_database_config():
    """Check database configuration"""
    print("🗄️ Database Configuration:")
    print("-" * 30)
    
    db_vars = [
        'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD'
    ]
    
    for var in db_vars:
        value = os.getenv(var, 'NOT SET')
        if var == 'DB_PASSWORD' and value != 'NOT SET':
            value = '*' * len(value)  # Hide password
        print(f"  {var}: {value}")
    
    # Test database URL construction
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'frs_db')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'password')
    
    db_url = f"postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}"
    print(f"  DATABASE_URL: {db_url}")
    print()

def check_security_config():
    """Check security configuration"""
    print("🔐 Security Configuration:")
    print("-" * 30)
    
    security_vars = [
        'SECRET_KEY', 'ALGORITHM', 'ACCESS_TOKEN_EXPIRE_MINUTES'
    ]
    
    for var in security_vars:
        value = os.getenv(var, 'NOT SET')
        if var == 'SECRET_KEY' and value != 'NOT SET':
            value = value[:10] + '...' if len(value) > 10 else value
        print(f"  {var}: {value}")
    print()

def check_face_recognition_config():
    """Check face recognition configuration"""
    print("👤 Face Recognition Configuration:")
    print("-" * 40)
    
    face_vars = [
        'FACE_RECOGNITION_TOLERANCE', 'FACE_DETECTION_MODEL', 
        'FACE_ENCODING_MODEL', 'DEFAULT_CAMERA_ID'
    ]
    
    for var in face_vars:
        value = os.getenv(var, 'NOT SET')
        print(f"  {var}: {value}")
    print()

def check_frontend_config():
    """Check frontend configuration"""
    print("🌐 Frontend Configuration:")
    print("-" * 30)
    
    frontend_vars = [
        'REACT_APP_API_URL', 'REACT_APP_API_BASE_URL', 'GENERATE_SOURCEMAP'
    ]
    
    for var in frontend_vars:
        value = os.getenv(var, 'NOT SET')
        print(f"  {var}: {value}")
    print()

def check_file_paths():
    """Check if required directories exist"""
    print("📁 File System Check:")
    print("-" * 25)
    
    directories = [
        'logs', 'uploads', 'face_images', 
        'backend/logs', 'backend/uploads', 'backend/face_images'
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"  ✅ {directory}")
        else:
            print(f"  ❌ {directory} (missing)")
    print()

def validate_required_vars():
    """Validate that all required variables are set"""
    print("🔍 Validation Results:")
    print("-" * 25)
    
    required_vars = [
        'DB_HOST', 'DB_NAME', 'DB_USER', 'SECRET_KEY', 
        'REACT_APP_API_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"  ❌ Missing required variables: {', '.join(missing_vars)}")
        return False
    else:
        print("  ✅ All required variables are set")
        return True

def main():
    print("🎯 Face Recognition Attendance System - Environment Checker")
    print("=" * 65)
    print()
    
    # Load all environment files
    load_all_env_files()
    
    # Check configurations
    check_database_config()
    check_security_config()
    check_face_recognition_config()
    check_frontend_config()
    check_file_paths()
    
    # Final validation
    if validate_required_vars():
        print("\n🎉 Environment configuration looks good!")
        sys.exit(0)
    else:
        print("\n❌ Environment configuration has issues. Please fix the missing variables.")
        sys.exit(1)

if __name__ == "__main__":
    main()