# 310-Ai-Security-System

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![React](https://img.shields.io/badge/React-18.3.1-blue)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Detection-green)
![FastAPI](https://img.shields.io/badge/FastAPI-WebSocket-teal)

An AI-powered security dashboard with real-time threat detection, weapon identification, and live camera monitoring. Built with a React frontend and FastAPI WebSocket backend, featuring advanced recording management and event logging.

---

# Project Setup Guide

## 1. Create a Virtual Environment

Run the following command to create a virtual environment named `.venv`:

```bash
python -m venv .venv
```

---

## 2. Activate the Virtual Environment

### On **Windows (PowerShell)**
```powershell
.venv\Scripts\Activate.ps1
```

### On **Windows (Command Prompt)**
```cmd
.venv\Scripts\activate.bat
```

### On **macOS / Linux (Bash/Zsh)**
```bash
source .venv/bin/activate
```

---

## 3. Install Python Dependencies

Once the virtual environment is active, install backend dependencies with:

```bash
pip install -r requirements.txt
```

---

## 4. Install Frontend Dependencies

Navigate to the frontend directory and install Node.js dependencies:

```bash
cd frontend
npm install
```

---

## 5. Run the Backend Server

To start the FastAPI WebSocket server, run from the root directory:

```bash
python -m backend.main
```

Or alternatively:

```bash
uvicorn backend.app:app --reload
```

The backend will start on `http://localhost:8000`

---

## 6. Run the Frontend

In a new terminal, navigate to the frontend directory and start the development server:

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:5173` (or another port if 5173 is busy)

---

## Threat Calculation

The system calculates threat levels based on:

| Factor | Impact | Points |
|--------|--------|--------|
| Weapon detected | High | +7 per weapon |
| 1 person | Low | +1 point |
| 3-4 people | Medium | +3 points |

**Maximum**: Capped at 10

---

## Project Structure

```
310-AI-Security-System/
├── backend/
│   ├── __init__.py                 # Package initialization
│   ├── app.py                      # FastAPI WebSocket server
│   ├── main.py                     # Application entry point
│   ├── config.py                   # Configuration constants
│   │
│   ├── managers/
│   │   ├── camera_manager.py       # Camera lifecycle management
│   │   ├── recording_manager.py    # Per-camera recording with rotation
│   │   ├── master_recorder.py      # 2x2 grid master recordings
│   │   └── log_manager.py          # Event logging system
│   │
│   ├── models/
│   │   └── # Data models and schemas
│   │
│   └── utils/
│       └── video_utils.py          # Video processing utilities
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CameraCard.jsx      # Individual camera display
│   │   │   ├── CameraGrid.jsx      # Grid layout for cameras
│   │   │   ├── CameraSettings.jsx  # Camera configuration UI
│   │   │   ├── Controls.jsx        # Recording/detection controls
│   │   │   ├── Header.jsx          # Application header
│   │   │   ├── LogsDropdown.jsx    # Event logs viewer
│   │   │   └── Sidebar.jsx         # Settings sidebar
│   │   │
│   │   ├── App.jsx                 # Main application component
│   │   ├── App.css                 # Application styles
│   │   ├── index.css               # Global styles
│   │   └── main.jsx                # React entry point
│   │
│   ├── public/                     # Static assets
│   ├── index.html                  # HTML template
│   ├── package.json                # Node.js dependencies
│   └── vite.config.js              # Vite configuration
│
├── recordings/
│   ├── camera_0/                   # Camera 0 recordings
│   ├── camera_1/                   # Camera 1 recordings
│   └── camera_2/                   # Camera 2 recordings
│
├── master/                         # Master 2x2 grid recordings
│
├── logs/                           # Daily event logs
│   └── YYYY-MM-DD.txt              # Date-based log files
│
├── yolo_models/                    # YOLO model files
│   └── # Pre-trained and custom YOLO models
│
├── model_training_scripts/         # Model training utilities
│   └── # Python scripts for training pipeline
│
├── runs/                           # Training session metrics
│   └── # Performance metrics from training
│
├── diagrams/                       # Documentation diagrams
│   └── pipeline.png                # System pipeline diagram
│
├── requirements.txt                # Python dependencies
├── train_yolo_model_pipeline.py    # YOLO training pipeline
└── README.md                       # This file
```

---

## Recordings & Logging System

### Recording Management

The system features an intelligent recording system with automatic rotation and storage management:

#### **Per-Camera Recordings**
- **Location**: `recordings/camera_X/` (where X is the camera index)
- **Duration**: Videos are saved in 1-minute intervals
- **Format**: MP4 with H.264 codec
- **Naming**: `YYYY-MM-DD_HH-MM-SS.mp4`
- **Features**:
  - Detection bounding boxes visible in recordings
  - Partial recordings saved if system stops abruptly
  - Automatic cleanup when folder exceeds 1GB (oldest files deleted first)

#### **Master Recordings**
- **Location**: `master/`
- **Layout**: 2x2 grid showing up to 4 cameras simultaneously
- **Overlays**: 
  - Current YOLO model name
  - People count per camera
  - Detection bounding boxes
- **Storage**: 1GB limit with automatic rotation
- **Duration**: 1-minute intervals

#### **Configuration**

Recordings can be configured in `backend/config.py`:

```python
# Storage limits (GB)
RECORDING_SIZE_LIMIT_GB = 1.0
MASTER_SIZE_LIMIT_GB = 1.0

# Recording settings
RECORDING_FPS = 20
RECORDING_ROTATION_SECONDS = 60  # 1 minute per file
```

---

### Event Logging

The system maintains comprehensive event logs for all security events:

#### **Log Location**
- **Directory**: `logs/`
- **Format**: Daily text files named `YYYY-MM-DD.txt`

#### **Logged Events**
- **Recording Events**: Start/stop of recording sessions
- **Detection Events**: Person and weapon detections with counts
- **Camera Events**: Camera additions, removals, and failures
- **System Events**: Application start/stop

#### **Log Format**
Each log entry includes:
- Timestamp (HH:MM:SS)
- Event type (INFO, WARNING, ERROR)
- Camera identifier
- Event description

Example:
```
[2025-12-03 14:35:22] INFO - Camera 0: Recording started
[2025-12-03 14:35:25] WARNING - Camera 0: Person detected (count: 3)
[2025-12-03 14:35:30] ERROR - Camera 1: Weapon detected
```

#### **Accessing Logs**
- Logs are accessible through the frontend UI via the **Logs Dropdown** component
- Real-time log updates displayed in the interface
- Historical logs available by date

---

## System Pipeline Diagram

![Pipeline Diagram](diagrams/pipeline.png)

---

## YOLOv8 Training Guide

Quick guide to train our custom YOLOv8 model to detect any class you want in our security system can be found [here](https://youtu.be/z9F9Hssbi-4).

---

## License

This project is licensed under the MIT License.

---

## Acknowledgments

- **Ultralytics YOLOv8** - State-of-the-art object detection
- **COCO Dataset** - Large image collection dataset
- **React** - Modern UI framework
- **FastAPI** - High-performance web framework