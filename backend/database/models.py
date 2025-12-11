"""Database ORM models"""

from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.database.database import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # user, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


class Camera(Base):
    """Camera configuration storage"""
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    camera_index = Column(Integer, unique=True, nullable=False)  # 0, 1, 2, etc.
    url = Column(String(255), nullable=True)  # For RTSP streams
    enabled = Column(Boolean, default=True)
    settings_json = Column(JSON, nullable=True)  # brightness, contrast, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recordings = relationship("Recording", back_populates="camera", cascade="all, delete-orphan")
    events = relationship("DetectionEvent", back_populates="camera", cascade="all, delete-orphan")


class Recording(Base):
    """Recording metadata and file tracking"""
    __tablename__ = "recordings"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    filepath = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    is_master = Column(Boolean, default=False)  # True for master grid recordings
    deleted = Column(Boolean, default=False)  # Soft delete flag
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    camera = relationship("Camera", back_populates="recordings")


class DetectionEvent(Base):
    """Detection events log"""
    __tablename__ = "detection_events"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=True)
    event_type = Column(String(50), nullable=False)  # person_detected, weapon_detected, etc.
    people_count = Column(Integer, default=0)
    weapon_detected = Column(Boolean, default=False)
    confidence = Column(Float, nullable=True)  # Average confidence score
    metadata_json = Column(JSON, nullable=True)  # Additional detection data
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    camera = relationship("Camera", back_populates="events")


class SystemLog(Base):
    """System event logs"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False, index=True)  # INFO, WARNING, ERROR, etc.
    message = Column(Text, nullable=False)
    context_json = Column(JSON, nullable=True)  # Additional context
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class ModelVersion(Base):
    """Track YOLO model versions used"""
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    filepath = Column(String(500), nullable=False)
    version = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)  # Currently loaded model
    loaded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
