from ultralytics import YOLO
import cv2
import sys

# Function to test model on a single image
def test_on_image(image_path, model_path='runs/detect/security_detector/weights/best.pt'):
    """Test model on a single image"""
    
    # Load trained model
    model = YOLO(model_path)
    
    # Run detection
    print(f"🔍 Running detection on: {image_path}")
    results = model(image_path, conf=0.25)
    
    # Get detections
    detections = results[0]
    
    print(f"\n🎯 Detections Found: {len(detections.boxes)}\n")
    
    for box in detections.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        class_name = detections.names[class_id]
        bbox = box.xyxy[0].tolist()
        
        print(f"  • {class_name}: {confidence:.2%} at {bbox}")
    
    # Save annotated image
    annotated = results[0].plot()
    output_path = 'output_detection.jpg'
    cv2.imwrite(output_path, annotated)
    print(f"\n💾 Saved result to: {output_path}")
    
    # Display (optional)
    cv2.imshow('Detection Result', annotated)
    print("\nPress any key to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = input("Enter image path: ")
    
    test_on_image(image_path)