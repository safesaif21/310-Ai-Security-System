#!/usr/bin/env python3
"""
Simple example of using the human detection function
"""

from human_detection_test import load_yolo_model, detect_humans_in_image
import os


def simple_human_check(image_path):
    """
    Simple function to check if an image contains humans
    
    Args:
        image_path (str): Path to the image
        
    Returns:
        bool: True if humans are detected, False otherwise
    """
    # Load the model (will download if not present)
    model = load_yolo_model("yolov8n.pt")
    
    if model is None:
        print("Failed to load model")
        return False
    
    # Detect humans
    results = detect_humans_in_image(model, image_path)
    
    if results is None:
        print("Failed to process image")
        return False
    
    return results['humans_detected']


def batch_check_images(image_folder):
    """
    Check multiple images in a folder for humans
    
    Args:
        image_folder (str): Path to folder containing images
    """
    # Supported image formats
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
    
    # Load model once for all images
    model = load_yolo_model("yolov8n.pt")
    if model is None:
        return
    
    print(f"🔍 Checking images in: {image_folder}")
    print("-" * 50)
    
    image_files = [f for f in os.listdir(image_folder) 
                   if f.lower().endswith(supported_formats)]
    
    if not image_files:
        print("No supported image files found")
        return
    
    human_images = []
    no_human_images = []
    
    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)
        results = detect_humans_in_image(model, image_path)
        
        if results is not None:
            if results['humans_detected']:
                human_images.append((image_file, results['human_count']))
                status = f"✅ {results['human_count']} humans"
            else:
                no_human_images.append(image_file)
                status = "❌ No humans"
            
            print(f"{image_file:30} | {status}")
    
    print("\n📊 Summary:")
    print(f"Images with humans: {len(human_images)}")
    print(f"Images without humans: {len(no_human_images)}")


if __name__ == "__main__":
    # Example usage
    print("Simple Human Detection Example")
    print("=" * 40)
    
    # Example 1: Check a single image
    image_path = input("Enter path to an image file (or press Enter to skip): ").strip()
    
    if image_path and os.path.exists(image_path):
        print(f"\nChecking: {image_path}")
        has_humans = simple_human_check(image_path)
        print(f"Result: {'Humans detected!' if has_humans else 'No humans detected'}")
    
    # Example 2: Batch check images in a folder
    folder_path = input("\nEnter path to image folder (or press Enter to skip): ").strip()
    
    if folder_path and os.path.exists(folder_path):
        batch_check_images(folder_path)
    
    if not image_path and not folder_path:
        print("\nNo paths provided. Here's how to use the functions:")
        print("\n# Check single image:")
        print("has_humans = simple_human_check('path/to/image.jpg')")
        print("\n# Check multiple images:")
        print("batch_check_images('path/to/image/folder')")