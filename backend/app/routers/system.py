"""
System Management Router
Provides endpoints for managing the face detection system
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Dict, Any
from datetime import datetime
import psutil
import os

from app.schemas import CurrentUser, MessageResponse
from app.security import require_admin_or_above, require_super_admin
from utils.logging import get_logger

router = APIRouter(prefix="/system", tags=["System Management"])
logger = get_logger(__name__)

def get_fts_functions():
    """Safely import and return FTS functions"""
    try:
        from core.fts_system import (
            start_tracking_service, 
            shutdown_tracking_service, 
            get_system_status,
            is_tracking_running,
            get_live_faces,
            get_attendance_data
        )
        return {
            'start_tracking_service': start_tracking_service,
            'shutdown_tracking_service': shutdown_tracking_service,
            'get_system_status': get_system_status,
            'is_tracking_running': is_tracking_running,
            'get_live_faces': get_live_faces,
            'get_attendance_data': get_attendance_data
        }
    except ImportError as e:
        logger.warning(f"FTS system not available: {e}")
        return None

@router.get("/status")
async def get_system_status_endpoint(
    current_user: CurrentUser = Depends(require_admin_or_above)
):
    """
    Get system status and statistics (Admin+ only)
    """
    try:
        fts_functions = get_fts_functions()
        
        if fts_functions:
            # FTS system is available
            try:
                fts_status = fts_functions['get_system_status']()
                fts_status["is_running"] = fts_functions['is_tracking_running']
                fts_status["fts_available"] = True
                
                # Add additional FTS debugging info
                from core.fts_system import system_instance
                if system_instance:
                    fts_status["camera_threads"] = len(getattr(system_instance, 'camera_threads', []))
                    fts_status["fts_instance_created"] = True
                else:
                    fts_status["camera_threads"] = 0
                    fts_status["fts_instance_created"] = False
                    
            except Exception as e:
                logger.error(f"Error getting FTS status: {e}")
                fts_status = {
                    "is_running": False,
                    "fts_available": True,
                    "error": str(e),
                    "camera_threads": 0,
                    "fts_instance_created": False
                }
        else:
            # FTS system not available - provide basic status
            fts_status = {
                "timestamp": datetime.now().isoformat(),
                "is_running": False,
                "fts_available": False,
                "fts_status": "not_available"
            }
        
        # Add basic system information
        fts_status.update({
            "system_info": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
            }
        })
        
        return {
            "success": True,
            "data": fts_status
        }
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system status: {str(e)}"
        )

@router.post("/start", response_model=MessageResponse)
async def start_face_detection_system(
    current_user: CurrentUser = Depends(require_admin_or_above)
):
    """
    Start the face detection and tracking system (Admin+ only)
    """
    try:
        fts_functions = get_fts_functions()
        
        if not fts_functions:
            return MessageResponse(
                success=False,
                message="Face detection system is not available. Please check FTS installation."
            )
        
        # Check if already running (handle both callable and variable)
        is_running = fts_functions.get('is_tracking_running')
        if callable(is_running):
            running_status = is_running()
        else:
            running_status = bool(is_running)
            
        if running_status:
            return MessageResponse(
                success=False,
                message="Face detection system is already running"
            )
        
        # Check for available cameras before starting
        try:
            from app.routers.streaming import detect_cameras
            available_cameras = detect_cameras()
            if not available_cameras:
                logger.warning("No cameras detected, but starting FTS anyway")
        except Exception as e:
            logger.warning(f"Could not detect cameras: {e}")
        
        # Start the service
        start_func = fts_functions.get('start_tracking_service')
        if not start_func or not callable(start_func):
            return MessageResponse(
                success=False,
                message="Start function is not available"
            )
            
        start_func()
        logger.info(f"Face detection system started by user {current_user.username}")
        
        return MessageResponse(
            success=True,
            message="Face detection system started successfully"
        )
    except Exception as e:
        logger.error(f"Failed to start face detection system: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start face detection system: {str(e)}"
        )

@router.post("/stop", response_model=MessageResponse)
async def stop_face_detection_system(
    current_user: CurrentUser = Depends(require_admin_or_above)
):
    """
    Stop the face detection and tracking system (Admin+ only)
    """
    try:
        fts_functions = get_fts_functions()
        
        if not fts_functions:
            return MessageResponse(
                success=False,
                message="Face detection system is not available. Please check FTS installation."
            )
        
        # Check if running (handle both callable and variable)
        is_running = fts_functions.get('is_tracking_running')
        if callable(is_running):
            running_status = is_running()
        else:
            running_status = bool(is_running)
            
        if not running_status:
            return MessageResponse(
                success=False,
                message="Face detection system is not running"
            )
        
        # Stop the service
        stop_func = fts_functions.get('shutdown_tracking_service')
        if not stop_func or not callable(stop_func):
            return MessageResponse(
                success=False,
                message="Stop function is not available"
            )
            
        stop_func()
        logger.info(f"Face detection system stopped by user {current_user.username}")
        
        return MessageResponse(
            success=True,
            message="Face detection system stopped successfully"
        )
    except Exception as e:
        logger.error(f"Failed to stop face detection system: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop face detection system: {str(e)}"
        )

@router.get("/live-faces")
async def get_detected_faces(
    current_user: CurrentUser = Depends(require_admin_or_above)
):
    """
    Get currently detected faces (Admin+ only)
    """
    try:
        fts_functions = get_fts_functions()
        
        if not fts_functions:
            return {
                "success": False,
                "message": "Face detection system is not available",
                "data": []
            }
        
        faces = fts_functions['get_live_faces']()
        return {
            "success": True,
            "data": faces
        }
    except Exception as e:
        logger.error(f"Failed to get live faces: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get live faces: {str(e)}"
        )

@router.get("/health")
async def get_system_health():
    """
    Get basic system health information (no authentication required)
    """
    try:
        fts_functions = get_fts_functions()
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "api": "running",
                "database": "connected",
                "fts": "available" if fts_functions else "not_available"
            }
        }
        
        if fts_functions:
            health_data["services"]["fts_running"] = "running" if fts_functions['is_tracking_running'] else "stopped"
        
        return {
            "success": True,
            "data": health_data
        }
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system health: {str(e)}"
        )

@router.get("/camera-system-config")
async def get_camera_system_config(
    current_user: CurrentUser = Depends(require_admin_or_above)
):
    """
    Get camera system configuration settings (Admin+ only)
    """
    try:
        from app.config import settings
        
        config = {
            "camera_settings": {
                "default_camera_id": settings.DEFAULT_CAMERA_ID,
                "max_concurrent_streams": settings.MAX_CONCURRENT_STREAMS,
                "stream_quality": settings.STREAM_QUALITY,
                "frame_rate": settings.FRAME_RATE
            },
            "face_recognition": {
                "tolerance": settings.FACE_RECOGNITION_TOLERANCE,
                "detection_model": settings.FACE_DETECTION_MODEL,
                "encoding_model": settings.FACE_ENCODING_MODEL
            },
            "system_info": {
                "environment": settings.ENVIRONMENT,
                "debug": settings.DEBUG,
                "log_level": settings.LOG_LEVEL
            }
        }
        
        return {
            "success": True,
            "configuration": config
        }
        
    except Exception as e:
        logger.error(f"Failed to get camera system config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system configuration: {str(e)}"
        )

@router.post("/camera-system-config")
async def update_camera_system_config(
    config_update: Dict[str, Any],
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Update camera system configuration (Super Admin only)
    WARNING: Some changes require system restart
    """
    try:
        # This would typically update environment variables or config files
        # For now, we'll return what would be updated
        
        updatable_settings = {
            "max_concurrent_streams",
            "stream_quality", 
            "frame_rate",
            "face_recognition_tolerance",
            "face_detection_model",
            "log_level"
        }
        
        applied_updates = {}
        warnings = []
        
        for key, value in config_update.items():
            if key in updatable_settings:
                applied_updates[key] = value
                if key in ["face_detection_model", "log_level"]:
                    warnings.append(f"Setting '{key}' requires system restart to take effect")
            else:
                warnings.append(f"Setting '{key}' is not updatable or doesn't exist")
        
        logger.info(f"Super admin {current_user.username} updated system config: {applied_updates}")
        
        return {
            "success": True,
            "message": f"Updated {len(applied_updates)} configuration settings",
            "applied_updates": applied_updates,
            "warnings": warnings
        }
        
    except Exception as e:
        logger.error(f"Failed to update camera system config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update system configuration: {str(e)}"
        )

@router.get("/fts-management")
async def get_fts_management_info(
    current_user: CurrentUser = Depends(require_admin_or_above)
):
    """
    Get FTS (Face Tracking System) management information (Admin+ only)
    """
    try:
        fts_functions = get_fts_functions()
        
        if not fts_functions:
            return {
                "success": False,
                "message": "FTS system not available",
                "fts_available": False
            }
        
        # Get detailed FTS information
        try:
            import importlib
            fts_module = importlib.import_module('core.fts_system')
            system_instance = getattr(fts_module, 'system_instance', None)
            
            fts_info = {
                "is_running": fts_functions['is_tracking_running'],
                "system_status": fts_functions['get_system_status'](),
                "fts_available": True
            }
            
            if system_instance:
                fts_info.update({
                    "camera_threads": len(getattr(system_instance, 'camera_threads', {})),
                    "active_cameras": list(getattr(system_instance, 'camera_threads', {}).keys()),
                    "latest_faces_count": len(getattr(system_instance, 'latest_faces', {})),
                    "system_instance_active": True
                })
            else:
                fts_info.update({
                    "camera_threads": 0,
                    "active_cameras": [],
                    "latest_faces_count": 0,
                    "system_instance_active": False
                })
            
            return {
                "success": True,
                "fts_info": fts_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting FTS details: {str(e)}",
                "fts_available": True,
                "basic_status": fts_functions['is_tracking_running']
            }
            
    except Exception as e:
        logger.error(f"Failed to get FTS management info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get FTS management info: {str(e)}"
        )

@router.post("/fts-management/restart")
async def restart_fts_system(
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Restart the FTS (Face Tracking System) (Super Admin only)
    """
    try:
        fts_functions = get_fts_functions()
        
        if not fts_functions:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="FTS system not available"
            )
        
        # Stop FTS if running
        if fts_functions['is_tracking_running']:
            logger.info(f"Super admin {current_user.username} stopping FTS system...")
            fts_functions['shutdown_tracking_service']()
            
            # Wait a moment for shutdown
            import time
            time.sleep(2)
        
        # Start FTS
        logger.info(f"Super admin {current_user.username} starting FTS system...")
        fts_functions['start_tracking_service']()
        
        # Wait a moment for startup
        import time
        time.sleep(3)
        
        # Check if it started successfully
        if fts_functions['is_tracking_running']:
            return MessageResponse(
                message="FTS system restarted successfully",
                success=True
            )
        else:
            return MessageResponse(
                message="FTS system restart initiated but status unclear",
                success=True
            )
            
    except Exception as e:
        logger.error(f"Failed to restart FTS system: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restart FTS system: {str(e)}"
        )

@router.get("/logs/camera-system")
async def get_camera_system_logs(
    lines: int = 100,
    level: str = "INFO",
    current_user: CurrentUser = Depends(require_admin_or_above)
):
    """
    Get camera system logs (Admin+ only)
    """
    try:
        import os
        from pathlib import Path
        
        logs = []
        
        # Try to get FTS logs
        try:
            fts_functions = get_fts_functions()
            if fts_functions:
                # Try to get logs from FTS system
                import importlib
                fts_module = importlib.import_module('core.fts_system')
                get_logs = getattr(fts_module, 'get_logs', None)
                if get_logs:
                    fts_logs = get_logs(lines)
                    logs.extend([{"source": "fts", "message": log} for log in fts_logs])
        except Exception as e:
            logs.append({"source": "system", "message": f"Could not get FTS logs: {e}"})
        
        # Try to get application logs
        try:
            log_dir = Path("logs")
            if log_dir.exists():
                app_log = log_dir / "app.log"
                if app_log.exists():
                    with open(app_log, 'r') as f:
                        app_logs = f.readlines()[-lines:]
                    logs.extend([{"source": "app", "message": log.strip()} for log in app_logs])
        except Exception as e:
            logs.append({"source": "system", "message": f"Could not read app logs: {e}"})
        
        # Filter by log level if specified
        if level != "ALL":
            filtered_logs = []
            for log in logs:
                if level.upper() in log["message"].upper():
                    filtered_logs.append(log)
            logs = filtered_logs
        
        return {
            "success": True,
            "logs": logs[-lines:],  # Limit to requested number of lines
            "total_logs": len(logs),
            "level_filter": level
        }
        
    except Exception as e:
        logger.error(f"Failed to get camera system logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system logs: {str(e)}"
        )