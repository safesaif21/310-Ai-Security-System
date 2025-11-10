import os
import shutil
import random

# Paths
src_folder = "data/converted_images"  # source folder with all JPGs
train_folder = "data/images/train"
val_folder = "data/images/val"

# Create target folders if they don't exist
os.makedirs(train_folder, exist_ok=True)
os.makedirs(val_folder, exist_ok=True)

# Get all images
images = [f for f in os.listdir(src_folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

# Shuffle the list to randomize
random.seed(42)
random.shuffle(images)

# Split 90% train, 10% validation
split_idx = int(0.9 * len(images))
train_images = images[:split_idx]
val_images = images[split_idx:]

# Copy images to their respective folders
for img in train_images:
    shutil.copy(os.path.join(src_folder, img), os.path.join(train_folder, img))

for img in val_images:
    shutil.copy(os.path.join(src_folder, img), os.path.join(val_folder, img))

print(f"Total images: {len(images)}")
print(f"Train: {len(train_images)} images")
print(f"Validation: {len(val_images)} images")
