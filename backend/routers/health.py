"""Health check and system status endpoints"""

import time
import psutil
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database

from backend.database import get_db_mongo
from backend.models.schemas import HealthResponse, DetailedHealthResponse
from backend.auth import get_current_user
from backend.config import settings

router = APIRouter(prefix="/api/v1", tags=["Health"])

# Track application start time
_start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Database = Depends(get_db_mongo)):
    """
    Basic health check endpoint (public, no authentication required)
    
    Returns system status and basic information
    """
    # Test database connection
    db_connected = False
    try:
        db.command("ping")
        db_connected = True
    except Exception:
        pass
    
    # Count active cameras (placeholder - will be dynamic later)
    cameras_active = 0
    
    return {
        "status": "healthy" if db_connected else "degraded",
        "version": settings.app_version,
        "environment": settings.environment,
        "database_connected": db_connected,
        "cameras_active": cameras_active
    }


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db_mongo)
):
    """
    Detailed health check with system metrics (requires authentication)
    
    Returns extended diagnostics including uptime, database stats, disk usage
    """
    # Test database connection
    db_connected = False
    try:
        db.command("ping")
        db_connected = True
    except Exception:
        pass
    
    # Calculate uptime
    uptime_seconds = time.time() - _start_time
    
    # Get database statistics
    total_recordings = 0
    total_events = 0
    
    try:
        total_recordings = db.recordings.count_documents({"deleted": False})
        total_events = db.detection_events.count_documents({})
    except Exception:
        pass
    
    # Get disk usage for recordings folder
    disk_usage_percent = 0.0
    try:
        recordings_path = Path(settings.recordings_folder)
        if recordings_path.exists():
            disk = psutil.disk_usage(str(recordings_path))
            disk_usage_percent = disk.percent
    except Exception:
        pass
    
    # Count active cameras (will be updated when integrated)
    cameras_active = 0
    
    return {
        "status": "healthy" if db_connected else "degraded",
        "version": settings.app_version,
        "environment": settings.environment,
        "database_connected": db_connected,
        "cameras_active": cameras_active,
        "uptime_seconds": uptime_seconds,
        "total_recordings": total_recordings,
        "total_events": total_events,
        "disk_usage_percent": disk_usage_percent
    }
