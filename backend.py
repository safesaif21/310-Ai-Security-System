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

logging.basicConfig(level=logging.INFO)

# Global state
CONNECTED_CLIENTS = set()
ACTIVE_CAMERAS = {}  # {camera_id: task}
model = YOLO("yolov8n.pt")
num_of_cameras = 3
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


def draw_detections(frame, detections):
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
    return frame


async def camera_loop(camera_id):
    """Continuously capture and process frames for one camera"""
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        logging.error(f"Could not open camera {camera_id}")
        return

    logging.info(f"Camera {camera_id} started successfully")

    try:
        while camera_id in ACTIVE_CAMERAS:
            ret, frame = cap.read()
            if not ret:
                logging.warning(f"Camera {camera_id} failed to read frame")
                await asyncio.sleep(0.1)
                continue

            detections = detect_objects(frame, camera_id)
            frame_with_detections = draw_detections(frame.copy(), detections)
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


async def handle_client(websocket):
    CONNECTED_CLIENTS.add(websocket)
    logging.info(f"Client connected. Total: {len(CONNECTED_CLIENTS)}")

    try:
        async for message in websocket:
            data = json.loads(message)

            if data.get('command') == 'innit':
                await websocket.send(json.dumps({
                    'type': 'innit',
                    'cameras': num_of_cameras,
                    'camera_ids': list(range(num_of_cameras))
                }))
                logging.info(f"Client init: {list(range(num_of_cameras))}")

            elif data.get('command') == 'start_all':
                for cam_id in range(num_of_cameras):
                    if cam_id not in ACTIVE_CAMERAS:
                        ACTIVE_CAMERAS[cam_id] = asyncio.create_task(camera_loop(cam_id))
                await websocket.send(json.dumps({
                    'type': 'status',
                    'message': f"Started {num_of_cameras} cameras"
                }))

            elif data.get('command') == 'stop_all':
                for cam_id, task in ACTIVE_CAMERAS.items():
                    task.cancel()
                ACTIVE_CAMERAS.clear()
                await websocket.send(json.dumps({
                    'type': 'status',
                    'message': 'All cameras stopped'
                }))
                logging.info("Stopped all cameras")

            elif data.get('command') == 'start_camera':
                cam_id = data.get('camera_id', 0)
                if cam_id not in ACTIVE_CAMERAS:
                    ACTIVE_CAMERAS[cam_id] = asyncio.create_task(camera_loop(cam_id))
                    await websocket.send(json.dumps({
                        'type': 'status',
                        'message': f"Camera {cam_id} started"
                    }))

            elif data.get('command') == 'stop_camera':
                cam_id = data.get('camera_id', 0)
                if cam_id in ACTIVE_CAMERAS:
                    ACTIVE_CAMERAS[cam_id].cancel()
                    del ACTIVE_CAMERAS[cam_id]
                    await websocket.send(json.dumps({
                        'type': 'status',
                        'message': f"Camera {cam_id} stopped"
                    }))

    except websockets.exceptions.ConnectionClosed:
        logging.info("Client disconnected")
    finally:
        CONNECTED_CLIENTS.discard(websocket)
        if not CONNECTED_CLIENTS:
            for cam_id, task in ACTIVE_CAMERAS.items():
                task.cancel()
            ACTIVE_CAMERAS.clear()
            logging.info("No clients connected, stopping all cameras")


async def main():
    async with websockets.serve(handle_client, "localhost", 8765):
        logging.info("Server running at ws://localhost:8765")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server shutting down...")
