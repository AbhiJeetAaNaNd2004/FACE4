"""
Camera Management API Router
Provides endpoints for camera discovery, configuration, and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.schemas import (
    CurrentUser, MessageResponse,
    CameraDiscoveryRequest, CameraDiscoveryResponse, CameraDiscoveryResult,
    CameraConfigurationRequest, CameraActivationRequest,
    CameraInfo, CameraListResponse, CameraStatusResponse,
    CameraCreate, CameraUpdate, TripwireCreate, TripwireUpdate, Tripwire,
    CameraSettingsUpdate
)
from app.security import require_admin_or_above, require_super_admin
from db.db_manager import DatabaseManager
from utils.camera_discovery import discover_cameras_on_network, CameraInfo as DiscoveredCameraInfo
from utils.logging import get_logger

router = APIRouter(prefix="/cameras", tags=["Camera Management"])
logger = get_logger(__name__)

# Background task storage for discovery operations
discovery_tasks = {}

@router.post("/discover", response_model=CameraDiscoveryResponse)
async def discover_cameras(
    request: CameraDiscoveryRequest,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Discover cameras on the network using ONVIF and port scanning
    (Super Admin only)
    """
    try:
        start_time = time.time()
        
        # Perform camera discovery
        discovered_cameras = await discover_cameras_on_network(
            network_range=request.network_range,
            timeout=request.timeout
        )
        
        discovery_time = time.time() - start_time
        
        # Convert to response format
        camera_results = []
        for camera in discovered_cameras:
            camera_results.append(CameraDiscoveryResult(
                ip_address=camera.ip_address,
                port=camera.port,
                manufacturer=camera.manufacturer,
                model=camera.model,
                firmware_version=camera.firmware_version,
                stream_urls=camera.stream_urls,
                onvif_supported=camera.onvif_supported,
                device_service_url=camera.device_service_url,
                media_service_url=camera.media_service_url
            ))
        
        # Store discovered cameras in database
        if camera_results:
            background_tasks.add_task(
                _store_discovered_cameras,
                [camera.__dict__ for camera in discovered_cameras]
            )
        
        logger.info(f"Discovered {len(camera_results)} cameras in {discovery_time:.2f}s")
        
        return CameraDiscoveryResponse(
            discovered_cameras=camera_results,
            total_discovered=len(camera_results),
            discovery_time=discovery_time,
            network_range=request.network_range
        )
        
    except Exception as e:
        logger.error(f"Camera discovery failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Camera discovery failed: {str(e)}"
        )

@router.get("/", response_model=CameraListResponse)
async def get_cameras(
    status_filter: Optional[str] = None,
    active_only: bool = False,
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Get list of all cameras with optional filtering
    (Super Admin only)
    """
    try:
        db_manager = DatabaseManager()
        
        if active_only:
            cameras = db_manager.get_active_cameras()
        elif status_filter:
            cameras = db_manager.get_cameras_by_status(status_filter)
        else:
            cameras = db_manager.get_all_cameras()
        
        # Convert to response format
        camera_infos = []
        for camera in cameras:
            tripwires = db_manager.get_camera_tripwires(camera.camera_id)
            camera_info = CameraInfo(
                id=camera.id,
                camera_id=camera.camera_id,
                camera_name=camera.name,
                camera_type=camera.camera_type,
                ip_address=camera.ip_address,
                stream_url=camera.stream_url,
                location_description=camera.location_description,
                resolution_width=camera.resolution_width,
                resolution_height=camera.resolution_height,
                fps=camera.fps,
                gpu_id=camera.gpu_id,
                manufacturer=camera.manufacturer,
                model=camera.model,
                firmware_version=camera.firmware_version,
                onvif_supported=camera.onvif_supported,
                status=camera.status,
                is_active=camera.is_active,
                created_at=camera.created_at,
                updated_at=camera.updated_at,
                tripwires=[Tripwire(
                    id=t.id,
                    camera_id=t.camera_id,
                    name=t.name,
                    position=t.position,
                    spacing=t.spacing,
                    direction=t.direction,
                    detection_type=t.detection_type,
                    is_active=t.is_active,
                    created_at=t.created_at,
                    updated_at=t.updated_at
                ) for t in tripwires]
            )
            camera_infos.append(camera_info)
        
        active_count = len([c for c in cameras if c.is_active])
        inactive_count = len(cameras) - active_count
        
        return CameraListResponse(
            cameras=camera_infos,
            total_count=len(cameras),
            active_count=active_count,
            inactive_count=inactive_count
        )
        
    except Exception as e:
        logger.error(f"Error getting cameras: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving cameras: {str(e)}"
        )

@router.get("/{camera_id}", response_model=CameraInfo)
async def get_camera(
    camera_id: int,
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Get detailed information about a specific camera
    (Super Admin only)
    """
    try:
        db_manager = DatabaseManager()
        camera = db_manager.get_camera(camera_id)
        
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camera {camera_id} not found"
            )
        
        tripwires = db_manager.get_camera_tripwires(camera_id)
        
        return CameraInfo(
            id=camera.id,
            camera_id=camera.camera_id,
            camera_name=camera.name,
            camera_type=camera.camera_type,
            ip_address=camera.ip_address,
            stream_url=camera.stream_url,
            location_description=camera.location_description,
            resolution_width=camera.resolution_width,
            resolution_height=camera.resolution_height,
            fps=camera.fps,
            gpu_id=camera.gpu_id,
            manufacturer=camera.manufacturer,
            model=camera.model,
            firmware_version=camera.firmware_version,
            onvif_supported=camera.onvif_supported,
            status=camera.status,
            is_active=camera.is_active,
            created_at=camera.created_at,
            updated_at=camera.updated_at,
            tripwires=[Tripwire(
                id=t.id,
                camera_id=t.camera_id,
                name=t.name,
                position=t.position,
                spacing=t.spacing,
                direction=t.direction,
                detection_type=t.detection_type,
                is_active=t.is_active,
                created_at=t.created_at,
                updated_at=t.updated_at
            ) for t in tripwires]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting camera {camera_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving camera: {str(e)}"
        )

@router.post("/", response_model=CameraInfo)
async def create_camera(
    camera_data: CameraCreate,
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Create a new camera configuration
    (Super Admin only)
    """
    try:
        db_manager = DatabaseManager()
        
        # Convert to dict for database manager
        camera_dict = camera_data.dict()
        
        camera = db_manager.create_camera(camera_dict)
        
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create camera"
            )
        
        return CameraInfo(
            id=camera.id,
            camera_id=camera.camera_id,
            camera_name=camera.name,
            camera_type=camera.camera_type,
            ip_address=camera.ip_address,
            stream_url=camera.stream_url,
            location_description=camera.location_description,
            resolution_width=camera.resolution_width,
            resolution_height=camera.resolution_height,
            fps=camera.fps,
            gpu_id=camera.gpu_id,
            manufacturer=camera.manufacturer,
            model=camera.model,
            firmware_version=camera.firmware_version,
            onvif_supported=camera.onvif_supported,
            status=camera.status,
            is_active=camera.is_active,
            created_at=camera.created_at,
            updated_at=camera.updated_at,
            tripwires=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating camera: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating camera: {str(e)}"
        )

@router.put("/{camera_id}", response_model=CameraInfo)
async def update_camera(
    camera_id: int,
    camera_data: CameraUpdate,
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Update camera configuration
    (Super Admin only)
    """
    try:
        db_manager = DatabaseManager()
        
        # Convert to dict, excluding None values
        update_dict = {k: v for k, v in camera_data.dict().items() if v is not None}
        
        camera = db_manager.update_camera(camera_id, update_dict)
        
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camera {camera_id} not found"
            )
        
        tripwires = db_manager.get_camera_tripwires(camera_id)
        
        return CameraInfo(
            id=camera.id,
            camera_id=camera.camera_id,
            camera_name=camera.name,
            camera_type=camera.camera_type,
            ip_address=camera.ip_address,
            stream_url=camera.stream_url,
            location_description=camera.location_description,
            resolution_width=camera.resolution_width,
            resolution_height=camera.resolution_height,
            fps=camera.fps,
            gpu_id=camera.gpu_id,
            manufacturer=camera.manufacturer,
            model=camera.model,
            firmware_version=camera.firmware_version,
            onvif_supported=camera.onvif_supported,
            status=camera.status,
            is_active=camera.is_active,
            created_at=camera.created_at,
            updated_at=camera.updated_at,
            tripwires=[Tripwire(
                id=t.id,
                camera_id=t.camera_id,
                name=t.name,
                position=t.position,
                spacing=t.spacing,
                direction=t.direction,
                detection_type=t.detection_type,
                is_active=t.is_active,
                created_at=t.created_at,
                updated_at=t.updated_at
            ) for t in tripwires]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating camera {camera_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating camera: {str(e)}"
        )

@router.post("/{camera_id}/configure", response_model=CameraInfo)
async def configure_camera(
    camera_id: int,
    config_data: CameraConfigurationRequest,
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Configure a discovered camera with tripwires and settings
    (Super Admin only)
    """
    try:
        db_manager = DatabaseManager()
        
        # Update camera configuration
        camera_update = {
            'camera_name': config_data.camera_name,
            'camera_type': config_data.camera_type,
            'location_description': config_data.location_description,
            'stream_url': config_data.stream_url,
            'username': config_data.username,
            'password': config_data.password,
            'resolution_width': config_data.resolution_width,
            'resolution_height': config_data.resolution_height,
            'fps': config_data.fps,
            'gpu_id': config_data.gpu_id,
            'status': 'configured'
        }
        
        camera = db_manager.update_camera(camera_id, camera_update)
        
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camera {camera_id} not found"
            )
        
        # Create tripwires
        tripwires = []
        for tripwire_data in config_data.tripwires:
            tripwire = db_manager.create_tripwire(camera_id, tripwire_data.dict())
            if tripwire:
                tripwires.append(tripwire)
        
        return CameraInfo(
            id=camera.id,
            camera_id=camera.camera_id,
            camera_name=camera.name,
            camera_type=camera.camera_type,
            ip_address=camera.ip_address,
            stream_url=camera.stream_url,
            location_description=camera.location_description,
            resolution_width=camera.resolution_width,
            resolution_height=camera.resolution_height,
            fps=camera.fps,
            gpu_id=camera.gpu_id,
            manufacturer=camera.manufacturer,
            model=camera.model,
            firmware_version=camera.firmware_version,
            onvif_supported=camera.onvif_supported,
            status=camera.status,
            is_active=camera.is_active,
            created_at=camera.created_at,
            updated_at=camera.updated_at,
            tripwires=[Tripwire(
                id=t.id,
                camera_id=t.camera_id,
                name=t.name,
                position=t.position,
                spacing=t.spacing,
                direction=t.direction,
                detection_type=t.detection_type,
                is_active=t.is_active,
                created_at=t.created_at,
                updated_at=t.updated_at
            ) for t in tripwires]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error configuring camera {camera_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error configuring camera: {str(e)}"
        )

@router.post("/{camera_id}/activate", response_model=MessageResponse)
async def activate_camera(
    camera_id: int,
    activation_data: CameraActivationRequest,
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Activate or deactivate a camera
    (Super Admin only)
    """
    try:
        db_manager = DatabaseManager()
        
        success = db_manager.activate_camera(camera_id, activation_data.is_active)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camera {camera_id} not found"
            )
        
        action = "activated" if activation_data.is_active else "deactivated"
        
        return MessageResponse(
            message=f"Camera {camera_id} {action} successfully",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating camera {camera_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error activating camera: {str(e)}"
        )

@router.delete("/{camera_id}", response_model=MessageResponse)
async def delete_camera(
    camera_id: int,
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Delete a camera configuration
    (Super Admin only)
    """
    try:
        db_manager = DatabaseManager()
        
        success = db_manager.delete_camera(camera_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camera {camera_id} not found"
            )
        
        return MessageResponse(
            message=f"Camera {camera_id} deleted successfully",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting camera {camera_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting camera: {str(e)}"
        )

@router.get("/{camera_id}/status", response_model=CameraStatusResponse)
async def get_camera_status(
    camera_id: int,
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Get real-time status of a camera
    (Super Admin only)
    """
    try:
        db_manager = DatabaseManager()
        camera = db_manager.get_camera(camera_id)
        
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camera {camera_id} not found"
            )
        
        # In a real implementation, this would check actual camera stream health
        # For now, we'll return mock status
        return CameraStatusResponse(
            camera_id=camera.camera_id,
            camera_name=camera.name,
            status=camera.status,
            is_active=camera.is_active,
            last_seen=camera.updated_at,
            stream_health="healthy" if camera.is_active else "offline",
            processing_load=0.3 if camera.is_active else 0.0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting camera status {camera_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting camera status: {str(e)}"
        )

# Tripwire management endpoints
@router.post("/{camera_id}/tripwires", response_model=Tripwire)
async def create_tripwire(
    camera_id: int,
    tripwire_data: TripwireCreate,
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Create a new tripwire for a camera
    (Super Admin only)
    """
    try:
        db_manager = DatabaseManager()
        
        tripwire = db_manager.create_tripwire(camera_id, tripwire_data.dict())
        
        if not tripwire:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camera {camera_id} not found"
            )
        
        return Tripwire(
            id=tripwire.id,
            camera_id=tripwire.camera_id,
            name=tripwire.name,
            position=tripwire.position,
            spacing=tripwire.spacing,
            direction=tripwire.direction,
            detection_type=tripwire.detection_type,
            is_active=tripwire.is_active,
            created_at=tripwire.created_at,
            updated_at=tripwire.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tripwire for camera {camera_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating tripwire: {str(e)}"
        )

@router.get("/{camera_id}/tripwires", response_model=List[Tripwire])
async def get_camera_tripwires(
    camera_id: int,
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Get all tripwires for a camera
    (Super Admin only)
    """
    try:
        db_manager = DatabaseManager()
        tripwires = db_manager.get_camera_tripwires(camera_id)
        
        return [Tripwire(
            id=t.id,
            camera_id=t.camera_id,
            name=t.name,
            position=t.position,
            spacing=t.spacing,
            direction=t.direction,
            detection_type=t.detection_type,
            is_active=t.is_active,
            created_at=t.created_at,
            updated_at=t.updated_at
        ) for t in tripwires]
        
    except Exception as e:
        logger.error(f"Error getting tripwires for camera {camera_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting tripwires: {str(e)}"
        )

@router.put("/tripwires/{tripwire_id}", response_model=Tripwire)
async def update_tripwire(
    tripwire_id: int,
    tripwire_data: TripwireUpdate,
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Update a tripwire configuration
    (Super Admin only)
    """
    try:
        db_manager = DatabaseManager()
        
        # Convert to dict, excluding None values
        update_dict = {k: v for k, v in tripwire_data.dict().items() if v is not None}
        
        tripwire = db_manager.update_tripwire(tripwire_id, update_dict)
        
        if not tripwire:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tripwire {tripwire_id} not found"
            )
        
        return Tripwire(
            id=tripwire.id,
            camera_id=tripwire.camera_id,
            name=tripwire.name,
            position=tripwire.position,
            spacing=tripwire.spacing,
            direction=tripwire.direction,
            detection_type=tripwire.detection_type,
            is_active=tripwire.is_active,
            created_at=tripwire.created_at,
            updated_at=tripwire.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tripwire {tripwire_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating tripwire: {str(e)}"
        )

@router.delete("/tripwires/{tripwire_id}", response_model=MessageResponse)
async def delete_tripwire(
    tripwire_id: int,
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Delete a tripwire
    (Super Admin only)
    """
    try:
        db_manager = DatabaseManager()
        
        success = db_manager.delete_tripwire(tripwire_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tripwire {tripwire_id} not found"
            )
        
        return MessageResponse(
            message=f"Tripwire {tripwire_id} deleted successfully",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tripwire {tripwire_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting tripwire: {str(e)}"
        )

# Background task function
async def _store_discovered_cameras(camera_data_list: List[dict]):
    """Background task to store discovered cameras in database"""
    try:
        db_manager = DatabaseManager()
        created_cameras = db_manager.bulk_create_cameras_from_discovery(camera_data_list)
        logger.info(f"Stored {len(created_cameras)} discovered cameras in database")
    except Exception as e:
        logger.error(f"Error storing discovered cameras: {e}")

@router.post("/reload-configurations", response_model=MessageResponse)
async def reload_camera_configurations(
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Reload camera configurations from database in the FTS system
    (Super Admin only)
    """
    try:
        # Import here to avoid circular imports
        from core.fts_system import system_instance
        
        if system_instance:
            system_instance.reload_camera_configurations()
            logger.info("Camera configurations reloaded in FTS system")
            return MessageResponse(
                message="Camera configurations reloaded successfully",
                success=True
            )
        else:
            logger.warning("FTS system not running, configurations will be loaded on next start")
            return MessageResponse(
                message="FTS system not running, configurations will be loaded on next start",
                success=True
            )
        
    except Exception as e:
        logger.error(f"Error reloading camera configurations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reloading camera configurations: {str(e)}"
        )

@router.post("/auto-detect", response_model=MessageResponse)
async def auto_detect_cameras(
    current_user: CurrentUser = Depends(require_admin_or_above)
):
    """
    Automatically detect all available cameras and configure them (Admin+ only)
    """
    try:
        from utils.auto_camera_detector import get_auto_detector
        
        # Get the auto detector instance
        auto_detector = get_auto_detector()
        
        # Run comprehensive camera detection
        detected_cameras = await auto_detector.detect_all_cameras()
        
        return MessageResponse(
            success=True,
            message=f"Successfully detected and configured {len(detected_cameras)} cameras"
        )
    except Exception as e:
        logger.error(f"Failed to auto-detect cameras: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to auto-detect cameras: {str(e)}"
        )

@router.post("/detect-all")
async def detect_all_cameras(
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Run comprehensive camera detection and return all found cameras (Super Admin only)
    """
    try:
        from utils.auto_camera_detector import get_auto_detector
        
        logger.info("Starting comprehensive camera detection...")
        auto_detector = get_auto_detector()
        
        # Run detection
        detected_cameras = await auto_detector.detect_all_cameras()
        
        # Convert to API response format with enhanced information
        camera_list = []
        for camera in detected_cameras:
            # Check if camera is already configured in FTS
            db_manager = DatabaseManager()
            db_camera = db_manager.get_camera_by_source(camera.source)
            
            camera_dict = {
                "camera_id": camera.camera_id,
                "name": camera.name,
                "type": camera.type,
                "source": camera.source,
                "resolution": f"{camera.resolution[0]}x{camera.resolution[1]}",
                "resolution_width": camera.resolution[0],
                "resolution_height": camera.resolution[1],
                "fps": camera.fps,
                "status": camera.status,
                "is_working": camera.is_working,
                "last_seen": camera.last_seen.isoformat() if camera.last_seen else None,
                "ip_address": camera.ip_address,
                "stream_url": camera.stream_url,
                "is_configured_for_fts": db_camera is not None,
                "fts_config": {
                    "database_id": db_camera.id if db_camera else None,
                    "enabled": db_camera.is_active if db_camera else False,
                    "camera_name": db_camera.name if db_camera else None,
                    "location": db_camera.location if db_camera else None
                } if db_camera else None
            }
            camera_list.append(camera_dict)
        
        return {
            "success": True,
            "data": {
                "detected_cameras": camera_list,
                "total_detected": len(camera_list),
                "working_cameras": len([c for c in detected_cameras if c.is_working]),
                "configured_cameras": len([c for c in camera_list if c["is_configured_for_fts"]]),
                "available_for_configuration": len([c for c in camera_list if c["is_working"] and not c["is_configured_for_fts"]])
            }
        }
    except Exception as e:
        logger.error(f"Failed to detect all cameras: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect cameras: {str(e)}"
        )

@router.get("/detected")
async def get_detected_cameras(
    current_user: CurrentUser = Depends(require_admin_or_above)
):
    """
    Get list of previously detected cameras from cache (Admin+ only)
    """
    try:
        from utils.auto_camera_detector import get_auto_detector
        
        auto_detector = get_auto_detector()
        detected_cameras = auto_detector.get_detected_cameras()
        
        # Convert to API response format
        camera_list = []
        for camera in detected_cameras:
            # Check if camera is already configured in FTS
            db_manager = DatabaseManager()
            db_camera = db_manager.get_camera_by_source(camera.source)
            
            camera_dict = {
                "camera_id": camera.camera_id,
                "name": camera.name,
                "type": camera.type,
                "source": camera.source,
                "resolution": f"{camera.resolution[0]}x{camera.resolution[1]}",
                "fps": camera.fps,
                "status": camera.status,
                "is_working": camera.is_working,
                "last_seen": camera.last_seen.isoformat() if camera.last_seen else None,
                "ip_address": camera.ip_address,
                "stream_url": camera.stream_url,
                "is_configured_for_fts": db_camera is not None
            }
            camera_list.append(camera_dict)
            
        return {
            "success": True,
            "data": {
                "detected_cameras": camera_list,
                "total_detected": len(camera_list),
                "working_cameras": len([c for c in detected_cameras if c.is_working])
            }
        }
    except Exception as e:
        logger.error(f"Failed to get detected cameras: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get detected cameras: {str(e)}"
        )

@router.put("/{camera_id}/settings", response_model=MessageResponse)
async def update_camera_settings(
    camera_id: int,
    settings: CameraSettingsUpdate,
    current_user: CurrentUser = Depends(require_admin_or_above)
):
    """
    Update camera settings like name, resolution, FPS, etc. (Admin+ only)
    """
    try:
        db_manager = DatabaseManager()
        
        # Check if camera exists
        camera = db_manager.get_camera_by_id(camera_id)
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camera with ID {camera_id} not found"
            )
        
        # Prepare update data
        update_data = {}
        if settings.camera_name is not None:
            update_data['name'] = settings.camera_name
        if settings.resolution_width is not None:
            update_data['resolution_width'] = settings.resolution_width
        if settings.resolution_height is not None:
            update_data['resolution_height'] = settings.resolution_height
        if settings.fps is not None:
            update_data['fps'] = settings.fps
        if settings.location_description is not None:
            update_data['location_description'] = settings.location_description
        if settings.is_active is not None:
            update_data['is_active'] = settings.is_active
        
        # Update camera in database
        success = db_manager.update_camera(camera_id, **update_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update camera settings"
            )
        
        # If FTS is running, reload camera configurations
        try:
            from core.fts_system import system_instance, is_tracking_running
            if is_tracking_running and system_instance:
                # Trigger camera config reload in FTS
                system_instance.reload_camera_configurations()
                logger.info(f"Reloaded FTS camera configurations after updating camera {camera_id}")
        except Exception as e:
            logger.warning(f"Failed to reload FTS configurations: {e}")
        
        logger.info(f"Updated camera settings for camera {camera_id} by user {current_user.username}")
        
        return MessageResponse(
            success=True,
            message=f"Camera settings updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update camera settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update camera settings: {str(e)}"
        )

@router.get("/{camera_id}/resolutions")
async def get_supported_resolutions(
    camera_id: int,
    current_user: CurrentUser = Depends(require_admin_or_above)
):
    """
    Get supported resolutions for a camera (Admin+ only)
    """
    try:
        # Common supported resolutions
        resolutions = [
            {"width": 320, "height": 240, "name": "QVGA", "aspect_ratio": "4:3"},
            {"width": 640, "height": 480, "name": "VGA", "aspect_ratio": "4:3"},
            {"width": 800, "height": 600, "name": "SVGA", "aspect_ratio": "4:3"},
            {"width": 1024, "height": 768, "name": "XGA", "aspect_ratio": "4:3"},
            {"width": 1280, "height": 720, "name": "HD 720p", "aspect_ratio": "16:9"},
            {"width": 1280, "height": 960, "name": "SXGA", "aspect_ratio": "4:3"},
            {"width": 1280, "height": 1024, "name": "SXGA", "aspect_ratio": "5:4"},
            {"width": 1600, "height": 1200, "name": "UXGA", "aspect_ratio": "4:3"},
            {"width": 1920, "height": 1080, "name": "Full HD 1080p", "aspect_ratio": "16:9"},
            {"width": 2048, "height": 1536, "name": "QXGA", "aspect_ratio": "4:3"},
            {"width": 2560, "height": 1440, "name": "QHD 1440p", "aspect_ratio": "16:9"},
            {"width": 3840, "height": 2160, "name": "4K UHD", "aspect_ratio": "16:9"}
        ]
        
        return {
            "success": True,
            "data": {
                "camera_id": camera_id,
                "supported_resolutions": resolutions
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get supported resolutions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get supported resolutions: {str(e)}"
        )

@router.post("/configure-for-fts")
async def configure_camera_for_fts(
    request: dict,
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Configure a detected camera for FTS use (Super Admin only)
    
    Expected request format:
    {
        "detected_camera_id": int,
        "camera_name": str,
        "location": str,
        "camera_type": str,  # "entry", "exit", "monitoring"
        "enabled": bool,
        "tripwires": [
            {
                "name": str,
                "position": float,
                "direction": str,  # "horizontal", "vertical"
                "spacing": float
            }
        ]
    }
    """
    try:
        from utils.auto_camera_detector import get_auto_detector
        
        # Get the detected camera
        auto_detector = get_auto_detector()
        detected_cameras = auto_detector.get_detected_cameras()
        
        detected_camera_id = request.get("detected_camera_id")
        detected_camera = next((c for c in detected_cameras if c.camera_id == detected_camera_id), None)
        
        if not detected_camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Detected camera with ID {detected_camera_id} not found"
            )
        
        if not detected_camera.is_working:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot configure a non-working camera for FTS"
            )
        
        # Check if camera is already configured
        db_manager = DatabaseManager()
        existing_camera = db_manager.get_camera_by_source(detected_camera.source)
        
        if existing_camera:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Camera is already configured for FTS (Database ID: {existing_camera.id})"
            )
        
        # Create camera configuration in database
        camera_data = {
            "name": request.get("camera_name", detected_camera.name),
            "location": request.get("location", "Unknown"),
            "camera_type": request.get("camera_type", "monitoring"),
            "source": detected_camera.source,
            "resolution_width": detected_camera.resolution[0],
            "resolution_height": detected_camera.resolution[1],
            "fps": detected_camera.fps,
            "is_active": request.get("enabled", True),
            "ip_address": detected_camera.ip_address,
            "stream_url": detected_camera.stream_url
        }
        
        # Create camera in database
        new_camera = db_manager.create_camera(camera_data)
        
        # Create tripwires if provided
        tripwires_data = request.get("tripwires", [])
        created_tripwires = []
        
        for tripwire_data in tripwires_data:
            tripwire_dict = {
                "name": tripwire_data.get("name", "Detection Zone"),
                "position": tripwire_data.get("position", 0.5),
                "direction": tripwire_data.get("direction", "horizontal"),
                "spacing": tripwire_data.get("spacing", 0.05)
            }
            created_tripwire = db_manager.create_tripwire(new_camera.id, tripwire_dict)
            created_tripwires.append(created_tripwire)
        
        return {
            "success": True,
            "message": f"Camera '{camera_data['name']}' successfully configured for FTS",
            "data": {
                "database_camera_id": new_camera.id,
                "camera_name": new_camera.name,
                "location": new_camera.location,
                "is_active": new_camera.is_active,
                "tripwires_created": len(created_tripwires),
                "detected_camera_info": {
                    "id": detected_camera.camera_id,
                    "type": detected_camera.type,
                    "source": detected_camera.source,
                    "resolution": f"{detected_camera.resolution[0]}x{detected_camera.resolution[1]}"
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to configure camera for FTS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to configure camera for FTS: {str(e)}"
        )

@router.delete("/fts-configuration/{database_camera_id}")
async def remove_camera_from_fts(
    database_camera_id: int,
    current_user: CurrentUser = Depends(require_super_admin)
):
    """
    Remove a camera from FTS configuration (Super Admin only)
    """
    try:
        db_manager = DatabaseManager()
        
        # Get camera from database
        camera = db_manager.get_camera(database_camera_id)
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camera with ID {database_camera_id} not found in FTS configuration"
            )
        
        # Delete camera and associated tripwires
        db_manager.delete_camera(database_camera_id)
        
        return {
            "success": True,
            "message": f"Camera '{camera.name}' removed from FTS configuration",
            "data": {
                "removed_camera_id": database_camera_id,
                "camera_name": camera.name
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove camera from FTS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove camera from FTS: {str(e)}"
        )

@router.get("/fts-configured")
async def get_fts_configured_cameras(
    current_user: CurrentUser = Depends(require_admin_or_above)
):
    """
    Get all cameras currently configured for FTS use (Admin+ only)
    """
    try:
        db_manager = DatabaseManager()
        configured_cameras = db_manager.get_all_cameras()
        
        camera_list = []
        for camera in configured_cameras:
            # Get tripwires for this camera
            tripwires = db_manager.get_camera_tripwires(camera.id)
            
            camera_dict = {
                "id": camera.id,
                "name": camera.name,
                "location": camera.location,
                "camera_type": camera.camera_type,
                "source": camera.source,
                "resolution": f"{camera.resolution_width}x{camera.resolution_height}",
                "fps": camera.fps,
                "is_active": camera.is_active,
                "ip_address": camera.ip_address,
                "stream_url": camera.stream_url,
                "created_at": camera.created_at.isoformat() if camera.created_at else None,
                "tripwires": [
                    {
                        "id": tw.id,
                        "name": tw.name,
                        "position": tw.position,
                        "direction": tw.direction,
                        "spacing": tw.spacing
                    } for tw in tripwires
                ]
            }
            camera_list.append(camera_dict)
        
        return {
            "success": True,
            "data": {
                "configured_cameras": camera_list,
                "total_configured": len(camera_list),
                "active_cameras": len([c for c in camera_list if c["is_active"]])
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get FTS configured cameras: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get FTS configured cameras: {str(e)}"
        )