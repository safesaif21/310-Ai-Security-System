# 🔒 AI Security System - Streamlit Dashboard

A beautiful AI-powered security dashboard with real-time threat detection, weapon identification, and live camera monitoring built with Streamlit.

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Detection-green)

## 🌟 Features

### 🎯 Real-time Detection
- **Live Camera Feed**: Real-time video processing with detection overlays
- **Human Detection**: Identifies and counts people in view
- **Weapon Detection**: Detects dangerous objects (knives, bats, scissors)
- **Threat Level Assessment**: Dynamic 0-10 scale with color-coded alerts
- **Bounding Boxes**: Visual overlays on detected objects

### 🎨 Beautiful Modern UI
- **Stunning Dark Theme**: Professional gradient backgrounds
- **Real-time Threat Meter**: Large circular display (0-10 scale)
- **Color-coded Alerts**: Green → Yellow → Red based on threat level
- **Weapon Alerts**: Instant visual notifications for detected threats
- **Statistics Dashboard**: People count, alerts, timestamps, system status
- **Responsive Layout**: Clean two-column design
- **Smooth Animations**: Professional transitions and effects

### 📊 Threat Level System
- **0**: 🟢 SAFE - No threats detected
- **1-3**: 🟢 LOW - Minimal threat, normal activity
- **4-6**: 🟡 MODERATE - Increased monitoring required
- **7-8**: 🔴 HIGH - Immediate attention needed
- **9-10**: 🔴 CRITICAL - Emergency response required

## 🚀 Quick Start

### Installation

1. **Clone or download the repository**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

The YOLO model (`yolov8n.pt`) will auto-download on first run.

### Running the Dashboard

**Single Command:**
```bash
streamlit run dashboard.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

That's it! 🎉

## 📖 How to Use

1. **Start the Dashboard**
   ```bash
   streamlit run dashboard.py
   ```

2. **Wait for the page to load** in your browser

3. **Click "Start Camera"** button to begin monitoring

4. **View Real-time Data:**
   - Left side: Live camera feed with detection overlays
   - Right side: Threat level, weapon alerts, statistics

5. **Click "Stop Camera"** when done

## 🎯 Dashboard Layout

### Left Panel - Camera Feed
- **Live Video Stream**: Real-time camera view
- **Detection Overlays**: Colored bounding boxes
  - 🟢 Green: People
  - 🔴 Red: Weapons
  - 🟠 Orange: Other objects
- **On-Screen Stats**: Threat level, people count, FPS

### Right Panel - Analysis
1. **Threat Level Meter**
   - Large numeric display (0-10)
   - Color-coded indicator
   - Status badge (SAFE/LOW/MODERATE/HIGH/CRITICAL)
   - Description text

2. **Weapon Detection Panel**
   - ✅ No weapons: Green checkmark display
   - ⚠️ Weapons found: Red alert box with details
   - Lists all detected weapons with confidence %

3. **Statistics Grid**
   - 👥 People Detected: Current count
   - 🚨 Alerts Today: Total alert count
   - ⏰ Last Update: Current timestamp
   - 🟢/🔴 System Status: Active/Inactive

## ⚙️ Configuration

### Change Camera Source

Edit `dashboard.py` line ~335:
```python
cap = cv2.VideoCapture(0)  # Change 0 to 1 for external USB camera
```

### Adjust Detection Threshold

Edit `dashboard.py` line ~170:
```python
if confidence >= 0.5:  # Change to 0.7 for stricter detection
```

### Modify Frame Rate

Edit `dashboard.py` line ~376:
```python
time.sleep(0.03)  # Decrease for faster, increase for slower
```

## 📊 Threat Calculation

The system calculates threat levels based on:

| Factor | Impact | Points |
|--------|--------|--------|
| Weapon detected | High | +7 per weapon |
| 5+ people | Medium | +2 points |
| 3-4 people | Low | +1 point |

**Maximum**: Capped at 10

## 🎨 Customization

### Colors

The dashboard uses these color themes:
- **Background**: Dark blue gradients (#0f172a to #1e293b)
- **Cards**: Slate gradients (#1e293b to #334155)
- **Primary**: Indigo (#6366f1)
- **Success**: Green (#10b981)
- **Warning**: Amber (#f59e0b)
- **Danger**: Red (#ef4444)

Edit the CSS in `dashboard.py` (lines 30-200) to customize.

### Layout

Change the column ratio on line 278:
```python
col1, col2 = st.columns([2, 1])  # Change to [3, 1] for wider video
```

## 🔧 Troubleshooting

### Camera Not Working
**Problem**: "Could not access camera"

**Solutions**:
- Grant camera permissions to your terminal/Python
- Close other apps using the camera (Zoom, Skype, etc.)
- Try a different camera ID (0, 1, 2...)
- Restart your computer

### Model Loading Slow
**Problem**: First run takes time

**Explanation**: YOLOv8 model downloads on first run (~6MB)

**Solution**: Be patient, subsequent runs will be instant

### Low FPS / Laggy
**Solutions**:
- Close other applications
- Reduce camera resolution:
  ```python
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
  ```
- Increase sleep time to 0.05 or 0.1
- Use GPU acceleration if available

### Port Already in Use
**Problem**: "Address already in use"

**Solution**:
```bash
# Stop the previous Streamlit instance
# Or use a different port:
streamlit run dashboard.py --server.port 8502
```

### Dependencies Issues
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 📱 Browser Compatibility

Tested and working on:
- ✅ Google Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Microsoft Edge 90+

## 🖥️ System Requirements

### Minimum
- Python 3.7+
- 4GB RAM
- Webcam
- CPU: Dual-core 2.0GHz

### Recommended
- Python 3.9+
- 8GB+ RAM
- HD Webcam (720p+)
- CPU: Quad-core 3.0GHz+
- GPU with CUDA (optional, for better performance)

## 📁 Project Structure

```
310-Ai-Security-System/
├── dashboard.py              # Main Streamlit dashboard (RUN THIS!)
├── human_detection_test.py   # YOLO detection functions
├── example_usage.py          # Simple usage examples
├── backend/
│   └── server.py            # WebSocket server (not used in Streamlit version)
├── requirements.txt          # Python dependencies
├── yolov8n.pt               # YOLOv8 model (auto-downloads)
├── usage_guide.md           # Additional documentation
└── README.md                # This file
```

## 🚀 Deployment

### Run Locally
```bash
streamlit run dashboard.py
```

### Run on Network
```bash
streamlit run dashboard.py --server.address 0.0.0.0
```
Access from other devices: `http://YOUR_IP:8501`

### Run on Custom Port
```bash
streamlit run dashboard.py --server.port 8080
```

## 💡 Tips for Best Results

1. **Good Lighting**: Ensure area is well-lit for better detection
2. **Camera Angle**: Position camera with clear view of monitored area
3. **Stable Mount**: Keep camera steady for consistent detection
4. **Distance**: Stay 2-10 feet from camera for optimal detection
5. **Background**: Avoid cluttered backgrounds when possible

## 🔐 Security & Privacy

- ✅ All processing happens locally on your machine
- ✅ No data sent to external servers
- ✅ No internet required after model download
- ✅ Camera access only when "Start Camera" is clicked
- ✅ No recording or storage of video
- ⚠️ For production use, add authentication and HTTPS

## 📝 Detection Capabilities

The system can detect 80+ objects from the COCO dataset, including:

**People & Security:**
- ✅ Person detection (tracks count)
- ⚠️ Knife detection
- ⚠️ Baseball bat detection
- ⚠️ Scissors detection

**Common Objects:**
- 🚗 Vehicles (car, truck, bus, motorcycle)
- 🎒 Bags (backpack, handbag, suitcase)
- 📱 Electronics (laptop, phone, keyboard, mouse)
- 🪑 Furniture (chair, couch, bed)
- And 60+ more...

## 🎓 How It Works

```
┌──────────────┐
│   Webcam     │
│   Input      │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  Streamlit App   │
│  • Captures      │
│  • Processes     │
│  • Displays      │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  YOLOv8 Model    │
│  • Detects       │
│  • Classifies    │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Threat Calc     │
│  • Analyzes      │
│  • Scores 0-10   │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  UI Update       │
│  • Video feed    │
│  • Threat meter  │
│  • Alerts        │
│  • Stats         │
└──────────────────┘
```

## 🤝 Contributing

Contributions welcome! To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your improvements
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Streamlit** - Beautiful Python web framework
- **Ultralytics YOLOv8** - State-of-the-art object detection
- **OpenCV** - Computer vision library
- **COCO Dataset** - Training data for object detection

## 📬 Support

For issues or questions:
- Check this README thoroughly
- Review the troubleshooting section
- Create an issue on GitHub with:
  - Your Python version
  - Operating system
  - Error messages
  - Steps to reproduce

## 🎯 Keyboard Shortcuts

While dashboard is running:
- **Ctrl+C** in terminal: Stop the server
- **R** in browser: Rerun the app
- **C** in browser: Clear cache

## 🔄 Updates

To update dependencies:
```bash
pip install --upgrade streamlit ultralytics opencv-python
```

## 📈 Performance Metrics

Expected performance:
- **Camera FPS**: 25-30 FPS
- **Detection FPS**: 10-20 FPS (hardware dependent)
- **UI Update**: Real-time
- **Model Inference**: 30-100ms per frame
- **RAM Usage**: 1-2GB
- **CPU Usage**: 30-60% (single core)

---

## Quick Command Summary

```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run dashboard.py

# Run on network
streamlit run dashboard.py --server.address 0.0.0.0

# Run on custom port
streamlit run dashboard.py --server.port 8080

# Update packages
pip install --upgrade streamlit ultralytics opencv-python
```

---

**Built with ❤️ using Streamlit**

🌟 **Star this repo if you find it useful!**

🚀 **Ready to run? Just type:** `streamlit run dashboard.py`
