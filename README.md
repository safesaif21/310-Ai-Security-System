# 310-Ai-Security-System

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Detection-green)

An AI-powered security dashboard with real-time threat detection, weapon identification, and live camera monitoring built with Streamlit.

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

## 3. Installing Dependencies

Once the virtual environment is active, install dependencies with:

```bash
pip install -r requirements.txt
```

---

## 7. Run server

To start the WebSocket server, run:

```bash
uvicorn backend:app --reload
```

---


## 8. Run frontend

To start the frontend, open the index.html file in a chrome browser:

```bash
Path/to/index.html
```

---

## 📊 Threat Calculation

The system calculates threat levels based on:

| Factor | Impact | Points |
|--------|--------|--------|
| Weapon detected | High | +7 per weapon |
| 1 people | low | +1 points |
| 3-4 people | Medium | +3 point |

**Maximum**: Capped at 10

## 📁 Project Structure

## Project Structure

```
310-AI-Security-System/
├── backend.py                      # WebSocket backend server
├── index.html                      # frontend UI
├── train_yolo_model_pipeline.py    # Yolo training pipeline
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
│
├── model_training_scripts/
│   └── # contains python scripts used by model training pipeline
│
├── runs/
│   └── # contains performance metrics of custom model training sessions
│
└── yolo_models/
    └── # contains all of the selectable yolo models in our program
```

## 🎓 Pipeline Diagram

![Pipeline Diagram](diagrams\pipeline.png)


# 🎯 YOLOv8 Training Guide - AI Security System

Quick guide to train our custom YOLOv8 model to detect any class you want in our security system can be found [here](https://youtu.be/z9F9Hssbi-4).

## 📄 License

This project is licensed under the MIT License.

## Acknowledgments

- **Ultralytics YOLOv8** - State-of-the-art object detection
- **COCO Dataset** - Large image collection dataset
---