import cv2
import time

def test_camera(camera_id, width=1920, height=1080, target_fps=60, duration=5):
    print(f"\n=== Testing Camera {camera_id} ===")
    cap = cv2.VideoCapture(camera_id)

    if not cap.isOpened():
        print(f"❌ Could not open camera {camera_id}")
        return

    # Try to set resolution and FPS
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, target_fps)

    # Read back actual settings
    actual_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Requested: {width}x{height} @ {target_fps} FPS")
    print(f"Actual:    {actual_w}x{actual_h} @ {actual_fps} FPS (reported by driver)")

    # Measure real capture FPS
    frame_count = 0
    start_time = time.time()

    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            continue
        frame_count += 1

    elapsed = time.time() - start_time
    real_fps = frame_count / elapsed
    print(f"Measured FPS over {duration:.1f}s: {real_fps:.2f}")

    cap.release()

if __name__ == "__main__":
    # Test all connected cameras (0, 1, 2, etc.)
    for cam_id in range(3):  # adjust the range if you have more cameras
        test_camera(cam_id)
