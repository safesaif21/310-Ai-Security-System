
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List
import os
from backend.config import settings

router = APIRouter(prefix="/recordings", tags=["recordings"])

RECORDINGS_DIR = Path(settings.recordings_folder)
MASTER_DIR = Path(settings.master_folder)

@router.get("/cameras")
async def get_cameras_with_recordings():
    """List cameras that have recordings available"""
    cameras = []
    if RECORDINGS_DIR.exists():
        for item in RECORDINGS_DIR.iterdir():
            if item.is_dir() and item.name.startswith("camera_"):
                try:
                    cam_id = int(item.name.replace("camera_", ""))
                    cameras.append(cam_id)
                except ValueError:
                    continue
    return {"cameras": sorted(cameras)}

@router.get("/master/files")
async def list_master_files():
    """List master recording files"""
    if not MASTER_DIR.exists():
        return {"files": []}
    
    files = []
    # Support both mp4 and webm
    for item in MASTER_DIR.glob("*.mp4"):
        stats = item.stat()
        files.append({
            "name": item.name,
            "size_mb": round(stats.st_size / (1024 * 1024), 2),
            "timestamp": stats.st_mtime
        })
    
    files.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"files": files}

@router.get("/{camera_id}/files")
async def list_recording_files(camera_id: int):
    """List recording files for a specific camera"""
    camera_dir = RECORDINGS_DIR / f"camera_{camera_id}"
    if not camera_dir.exists():
        return {"files": []}
    
    files = []
    # Support both mp4 and webm
    for item in camera_dir.glob("*.mp4"):
        stats = item.stat()
        files.append({
            "name": item.name,
            "size_mb": round(stats.st_size / (1024 * 1024), 2),
            "timestamp": stats.st_mtime,
            "date": item.name.split("_")[1] # Extract date from filename rec_YYYYMMDD...
        })
    
    # Sort by timestamp descending (newest first)
    files.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"files": files}



@router.get("/files/master")
async def list_master_files_legacy():
    # Alias or moved
    return await list_master_files()

@router.get("/serve/master/{filename}")
async def serve_master_recording(filename: str):
    """Serve a master recording file"""
    file_path = MASTER_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    media_type = "video/webm" if filename.endswith(".webm") else "video/mp4"
    return FileResponse(file_path, media_type=media_type)

@router.get("/serve/{camera_id}/{filename}")
async def serve_recording(camera_id: int, filename: str):
    """Serve a recording file"""
    file_path = RECORDINGS_DIR / f"camera_{camera_id}" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    media_type = "video/webm" if filename.endswith(".webm") else "video/mp4"
    return FileResponse(file_path, media_type=media_type)
