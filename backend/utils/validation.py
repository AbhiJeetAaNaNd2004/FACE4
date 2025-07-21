"""
Comprehensive input validation utilities for the Face Recognition System
"""

import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from utils.error_handling import ValidationError
import ipaddress

def validate_email(email: str) -> str:
    """Validate email format"""
    if not email or not isinstance(email, str):
        raise ValidationError("Email is required and must be a string")
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email.strip()):
        raise ValidationError(f"Invalid email format: {email}")
    
    return email.strip().lower()

def validate_employee_id(employee_id: str) -> str:
    """Validate employee ID format"""
    if not employee_id or not isinstance(employee_id, str):
        raise ValidationError("Employee ID is required and must be a string")
    
    employee_id = employee_id.strip()
    
    # Must be alphanumeric, 3-20 characters
    if not re.match(r'^[a-zA-Z0-9_-]{3,20}$', employee_id):
        raise ValidationError("Employee ID must be 3-20 alphanumeric characters, underscores, or hyphens")
    
    return employee_id

def validate_camera_id(camera_id: Union[int, str]) -> int:
    """Validate camera ID"""
    try:
        cam_id = int(camera_id)
        if cam_id < 0 or cam_id > 99:
            raise ValidationError("Camera ID must be between 0 and 99")
        return cam_id
    except (ValueError, TypeError):
        raise ValidationError(f"Camera ID must be a valid integer: {camera_id}")

def validate_ip_address(ip: str) -> str:
    """Validate IP address format"""
    if not ip or not isinstance(ip, str):
        raise ValidationError("IP address is required and must be a string")
    
    try:
        ipaddress.ip_address(ip.strip())
        return ip.strip()
    except ValueError:
        raise ValidationError(f"Invalid IP address format: {ip}")

def validate_port(port: Union[int, str]) -> int:
    """Validate network port number"""
    try:
        port_num = int(port)
        if port_num < 1 or port_num > 65535:
            raise ValidationError("Port must be between 1 and 65535")
        return port_num
    except (ValueError, TypeError):
        raise ValidationError(f"Port must be a valid integer: {port}")

def validate_url(url: str, allowed_schemes: List[str] = None) -> str:
    """Validate URL format"""
    if not url or not isinstance(url, str):
        raise ValidationError("URL is required and must be a string")
    
    if allowed_schemes is None:
        allowed_schemes = ['http', 'https', 'rtsp']
    
    url = url.strip()
    
    # Basic URL pattern
    url_pattern = r'^(https?|rtsp)://[^\s/$.?#].[^\s]*$'
    if not re.match(url_pattern, url, re.IGNORECASE):
        raise ValidationError(f"Invalid URL format: {url}")
    
    scheme = url.split('://')[0].lower()
    if scheme not in allowed_schemes:
        raise ValidationError(f"URL scheme must be one of {allowed_schemes}: {url}")
    
    return url

def validate_resolution(width: Union[int, str], height: Union[int, str]) -> tuple:
    """Validate camera resolution"""
    try:
        w = int(width)
        h = int(height)
        
        if w < 160 or w > 7680:  # Min 160p, Max 8K
            raise ValidationError("Width must be between 160 and 7680 pixels")
        
        if h < 120 or h > 4320:  # Min 120p, Max 8K
            raise ValidationError("Height must be between 120 and 4320 pixels")
        
        return (w, h)
    except (ValueError, TypeError):
        raise ValidationError(f"Resolution must be valid integers: {width}x{height}")

def validate_fps(fps: Union[int, str, float]) -> int:
    """Validate frames per second"""
    try:
        fps_val = int(float(fps))
        if fps_val < 1 or fps_val > 120:
            raise ValidationError("FPS must be between 1 and 120")
        return fps_val
    except (ValueError, TypeError):
        raise ValidationError(f"FPS must be a valid number: {fps}")

def validate_percentage(value: Union[int, str, float], field_name: str = "value") -> float:
    """Validate percentage value (0-100)"""
    try:
        pct = float(value)
        if pct < 0 or pct > 100:
            raise ValidationError(f"{field_name} must be between 0 and 100")
        return pct
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid number: {value}")

def validate_threshold(value: Union[int, str, float], field_name: str = "threshold") -> float:
    """Validate threshold value (0.0-1.0)"""
    try:
        thresh = float(value)
        if thresh < 0.0 or thresh > 1.0:
            raise ValidationError(f"{field_name} must be between 0.0 and 1.0")
        return thresh
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid number: {value}")

def validate_date_string(date_str: str, field_name: str = "date") -> datetime:
    """Validate date string in ISO format"""
    if not date_str or not isinstance(date_str, str):
        raise ValidationError(f"{field_name} is required and must be a string")
    
    try:
        # Try multiple common formats
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        raise ValueError("No valid format found")
    
    except ValueError:
        raise ValidationError(f"Invalid date format for {field_name}: {date_str}")

def validate_password_strength(password: str) -> str:
    """Validate password strength"""
    if not password or not isinstance(password, str):
        raise ValidationError("Password is required and must be a string")
    
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    
    if len(password) > 128:
        raise ValidationError("Password must not exceed 128 characters")
    
    # Check for at least one uppercase, lowercase, digit
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        raise ValidationError("Password must contain at least one digit")
    
    return password

def validate_username(username: str) -> str:
    """Validate username format"""
    if not username or not isinstance(username, str):
        raise ValidationError("Username is required and must be a string")
    
    username = username.strip()
    
    if len(username) < 3:
        raise ValidationError("Username must be at least 3 characters long")
    
    if len(username) > 50:
        raise ValidationError("Username must not exceed 50 characters")
    
    # Must be alphanumeric with underscores/dots
    if not re.match(r'^[a-zA-Z0-9._-]+$', username):
        raise ValidationError("Username can only contain letters, numbers, dots, underscores, and hyphens")
    
    return username

def validate_role(role: str) -> str:
    """Validate user role"""
    if not role or not isinstance(role, str):
        raise ValidationError("Role is required and must be a string")
    
    valid_roles = ['employee', 'admin', 'super_admin']
    role = role.strip().lower()
    
    if role not in valid_roles:
        raise ValidationError(f"Role must be one of: {', '.join(valid_roles)}")
    
    return role

def validate_camera_type(camera_type: str) -> str:
    """Validate camera type"""
    if not camera_type or not isinstance(camera_type, str):
        raise ValidationError("Camera type is required and must be a string")
    
    valid_types = ['usb', 'ip', 'rtsp', 'onvif', 'builtin']
    camera_type = camera_type.strip().lower()
    
    if camera_type not in valid_types:
        raise ValidationError(f"Camera type must be one of: {', '.join(valid_types)}")
    
    return camera_type

def validate_file_size(file_size: int, max_size_mb: int = 10) -> int:
    """Validate file size"""
    if not isinstance(file_size, int) or file_size < 0:
        raise ValidationError("File size must be a non-negative integer")
    
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise ValidationError(f"File size exceeds maximum allowed size of {max_size_mb}MB")
    
    return file_size

def validate_file_extension(filename: str, allowed_extensions: List[str]) -> str:
    """Validate file extension"""
    if not filename or not isinstance(filename, str):
        raise ValidationError("Filename is required and must be a string")
    
    filename = filename.strip()
    
    if '.' not in filename:
        raise ValidationError("Filename must have an extension")
    
    extension = filename.split('.')[-1].lower()
    allowed_extensions = [ext.lower().lstrip('.') for ext in allowed_extensions]
    
    if extension not in allowed_extensions:
        raise ValidationError(f"File extension must be one of: {', '.join(allowed_extensions)}")
    
    return filename

def sanitize_string(value: str, max_length: int = 255, allow_html: bool = False) -> str:
    """Sanitize string input"""
    if not isinstance(value, str):
        raise ValidationError("Value must be a string")
    
    value = value.strip()
    
    if len(value) > max_length:
        raise ValidationError(f"String exceeds maximum length of {max_length} characters")
    
    if not allow_html:
        # Remove potential HTML/script tags
        value = re.sub(r'<[^>]*>', '', value)
    
    return value

def validate_pagination(page: Union[int, str], page_size: Union[int, str]) -> tuple:
    """Validate pagination parameters"""
    try:
        page_num = int(page) if page else 1
        size = int(page_size) if page_size else 20
        
        if page_num < 1:
            raise ValidationError("Page number must be at least 1")
        
        if size < 1 or size > 1000:
            raise ValidationError("Page size must be between 1 and 1000")
        
        return (page_num, size)
    except (ValueError, TypeError):
        raise ValidationError("Page and page_size must be valid integers")

# Batch validation function
def validate_request_data(data: Dict[str, Any], validation_rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate request data against validation rules
    
    validation_rules format:
    {
        'field_name': {
            'required': True/False,
            'type': str/int/float/etc,
            'validator': validation_function,
            'default': default_value
        }
    }
    """
    validated_data = {}
    
    for field, rules in validation_rules.items():
        value = data.get(field)
        
        # Check if required
        if rules.get('required', False) and (value is None or value == ''):
            raise ValidationError(f"Field '{field}' is required")
        
        # Use default if not provided
        if value is None and 'default' in rules:
            value = rules['default']
        
        # Skip validation if value is None and not required
        if value is None:
            continue
        
        # Type validation
        expected_type = rules.get('type')
        if expected_type and not isinstance(value, expected_type):
            try:
                value = expected_type(value)
            except (ValueError, TypeError):
                raise ValidationError(f"Field '{field}' must be of type {expected_type.__name__}")
        
        # Custom validator
        validator = rules.get('validator')
        if validator and callable(validator):
            value = validator(value)
        
        validated_data[field] = value
    
    return validated_data