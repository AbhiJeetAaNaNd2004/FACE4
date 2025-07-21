#!/usr/bin/env python3
"""
PostgreSQL Setup Script for Face Recognition Attendance System
Helps create database and user for the application
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('backend/.env')

def check_postgresql_service():
    """Check if PostgreSQL service is running"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'postgresql'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PostgreSQL service is running")
            return True
        else:
            print("❌ PostgreSQL service is not running")
            print("💡 Try: sudo systemctl start postgresql")
            return False
    except FileNotFoundError:
        print("⚠️ systemctl not found. Checking if PostgreSQL is running another way...")
        try:
            result = subprocess.run(['pg_isready'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ PostgreSQL is running")
                return True
            else:
                print("❌ PostgreSQL is not running")
                return False
        except FileNotFoundError:
            print("❌ PostgreSQL tools not found. Please install PostgreSQL.")
            return False

def connect_as_superuser():
    """Connect to PostgreSQL as superuser"""
    try:
        # Try to connect as postgres user to postgres database
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='postgres',
            user='postgres',
            password=''  # Empty password for peer authentication
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print("✅ Connected to PostgreSQL as superuser")
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ Failed to connect as postgres user: {e}")
        print("💡 You might need to:")
        print("   1. Set a password for postgres user")
        print("   2. Modify pg_hba.conf for authentication")
        print("   3. Run this script as postgres user: sudo -u postgres python3 setup_postgresql.py")
        return None

def create_database_and_user():
    """Create database and user for the application"""
    conn = connect_as_superuser()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Get configuration from environment
        db_name = os.getenv('DB_NAME', 'frs_db')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', 'password')
        
        print(f"📊 Setting up database: {db_name}")
        print(f"👤 Setting up user: {db_user}")
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        db_exists = cursor.fetchone()
        
        if not db_exists:
            print(f"🔄 Creating database: {db_name}")
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ Database {db_name} created successfully")
        else:
            print(f"ℹ️ Database {db_name} already exists")
        
        # Check if user exists (only if not postgres)
        if db_user != 'postgres':
            cursor.execute("SELECT 1 FROM pg_user WHERE usename = %s", (db_user,))
            user_exists = cursor.fetchone()
            
            if not user_exists:
                print(f"🔄 Creating user: {db_user}")
                cursor.execute(f"CREATE USER \"{db_user}\" WITH PASSWORD '{db_password}'")
                print(f"✅ User {db_user} created successfully")
            else:
                print(f"ℹ️ User {db_user} already exists")
                print(f"🔄 Updating password for user: {db_user}")
                cursor.execute(f"ALTER USER \"{db_user}\" WITH PASSWORD '{db_password}'")
                print(f"✅ Password updated for user {db_user}")
            
            # Grant privileges
            print(f"🔄 Granting privileges to {db_user} on {db_name}")
            cursor.execute(f'GRANT ALL PRIVILEGES ON DATABASE "{db_name}" TO "{db_user}"')
            print(f"✅ Privileges granted to {db_user}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during database setup: {e}")
        conn.close()
        return False

def test_application_connection():
    """Test connection with application credentials"""
    try:
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'frs_db')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', 'password')
        
        print(f"🔍 Testing connection to {db_name} as {db_user}...")
        
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ Connection successful!")
        print(f"   PostgreSQL version: {version}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def show_connection_info():
    """Show connection information"""
    print("\n📋 Database Connection Information:")
    print("-" * 40)
    print(f"Host: {os.getenv('DB_HOST', 'localhost')}")
    print(f"Port: {os.getenv('DB_PORT', '5432')}")
    print(f"Database: {os.getenv('DB_NAME', 'frs_db')}")
    print(f"User: {os.getenv('DB_USER', 'postgres')}")
    print(f"Password: {'*' * len(os.getenv('DB_PASSWORD', 'password'))}")

def main():
    print("🎯 PostgreSQL Setup for Face Recognition Attendance System")
    print("=" * 60)
    print()
    
    # Check if PostgreSQL is running
    if not check_postgresql_service():
        print("\n❌ PostgreSQL is not running. Please start it and try again.")
        sys.exit(1)
    
    print()
    
    # Show configuration
    show_connection_info()
    
    print("\n🔄 Setting up database and user...")
    if create_database_and_user():
        print("\n✅ Database setup completed successfully!")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)
    
    print("\n🔍 Testing application connection...")
    if test_application_connection():
        print("\n🎉 PostgreSQL setup completed successfully!")
        print("💡 You can now start the Face Recognition Attendance System")
    else:
        print("\n❌ Connection test failed. Please check the configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()