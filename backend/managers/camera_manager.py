"""Camera management"""

import cv2
import logging
import platform
import threading
import time
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class CameraManager:
    def __init__(self, log_manager):
        self.cameras: Dict[int, cv2.VideoCapture] = {}
        self.locks: Dict[int, threading.Lock] = {}
        self.settings: Dict[int, dict] = {}
        self.people_counts: Dict[int, int] = {}
        self.weapon_detected: Dict[int, bool] = {}
        self.last_frame_time: Dict[int, float] = {}
        self.stats_lock = threading.Lock()
        self.log_manager = log_manager
        
        self.is_windows = platform.system() == "Windows"
        self.is_mac = platform.system() == "Darwin"
        
        logger.info(f"🖥️  Platform detected: {platform.system()}")

    def get_camera(self, camera_id: int) -> Tuple[Optional[cv2.VideoCapture], Optional[threading.Lock]]:
        if camera_id not in self.cameras:
            self.log_manager.add_log(f"Opening camera {camera_id}...", "info")
            
            try:
                if self.is_windows:
                    cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
                elif self.is_mac:
                    cap = cv2.VideoCapture(camera_id, cv2.CAP_AVFOUNDATION)
                else:
                    cap = cv2.VideoCapture(camera_id)

                if not cap.isOpened():
                    self.log_manager.add_log(f"Failed to open camera {camera_id}", "error")
                    return None, None
                
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
                
                self.cameras[camera_id] = cap
                self.locks[camera_id] = threading.Lock()
                self.last_frame_time[camera_id] = time.time()
                
                with self.stats_lock:
                    self.people_counts[camera_id] = 0
                    self.weapon_detected[camera_id] = False
                
                if camera_id not in self.settings:
                    self.settings[camera_id] = {
                        "brightness": 50,
                        "contrast": 50,
                        "saturation": 50,
                        "gamma": 50
                    }
                
                self.log_manager.add_log(f"Camera {camera_id} connected", "success")
            except Exception as e:
                logger.error(f"Error opening camera {camera_id}: {e}")
                self.log_manager.add_log(f"Error opening camera {camera_id}: {str(e)}", "error")
                return None, None
        
        return self.cameras[camera_id], self.locks[camera_id]

    def release_camera(self, camera_id: int):
        if camera_id in self.cameras:
            try:
                self.cameras[camera_id].release()
                del self.cameras[camera_id]
                if camera_id in self.locks:
                    del self.locks[camera_id]
                self.log_manager.add_log(f"Released camera {camera_id}", "info")
            except Exception as e:
                logger.error(f"Error releasing camera {camera_id}: {e}")

    def release_all(self):
        for camera_id in list(self.cameras.keys()):
            self.release_camera(camera_id)

    def update_stats(self, camera_id: int, people_count: int, weapon_detected: bool):
        with self.stats_lock:
            prev_count = self.people_counts.get(camera_id, 0)
            prev_weapon = self.weapon_detected.get(camera_id, False)
            
            self.people_counts[camera_id] = people_count
            self.weapon_detected[camera_id] = weapon_detected
            
            if people_count > 0 and prev_count == 0:
                self.log_manager.add_log(f"Person detected on Camera {camera_id} ({people_count})", "detection")
            
            if weapon_detected and not prev_weapon:
                self.log_manager.add_log(f"WEAPON DETECTED on Camera {camera_id}", "warning")

    def get_stats(self):
        with self.stats_lock:
            total_people = sum(self.people_counts.values())
            any_weapon = any(self.weapon_detected.values())
            
            threat_level = 0
            if total_people > 0:
                threat_level += min(total_people, 3)
            if any_weapon:
                threat_level += 5
            if total_people > 1 and any_weapon:
                threat_level += 2
            
            return {
                "people_count": total_people,
                "weapon_detected": any_weapon,
                "threat_level": min(threat_level, 10)
            }
