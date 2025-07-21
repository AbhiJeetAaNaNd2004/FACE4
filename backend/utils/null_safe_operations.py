"""
Null-safe operations utility
Provides wrapper functions for handling null values gracefully across the application
"""

from typing import Any, Optional, List, Dict, Union, Callable
import logging

logger = logging.getLogger(__name__)

def safe_get(obj: Any, key: str, default: Any = None) -> Any:
    """
    Safely get a value from an object/dict with null checking
    """
    if obj is None:
        return default
    
    try:
        if isinstance(obj, dict):
            return obj.get(key, default)
        else:
            return getattr(obj, key, default)
    except (AttributeError, KeyError, TypeError):
        return default

def safe_list(obj: Any) -> List:
    """
    Safely convert object to list, returning empty list for null/invalid values
    """
    if obj is None:
        return []
    
    if isinstance(obj, list):
        return obj
    
    try:
        return list(obj)
    except (TypeError, ValueError):
        return []

def safe_dict(obj: Any) -> Dict:
    """
    Safely convert object to dict, returning empty dict for null/invalid values
    """
    if obj is None:
        return {}
    
    if isinstance(obj, dict):
        return obj
    
    try:
        return dict(obj)
    except (TypeError, ValueError):
        return {}

def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to int with default fallback
    """
    if value is None:
        return default
    
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float with default fallback
    """
    if value is None:
        return default
    
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def safe_str(value: Any, default: str = "") -> str:
    """
    Safely convert value to string with default fallback
    """
    if value is None:
        return default
    
    try:
        return str(value)
    except (TypeError, ValueError):
        return default

def safe_bool(value: Any, default: bool = False) -> bool:
    """
    Safely convert value to boolean with default fallback
    """
    if value is None:
        return default
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    
    try:
        return bool(value)
    except (TypeError, ValueError):
        return default

def safe_call(func: Optional[Callable], *args, default: Any = None, **kwargs) -> Any:
    """
    Safely call a function with null checking
    """
    if func is None or not callable(func):
        logger.debug(f"Function {func} is not callable")
        return default
    
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Function call failed: {e}")
        return default

def safe_access_nested(obj: Any, path: str, separator: str = ".", default: Any = None) -> Any:
    """
    Safely access nested object properties using dot notation
    Example: safe_access_nested(user, "profile.settings.theme", default="light")
    """
    if obj is None:
        return default
    
    try:
        current = obj
        for key in path.split(separator):
            if isinstance(current, dict):
                current = current.get(key)
            else:
                current = getattr(current, key, None)
            
            if current is None:
                return default
                
        return current
    except (AttributeError, KeyError, TypeError):
        return default

def safe_filter_list(items: Any, filter_func: Optional[Callable] = None) -> List:
    """
    Safely filter a list with null checking
    """
    safe_items = safe_list(items)
    
    if filter_func is None or not callable(filter_func):
        return safe_items
    
    try:
        return [item for item in safe_items if safe_call(filter_func, item, default=False)]
    except Exception as e:
        logger.warning(f"List filtering failed: {e}")
        return safe_items

def safe_map_list(items: Any, map_func: Optional[Callable] = None, default_value: Any = None) -> List:
    """
    Safely map a function over a list with null checking
    """
    safe_items = safe_list(items)
    
    if map_func is None or not callable(map_func):
        return safe_items
    
    try:
        return [safe_call(map_func, item, default=default_value) for item in safe_items]
    except Exception as e:
        logger.warning(f"List mapping failed: {e}")
        return safe_items

def safe_database_operation(operation: Callable, *args, default: Any = None, **kwargs) -> Any:
    """
    Safely execute database operations with comprehensive error handling
    """
    try:
        result = operation(*args, **kwargs)
        return result if result is not None else default
    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        return default

def safe_camera_operation(operation: Callable, camera_id: Any = None, default: Any = None, **kwargs) -> Any:
    """
    Safely execute camera operations with null checking
    """
    # Validate camera_id
    safe_camera_id = safe_int(camera_id, -1)
    if safe_camera_id < 0:
        logger.warning(f"Invalid camera ID: {camera_id}")
        return default
    
    try:
        return operation(safe_camera_id, **kwargs)
    except Exception as e:
        logger.error(f"Camera operation failed for camera {safe_camera_id}: {e}")
        return default

def safe_json_loads(json_str: Any, default: Any = None) -> Any:
    """
    Safely parse JSON string with null checking
    """
    if json_str is None:
        return default
    
    try:
        import json
        return json.loads(str(json_str))
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        logger.warning(f"JSON parsing failed: {e}")
        return default

def safe_file_operation(operation: Callable, filepath: Any = None, default: Any = None, **kwargs) -> Any:
    """
    Safely execute file operations with null checking
    """
    if filepath is None:
        logger.warning("File path is None")
        return default
    
    try:
        return operation(str(filepath), **kwargs)
    except Exception as e:
        logger.error(f"File operation failed for {filepath}: {e}")
        return default

def validate_and_sanitize_input(value: Any, expected_type: type, default: Any = None, max_length: Optional[int] = None) -> Any:
    """
    Validate and sanitize user input with type checking and length limits
    """
    if value is None:
        return default
    
    # Type conversion
    if expected_type == str:
        result = safe_str(value, default)
        if max_length and len(result) > max_length:
            result = result[:max_length]
        return result.strip()
    elif expected_type == int:
        return safe_int(value, default)
    elif expected_type == float:
        return safe_float(value, default)
    elif expected_type == bool:
        return safe_bool(value, default)
    elif expected_type == list:
        return safe_list(value)
    elif expected_type == dict:
        return safe_dict(value)
    else:
        return value if isinstance(value, expected_type) else default

class NullSafeDict(dict):
    """
    Dictionary that returns None for missing keys instead of raising KeyError
    """
    
    def __getitem__(self, key):
        return self.get(key, None)
    
    def safe_get(self, key: str, default: Any = None, expected_type: type = None):
        """Get value with type validation"""
        value = self.get(key, default)
        if expected_type:
            return validate_and_sanitize_input(value, expected_type, default)
        return value

def create_null_safe_response(data: Any = None, success: bool = True, message: str = "", errors: List[str] = None) -> Dict:
    """
    Create a standardized null-safe API response
    """
    return {
        "success": safe_bool(success),
        "message": safe_str(message),
        "data": data,
        "errors": safe_list(errors),
        "timestamp": safe_call(lambda: __import__('datetime').datetime.now().isoformat(), default="")
    }

# Decorator for null-safe endpoint handling
def null_safe_endpoint(default_response: Any = None):
    """
    Decorator to wrap endpoints with null-safe error handling
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result if result is not None else default_response
            except Exception as e:
                logger.error(f"Endpoint {func.__name__} failed: {e}")
                return create_null_safe_response(
                    success=False,
                    message=f"Operation failed: {str(e)}",
                    errors=[str(e)]
                )
        return wrapper
    return decorator