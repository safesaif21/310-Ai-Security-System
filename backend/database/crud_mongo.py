"""CRUD operations for MongoDB models"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pymongo.database import Database
from bson import ObjectId

from backend.database.models_mongo import (
    UserModel, CameraModel, RecordingModel, 
    DetectionEventModel, SystemLogModel, ModelVersionModel
)


# ===========================================
# User CRUD
# ===========================================

def get_user_by_username(db: Database, username: str) -> Optional[Dict[str, Any]]:
    """Get user by username"""
    return db.users.find_one({"username": username})


def get_user_by_email(db: Database, email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    return db.users.find_one({"email": email})


def get_user_by_id(db: Database, user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    return db.users.find_one({"_id": ObjectId(user_id)})


def create_user(db: Database, username: str, email: str, hashed_password: str, role: str = "user") -> Dict[str, Any]:
    """Create a new user"""
    user_data = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "role": role,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "last_login": None
    }
    result = db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    return user_data


def update_user_last_login(db: Database, user_id: str):
    """Update user's last login timestamp"""
    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"last_login": datetime.utcnow()}}
    )


# ===========================================
# Camera CRUD
# ===========================================

def get_camera_by_index(db: Database, camera_index: int) -> Optional[Dict[str, Any]]:
    """Get camera by its index"""
    return db.cameras.find_one({"camera_index": camera_index})


def get_camera_by_id(db: Database, camera_id: str) -> Optional[Dict[str, Any]]:
    """Get camera by ID"""
    return db.cameras.find_one({"_id": ObjectId(camera_id)})


def get_all_cameras(db: Database, enabled_only: bool = False) -> List[Dict[str, Any]]:
    """Get all cameras"""
    query = {"enabled": True} if enabled_only else {}
    return list(db.cameras.find(query))


def create_camera(db: Database, name: str, camera_index: int, url: Optional[str] = None,
                  settings_json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a new camera"""
    camera_data = {
        "name": name,
        "camera_index": camera_index,
        "url": url,
        "enabled": True,
        "settings_json": settings_json,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = db.cameras.insert_one(camera_data)
    camera_data["_id"] = result.inserted_id
    return camera_data


def update_camera_settings(db: Database, camera_id: str, settings_json: Dict[str, Any]):
    """Update camera settings"""
    db.cameras.update_one(
        {"_id": ObjectId(camera_id)},
        {"$set": {
            "settings_json": settings_json,
            "updated_at": datetime.utcnow()
        }}
    )


def delete_camera(db: Database, camera_id: str):
    """Delete a camera (and related data)"""
    camera_oid = ObjectId(camera_id)
    
    # Delete camera
    db.cameras.delete_one({"_id": camera_oid})
    
    # Delete related recordings and events
    db.recordings.delete_many({"camera_id": camera_oid})
    db.detection_events.delete_many({"camera_id": camera_oid})


# ===========================================
# Recording CRUD
# ===========================================

def create_recording(db: Database, camera_id: str, filepath: str, start_time: datetime,
                     is_master: bool = False) -> Dict[str, Any]:
    """Create a new recording entry"""
    recording_data = {
        "camera_id": ObjectId(camera_id),
        "filepath": filepath,
        "file_size_bytes": None,
        "start_time": start_time,
        "end_time": None,
        "is_master": is_master,
        "deleted": False,
        "deleted_at": None,
        "created_at": datetime.utcnow()
    }
    result = db.recordings.insert_one(recording_data)
    recording_data["_id"] = result.inserted_id
    return recording_data


def update_recording_end(db: Database, recording_id: str, end_time: datetime, file_size_bytes: int):
    """Update recording when it finishes"""
    db.recordings.update_one(
        {"_id": ObjectId(recording_id)},
        {"$set": {
            "end_time": end_time,
            "file_size_bytes": file_size_bytes
        }}
    )


def get_recordings_by_camera(db: Database, camera_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get recordings for a specific camera"""
    return list(db.recordings.find({
        "camera_id": ObjectId(camera_id),
        "deleted": False
    }).sort("start_time", -1).limit(limit))


def get_recordings_in_date_range(db: Database, start_date: datetime, end_date: datetime,
                                  camera_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get recordings within a date range"""
    query = {
        "start_time": {"$gte": start_date, "$lte": end_date},
        "deleted": False
    }
    if camera_id:
        query["camera_id"] = ObjectId(camera_id)
    return list(db.recordings.find(query).sort("start_time", -1))


def soft_delete_recording(db: Database, recording_id: str):
    """Soft delete a recording"""
    db.recordings.update_one(
        {"_id": ObjectId(recording_id)},
        {"$set": {
            "deleted": True,
            "deleted_at": datetime.utcnow()
        }}
    )


def get_oldest_recordings(db: Database, camera_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get oldest recordings for cleanup purposes"""
    return list(db.recordings.find({
        "camera_id": ObjectId(camera_id),
        "deleted": False
    }).sort("start_time", 1).limit(limit))


# ===========================================
# Detection Event CRUD
# ===========================================

def create_detection_event(db: Database, camera_id: str, event_type: str, people_count: int = 0,
                            weapon_detected: bool = False, confidence: Optional[float] = None,
                            metadata_json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a new detection event"""
    event_data = {
        "camera_id": ObjectId(camera_id),
        "event_type": event_type,
        "people_count": people_count,
        "weapon_detected": weapon_detected,
        "confidence": confidence,
        "metadata_json": metadata_json,
        "timestamp": datetime.utcnow()
    }
    result = db.detection_events.insert_one(event_data)
    event_data["_id"] = result.inserted_id
    return event_data


def get_recent_events(db: Database, limit: int = 100, camera_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get recent detection events"""
    query = {}
    if camera_id:
        query["camera_id"] = ObjectId(camera_id)
    return list(db.detection_events.find(query).sort("timestamp", -1).limit(limit))


def get_events_in_date_range(db: Database, start_date: datetime, end_date: datetime,
                              event_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get events within a date range"""
    query = {"timestamp": {"$gte": start_date, "$lte": end_date}}
    if event_type:
        query["event_type"] = event_type
    return list(db.detection_events.find(query).sort("timestamp", -1))


def get_event_statistics(db: Database, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Get statistics about events in a date range"""
    events = get_events_in_date_range(db, start_date, end_date)
    
    total_events = len(events)
    weapon_detections = sum(1 for e in events if e.get("weapon_detected", False))
    total_people = sum(e.get("people_count", 0) for e in events)
    
    return {
        "total_events": total_events,
        "weapon_detections": weapon_detections,
        "total_people_detected": total_people,
        "average_people_per_event": total_people / total_events if total_events > 0 else 0
    }


# ===========================================
# System Log CRUD
# ===========================================

def create_system_log(db: Database, level: str, message: str, context_json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a system log entry"""
    log_data = {
        "level": level.upper(),
        "message": message,
        "context_json": context_json,
        "timestamp": datetime.utcnow()
    }
    result = db.system_logs.insert_one(log_data)
    log_data["_id"] = result.inserted_id
    return log_data


def get_recent_logs(db: Database, limit: int = 100, level: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get recent system logs"""
    query = {}
    if level:
        query["level"] = level.upper()
    return list(db.system_logs.find(query).sort("timestamp", -1).limit(limit))


def cleanup_old_logs(db: Database, days: int = 30):
    """Delete logs older than specified days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    db.system_logs.delete_many({"timestamp": {"$lt": cutoff_date}})


# ===========================================
# Model Version CRUD
# ===========================================

def create_model_version(db: Database, name: str, filepath: str, version: Optional[str] = None,
                         description: Optional[str] = None) -> Dict[str, Any]:
    """Register a new model version"""
    model_data = {
        "name": name,
        "filepath": filepath,
        "version": version,
        "description": description,
        "is_active": False,
        "loaded_at": None,
        "created_at": datetime.utcnow()
    }
    result = db.model_versions.insert_one(model_data)
    model_data["_id"] = result.inserted_id
    return model_data


def set_active_model(db: Database, model_id: str):
    """Set a model as active (deactivate others)"""
    # Deactivate all models
    db.model_versions.update_many({}, {"$set": {"is_active": False}})
    
    # Activate the specified model
    db.model_versions.update_one(
        {"_id": ObjectId(model_id)},
        {"$set": {
            "is_active": True,
            "loaded_at": datetime.utcnow()
        }}
    )


def get_active_model(db: Database) -> Optional[Dict[str, Any]]:
    """Get the currently active model"""
    return db.model_versions.find_one({"is_active": True})
