# python human_detection_test.py path\to\your\image.jpg

#!/usr/bin/env python3
"""
YOLOv8 Human Detection Test Script
This script uses YOLOv8 to detect if there are humans in an image.
"""

import cv2
import numpy as np
from ultralytics import YOLO
import argparse
import os
from pathlib import Path


def load_yolo_model(model_path="yolov8n.pt"):
    """
    Load YOLOv8 model
    
    Args:
        model_path (str): Path to the YOLOv8 model file
        
    Returns:
        YOLO: Loaded YOLO model
    """
    try:
        model = YOLO(model_path)
        print(f"✅ Successfully loaded YOLOv8 model: {model_path}")
        return model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None


def detect_humans_in_image(model, image_path, confidence_threshold=0.5):
    """
    Detect humans in an image using YOLOv8
    
    Args:
        model (YOLO): Loaded YOLOv8 model
        image_path (str): Path to the image file
        confidence_threshold (float): Minimum confidence threshold for detection
        
    Returns:
        dict: Detection results containing human count and details
    """
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return None
    
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Could not load image: {image_path}")
            return None
        
        # Run inference
        results = model(image, verbose=False)
        
        # Process results
        human_detections = []
        human_count = 0
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Class 0 is 'person' in COCO dataset (which YOLOv8 uses)
                    if int(box.cls) == 0 and float(box.conf) >= confidence_threshold:
                        human_count += 1
                        
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        confidence = float(box.conf)
                        
                        human_detections.append({
                            'bbox': [x1, y1, x2, y2],
                            'confidence': confidence
                        })
        
        result_data = {
            'image_path': image_path,
            'humans_detected': human_count > 0,
            'human_count': human_count,
            'detections': human_detections,
            'image_shape': image.shape
        }
        
        return result_data
        
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return None


def save_annotated_image(model, image_path, output_path=None, confidence_threshold=0.5):
    """
    Save an annotated image with bounding boxes around detected humans
    
    Args:
        model (YOLO): Loaded YOLOv8 model
        image_path (str): Path to the input image
        output_path (str): Path to save the annotated image
        confidence_threshold (float): Minimum confidence threshold for detection
    """
    if output_path is None:
        name = Path(image_path).with_suffix('')
        ext = Path(image_path).suffix
        output_path = f"{name}_annotated{ext}"
    
    try:
        # Load image
        image = cv2.imread(image_path)
        
        # Run inference
        results = model(image, verbose=False)
        
        # Draw bounding boxes
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    if int(box.cls) == 0 and float(box.conf) >= confidence_threshold:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        confidence = float(box.conf)
                        
                        # Draw rectangle
                        cv2.rectangle(image, (x1, y1), (x2, y2), (128, 0, 128), 5)
                        
                        # Add label
                        label = f"Person: {confidence:.2f}"
                        cv2.putText(image, label, (x1, y1 - 10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 2, (128, 0, 128), 5)
        
        # Save annotated image
        cv2.imwrite(output_path, image)
        print(f"✅ Annotated image saved: {output_path}")
        
    except Exception as e:
        print(f"❌ Error saving annotated image: {e}")


def test_human_detection(image_path, model_path="yolov8n.pt", confidence=0.5, save_annotated=False):
    """
    Test human detection on a single image
    
    Args:
        image_path (str): Path to the test image
        model_path (str): Path to the YOLOv8 model
        confidence (float): Confidence threshold
        save_annotated (bool): Whether to save annotated image
    """
    print("🔍 YOLOv8 Human Detection Test")
    print("=" * 50)
    
    # Load model
    model = load_yolo_model(model_path)
    if model is None:
        return
    
    # Detect humans
    print(f"\n📸 Processing image: {image_path}")
    results = detect_humans_in_image(model, image_path, confidence)
    
    if results is None:
        return
    
    # Display results
    print(f"\n📊 Detection Results:")
    print(f"   Image: {results['image_path']}")
    print(f"   Image size: {results['image_shape'][1]}x{results['image_shape'][0]} pixels")
    print(f"   Humans detected: {'✅ YES' if results['humans_detected'] else '❌ NO'}")
    print(f"   Number of humans: {results['human_count']}")
    
    if results['detections']:
        print(f"\n🎯 Detection Details:")
        for i, detection in enumerate(results['detections'], 1):
            bbox = detection['bbox']
            conf = detection['confidence']
            print(f"   Human {i}: Confidence {conf:.3f}, "
                  f"BBox: ({bbox[0]:.0f}, {bbox[1]:.0f}, {bbox[2]:.0f}, {bbox[3]:.0f})")
    
    # Save annotated image if requested
    if save_annotated:
        print(f"\n💾 Saving annotated image...")
        save_annotated_image(model, image_path, confidence_threshold=confidence)


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='YOLOv8 Human Detection Test')
    parser.add_argument('image_path', help='Path to the input image')
    parser.add_argument('--model', default='yolov8n.pt', 
                       help='Path to YOLOv8 model (default: yolov8n.pt)')
    parser.add_argument('--confidence', type=float, default=0.5,
                       help='Confidence threshold (default: 0.5)')
    parser.add_argument('--save-annotated', action='store_true',
                       help='Save annotated image with bounding boxes')
    
    args = parser.parse_args()
    
    test_human_detection(
        image_path=args.image_path,
        model_path=args.model,
        confidence=args.confidence,
        save_annotated=args.save_annotated
    )


if __name__ == "__main__":
    main()

