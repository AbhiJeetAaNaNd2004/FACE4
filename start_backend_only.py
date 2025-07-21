#!/usr/bin/env python3
"""
Start Backend API Only
This script starts only the FastAPI backend without the Face Tracking System.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def setup_environment():
    """Set up environment variables for backend only"""
    print("🔧 Setting up backend environment...")
    
    # Disable FTS auto-start
    os.environ['FTS_AUTO_START'] = 'false'
    
    # Set conservative memory settings anyway
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    os.environ['NUMEXPR_NUM_THREADS'] = '1'
    
    print("✅ Backend environment configured")

def start_backend(host="127.0.0.1", port=8000, reload=False):
    """Start the FastAPI backend only"""
    print("🚀 Starting FastAPI Backend...")
    
    try:
        backend_path = Path(__file__).parent / "backend"
        os.chdir(backend_path)
        
        # Build uvicorn command
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", host,
            "--port", str(port),
            "--access-log",
            "--loop", "asyncio",
            "--workers", "1"  # Single worker for stability
        ]
        
        if reload:
            cmd.append("--reload")
        
        print(f"🎯 Starting Backend API on {host}:{port}")
        print("📝 Command:", " ".join(cmd))
        print("🔄 Face Tracking System is DISABLED")
        print("")
        
        # Start the backend
        process = subprocess.Popen(cmd)
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Check if server is running
        if process.poll() is None:
            print("✅ Backend API started successfully!")
            print(f"🌐 API available at: http://{host}:{port}")
            print(f"📚 API docs available at: http://{host}:{port}/docs")
            print("")
            print("🎛️ Available API endpoints:")
            print("   • Authentication: /auth/")
            print("   • Employees: /employees/")
            print("   • Attendance: /attendance/")
            print("   • Cameras: /cameras/")
            print("   • System: /system/")
            print("")
            print("🛑 Press Ctrl+C to stop the backend")
            
            # Wait for the process to complete
            process.wait()
        else:
            print("❌ Backend failed to start")
            return False
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down backend...")
        if 'process' in locals():
            process.terminate()
            process.wait()
        print("✅ Backend stopped")
        return True
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False

def main():
    print("🎯 Face Recognition System - Backend API Only")
    print("=" * 50)
    
    # Set up environment
    setup_environment()
    print()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Start Backend API Only")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    # Start backend
    if start_backend(args.host, args.port, args.reload):
        print("✅ Backend API session completed!")
    else:
        print("❌ Failed to start backend API")
        sys.exit(1)

if __name__ == "__main__":
    main()