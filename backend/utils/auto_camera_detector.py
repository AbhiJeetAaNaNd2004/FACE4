#!/usr/bin/env python3
"""
Automatic Camera Detection and Integration System
Detects all available cameras and integrates them with the FTS system
"""

import cv2
import os
import time
import logging
import threading
import requests
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
import socket
import subprocess
import platform

from db.db_manager import DatabaseManager
from db.db_models import CameraConfig as DBCameraConfig
from utils.camera_discovery import discover_cameras_on_network

logger = logging.getLogger(__name__)

@dataclass
class DetectedCamera:
    """Represents a detected camera"""
    camera_id: int
    name: str
    type: str  # "USB", "Built-in", "IP", "RTSP"
    source: str  # Camera index, IP address, or stream URL
    resolution: Tuple[int, int]
    fps: int
    status: str
    last_seen: datetime
    is_working: bool = True
    ip_address: Optional[str] = None
    stream_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class AutoCameraDetector:
    """
    Automatically detects and manages all available cameras for FTS integration
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.detected_cameras: Dict[int, DetectedCamera] = {}
        self.detection_lock = threading.Lock()
        self.running = False
        self.detection_thread = None
        
    async def detect_all_cameras(self) -> List[DetectedCamera]:
        """
        Detect all available cameras on the system and automatically store them
        
        Returns:
            List of detected cameras
        """
        logger.info("Starting comprehensive camera detection...")
        
        all_cameras = []
        
        # 1. Detect USB and built-in cameras (use sequential IDs 0, 1, 2, etc.)
        usb_cameras = self._detect_usb_cameras()
        for i, camera in enumerate(usb_cameras):
            camera.camera_id = i  # Use sequential camera IDs for local cameras
            all_cameras.append(camera)
        
        # 2. Detect IP cameras via ONVIF discovery (continue sequential numbering)
        ip_cameras = await self._detect_ip_cameras()
        start_id = len(usb_cameras)
        for i, camera in enumerate(ip_cameras):
            camera.camera_id = start_id + i
            all_cameras.append(camera)
        
        # 3. Check for cameras in database that might not be auto-detected
        db_cameras = self._get_database_cameras()
        start_id = len(usb_cameras) + len(ip_cameras)
        for i, camera in enumerate(db_cameras):
            # Only add if not already detected
            if not any(c.source == camera.source for c in all_cameras):
                camera.camera_id = start_id + i
                all_cameras.append(camera)
        
        # 4. Test and validate all detected cameras
        working_cameras = self._validate_cameras(all_cameras)
        
        # 5. Automatically store working cameras in database with default tripwires
        await self._auto_store_cameras_with_tripwires(working_cameras)
        
        logger.info(f"Detected {len(working_cameras)} working cameras out of {len(all_cameras)} total")
        
        with self.detection_lock:
            self.detected_cameras = {cam.camera_id: cam for cam in working_cameras}
        
        return working_cameras
    
    def _detect_usb_cameras(self) -> List[DetectedCamera]:
        """Detect USB and built-in cameras"""
        cameras = []
        logger.info("Scanning for USB/built-in cameras...")
        
        # Check indices 0-5 for USB cameras (reduced range to minimize errors)
        for i in range(5):
            try:
                # Suppress OpenCV errors during camera detection
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW if platform.system() == "Windows" else cv2.CAP_V4L2)
                
                # Set a timeout for camera initialization
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                if cap.isOpened():
                    # Try to read a frame to verify camera is working
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        # Get camera properties
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = int(cap.get(cv2.CAP_PROP_FPS))
                        
                        # Determine camera type
                        camera_type = "Built-in" if i == 0 else "USB"
                        
                        camera = DetectedCamera(
                            camera_id=i,
                            name=f"{camera_type} Camera {i}",
                            type=camera_type,
                            source=str(i),
                            resolution=(width if width > 0 else 640, height if height > 0 else 480),
                            fps=fps if fps > 0 else 30,
                            status="active",
                            last_seen=datetime.now(),
                            is_working=True
                        )
                        
                        cameras.append(camera)
                        logger.info(f"Detected {camera_type} camera {i}: {width}x{height} @ {fps}fps")
                    
                    cap.release()
                    
            except Exception as e:
                logger.debug(f"Failed to check camera index {i}: {e}")
                continue
        
        return cameras
    
    async def _detect_ip_cameras(self) -> List[DetectedCamera]:
        """Detect IP cameras via network discovery"""
        cameras = []
        logger.info("Scanning for IP cameras...")
        
        try:
            # Use ONVIF discovery
            discovered_cameras = await discover_cameras_on_network(timeout=5)
            
            for i, cam_info in enumerate(discovered_cameras):
                try:
                    camera = DetectedCamera(
                        camera_id=1000 + i,  # Start IP cameras at 1000
                        name=cam_info.get('name', f"IP Camera {cam_info['ip']}"),
                        type="IP",
                        source=cam_info['stream_url'],
                        resolution=(1920, 1080),  # Default, will be updated during validation
                        fps=25,  # Default
                        status="active",
                        last_seen=datetime.now(),
                        is_working=True,
                        ip_address=cam_info['ip'],
                        stream_url=cam_info['stream_url'],
                        username=cam_info.get('username'),
                        password=cam_info.get('password')
                    )
                    
                    cameras.append(camera)
                    logger.info(f"Discovered IP camera at {cam_info['ip']}")
                    
                except Exception as e:
                    logger.warning(f"Failed to process discovered camera {cam_info}: {e}")
                    
        except Exception as e:
            logger.warning(f"IP camera discovery failed: {e}")
            
        # Also scan common IP camera addresses
        cameras.extend(self._scan_common_ip_addresses())
        
        return cameras
    
    def _scan_common_ip_addresses(self) -> List[DetectedCamera]:
        """Scan common IP camera addresses on local network"""
        cameras = []
        
        # Get local network range
        try:
            # Get local IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Extract network base (assuming /24 subnet)
            network_base = '.'.join(local_ip.split('.')[:-1])
            
            # Common camera ports and paths
            common_ports = [80, 554, 8080, 8081, 8554]
            common_paths = [
                '/stream',
                '/video',
                '/cam/realmonitor?channel=1&subtype=0',
                '/h264',
                '/mjpeg',
                '/stream1'
            ]
            
            # Scan last 50 IPs in range (to avoid too long scan)
            for ip_suffix in range(200, 250):
                ip = f"{network_base}.{ip_suffix}"
                
                for port in common_ports:
                    if self._check_ip_camera_port(ip, port):
                        # Try different stream URLs
                        for path in common_paths:
                            if port == 554:
                                stream_url = f"rtsp://{ip}:{port}{path}"
                            else:
                                stream_url = f"http://{ip}:{port}{path}"
                            
                            # Quick test
                            if self._test_stream_url(stream_url, timeout=2):
                                camera = DetectedCamera(
                                    camera_id=2000 + len(cameras),
                                    name=f"IP Camera {ip}",
                                    type="IP",
                                    source=stream_url,
                                    resolution=(1280, 720),
                                    fps=25,
                                    status="active",
                                    last_seen=datetime.now(),
                                    is_working=True,
                                    ip_address=ip,
                                    stream_url=stream_url
                                )
                                cameras.append(camera)
                                logger.info(f"Found IP camera at {stream_url}")
                                break  # Found working stream for this IP
                        
                        if cameras and cameras[-1].ip_address == ip:
                            break  # Found working camera for this IP
        
        except Exception as e:
            logger.warning(f"IP scanning failed: {e}")
        
        return cameras
    
    def _check_ip_camera_port(self, ip: str, port: int, timeout: float = 1.0) -> bool:
        """Check if a port is open on an IP address"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def _test_stream_url(self, url: str, timeout: float = 3.0) -> bool:
        """Test if a stream URL is accessible"""
        try:
            cap = cv2.VideoCapture(url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Set timeout for connection
            start_time = time.time()
            
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                
                if ret and frame is not None and time.time() - start_time < timeout:
                    return True
            else:
                cap.release()
            
            return False
            
        except Exception as e:
            logger.debug(f"Stream test failed for {url}: {e}")
            return False
    
    def _get_database_cameras(self) -> List[DetectedCamera]:
        """Get cameras from database configuration"""
        cameras = []
        
        try:
            db_cameras = self.db_manager.get_all_cameras()
            
            for db_cam in db_cameras:
                # Convert database camera to detected camera
                source = db_cam.stream_url or str(db_cam.camera_id)
                
                camera = DetectedCamera(
                    camera_id=db_cam.camera_id,
                    name=db_cam.name,
                    type=db_cam.camera_type,
                    source=source,
                    resolution=(1280, 720),  # Default
                    fps=25,
                    status="active" if db_cam.is_active else "inactive",
                    last_seen=datetime.now(),
                    is_working=True,
                    ip_address=db_cam.ip_address,
                    stream_url=db_cam.stream_url,
                    username=db_cam.username,
                    password=db_cam.password
                )
                
                cameras.append(camera)
                
        except Exception as e:
            logger.warning(f"Failed to load database cameras: {e}")
        
        return cameras
    
    def _validate_cameras(self, cameras: List[DetectedCamera]) -> List[DetectedCamera]:
        """Validate that detected cameras are actually working"""
        working_cameras = []
        
        for camera in cameras:
            try:
                logger.info(f"Validating camera: {camera.name}")
                
                # Test camera access
                if camera.type in ["USB", "Built-in"]:
                    # Test USB/built-in camera
                    cap = cv2.VideoCapture(int(camera.source))
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            # Update actual resolution
                            h, w = frame.shape[:2]
                            camera.resolution = (w, h)
                            camera.is_working = True
                            working_cameras.append(camera)
                        cap.release()
                    
                elif camera.type == "IP":
                    # Test IP camera
                    if self._test_stream_url(camera.source, timeout=5):
                        # Try to get actual resolution
                        cap = cv2.VideoCapture(camera.source)
                        if cap.isOpened():
                            ret, frame = cap.read()
                            if ret and frame is not None:
                                h, w = frame.shape[:2]
                                camera.resolution = (w, h)
                            cap.release()
                        
                        camera.is_working = True
                        working_cameras.append(camera)
                
            except Exception as e:
                logger.warning(f"Camera validation failed for {camera.name}: {e}")
                camera.is_working = False
        
        return working_cameras
    
    async def _auto_store_cameras_with_tripwires(self, cameras: List[DetectedCamera]) -> None:
        """Automatically store detected cameras in database with default tripwire configuration."""
        logger.info("Automatically storing detected cameras with default tripwires...")
        
        for camera in cameras:
            try:
                # Check if camera already exists in database
                existing = self.db_manager.get_camera(camera.camera_id)
                
                if existing:
                    # Update existing camera
                    update_data = {
                        'camera_name': camera.name,
                        'camera_type': camera.type.lower(),
                        'is_active': camera.is_working,
                        'stream_url': camera.stream_url,
                        'ip_address': camera.ip_address,
                        'username': camera.username,
                        'password': camera.password,
                        'resolution_width': camera.resolution[0],
                        'resolution_height': camera.resolution[1],
                        'fps': camera.fps,
                        'status': 'active' if camera.is_working else 'inactive'
                    }
                    
                    self.db_manager.update_camera(camera.camera_id, update_data)
                    logger.info(f"Updated existing camera {camera.camera_id}: {camera.name}")
                    
                else:
                    # Create new camera in database
                    camera_data = {
                        'camera_id': camera.camera_id,
                        'camera_name': camera.name,
                        'camera_type': camera.type.lower() if camera.type.lower() in ['entry', 'exit', 'general'] else 'entry',
                        'gpu_id': 0,
                        'stream_url': camera.stream_url,
                        'ip_address': camera.ip_address,
                        'username': camera.username,
                        'password': camera.password,
                        'resolution_width': camera.resolution[0],
                        'resolution_height': camera.resolution[1],
                        'fps': camera.fps,
                        'is_active': True,
                        'status': 'active',
                        'location_description': f"Auto-detected {camera.type} camera"
                    }
                    
                    created_camera = self.db_manager.create_camera(camera_data)
                    if created_camera:
                        logger.info(f"Created new camera {camera.camera_id}: {camera.name}")
                        
                        # Create default tripwire for the new camera
                        tripwire_data = {
                            'name': 'EntryDetection',
                            'position': 0.5,
                            'spacing': 0.01,
                            'direction': 'horizontal',
                            'detection_type': 'entry',
                            'is_active': True
                        }
                        
                        tripwire = self.db_manager.create_tripwire(camera.camera_id, tripwire_data)
                        if tripwire:
                            logger.info(f"Created default tripwire for camera {camera.camera_id}: {camera.name}")
                        else:
                            logger.warning(f"Failed to create tripwire for camera {camera.camera_id}: {camera.name}")
                    else:
                        logger.error(f"Failed to create camera {camera.camera_id}: {camera.name}")
                        
            except Exception as e:
                logger.error(f"Error storing camera {camera.camera_id}: {e}")
        
        logger.info("Finished automatically storing detected cameras with default tripwires")
    
    def sync_to_database(self, cameras: List[DetectedCamera]) -> None:
        """Synchronize detected cameras to database"""
        logger.info("Synchronizing detected cameras to database...")
        
        try:
            for camera in cameras:
                # Check if camera exists in database
                existing = self.db_manager.get_camera(camera.camera_id)
                
                if existing:
                    # Update existing camera
                    existing.name = camera.name
                    existing.camera_type = camera.type.lower()
                    existing.is_active = camera.is_working
                    existing.stream_url = camera.stream_url
                    existing.ip_address = camera.ip_address
                    existing.username = camera.username
                    existing.password = camera.password
                    existing.resolution_width = camera.resolution[0]
                    existing.resolution_height = camera.resolution[1]
                    existing.fps = camera.fps
                    
                    self.db_manager.update_camera(existing)
                    logger.info(f"Updated camera {camera.camera_id} in database")
                    
                else:
                    # Create new camera in database
                    db_camera = DBCameraConfig(
                        camera_id=camera.camera_id,
                        name=camera.name,
                        camera_type=camera.type.lower(),
                        gpu_id=0,  # Will be assigned by FTS system
                        stream_url=camera.stream_url,
                        ip_address=camera.ip_address,
                        username=camera.username,
                        password=camera.password,
                        port=554 if camera.type == "IP" else None,
                        protocol="rtsp" if camera.stream_url and "rtsp" in camera.stream_url else "http",
                        resolution_width=camera.resolution[0],
                        resolution_height=camera.resolution[1],
                        fps=camera.fps,
                        is_active=camera.is_working,
                        location_description=f"Auto-detected {camera.type} camera"
                    )
                    
                    self.db_manager.create_camera(db_camera)
                    logger.info(f"Added new camera {camera.camera_id} to database")
        
        except Exception as e:
            logger.error(f"Failed to sync cameras to database: {e}")
    
    def get_detected_cameras(self) -> List[DetectedCamera]:
        """Get list of detected cameras"""
        with self.detection_lock:
            return list(self.detected_cameras.values())
    
    def start_continuous_detection(self, interval: int = 300) -> None:
        """Start continuous camera detection in background"""
        if self.running:
            logger.warning("Continuous detection already running")
            return
        
        self.running = True
        self.detection_thread = threading.Thread(
            target=self._continuous_detection_worker,
            args=(interval,),
            daemon=True
        )
        self.detection_thread.start()
        logger.info(f"Started continuous camera detection (interval: {interval}s)")
    
    def stop_continuous_detection(self) -> None:
        """Stop continuous camera detection"""
        self.running = False
        if self.detection_thread:
            self.detection_thread.join(timeout=5)
        logger.info("Stopped continuous camera detection")
    
    def _continuous_detection_worker(self, interval: int) -> None:
        """Worker thread for continuous camera detection"""
        import asyncio
        
        async def async_detection_work():
            while self.running:
                try:
                    # Run detection
                    cameras = await self.detect_all_cameras()
                    
                    # Sync to database
                    self.sync_to_database(cameras)
                    
                    # Wait for next detection cycle
                    for _ in range(interval):
                        if not self.running:
                            break
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    logger.error(f"Error in continuous detection: {e}")
                    await asyncio.sleep(10)  # Wait before retrying
        
        # Run the async function in this thread
        asyncio.run(async_detection_work())

# Global instance
auto_detector = AutoCameraDetector()

def get_auto_detector() -> AutoCameraDetector:
    """Get the global auto detector instance"""
    return auto_detector

async def detect_all_available_cameras() -> List[DetectedCamera]:
    """Convenience function to detect all cameras"""
    return await auto_detector.detect_all_cameras()

def start_auto_detection(interval: int = 300) -> None:
    """Start automatic camera detection"""
    auto_detector.start_continuous_detection(interval)

def stop_auto_detection() -> None:
    """Stop automatic camera detection"""
    auto_detector.stop_continuous_detection()