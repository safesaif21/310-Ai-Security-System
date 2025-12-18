"""Master grid recording management"""

import cv2
import logging
import numpy as np
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class MasterRecorder:
    """Manages grid recording of all cameras combined"""
    def __init__(self, log_manager, base_folder: str = "master", max_size_gb: float = 1.0):
        self.base_folder = Path(base_folder)
        self.max_size_bytes = max_size_gb * 1024 * 1024 * 1024
        self.writer: Optional[cv2.VideoWriter] = None
        self.start_time: float = 0
        self.current_file: Optional[Path] = None
        self.lock = threading.Lock()
        self.recording_started = False
        self.grid_width = 640
        self.grid_height = 480
        self.log_manager = log_manager
        
        if not self.base_folder.exists():
            self.base_folder.mkdir(parents=True)

    def _check_storage(self):
        """Delete oldest files if storage limit exceeded"""
        try:
            files = sorted(self.base_folder.glob("*.mp4"), key=os.path.getmtime)
            total_size = sum(f.stat().st_size for f in files)
            
            while total_size > self.max_size_bytes and len(files) > 1:
                oldest = files.pop(0)
                try:
                    size = oldest.stat().st_size
                    oldest.unlink()
                    total_size -= size
                    self.log_manager.add_log(f"Deleted old master recording: {oldest.name} (storage limit)", "info")
                except Exception as e:
                    logger.error(f"Error deleting file {oldest}: {e}")
        except Exception as e:
            logger.error(f"Error checking master storage: {e}")

    def start_recording(self):
        with self.lock:
            if not self.recording_started:
                self.log_manager.add_log("Master grid recording started", "info")
                self.recording_started = True
            self._start_new_file()

    def _start_new_file(self):
        try:
            if self.writer is not None:
                try:
                    self.writer.release()
                except Exception as e:
                    logger.error(f"Error releasing previous master writer: {e}")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H_%M_%S")
            filename = self.base_folder / f"master_{timestamp}.mp4"
            
            # Use 'H264' (Intel/Microsoft) instead of 'avc1' (OpenH264) for better Windows compatibility
            fourcc = cv2.VideoWriter_fourcc(*'H264')
            writer = cv2.VideoWriter(str(filename), fourcc, 20.0, (self.grid_width, self.grid_height))
            
            if not writer.isOpened():
                logger.error("Failed to create master video writer")
                return
            
            self.writer = writer
            self.start_time = time.time()
            self.current_file = filename
            
            self._check_storage()
        except Exception as e:
            logger.error(f"Error starting new master recording file: {e}")

    def write_grid_frame(self, camera_frames: Dict[int, np.ndarray], model_name: str, people_count: int):
        """Combine camera frames into 2x2 grid and write"""
        with self.lock:
            if self.writer is None:
                return

            try:
                if time.time() - self.start_time >= 60:
                    self._start_new_file()
                
                if self.writer and self.writer.isOpened():
                    grid = self._create_grid(camera_frames, model_name, people_count)
                    self.writer.write(grid)
            except Exception as e:
                logger.error(f"Error writing master frame: {e}")

    def _create_grid(self, camera_frames: Dict[int, np.ndarray], model_name: str, people_count: int) -> np.ndarray:
        """Create 2x2 grid from camera frames"""
        cell_width, cell_height = 320, 240
        grid = np.zeros((self.grid_height, self.grid_width, 3), dtype=np.uint8)
        
        camera_ids = sorted(camera_frames.keys())[:4]
        positions = [(0, 0), (cell_width, 0), (0, cell_height), (cell_width, cell_height)]
        
        for idx, camera_id in enumerate(camera_ids):
            if idx >= 4:
                break
            
            frame = camera_frames[camera_id]
            if frame is None:
                continue
            
            resized = cv2.resize(frame, (cell_width, cell_height))
            x, y = positions[idx]
            grid[y:y+cell_height, x:x+cell_width] = resized
        
        # Overlays in bottom-right (same style as timestamp)
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.5
        thickness = 1
        color = (255, 255, 255)
        padding = 5
        
        # Calculate positions from bottom-right
        model_text = f"Model: {model_name if model_name else 'None'}"
        people_text = f"People: {people_count}"
        
        (model_w, model_h), _ = cv2.getTextSize(model_text, font, scale, thickness)
        (people_w, people_h), _ = cv2.getTextSize(people_text, font, scale, thickness)
        
        # Model name on bottom line
        model_x = self.grid_width - model_w - padding - 5
        model_y = self.grid_height - padding - 5
        
        # People count above model name
        people_x = self.grid_width - people_w - padding - 5
        people_y = model_y - model_h - padding - 5
        
        # Draw with semi-transparent background (like timestamp)
        overlay = grid.copy()
        
        # Background for people count
        bg_x1 = people_x - padding
        bg_y1 = people_y - people_h - padding
        bg_x2 = people_x + people_w + padding
        bg_y2 = people_y + padding
        cv2.rectangle(overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
        
        # Background for model name
        bg_x1 = model_x - padding
        bg_y1 = model_y - model_h - padding
        bg_x2 = model_x + model_w + padding
        bg_y2 = model_y + padding
        cv2.rectangle(overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
        
        # Apply transparency
        alpha = 0.6
        cv2.addWeighted(overlay, alpha, grid, 1 - alpha, 0, grid)
        
        # Draw text
        cv2.putText(grid, people_text, (people_x, people_y), font, scale, color, thickness, cv2.LINE_AA)
        cv2.putText(grid, model_text, (model_x, model_y), font, scale, color, thickness, cv2.LINE_AA)
        
        return grid

    def stop_recording(self):
        with self.lock:
            try:
                if self.writer is not None:
                    self.writer.release()
                    self.writer = None
                if self.recording_started:
                    self.recording_started = False
                    self.log_manager.add_log("Master grid recording stopped", "info")
            except Exception as e:
                logger.error(f"Error stopping master recording: {e}")
