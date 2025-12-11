"""FastAPI application with all routes"""

import cv2
import logging
import threading
import time
from pathlib import Path
from typing import Dict

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from ultralytics import YOLO

from backend.config import settings
from backend.models.schemas import CameraSettings
from backend.managers.log_manager import LogManager
from backend.managers.camera_manager import CameraManager
from backend.managers.recording_manager import RecordingManager
from backend.managers.master_recorder import MasterRecorder
from backend.utils.video_utils import draw_timestamp
from backend.database.mongodb import get_database, close_mongo_connection
from backend.routers import auth, health

logger = logging.getLogger(__name__)

# Initialize managers
log_manager = LogManager(settings.logs_folder)
camera_manager = CameraManager(log_manager)
recording_manager = RecordingManager(log_manager, settings.recordings_folder, settings.recording_size_limit_gb)
master_recorder = MasterRecorder(log_manager, settings.master_folder, settings.master_size_limit_gb)

# Track latest frames for master recording
latest_frames: Dict[int, np.ndarray] = {}
frames_lock = threading.Lock()

# YOLO model management
current_model = None
model_lock = threading.Lock()
detection_enabled = False
recording_enabled = False

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered security system with real-time threat detection",
)

# CORS configuration from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router)
app.include_router(health.router)

def generate_mjpeg_stream(camera_id: int):
    """Generate MJPEG stream for a camera"""
    cap, lock = camera_manager.get_camera(camera_id)
    if cap is None:
        return
    
    consecutive_failures = 0
    last_settings = {}
    
    while True:
        try:
            with lock:
                current_settings = camera_manager.settings.get(camera_id, {})
                if current_settings != last_settings:
                    try:
                        if camera_manager.is_windows:
                            cap.set(cv2.CAP_PROP_BRIGHTNESS, current_settings["brightness"] / 100.0 * 255)
                            cap.set(cv2.CAP_PROP_CONTRAST, current_settings["contrast"] / 100.0 * 255)
                            cap.set(cv2.CAP_PROP_SATURATION, current_settings["saturation"] / 100.0 * 255)
                        else:
                            cap.set(cv2.CAP_PROP_BRIGHTNESS, current_settings["brightness"])
                            cap.set(cv2.CAP_PROP_CONTRAST, current_settings["contrast"])
                            cap.set(cv2.CAP_PROP_SATURATION, current_settings["saturation"])
                        cap.set(cv2.CAP_PROP_GAMMA, current_settings["gamma"])
                        last_settings = current_settings.copy()
                    except Exception as e:
                        logger.warning(f"Error applying settings: {e}")

                success, frame = cap.read()
            
            if not success:
                consecutive_failures += 1
                if consecutive_failures > settings.max_consecutive_failures:
                    log_manager.add_log(f"Camera {camera_id} appears frozen, releasing", "error")
                    camera_manager.release_camera(camera_id)
                    break
                time.sleep(0.1)
                continue
            
            consecutive_failures = 0
            camera_manager.last_frame_time[camera_id] = time.time()
            
            draw_timestamp(frame)

            frame_people_count = 0
            frame_weapon_detected = False
            
            if detection_enabled and current_model is not None:
                with model_lock:
                    try:
                        results = current_model(frame, verbose=False)
                        for result in results:
                            for box in result.boxes:
                                cls = int(box.cls[0])
                                conf = float(box.conf[0])
                                x1, y1, x2, y2 = map(int, box.xyxy[0])
                                
                                if cls == 0 or cls == 1: 
                                    frame_people_count += 1
                                    color = (0, 0, 255) if cls == 0 and 'sus' in getattr(current_model, 'model_name', '') else (0, 255, 0)
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                                    cv2.putText(frame, f"Person {conf:.2f}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                                
                                elif cls in [43, 76]:
                                    frame_weapon_detected = True
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                                    cv2.putText(frame, f"Weapon {conf:.2f}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    except Exception as e:
                        logger.error(f"Detection error: {e}")
            
            camera_manager.update_stats(camera_id, frame_people_count, frame_weapon_detected)

            with frames_lock:
                latest_frames[camera_id] = frame.copy()

            if recording_enabled:
                recording_manager.write_frame(camera_id, frame)
            elif camera_id in recording_manager.writers:
                recording_manager.stop_recording(camera_id)
            
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, settings.jpeg_quality])
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            
            time.sleep(0.033)
            
        except GeneratorExit:
            break
        except Exception as e:
            logger.error(f"Stream error: {e}")
            time.sleep(0.1)

def master_recording_thread():
    """Background thread for master recording"""
    while True:
        try:
            if recording_enabled and master_recorder.writer is not None:
                with frames_lock:
                    frames_copy = latest_frames.copy()
                
                model_name = getattr(current_model, 'model_name', 'None') if current_model else 'None'
                people_count = camera_manager.get_stats()['people_count']
                
                master_recorder.write_grid_frame(frames_copy, model_name, people_count)
            
            time.sleep(0.05)
        except Exception as e:
            logger.error(f"Master recording thread error: {e}")
            time.sleep(0.1)

# Start master recording thread
master_thread = threading.Thread(target=master_recording_thread, daemon=True)
master_thread.start()

# Routes
@app.get("/")
async def root():
    return {"message": "Camera Server Running"}

@app.get("/camera/{camera_id}")
async def video_feed(camera_id: int):
    return StreamingResponse(
        generate_mjpeg_stream(camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/cameras")
async def list_cameras():
    available = []
    for i in range(settings.max_cameras):
        try:
            if camera_manager.is_windows:
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(i)
            
            # Shorter timeout to reduce delay
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 500)
            
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available.append({
                        "id": i,
                        "name": f"Camera {i}",
                        "url": f"http://localhost:8000/camera/{i}"
                    })
            cap.release()
        except Exception:
            # Silently skip cameras that can't be accessed
            continue
    return {"cameras": available}

@app.get("/models")
async def list_models():
    models_dir = Path(settings.models_folder)
    if not models_dir.exists():
        return {"models": []}
    
    models = []
    for model_file in models_dir.glob("*.pt"):
        models.append({
            "name": model_file.name,
            "path": str(model_file),
            "size_mb": round(model_file.stat().st_size / (1024 * 1024), 2)
        })
    
    return {
        "models": models,
        "current_model": current_model.model_name if current_model and hasattr(current_model, 'model_name') else None,
        "detection_enabled": detection_enabled
    }

@app.post("/model/load")
async def load_model(model_name: str):
    global current_model, detection_enabled
    model_path = Path(settings.models_folder) / model_name
    
    if not model_path.exists():
        return {"success": False}
    
    try:
        with model_lock:
            current_model = YOLO(str(model_path))
            current_model.model_name = model_name
            detection_enabled = True
            log_manager.add_log(f"Model loaded: {model_name}", "info")
        return {"success": True}
    except Exception:
        return {"success": False}

@app.post("/detection/toggle")
async def toggle_detection(enabled: bool):
    global detection_enabled
    detection_enabled = enabled
    log_manager.add_log(f"Detection {'enabled' if enabled else 'disabled'}", "info")
    return {"success": True}

@app.post("/recording/toggle")
async def toggle_recording(enabled: bool):
    global recording_enabled
    recording_enabled = enabled
    
    if enabled:
        for cid in camera_manager.cameras:
            cap = camera_manager.cameras[cid]
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            recording_manager.start_recording(cid, w, h)
        master_recorder.start_recording()
    else:
        recording_manager.stop_all()
        master_recorder.stop_recording()
            
    return {"success": True}

@app.get("/recording/status")
async def get_recording_status():
    return {"recording_enabled": recording_enabled}

@app.post("/camera/{camera_id}/settings")
async def update_camera_settings(camera_id: int, settings: CameraSettings):
    camera_manager.settings[camera_id] = {
        "brightness": settings.brightness,
        "contrast": settings.contrast,
        "saturation": settings.saturation,
        "gamma": settings.gamma
    }
    return {"success": True}

@app.get("/camera/{camera_id}/settings")
async def get_camera_settings(camera_id: int):
    return camera_manager.settings.get(camera_id, {
        "brightness": 50, "contrast": 50, "saturation": 50, "gamma": 50
    })

@app.get("/stats")
async def get_stats():
    return camera_manager.get_stats()

@app.get("/logs")
async def get_logs():
    return {"logs": log_manager.get_logs()}

@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    logger.info("🚀 Starting AI Security System...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"MongoDB URI: {settings.mongodb_uri}")
    logger.info(f"Database: {settings.mongodb_database}")
    
    # Initialize MongoDB connection and collections
    try:
        db = get_database()
        logger.info(f"✅ Connected to MongoDB: {db.name}")
        logger.info(f"   Collections: {', '.join(db.list_collection_names())}")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        logger.error("   Make sure MongoDB is running!")
    
    log_manager.add_log("System started", "info")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    recording_manager.stop_all()
    master_recorder.stop_recording()
    camera_manager.release_all()
    close_mongo_connection()
    log_manager.add_log("System shutdown", "info")
