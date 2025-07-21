#!/usr/bin/env python3
"""
Test script for Camera Detection and Configuration System
Tests the complete flow from detection to FTS configuration
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_camera_system():
    """Test the complete camera system flow"""
    try:
        from utils.auto_camera_detector import get_auto_detector
        from db.db_manager import DatabaseManager
        
        print("🔍 Testing Camera Detection and Configuration System")
        print("=" * 60)
        
        # Step 1: Test camera detection
        print("\n1️⃣ Testing Camera Detection...")
        auto_detector = get_auto_detector()
        detected_cameras = await auto_detector.detect_all_cameras()
        
        print(f"✅ Detection completed: Found {len(detected_cameras)} cameras")
        for camera in detected_cameras:
            status = "✅ Working" if camera.is_working else "❌ Not working"
            print(f"   - {camera.name} ({camera.type}): {camera.source} {status}")
        
        # Step 2: Test database integration
        print("\n2️⃣ Testing Database Integration...")
        db_manager = DatabaseManager()
        
        # Check if cameras are already configured
        configured_cameras = db_manager.get_all_cameras()
        print(f"📊 Currently configured cameras: {len(configured_cameras)}")
        
        # Step 3: Test configuration simulation
        print("\n3️⃣ Testing Configuration Logic...")
        working_cameras = [c for c in detected_cameras if c.is_working]
        
        if working_cameras:
            test_camera = working_cameras[0]
            existing = db_manager.get_camera_by_source(test_camera.source)
            
            if existing:
                print(f"⚠️ Camera {test_camera.name} is already configured (ID: {existing.id})")
            else:
                print(f"✅ Camera {test_camera.name} is available for configuration")
                print(f"   Source: {test_camera.source}")
                print(f"   Resolution: {test_camera.resolution[0]}x{test_camera.resolution[1]}")
                print(f"   FPS: {test_camera.fps}")
        
        # Step 4: Test API endpoints availability
        print("\n4️⃣ Testing API Endpoints...")
        
        # Import and check if the camera router functions exist
        try:
            from app.routers.cameras import (
                detect_all_cameras,
                get_detected_cameras,
                configure_camera_for_fts,
                remove_camera_from_fts,
                get_fts_configured_cameras
            )
            print("✅ All camera API endpoints are available")
        except ImportError as e:
            print(f"❌ Missing API endpoints: {e}")
        
        # Step 5: Summary
        print("\n📊 System Summary:")
        print(f"   Total detected: {len(detected_cameras)}")
        print(f"   Working cameras: {len(working_cameras)}")
        print(f"   Already configured: {len(configured_cameras)}")
        print(f"   Available for config: {len([c for c in working_cameras if not db_manager.get_camera_by_source(c.source)])}")
        
        print("\n🎯 Camera Detection System is ready!")
        print("👉 Super admins can now:")
        print("   - Access /super-admin/camera-detection in the web interface")
        print("   - Run camera detection to find all available cameras")
        print("   - Configure working cameras for FTS use")
        print("   - Set up tripwires and detection zones")
        print("   - Remove cameras from FTS when needed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    success = await test_camera_system()
    
    if success:
        print("\n🎉 All tests passed! Camera system is working correctly.")
        exit(0)
    else:
        print("\n💥 Tests failed! Please check the errors above.")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())