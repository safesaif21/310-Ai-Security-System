"""Configuration constants for the backend"""

# Folders
MODELS_FOLDER = "yolo_models"
RECORDINGS_FOLDER = "recordings"
MASTER_FOLDER = "master"
LOGS_FOLDER = "logs"

# Storage limits (GB)
RECORDING_SIZE_LIMIT_GB = 1.0
MASTER_SIZE_LIMIT_GB = 1.0

# Camera settings
MAX_CAMERAS = 10
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Recording settings
RECORDING_FPS = 20
RECORDING_ROTATION_SECONDS = 60
JPEG_QUALITY = 85

# Master recording settings
MASTER_WIDTH = 640
MASTER_HEIGHT = 480
MASTER_CELL_WIDTH = 320
MASTER_CELL_HEIGHT = 240

# Detection settings
MAX_CONSECUTIVE_FAILURES = 30
