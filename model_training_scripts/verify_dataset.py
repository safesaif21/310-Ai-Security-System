import os
from pathlib import Path
import sys

def verify_dataset(images_root, labels_root):
    """Verify dataset structure and files"""
    
    base_images = Path(images_root)
    base_labels = Path(labels_root)
    
    # Directories
    train_images = base_images / 'train'
    val_images = base_images / 'val'
    train_labels = base_labels / 'train'
    val_labels = base_labels / 'val'
    
    print("🔍 Verifying dataset structure...\n")
    
    # Check directories exist
    dirs = [train_images, val_images, train_labels, val_labels]
    for d in dirs:
        if d.exists():
            print(f"✅ {d} exists")
        else:
            print(f"❌ {d} NOT FOUND!")
            return False
    
    # Count files
    train_img_count = len(list(train_images.glob('*.jpg'))) + len(list(train_images.glob('*.png')))
    val_img_count = len(list(val_images.glob('*.jpg'))) + len(list(val_images.glob('*.png')))
    train_label_count = len(list(train_labels.glob('*.txt')))
    val_label_count = len(list(val_labels.glob('*.txt')))
    
    print(f"\n📊 Dataset Statistics:")
    print(f"  Training images: {train_img_count}")
    print(f"  Training labels: {train_label_count}")
    print(f"  Validation images: {val_img_count}")
    print(f"  Validation labels: {val_label_count}")
    
    if train_img_count != train_label_count:
        print(f"\n⚠️  Training images ({train_img_count}) != labels ({train_label_count})")
    else:
        print(f"\n✅ Training images and labels match!")
    
    if val_img_count != val_label_count:
        print(f"⚠️  Validation images ({val_img_count}) != labels ({val_label_count})")
    else:
        print(f"✅ Validation images and labels match!")
    
    # Warn about small dataset
    if train_img_count < 100:
        print(f"⚠️  Training set is very small ({train_img_count} images). Expect overfitting.")
    if val_img_count < 20:
        print(f"⚠️  Validation set is very small ({val_img_count} images). Metrics may be unreliable.")
    
    # Sample label file check
    sample_labels = list(train_labels.glob('*.txt'))
    if sample_labels:
        with open(sample_labels[0], 'r') as f:
            lines = f.readlines()
        print(f"\n📝 Sample Label File ({sample_labels[0].name}):")
        for line in lines[:3]:
            parts = line.strip().split()
            if len(parts) == 5:
                print(f"  ✅ suspicious person: {parts[1:5]}")
            else:
                print(f"  ❌ Invalid format: {line.strip()}")
    
    print("\n✅ Dataset verification complete!")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python verify_dataset.py <images_root> <labels_root>")
        sys.exit(1)

    images_root = sys.argv[1]
    labels_root = sys.argv[2]
    verify_dataset(images_root, labels_root)
