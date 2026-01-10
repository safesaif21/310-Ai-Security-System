"""Camera Service Entry Point (Raw Capture)"""

import os
import threading
import time
import logging
from typing import Dict
import cv2
import numpy as np
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.shared.config import settings
from backend.shared.managers import CameraManager
from backend.shared.utils.logging_utils import send_log

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Initialize manager (No Recording/Logs here)
camera_manager = CameraManager()

# Track latest frames for streaming
latest_frames: Dict[int, np.ndarray] = {}
frames_lock = threading.Lock()
frame_events: Dict[int, threading.Event] = {}
stop_events: Dict[int, threading.Event] = {}

class CameraSettingsModel(BaseModel):
    brightness: int
    contrast: int
    saturation: int
    gamma: int

def capture_camera_loop(camera_id: int):
    """Background loop to capture raw frames"""
    cap, lock = camera_manager.get_camera(camera_id)
    if cap is None: return

    if camera_id not in frame_events:
        frame_events[camera_id] = threading.Event()
    
    while not stop_events.get(camera_id, threading.Event()).is_set():
        try:
            with lock:
                success, frame = cap.read()
            
            if not success:
                time.sleep(0.1)
                continue
            
            with frames_lock:
                latest_frames[camera_id] = frame.copy()
            
            frame_events[camera_id].set()
            # Note: We don't clear immediately, we let the generator wait for it
            
            time.sleep(0.01) # ~30-60 FPS
        except Exception as e:
            logger.error(f"Capture error cam {camera_id}: {e}")
            time.sleep(1)

def generate_mjpeg_stream(camera_id: int):
    """Serve Raw MJPEG Stream"""
    while True:
        try:
            event = frame_events.get(camera_id)
            if event: event.wait(timeout=1.0)
            
            with frames_lock:
                frame = latest_frames.get(camera_id)
            
            if frame is None:
                time.sleep(0.1)
                continue
            
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            
            if event: event.clear()
        except GeneratorExit: break
        except Exception: time.sleep(0.1)

app = FastAPI(title="Camera Service (Raw)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/camera/{camera_id}")
async def video_feed(camera_id: int):
    return StreamingResponse(generate_mjpeg_stream(camera_id), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/cameras")
async def list_cameras():
    return {"cameras": [{"id": cid, "name": f"Camera {cid}"} for cid in camera_manager.cameras.keys()]}

@app.put("/camera/{camera_id}/settings")
async def update_camera_settings(camera_id: int, settings: CameraSettingsModel):
    success = camera_manager.update_settings(camera_id, settings.dict())
    if success:
        return {"status": "success", "settings": settings}
    return {"status": "error", "message": "Failed to update camera settings"}

@app.get("/camera/{camera_id}/settings")
async def get_camera_settings(camera_id: int):
    if camera_id in camera_manager.settings:
        return camera_manager.settings[camera_id]
    return {"brightness": 50, "contrast": 50, "saturation": 50, "gamma": 50}

@app.on_event("startup")
async def startup_event():
    available = camera_manager.detect_available_cameras(settings.max_cameras)
    send_log(f"Camera Service discovered {len(available)} cameras: {available}", "info")
    for cam_id in available:
        send_log(f"Starting capture thread for Camera {cam_id}", "info")
        stop_events[cam_id] = threading.Event()
        threading.Thread(target=capture_camera_loop, args=(cam_id,), daemon=True).start()

@app.on_event("shutdown")
async def shutdown_event():
    for event in stop_events.values(): event.set()
    camera_manager.release_all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8041)
