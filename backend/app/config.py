import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database Configuration
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "frs_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    
    # Security Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application Configuration
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # CORS Configuration
    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
    
    # Face Recognition Configuration
    FACE_RECOGNITION_TOLERANCE: float = 0.6
    FACE_DETECTION_MODEL: str = "hog"
    FACE_ENCODING_MODEL: str = "large"
    
    # Camera Configuration
    DEFAULT_CAMERA_ID: int = 0
    MAX_CONCURRENT_STREAMS: int = 5
    STREAM_QUALITY: str = "medium"
    FRAME_RATE: int = 30
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    FACE_IMAGES_DIR: str = "face_images"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    # Logging Configuration
    LOG_FILE: str = "logs/app.log"
    LOG_ROTATION: str = "1 day"
    LOG_RETENTION: str = "30 days"
    
    # Face Tracking System Configuration
    FTS_AUTO_START: bool = True  # Auto-start FTS on server startup
    FTS_STARTUP_DELAY: int = 2   # Delay in seconds before starting FTS
    FACE_TRACKING_AUTO_START: bool = True  # Legacy setting for compatibility
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',')]

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = 'allow'  # Allow extra fields in configuration

settings = Settings()
