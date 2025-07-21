#!/usr/bin/env python3
"""
Fixed Face Tracking System Startup Script
This script applies memory optimizations and port fixes before starting the system.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def setup_environment():
    """Set up environment variables for optimal performance"""
    print("🔧 Setting up optimized environment...")
    
    # PyTorch memory optimization
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Use only first GPU
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    os.environ['NUMEXPR_NUM_THREADS'] = '1'
    os.environ['PYTORCH_JIT'] = '0'
    
    # Multiprocessing settings
    os.environ['PYTORCH_MULTIPROCESSING_START_METHOD'] = 'spawn'
    
    # Disable FTS auto-start initially to prevent memory conflicts
    os.environ['FTS_AUTO_START'] = 'false'
    
    print("✅ Environment configured for optimal memory usage")

def run_memory_fix():
    """Run the memory and port fix script"""
    print("🔧 Running memory and port fixes...")
    
    try:
        result = subprocess.run([sys.executable, "fix_memory_and_ports.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Memory and port fixes applied successfully")
            return True
        else:
            print(f"⚠️ Fix script warning: {result.stderr}")
            return True  # Continue anyway
            
    except subprocess.TimeoutExpired:
        print("⚠️ Fix script timeout, continuing...")
        return True
    except Exception as e:
        print(f"⚠️ Error running fix script: {e}")
        return True  # Continue anyway

def start_server():
    """Start the server with optimal settings"""
    print("🚀 Starting Face Recognition Attendance System...")
    
    try:
        # Start with conservative settings
        cmd = [
            sys.executable, "start_unified_server.py",
            "--host", "127.0.0.1",  # Use localhost for better security
            "--port", "8000",
            "--workers", "1",  # Single worker for stability
            "--no-fts"  # Start without FTS initially
        ]
        
        print("🎯 Starting server with conservative settings...")
        print("📝 Command:", " ".join(cmd))
        
        # Start the server
        process = subprocess.Popen(cmd)
        
        # Wait a bit for server to start
        time.sleep(5)
        
        # Check if server is running
        if process.poll() is None:
            print("✅ Server started successfully!")
            print("🌐 Server available at: http://127.0.0.1:8000")
            print("📚 API docs available at: http://127.0.0.1:8000/docs")
            print("")
            print("💡 To enable Face Tracking System:")
            print("   1. Go to the API docs")
            print("   2. Use the /system/start-fts endpoint")
            print("   3. Or set FTS_AUTO_START=true and restart")
            print("")
            print("🛑 Press Ctrl+C to stop the server")
            
            # Wait for the process to complete
            process.wait()
        else:
            print("❌ Server failed to start")
            return False
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        if 'process' in locals():
            process.terminate()
            process.wait()
        print("✅ Server stopped")
        return True
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    required_packages = ['torch', 'fastapi', 'uvicorn', 'psutil']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️ Missing packages: {', '.join(missing_packages)}")
        print("💡 Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies available")
    return True

def main():
    print("🎯 Face Tracking System - Fixed Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print()
    
    # Set up environment
    setup_environment()
    print()
    
    # Run memory fixes
    run_memory_fix()
    print()
    
    # Start server
    if start_server():
        print("✅ System started successfully!")
    else:
        print("❌ Failed to start system")
        sys.exit(1)

if __name__ == "__main__":
    main()