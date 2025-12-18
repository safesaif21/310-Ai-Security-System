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
from backend.database.mongodb import get_database, close_mongo_connection
from backend.routers import auth, health, recordings, logs

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

# Global event for new frames
frame_events: Dict[int, threading.Event] = {}
stop_events: Dict[int, threading.Event] = {}

def capture_camera_loop(camera_id: int):
    """Background loop to capture frames from a camera"""
    logger.info(f"Starting capture loop for camera {camera_id}")
    cap, lock = camera_manager.get_camera(camera_id)
    if cap is None:
        logger.error(f"Could not open camera {camera_id} for capture loop")
        return

    consecutive_failures = 0
    last_settings = {}
    
    # Create event for this camera
    if camera_id not in frame_events:
        frame_events[camera_id] = threading.Event()
    
    while not stop_events.get(camera_id, threading.Event()).is_set():
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
                    # Break loop, but maybe we should try to re-init? 
                    # For now, just stop to prevent infinite error loops
                    break 
                time.sleep(0.1)
                continue
            
            consecutive_failures = 0
            camera_manager.last_frame_time[camera_id] = time.time()
            
            draw_timestamp(frame)

            frame_people_count = 0
            frame_weapon_detected = False
            
            # Run detection if enabled
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
            
            # Signal new frame available
            frame_events[camera_id].set()
            frame_events[camera_id].clear() # Reset for next frame

            if recording_enabled:
                recording_manager.write_frame(camera_id, frame)
            elif camera_id in recording_manager.writers:
                recording_manager.stop_recording(camera_id)
            
            # Cap at ~30 FPS
            time.sleep(0.01)

        except Exception as e:
            logger.error(f"Capture loop error camera {camera_id}: {e}")
            time.sleep(0.1)
        
        if consecutive_failures % 100 == 0:
             logger.debug(f"Cam {camera_id} capture loop alive. Settings: {last_settings}")
    
    logger.info(f"Stopping capture loop for camera {camera_id}")
    camera_manager.release_camera(camera_id)

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
app.include_router(recordings.router)
app.include_router(logs.router)

def generate_mjpeg_stream(camera_id: int):
    """Generate MJPEG stream for a camera from the latest captured frame"""
    if camera_id not in latest_frames and camera_id not in frame_events:
         # Wait a bit to see if it starts
         time.sleep(1)
         if camera_id not in latest_frames:
             return

    # Helper event to wait for
    event = frame_events.get(camera_id)
    logger.info(f"Stream started for camera {camera_id}")

    frame_count_debug = 0

    while True:
        try:
            # Wait for new frame
            if event:
                event.wait(timeout=1.0)
            
            with frames_lock:
                if camera_id in latest_frames:
                    frame = latest_frames[camera_id].copy()
                else:
                    frame = None
            
            if frame is None:
                time.sleep(0.1)
                continue
            
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, settings.jpeg_quality])
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            
            # Avoid tight loops if event logic fails
            time.sleep(0.01)

            frame_count_debug += 1
            if frame_count_debug % 30 == 0:
                logger.debug(f"Stream {camera_id} sending frame {frame_count_debug}")
            
        except GeneratorExit:
            logger.info(f"Stream client disconnected for camera {camera_id}")
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
    # Return currently active cameras + any that were detected
    # With the new background loop, we could just return 'latest_frames.keys()'
    # but we also want to return what is 'available' even if not currently running (e.g. crashed)
    
    # For now, let's just return all cameras that we have data for or are in manager
    active_cameras = []
    
    # Combine keys from camera_manager.cameras and any detected available ones
    # We rely on the startup detection being the source of truth for now
    
    # We can invoke detection if no cameras are found? 
    # Or just return the ones we started
    
    for cam_id in list(camera_manager.cameras.keys()):
        active_cameras.append({
            "id": cam_id,
            "name": f"Camera {cam_id}",
            "url": f"/camera/{cam_id}" # Relative URL for network access
        })
        
    return {"cameras": active_cameras}

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
            # Check if we already have a writer for this camera to avoid double-start
            if cid not in recording_manager.writers:
                 cap = camera_manager.cameras[cid]
                 w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                 h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                 fps = cap.get(cv2.CAP_PROP_FPS)
                 if fps <= 0 or fps > 60: fps = 30.0 # Fallback
                 
                 recording_manager.start_recording(cid, w, h, fps)
        
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

@app.get("/debug/status")
async def debug_status():
    return {
        "recording_enabled": recording_enabled,
        "active_recordings": list(recording_manager.writers.keys()),
        "master_recording": master_recorder.writer is not None,
        "camera_threads": list(stop_events.keys()),
        "active_cameras": list(camera_manager.cameras.keys())
    }

@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    logger.info("Starting AI Security System...")
    logger.info(f"Environment: {settings.environment}")
    
    # Initialize MongoDB connection and collections
    try:
        db = get_database()
        logger.info(f"✅ Connected to MongoDB: {db.name}")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        logger.error("   Make sure MongoDB is running!")
    
    log_manager.add_log("System started", "info")
    
    # Auto-detect available cameras
    available_cameras = camera_manager.detect_available_cameras(settings.max_cameras)
    
    if not available_cameras:
        logger.warning("No cameras detected on startup.")
        log_manager.add_log("No cameras detected on startup", "warning")
        return
    
    # Start background capture threads for each camera
    logger.info(f"Starting capture threads for {len(available_cameras)} camera(s)...")
    for cam_id in available_cameras:
        logger.info(f"Starting background capture for Camera {cam_id}")
        stop_events[cam_id] = threading.Event()
        t = threading.Thread(target=capture_camera_loop, args=(cam_id,), daemon=True)
        t.start()
    
    # Give capture threads time to initialize cameras
    logger.info("Waiting for cameras to initialize...")
    time.sleep(2)
    
    # Enable global recording
    global recording_enabled
    recording_enabled = True
    logger.info("✅ Enabling global recording on startup")
    log_manager.add_log("Global recording enabled on startup", "info")
    
    # Start recording for all cameras
    for cam_id in available_cameras:
        try:
            cap, _ = camera_manager.get_camera(cam_id)
            if cap is not None and cap.isOpened():
                w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps <= 0 or fps > 60: fps = 30.0 # Fallback
                
                recording_manager.start_recording(cam_id, w, h, fps)
                logger.info(f"✅ Recording started for Camera {cam_id} ({w}x{h} @ {fps}fps)")
            else:
                logger.warning(f"⚠️  Camera {cam_id} not ready for recording")
        except Exception as e:
            logger.error(f"❌ Failed to start recording for Camera {cam_id}: {e}")
    
    # Start master recorder
    try:
        master_recorder.start_recording()
        logger.info("✅ Master recorder started")
    except Exception as e:
        logger.error(f"❌ Failed to start master recorder: {e}")
    
    logger.info("🚀 System startup complete!")
    log_manager.add_log("System startup complete", "success")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    
    # Stop all capture threads
    for cam_id, event in stop_events.items():
        event.set()
    
    recording_manager.stop_all()
    master_recorder.stop_recording()
    camera_manager.release_all()
    close_mongo_connection()
    log_manager.add_log("System shutdown", "info")
