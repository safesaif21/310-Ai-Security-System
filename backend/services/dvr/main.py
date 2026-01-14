"""DVR Service Entry Point (Annotated Recording + Centralized Logging + Static Serving)"""

import threading
import time
import logging
import os
from pathlib import Path
import requests
import cv2
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.shared.config import settings
from backend.shared.managers import LogManager, RecordingManager

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Environment variables
ANALYSIS_SERVICE_URL = os.getenv("ANALYSIS_SERVICE_URL", "http://analysis-service:8042")

# Initialize managers
log_manager = LogManager(settings.logs_folder)
recording_manager = RecordingManager(
    log_manager, 
    settings.recordings_folder, 
    settings.recording_size_limit_gb,
    rotation_seconds=settings.recording_rotation_seconds
)

stop_events = {}
recording_threads = {}

# --- Log Service Logic ---
class LogEntry(BaseModel):
    message: str
    type: str = "info"

app = FastAPI(title="DVR & Log Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serves recordings so the frontend can play them: http://localhost:8043/stream/camera_0/rec_...mp4
app.mount("/stream", StaticFiles(directory=settings.recordings_folder), name="recordings")

def recording_loop(camera_id: int):
    """Consume annotated stream via custom MJPEG parser"""
    stream_url = f"{ANALYSIS_SERVICE_URL}/annotated/{camera_id}"
    logger.info(f"Connecting to annotated stream: {stream_url}")
    log_manager.add_log(f"DVR starting recording for camera {camera_id}", "info")
    
    TARGET_FPS = 15.0
    frame_interval = 1.0 / TARGET_FPS
    last_frame_write = time.time()
    
    while not stop_events.get(camera_id, threading.Event()).is_set():
        try:
            # Use requests with stream=True for manual MJPEG parsing
            # This bypasses OpenCV's internal ffmpeg demuxer which is failing
            with requests.get(stream_url, stream=True, timeout=30) as r:
                if r.status_code != 200:
                    logger.error(f"Stream error {r.status_code}")
                    time.sleep(2)
                    continue

                bytes_data = b""
                for chunk in r.iter_content(chunk_size=4096):
                    if stop_events.get(camera_id, threading.Event()).is_set():
                        break
                    
                    bytes_data += chunk
                    
                    # Look for JPEG delimiters
                    a = bytes_data.find(b'\xff\xd8')
                    b = bytes_data.find(b'\xff\xd9')
                    
                    if a != -1 and b != -1:
                        # Found a full frame
                        jpg = bytes_data[a:b+2]
                        bytes_data = bytes_data[b+2:]
                        
                        frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        if frame is None: continue

                        # Ensure recording is initialized
                        if not recording_manager.recording_started.get(camera_id):
                            h, w = frame.shape[:2]
                            recording_manager.start_recording(camera_id, w, h, TARGET_FPS)
                            last_frame_write = time.time()

                        # Write at strict FPS
                        current_time = time.time()
                        if current_time - last_frame_write >= frame_interval:
                            recording_manager.write_frame(camera_id, frame)
                            last_frame_write += frame_interval
                            
                            # Prevent drift/lag
                            if current_time - last_frame_write > 1.0:
                                last_frame_write = current_time

        except Exception as e:
            logger.error(f"DVR stream error cam {camera_id}: {e}")
            time.sleep(2)

    recording_manager.stop_recording(camera_id)
    log_manager.add_log(f"DVR stopped recording for camera {camera_id}", "info")

def auto_start_recordings_loop():
    """Periodically check analysis service for active streams to record"""
    logger.info("Starting DVR auto-start loop...")
    while True:
        try:
            response = requests.get(f"{ANALYSIS_SERVICE_URL}/status", timeout=2)
            if response.status_code == 200:
                analyzing = response.json().get("analyzing", [])
                for cid in analyzing:
                    if int(cid) not in recording_threads:
                        # Use the start_recording helper logic
                        camera_id = int(cid)
                        stop_events[camera_id] = threading.Event()
                        t = threading.Thread(target=recording_loop, args=(camera_id,), daemon=True)
                        t.start()
                        recording_threads[camera_id] = t
                        logger.info(f"Auto-started recording for cam {cid}")
        except Exception:
            pass
        time.sleep(30)

@app.on_event("startup")
async def startup_event():
    logger.info("DVR & Log Service initializing...")
    log_manager.add_log("DVR & Log Service started and ready for events", "info")
    
    # Start auto-start monitor
    threading.Thread(target=auto_start_recordings_loop, daemon=True).start()

# --- API Endpoints ---

@app.post("/logs/events")
async def post_log_event(entry: LogEntry):
    """Unified endpoint for all services to push logs to"""
    print(f"-> Log received: {entry.message} [{entry.type}]")
    log_manager.add_log(entry.message, entry.type)
    return {"status": "ok"}

@app.get("/logs")
async def get_logs():
    """Retrieve recent logs for the prompt display"""
    return {"logs": log_manager.get_logs(100)}

@app.get("/logs/dates")
async def get_log_dates():
    """List all available log files directly from the filesystem"""
    log_dir = Path(settings.logs_folder)
    if not log_dir.exists(): return {"dates": []}
    
    # Get all .txt files, sorted by newest first
    files = sorted(log_dir.glob("*.txt"), key=os.path.getmtime, reverse=True)
    # Return filenames (e.g., '2026-01-10.txt')
    return {"dates": [f.name for f in files]}

@app.get("/logs/by-date/{date_str}")
async def get_logs_by_date(date_str: str):
    """Retrieve full logs for a specific date/file"""
    # Clean up filename if provided with extension
    clean_date = date_str.replace(".txt", "")
    return {"logs": log_manager.get_logs_by_date(clean_date)}

@app.get("/recordings")
async def list_recordings():
    """List all available recording files for the frontend"""
    results = {}
    base_path = Path(settings.recordings_folder)
    if not base_path.exists(): return {"recordings": {}}
    
    for cam_dir in base_path.iterdir():
        if cam_dir.is_dir():
            cam_id = cam_dir.name.replace("camera_", "")
            files = sorted(cam_dir.glob("*.mp4"), key=os.path.getmtime, reverse=True)
            results[cam_id] = [f.name for f in files]
            
    return {"recordings": results}

@app.post("/recording/start/{camera_id}")
async def start_recording(camera_id: int):
    if camera_id not in recording_threads:
        stop_events[camera_id] = threading.Event()
        t = threading.Thread(target=recording_loop, args=(camera_id,), daemon=True)
        t.start()
        recording_threads[camera_id] = t
    return {"status": "started", "camera_id": camera_id}

@app.post("/recording/stop/{camera_id}")
async def stop_recording(camera_id: int):
    if camera_id in stop_events:
        stop_events[camera_id].set()
        del stop_events[camera_id]
        if camera_id in recording_threads:
            del recording_threads[camera_id]
    return {"status": "stopped", "camera_id": camera_id}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "dvr-logs-unified"}
