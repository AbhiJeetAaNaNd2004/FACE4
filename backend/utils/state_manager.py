"""
Centralized state management for the Face Recognition System
Reduces reliance on global variables and improves thread safety
"""

import threading
import time
from typing import Dict, Any, Optional, List
from collections import deque, defaultdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StateManager:
    """Thread-safe state manager for the FRS system"""
    
    def __init__(self):
        # Thread synchronization
        self._lock = threading.RLock()
        self._log_lock = threading.Lock()
        self._stats_lock = threading.Lock()
        
        # System state
        self._system_instance = None
        self._is_tracking_running = False
        self._start_time = None
        
        # Buffers and caches
        self._log_buffer = []
        self._latest_faces = {}
        self._latest_attendance = deque(maxlen=100)
        self._present_users_by_department = defaultdict(list)
        
        # System statistics
        self._system_stats = {
            "uptime": 0,
            "cam_count": 0,
            "load": 0,
            "faces_detected": 0,
            "attendance_count": 0
        }
    
    # System Instance Management
    def set_system_instance(self, instance):
        """Set the FTS system instance"""
        with self._lock:
            self._system_instance = instance
    
    def get_system_instance(self):
        """Get the FTS system instance"""
        with self._lock:
            return self._system_instance
    
    # Tracking State Management
    def set_tracking_running(self, running: bool):
        """Set tracking running state"""
        with self._lock:
            self._is_tracking_running = running
            if running and self._start_time is None:
                self._start_time = time.time()
    
    def is_tracking_running(self) -> bool:
        """Check if tracking is running"""
        with self._lock:
            return self._is_tracking_running
    
    def get_start_time(self) -> Optional[float]:
        """Get system start time"""
        with self._lock:
            return self._start_time
    
    # Logging Management
    def add_log_message(self, message: str):
        """Add a log message to the buffer"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        with self._log_lock:
            self._log_buffer.append(log_entry)
            # Keep only last 1000 entries
            if len(self._log_buffer) > 1000:
                self._log_buffer.pop(0)
    
    def get_logs(self, n: int = 100) -> List[str]:
        """Get recent log entries"""
        with self._log_lock:
            return self._log_buffer[-n:].copy()
    
    def clear_logs(self):
        """Clear the log buffer"""
        with self._log_lock:
            self._log_buffer.clear()
    
    # Face Data Management
    def update_latest_faces(self, camera_id: int, faces: List[Any]):
        """Update latest faces for a camera"""
        with self._lock:
            self._latest_faces[camera_id] = faces
    
    def get_latest_faces(self, camera_id: Optional[int] = None) -> Dict[int, List[Any]]:
        """Get latest faces for camera(s)"""
        with self._lock:
            if camera_id is not None:
                return {camera_id: self._latest_faces.get(camera_id, [])}
            return self._latest_faces.copy()
    
    # Attendance Management
    def add_attendance_record(self, record: Dict[str, Any]):
        """Add an attendance record"""
        with self._lock:
            self._latest_attendance.append(record)
    
    def get_attendance_records(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent attendance records"""
        with self._lock:
            if n is None:
                return list(self._latest_attendance)
            return list(self._latest_attendance)[-n:]
    
    # Department Presence Management
    def update_department_presence(self, department: str, users: List[str]):
        """Update present users for a department"""
        with self._lock:
            self._present_users_by_department[department] = users.copy()
    
    def get_department_presence(self, department: Optional[str] = None) -> Dict[str, List[str]]:
        """Get present users by department"""
        with self._lock:
            if department is not None:
                return {department: self._present_users_by_department.get(department, [])}
            return dict(self._present_users_by_department)
    
    # Statistics Management
    def update_stats(self, **kwargs):
        """Update system statistics"""
        with self._stats_lock:
            for key, value in kwargs.items():
                if key in self._system_stats:
                    self._system_stats[key] = value
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        with self._stats_lock:
            # Update uptime if system is running
            if self._start_time:
                self._system_stats["uptime"] = time.time() - self._start_time
            return self._system_stats.copy()
    
    def increment_stat(self, stat_name: str, increment: int = 1):
        """Increment a statistic counter"""
        with self._stats_lock:
            if stat_name in self._system_stats:
                self._system_stats[stat_name] += increment
    
    # Cleanup Methods
    def reset_state(self):
        """Reset all state (useful for testing or restart)"""
        with self._lock:
            with self._log_lock:
                with self._stats_lock:
                    self._system_instance = None
                    self._is_tracking_running = False
                    self._start_time = None
                    self._log_buffer.clear()
                    self._latest_faces.clear()
                    self._latest_attendance.clear()
                    self._present_users_by_department.clear()
                    self._system_stats = {
                        "uptime": 0,
                        "cam_count": 0,
                        "load": 0,
                        "faces_detected": 0,
                        "attendance_count": 0
                    }
    
    def cleanup_old_data(self, max_age_seconds: int = 3600):
        """Cleanup old data to prevent memory leaks"""
        current_time = time.time()
        
        with self._lock:
            # Clean up old face data (keep only recent)
            for camera_id in list(self._latest_faces.keys()):
                # This is a simple cleanup - in practice you'd check timestamps
                if len(self._latest_faces[camera_id]) > 100:
                    self._latest_faces[camera_id] = self._latest_faces[camera_id][-50:]
        
        logger.debug("Cleaned up old state data")

# Global state manager instance
_state_manager = None
_state_manager_lock = threading.Lock()

def get_state_manager() -> StateManager:
    """Get the global state manager instance (singleton pattern)"""
    global _state_manager
    
    if _state_manager is None:
        with _state_manager_lock:
            if _state_manager is None:
                _state_manager = StateManager()
    
    return _state_manager

# Convenience functions for backward compatibility
def log_message(msg: str):
    """Add a log message (backward compatibility)"""
    get_state_manager().add_log_message(msg)

def get_system_stats() -> Dict[str, Any]:
    """Get system statistics (backward compatibility)"""
    return get_state_manager().get_stats()

def is_tracking_running() -> bool:
    """Check if tracking is running (backward compatibility)"""
    return get_state_manager().is_tracking_running()