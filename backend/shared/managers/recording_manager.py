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

import subprocess

class RecordingManager:
    def __init__(self, log_manager, base_folder: str = "recordings", max_size_gb: float = 1.0, rotation_seconds: int = 60):
        self.base_folder = Path(base_folder)
        self.max_size_bytes = max_size_gb * 1024 * 1024 * 1024
        self.rotation_seconds = rotation_seconds
        self.writers: Dict[int, subprocess.Popen] = {}
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
                    self.log_manager.add_log(f"Deleted old recording: {oldest.name} (storage limit)", "info")
                except Exception as e:
                    logger.error(f"Error deleting file {oldest}: {e}")
        except Exception as e:
            logger.error(f"Error checking storage for camera {camera_id}: {e}")

    def start_recording(self, camera_id: int, width: int, height: int, fps: float = 20.0):
        with self.lock:
            if camera_id not in self.recording_started or not self.recording_started[camera_id]:
                # Force even dimensions for H.264
                target_height = min(height, 360)
                if target_height % 2 != 0: target_height -= 1
                
                scale = target_height / height
                target_width = int(width * scale)
                if target_width % 2 != 0: target_width -= 1
                
                self.log_manager.add_log(f"Recording started for camera {camera_id} at {fps:.1f} FPS ({width}x{height} -> {target_width}x{target_height})", "info")
                self.recording_started[camera_id] = True
                self.camera_fps[camera_id] = fps
                if not hasattr(self, 'camera_dims'): self.camera_dims = {}
                self.camera_dims[camera_id] = (target_width, target_height)
                
            width, height = self.camera_dims[camera_id]
            self._start_new_file(camera_id, width, height, fps)

    def _start_new_file(self, camera_id: int, width: int, height: int, fps: float):
        try:
            if camera_id in self.writers:
                try:
                    self.writers[camera_id].stdin.close()
                    self.writers[camera_id].wait()
                except Exception as e:
                    logger.error(f"Error closing previous ffmpeg process: {e}")
            
            folder = self._get_camera_folder(camera_id)
            timestamp = datetime.now().strftime("%Y%m%d_%H_%M_%S")
            filename = folder / f"rec_{timestamp}.mp4"
            
            # Using FFmpeg pipe for reliable H.264 encoding in Docker
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
                '-f', 'mp4',
                str(filename)
            ]
            
            # Redirect stderr to a log file instead of a pipe to prevent hanging
            ffmpeg_log = folder / f"rec_{timestamp}.log"
            with open(ffmpeg_log, "w") as f_log:
                process = subprocess.Popen(
                    command, 
                    stdin=subprocess.PIPE, 
                    stderr=f_log,
                    bufsize=0
                )
            
            self.writers[camera_id] = process
            self.start_times[camera_id] = time.time()
            self.current_files[camera_id] = filename
            
            self._check_storage(camera_id)
            self.log_manager.add_log(f"Recording file created: {filename.name} ({width}x{height})", "info")
            logger.info(f"FFmpeg process started for cam {camera_id}, pid: {process.pid}")
        except Exception as e:
            logger.error(f"Error starting new recording file for camera {camera_id}: {e}")

    def write_frame(self, camera_id: int, frame):
        with self.lock:
            if camera_id not in self.writers:
                return

            try:
                # auto-rotate files
                if time.time() - self.start_times[camera_id] >= self.rotation_seconds:
                    h, w = frame.shape[:2]
                    fps = self.camera_fps.get(camera_id, 30.0)
                    target_w, target_h = self.camera_dims.get(camera_id, (w, h))
                    self._start_new_file(camera_id, target_w, target_h, fps)
                
                if camera_id in self.writers:
                    target_w, target_h = self.camera_dims.get(camera_id, (None, None))
                    if target_w and target_h:
                        frame = cv2.resize(frame, (target_w, target_h))
                    
                    # Add security-style timestamp overlay
                    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    label = f"SAFE-CAM {camera_id} | {timestamp_str}"
                    font = cv2.FONT_HERSHEY_DUPLEX
                    font_scale = 0.5
                    thickness = 1
                    
                    # Position: Top-Left
                    pos = (15, 30)
                    
                    # Measure text for background rectangle
                    (w_text, h_text), baseline = cv2.getTextSize(label, font, font_scale, thickness)
                    
                    # Draw semi-transparent background for text
                    overlay = frame.copy()
                    cv2.rectangle(overlay, (pos[0]-5, pos[1]-h_text-10), (pos[0]+w_text+10, pos[1]+10), (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
                    
                    # Draw the text
                    cv2.putText(frame, label, pos, font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
                    
                    # Write frame to ffmpeg stdin
                    self.writers[camera_id].stdin.write(frame.tobytes())
            except Exception as e:
                logger.error(f"Error writing frame to recording: {e}")

    def stop_recording(self, camera_id: int):
        with self.lock:
            self._stop_recording_internal(camera_id)

    def _stop_recording_internal(self, camera_id: int):
        try:
            if camera_id in self.writers:
                self.writers[camera_id].stdin.close()
                self.writers[camera_id].wait()
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
