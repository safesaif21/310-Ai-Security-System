"""CRUD operations for database models"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from backend.database import models


# ===========================================
# User CRUD
# ===========================================

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get user by username"""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email"""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, username: str, email: str, hashed_password: str, role: str = "user") -> models.User:
    """Create a new user"""
    db_user = models.User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_last_login(db: Session, user_id: int):
    """Update user's last login timestamp"""
    db.query(models.User).filter(models.User.id == user_id).update({"last_login": datetime.utcnow()})
    db.commit()


# ===========================================
# Camera CRUD
# ===========================================

def get_camera_by_index(db: Session, camera_index: int) -> Optional[models.Camera]:
    """Get camera by its index"""
    return db.query(models.Camera).filter(models.Camera.camera_index == camera_index).first()


def get_all_cameras(db: Session, enabled_only: bool = False) -> List[models.Camera]:
    """Get all cameras"""
    query = db.query(models.Camera)
    if enabled_only:
        query = query.filter(models.Camera.enabled == True)
    return query.all()


def create_camera(db: Session, name: str, camera_index: int, url: Optional[str] = None, 
                  settings_json: Optional[dict] = None) -> models.Camera:
    """Create a new camera"""
    db_camera = models.Camera(
        name=name,
        camera_index=camera_index,
        url=url,
        settings_json=settings_json
    )
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera


def update_camera_settings(db: Session, camera_id: int, settings_json: dict):
    """Update camera settings"""
    db.query(models.Camera).filter(models.Camera.id == camera_id).update({
        "settings_json": settings_json,
        "updated_at": datetime.utcnow()
    })
    db.commit()


def delete_camera(db: Session, camera_id: int):
    """Delete a camera (and cascade to recordings/events)"""
    camera = db.query(models.Camera).filter(models.Camera.id == camera_id).first()
    if camera:
        db.delete(camera)
        db.commit()


# ===========================================
# Recording CRUD
# ===========================================

def create_recording(db: Session, camera_id: int, filepath: str, start_time: datetime,
                     is_master: bool = False) -> models.Recording:
    """Create a new recording entry"""
    db_recording = models.Recording(
        camera_id=camera_id,
        filepath=filepath,
        start_time=start_time,
        is_master=is_master
    )
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    return db_recording


def update_recording_end(db: Session, recording_id: int, end_time: datetime, file_size_bytes: int):
    """Update recording when it finishes"""
    db.query(models.Recording).filter(models.Recording.id == recording_id).update({
        "end_time": end_time,
        "file_size_bytes": file_size_bytes
    })
    db.commit()


def get_recordings_by_camera(db: Session, camera_id: int, limit: int = 50) -> List[models.Recording]:
    """Get recordings for a specific camera"""
    return db.query(models.Recording).filter(
        and_(
            models.Recording.camera_id == camera_id,
            models.Recording.deleted == False
        )
    ).order_by(desc(models.Recording.start_time)).limit(limit).all()


def get_recordings_in_date_range(db: Session, start_date: datetime, end_date: datetime,
                                  camera_id: Optional[int] = None) -> List[models.Recording]:
    """Get recordings within a date range"""
    query = db.query(models.Recording).filter(
        and_(
            models.Recording.start_time >= start_date,
            models.Recording.start_time <= end_date,
            models.Recording.deleted == False
        )
    )
    if camera_id:
        query = query.filter(models.Recording.camera_id == camera_id)
    return query.order_by(desc(models.Recording.start_time)).all()


def soft_delete_recording(db: Session, recording_id: int):
    """Soft delete a recording"""
    db.query(models.Recording).filter(models.Recording.id == recording_id).update({
        "deleted": True,
        "deleted_at": datetime.utcnow()
    })
    db.commit()


def get_oldest_recordings(db: Session, camera_id: int, limit: int = 10) -> List[models.Recording]:
    """Get oldest recordings for cleanup purposes"""
    return db.query(models.Recording).filter(
        and_(
            models.Recording.camera_id == camera_id,
            models.Recording.deleted == False
        )
    ).order_by(models.Recording.start_time).limit(limit).all()


# ===========================================
# Detection Event CRUD
# ===========================================

def create_detection_event(db: Session, camera_id: int, event_type: str, people_count: int = 0,
                            weapon_detected: bool = False, confidence: Optional[float] = None,
                            metadata_json: Optional[dict] = None) -> models.DetectionEvent:
    """Create a new detection event"""
    db_event = models.DetectionEvent(
        camera_id=camera_id,
        event_type=event_type,
        people_count=people_count,
        weapon_detected=weapon_detected,
        confidence=confidence,
        metadata_json=metadata_json
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def get_recent_events(db: Session, limit: int = 100, camera_id: Optional[int] = None) -> List[models.DetectionEvent]:
    """Get recent detection events"""
    query = db.query(models.DetectionEvent)
    if camera_id:
        query = query.filter(models.DetectionEvent.camera_id == camera_id)
    return query.order_by(desc(models.DetectionEvent.timestamp)).limit(limit).all()


def get_events_in_date_range(db: Session, start_date: datetime, end_date: datetime,
                              event_type: Optional[str] = None) -> List[models.DetectionEvent]:
    """Get events within a date range"""
    query = db.query(models.DetectionEvent).filter(
        and_(
            models.DetectionEvent.timestamp >= start_date,
            models.DetectionEvent.timestamp <= end_date
        )
    )
    if event_type:
        query = query.filter(models.DetectionEvent.event_type == event_type)
    return query.order_by(desc(models.DetectionEvent.timestamp)).all()


def get_event_statistics(db: Session, start_date: datetime, end_date: datetime) -> dict:
    """Get statistics about events in a date range"""
    events = get_events_in_date_range(db, start_date, end_date)
    
    total_events = len(events)
    weapon_detections = sum(1 for e in events if e.weapon_detected)
    total_people = sum(e.people_count for e in events)
    
    return {
        "total_events": total_events,
        "weapon_detections": weapon_detections,
        "total_people_detected": total_people,
        "average_people_per_event": total_people / total_events if total_events > 0 else 0
    }


# ===========================================
# System Log CRUD
# ===========================================

def create_system_log(db: Session, level: str, message: str, context_json: Optional[dict] = None) -> models.SystemLog:
    """Create a system log entry"""
    db_log = models.SystemLog(
        level=level.upper(),
        message=message,
        context_json=context_json
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_recent_logs(db: Session, limit: int = 100, level: Optional[str] = None) -> List[models.SystemLog]:
    """Get recent system logs"""
    query = db.query(models.SystemLog)
    if level:
        query = query.filter(models.SystemLog.level == level.upper())
    return query.order_by(desc(models.SystemLog.timestamp)).limit(limit).all()


def cleanup_old_logs(db: Session, days: int = 30):
    """Delete logs older than specified days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    db.query(models.SystemLog).filter(models.SystemLog.timestamp < cutoff_date).delete()
    db.commit()


# ===========================================
# Model Version CRUD
# ===========================================

def create_model_version(db: Session, name: str, filepath: str, version: Optional[str] = None,
                         description: Optional[str] = None) -> models.ModelVersion:
    """Register a new model version"""
    db_model = models.ModelVersion(
        name=name,
        filepath=filepath,
        version=version,
        description=description
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


def set_active_model(db: Session, model_id: int):
    """Set a model as active (deactivate others)"""
    # Deactivate all models
    db.query(models.ModelVersion).update({"is_active": False})
    
    # Activate the specified model
    db.query(models.ModelVersion).filter(models.ModelVersion.id == model_id).update({
        "is_active": True,
        "loaded_at": datetime.utcnow()
    })
    db.commit()


def get_active_model(db: Session) -> Optional[models.ModelVersion]:
    """Get the currently active model"""
    return db.query(models.ModelVersion).filter(models.ModelVersion.is_active == True).first()
