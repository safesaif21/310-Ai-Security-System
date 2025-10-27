# 🎯 YOLOv8 Training Guide - AI Security System

Quick guide to train our custom YOLOv8 model to detect **person**, **weapon**, and **object** in our security system.

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Setup Instructions](#setup-instructions)
4. [Training Workflow](#training-workflow)
5. [Troubleshooting](#troubleshooting)
6. [Testing & Deployment](#testing--deployment)

---

## 🔧 Prerequisites

### Required Software
- Python 3.8+
- Git
- 8GB+ RAM (16GB recommended)
- GPU with CUDA support (optional but recommended)

### Required Python Packages
All dependencies are in `requirements.txt`

---

## 📁 Project Structure
```
310-Ai-Security-System/
├── .venv/                          # Virtual environment
├── data/                           # Dataset directory
│   ├── images/
│   │   ├── train/                 # Training images
│   │   └── val/                   # Validation images
│   ├── labels/
│   │   ├── train/                 # Training labels (YOLO format)
│   │   └── val/                   # Validation labels
│   └── data.yaml                  # Dataset configuration
├── scripts/                        # Training scripts
│   ├── verify_dataset.py          # Verify dataset integrity
│   ├── train_security.py          # Main training script
│   ├── validate_model.py          # Validate trained model
│   └── test_image.py              # Test on single images
├── runs/                           # Training outputs (auto-created)
│   └── detect/
│       └── security_model/
│           ├── weights/
│           │   ├── best.pt        # Best model weights
│           │   └── last.pt        # Last checkpoint
│           └── results.csv        # Training metrics
└── models/                         # Final trained models
```

---

## 🚀 Setup Instructions


### Activate Virtual Environment
```bash
# On Mac/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Verify Installation
```bash
python -c "from ultralytics import YOLO; print('✅ YOLOv8 ready!')"
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}')"
```

---

## 📊 Dataset Setup

### Dataset Requirements

**Minimum images:**
- **Total:** 300+ images
- **Per class:** 100+ images each (person, weapon, object)
- **Split:** 70% train (~210), 30% validation (~90)

### Our 3 Classes

- **Class 0:** person
- **Class 1:** weapon
- **Class 2:** object

### Label Format (YOLO)

Each image needs a matching `.txt` file:
```
<class_id> <x_center> <y_center> <width> <height>
```

All values are normalized (0-1). Example:
```
0 0.5 0.5 0.3 0.4
1 0.7 0.3 0.2 0.15
```

### `data.yaml` Configuration

Located at `data/data.yaml`:
```yaml
# Dataset paths
path: ../data
train: images/train
val: images/val

# Number of classes
nc: 3

# Class names
names:
  0: person
  1: weapon
  2: object
```

---

## 🎓 Training Workflow

### **Step 1: Verify Dataset**

Always verify your dataset before training:
```bash
python scripts/verify_dataset.py
```

**Expected output:**
```
🔍 Verifying dataset structure...

✅ data/images/train exists
✅ data/images/val exists
✅ data/labels/train exists
✅ data/labels/val exists

📊 Dataset Statistics:
  Training images: 210
  Training labels: 210
  Validation images: 90
  Validation labels: 90

✅ Training images and labels match!
✅ Validation images and labels match!
✅ Dataset verification complete!
```

---

### **Step 2: Train the Model**

Run the main training script:
```bash
python scripts/train_security.py
```

**What happens:**
1. Loads pretrained YOLOv8s weights
2. Trains on your dataset for 100 epochs
3. Validates after each epoch
4. Saves best model automatically

**Training output:**
```
🚀 YOLOv8 Security Training
============================================================
⏰ Started: 2024-01-15 14:30:00
💻 GPU Available: True
============================================================

⚙️  Configuration:
   Classes: person, weapon, object
   Epochs: 100
   Image Size: 640
   Batch: 16

============================================================

Epoch  GPU_mem  box_loss  cls_loss  dfl_loss  Instances  Size
  1/100   2.5G    1.234     0.876     1.123      156      640
  2/100   2.5G    1.187     0.823     1.089      145      640
...
100/100   2.5G    0.335     0.149     0.382       88      640

✅ TRAINING COMPLETE!
============================================================
📁 Results: runs/detect/security_model/
🏆 Best model: runs/detect/security_model/weights/best.pt
```

**Training time (300 images):**
- **With GPU (RTX 3060):** 1-1.5 hours
- **With CPU:** 6-8 hours

---

### **Step 3: Validate the Model**

Check model performance:
```bash
python scripts/validate_model.py
```

**Expected output:**
```
🔍 Validating model...

============================================================
📊 Validation Results
============================================================
  mAP50: 0.7234
  mAP50-95: 0.4567
  Precision: 0.7891
  Recall: 0.6543

📋 Per-Class Results:
  person:     AP50: 0.8123
  weapon:     AP50: 0.6789
  object:     AP50: 0.6789
============================================================
```

**What good metrics look like:**
- **mAP50:** > 0.5 (acceptable), > 0.7 (good)
- **Precision:** > 0.6 (acceptable), > 0.8 (good)
- **Recall:** > 0.5 (acceptable), > 0.7 (good)

---

### **Step 4: Test the Model**

Test on a single image:
```bash
python scripts/test_image.py path/to/test_image.jpg
```

**Output:**
```
🔍 Running detection on: test_image.jpg

🎯 Detections Found: 3

  • person: 92.34%
  • weapon: 78.56%
  • object: 65.23%

💾 Saved result to: output_detection.jpg
```

---

## 🎛️ Customizing Training

### Change Model Size

Edit `scripts/train_security.py`:
```python
model = YOLO('yolov8n.pt')  # Fast, less accurate
model = YOLO('yolov8s.pt')  # Balanced (default)
model = YOLO('yolov8m.pt')  # Accurate, slower
```

### Adjust Training Time
```python
epochs=50,   # Quick test
epochs=100,  # Default
epochs=200,  # Better accuracy
```

### Fix Memory Issues
```python
batch=8,   # If out of memory
batch=16,  # Default
batch=32,  # If you have more memory
```

### Use CPU Instead of GPU
```python
device='cpu',  # Change from 0 to 'cpu'
```

---

## 🐛 Troubleshooting

### "Dataset not found" Error

**Solution:**
- Verify `data.yaml` exists in `data/` folder
- Check paths are correct
- Use absolute paths if needed:
```yaml
train: /full/path/to/310-Ai-Security-System/data/images/train
val: /full/path/to/310-Ai-Security-System/data/images/val
```

---

### CUDA Out of Memory

**Solutions:**
1. Reduce batch size: `batch=8`
2. Use smaller images: `imgsz=416`
3. Use CPU: `device='cpu'`

---

### Low Accuracy (mAP < 0.5)

**Solutions:**
1. Collect more data (aim for 300+ total images)
2. Check label quality
3. Train longer: `epochs=200`
4. Use larger model: `model = YOLO('yolov8m.pt')`

---

### Images and Labels Don't Match

**Solution:**
- Run `python scripts/verify_dataset.py`
- Ensure every `.jpg` has matching `.txt` file
- Remove images without labels

---

### Training Stops Early

**Cause:** Early stopping enabled (patience=50)

**Solutions:**
- Increase patience: `patience=100`
- Disable: `patience=0`

---

## 📊 Understanding Results

After training, check these files:
```
runs/detect/security_model/
├── weights/
│   ├── best.pt              # Use this model!
│   └── last.pt              # Last checkpoint
├── results.csv              # Training metrics
├── results.png              # Training curves
├── confusion_matrix.png     # Classification accuracy
└── val_batch0_pred.jpg      # Sample predictions
```

**Good training looks like:**
- Loss curves decreasing
- mAP increasing
- No large fluctuations

---

## 🧪 Testing & Deployment

### Test on Image
```bash
python scripts/test_image.py path/to/image.jpg
```

### Deploy Model
```bash
# Copy to models directory
mkdir -p models
cp runs/detect/security_model/weights/best.pt models/security_v1.pt
```

### Use in Your App
```python
from ultralytics import YOLO

model = YOLO('models/security_v1.pt')
results = model('test.jpg', conf=0.3)
```

---

## 🎯 Quick Commands
```bash
# Complete workflow
source .venv/bin/activate
python scripts/verify_dataset.py
python scripts/train_security.py
python scripts/validate_model.py
python scripts/test_image.py test.jpg

# Resume interrupted training
yolo train resume model=runs/detect/security_model/weights/last.pt

# Export model
yolo export model=runs/detect/security_model/weights/best.pt format=onnx
```

---

## ✅ Training Checklist

**Before training:**
- [ ] 300+ total images (100+ per class)
- [ ] Images split: 70% train, 30% val
- [ ] Labels in YOLO format
- [ ] `data.yaml` configured
- [ ] `verify_dataset.py` runs without errors

**After training:**
- [ ] mAP > 0.5
- [ ] Test on sample images
- [ ] Model detects correctly
- [ ] Copy to `models/` directory

---

## 🔄 Retraining

### When to Retrain
- Performance below target
- Have new training data
- Seeing consistent errors

### How to Retrain

**Continue from checkpoint:**
```python
model = YOLO('runs/detect/security_model/weights/best.pt')
model.train(data='data/data.yaml', epochs=50)
```

**Start fresh:**
```bash
# Add new images to data/images/train and data/labels/train
python scripts/verify_dataset.py
python scripts/train_security.py
```

---
