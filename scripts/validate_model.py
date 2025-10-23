from ultralytics import YOLO

def validate_model(model_path='runs/detect/security_detector/weights/best.pt'):
    """Validate the trained model"""
    
    # Load best trained model
    model = YOLO(model_path)
    
    # Validate
    print("🔍 Validating model...")
    metrics = model.val(data='data/data.yaml')
    
    print("\n" + "="*60)
    print("📊 Validation Results")
    print("="*60)
    print(f"  mAP50: {metrics.box.map50:.4f}")
    print(f"  mAP50-95: {metrics.box.map:.4f}")
    print(f"  Precision: {metrics.box.mp:.4f}")
    print(f"  Recall: {metrics.box.mr:.4f}")
    
    # Per-class metrics
    print("\n📋 Per-Class Results:")
    classes = ['person', 'weapon', 'object']
    for i, class_name in enumerate(classes):
        print(f"  {class_name}:")
        print(f"    AP50: {metrics.box.ap50[i]:.4f}")
        print(f"    Precision: {metrics.box.p[i]:.4f}")
        print(f"    Recall: {metrics.box.r[i]:.4f}")
    print("="*60)
    
    return metrics

if __name__ == '__main__':
    validate_model()