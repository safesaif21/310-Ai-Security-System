# YOLOv8 Human Detection Test

This script uses YOLOv8 to detect humans in images.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **The script will automatically download the YOLOv8 model on first run** (yolov8n.pt - nano version, ~6MB)

## Usage

### Basic usage:
```bash
python human_detection_test.py path/to/your/image.jpg
```

### Advanced usage:
```bash
# Use a larger model for better accuracy
python human_detection_test.py image.jpg --model yolov8s.pt

# Adjust confidence threshold
python human_detection_test.py image.jpg --confidence 0.7

# Save annotated image with bounding boxes
python human_detection_test.py image.jpg --save-annotated
```

### Example output:
```
🔍 YOLOv8 Human Detection Test
==================================================
✅ Successfully loaded YOLOv8 model: yolov8n.pt

📸 Processing image: test_image.jpg

📊 Detection Results:
   Image: test_image.jpg
   Image size: 1920x1080 pixels
   Humans detected: ✅ YES
   Number of humans: 2

🎯 Detection Details:
   Human 1: Confidence 0.876, BBox: (245, 123, 456, 678)
   Human 2: Confidence 0.743, BBox: (789, 234, 987, 654)
```

## Available YOLOv8 Models

- `yolov8n.pt` - Nano (fastest, least accurate)
- `yolov8s.pt` - Small
- `yolov8m.pt` - Medium
- `yolov8l.pt` - Large
- `yolov8x.pt` - Extra Large (slowest, most accurate)

## Functions

- `load_yolo_model()` - Load YOLOv8 model
- `detect_humans_in_image()` - Detect humans and return results
- `save_annotated_image()` - Save image with bounding boxes
- `test_human_detection()` - Main test function

## Return Format

The detection function returns a dictionary with:
```python
{
    'image_path': str,
    'humans_detected': bool,
    'human_count': int,
    'detections': [
        {
            'bbox': [x1, y1, x2, y2],
            'confidence': float
        }
    ],
    'image_shape': tuple
}
```