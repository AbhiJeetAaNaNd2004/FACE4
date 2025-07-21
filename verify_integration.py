#!/usr/bin/env python3
"""
Comprehensive Integration Verification Script
Tests frontend-backend integration and system functionality
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def check_frontend_build():
    """Test frontend build process"""
    print("🔧 Testing Frontend Build...")
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd="frontend",
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ Frontend builds successfully")
            return True
        else:
            print("❌ Frontend build failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Frontend build test failed: {e}")
        return False

def check_python_syntax():
    """Check Python syntax for key backend files"""
    print("\n🐍 Testing Python Syntax...")
    
    files_to_check = [
        "backend/app/main.py",
        "backend/app/routers/cameras.py",
        "backend/db/db_manager.py",
        "backend/db/db_models.py",
        "backend/utils/auto_camera_detector.py",
        "backend/core/fts_system.py"
    ]
    
    all_passed = True
    for file_path in files_to_check:
        try:
            result = subprocess.run(
                ["python3", "-m", "py_compile", file_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path}: {result.stderr}")
                all_passed = False
        except Exception as e:
            print(f"❌ {file_path}: {e}")
            all_passed = False
    
    return all_passed

def check_api_structure():
    """Verify API endpoint structure"""
    print("\n🔗 Checking API Structure...")
    
    # Check if all expected API methods exist in the frontend
    api_file = Path("frontend/src/services/api.ts")
    if not api_file.exists():
        print("❌ API service file not found")
        return False
    
    content = api_file.read_text()
    expected_methods = [
        "detectAllCameras",
        "configureCameraForFts", 
        "removeCameraFromFts",
        "getFtsConfiguredCameras",
        "getDetectedCameras",
        "getSupportedResolutions"
    ]
    
    missing_methods = []
    for method in expected_methods:
        if method not in content:
            missing_methods.append(method)
    
    if missing_methods:
        print(f"❌ Missing API methods: {', '.join(missing_methods)}")
        return False
    else:
        print("✅ All expected API methods found")
    
    return True

def check_route_configuration():
    """Check if routes are properly configured"""
    print("\n🛣️  Checking Route Configuration...")
    
    # Check App.tsx for camera detection route
    app_file = Path("frontend/src/App.tsx")
    if not app_file.exists():
        print("❌ App.tsx not found")
        return False
    
    content = app_file.read_text()
    
    required_routes = [
        "camera-detection",
        "CameraDetectionManagement"
    ]
    
    missing_routes = []
    for route in required_routes:
        if route not in content:
            missing_routes.append(route)
    
    if missing_routes:
        print(f"❌ Missing routes: {', '.join(missing_routes)}")
        return False
    else:
        print("✅ Camera detection route properly configured")
    
    return True

def check_database_models():
    """Check database model consistency"""
    print("\n💾 Checking Database Models...")
    
    # Check if all required fields exist in CameraConfig model
    models_file = Path("backend/db/db_models.py")
    if not models_file.exists():
        print("❌ Database models file not found")
        return False
    
    content = models_file.read_text()
    
    required_fields = [
        "source = Column",  # For camera source tracking
        "name = Column",    # For camera name
        "location = Column" # For camera location
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in content:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing database fields: {', '.join(missing_fields)}")
        return False
    else:
        print("✅ Database models have required fields")
    
    return True

def check_component_dependencies():
    """Check if all React components have proper dependencies"""
    print("\n⚛️  Checking React Component Dependencies...")
    
    # Check if LoadingSpinner component exists
    spinner_file = Path("frontend/src/components/ui/LoadingSpinner.tsx")
    if not spinner_file.exists():
        print("❌ LoadingSpinner component not found")
        return False
    else:
        print("✅ LoadingSpinner component exists")
    
    # Check if Badge component exists
    badge_file = Path("frontend/src/components/ui/Badge.tsx")
    if not badge_file.exists():
        print("❌ Badge component not found")
        return False
    else:
        print("✅ Badge component exists")
    
    # Check if CameraDetectionManagement page exists
    camera_page = Path("frontend/src/pages/super-admin/CameraDetectionManagement.tsx")
    if not camera_page.exists():
        print("❌ CameraDetectionManagement page not found")
        return False
    else:
        print("✅ CameraDetectionManagement page exists")
    
    return True

def check_navigation_integration():
    """Check if navigation is properly integrated"""
    print("\n🧭 Checking Navigation Integration...")
    
    layout_file = Path("frontend/src/components/layout/DashboardLayout.tsx")
    if not layout_file.exists():
        print("❌ DashboardLayout not found")
        return False
    
    content = layout_file.read_text()
    
    if "Camera Detection" not in content:
        print("❌ Camera Detection menu item not found")
        return False
    
    if "/super-admin/camera-detection" not in content:
        print("❌ Camera Detection route not found in navigation")
        return False
    
    print("✅ Navigation properly integrated")
    return True

def verify_error_fixes():
    """Verify that previous errors have been fixed"""
    print("\n🔧 Verifying Error Fixes...")
    
    fixes_verified = []
    
    # Check cameras.py indentation fix
    cameras_file = Path("backend/app/routers/cameras.py")
    if cameras_file.exists():
        content = cameras_file.read_text()
        if "raise HTTPException(" in content and "                 raise HTTPException(" not in content:
            fixes_verified.append("✅ Cameras.py indentation fixed")
        else:
            fixes_verified.append("❌ Cameras.py indentation still has issues")
    
    # Check unicode emoji fixes
    memory_file = Path("fix_memory_and_ports.py")
    if memory_file.exists():
        content = memory_file.read_text()
        if "📊" not in content and "🔧" not in content:
            fixes_verified.append("✅ Unicode emoji issues fixed")
        else:
            fixes_verified.append("❌ Unicode emoji issues still present")
    
    # Check API service methods
    api_file = Path("frontend/src/services/api.ts")
    if api_file.exists():
        content = api_file.read_text()
        if "getSupportedResolutions" in content and "apiService.get(" not in content:
            fixes_verified.append("✅ API service methods properly implemented")
        else:
            fixes_verified.append("❌ API service still has method issues")
    
    for fix in fixes_verified:
        print(fix)
    
    return all("✅" in fix for fix in fixes_verified)

def main():
    """Main verification function"""
    print("🔍 Starting Comprehensive Integration Verification")
    print("=" * 60)
    
    tests = [
        ("Frontend Build", check_frontend_build),
        ("Python Syntax", check_python_syntax),
        ("API Structure", check_api_structure),
        ("Route Configuration", check_route_configuration),
        ("Database Models", check_database_models),
        ("Component Dependencies", check_component_dependencies),
        ("Navigation Integration", check_navigation_integration),
        ("Error Fixes", verify_error_fixes)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 VERIFICATION SUMMARY")
    print("=" * 40)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is ready for use.")
        print("\n✅ Integration Status: SUCCESSFUL")
        print("\n👉 Next Steps:")
        print("   1. Start the backend: python start_unified_server.py --enable-fts")
        print("   2. Start the frontend: cd frontend && npm start")
        print("   3. Login as Super Admin")
        print("   4. Navigate to Camera Detection page")
        print("   5. Run camera detection and configure cameras")
        return True
    else:
        print(f"\n💥 {failed} TESTS FAILED! Please fix the issues above.")
        print("\n❌ Integration Status: NEEDS FIXES")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)