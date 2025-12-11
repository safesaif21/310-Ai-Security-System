"""MongoDB schema models using Pydantic v2"""

from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, EmailStr
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from bson import ObjectId


class PyObjectId(str):
    """Custom Pydantic type for MongoDB ObjectId (Pydantic v2 compatible)"""
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler
    ) -> core_schema.CoreSchema:
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ])
        ])
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return v
            raise ValueError("Invalid ObjectId")
        raise ValueError("Invalid ObjectId")
    
    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler
    ) -> JsonSchemaValue:
        return {"type": "string"}


class UserModel(BaseModel):
    """User model for authentication"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    hashed_password: str
    role: str = "user"  # user, admin
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CameraModel(BaseModel):
    """Camera configuration storage"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., min_length=1, max_length=100)
    camera_index: int = Field(..., ge=0)  # 0, 1, 2, etc.
    url: Optional[str] = Field(None, max_length=255)  # For RTSP streams
    enabled: bool = True
    settings_json: Optional[Dict[str, Any]] = None  # brightness, contrast, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class RecordingModel(BaseModel):
    """Recording metadata and file tracking"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    camera_id: PyObjectId  # Reference to camera
    filepath: str = Field(..., max_length=500)
    file_size_bytes: Optional[int] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    is_master: bool = False  # True for master grid recordings
    deleted: bool = False  # Soft delete flag
    deleted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DetectionEventModel(BaseModel):
    """Detection events log"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    camera_id: Optional[PyObjectId] = None  # Reference to camera
    event_type: str = Field(..., max_length=50)  # person_detected, weapon_detected, etc.
    people_count: int = 0
    weapon_detected: bool = False
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)  # Average confidence score
    metadata_json: Optional[Dict[str, Any]] = None  # Additional detection data
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class SystemLogModel(BaseModel):
    """System event logs"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    level: str = Field(..., max_length=20)  # INFO, WARNING, ERROR, etc.
    message: str
    context_json: Optional[Dict[str, Any]] = None  # Additional context
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ModelVersionModel(BaseModel):
    """Track YOLO model versions used"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., max_length=100)
    filepath: str = Field(..., max_length=500)
    version: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: bool = False  # Currently loaded model
    loaded_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
