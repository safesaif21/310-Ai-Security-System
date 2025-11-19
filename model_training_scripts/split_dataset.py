import os
import shutil
import random
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python split_dataset.py <path_to_original_images>")
        sys.exit(1)

    src_folder = sys.argv[1]
    if not os.path.exists(src_folder):
        print(f"❌ Source folder not found: {src_folder}")
        sys.exit(1)

    images_folder = os.path.join(os.path.dirname(src_folder), "images")
    os.makedirs(images_folder, exist_ok=True)

    split_folder = os.path.join(images_folder, "split")
    os.makedirs(split_folder, exist_ok=True)

    train_folder = os.path.join(split_folder, "train")
    val_folder = os.path.join(split_folder, "val")

    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(val_folder, exist_ok=True)

    # create 'labels' directory inside the original image folder and make its split subdirs
    labels_root = os.path.join(os.path.dirname(src_folder), "labels")
    os.makedirs(labels_root, exist_ok=True)

    split_labels_folder = os.path.join(labels_root, "split")
    os.makedirs(split_labels_folder, exist_ok=True)

    train_labels = os.path.join(split_labels_folder, "train")
    val_labels = os.path.join(split_labels_folder, "val")

    os.makedirs(train_labels, exist_ok=True)
    os.makedirs(val_labels, exist_ok=True)
    
    # Gather all image files
    images = [
        f for f in os.listdir(src_folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    if not images:
        print("⚠️ No images found in source folder.")
        sys.exit(0)

    # Shuffle and split
    random.seed(42)
    random.shuffle(images)
    split_idx = int(0.8 * len(images))
    train_images = images[:split_idx]
    val_images = images[split_idx:]

    # Copy images
    for img in train_images:
        shutil.copy(os.path.join(src_folder, img), os.path.join(train_folder, img))

    for img in val_images:
        shutil.copy(os.path.join(src_folder, img), os.path.join(val_folder, img))

    print(f"✅ Dataset split complete.")
    print(f"📂 Train folder: {train_folder} ({len(train_images)} images)")
    print(f"📂 Val folder:   {val_folder} ({len(val_images)} images)")
    print(f"📊 Total: {len(images)} images")

if __name__ == "__main__":
    main()
