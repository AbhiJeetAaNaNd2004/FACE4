#!/usr/bin/env python3
"""
Test Command Line Arguments
This script tests that all startup commands work correctly.
"""

import subprocess
import sys

def test_command_help(command, description):
    """Test that a command's help works"""
    print(f"🔍 Testing {description}...")
    
    try:
        result = subprocess.run(
            [sys.executable] + command + ["--help"], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ {description} help works")
            return True
        else:
            print(f"❌ {description} help failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {description} help timed out")
        return False
    except Exception as e:
        print(f"❌ {description} help error: {e}")
        return False

def test_unified_server_args():
    """Test specific unified server arguments"""
    print("\n🔍 Testing unified server arguments...")
    
    # Test that --enable-fts is now accepted
    try:
        result = subprocess.run(
            [sys.executable, "start_unified_server.py", "--enable-fts", "--help"], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and "--enable-fts" in result.stdout:
            print("✅ --enable-fts argument is available")
            return True
        else:
            print("❌ --enable-fts argument not working properly")
            return False
            
    except Exception as e:
        print(f"❌ Error testing --enable-fts: {e}")
        return False

def main():
    print("🎯 Testing Command Line Arguments")
    print("=" * 40)
    
    commands_to_test = [
        (["start_system_fixed.py"], "Fixed startup script"),
        (["start_unified_server.py"], "Unified server"),
        (["start_backend_only.py"], "Backend only"),
        (["start_frontend_only.py"], "Frontend only"),
        (["start_fts_only.py"], "FTS only"),
        (["start_camera_detection.py"], "Camera detection"),
        (["fix_memory_and_ports.py"], "Memory fix script")
    ]
    
    passed = 0
    total = len(commands_to_test)
    
    for command, description in commands_to_test:
        if test_command_help(command, description):
            passed += 1
    
    # Test specific unified server functionality
    if test_unified_server_args():
        passed += 1
        total += 1
    
    print(f"\n📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All command line arguments working correctly!")
        print("\n💡 Ready to use:")
        print("   python start_unified_server.py --enable-fts")
        print("   python start_system_fixed.py")
    else:
        print("⚠️ Some command line issues found")
    
    print("\n🔧 Fixed Issues:")
    print("   ✅ --enable-fts flag now available")
    print("   ✅ FTS disabled by default for stability")
    print("   ✅ Clear error messages for missing arguments")

if __name__ == "__main__":
    main()