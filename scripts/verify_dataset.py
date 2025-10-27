import os
from pathlib import Path

def verify_dataset():
    """Verify dataset structure and files"""
    
    base_path = Path('./data')
    
    # Check directories exist
    train_images = base_path / 'images' / 'train'
    val_images = base_path / 'images' / 'val'
    train_labels = base_path / 'labels' / 'train'
    val_labels = base_path / 'labels' / 'val'
    
    print("🔍 Verifying dataset structure...\n")
    
    # Check if directories exist
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
    
    # Check if images and labels match
    if train_img_count != train_label_count:
        print(f"\n⚠️  WARNING: Training images ({train_img_count}) != labels ({train_label_count})")
    else:
        print(f"\n✅ Training images and labels match!")
    
    if val_img_count != val_label_count:
        print(f"⚠️  WARNING: Validation images ({val_img_count}) != labels ({val_label_count})")
    else:
        print(f"✅ Validation images and labels match!")
    
    # Check minimum dataset size
    print(f"\n📈 Dataset Size Check:")
    if train_img_count < 100:
        print(f"⚠️  Training set is small ({train_img_count} images). Recommend 500+ for production.")
    else:
        print(f"✅ Training set size is good ({train_img_count} images)")
    
    if val_img_count < 20:
        print(f"⚠️  Validation set is small ({val_img_count} images). Recommend 100+ for production.")
    else:
        print(f"✅ Validation set size is good ({val_img_count} images)")
    
    # Verify a sample label file
    sample_labels = list(train_labels.glob('*.txt'))
    if sample_labels:
        with open(sample_labels[0], 'r') as f:
            lines = f.readlines()
        
        print(f"\n📝 Sample Label File ({sample_labels[0].name}):")
        for line in lines[:3]:  # Show first 3 lines
            parts = line.strip().split()
            if len(parts) == 5:
                class_id = int(parts[0])
                if class_id in [0, 1, 2]:
                    class_names = ['person', 'weapon', 'object']
                    print(f"  ✅ {class_names[class_id]}: {parts[1:5]}")
                else:
                    print(f"  ❌ Invalid class ID: {class_id} (should be 0, 1, or 2)")
            else:
                print(f"  ❌ Invalid format: {line.strip()}")
    
    print("\n✅ Dataset verification complete!")
    return True

if __name__ == '__main__':
    verify_dataset()