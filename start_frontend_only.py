#!/usr/bin/env python3
"""
Start Frontend Only
This script starts only the React frontend application.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_node_and_npm():
    """Check if Node.js and npm are available"""
    print("🔍 Checking Node.js and npm...")
    
    try:
        # Check Node.js
        node_result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if node_result.returncode == 0:
            print(f"✅ Node.js: {node_result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
        
        # Check npm
        npm_result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if npm_result.returncode == 0:
            print(f"✅ npm: {npm_result.stdout.strip()}")
        else:
            print("❌ npm not found")
            return False
        
        return True
        
    except FileNotFoundError:
        print("❌ Node.js/npm not found in PATH")
        print("💡 Please install Node.js from https://nodejs.org/")
        return False
    except Exception as e:
        print(f"❌ Error checking Node.js/npm: {e}")
        return False

def install_dependencies():
    """Install frontend dependencies if needed"""
    print("📦 Checking frontend dependencies...")
    
    frontend_path = Path(__file__).parent / "frontend"
    node_modules = frontend_path / "node_modules"
    
    if not node_modules.exists():
        print("📥 Installing frontend dependencies...")
        try:
            result = subprocess.run(
                ["npm", "install"], 
                cwd=frontend_path, 
                capture_output=True, 
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print("✅ Dependencies installed successfully")
                return True
            else:
                print(f"❌ Failed to install dependencies: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Dependency installation timed out")
            return False
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
    else:
        print("✅ Dependencies already installed")
        return True

def setup_frontend_environment():
    """Set up environment variables for frontend"""
    print("🔧 Setting up frontend environment...")
    
    # Set React development environment
    os.environ['REACT_APP_API_URL'] = 'http://127.0.0.1:8000'
    os.environ['BROWSER'] = 'none'  # Prevent auto-opening browser
    os.environ['GENERATE_SOURCEMAP'] = 'false'  # Faster builds
    
    print("✅ Frontend environment configured")

def start_frontend(port=3000, open_browser=False):
    """Start the React frontend"""
    print("🚀 Starting React Frontend...")
    
    try:
        frontend_path = Path(__file__).parent / "frontend"
        os.chdir(frontend_path)
        
        # Set port
        os.environ['PORT'] = str(port)
        
        if not open_browser:
            os.environ['BROWSER'] = 'none'
        
        # Build npm command
        cmd = ["npm", "start"]
        
        print(f"🎯 Starting Frontend on port {port}")
        print("📝 Command:", " ".join(cmd))
        print("🔄 Backend API should be running on http://127.0.0.1:8000")
        print("")
        
        # Start the frontend
        process = subprocess.Popen(cmd)
        
        # Wait a bit for server to start
        time.sleep(5)
        
        # Check if server is running
        if process.poll() is None:
            print("✅ Frontend started successfully!")
            print(f"🌐 Frontend available at: http://127.0.0.1:{port}")
            print("")
            print("📋 Make sure the backend is running:")
            print("   python start_backend_only.py")
            print("")
            print("🎛️ Available pages:")
            print("   • Login: http://127.0.0.1:3000/login")
            print("   • Dashboard: http://127.0.0.1:3000/dashboard")
            print("   • Employees: http://127.0.0.1:3000/employees")
            print("   • Attendance: http://127.0.0.1:3000/attendance")
            print("   • Cameras: http://127.0.0.1:3000/cameras")
            print("")
            print("🛑 Press Ctrl+C to stop the frontend")
            
            # Wait for the process to complete
            process.wait()
        else:
            print("❌ Frontend failed to start")
            return False
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down frontend...")
        if 'process' in locals():
            process.terminate()
            process.wait()
        print("✅ Frontend stopped")
        return True
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return False

def main():
    print("🎯 Face Recognition System - Frontend Only")
    print("=" * 50)
    
    # Check Node.js and npm
    if not check_node_and_npm():
        sys.exit(1)
    
    print()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    print()
    
    # Set up environment
    setup_frontend_environment()
    print()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Start Frontend Only")
    parser.add_argument("--port", type=int, default=3000, help="Port to bind to")
    parser.add_argument("--browser", action="store_true", help="Open browser automatically")
    
    args = parser.parse_args()
    
    # Start frontend
    if start_frontend(args.port, args.browser):
        print("✅ Frontend session completed!")
    else:
        print("❌ Failed to start frontend")
        sys.exit(1)

if __name__ == "__main__":
    main()