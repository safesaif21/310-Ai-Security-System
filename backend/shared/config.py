"""Configuration management with environment variables"""

from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = Field(default="AI Security System", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    
    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    reload: bool = Field(default=True, alias="RELOAD")
    
    # Security
    secret_key: str = Field(default="dev-secret-change-in-production", alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS
    allowed_origins: str = Field(default="*", alias="ALLOWED_ORIGINS")
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    # Database - MongoDB
    mongodb_uri: str = Field(default="mongodb://localhost:27017/", alias="MONGODB_URI")
    mongodb_database: str = Field(default="safe_security_system", alias="MONGODB_DATABASE")
    
    
    # Storage
    models_folder: str = Field(default="yolo_models", alias="MODELS_FOLDER")
    recordings_folder: str = Field(default="recordings", alias="RECORDINGS_FOLDER")
    master_folder: str = Field(default="master", alias="MASTER_FOLDER")
    logs_folder: str = Field(default="logs", alias="LOGS_FOLDER")
    
    recording_size_limit_gb: float = Field(default=10.0, alias="RECORDING_SIZE_LIMIT_GB")
    master_size_limit_gb: float = Field(default=1.0, alias="MASTER_SIZE_LIMIT_GB")
    
    # Camera Settings
    max_cameras: int = Field(default=10, alias="MAX_CAMERAS")
    fixed_camera_count: int = Field(default=0, alias="FIXED_CAMERA_COUNT")
    camera_width: int = Field(default=640, alias="CAMERA_WIDTH")
    camera_height: int = Field(default=480, alias="CAMERA_HEIGHT")
    camera_fps: int = Field(default=30, alias="CAMERA_FPS")
    max_consecutive_failures: int = Field(default=30, alias="MAX_CONSECUTIVE_FAILURES")
    
    # Recording Settings
    recording_fps: int = Field(default=20, alias="RECORDING_FPS")
    recording_rotation_seconds: int = Field(default=180, alias="RECORDING_ROTATION_SECONDS")
    jpeg_quality: int = Field(default=85, alias="JPEG_QUALITY")
    
    # Master Recording
    master_width: int = Field(default=640, alias="MASTER_WIDTH")
    master_height: int = Field(default=480, alias="MASTER_HEIGHT")
    master_cell_width: int = Field(default=320, alias="MASTER_CELL_WIDTH")
    master_cell_height: int = Field(default=240, alias="MASTER_CELL_HEIGHT")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="text", alias="LOG_FORMAT")
    log_max_bytes: int = Field(default=10485760, alias="LOG_MAX_BYTES")  # 10MB
    log_backup_count: int = Field(default=5, alias="LOG_BACKUP_COUNT")
    log_retention_days: int = Field(default=30, alias="LOG_RETENTION_DAYS")
    
    # Monitoring
    metrics_enabled: bool = Field(default=True, alias="METRICS_ENABLED")
    prometheus_port: int = Field(default=9090, alias="PROMETHEUS_PORT")
    
    # Feature Flags
    enable_master_recording: bool = Field(default=True, alias="ENABLE_MASTER_RECORDING")
    enable_detection_logging: bool = Field(default=True, alias="ENABLE_DETECTION_LOGGING")
    enable_auto_cleanup: bool = Field(default=True, alias="ENABLE_AUTO_CLEANUP")
    
    # Development
    debug: bool = Field(default=False, alias="DEBUG")
    testing: bool = Field(default=False, alias="TESTING")


# Global settings instance
settings = Settings()

# Backwards compatibility - expose settings as module-level constants
# These will be gradually phased out
MODELS_FOLDER = settings.models_folder
RECORDINGS_FOLDER = settings.recordings_folder
MASTER_FOLDER = settings.master_folder
LOGS_FOLDER = settings.logs_folder

RECORDING_SIZE_LIMIT_GB = settings.recording_size_limit_gb
MASTER_SIZE_LIMIT_GB = settings.master_size_limit_gb

MAX_CAMERAS = settings.max_cameras
CAMERA_WIDTH = settings.camera_width
CAMERA_HEIGHT = settings.camera_height
CAMERA_FPS = settings.camera_fps

RECORDING_FPS = settings.recording_fps
RECORDING_ROTATION_SECONDS = settings.recording_rotation_seconds
JPEG_QUALITY = settings.jpeg_quality

MASTER_WIDTH = settings.master_width
MASTER_HEIGHT = settings.master_height
MASTER_CELL_WIDTH = settings.master_cell_width
MASTER_CELL_HEIGHT = settings.master_cell_height

MAX_CONSECUTIVE_FAILURES = settings.max_consecutive_failures
