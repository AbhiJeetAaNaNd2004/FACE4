#!/usr/bin/env python3
"""
Unified Startup Script for Face Recognition Attendance System
Handles environment setup, database initialization, and server startup with integrated FTS
"""

import os
import sys
import subprocess
import argparse
import socket
import time
import asyncio
from pathlib import Path

def check_port_available(host, port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False

def find_available_port(host, start_port, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        if check_port_available(host, port):
            return port
    return None

def kill_process_on_port(port):
    """Kill any process using the specified port"""
    try:
        # Try to find and kill process using the port
        if sys.platform == "win32":
            # Windows command
            cmd = f"netstat -ano | findstr :{port}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if f":{port}" in line and "LISTENING" in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            subprocess.run(f"taskkill /f /pid {pid}", shell=True, capture_output=True)
                            print(f"🔄 Killed process {pid} using port {port}")
                            time.sleep(1)  # Give time for port to be released
        else:
            # Unix/Linux command
            cmd = f"lsof -ti:{port}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        subprocess.run(f"kill -9 {pid}", shell=True, capture_output=True)
                        print(f"🔄 Killed process {pid} using port {port}")
                time.sleep(1)  # Give time for port to be released
    except Exception as e:
        print(f"⚠️ Could not kill process on port {port}: {e}")

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        # import psycopg2  # PostgreSQL support
        import passlib
        import jose
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements with: pip install -r requirements.txt")
        return False

def check_database_connection():
    """Test database connection"""
    try:
        from backend.db.db_config import test_connection
        if test_connection():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def initialize_database():
    """Initialize database with tables and sample data"""
    try:
        backend_path = Path(__file__).parent / "backend"
        init_script = backend_path / "init_db.py"
        
        if init_script.exists():
            print("🔄 Initializing database...")
            result = subprocess.run([sys.executable, str(init_script)], 
                                  cwd=str(backend_path), 
                                  capture_output=True, 
                                  text=True)
            
            if result.returncode == 0:
                print("✅ Database initialized successfully")
                return True
            else:
                print(f"❌ Database initialization failed: {result.stderr}")
                return False
        else:
            print("❌ Database initialization script not found")
            return False
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        return False

def start_server(host="0.0.0.0", port=8000, reload=False, workers=1, enable_fts=True, force_kill=False):
    """Start the FastAPI server with integrated FTS"""
    try:
        print("🔧 Optimizing system for Face Tracking System...")
        
        # Set environment variables for memory optimization BEFORE any imports
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
        os.environ['OMP_NUM_THREADS'] = '1'
        os.environ['MKL_NUM_THREADS'] = '1'
        os.environ['NUMEXPR_NUM_THREADS'] = '1'
        os.environ['PYTORCH_JIT'] = '0'
        
        # Force single worker mode if FTS is enabled to prevent memory conflicts
        if enable_fts and workers > 1:
            print("⚠️ Forcing single worker mode when FTS is enabled to prevent memory conflicts")
            workers = 1
        
        # Check if port is available or force kill if requested
        if force_kill or not check_port_available(host, port):
            if force_kill:
                print(f"🔄 Force killing any process on port {port}...")
            else:
                print(f"⚠️ Port {port} is already in use")
                print(f"🔄 Attempting to free port {port}...")
            kill_process_on_port(port)
            
            # Check again if port is now available
            if check_port_available(host, port):
                print(f"✅ Port {port} is now available")
            else:
                # Find an alternative port
                alternative_port = find_available_port(host, port)
                if alternative_port:
                    print(f"🔄 Using alternative port {alternative_port}")
                    port = alternative_port
                else:
                    print(f"❌ No available ports found starting from {port}")
                    return
        
        backend_path = Path(__file__).parent / "backend"
        os.chdir(backend_path)
        
        # Set environment variable for FTS auto-start
        if enable_fts:
            os.environ["FTS_AUTO_START"] = "true"
            print("🤖 Face Tracking System will start automatically with the server")
        else:
            os.environ["FTS_AUTO_START"] = "false"
            print("⚠️ Face Tracking System auto-start is disabled")
        
        # Build uvicorn command with conservative settings
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", host,
            "--port", str(port),
            "--access-log",  # Enable access logging
            "--loop", "asyncio",  # Use asyncio loop for better compatibility
        ]
        
        if reload:
            cmd.append("--reload")
        
        # Only use multiple workers if reload is disabled and FTS is disabled
        if workers > 1 and not reload and not enable_fts:
            cmd.extend(["--workers", str(workers)])
        
        print("🎯 Face Recognition Attendance System")
        print("=" * 50)
        print(f"🚀 Starting unified server on http://{host}:{port}")
        print(f"📚 API Documentation: http://{host}:{port}/docs")
        print(f"🤖 FTS Integration: {'Enabled' if enable_fts else 'Disabled'}")
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start server
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def run_camera_detection():
    """Run automatic camera detection and configuration"""
    try:
        print("🔍 Starting automatic camera detection...")
        
        # Import here to avoid circular imports
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from backend.utils.auto_camera_detector import AutoCameraDetector
        
        async def detect_cameras():
            detector = AutoCameraDetector()
            cameras = await detector.detect_all_cameras()
            return cameras
        
        # Run camera detection
        cameras = asyncio.run(detect_cameras())
        
        if cameras:
            print(f"✅ Detected and configured {len(cameras)} cameras:")
            for camera in cameras:
                print(f"   • Camera {camera.camera_id}: {camera.name}")
                print(f"     Default tripwire: EntryDetection at position 0.5")
        else:
            print("⚠️  No cameras detected")
            print("💡 Cameras can be added manually through the admin interface")
        
        print()  # Add spacing
        
    except Exception as e:
        print(f"❌ Error during camera detection: {e}")
        print("💡 Cameras can be added manually through the admin interface")
        print()  # Add spacing

def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(
        description="Face Recognition Attendance System Unified Startup Script"
    )
    
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to bind the server to (default: 8000)"
    )
    
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Enable auto-reload for development"
    )
    
    parser.add_argument(
        "--workers", 
        type=int, 
        default=1, 
        help="Number of worker processes (default: 1)"
    )
    
    parser.add_argument(
        "--skip-checks", 
        action="store_true", 
        help="Skip pre-startup checks"
    )
    
    parser.add_argument(
        "--init-db", 
        action="store_true", 
        help="Initialize database and exit"
    )
    
    parser.add_argument(
        "--enable-fts", 
        action="store_true", 
        help="Enable Face Tracking System auto-start (default: disabled for stability)"
    )
    
    parser.add_argument(
        "--no-fts", 
        action="store_true", 
        help="Disable Face Tracking System auto-start (legacy option)"
    )
    
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force kill any existing process on the target port"
    )
    
    parser.add_argument(
        "--auto-detect-cameras", 
        action="store_true", 
        help="Automatically detect and configure cameras on startup"
    )
    
    args = parser.parse_args()
    
    print("🎯 Face Recognition Attendance System - Unified Server")
    print("=" * 60)
    
    # Initialize database only
    if args.init_db:
        if not check_requirements():
            sys.exit(1)
        
        if not initialize_database():
            sys.exit(1)
        
        print("✅ Database initialization completed")
        return
    
    # Pre-startup checks
    if not args.skip_checks:
        print("🔍 Running pre-startup checks...")
        
        if not check_requirements():
            sys.exit(1)
        
        if not check_database_connection():
            print("\n💡 Tip: Try running with --init-db to initialize the database")
            sys.exit(1)
    
    # Auto-detect cameras if requested
    if args.auto_detect_cameras:
        print("🔍 Auto-detecting cameras...")
        run_camera_detection()
    
    # Determine FTS enable status
    # Priority: --enable-fts > --no-fts > default (disabled for stability)
    if args.enable_fts:
        enable_fts = True
        print("🤖 Face Tracking System will be enabled (--enable-fts)")
    elif args.no_fts:
        enable_fts = False
        print("⚠️ Face Tracking System will be disabled (--no-fts)")
    else:
        enable_fts = False  # Default to disabled for stability
        print("⚠️ Face Tracking System disabled by default (use --enable-fts to enable)")
    
    # Start unified server
    start_server(
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        enable_fts=enable_fts,
        force_kill=args.force
    )

if __name__ == "__main__":
    main()