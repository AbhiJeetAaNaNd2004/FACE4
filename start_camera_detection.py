#!/usr/bin/env python3
"""
Start Camera Detection & Discovery
This script runs camera discovery and basic detection without the full FTS.
"""

import os
import sys
import time
import signal
import cv2
import threading
from pathlib import Path

def setup_environment():
    """Set up environment for camera detection"""
    print("🔧 Setting up camera detection environment...")
    
    # Conservative memory settings
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    os.environ['NUMEXPR_NUM_THREADS'] = '1'
    
    print("✅ Camera detection environment configured")

def discover_onvif_cameras():
    """Discover ONVIF cameras on the network"""
    print("🔍 Discovering ONVIF cameras...")
    
    try:
        backend_path = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        from utils.camera_discovery import ONVIFCameraDiscovery
        
        discovery = ONVIFCameraDiscovery()
        cameras = discovery.discover_cameras(timeout=10)
        
        if cameras:
            print(f"✅ Found {len(cameras)} ONVIF camera(s):")
            for i, cam in enumerate(cameras, 1):
                print(f"   {i}. {cam.name} - {cam.ip}:{cam.port}")
                print(f"      Manufacturer: {cam.manufacturer}")
                print(f"      Model: {cam.model}")
                print(f"      Stream URL: {cam.stream_url}")
                print()
        else:
            print("⚠️ No ONVIF cameras discovered")
            print("💡 Make sure cameras are on the same network and ONVIF is enabled")
        
        return cameras
        
    except Exception as e:
        print(f"❌ Error discovering cameras: {e}")
        return []

def test_camera_connection(camera_url, camera_name="Unknown"):
    """Test connection to a camera"""
    print(f"🔌 Testing connection to {camera_name}...")
    
    try:
        cap = cv2.VideoCapture(camera_url)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                height, width = frame.shape[:2]
                print(f"✅ {camera_name} connected successfully")
                print(f"   Resolution: {width}x{height}")
                
                # Test a few frames
                for i in range(5):
                    ret, frame = cap.read()
                    if not ret:
                        print(f"⚠️ Failed to read frame {i+1}")
                        break
                    time.sleep(0.1)
                
                cap.release()
                return True
            else:
                print(f"❌ {camera_name} opened but cannot read frames")
                cap.release()
                return False
        else:
            print(f"❌ Cannot connect to {camera_name}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing {camera_name}: {e}")
        return False

def start_basic_detection(camera_urls):
    """Start basic face detection on cameras"""
    print("🚀 Starting basic face detection...")
    
    try:
        # Initialize face detector (using OpenCV's built-in detector)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        if face_cascade.empty():
            print("❌ Failed to load face cascade classifier")
            return False
        
        # Create video captures for each camera
        captures = []
        for i, url in enumerate(camera_urls):
            cap = cv2.VideoCapture(url)
            if cap.isOpened():
                captures.append((cap, f"Camera_{i+1}"))
                print(f"✅ Opened Camera_{i+1}: {url}")
            else:
                print(f"❌ Failed to open Camera_{i+1}: {url}")
        
        if not captures:
            print("❌ No cameras could be opened")
            return False
        
        print(f"🎯 Monitoring {len(captures)} camera(s) for faces...")
        print("🛑 Press Ctrl+C to stop detection")
        print("")
        
        # Detection loop
        frame_count = 0
        detection_count = 0
        
        try:
            while True:
                for cap, name in captures:
                    ret, frame = cap.read()
                    if ret:
                        # Convert to grayscale for detection
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        
                        # Detect faces
                        faces = face_cascade.detectMultiScale(
                            gray,
                            scaleFactor=1.1,
                            minNeighbors=5,
                            minSize=(30, 30)
                        )
                        
                        if len(faces) > 0:
                            detection_count += len(faces)
                            print(f"👤 {name}: Detected {len(faces)} face(s) [Total: {detection_count}]")
                
                frame_count += 1
                
                # Print status every 100 frames
                if frame_count % 100 == 0:
                    print(f"📊 Processed {frame_count} frames, detected {detection_count} faces total")
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping face detection...")
        
        finally:
            # Clean up
            for cap, name in captures:
                cap.release()
            print("✅ Camera detection stopped")
            
        return True
        
    except Exception as e:
        print(f"❌ Error in face detection: {e}")
        return False

def get_default_cameras():
    """Get default camera sources"""
    default_cameras = []
    
    # Test USB cameras (0-4)
    print("🔍 Checking for USB cameras...")
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                default_cameras.append(i)
                print(f"✅ Found USB camera at index {i}")
            cap.release()
        else:
            break
    
    # Add common IP camera URLs for testing
    test_urls = [
        "http://admin:admin@192.168.1.100:80/video",
        "rtsp://admin:admin@192.168.1.100:554/stream",
        "http://192.168.1.100:8080/video"
    ]
    
    return default_cameras

def main():
    print("🎯 Face Recognition System - Camera Detection & Discovery")
    print("=" * 60)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Camera Detection & Discovery")
    parser.add_argument("--discover", action="store_true", help="Discover ONVIF cameras")
    parser.add_argument("--test-usb", action="store_true", help="Test USB cameras")
    parser.add_argument("--detect", action="store_true", help="Start face detection")
    parser.add_argument("--camera-url", action="append", help="Add camera URL for testing")
    
    args = parser.parse_args()
    
    # Set up environment
    setup_environment()
    print()
    
    camera_urls = []
    
    # Discover ONVIF cameras
    if args.discover:
        cameras = discover_onvif_cameras()
        for cam in cameras:
            if cam.stream_url:
                camera_urls.append(cam.stream_url)
        print()
    
    # Test USB cameras
    if args.test_usb:
        print("🔍 Testing USB cameras...")
        usb_cameras = get_default_cameras()
        camera_urls.extend(usb_cameras)
        print()
    
    # Add manual camera URLs
    if args.camera_url:
        print("📝 Adding manual camera URLs...")
        for url in args.camera_url:
            camera_urls.append(url)
            print(f"   Added: {url}")
        print()
    
    # Test camera connections
    if camera_urls:
        print("🔌 Testing camera connections...")
        working_cameras = []
        for url in camera_urls:
            if test_camera_connection(url, str(url)):
                working_cameras.append(url)
        
        camera_urls = working_cameras
        print()
    
    # Start detection if requested
    if args.detect:
        if camera_urls:
            start_basic_detection(camera_urls)
        else:
            print("❌ No working cameras found for detection")
            print("💡 Try: python start_camera_detection.py --discover --test-usb --detect")
    
    # If no specific action requested, show help
    if not any([args.discover, args.test_usb, args.detect, args.camera_url]):
        print("💡 Camera Detection & Discovery Tool")
        print("")
        print("Usage examples:")
        print("  python start_camera_detection.py --discover")
        print("  python start_camera_detection.py --test-usb")
        print("  python start_camera_detection.py --discover --detect")
        print("  python start_camera_detection.py --camera-url rtsp://192.168.1.100:554/stream --detect")
        print("")
        print("Available options:")
        print("  --discover      Discover ONVIF cameras on network")
        print("  --test-usb      Test USB cameras (indices 0-4)")
        print("  --detect        Start basic face detection")
        print("  --camera-url    Add specific camera URL")

if __name__ == "__main__":
    main()