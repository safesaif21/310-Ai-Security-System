import asyncio
import websockets
import logging
import cv2
import numpy as np
import base64
import json
from ultralytics import YOLO
from datetime import datetime
import time
import sys
import os
from pathlib import Path
import torch

logging.basicConfig(level=logging.INFO)

# Global state
CONNECTED_CLIENTS = set()
ACTIVE_CAMERAS = {}  # {camera_id: task}
device = "cuda" if torch.cuda.is_available() else "cpu"
# Use yolov8l.pt (large) for best accuracy - significantly better weapon detection
# Model sizes: nano (37% mAP) < small (45% mAP) < medium (50% mAP) < large (53% mAP) < xlarge (54% mAP)
model = YOLO("yolo_models/yolov8l.pt").to(device)
print(f"Using device: {device}")
print(f"Loaded model: yolov8l.pt (Large - Best accuracy for weapon detection, 53% mAP)")
current_model_path = "yolo_models/yolov8l.pt"

if(len(sys.argv) > 1):
    num_of_cameras = int(sys.argv[1])
else:
    num_of_cameras = 1

print(f"Number of cameras set to: {num_of_cameras}")
# Detection memory per camera
DETECTION_STATE = {}

THREAT_DECAY_SECONDS = 5  # how long to keep high threat after last detection

# Temporal smoothing for weapon detection (reduces false negatives)
WEAPON_DETECTION_HISTORY = {}  # Track recent weapon detections per camera
TEMPORAL_SMOOTHING_FRAMES = 3  # Require detection in N of last M frames

def encode_frame(frame):
    """Encode frame to base64 for transmission - optimized for speed"""
    # Reduce quality slightly for faster encoding/transmission (70 is good balance)
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
    return base64.b64encode(buffer).decode('utf-8')


def preprocess_frame_for_detection(frame):
    """Preprocess frame to improve weapon detection accuracy - optimized version"""
    # Lightweight preprocessing - skip heavy operations for speed
    # Only apply CLAHE if really needed (can be disabled for speed)
    USE_PREPROCESSING = False  # Set to True if detection accuracy drops
    
    if not USE_PREPROCESSING:
        return frame  # Skip preprocessing for speed
    
    # Only apply lightweight contrast adjustment if enabled
    # Convert to LAB color space for better contrast control
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
    # Use smaller tile size for faster processing
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))  # Smaller tiles = faster
    l = clahe.apply(l)
    
    # Merge channels and convert back
    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    return enhanced  # Skip sharpening for speed


def detect_objects(frame, camera_id):
    """Run YOLO detection on frame with improved accuracy for weapons"""
    state = DETECTION_STATE.setdefault(camera_id, {
        'last_weapon_time': None,
        'weapon_alert_active': False
    })
    
    # Preprocess frame for better detection
    processed_frame = preprocess_frame_for_detection(frame)
    
    # Run YOLO with optimized settings for speed and accuracy
    # Reduce image size for faster inference (YOLO will resize anyway)
    # Use lower conf for weapons (0.25) vs people (0.5)
    # imgsz=416 instead of 640 for ~2x speedup with minimal accuracy loss
    results = model(processed_frame, verbose=False, conf=0.25, iou=0.45, imgsz=416)

    detections = {
        'people': [],
        'weapons': [],
        'objects': [],
        'people_count': 0,
        'threat_level': 0,
        'alert': None
    }

    # Weapon classes with threat severity weights and minimum confidence thresholds
    # Expanded to include more weapon-related objects from COCO
    weapon_classes = {
        43: {'name': 'Knife', 'severity': 8.5, 'min_conf': 0.20},      # Most dangerous, very low threshold
        34: {'name': 'Baseball Bat', 'severity': 7.0, 'min_conf': 0.20}, # Dangerous, very low threshold
        76: {'name': 'Scissors', 'severity': 6.0, 'min_conf': 0.25},   # Moderately dangerous
        # Additional potentially dangerous objects
        39: {'name': 'Bottle', 'severity': 4.0, 'min_conf': 0.40},     # Can be used as weapon (context-dependent)
        40: {'name': 'Wine Glass', 'severity': 3.5, 'min_conf': 0.40}, # Can be used as weapon (context-dependent)
    }
    
    # Minimum confidence thresholds
    PEOPLE_CONF_THRESHOLD = 0.5  # Higher confidence for people (more reliable)
    WEAPON_CONF_THRESHOLD = 0.20  # Very low confidence for weapons (better recall)
    OBJECT_CONF_THRESHOLD = 0.5   # Standard confidence for other objects
    
    # Initialize temporal smoothing history for this camera
    if camera_id not in WEAPON_DETECTION_HISTORY:
        WEAPON_DETECTION_HISTORY[camera_id] = []
    
    weapon_candidates = []  # Store potential weapon detections before temporal smoothing

    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().tolist()
            label = model.names[cls]

            if cls == 0:  # Person
                # Apply confidence threshold for people
                if conf >= PEOPLE_CONF_THRESHOLD:
                    detections['people'].append({
                        'bbox': [x1, y1, x2, y2],
                        'confidence': conf
                    })
                    detections['people_count'] += 1

            elif cls in weapon_classes:
                weapon_info = weapon_classes[cls]
                weapon_min_conf = weapon_info.get('min_conf', WEAPON_CONF_THRESHOLD)
                
                # Apply weapon-specific confidence threshold (lower for better detection)
                if conf >= weapon_min_conf:
                    weapon_candidates.append({
                        'name': weapon_info['name'],
                        'confidence': conf,
                        'bbox': [x1, y1, x2, y2],
                        'severity': weapon_info['severity'],
                        'class': cls
                    })

            else:
                # Other objects with standard threshold
                if conf >= OBJECT_CONF_THRESHOLD:
                    detections['objects'].append({
                        'name': label,
                        'confidence': conf,
                        'bbox': [x1, y1, x2, y2]
                    })

    # Temporal smoothing: improve detection accuracy by requiring consistency
    now = time.time()
    WEAPON_DETECTION_HISTORY[camera_id].append({
        'time': now,
        'weapons': weapon_candidates
    })
    
    # Keep only recent history (last N frames)
    max_history_time = TEMPORAL_SMOOTHING_FRAMES * 0.1  # Assuming ~10 fps
    WEAPON_DETECTION_HISTORY[camera_id] = [
        h for h in WEAPON_DETECTION_HISTORY[camera_id] 
        if now - h['time'] < max_history_time
    ]
    
    # Count how many recent frames had weapon detections
    recent_weapon_frames = [h for h in WEAPON_DETECTION_HISTORY[camera_id] if h['weapons']]
    
    # Smart confirmation: allow high-confidence single-frame detections,
    # but require multiple frames for low-confidence detections
    weapon_found = False
    confirmed_weapons = []
    
    if weapon_candidates:
        for weapon in weapon_candidates:
            weapon_conf = weapon['confidence']
            
            # High confidence (>=0.5): accept immediately
            if weapon_conf >= 0.5:
                confirmed_weapons.append(weapon)
            # Medium confidence (0.3-0.5): require detection in 2+ recent frames
            elif weapon_conf >= 0.3 and len(recent_weapon_frames) >= 2:
                confirmed_weapons.append(weapon)
            # Low confidence (<0.3): require detection in 3+ recent frames
            elif weapon_conf < 0.3 and len(recent_weapon_frames) >= 3:
                confirmed_weapons.append(weapon)
    
    # If we have confirmed weapons from history but not current frame, use recent history
    if not confirmed_weapons and recent_weapon_frames:
        # Use weapons from most recent frame with detections
        confirmed_weapons = recent_weapon_frames[-1]['weapons']
    
    weapon_found = len(confirmed_weapons) > 0
    
    # Add confirmed weapons to detections
    for weapon in confirmed_weapons:
        detections['weapons'].append(weapon)

    # Alert logic per camera
    if weapon_found:
        state['last_weapon_time'] = now
        if not state['weapon_alert_active']:
            detections['alert'] = "⚠️ Weapon detected!"
            state['weapon_alert_active'] = True
    else:
        if (
            state['weapon_alert_active']
            and state['last_weapon_time']
            and now - state['last_weapon_time'] > THREAT_DECAY_SECONDS
        ):
            state['weapon_alert_active'] = False

    # Calculate accurate threat level
    detections['threat_level'] = calculate_threat_level(
        detections['people'],
        detections['weapons'],
        state['weapon_alert_active']
    )

    return detections


def calculate_bbox_center(bbox):
    """Calculate center point of bounding box"""
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def calculate_distance(bbox1, bbox2):
    """Calculate distance between centers of two bounding boxes"""
    center1 = calculate_bbox_center(bbox1)
    center2 = calculate_bbox_center(bbox2)
    return np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)


def calculate_bbox_size(bbox):
    """Calculate size (area) of bounding box"""
    x1, y1, x2, y2 = bbox
    return (x2 - x1) * (y2 - y1)


def calculate_threat_level(people, weapons, weapon_alert_active):
    """
    Calculate accurate threat level (0-10) based on multiple factors:
    - Weapon type and confidence
    - Number of weapons
    - Proximity of weapons to people
    - Number of people
    - Weapon detection confidence
    """
    threat = 0.0
    
    # Base threat from people count (minimal)
    people_count = len(people)
    people_threat = min(2.0, people_count * 0.3)  # Max 2 points from people alone
    threat += people_threat
    
    # Weapon-based threat calculation
    if weapons:
        weapon_threat = 0.0
        
        for weapon in weapons:
            weapon_conf = weapon['confidence']
            weapon_severity = weapon.get('severity', 7.0)  # Default severity
            
            # Base weapon threat = severity * confidence
            # Higher confidence weapons contribute more
            base_weapon_threat = weapon_severity * weapon_conf
            
            # Check proximity to people (critical factor)
            min_distance_to_person = float('inf')
            weapon_center = calculate_bbox_center(weapon['bbox'])
            weapon_size = calculate_bbox_size(weapon['bbox'])
            normalized_distance = None
            
            for person in people:
                person_center = calculate_bbox_center(person['bbox'])
                person_size = calculate_bbox_size(person['bbox'])
                
                # Calculate normalized distance (relative to frame size)
                distance = calculate_distance(weapon['bbox'], person['bbox'])
                avg_size = np.sqrt((weapon_size + person_size) / 2)
                norm_dist = distance / (avg_size + 1e-6)  # Avoid division by zero
                
                if norm_dist < min_distance_to_person:
                    min_distance_to_person = norm_dist
                    normalized_distance = norm_dist
            
            # Proximity multiplier: closer weapons = higher threat
            if normalized_distance is not None and min_distance_to_person < float('inf'):
                if normalized_distance < 1.5:  # Very close to person
                    proximity_multiplier = 1.5  # 50% increase
                elif normalized_distance < 3.0:  # Close to person
                    proximity_multiplier = 1.3  # 30% increase
                elif normalized_distance < 5.0:  # Moderate distance
                    proximity_multiplier = 1.1  # 10% increase
                else:  # Far from people
                    proximity_multiplier = 0.8  # 20% decrease
            else:
                proximity_multiplier = 0.7  # No people nearby, lower threat
            
            # Apply proximity multiplier
            weapon_threat += base_weapon_threat * proximity_multiplier
        
        # Multiple weapons increase threat exponentially
        if len(weapons) > 1:
            multi_weapon_multiplier = 1.0 + (len(weapons) - 1) * 0.3  # +30% per additional weapon
            weapon_threat *= multi_weapon_multiplier
        
        threat += weapon_threat
    
    # Weapon alert active adds urgency (decay over time)
    if weapon_alert_active:
        threat += 1.0  # Add urgency bonus
    
    # Combine with people presence near weapons
    if weapons and people:
        # If weapons and people are both present, multiply threat
        interaction_multiplier = 1.2  # 20% increase when both present
        threat *= interaction_multiplier
    
    # Cap threat at 10 and round to 1 decimal
    threat = min(10.0, threat)
    threat = round(threat, 1)
    
    return threat


def draw_detections(frame, detections, camera_id=None):
    """Draw bounding boxes on frame"""
    for person in detections['people']:
        x1, y1, x2, y2 = map(int, person['bbox'])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"Person {person['confidence']:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    for weapon in detections['weapons']:
        x1, y1, x2, y2 = map(int, weapon['bbox'])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
        label = f"{weapon['name']} {weapon['confidence']:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
    # Annotate camera ID on bottom-right
    if camera_id is not None:
        h, w = frame.shape[:2]
        text = f"Camera {camera_id}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 1
        thickness = 2
        color = (255, 255, 255)  # white
        text_size = cv2.getTextSize(text, font, scale, thickness)[0]
        position = (w - text_size[0] - 10, h - 10)
        cv2.putText(frame, text, position, font, scale, color, thickness)
    return frame


async def camera_loop(camera_id):
    """Continuously capture and process frames for one camera - optimized for smoothness"""
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        logging.error(f"Could not open camera {camera_id}")
        return

    # Optimize camera settings for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Reduce resolution for faster processing
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 640x480 is good balance
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)      # Minimal buffer to reduce latency
    
    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    logging.info(f"Camera {camera_id} started at {int(actual_width)}x{int(actual_height)}")

    # Frame skipping for smoother performance
    frame_skip_count = 0
    FRAME_SKIP = 1  # Process every 2nd frame (skip 1) for better FPS
    
    # Store last detections for skipped frames
    last_detections = None
    last_encoded_frame = None

    try:
        while camera_id in ACTIVE_CAMERAS:
            ret, frame = cap.read()
            if not ret:
                logging.warning(f"Camera {camera_id} failed to read frame")
                await asyncio.sleep(0.01)  # Shorter sleep for faster recovery
                continue
            
            frame_skip_count += 1
            
            # Skip frames for smoother playback - only process every Nth frame
            if frame_skip_count <= FRAME_SKIP:
                # Use last frame for display while processing happens
                if last_encoded_frame:
                    message = json.dumps({
                        'type': 'frame',
                        'camera_id': camera_id,
                        'frame': last_encoded_frame,
                        'detections': last_detections,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Send to all connected clients quickly
                    disconnected = set()
                    for client in CONNECTED_CLIENTS.copy():
                        try:
                            await client.send(message)
                        except websockets.exceptions.ConnectionClosed:
                            disconnected.add(client)
                    
                    for d in disconnected:
                        CONNECTED_CLIENTS.discard(d)
                
                await asyncio.sleep(0.01)  # Fast loop for display
                continue
            
            # Reset counter and process this frame
            frame_skip_count = 0
            
            # Keep original for display
            original_frame = frame.copy()
            
            # Run detection (this is the heavy operation)
            detections = detect_objects(frame, camera_id)
            
            # Draw on original resolution frame
            frame_with_detections = draw_detections(original_frame, detections, camera_id)
            encoded_frame = encode_frame(frame_with_detections)
            
            # Store for next iterations
            last_detections = detections
            last_encoded_frame = encoded_frame

            message = json.dumps({
                'type': 'frame',
                'camera_id': camera_id,
                'frame': encoded_frame,
                'detections': detections,
                'timestamp': datetime.now().isoformat()
            })

            # Send to all connected clients
            disconnected = set()
            for client in CONNECTED_CLIENTS.copy():
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            for d in disconnected:
                CONNECTED_CLIENTS.discard(d)

            # Adaptive sleep - allow other tasks to run
            await asyncio.sleep(0.001)  # Minimal sleep, frame skip handles rate limiting

    finally:
        cap.release()
        logging.info(f"Camera {camera_id} stopped")




def detect_cameras():
    """Detect available camera devices"""
    index = 0
    arr = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        arr.append(index)
        cap.release()
        index += 1
    return arr


def scan_yolo_models():
    """Scan for all .pt YOLO model files in the repository"""
    models = []
    base_path = Path(__file__).parent
    
    # Common locations to search for models
    search_paths = [
        base_path / "yolo_models",
        base_path,
        base_path / "models",
        base_path / "weights"
    ]
    
    # Also search for common YOLO model names
    common_models = [
        "yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt", "yolov8x.pt",
        "yolov5n.pt", "yolov5s.pt", "yolov5m.pt", "yolov5l.pt", "yolov5x.pt"
    ]
    
    found_paths = set()
    
    # Search in specific directories
    for search_path in search_paths:
        if search_path.exists():
            for pt_file in search_path.glob("*.pt"):
                # Use forward slashes for cross-platform compatibility
                rel_path = str(pt_file.relative_to(base_path)).replace('\\', '/')
                if rel_path not in found_paths:
                    models.append({
                        "name": pt_file.stem,
                        "path": rel_path,
                        "full_path": str(pt_file.absolute())
                    })
                    found_paths.add(rel_path)
    
    # Check for common model names in root
    for model_name in common_models:
        model_path = base_path / model_name
        if model_path.exists():
            rel_path = model_name
            if rel_path not in found_paths:
                models.append({
                    "name": model_path.stem,
                    "path": rel_path,
                    "full_path": str(model_path.absolute())
                })
                found_paths.add(rel_path)
    
    # Sort by name
    models.sort(key=lambda x: x["name"])
    
    logging.info(f"Found {len(models)} YOLO models: {[m['name'] for m in models]}")
    
    return models


def switch_model(model_path):
    """Switch to a different YOLO model"""
    global model, current_model_path
    try:
        # Ensure path is correct (handle relative paths)
        base_path = Path(__file__).parent
        full_path = (base_path / model_path).resolve()
        
        if not full_path.exists():
            logging.error(f"Model file not found: {full_path}")
            return False
        
        # Load the new model
        new_model = YOLO(str(full_path))
        model = new_model
        model.to("cuda")
        current_model_path = model_path
        logging.info(f"✅ Successfully switched to model: {model_path}")
        return True
    except Exception as e:
        logging.error(f"❌ Failed to load model {model_path}: {e}")
        import traceback
        traceback.print_exc()
        return False


async def handle_client(websocket):
    CONNECTED_CLIENTS.add(websocket)
    logging.info(f"Client connected. Total: {len(CONNECTED_CLIENTS)}")

    try:
        async for message in websocket:
            data = json.loads(message)

            if data.get('command') == 'innit':
                # Scan for available models
                available_models = scan_yolo_models()
                await websocket.send(json.dumps({
                    'type': 'innit',
                    'cameras': num_of_cameras,
                    'camera_ids': list(range(num_of_cameras)),
                    'available_models': available_models,
                    'current_model': current_model_path
                }))

            elif data.get('command') == 'start_cameras':
                camera_details = []
                available_cameras = range(num_of_cameras) # generate camera IDs based on num_of_cameras

                # Start each detected camera if not already active
                for cam_id in available_cameras:
                    if cam_id not in ACTIVE_CAMERAS:
                        ACTIVE_CAMERAS[cam_id] = asyncio.create_task(camera_loop(cam_id))
                        camera_details.append({
                            "camera_id": cam_id,
                            "status": "active",
                            "name": f"Camera {cam_id}",
                            "started_at": datetime.now().isoformat()
                        })
                    else:
                        camera_details.append({
                            "camera_id": cam_id,
                            "status": "already_active",
                            "name": f"Camera {cam_id}"
                        })

                await websocket.send(json.dumps({
                    "type": "camera_activation",
                    "cameras": camera_details,
                    "message": f"Activated {len(camera_details)} cameras"
                }))

            elif data.get('command') == 'stop_cameras':
                for cam_id, task in ACTIVE_CAMERAS.items():
                    task.cancel()
                ACTIVE_CAMERAS.clear()
                await websocket.send(json.dumps({
                    'type': 'status',
                    'message': 'All cameras stopped'
                }))
            
            elif data.get('command') == 'switch_model':
                model_path = data.get('model_path')
                if model_path:
                    success = switch_model(model_path)
                    if success:
                        await websocket.send(json.dumps({
                            'type': 'model_switched',
                            'model_path': model_path,
                            'message': f'Successfully switched to {model_path}'
                        }))
                    else:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': f'Failed to switch to model: {model_path}'
                        }))
                else:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'No model_path provided'
                    }))

    except websockets.exceptions.ConnectionClosed:
        logging.info("Client disconnected")
    finally:
        CONNECTED_CLIENTS.discard(websocket)
        if not CONNECTED_CLIENTS:
            for cam_id, task in ACTIVE_CAMERAS.items():
                task.cancel()
            ACTIVE_CAMERAS.clear()


async def main():
    # Scan for available models on startup
    available_models = scan_yolo_models()
    if available_models:
        for m in available_models:
            logging.info(f"- {m['name']}: {m['path']}")
    else:
        logging.warning("No YOLO models found in repository")
    
    async with websockets.serve(handle_client, "localhost", 8765):
        logging.info("Server running at ws://localhost:8765")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server shutting down...")
