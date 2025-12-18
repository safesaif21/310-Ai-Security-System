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

## ⚡ Recent Optimizations & Features

### 🚀 Instant Backend Startup
- **Skip Scanning**: Bypass the slow camera auto-detection phase.
- **Configuration**: Add `FIXED_CAMERA_COUNT=1` to your `.env` file to jump straight to active feeds.

### 🛡️ Robust Auto-Recovery
- **Self-Healing**: The backend automatically monitors camera health.
- **Reconnection**: If a camera cable is bumped or a signal is lost, the system will **automatically attempt to restart the connection** after a short delay without requiring a full restart.

### 🧠 Intelligent Detection Logic
- **Hysteresis (Persistence)**: AI must see an object for several consecutive frames (10 for people, 5 for weapons) to filter out flickering/glitches.
- **Logging Cooldown**: Prevents log spam by limiting alerts to once every 30-60 seconds for stable objects.

### 📼 Recording & Performance
- **360p Optimization**: Records at **640x360 (nHD)** to drastically reduce file sizes (5-10MB/min) while maintaining high clarity for security review.
- **Dynamic FPS**: Automatically detects and matches the camera's native frame rate for perfect synchronization.
- **Browser Playback**: Uses stabilized **H.264 (avc1)** encoding for instant playback in modern web browsers without external codecs.

### 📱 Improved for Mobile
- **Responsive Navigation**: Automatically pivots from a multi-column desktop grid to a single-column layout on smartphones.
- **Safe Area Awareness**: Fully supports notched screens and home indicators for a seamless edge-to-edge experience.
- **UI Compactness**: Navigation and headers shrink on mobile to maximize screen space for camera feeds.

---

## Project Structure

```
310-AI-Security-System/
├── backend/
│   ├── __init__.py                 # Package initialization
│   ├── app.py                      # Main loop, video capture & recovery logic
│   ├── main.py                     # Entry point (Uvicorn)
│   ├── config.py                   # Pydantic-based configuration management
│   │
│   ├── managers/
│   │   ├── camera_manager.py       # Detection stats & startup logic
│   │   ├── recording_manager.py    # Multi-camera segmenting & storage rotation
│   │   ├── master_recorder.py      # Composite 2x2 grid recording
│   │   └── log_manager.py          # Centralized event logging (UTF-8)
│   │
│   ├── routers/
│   │   ├── logs.py                 # Date-based log retrieval API
│   │   └── recordings.py           # Stream-optimized video delivery
│   │
│   └── utils/
│       └── video_utils.py          # Frame drawing & overlay utilities
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CameraCard.jsx      # Feed display with fullscreen support
│   │   │   ├── CameraGrid.jsx      # Adaptive layout engine
│   │   │   ├── Header.jsx          # Mobile-aware dashboard header
│   │   │   ├── Navigation.jsx      # Responsive view switcher
│   │   │   ├── RecordingsView.jsx  # Video browser with desktop/mobile stacking
│   │   │   ├── LogsView.jsx        # Colored console with viewport fixes
│   │   │   └── Sidebar.jsx         # Controls, threat level, and statistics
│   │   │
│   │   ├── App.jsx                 # Global state & window resize management
│   │   ├── index.css               # Premium dark-mode glassmorphism styles
│   │   └── main.jsx                # React root
│   │
│   ├── index.html                  # Viewport-fit cover support
│   └── vite.config.js              # Build & Dev configuration
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

The system features an intelligent recording system with automatic rotation:

#### **Per-Camera Recordings (Optimized)**
- **Location**: `recordings/camera_X/`
- **Resolution**: **360p (nHD)** - Optimized for tiny file sizes (approx. 5-10MB / min) while preserving clarity.
- **Format**: MP4 with **H.264 (avc1/H264)** codec.
- **Features**:
  - Automatic frame downscaling.
  - Storage management (1GB per camera limit).

#### **Master Recordings**
- **Location**: `master/`
- **Layout**: 2x2 grid showing up to 4 cameras simultaneously.
- **Overlays**: Active YOLO model, people counts, and threat level.

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

The system maintains comprehensive event logs with improved readability:

#### **Log Location**
- **Directory**: `logs/`
- **Format**: Daily text files named `YYYY-MM-DD.txt`

#### **Logged Events**
- **Recording Events**: Start/stop of recording sessions
- **Detection Events**: Person and weapon detections with counts
- **Camera Events**: Camera additions, removals, and failures
- **System Events**: Application start/stop

#### **Log Formats**
- **Daily Files**: `logs/YYYY-MM-DD.txt` (UTF-8 encoding).
- **Frontend View**: Colored codes for faster scanning:
  - `[ERROR]` - Red (Critical alerts)
  - `[WARNING]` - Orange (System warnings/Weapons)
  - `[SUCCESS]` - Green (Connections/Status)
  - `[DETECTION]` - Blue (Object events)

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