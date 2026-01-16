"""Individual camera recording management"""

import cv2
import logging
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class RecordingManager:
    def __init__(self, log_manager, base_folder: str = "recordings", max_size_gb: float = 1.0):
        self.base_folder = Path(base_folder)
        self.max_size_bytes = max_size_gb * 1024 * 1024 * 1024
        self.writers: Dict[int, cv2.VideoWriter] = {}
        self.start_times: Dict[int, float] = {}
        self.current_files: Dict[int, Path] = {}
        self.camera_fps: Dict[int, float] = {}
        self.recording_started: Dict[int, bool] = {}
        self.lock = threading.Lock()
        self.log_manager = log_manager
        
        if not self.base_folder.exists():
            self.base_folder.mkdir(parents=True)

    def _get_camera_folder(self, camera_id: int) -> Path:
        folder = self.base_folder / f"camera_{camera_id}"
        if not folder.exists():
            folder.mkdir(parents=True)
        return folder

    def _check_storage(self, camera_id: int):
        """Delete oldest files if storage limit exceeded"""
        try:
            folder = self._get_camera_folder(camera_id)
            files = sorted(folder.glob("*.mp4"), key=os.path.getmtime)
            
            total_size = sum(f.stat().st_size for f in files)
            
            while total_size > self.max_size_bytes and len(files) > 1:
                oldest = files.pop(0)
                try:
                    size = oldest.stat().st_size
                    oldest.unlink()
                    total_size -= size
                except Exception as e:
                    logger.error(f"Error deleting file {oldest}: {e}")
        except Exception as e:
            logger.error(f"Error checking storage for camera {camera_id}: {e}")

    def start_recording(self, camera_id: int, width: int, height: int, fps: float = 20.0):
        with self.lock:
            if camera_id not in self.recording_started or not self.recording_started[camera_id]:
                # Downscale to 360p (nHD) to drastically reduce file size (~640x360)
                target_height = min(height, 360)
                scale = target_height / height
                target_width = int(width * scale)
                
                self.log_manager.add_log(f"Recording started for camera {camera_id} at {fps:.1f} FPS ({width}x{height} -> {target_width}x{target_height})", "info")
                self.recording_started[camera_id] = True
                self.camera_fps[camera_id] = fps
                # Store target dimensions for this camera
                if not hasattr(self, 'camera_dims'): self.camera_dims = {}
                self.camera_dims[camera_id] = (target_width, target_height)
                
            width, height = self.camera_dims[camera_id]
            self._start_new_file(camera_id, width, height, fps)

    def _start_new_file(self, camera_id: int, width: int, height: int, fps: float):
        try:
            if camera_id in self.writers:
                try:
                    self.writers[camera_id].release()
                except Exception as e:
                    logger.error(f"Error releasing previous writer: {e}")
            
            folder = self._get_camera_folder(camera_id)
            timestamp = datetime.now().strftime("%Y%m%d_%H_%M_%S")
            filename = folder / f"rec_{timestamp}.mp4"
            
            # Use 'H264' (Intel/Microsoft) instead of 'avc1' (OpenH264) for better Windows compatibility
            fourcc = cv2.VideoWriter_fourcc(*'H264')
            writer = cv2.VideoWriter(str(filename), fourcc, fps, (width, height))
            
            if not writer.isOpened():
                logger.error(f"Failed to create video writer for camera {camera_id}")
                return
            
            self.writers[camera_id] = writer
            self.start_times[camera_id] = time.time()
            self.current_files[camera_id] = filename
            

            
            self._check_storage(camera_id)
        except Exception as e:
            logger.error(f"Error starting new recording file for camera {camera_id}: {e}")

    def write_frame(self, camera_id: int, frame):
        with self.lock:
            if camera_id not in self.writers:
                return

            try:
                if time.time() - self.start_times[camera_id] >= 60:
                    h, w = frame.shape[:2]
                    fps = self.camera_fps.get(camera_id, 30.0)
                    # Use stored target dims for new file creation
                    target_w, target_h = self.camera_dims.get(camera_id, (w, h))
                    self._start_new_file(camera_id, target_w, target_h, fps)
                
                if camera_id in self.writers and self.writers[camera_id].isOpened():
                    target_w, target_h = self.camera_dims.get(camera_id, None)
                    if target_w and target_h:
                        frame = cv2.resize(frame, (target_w, target_h))
                    self.writers[camera_id].write(frame)
            except Exception as e:
                logger.error(f"Error writing frame to recording for camera {camera_id}: {e}")

    def stop_recording(self, camera_id: int):
        """Public method to stop recording for a camera"""
        with self.lock:
            self._stop_recording_internal(camera_id)

    def _stop_recording_internal(self, camera_id: int):
        """Internal method to stop recording (assumes lock is held)"""
        try:
            if camera_id in self.writers:
                self.writers[camera_id].release()
                del self.writers[camera_id]
            if camera_id in self.start_times:
                del self.start_times[camera_id]
            if camera_id in self.current_files:
                del self.current_files[camera_id]
            if camera_id in self.recording_started:
                self.recording_started[camera_id] = False
                self.log_manager.add_log(f"Recording stopped for camera {camera_id}", "info")
        except Exception as e:
            logger.error(f"Error stopping recording for camera {camera_id}: {e}")

    def stop_all(self):
        """Stop all recordings"""
        with self.lock:
            for cid in list(self.writers.keys()):
                self._stop_recording_internal(cid)
