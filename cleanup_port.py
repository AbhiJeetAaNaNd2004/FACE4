#!/usr/bin/env python3
"""
Port Cleanup Utility for Face Recognition Attendance System
Helps clean up port conflicts by killing processes using specific ports
"""

import sys
import subprocess
import argparse
import socket

def check_port_available(host, port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False

def kill_process_on_port(port):
    """Kill any process using the specified port"""
    try:
        processes_killed = 0
        
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
                            kill_result = subprocess.run(f"taskkill /f /pid {pid}", shell=True, capture_output=True)
                            if kill_result.returncode == 0:
                                print(f"✅ Killed process {pid} using port {port}")
                                processes_killed += 1
                            else:
                                print(f"❌ Failed to kill process {pid}")
        else:
            # Unix/Linux command
            cmd = f"lsof -ti:{port}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid.strip():
                        kill_result = subprocess.run(f"kill -9 {pid}", shell=True, capture_output=True)
                        if kill_result.returncode == 0:
                            print(f"✅ Killed process {pid} using port {port}")
                            processes_killed += 1
                        else:
                            print(f"❌ Failed to kill process {pid}")
        
        if processes_killed == 0:
            print(f"ℹ️ No processes found using port {port}")
        else:
            print(f"✅ Total processes killed: {processes_killed}")
            
        return processes_killed > 0
        
    except Exception as e:
        print(f"❌ Error killing process on port {port}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Port Cleanup Utility")
    parser.add_argument("port", type=int, help="Port number to clean up")
    parser.add_argument("--host", default="0.0.0.0", help="Host to check (default: 0.0.0.0)")
    
    args = parser.parse_args()
    
    print(f"🔍 Checking port {args.port} on {args.host}...")
    
    if check_port_available(args.host, args.port):
        print(f"✅ Port {args.port} is already available")
    else:
        print(f"⚠️ Port {args.port} is in use, attempting cleanup...")
        if kill_process_on_port(args.port):
            # Check again
            if check_port_available(args.host, args.port):
                print(f"✅ Port {args.port} is now available")
            else:
                print(f"❌ Port {args.port} is still in use")
        else:
            print(f"❌ Could not clean up port {args.port}")

if __name__ == "__main__":
    main()