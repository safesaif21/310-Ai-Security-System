"""Pydantic models for request/response schemas"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ===========================================
# Camera Schemas
# ===========================================

class CameraSettings(BaseModel):
    """Camera settings for adjustments"""
    brightness: int = Field(default=50, ge=0, le=100)
    contrast: int = Field(default=50, ge=0, le=100)
    saturation: int = Field(default=50, ge=0, le=100)
    gamma: int = Field(default=50, ge=0, le=100)


class CameraCreate(BaseModel):
    """Schema for creating a new camera"""
    name: str = Field(..., min_length=1, max_length=100)
    camera_index: int = Field(..., ge=0)
    url: Optional[str] = None
    settings: Optional[CameraSettings] = None


class CameraResponse(BaseModel):
    """Schema for camera response"""
    id: int
    name: str
    camera_index: int
    url: Optional[str]
    enabled: bool
    settings_json: Optional[dict]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===========================================
# Authentication Schemas
# ===========================================

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserRegister(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    """Schema for user response (no password)"""
    id: Optional[str] = None
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_mongo(cls, data: dict):
        """Convert MongoDB document to UserResponse"""
        if "_id" in data:
            data["id"] = str(data["_id"])
        return cls(**data)



class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for token refresh request"""
    refresh_token: str


# ===========================================
# Recording Schemas
# ===========================================

class RecordingResponse(BaseModel):
    """Schema for recording metadata"""
    id: int
    camera_id: int
    filepath: str
    file_size_bytes: Optional[int]
    start_time: datetime
    end_time: Optional[datetime]
    is_master: bool
    
    class Config:
        from_attributes = True


class RecordingFilter(BaseModel):
    """Schema for filtering recordings"""
    camera_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_master: Optional[bool] = None


# ===========================================
# Detection Event Schemas
# ===========================================

class DetectionEventResponse(BaseModel):
    """Schema for detection event"""
    id: int
    camera_id: Optional[int]
    event_type: str
    people_count: int
    weapon_detected: bool
    confidence: Optional[float]
    metadata_json: Optional[dict]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class EventStatistics(BaseModel):
    """Schema for event statistics"""
    total_events: int
    weapon_detections: int
    total_people_detected: int
    average_people_per_event: float


# ===========================================
# Log Schemas
# ===========================================

class LogEntry(BaseModel):
    """Schema for log entry"""
    id: str
    timestamp: str
    message: str
    type: str


class SystemLogResponse(BaseModel):
    """Schema for system log from database"""
    id: int
    level: str
    message: str
    context_json: Optional[dict]
    timestamp: datetime
    
    class Config:
        from_attributes = True


# ===========================================
# Stats Schemas
# ===========================================

class SystemStats(BaseModel):
    """Schema for real-time system statistics"""
    people_count: int
    weapon_detected: bool
    threat_level: int


# ===========================================
# Health Check Schemas
# ===========================================

class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    version: str
    environment: str
    database_connected: bool
    cameras_active: int


class DetailedHealthResponse(HealthResponse):
    """Extended health check with more details"""
    uptime_seconds: float
    total_recordings: int
    total_events: int
    disk_usage_percent: float
