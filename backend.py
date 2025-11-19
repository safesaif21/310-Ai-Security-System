"""
FastAPI Backend for USB Camera Streaming with YOLO Detection
Run with: uvicorn backend:app --reload
"""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import threading
import time
from pathlib import Path
from ultralytics import YOLO
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store camera objects
cameras = {}
camera_locks = {}

# Stat variables - track per camera
camera_people_counts = {}  # {camera_id: count}
camera_weapon_detected = {}  # {camera_id: bool}
stats_lock = threading.Lock()

# YOLO model management
current_model = None
model_lock = threading.Lock()
detection_enabled = False
MODELS_FOLDER = "yolo_models"  # Folder containing YOLO models

def get_camera(camera_id: int):
    """Get or create camera capture object"""
    if camera_id not in cameras:
        # Use DirectShow backend for Windows (faster)
        cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 15)  # Limit FPS
        cameras[camera_id] = cap
        camera_locks[camera_id] = threading.Lock()
        # Initialize stats for this camera
        camera_people_counts[camera_id] = 0
        camera_weapon_detected[camera_id] = False
    return cameras[camera_id], camera_locks[camera_id]

def calculate_threat_level():
    """Calculate threat level based on detections across all cameras"""
    # Sum people across all cameras
    total_people = sum(camera_people_counts.values())
    # Check if any camera detected a weapon
    any_weapon = any(camera_weapon_detected.values())
    
    level = 0
    
    # Base threat from people count
    if total_people > 0:
        people_threat = min(total_people, 3)  # Max 3 points for people
        level += people_threat
    
    # Weapon detection - major threat
    if any_weapon:
        level += 5
    
    # Multiple people + weapon = critical
    if total_people > 1 and any_weapon:
        level += 2
    
    return min(level, 10)  # Cap at 10


def generate_mjpeg_stream(camera_id: int):
    """Generate MJPEG stream for a camera"""
    
    cap, lock = get_camera(camera_id)
    
    while True:
        with lock:
            success, frame = cap.read()
        
        if not success:
            print(f"Failed to read from camera {camera_id}")
            time.sleep(0.1)
            continue
        
        # Reset detection counters for this frame
        frame_people_count = 0
        frame_weapon_detected = False
        
        # Apply YOLO detection if enabled
        if detection_enabled and current_model is not None:
            with model_lock:
                try:
                    # Run inference
                    results = current_model(frame, verbose=False)
                    
                    if current_model.model_name == 'pre-trained-sus-saif-only.pt':
                        # Draw custom detections
                        for result in results:
                            boxes = result.boxes
                            for box in boxes:
                                class_id = int(box.cls[0])
                                confidence = float(box.conf[0])
                                x1, y1, x2, y2 = map(int, box.xyxy[0])
                                
                                # Sus Person detection (class 0)
                                if class_id == 0:
                                    frame_weapon_detected = True
                                    frame_people_count += 1
                                    
                                    # Draw bounding box
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                                    
                                    # Draw label
                                    label = f"Sus Person {confidence:.2f}"
                                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                                    cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                                (x1 + label_size[0], y1), (0, 0, 255), -1)
                                    cv2.putText(frame, label, (x1, y1 - 5), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                                
                                # Person detection (class 1)
                                elif class_id == 1:
                                    
                                    frame_people_count += 1
                                    # Draw bounding box
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                    
                                    # Draw label
                                    label = f"Person {confidence:.2f}"
                                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                                    cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                                (x1 + label_size[0], y1), (0, 255, 0), -1)
                                    cv2.putText(frame, label, (x1, y1 - 5), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    else:
                        # Draw detections
                        for result in results:
                            boxes = result.boxes
                            for box in boxes:
                                class_id = int(box.cls[0])
                                confidence = float(box.conf[0])
                                x1, y1, x2, y2 = map(int, box.xyxy[0])
                                
                                # Person detection (class 0)
                                if class_id == 0:
                                    frame_people_count += 1
                                    
                                    # Draw bounding box
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                    
                                    # Draw label
                                    label = f"Person {confidence:.2f}"
                                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                                    cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                                (x1 + label_size[0], y1), (0, 255, 0), -1)
                                    cv2.putText(frame, label, (x1, y1 - 5), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                                
                                # Knife detection (class 43)
                                elif class_id == 43:
                                    frame_weapon_detected = True
                                    
                                    # Draw bounding box
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                                    
                                    # Draw label
                                    label = f"Knife {confidence:.2f}"
                                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                                    cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                                (x1 + label_size[0], y1), (0, 0, 255), -1)
                                    cv2.putText(frame, label, (x1, y1 - 5), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                                
                                # Scissors detection (class 76)
                                elif class_id == 76:
                                    frame_weapon_detected = True
                                    
                                    # Draw bounding box
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                                    
                                    # Draw label
                                    label = f"Scissors {confidence:.2f}"
                                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                                    cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                                (x1 + label_size[0], y1), (0, 0, 255), -1)
                                    cv2.putText(frame, label, (x1, y1 - 5), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    
                    # Update this camera's stats with thread safety
                    with stats_lock:
                        camera_people_counts[camera_id] = frame_people_count
                        camera_weapon_detected[camera_id] = frame_weapon_detected
                        
                except Exception as e:
                    print(f"Detection error: {e}")
        else:
            # If detection is disabled, reset this camera's stats
            with stats_lock:
                camera_people_counts[camera_id] = 0
                camera_weapon_detected[camera_id] = False
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        
        if not ret:
            continue
        
        # Yield frame in MJPEG format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        time.sleep(0.033)  # ~30 FPS

@app.get("/")
async def root():
    """API info endpoint"""
    return {
        "message": "Camera Server Running",
        "endpoints": {
            "camera_stream": "/camera/{camera_id}",
            "camera_list": "/cameras",
            "camera_info": "/camera/{camera_id}/info",
            "stats": "/stats",
            "models": "/models"
        }
    }

@app.get("/camera/{camera_id}")
async def video_feed(camera_id: int):
    """Stream video from specified camera as MJPEG"""
    return StreamingResponse(
        generate_mjpeg_stream(camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/cameras")
async def list_cameras():
    """List available cameras - fast version"""
    available = []
    
    # Check cameras 0-2 with longer timeout for slow cameras
    for i in range(3):
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            # Increase timeout for slow cameras (like your 3rd one)
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
            
            # Try to grab a frame to verify it really works
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available.append({
                        "id": i,
                        "name": f"Camera {i}",
                        "url": f"http://localhost:8000/camera/{i}"
                    })
            cap.release()
        except Exception as e:
            print(f"Error checking camera {i}: {e}")
            continue
    
    return {"cameras": available}

@app.get("/camera/{camera_id}/info")
async def camera_info(camera_id: int):
    """Get camera information"""
    cap, lock = get_camera(camera_id)
    
    with lock:
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    return {
        "id": camera_id,
        "resolution": f"{width}x{height}",
        "fps": fps,
        "is_opened": cap.isOpened()
    }

@app.get("/models")
async def list_models():
    """List available YOLO models"""
    models_dir = Path(MODELS_FOLDER)
    
    if not models_dir.exists():
        return {"models": [], "message": "Models folder not found"}
    
    # Find all .pt files
    model_files = list(models_dir.glob("*.pt"))
    
    models = []
    for model_file in model_files:
        models.append({
            "name": model_file.name,
            "path": str(model_file),
            "size_mb": round(model_file.stat().st_size / (1024 * 1024), 2)
        })
    
    return {
        "models": models,
        "current_model": current_model.model_name if current_model else None,
        "detection_enabled": detection_enabled
    }

@app.post("/model/load")
async def load_model(model_name: str):
    """Load a YOLO model"""
    global current_model, detection_enabled
    
    model_path = Path(MODELS_FOLDER) / model_name
    
    if not model_path.exists():
        return {"success": False, "message": f"Model {model_name} not found"}
    
    try:
        with model_lock:
            print(f"Loading model: {model_name}")
            current_model = YOLO(str(model_path))
            current_model.model_name = model_name
            detection_enabled = True
            print(f"Model {model_name} loaded successfully")
        
        return {
            "success": True, 
            "message": f"Model {model_name} loaded successfully",
            "model_name": model_name
        }
    except Exception as e:
        return {"success": False, "message": f"Error loading model: {str(e)}"}

@app.post("/detection/toggle")
async def toggle_detection(enabled: bool):
    """Enable or disable detection"""
    global detection_enabled
    
    if enabled and current_model is None:
        return {
            "success": False, 
            "message": "No model loaded. Load a model first."
        }
    
    detection_enabled = enabled
    status = "enabled" if enabled else "disabled"
    
    # Reset all stats when toggling
    if not enabled:
        with stats_lock:
            for camera_id in camera_people_counts:
                camera_people_counts[camera_id] = 0
                camera_weapon_detected[camera_id] = False
    
    return {
        "success": True,
        "message": f"Detection {status}",
        "detection_enabled": detection_enabled
    }

@app.get("/stats")
async def get_stats():
    """Get current detection statistics"""
    
    with stats_lock:
        total_people = sum(camera_people_counts.values())
        any_weapon = any(camera_weapon_detected.values())
        threat_level = calculate_threat_level()
        
        return {
            "people_count": total_people,
            "weapon_detected": any_weapon,
            "threat_level": threat_level
        }

@app.on_event("shutdown")
async def shutdown_event():
    """Release all cameras on shutdown"""
    for cap in cameras.values():
        cap.release()
    print("All cameras released")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)