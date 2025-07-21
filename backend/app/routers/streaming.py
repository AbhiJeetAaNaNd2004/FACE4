"""
Live streaming router for camera feed
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import StreamingResponse
from typing import Generator, Optional
import cv2
import time
import asyncio
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import jwt
from datetime import datetime
import threading

from app.schemas import CurrentUser
from app.security import require_admin_or_above
from app.config import settings
from db.db_manager import DatabaseManager
from utils.logging import get_logger

router = APIRouter(prefix="/stream", tags=["Live Streaming"])
logger = get_logger(__name__)

# Global camera streams cache
active_streams = {}

def verify_token(token: str) -> bool:
    """Verify JWT token manually"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None or role is None:
            return False
            
        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            return False
            
        # Check if user has admin+ role
        return role in ["admin", "super_admin"]
    except jwt.InvalidTokenError:
        return False

def detect_cameras():
    """Detect available cameras on the system"""
    available_cameras = []
    
    # Check for USB/built-in cameras (indices 0-10)
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                # Get camera properties
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                
                available_cameras.append({
                    "id": i,
                    "name": f"Camera {i}",
                    "type": "USB/Built-in",
                    "status": "active",
                    "resolution": f"{width}x{height}",
                    "fps": fps,
                    "last_seen": time.strftime("%Y-%m-%dT%H:%M:%SZ")
                })
                logger.info(f"Detected camera {i}: {width}x{height} @ {fps}fps")
            cap.release()
    
    return available_cameras

def generate_camera_stream(camera_id: int) -> Generator[bytes, None, None]:
    """Generate live MJPEG stream from camera with FTS processing"""
    cap = None  # Initialize cap variable
    try:
        # Try to get processed frame from FTS system first
        try:
            from backend.core.fts_system import system_instance
        except ImportError:
            system_instance = None
        
        if system_instance and hasattr(system_instance, 'latest_frames'):
            logger.info(f"Using FTS-processed stream for camera {camera_id}")
            
            frame_count = 0
            last_frame_time = time.time()
            last_fps = 0
            
            while True:
                try:
                    # Get latest processed frame from FTS
                    with system_instance.frame_locks.get(camera_id, threading.Lock()):
                        if camera_id in system_instance.latest_frames:
                            frame = system_instance.latest_frames[camera_id]
                            if frame is not None:
                                frame = frame.copy()
                            else:
                                frame = None
                        else:
                            frame = None
                    
                    if frame is None:
                        # Generate "processing" frame
                        processing_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                        cv2.putText(processing_frame, "FTS Processing...", (180, 220), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        cv2.putText(processing_frame, f"Camera {camera_id}", (220, 260), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                        frame = processing_frame
                    
                    frame_count += 1
                    current_time = time.time()
                    
                    # Add FTS overlay information
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cv2.putText(frame, f"FTS Camera {camera_id}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.putText(frame, timestamp, (10, frame.shape[0] - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    # Calculate and display FPS
                    if current_time - last_frame_time >= 1.0:
                        last_fps = frame_count / (current_time - last_frame_time)
                        frame_count = 0
                        last_frame_time = current_time
                    
                    cv2.putText(frame, f"FPS: {last_fps:.1f}", 
                               (frame.shape[1] - 100, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    
                    # Add face detection info if available
                    if camera_id in system_instance.latest_faces:
                        face_count = len(system_instance.latest_faces[camera_id])
                        cv2.putText(frame, f"Faces: {face_count}", 
                                   (frame.shape[1] - 100, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
                    
                    # Encode frame as JPEG
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                    if ret:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                    
                    # Control frame rate
                    time.sleep(0.033)  # ~30 FPS
                    
                except Exception as e:
                    logger.warning(f"Error getting FTS frame for camera {camera_id}: {e}")
                    time.sleep(0.1)
                    continue
        
        else:
            # Fallback to direct camera access if FTS not available
            logger.info(f"FTS not available, using direct camera access for camera {camera_id}")
            
            # Get camera from auto-detector or database
            try:
                from backend.utils.auto_camera_detector import get_auto_detector
                auto_detector = get_auto_detector()
                detected_cameras = auto_detector.get_detected_cameras()
            except ImportError:
                detected_cameras = []
            
            camera_source = None
            for cam in detected_cameras:
                if cam.camera_id == camera_id:
                    camera_source = cam.source
                    break
            
            if camera_source is None:
                camera_source = camera_id
            
            cap = cv2.VideoCapture(camera_source)
            
            if not cap.isOpened():
                logger.error(f"Cannot open camera {camera_id}")
                # Generate error frame
                error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(error_frame, f"Camera {camera_id} not available", (50, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                _, buffer = cv2.imencode('.jpg', error_frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                return
            
            # Set camera properties for better performance
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size for lower latency
            
            frame_count = 0
            start_time = time.time()
            
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    logger.warning(f"Failed to read frame from camera {camera_id}")
                    # Generate "no signal" frame
                    no_signal_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(no_signal_frame, "No Signal", (250, 240), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    _, buffer = cv2.imencode('.jpg', no_signal_frame)
                    frame_bytes = buffer.tobytes()
                else:
                    # Add timestamp and camera info overlay
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    cv2.putText(frame, f"Direct Camera {camera_id} - {timestamp}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                frame_count += 1
                elapsed = time.time() - start_time
                if elapsed > 0:
                    fps = frame_count / elapsed
                    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_bytes = buffer.tobytes()
            
            # Yield frame in MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # Control frame rate
            time.sleep(1/30)  # 30 FPS
            
    except Exception as e:
        logger.error(f"Error in camera stream {camera_id}: {e}")
    finally:
        if cap:
            cap.release()
            logger.info(f"Released camera {camera_id}")

def generate_mock_mjpeg_stream() -> Generator[bytes, None, None]:
    """
    Generate a mock MJPEG stream for demonstration when no cameras are available
    """
    # Create a simple test image
    import numpy as np
    
    frame_count = 0
    start_time = time.time()
    
    while True:
        # Create a simple test frame with timestamp
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add some color and pattern
        frame[:, :] = [50, 100, 150]  # Blue background
        
        # Add animated elements
        t = time.time() - start_time
        x = int(320 + 200 * np.sin(t))
        y = int(240 + 100 * np.cos(t))
        cv2.circle(frame, (x, y), 30, (255, 255, 255), -1)
        
        # Add timestamp text
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"Mock Feed - {timestamp}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "No physical cameras detected", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add frame counter
        frame_count += 1
        cv2.putText(frame, f"Frame: {frame_count}", (10, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        # Yield frame in MJPEG format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # Sleep to control frame rate
        time.sleep(1/30)  # 30 FPS

@router.get("/live-feed")
async def get_live_feed(
    camera_id: Optional[int] = Query(None, description="Camera ID to stream from"),
    auth: Optional[str] = Query(None, description="Auth token for streaming"),
    current_user: CurrentUser = Depends(require_admin_or_above)
):
    """
    Get live camera feed (Admin+ only)
    Returns an MJPEG stream from the specified camera or default camera
    Supports both Bearer token and query parameter authentication for MJPEG compatibility
    """
    try:
        # If no camera_id specified, try to find an available camera
        if camera_id is None:
            available_cameras = detect_cameras()
            if available_cameras:
                camera_id = available_cameras[0]["id"]
                logger.info(f"Using default camera {camera_id}")
            else:
                logger.warning("No cameras detected, using mock stream")
                return StreamingResponse(
                    generate_mock_mjpeg_stream(),
                    media_type="multipart/x-mixed-replace; boundary=frame"
                )
        
        logger.info(f"Starting live feed for camera {camera_id}")
        return StreamingResponse(
            generate_camera_stream(camera_id),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
        
    except Exception as e:
        logger.error(f"Failed to start live feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start camera feed: {str(e)}"
        )

@router.get("/feed")
async def get_camera_stream(
    request: Request,
    camera_id: Optional[int] = Query(None, description="Camera ID to stream from"),
    auth: Optional[str] = Query(None, description="Auth token for streaming")
):
    """
    Get camera stream with token-based authentication
    Alternative endpoint for MJPEG streaming that supports query-based auth
    """
    try:
        # Get token from query param or Authorization header
        token = auth
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Verify token manually
        if not verify_token(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # If no camera_id specified, try to find an available camera
        if camera_id is None:
            available_cameras = detect_cameras()
            if available_cameras:
                camera_id = available_cameras[0]["id"]
                logger.info(f"Using default camera {camera_id}")
            else:
                logger.warning("No cameras detected, using mock stream")
                return StreamingResponse(
                    generate_mock_mjpeg_stream(),
                    media_type="multipart/x-mixed-replace; boundary=frame"
                )
        
        logger.info(f"Starting camera stream for camera {camera_id}")
        return StreamingResponse(
            generate_camera_stream(camera_id),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start camera stream: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start camera stream: {str(e)}"
        )

@router.get("/camera-status")
async def get_camera_status(
    current_user: CurrentUser = Depends(require_admin_or_above)
):
    """
    Get camera status information (Admin+ only)
    """
    try:
        # Detect available cameras
        available_cameras = detect_cameras()
        
        # Get database cameras
        db_manager = DatabaseManager()
        db_cameras = db_manager.get_all_cameras()
        
        # Combine information
        all_cameras = []
        
        # Add detected cameras
        for cam in available_cameras:
            all_cameras.append(cam)
        
        # Add database cameras that aren't in detected list
        for db_cam in db_cameras:
            if not any(cam["id"] == db_cam.camera_id for cam in all_cameras):
                all_cameras.append({
                    "id": db_cam.camera_id,
                    "name": db_cam.name,
                    "type": db_cam.camera_type,
                    "status": "configured" if db_cam.is_active else "inactive",
                    "resolution": f"{db_cam.resolution_width}x{db_cam.resolution_height}",
                    "fps": db_cam.fps,
                    "last_seen": db_cam.updated_at.isoformat() if db_cam.updated_at else None,
                    "ip_address": db_cam.ip_address,
                    "stream_url": db_cam.stream_url
                })
        
        active_count = len([cam for cam in all_cameras if cam["status"] == "active"])
        
        return {
            "cameras": all_cameras,
            "total_cameras": len(all_cameras),
            "active_cameras": active_count,
            "inactive_cameras": len(all_cameras) - active_count,
            "detection_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
    except Exception as e:
        logger.error(f"Failed to get camera status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get camera status: {str(e)}"
        )

@router.get("/detect")
async def detect_available_cameras(
    current_user: CurrentUser = Depends(require_admin_or_above)
):
    """
    Detect all available cameras using comprehensive auto-detection (Admin+ only)
    """
    try:
        # Use comprehensive auto-detection
        try:
            from backend.utils.auto_camera_detector import get_auto_detector
            auto_detector = get_auto_detector()
            detected_cameras = auto_detector.detect_all_cameras()
        except ImportError:
            detected_cameras = []
        
        # Convert to API response format
        camera_list = []
        for cam in detected_cameras:
            camera_list.append({
                "id": cam.camera_id,
                "name": cam.name,
                "type": cam.type,
                "source": cam.source,
                "resolution": f"{cam.resolution[0]}x{cam.resolution[1]}",
                "fps": cam.fps,
                "status": cam.status,
                "is_working": cam.is_working,
                "ip_address": cam.ip_address,
                "stream_url": cam.stream_url,
                "last_seen": cam.last_seen.isoformat()
            })
        
        return {
            "detected_cameras": camera_list,
            "total_detected": len(camera_list),
            "detection_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "auto_detection_active": True,
            "fts_integration": True
        }
    except Exception as e:
        logger.error(f"Camera detection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Camera detection failed: {str(e)}"
        )

@router.get("/health")
async def streaming_health_check(
    current_user: CurrentUser = Depends(require_admin_or_above)
):
    """
    Health check for streaming service (Admin+ only)
    """
    try:
        # Test camera detection
        cameras = detect_cameras()
        
        return {
            "status": "healthy",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "cameras_detected": len(cameras),
            "opencv_version": cv2.__version__,
            "streaming_active": len(active_streams)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
