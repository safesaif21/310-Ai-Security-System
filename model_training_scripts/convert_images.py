import os
import sys
from PIL import Image
import pillow_heif

# === CONFIGURATION ===
YOLO_IMAGE_SIZE = (640, 640)  # Standard YOLO image size (width, height)
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".heic"}


def convert_images_to_jpeg(input_folder, output_folder, size):
    os.makedirs(output_folder, exist_ok=True)
    count = 0

    for filename in os.listdir(input_folder):
        ext = os.path.splitext(filename.lower())[1]
        if ext not in ALLOWED_EXTENSIONS:
            continue

        input_path = os.path.join(input_folder, filename)
        output_filename = "image" + str(count) + ".jpg"
        output_path = os.path.join(output_folder, output_filename)

        try:
            # Handle HEIC images
            if ext == ".heic":
                heif_file = pillow_heif.read_heif(input_path)
                image = Image.frombytes(
                    heif_file.mode, heif_file.size, heif_file.data
                )
            else:
                image = Image.open(input_path)

            # Convert to RGB (important for YOLO compatibility)
            image = image.convert("RGB")

            # Resize (stretched to YOLO size)
            image = image.resize(size, Image.LANCZOS)

            # Save as JPEG
            image.save(output_path, "JPEG", quality=95)
            count += 1
            print(f"✅ Converted: {filename} → {output_filename}")

        except Exception as e:
            print(f"❌ Failed to process {filename}: {e}")

    print(f"\nDone! {count} images converted and resized.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_and_resize_for_yolo.py <input_folder>")
        sys.exit(1)

    INPUT_FOLDER = sys.argv[1]
    OUTPUT_FOLDER = os.path.join(os.path.dirname(INPUT_FOLDER), "converted_images")

    convert_images_to_jpeg(INPUT_FOLDER, OUTPUT_FOLDER, YOLO_IMAGE_SIZE)
