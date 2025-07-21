"""
Consistent error handling utilities for the Face Recognition Attendance System
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException, status
import logging
from functools import wraps
import traceback

logger = logging.getLogger(__name__)

# Custom Exception Classes
class FRSBaseException(Exception):
    """Base exception for Face Recognition System"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class DatabaseError(FRSBaseException):
    """Database operation errors"""
    pass

class CameraError(FRSBaseException):
    """Camera operation errors"""
    pass

class FaceRecognitionError(FRSBaseException):
    """Face recognition processing errors"""
    pass

class AuthenticationError(FRSBaseException):
    """Authentication and authorization errors"""
    pass

class ValidationError(FRSBaseException):
    """Input validation errors"""
    pass

class ConfigurationError(FRSBaseException):
    """Configuration and setup errors"""
    pass

# Error Response Formatter
def format_error_response(
    error: Exception,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    include_traceback: bool = False
) -> Dict[str, Any]:
    """Format error response consistently"""
    response = {
        "error": True,
        "status_code": status_code,
        "message": str(error),
        "type": type(error).__name__
    }
    
    if hasattr(error, 'error_code') and error.error_code:
        response["error_code"] = error.error_code
    
    if include_traceback:
        response["traceback"] = traceback.format_exc()
    
    return response

# Decorator for consistent error handling
def handle_errors(
    default_status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    log_errors: bool = True,
    include_traceback: bool = False
):
    """Decorator to handle errors consistently across endpoints"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # Re-raise HTTP exceptions as-is
                raise
            except FRSBaseException as e:
                if log_errors:
                    logger.error(f"FRS Error in {func.__name__}: {e}")
                error_response = format_error_response(e, default_status_code, include_traceback)
                raise HTTPException(status_code=default_status_code, detail=error_response)
            except Exception as e:
                if log_errors:
                    logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
                error_response = format_error_response(e, default_status_code, include_traceback)
                raise HTTPException(status_code=default_status_code, detail=error_response)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HTTPException:
                # Re-raise HTTP exceptions as-is
                raise
            except FRSBaseException as e:
                if log_errors:
                    logger.error(f"FRS Error in {func.__name__}: {e}")
                error_response = format_error_response(e, default_status_code, include_traceback)
                raise HTTPException(status_code=default_status_code, detail=error_response)
            except Exception as e:
                if log_errors:
                    logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
                error_response = format_error_response(e, default_status_code, include_traceback)
                raise HTTPException(status_code=default_status_code, detail=error_response)
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Context manager for database operations
class DatabaseOperationContext:
    """Context manager for safe database operations"""
    
    def __init__(self, session, operation_name: str = "database operation"):
        self.session = session
        self.operation_name = operation_name
    
    def __enter__(self):
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            try:
                self.session.rollback()
                logger.error(f"Database error during {self.operation_name}: {exc_val}")
            except Exception as rollback_error:
                logger.error(f"Error during rollback: {rollback_error}")
        
        try:
            self.session.close()
        except Exception as close_error:
            logger.error(f"Error closing database session: {close_error}")
        
        # Don't suppress the original exception
        return False

# Camera resource context manager
class CameraResourceContext:
    """Context manager for camera resource management"""
    
    def __init__(self, camera_source, backend=None):
        self.camera_source = camera_source
        self.backend = backend
        self.cap = None
    
    def __enter__(self):
        import cv2
        import platform
        
        try:
            # Use appropriate backend based on platform
            if self.backend:
                self.cap = cv2.VideoCapture(self.camera_source, self.backend)
            elif platform.system() == "Windows":
                self.cap = cv2.VideoCapture(self.camera_source, cv2.CAP_MSMF)
            else:
                self.cap = cv2.VideoCapture(self.camera_source)
            
            if not self.cap.isOpened():
                raise CameraError(f"Failed to open camera: {self.camera_source}")
            
            return self.cap
        
        except Exception as e:
            if self.cap:
                self.cap.release()
            raise CameraError(f"Camera initialization failed: {e}")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cap:
            try:
                self.cap.release()
            except Exception as e:
                logger.error(f"Error releasing camera: {e}")
        
        return False

# Utility functions for common error scenarios
def validate_required_fields(data: dict, required_fields: list) -> None:
    """Validate that required fields are present in data"""
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

def safe_int_conversion(value: Any, field_name: str) -> int:
    """Safely convert value to integer with error handling"""
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid integer value for {field_name}: {value}")

def safe_float_conversion(value: Any, field_name: str) -> float:
    """Safely convert value to float with error handling"""
    try:
        return float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid float value for {field_name}: {value}")

# Log error with context
def log_error_with_context(error: Exception, context: dict = None, logger_instance: logging.Logger = None):
    """Log error with additional context information"""
    if logger_instance is None:
        logger_instance = logger
    
    error_msg = f"Error: {error}"
    if context:
        context_str = ", ".join([f"{k}={v}" for k, v in context.items()])
        error_msg += f" | Context: {context_str}"
    
    logger_instance.error(error_msg, exc_info=True)