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
from app.security import require_admin_or_above
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
        
        if fts_functions['is_tracking_running']:
            return MessageResponse(
                success=False,
                message="Face detection system is already running"
            )
        
        fts_functions['start_tracking_service']()
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
        
        if not fts_functions['is_tracking_running']:
            return MessageResponse(
                success=False,
                message="Face detection system is not running"
            )
        
        fts_functions['shutdown_tracking_service']()
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