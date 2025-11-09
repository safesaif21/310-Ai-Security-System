# 🤖 YOLO Model Selection Feature

## Overview

The system now supports dynamic YOLO model selection! You can switch between different pre-trained models or custom trained models on-the-fly without restarting the server.

## How It Works

### Backend (`backend.py`)

1. **Model Scanning** (`scan_yolo_models()`):
   - Automatically scans for `.pt` files in:
     - `yolo_models/` directory
     - Root directory
     - `models/` directory
     - `weights/` directory
   - Searches for common YOLO model names (yolov8n, yolov8s, yolov5n, etc.)
   - Returns list of available models with paths

2. **Model Switching** (`switch_model()`):
   - Loads new YOLO model when requested
   - Updates global `model` variable
   - Handles path resolution (relative/absolute)

3. **Initialization Response**:
   - When client sends `innit` command, backend responds with:
     - Available models list
     - Current active model path

4. **Switch Command** (`switch_model`):
   - Client sends model path
   - Backend switches model
   - Responds with success/error message

### Frontend (`frontend.py`)

1. **Model Dropdown**:
   - Located in right panel at the top
   - Shows available models by name
   - Disabled when not connected
   - Enabled after connection

2. **Model Selection**:
   - User selects model from dropdown
   - Frontend sends `switch_model` command
   - Status label shows switching progress
   - Updates on success/error

3. **Status Display**:
   - Shows current active model
   - Updates when model switches
   - Color-coded: Green (active), Yellow (switching), Red (error)

## Usage

### Step 1: Start Backend
```bash
python3 backend.py
```

The backend will:
- Load default model (`yolo_models/yolov8n.pt`)
- Scan for available models
- Log all found models

### Step 2: Start Frontend
```bash
python3 frontend.py
```

### Step 3: Connect and Select Model
1. Click **"Connect"** button
2. Model dropdown will populate with available models
3. Select a model from dropdown
4. Status will show "Switching to [model]..."
5. On success: "✅ Active: [model_name]"

## Model File Locations

The system searches for `.pt` files in:
- `yolo_models/*.pt`
- `*.pt` (root directory)
- `models/*.pt`
- `weights/*.pt`

## Adding Custom Models

### Option 1: Place in `yolo_models/` directory
```bash
cp your_custom_model.pt yolo_models/
```

### Option 2: Place in root directory
```bash
cp your_custom_model.pt .
```

### Option 3: Place in `models/` directory
```bash
mkdir models
cp your_custom_model.pt models/
```

The model will automatically appear in the dropdown after restarting the backend.

## Supported Model Types

- ✅ YOLOv8 models (n, s, m, l, x)
- ✅ YOLOv5 models (n, s, m, l, x)
- ✅ Custom trained YOLO models
- ✅ Any `.pt` file compatible with Ultralytics YOLO

## WebSocket Protocol

### `innit` Command Response
```json
{
  "type": "innit",
  "cameras": 1,
  "camera_ids": [0],
  "available_models": [
    {
      "name": "yolov8n",
      "path": "yolo_models/yolov8n.pt",
      "full_path": "/absolute/path/to/yolo_models/yolov8n.pt"
    }
  ],
  "current_model": "yolo_models/yolov8n.pt"
}
```

### `switch_model` Command
```json
{
  "command": "switch_model",
  "model_path": "yolo_models/yolov8s.pt"
}
```

### Success Response
```json
{
  "type": "model_switched",
  "model_path": "yolo_models/yolov8s.pt",
  "message": "Successfully switched to yolo_models/yolov8s.pt"
}
```

### Error Response
```json
{
  "type": "error",
  "message": "Failed to switch to model: invalid_path.pt"
}
```

## Features

✅ **Dynamic Model Scanning** - Automatically finds all models on startup  
✅ **Live Model Switching** - Switch models without restarting  
✅ **Visual Feedback** - Status indicators for model operations  
✅ **Error Handling** - Graceful error messages for invalid models  
✅ **Path Resolution** - Handles relative and absolute paths  
✅ **Cross-Platform** - Works on Windows, macOS, and Linux  

## Notes

- Model switching happens instantly
- Current detections continue with old model until switch completes
- Large models may take a few seconds to load
- The system will use the newly selected model for all future detections
- You can switch models even while cameras are running

## Troubleshooting

### Model Not Appearing in Dropdown
- Check file extension is `.pt`
- Verify file is in one of the searched directories
- Restart backend to rescan models
- Check backend logs for scan results

### Model Switch Fails
- Verify model file exists and is readable
- Check model is compatible with Ultralytics YOLO
- Look at backend logs for detailed error messages
- Ensure model path is correct

### Dropdown Disabled
- Make sure backend is running
- Click "Connect" button first
- Check WebSocket connection status

---

**Enjoy dynamic model selection!** 🚀

