from ultralytics import YOLO
import torch
from datetime import datetime
import os
import sys

# Function to train YOLOv8 on any dataset given by a data.yaml
def train_yolo_model(data_yaml_path, model_name):
    """
    Train YOLOv8 on the dataset specified by data_yaml_path
    """
    if not os.path.exists(data_yaml_path):
        print(f"❌ data.yaml not found at {data_yaml_path}")
        sys.exit(1)

    print("="*60)
    print("🚀 YOLOv8 Training")
    print("="*60)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖥️  GPU Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
    print("="*60)
    
    # Load pretrained YOLOv8 small model
    model = YOLO('yolov8s.pt')  # Small model (balanced)
    
    print("\n📚 Training Configuration:")
    print(f"  - Model: YOLOv8s")
    print(f"  - Data YAML: {data_yaml_path}")
    print("  - Epochs: 25 (recommended for small dataset)")
    print("  - Image Size: 640x640")
    print("  - Batch Size: 8")
    print("\n" + "="*60 + "\n")
    
    # Train the model
    results = model.train(
        data=data_yaml_path,          # Use the provided data.yaml
        epochs=25,                    # Fewer epochs for small dataset
        imgsz=640,                    # Image size
        batch=8,                      # Smaller batch for small dataset / GPU
        name=model_name,              # Experiment name
        patience=10,                  # Early stopping patience
        save=True,                    # Save checkpoints
        device=0 if torch.cuda.is_available() else 'cpu',  # GPU or CPU
        workers=2,                    # Fewer workers for small dataset
        project='runs/detect',        # Project directory
        exist_ok=True,                # Overwrite existing
        pretrained=True,              # Use pretrained weights
        verbose=True,                 # Verbose output
        seed=42,                      # Random seed
        deterministic=True,           # Deterministic training
        amp=True,                     # Mixed precision
        
        # Data Augmentation
        mosaic=1.0,
        fliplr=0.5,
        degrees=15.0,
        translate=0.1,
        scale=0.5,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4
    )
    
    print("\n" + "="*60)
    print("✅ Training Completed!")
    print("="*60)
    print(f"📁 Results: runs/detect/{model_name}")
    print(f"🏆 Best Model: runs/detect/{model_name}/weights/best.pt")
    print(f"📊 Last Model: runs/detect/{model_name}/weights/last.pt")
    print(f"📈 Metrics: runs/detect/{model_name}/results.csv")
    print("="*60)
    
    return results

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python train_model.py <path_to_data.yaml>")
        sys.exit(1)

    data_yaml_path = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "yolo_model_experiment"
    train_yolo_model(data_yaml_path, model_name)
