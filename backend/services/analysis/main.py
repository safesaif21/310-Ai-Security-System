"""Analysis Service Entry Point (YOLO + Optimized Annotated Streaming)"""

import logging
import os
import threading
import time
import requests
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO

from backend.shared.config import settings
from backend.shared.utils.logging_utils import send_log

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Environment variables
CAMERA_SERVICE_URL = os.getenv("CAMERA_SERVICE_URL", "http://localhost:8041")
LOG_SERVICE_URL = os.getenv("LOG_SERVICE_URL", "http://dvr-service:8043")

# Global state
current_model = None
detection_enabled = True
model_lock = threading.Lock()
stop_events: Dict[int, threading.Event] = {}

# Annotated Frames for re-streaming
annotated_frames: Dict[int, np.ndarray] = {}
frames_lock = threading.Lock()
frame_events: Dict[int, threading.Event] = {}

# Detection persistence and cooldown (Moved from CameraManager logic)
people_streak: Dict[int, int] = {}
weapon_streak: Dict[int, int] = {}
current_counts: Dict[int, int] = {}
current_weapons: Dict[int, bool] = {}
last_log_times: Dict[int, Dict[str, float]] = {}
stats_lock = threading.Lock()

# Target Classes (COCO)
# 0: person
# 43: knife
# 76: scissors
# 34: baseball bat
TARGET_CLASSES = [0, 34, 43, 76]

def get_cameras_from_service():
    """Fetch active cameras from Camera Service"""
    try:
        response = requests.get(f"{CAMERA_SERVICE_URL}/cameras", timeout=2)
        if response.status_code == 200:
            return response.json().get("cameras", [])
        return []
    except Exception as e:
        logger.error(f"Failed to fetch cameras: {e}")
        return []

def process_stream(camera_id: int):
    """Analyze stream from a camera and save annotated frames"""
    stream_url = f"{CAMERA_SERVICE_URL}/camera/{camera_id}"
    logger.info(f"Connecting to raw stream: {stream_url}")
    
    # Use a faster buffer setting
    cap = cv2.VideoCapture(stream_url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if camera_id not in frame_events:
        frame_events[camera_id] = threading.Event()

    frame_count = 0
    last_results = []
    people_count = 0
    weapon_detected = False
    
    while not stop_events.get(camera_id, threading.Event()).is_set():
        try:
            # --- HIGH FPS STREAMING: Read every frame ---
            success, frame = cap.read()
            if not success:
                time.sleep(0.01) # Small sleep to avoid CPU hogging on fail
                continue

            frame_count += 1
            
            # Update AI results every 6th frame (~5 updates per second)
            if detection_enabled and frame_count % 6 == 0:
                with model_lock:
                     if current_model:
                         last_results = current_model(
                             frame, 
                             verbose=False, 
                             imgsz=320, 
                             classes=TARGET_CLASSES,
                             conf=0.50 
                         )
                         
                # Only update counts when results change (every 6th frame)
                new_people_count = 0
                new_weapon_detected = False
                for result in last_results:
                    for box in result.boxes:
                        cls = int(box.cls[0])
                        if cls in TARGET_CLASSES:
                            if cls == 0: new_people_count += 1
                            else: new_weapon_detected = True
                
                people_count = new_people_count
                weapon_detected = new_weapon_detected

            # Draw Boxes EVERY frame using persistent last_results
            for result in last_results:
                for box in result.boxes:
                    cls = int(box.cls[0])
                    if cls not in TARGET_CLASSES: continue
                    
                    conf = float(box.conf[0])
                    color = (0, 255, 0) if cls == 0 else (0, 0, 255)
                    label = "Person" if cls == 0 else result.names[cls].upper()

                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Draw Overlays
            cv2.putText(frame, f"People: {people_count}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            if weapon_detected:
                cv2.putText(frame, "!!! THREAT DETECTED !!!", (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # --- Persistent Logging Logic ---
            now = time.time()
            with stats_lock:
                current_counts[camera_id] = people_count
                current_weapons[camera_id] = weapon_detected
                
                if camera_id not in last_log_times:
                    last_log_times[camera_id] = {"person": 0, "weapon": 0}
                
                # Person Logging
                p_streak = people_streak.get(camera_id, 0)
                if people_count > 0: p_streak += 1
                else: p_streak = 0
                people_streak[camera_id] = p_streak
                
                if p_streak == 5 and (now - last_log_times[camera_id]["person"] > 30):
                    # Background logging
                    threading.Thread(
                        target=send_log, 
                        args=(f"({people_count}) Person detected on Camera {camera_id}", "detection"),
                        daemon=True
                    ).start()
                    last_log_times[camera_id]["person"] = now
                
                # Weapon Logging
                w_streak = weapon_streak.get(camera_id, 0)
                if weapon_detected: w_streak += 1
                else: w_streak = 0
                weapon_streak[camera_id] = w_streak
                
                if w_streak == 3 and (now - last_log_times[camera_id]["weapon"] > 60):
                    # Use a background thread for logging to prevent network lag from tanking FPS
                    threading.Thread(
                        target=send_log, 
                        args=(f"WEAPON DETECTED on Camera {camera_id}", "warning"),
                        daemon=True
                    ).start()
                    last_log_times[camera_id]["weapon"] = now

            # Store Annotated Frame Immediately (Update Stream)
            with frames_lock:
                annotated_frames[camera_id] = frame
            
            frame_events[camera_id].set()
            frame_events[camera_id].clear()

            # No sleep needed here, we want to match the camera's natural FPS
            
        except Exception as e:
            logger.error(f"Analysis error cam {camera_id}: {e}")
            time.sleep(1)

    cap.release()

def generate_annotated_mjpeg(camera_id: int):
    """Serve Annotated MJPEG Stream"""
    while True:
        try:
            event = frame_events.get(camera_id)
            if event: event.wait(timeout=1.0)
            
            with frames_lock:
                frame = annotated_frames.get(camera_id)
            
            if frame is None:
                time.sleep(0.1)
                continue
            
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        except GeneratorExit: break
        except Exception: time.sleep(0.1)

app = FastAPI(title="Analysis Service (YOLO Nano)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def discovery_loop():
    """Periodically check for new cameras"""
    logger.info("Starting camera discovery loop...")
    while True:
        try:
            available = get_cameras_from_service()
            for cam in available:
                cid = cam["id"]
                if cid not in stop_events:
                    logger.info(f"New camera discovered: {cid}")
                    stop_events[cid] = threading.Event()
                    with stats_lock:
                        current_counts[cid] = 0
                        current_weapons[cid] = False
                    threading.Thread(target=process_stream, args=(cid,), daemon=True).start()
                    
                    # Tell DVR to start recording
                    try:
                        requests.post(f"{LOG_SERVICE_URL}/recording/start/{cid}", timeout=1)
                    except: pass
        except Exception as e:
            logger.error(f"Discovery error: {e}")
        
        time.sleep(10)

@app.on_event("startup")
async def startup_event():
    global current_model
    try:
        model_path = "yolo_models/yolov8n.pt" 
        current_model = YOLO(model_path)
        logger.info(f"YOLO Nano loaded: {model_path}")
    except Exception as e:
        logger.error(f"Failed to load YOLO model: {e}")
    
    logger.info("Analysis Service starting...")
    send_log("Analysis Service started and connected to DVR", "info")
    
    # Start persistent discovery
    threading.Thread(target=discovery_loop, daemon=True).start()

@app.get("/status")
async def get_status():
    """Return status of processing for each camera"""
    active_cameras = [cid for cid, event in stop_events.items() if not event.is_set()]
    return {
        "analyzing": active_cameras,
        "detection_enabled": detection_enabled,
        "model": os.path.basename(current_model.ckpt_path) if current_model else "none"
    }

@app.get("/annotated/{camera_id}")
async def annotated_feed(camera_id: int):
    return StreamingResponse(generate_annotated_mjpeg(camera_id), 
                             media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/models")
async def list_models():
    """List available YOLO models in the models folder"""
    models_dir = Path("yolo_models")
    if not models_dir.exists():
        return {"models": ["yolov8n.pt"], "current_model": "yolov8n.pt", "detection_enabled": detection_enabled}
    
    files = [f.name for f in models_dir.glob("*.pt")]
    return {
        "models": [{"name": f, "size_mb": round(os.path.getsize(models_dir / f) / (1024*1024), 1)} for f in files], 
        "current_model": os.path.basename(current_model.ckpt_path) if current_model else "yolov8n.pt",
        "detection_enabled": detection_enabled
    }

@app.post("/detection/toggle")
async def toggle_detection(enabled: bool):
    global detection_enabled
    detection_enabled = enabled
    return {"status": "success", "enabled": detection_enabled}

@app.post("/model/select")
async def select_model(model_name: str):
    global current_model
    model_path = Path("yolo_models") / model_name
    if not model_path.exists():
        raise HTTPException(status_code=404, detail="Model file not found")
    
    with model_lock:
        try:
            current_model = YOLO(str(model_path))
            return {"status": "success", "model": model_name}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_overall_stats():
    """Calculate overall system stats across all active streams"""
    with stats_lock:
        total_people = sum(current_counts.values())
        any_weapon = any(current_weapons.values())
        
        # Threat level logic
        threat_level = 0
        if total_people > 0:
            threat_level += min(total_people, 3)
        if any_weapon:
            threat_level += 5
            
        return {
            "people_count": total_people,
            "weapon_detected": any_weapon,
            "threat_level": min(threat_level, 10)
        }
