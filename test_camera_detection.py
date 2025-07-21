#!/usr/bin/env python3
"""
Simple Camera Detection Test
Tests for available cameras without extensive scanning
"""

import cv2
import platform

def test_camera_detection():
    """Test basic camera detection"""
    print("🔍 Testing camera detection...")
    print(f"🖥️ Platform: {platform.system()}")
    
    cameras_found = []
    
    # Test only first 3 camera indices
    for i in range(3):
        try:
            print(f"Testing camera index {i}...")
            
            # Use platform-specific backend
            if platform.system() == "Windows":
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(i)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = int(cap.get(cv2.CAP_PROP_FPS))
                    
                    cameras_found.append({
                        'index': i,
                        'resolution': f"{width}x{height}",
                        'fps': fps
                    })
                    
                    print(f"✅ Camera {i}: {width}x{height} @ {fps}fps")
                else:
                    print(f"❌ Camera {i}: Could not read frame")
            else:
                print(f"❌ Camera {i}: Could not open")
                
            cap.release()
            
        except Exception as e:
            print(f"❌ Camera {i}: Error - {e}")
    
    print(f"\n📊 Summary: Found {len(cameras_found)} working cameras")
    
    if not cameras_found:
        print("⚠️ No cameras detected. This may explain why FTS is not starting properly.")
        print("💡 Suggestions:")
        print("   - Connect a USB camera or webcam")
        print("   - Check if camera drivers are installed")
        print("   - Ensure no other applications are using the camera")
        print("   - You can still use the system with IP cameras configured manually")
    
    return cameras_found

if __name__ == "__main__":
    test_camera_detection()