from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, LargeBinary, JSON, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Department(Base):
    __tablename__ = 'departments'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    employees = relationship("Employee", back_populates="department", cascade="all, delete-orphan")

class Employee(Base):
    __tablename__ = 'employees'
    
    employee_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    role = Column(String, nullable=False)
    date_joined = Column(Date, nullable=False)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    department = relationship("Department", back_populates="employees")
    face_embeddings = relationship("FaceEmbedding", back_populates="employee", cascade="all, delete-orphan")
    attendance_logs = relationship("AttendanceLog", back_populates="employee", cascade="all, delete-orphan")

class FaceEmbedding(Base):
    __tablename__ = 'face_embeddings'
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey('employees.employee_id'), nullable=False)
    image_path = Column(String, nullable=False)
    embedding_vector = Column(LargeBinary, nullable=False)  # Stored as binary data
    embedding_type = Column(String, default='enroll', nullable=False)  # 'enroll', 'update', 'verify'
    quality_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="face_embeddings")

class AttendanceLog(Base):
    __tablename__ = 'attendance_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey('employees.employee_id'), nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    status = Column(String, nullable=False)  # 'present' or 'absent'
    confidence_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="attendance_logs")

class UserAccount(Base):
    __tablename__ = 'user_accounts'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'employee', 'admin', 'super_admin'
    employee_id = Column(String, ForeignKey('employees.employee_id'), nullable=True)  # Optional link to employee
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])

# Legacy models for backward compatibility (can be removed if not needed)
class TrackingRecord(Base):
    __tablename__ = 'tracking_records'
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey('employees.employee_id'), nullable=False)
    camera_id = Column(Integer, nullable=False)
    position_x = Column(Float)
    position_y = Column(Float)
    confidence_score = Column(Float)
    quality_metrics = Column(JSON)
    timestamp = Column(DateTime, default=func.now())
    tracking_state = Column(String, default='active')

class CameraConfig(Base):
    __tablename__ = 'camera_configs'
    
    # Essential fields for LAN camera operation
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, unique=True, nullable=False)  # Used as camera source (0, 1, 2, etc.)
    camera_type = Column(String, default='entry')  # 'entry', 'exit', 'general'
    resolution_width = Column(Integer, default=1920)
    resolution_height = Column(Integer, default=1080)
    fps = Column(Integer, default=30)
    gpu_id = Column(Integer, default=0)  # GPU assignment for processing
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Optional fields - only needed for network cameras or advanced features
    name = Column(String, nullable=True)  # Display name (camera_name alias)
    source = Column(String, nullable=True)  # Camera source (index, IP, or URL)
    location = Column(String, nullable=True)  # Human-readable location
    ip_address = Column(String, nullable=True)  # Only for network cameras
    stream_url = Column(String, nullable=True)  # Only for network cameras
    username = Column(String, nullable=True)  # Only for authenticated cameras
    password = Column(String, nullable=True)  # Only for authenticated cameras
    status = Column(String, default='active')  # Status tracking (optional)
    location_description = Column(String, nullable=True)  # Legacy location field
    manufacturer = Column(String, nullable=True)  # Camera manufacturer
    model = Column(String, nullable=True)  # Camera model
    firmware_version = Column(String, nullable=True)  # Camera firmware
    onvif_supported = Column(Boolean, default=False)  # ONVIF support flag
    
    # Relationships
    tripwires = relationship("Tripwire", back_populates="camera", cascade="all, delete-orphan")

class Tripwire(Base):
    __tablename__ = 'tripwires'
    
    # Essential fields for tripwire detection
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey('camera_configs.camera_id'), nullable=False)
    name = Column(String, nullable=False)  # Tripwire name/identifier
    position = Column(Float, nullable=False)  # Position (0.0 to 1.0)
    spacing = Column(Float, default=0.01)  # Spacing for detection
    direction = Column(String, nullable=False)  # 'horizontal', 'vertical'
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Optional fields for advanced features
    detection_type = Column(String, default='entry')  # 'entry', 'exit', 'counting'
    is_active = Column(Boolean, default=True)  # Allow disabling tripwires
    
    # Relationships
    camera = relationship("CameraConfig", back_populates="tripwires")

class SystemLog(Base):
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    log_level = Column(String, default='INFO')
    message = Column(Text, nullable=False)
    component = Column(String)
    employee_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=func.now())
    additional_data = Column(JSON)