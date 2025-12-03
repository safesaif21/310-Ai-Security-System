"""Pydantic models for request/response schemas"""

from pydantic import BaseModel

class CameraSettings(BaseModel):
    brightness: int = 50
    contrast: int = 50
    saturation: int = 50
    gamma: int = 50

class LogEntry(BaseModel):
    id: str
    timestamp: str
    message: str
    type: str
