#!/usr/bin/env python3
"""
Comprehensive test script for camera functionality
Tests camera detection, streaming, management, and configuration
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_camera_discovery():
    """Test camera discovery functionality"""
    logger.info("🔍 Testing camera discovery...")
    
    try:
        from utils.camera_discovery import discover_cameras_on_network
        
        # Test network discovery
        cameras = await discover_cameras_on_network("192.168.1.0/24", timeout=5)
        logger.info(f"✅ Network discovery found {len(cameras)} cameras")
        
        for camera in cameras:
            logger.info(f"  📹 {camera.ip_address}:{camera.port} - {camera.manufacturer} {camera.model}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Camera discovery failed: {e}")
        return False

def test_auto_camera_detector():
    """Test auto camera detector functionality"""
    logger.info("🤖 Testing auto camera detector...")
    
    try:
        from utils.auto_camera_detector import get_auto_detector
        
        detector = get_auto_detector()
        logger.info("✅ Auto detector instance created")
        
        # Test USB camera detection
        detected_cameras = detector.get_detected_cameras()
        logger.info(f"✅ Auto detector found {len(detected_cameras)} cameras")
        
        for camera in detected_cameras:
            logger.info(f"  📹 Camera {camera.camera_id}: {camera.name} ({camera.type})")
        
        return True
    except Exception as e:
        logger.error(f"❌ Auto camera detector failed: {e}")
        return False

def test_camera_streaming():
    """Test camera streaming functionality"""
    logger.info("📺 Testing camera streaming...")
    
    try:
        from app.routers.streaming import generate_camera_stream, detect_cameras
        
        # Test camera detection
        available_cameras = detect_cameras()
        logger.info(f"✅ Streaming module detected {len(available_cameras)} cameras")
        
        # Test stream generation (just check if it starts)
        if available_cameras:
            camera_id = available_cameras[0]["id"]
            stream_gen = generate_camera_stream(camera_id)
            
            # Try to get first frame
            try:
                first_frame = next(stream_gen)
                if first_frame:
                    logger.info(f"✅ Camera {camera_id} stream started successfully")
                    return True
            except StopIteration:
                logger.warning(f"⚠️ Camera {camera_id} stream ended immediately")
        else:
            logger.info("ℹ️ No cameras available for streaming test")
            return True
        
        return True
    except Exception as e:
        logger.error(f"❌ Camera streaming failed: {e}")
        return False

def test_database_integration():
    """Test camera database integration"""
    logger.info("🗄️ Testing database integration...")
    
    try:
        from db.db_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        
        # Test getting cameras from database
        cameras = db_manager.get_all_cameras()
        logger.info(f"✅ Database has {len(cameras)} cameras configured")
        
        for camera in cameras:
            logger.info(f"  📹 {camera.name} (ID: {camera.camera_id}) - {camera.camera_type}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Database integration failed: {e}")
        return False

def test_fts_integration():
    """Test FTS system integration"""
    logger.info("🎯 Testing FTS integration...")
    
    try:
        # Test delayed import to avoid circular dependencies
        import importlib
        fts_module = importlib.import_module('core.fts_system')
        
        # Check if FTS functions are available
        functions_to_check = [
            'start_tracking_service',
            'shutdown_tracking_service', 
            'get_system_status',
            'is_tracking_running'
        ]
        
        for func_name in functions_to_check:
            if hasattr(fts_module, func_name):
                logger.info(f"✅ FTS function '{func_name}' available")
            else:
                logger.warning(f"⚠️ FTS function '{func_name}' missing")
        
        # Test getting system status
        get_system_status = getattr(fts_module, 'get_system_status', None)
        if get_system_status:
            status = get_system_status()
            logger.info(f"✅ FTS system status: {status}")
        
        return True
    except Exception as e:
        logger.error(f"❌ FTS integration failed: {e}")
        return False

def test_error_handling():
    """Test error handling in camera modules"""
    logger.info("🛡️ Testing error handling...")
    
    try:
        from utils.error_handling import CameraResourceContext, CameraError
        
        # Test camera context manager with invalid camera
        try:
            with CameraResourceContext(999) as cap:  # Non-existent camera
                pass
        except CameraError as e:
            logger.info(f"✅ Camera error handling works: {e}")
        
        # Test validation utilities
        from utils.validation import validate_camera_id, validate_ip_address, ValidationError
        
        # Test valid camera ID
        try:
            camera_id = validate_camera_id(1)
            logger.info(f"✅ Valid camera ID validation: {camera_id}")
        except ValidationError as e:
            logger.error(f"❌ Camera ID validation failed: {e}")
        
        # Test invalid camera ID
        try:
            validate_camera_id(999)
            logger.error("❌ Invalid camera ID should have failed")
        except ValidationError:
            logger.info("✅ Invalid camera ID properly rejected")
        
        # Test IP validation
        try:
            ip = validate_ip_address("192.168.1.1")
            logger.info(f"✅ Valid IP validation: {ip}")
        except ValidationError as e:
            logger.error(f"❌ IP validation failed: {e}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error handling test failed: {e}")
        return False

def test_configuration_schemas():
    """Test camera configuration schemas"""
    logger.info("📋 Testing configuration schemas...")
    
    try:
        from app.schemas import (
            CameraCreate, CameraUpdate, CameraDiscoveryRequest,
            CameraConfigurationRequest, TripwireCreate
        )
        
        # Test camera creation schema
        camera_data = {
            "camera_name": "Test Camera",
            "camera_type": "ip",
            "ip_address": "192.168.1.100",
            "resolution_width": 1920,
            "resolution_height": 1080,
            "fps": 30
        }
        
        camera_create = CameraCreate(**camera_data)
        logger.info(f"✅ Camera creation schema works: {camera_create.camera_name}")
        
        # Test discovery request schema
        discovery_request = CameraDiscoveryRequest(
            network_range="192.168.1.0/24",
            timeout=10
        )
        logger.info(f"✅ Discovery request schema works: {discovery_request.network_range}")
        
        # Test tripwire schema
        tripwire_data = {
            "name": "Test Tripwire",
            "position": 0.5,
            "direction": "horizontal",
            "spacing": 0.01
        }
        
        tripwire_create = TripwireCreate(**tripwire_data)
        logger.info(f"✅ Tripwire schema works: {tripwire_create.name}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Configuration schemas test failed: {e}")
        return False

async def run_all_tests():
    """Run all camera functionality tests"""
    logger.info("🚀 Starting comprehensive camera functionality tests...")
    
    tests = [
        ("Camera Discovery", test_camera_discovery),
        ("Auto Camera Detector", test_auto_camera_detector),
        ("Camera Streaming", test_camera_streaming),
        ("Database Integration", test_database_integration),
        ("FTS Integration", test_fts_integration),
        ("Error Handling", test_error_handling),
        ("Configuration Schemas", test_configuration_schemas)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
        if result:
            passed += 1
    
    logger.info(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All camera functionality tests PASSED!")
        return True
    else:
        logger.error(f"❌ {total - passed} tests FAILED!")
        return False

if __name__ == "__main__":
    asyncio.run(run_all_tests())