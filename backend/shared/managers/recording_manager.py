"""Individual camera recording management"""

import cv2
import logging
import os
import threading
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class RecordingManager:
    def __init__(self, log_manager, base_folder: str = "recordings", max_size_gb: float = 1.0):
        self.base_folder = Path(base_folder)
        self.max_size_bytes = max_size_gb * 1024 * 1024 * 1024
        self.writers: Dict[int, subprocess.Popen] = {}
        self.start_times: Dict[int, float] = {}
        self.current_files: Dict[int, Path] = {}
        self.camera_fps: Dict[int, float] = {}
        self.recording_started: Dict[int, bool] = {}
        self.camera_dims: Dict[int, tuple] = {}
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
                    self.log_manager.add_log(f"Deleted old recording: {oldest.name} (storage limit)", "info")
                except Exception as e:
                    logger.error(f"Error deleting file {oldest}: {e}")
        except Exception as e:
            logger.error(f"Error checking storage for camera {camera_id}: {e}")

    def start_recording(self, camera_id: int, width: int, height: int, fps: float = 20.0):
        with self.lock:
            if camera_id not in self.recording_started or not self.recording_started[camera_id]:
                # Force even dimensions for H.264 (FFmpeg requirement)
                target_height = min(height, 360)
                if target_height % 2 != 0: target_height -= 1
                
                scale = target_height / height
                target_width = int(width * scale)
                if target_width % 2 != 0: target_width -= 1
                
                self.log_manager.add_log(f"Recording started for camera {camera_id} at {fps:.1f} FPS ({width}x{height} -> {target_width}x{target_height})", "info")
                self.recording_started[camera_id] = True
                self.camera_fps[camera_id] = fps
                self.camera_dims[camera_id] = (target_width, target_height)
                
            width, height = self.camera_dims[camera_id]
            self._start_new_file(camera_id, width, height, fps)

    def _start_new_file(self, camera_id: int, width: int, height: int, fps: float):
        try:
            if camera_id in self.writers:
                try:
                    self.writers[camera_id].stdin.close()
                    self.writers[camera_id].wait(timeout=2)
                except Exception as e:
                    logger.error(f"Error closing previous ffmpeg process: {e}")
            
            folder = self._get_camera_folder(camera_id)
            timestamp = datetime.now().strftime("%Y%m%d_%H_%M_%S")
            filename = folder / f"rec_{timestamp}.mp4"
            
            # Using FFmpeg pipe for reliable H.264 encoding in Docker
            # This is much more reliable than cv2.VideoWriter for H.264
            command = [
                'ffmpeg',
                '-y',
                '-f', 'rawvideo',
                '-vcodec', 'rawvideo',
                '-s', f'{width}x{height}',
                '-pix_fmt', 'bgr24',
                '-r', str(fps),
                '-i', '-',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-preset', 'ultrafast',
                '-crf', '25',
                '-f', 'mp4',
                str(filename)
            ]
            
            # Redirect stderr to devnull to keep logs clean, or use a specific log file if debugging
            process = subprocess.Popen(
                command, 
                stdin=subprocess.PIPE, 
                stderr=subprocess.DEVNULL,
                bufsize=0
            )
            
            self.writers[camera_id] = process
            self.start_times[camera_id] = time.time()
            self.current_files[camera_id] = filename
            
            self._check_storage(camera_id)
        catch Exception as e:
            logger.error(f"Error starting new recording file for camera {camera_id}: {e}")

    def write_frame(self, camera_id: int, frame):
        with self.lock:
            if camera_id not in self.writers:
                return

            try:
                # auto-rotate files every 60 seconds
                if time.time() - self.start_times[camera_id] >= 60:
                    h, w = frame.shape[:2]
                    fps = self.camera_fps.get(camera_id, 30.0)
                    target_w, target_h = self.camera_dims.get(camera_id, (w, h))
                    self._start_new_file(camera_id, target_w, target_h, fps)
                
                if camera_id in self.writers:
                    target_w, target_h = self.camera_dims.get(camera_id, (None, None))
                    if target_w and target_h:
                        frame = cv2.resize(frame, (target_w, target_h))
                    
                    # Write frame to ffmpeg stdin
                    if self.writers[camera_id].poll() is None:
                        self.writers[camera_id].stdin.write(frame.tobytes())
            except Exception as e:
                logger.error(f"Error writing frame to recording: {e}")

    def stop_recording(self, camera_id: int):
        """Public method to stop recording for a camera"""
        with self.lock:
            self._stop_recording_internal(camera_id)

    def _stop_recording_internal(self, camera_id: int):
        """Internal method to stop recording (assumes lock is held)"""
        try:
            if camera_id in self.writers:
                try:
                    self.writers[camera_id].stdin.close()
                    self.writers[camera_id].wait(timeout=2)
                except: pass
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
