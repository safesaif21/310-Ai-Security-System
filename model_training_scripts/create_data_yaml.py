import os
import yaml

def create_data_yaml(base_path):
    """
    Dynamically generate data.yaml for YOLOv8 with selected COCO classes
    and a new custom class 'sus person', specifying separate labels folder.
    """
    # Map of original COCO IDs to names
    coco_classes = {
            0: 'person',
            1: 'sus person'}

    # YOLO requires contiguous 0-based indices for training
    classes = list(coco_classes.values())
    names_dict = {i: name for i, name in enumerate(classes)}

    # Absolute paths for images and labels
    images_train = os.path.abspath(os.path.join(base_path, "images", "split", "train")).replace("\\", "/")
    images_val = os.path.abspath(os.path.join(base_path, "images", "split", "val")).replace("\\", "/")

    data_yaml = {
        "train": images_train,
        "val": images_val,
        "nc": len(classes),
        "names": names_dict
    }

    # Save to file
    yaml_path = os.path.join(base_path, "data.yaml")
    os.makedirs(os.path.dirname(yaml_path), exist_ok=True)
    with open(yaml_path, "w") as f:
        yaml.dump(data_yaml, f)

    print(f"✅ data.yaml created at: {yaml_path}")
    print(f"📝 Class indices in data.yaml: {names_dict}")
    return yaml_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python create_data_yaml.py <path_to_dataset_root>")
        sys.exit(1)

    dataset_root = sys.argv[1]
    create_data_yaml(dataset_root)
