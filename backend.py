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

logging.basicConfig(level=logging.INFO)

# Global state
CONNECTED_CLIENTS = set()
ACTIVE_CAMERAS = {}  # {camera_id: task}
model = YOLO("yolo_models/yolov8n.pt")
current_model_path = "yolo_models/yolov8n.pt"

if(len(sys.argv) > 1):
    num_of_cameras = int(sys.argv[1])
else:
    num_of_cameras = 1

print(f"Number of cameras set to: {num_of_cameras}")
# Detection memory per camera
DETECTION_STATE = {}

THREAT_DECAY_SECONDS = 5  # how long to keep high threat after last detection

if (model):
    logging.info("YOLO model loaded successfully")
else:
    logging.error("Failed to load YOLO model")

def encode_frame(frame):
    """Encode frame to base64 for transmission"""
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return base64.b64encode(buffer).decode('utf-8')


def detect_objects(frame, camera_id):
    """Run YOLO detection on frame"""
    state = DETECTION_STATE.setdefault(camera_id, {
        'last_weapon_time': None,
        'weapon_alert_active': False
    })
    results = model(frame, verbose=False)

    detections = {
        'people': [],
        'weapons': [],
        'objects': [],
        'people_count': 0,
        'threat_level': 0,
        'alert': None
    }

    weapon_classes = {43: 'Knife', 34: 'Baseball Bat', 76: 'Scissors'}
    weapon_found = False

    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().tolist()
            label = model.names[cls]

            if cls == 0:
                detections['people'].append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': conf
                })
                detections['people_count'] += 1

            elif cls in weapon_classes:
                weapon_found = True
                detections['weapons'].append({
                    'name': weapon_classes[cls],
                    'confidence': conf,
                    'bbox': [x1, y1, x2, y2]
                })

            else:
                detections['objects'].append({
                    'name': label,
                    'confidence': conf,
                    'bbox': [x1, y1, x2, y2]
                })

    now = time.time()

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

    # Threat level logic
    if state['weapon_alert_active']:
        detections['threat_level'] = 10
    else:
        detections['threat_level'] = min(
            10,
            detections['people_count'] + (len(detections['weapons']) * 3)
        )

    return detections


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
    """Continuously capture and process frames for one camera"""
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        logging.error(f"Could not open camera {camera_id}")
        return

    # Re-read values to verify
    actual_brightness = cap.get(cv2.CAP_PROP_BRIGHTNESS)
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Brightness set to {actual_brightness}, FPS set to {actual_fps}")

    logging.info(f"Camera {camera_id} started successfully")

    try:
        while camera_id in ACTIVE_CAMERAS:
            ret, frame = cap.read()
            if not ret:
                logging.warning(f"Camera {camera_id} failed to read frame")
                await asyncio.sleep(0.1)
                continue
            
            if camera_id == 0: # hardcoded enhancements for camera 0
                 # --- Convert to float for precision ---
                frame_float = frame.astype(np.float32) / 255.0

                # --- Gamma correction ---
                gamma = 125 / 100  # scale OBS 0-255 to ~0-3, 150 → 1.5
                frame_float = np.power(frame_float, 1.0 / gamma)

                # --- Convert to HSV for hue & saturation ---
                hsv = cv2.cvtColor((frame_float * 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)

                # Hue (OBS 0 → 0 shift)
                hue_shift = 0
                hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180

                # Saturation (OBS 255 → full)
                sat_scale = 200 / 128  # scale OBS 0–255 (128 = no change)
                hsv[:, :, 1] = np.clip(hsv[:, :, 1] * sat_scale, 0, 255)

                # Convert back to BGR
                frame = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

                # --- Brightness and Contrast ---
                # OBS 0–255 → OpenCV alpha/beta mapping
                alpha = 150 / 128   # contrast
                beta = 200 - 128    # brightness offset
                frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

                # --- Sharpness (Unsharp Mask) ---
                sharpness = 25 / 100  # scale 0–1
                blurred = cv2.GaussianBlur(frame, (0, 0), 3)
                frame = cv2.addWeighted(frame, 1 + sharpness, blurred, -sharpness, 0)
    
            detections = detect_objects(frame, camera_id)
            frame_with_detections = draw_detections(frame.copy(), detections, camera_id)
            encoded_frame = encode_frame(frame_with_detections)

            message = json.dumps({
                'type': 'frame',
                'camera_id': camera_id,
                'frame': encoded_frame,
                'detections': detections,
                'timestamp': datetime.now().isoformat()
            })

            disconnected = set()
            for client in CONNECTED_CLIENTS:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            for d in disconnected:
                CONNECTED_CLIENTS.discard(d)

            await asyncio.sleep(0.016)  # ~60 FPS

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
        logging.info(f"Found {len(available_models)} YOLO model(s) available for selection")
        for m in available_models:
            logging.info(f"  - {m['name']}: {m['path']}")
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
