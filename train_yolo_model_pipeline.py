import subprocess
import sys
import os

input_folder = sys.argv[1]
name = sys.argv[2]

def step1():
    if len(sys.argv) < 3:
        print("Usage: python pipeline.py <path_to_original_images> <model_name>")
        sys.exit(1)

    convert_script = os.path.join("model_training_scripts", "convert_images.py")

    if not os.path.exists(convert_script):
        print(f"❌ Could not find script at {convert_script}")
        sys.exit(1)

    print(f"🚀 Starting data preprocessing pipeline...")
    print(f"📁 Input images: {input_folder}")
    print(f"⚙️ Running convert_images.py...")

    try:
        subprocess.run(
            [sys.executable, convert_script, input_folder],
            check=True
        )
        print(f"✅ Image conversion completed successfully → {os.path.join(os.path.dirname(input_folder), 'converted_images')}\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while running convert_images.py: {e}")
        sys.exit(1)

def step2():
    split_script = os.path.join("model_training_scripts", "split_dataset.py")
    converted_folder = os.path.join(os.path.dirname(input_folder), "converted_images")
    print(f"⚙️ Running split_dataset.py on {converted_folder}...")
    subprocess.run([sys.executable, split_script, converted_folder], check=True)
    print("✅ Dataset splitting completed successfully!\n")

def step3():
    
    print("\n📝 Please copy your annotated .txt files into the respective folders.")

    # Step 3 confirmation
    while True:
        proceed = input("Once done, type 'y' to continue: ").strip().lower()
        if proceed == 'y':
            break
        else:
            print("Please type 'y' when you have finished copying the labels.")

def step4(base_path):
    verify_script = os.path.join("model_training_scripts", "verify_dataset.py")
    
    # Paths for images and labels
    images_root = os.path.join(base_path, "images", "split")
    labels_root = os.path.join(base_path, "labels", "split")

    if not os.path.exists(images_root) or not os.path.exists(labels_root):
        print("❌ Images or labels root folder not found!")
        return

    # 1️⃣ Run dataset verification
    print("⚙️ Running verify_dataset.py...")
    subprocess.run([sys.executable, verify_script, images_root, labels_root], check=True)

    print("✅ Step 4 completed: Dataset verified and labels updated.\n")

# === Step 5: Generate data.yaml by calling create_data_yaml.py ===
def step5():
    create_yaml_script = os.path.join("model_training_scripts", "create_data_yaml.py")
    
    if not os.path.exists(create_yaml_script):
        print(f"❌ Could not find script at {create_yaml_script}")
        sys.exit(1)

    base_path = os.path.dirname(input_folder)  # e.g., images/saif

    print(f"⚙️ Running create_data_yaml.py to generate data.yaml in model_training_scripts...")

    try:
        subprocess.run(
            [sys.executable, create_yaml_script, base_path],
            check=True
        )
        print("✅ data.yaml generated successfully!\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while running create_data_yaml.py: {e}")
        sys.exit(1)

# === Step 6: Train YOLO model ===
def step6(data_yaml_path, model_name):
    train_script = os.path.join("model_training_scripts", "train_model.py")
    
    if not os.path.exists(train_script):
        print(f"❌ Could not find training script at {train_script}")
        sys.exit(1)

    print(f"⚙️ Running train_yolo_model.py with data.yaml={data_yaml_path}...")
    
    try:
        subprocess.run(
            [sys.executable, train_script, data_yaml_path, model_name],
            check=True
        )
        print("✅ YOLO model training completed successfully!\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while running train_yolo_model.py: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # === Normal full pipeline ===
    # step1() # convert images to jpeg and resize
    # step2() # split dataset
    # step3()  # will wait for user to copy labels
    # step4(os.path.dirname(input_folder)) # verify dataset and update class numbers
    # step5() # generate data.yaml

    data_yaml_path = os.path.join(os.path.dirname(input_folder), "data.yaml")
    step6(data_yaml_path, name) # train YOLO model
    print("🏁 Full YOLO data preprocessing pipeline completed successfully!")
