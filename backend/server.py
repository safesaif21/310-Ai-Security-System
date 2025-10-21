import asyncio
import websockets
import logging
import cv2
import numpy as np
import base64
import json
from ultralytics import YOLO
from datetime import datetime

logging.basicConfig(level=logging.INFO)

# Global state
CONNECTED_CLIENTS = set()
camera_active = False
cap = None
model = None

def initialize_model():
    """Load YOLO model at startup"""
    global model
    logging.info("Loading YOLO model...")
    model = YOLO('yolov8n.pt')  # Use nano for speed
    logging.info("YOLO model loaded successfully")

def encode_frame(frame):
    """Encode frame to base64 for transmission"""
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return jpg_as_text

def detect_objects(frame):
    """Run YOLO detection on frame"""
    results = model(frame, verbose=False)
    
    detections = {
        'people': [],
        'weapons': [],
        'people_count': 0,
        'threat_level': 0
    }
    
    weapon_classes = {43: 'Knife', 34: 'Baseball Bat', 76: 'Scissors'}
    
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().tolist()
            
            # Detect people
            if cls == 0:
                detections['people'].append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': conf
                })
                detections['people_count'] += 1
            
            # Detect weapons
            elif cls in weapon_classes:
                detections['weapons'].append({
                    'name': weapon_classes[cls],
                    'confidence': conf,
                    'bbox': [x1, y1, x2, y2]
                })
    
    # Calculate threat level
    threat_level = min(10, detections['people_count'] + (len(detections['weapons']) * 3))
    detections['threat_level'] = threat_level
    
    return detections

def draw_detections(frame, detections):
    """Draw bounding boxes on frame"""
    # Draw people
    for person in detections['people']:
        x1, y1, x2, y2 = [int(coord) for coord in person['bbox']]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"Person {person['confidence']:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Draw weapons
    for weapon in detections['weapons']:
        x1, y1, x2, y2 = [int(coord) for coord in weapon['bbox']]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
        label = f"{weapon['name']} {weapon['confidence']:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    return frame

async def camera_loop():
    """Continuously capture and process frames"""
    global camera_active, cap
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        logging.error("Could not open camera")
        camera_active = False
        return
    
    logging.info("Camera started successfully")
    
    try:
        while camera_active:
            ret, frame = cap.read()
            if not ret:
                logging.warning("Failed to read frame")
                await asyncio.sleep(0.1)
                continue
            
            # Run YOLO detection
            detections = detect_objects(frame)
            
            # Draw detections on frame
            frame_with_detections = draw_detections(frame.copy(), detections)
            
            # Convert BGR to RGB
            # frame_rgb = cv2.cvtColor(frame_with_detections, cv2.COLOR_BGR2RGB)
            
            # Encode frame
            encoded_frame = encode_frame(frame_with_detections)
            
            # Prepare message
            message = json.dumps({
                'type': 'frame',
                'frame': encoded_frame,
                'detections': detections,
                'timestamp': datetime.now().isoformat()
            })
            
            # Broadcast to all clients
            if CONNECTED_CLIENTS:
                disconnected = set()
                for client in CONNECTED_CLIENTS:
                    try:
                        await client.send(message)
                    except websockets.exceptions.ConnectionClosed:
                        disconnected.add(client)
                
                # Clean up disconnected clients
                for client in disconnected:
                    CONNECTED_CLIENTS.discard(client)
            
            await asyncio.sleep(0.016)  # ~60 FPS
            
    finally:
        if cap:
            cap.release()
        logging.info("Camera stopped")

async def handle_client(websocket):
    """Handle individual client connections"""
    global camera_active
    
    CONNECTED_CLIENTS.add(websocket)
    logging.info(f"Client connected. Total clients: {len(CONNECTED_CLIENTS)}")
    
    try:
        async for message in websocket:
            data = json.loads(message)
            
            if data.get('command') == 'start_camera':
                if not camera_active:
                    camera_active = True
                    asyncio.create_task(camera_loop())
                    await websocket.send(json.dumps({
                        'type': 'status',
                        'message': 'Camera started'
                    }))
                    logging.info("Camera start command received")
            
            elif data.get('command') == 'stop_camera':
                camera_active = False
                await websocket.send(json.dumps({
                    'type': 'status',
                    'message': 'Camera stopped'
                }))
                logging.info("Camera stop command received")
    
    except websockets.exceptions.ConnectionClosed:
        logging.info("Client disconnected unexpectedly")
    except Exception as e:
        logging.error(f"Error handling client: {e}")
    finally:
        CONNECTED_CLIENTS.discard(websocket)
        logging.info(f"Client removed. Total clients: {len(CONNECTED_CLIENTS)}")
        
        # Stop camera if no clients
        if len(CONNECTED_CLIENTS) == 0:
            camera_active = False

async def main():
    """Start the WebSocket server"""
    initialize_model()
    
    host = "localhost"
    port = 8765
    
    async with websockets.serve(
        handle_client,
        host,
        port,
        ping_interval=20,
        ping_timeout=20
    ):
        logging.info(f"WebSocket server started at ws://{host}:{port}")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server shutting down...")