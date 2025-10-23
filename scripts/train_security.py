from ultralytics import YOLO
import torch
from datetime import datetime

def train_security_model():
    """
    Train YOLOv8 for person, weapon, and object detection
    """
    print("="*60)
    print("🚀 YOLOv8 Security System Training")
    print("="*60)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖥️  GPU Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
    print("="*60)
    
    # Load pretrained YOLOv8 model
    # Choose model size based on your needs:
    # - yolov8n.pt: Fastest, least accurate (good for testing)
    # - yolov8s.pt: Balanced (recommended for most cases)
    # - yolov8m.pt: More accurate, slower
    # - yolov8l.pt: Most accurate, slowest
    
    model = YOLO('yolov8s.pt')  # Using Small model (balanced)
    
    print("\n📚 Training Configuration:")
    print("  - Model: YOLOv8s")
    print("  - Classes: person, weapon, object")
    print("  - Epochs: 100")
    print("  - Image Size: 640x640")
    print("  - Batch Size: 16")
    print("\n" + "="*60 + "\n")
    
    # Train the model
    results = model.train(
        data='data/data.yaml',        # Path to your data.yaml
        epochs=100,                   # Number of training epochs
        imgsz=640,                    # Image size
        batch=16,                     # Batch size (reduce if out of memory)
        name='security_detector',     # Experiment name
        patience=50,                  # Early stopping patience
        save=True,                    # Save checkpoints
        device=0,                     # Use GPU 0 (change to 'cpu' if no GPU)
        workers=4,                    # Number of dataloader workers
        project='runs/detect',        # Project directory
        exist_ok=True,                # Overwrite existing
        pretrained=True,              # Use pretrained weights
        optimizer='auto',             # Optimizer
        verbose=True,                 # Verbose output
        seed=42,                      # Random seed
        deterministic=True,           # Deterministic training
        amp=True,                     # Mixed precision training
        
        # Hyperparameters
        lr0=0.01,                     # Initial learning rate
        lrf=0.01,                     # Final learning rate fraction
        momentum=0.937,               # Momentum
        weight_decay=0.0005,          # Weight decay
        warmup_epochs=3.0,            # Warmup epochs
        warmup_momentum=0.8,          # Warmup momentum
        
        # Data Augmentation
        hsv_h=0.015,                  # HSV-Hue augmentation
        hsv_s=0.7,                    # HSV-Saturation
        hsv_v=0.4,                    # HSV-Value
        degrees=0.0,                  # Rotation (+/- deg)
        translate=0.1,                # Translation (+/- fraction)
        scale=0.5,                    # Scale (+/- gain)
        shear=0.0,                    # Shear (+/- deg)
        perspective=0.0,              # Perspective (+/- fraction)
        flipud=0.0,                   # Vertical flip probability
        fliplr=0.5,                   # Horizontal flip probability
        mosaic=1.0,                   # Mosaic augmentation probability
        mixup=0.0,                    # MixUp augmentation probability
        copy_paste=0.0,               # Copy-paste augmentation
    )
    
    print("\n" + "="*60)
    print("✅ Training Completed!")
    print("="*60)
    print(f"📁 Results: runs/detect/security_detector")
    print(f"🏆 Best Model: runs/detect/security_detector/weights/best.pt")
    print(f"📊 Last Model: runs/detect/security_detector/weights/last.pt")
    print(f"📈 Metrics: runs/detect/security_detector/results.csv")
    print("="*60)
    
    return results

if __name__ == '__main__':
    train_security_model()



##alternative 
'''
from ultralytics import YOLO
import torch

print("🚀 Starting YOLO Training...")
print(f"GPU Available: {torch.cuda.is_available()}")

# Load pretrained model
model = YOLO('yolov8s.pt')

# Train
results = model.train(
    data='data/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='security_model',
    device=0  # Use 'cpu' if no GPU
)

print("✅ Training complete!")
print("📁 Model saved to: runs/detect/security_model/weights/best.pt")
'''