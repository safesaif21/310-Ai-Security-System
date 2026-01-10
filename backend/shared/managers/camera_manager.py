"""Camera management"""

import cv2
import logging
import platform
import threading
import time
from typing import Dict, Optional, Tuple, List

logger = logging.getLogger(__name__)

class CameraManager:
    def __init__(self, log_manager=None):
        self.cameras: Dict[int, cv2.VideoCapture] = {}
        self.locks: Dict[int, threading.Lock] = {}
        self.settings: Dict[int, dict] = {}
        self.people_counts: Dict[int, int] = {}
        self.weapon_detected: Dict[int, bool] = {}
        self.last_frame_time: Dict[int, float] = {}
        self.stats_lock = threading.Lock()
        
        # Detection persistence and cooldown
        self.people_streak: Dict[int, int] = {}
        self.weapon_streak: Dict[int, int] = {}
        self.last_log_times: Dict[int, Dict[str, float]] = {}
        
        self.init_lock = threading.Lock()  # Add lock for camera initialization
        self.log_manager = log_manager
        
        self.is_windows = platform.system() == "Windows"
        self.is_mac = platform.system() == "Darwin"
        
        # Define available backends based on platform
        self.backends = self._get_platform_backends()
        
        logger.info(f"🖥️  Platform detected: {platform.system()}")

    def _log(self, message: str, level: str = "info"):
        """Internal helper to log to log_manager if available"""
        logger.info(message) if level == "info" else logger.warning(message)
        if self.log_manager:
            try:
                self.log_manager.add_log(message, level)
            except Exception as e:
                logger.error(f"Failed to send log to log_manager: {e}")

    def _get_platform_backends(self) -> List[Tuple[int, str]]:
        """Get list of backends to try for this platform"""
        if self.is_windows:
            return [
                (cv2.CAP_DSHOW, "DirectShow"),
                (cv2.CAP_MSMF, "Media Foundation"),
            ]
        elif self.is_mac:
            return [(cv2.CAP_AVFOUNDATION, "AVFoundation")]
        else:
            return [
                (cv2.CAP_V4L2, "V4L2"),
                (cv2.CAP_ANY, "Default")
            ]

    def _try_open_camera(self, camera_id: int, timeout: float = 2.0) -> Optional[cv2.VideoCapture]:
        """Try to open camera with all available backends"""
        # Special handling for camera 0 on Windows - often needs MSMF
        backends = self.backends
        if self.is_windows and camera_id == 0:
            backends = [(cv2.CAP_MSMF, "Media Foundation"), (cv2.CAP_DSHOW, "DirectShow")]
        
        for backend_id, backend_name in backends:

            # Try up to 2 times for each backend (in case camera is releasing)
            for attempt in range(2):
                try:
                    if attempt > 0:
                        logger.debug(f"Retry attempt {attempt + 1} for camera {camera_id} with {backend_name}")
                        time.sleep(0.5)  # Wait before retry
                    else:
                        logger.debug(f"Trying {backend_name} for camera {camera_id}...")
                
                        cap = cv2.VideoCapture(camera_id, backend_id)
                        
                        # Longer timeout for MSMF on camera 0
                        if backend_id == cv2.CAP_MSMF and camera_id == 0:
                            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 2000)
                        else:
                            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 500)
                        
                        if cap.isOpened():
                            # Quick frame test
                            ret = cap.grab()
                            if ret:
                                logger.info(f"✓ Camera {camera_id} opened with {backend_name}")
                                return cap
                            else:
                                logger.debug(f"{backend_name}: grab() failed")
                                cap.release()
                        else:
                            logger.debug(f"{backend_name}: not opened")
                            cap.release()
                            
                except Exception as e:
                    logger.debug(f"{backend_name} exception: {e}")
        
        return None

    def detect_available_cameras(self, max_cameras: int = 3) -> List[int]:
        """Detect all available cameras"""
        # FAST PATH: If fixed count is set, skip detection
        from backend.shared.config import settings
        if settings.fixed_camera_count is not None:
            count = settings.fixed_camera_count
            logger.info(f"⚡ Using fixed camera count: {count}")
            self._log(f"Using fixed camera count: {count}", "info")
            return list(range(count))

        available_indices = []
        self._log("🔍 Scanning for cameras...", "info")
        logger.info("Starting camera detection...")
        
        start_time = time.time()
        
        for i in range(max_cameras):
            # Only log debug for scanning to reduce noise
            cap = self._try_open_camera(i, timeout=1.5)
            
            if cap is not None:
                try:
                    # Verify we can actually get a frame
                    ret, frame = cap.retrieve()
                    if ret and frame is not None and frame.size > 0:
                        h, w = frame.shape[:2]
                        available_indices.append(i)
                        logger.info(f"✅ Camera {i} detected ({w}x{h})")
                        self._log(f"Camera {i} detected ({w}x{h})", "success")
                    else:
                        logger.debug(f"Camera {i} opened but frame invalid")
                except Exception as e:
                    logger.debug(f"Camera {i} error during verification: {e}")
                finally:
                    # Properly release and wait for Windows to free the device
                    cap.release()
                    if self.is_windows:
                        time.sleep(0.5)  # Windows needs time to release camera
            
            # Very small delay to prevent camera conflicts
            time.sleep(0.02)
        
        elapsed = time.time() - start_time
        logger.info(f"Camera scan complete in {elapsed:.1f}s - Found: {available_indices}")
        
        if available_indices:
            self._log(
                f"✅ Found {len(available_indices)} camera(s) in {elapsed:.1f}s", 
                "success"
            )
        else:
            self._log("⚠️  No cameras detected", "warning")
        
        return available_indices

    def get_camera(self, camera_id: int) -> Tuple[Optional[cv2.VideoCapture], Optional[threading.Lock]]:
        """Get or open a camera"""
        with self.init_lock:  # Thread-safe camera initialization
            # Return existing camera if already open
            if camera_id in self.cameras:
                return self.cameras[camera_id], self.locks[camera_id]
            
            self._log(f"Opening camera {camera_id}...", "info")
            
            cap = self._try_open_camera(camera_id, timeout=3.0)
            
            if cap is None:
                self._log(f"Failed to open camera {camera_id}", "error")
                return None, None
            
            try:
                # Configure camera
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
                
                # Store camera
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
                else:
                    # Apply existing settings
                    self.update_settings(camera_id, self.settings[camera_id])
                
                self._log(f"Camera {camera_id} connected", "success")
                
                return self.cameras[camera_id], self.locks[camera_id]
                
            except Exception as e:
                logger.error(f"Error configuring camera {camera_id}: {e}")
                cap.release()
                return None, None
        
        # This line should NEVER be reached, but just in case
        return None, None

    def set_camera_property(self, camera_id: int, prop_id: int, value: float):
        """Set a hardware camera property"""
        with self.init_lock:
            if camera_id in self.cameras:
                try:
                    cap = self.cameras[camera_id]
                    # Map 0-100 to hardware values (often -255 to 255 or 0-255)
                    # For brightness/contrast, we'll try to map 0-100 to 0-255 for now
                    hw_value = value * 2.55
                    cap.set(prop_id, hw_value)
                    self._log(f"Set camera {camera_id} property {prop_id} to {value}", "debug")
                    return True
                except Exception as e:
                    logger.error(f"Error setting camera property: {e}")
        return False

    def update_settings(self, camera_id: int, settings: dict):
        """Update multiple camera settings at once"""
        if camera_id not in self.settings:
            self.settings[camera_id] = {}
        
        self.settings[camera_id].update(settings)
        
        results = []
        if "brightness" in settings:
            results.append(self.set_camera_property(camera_id, cv2.CAP_PROP_BRIGHTNESS, settings["brightness"]))
        if "contrast" in settings:
            results.append(self.set_camera_property(camera_id, cv2.CAP_PROP_CONTRAST, settings["contrast"]))
        if "saturation" in settings:
            results.append(self.set_camera_property(camera_id, cv2.CAP_PROP_SATURATION, settings["saturation"]))
            
        return all(results)

    def release_camera(self, camera_id: int):
        """Release a specific camera"""
        with self.init_lock:  # Thread-safe camera release
            if camera_id in self.cameras:
                try:
                    self.cameras[camera_id].release()
                    del self.cameras[camera_id]
                    if camera_id in self.locks:
                        del self.locks[camera_id]
                    self._log(f"Released camera {camera_id}", "info")
                    
                    # Windows needs time to fully release the device
                    if self.is_windows:
                        time.sleep(0.1)
                except Exception as e:
                    logger.error(f"Error releasing camera {camera_id}: {e}")

    def release_all(self):
        """Release all cameras"""
        for camera_id in list(self.cameras.keys()):
            self.release_camera(camera_id)

    def update_stats(self, camera_id: int, people_count: int, weapon_detected: bool):
        """Update detection statistics for a camera with persistence and cooldown"""
        with self.stats_lock:
            now = time.time()
            if camera_id not in self.last_log_times:
                self.last_log_times[camera_id] = {"person": 0, "weapon": 0}
            
            # --- Person Detection Persistence & Cooldown ---
            current_people_streak = self.people_streak.get(camera_id, 0)
            if people_count > 0:
                current_people_streak += 1
            else:
                current_people_streak = 0
            self.people_streak[camera_id] = current_people_streak
            
            # Only log if person count changed AND we have persistence AND cooldown passed
            if current_people_streak == 10: # Log after 10 consecutive frames
                last_person_log = self.last_log_times[camera_id]["person"]
                if now - last_person_log > 30: # 30s cooldown
                    self._log(
                        f"({people_count}) Person detected on Camera {camera_id} ", 
                        "detection"
                    )
                    self.last_log_times[camera_id]["person"] = now
            
            # --- Weapon Detection Persistence & Cooldown ---
            current_weapon_streak = self.weapon_streak.get(camera_id, 0)
            if weapon_detected:
                current_weapon_streak += 1
            else:
                current_weapon_streak = 0
            self.weapon_streak[camera_id] = current_weapon_streak
            
            if current_weapon_streak == 5: # Faster for weapons
                last_weapon_log = self.last_log_times[camera_id]["weapon"]
                if now - last_weapon_log > 60: # Longer cooldown for weapons to avoid spamming alerts
                    self._log(
                        f"WEAPON DETECTED on Camera {camera_id}", 
                        "warning"
                    )
                    self.last_log_times[camera_id]["weapon"] = now

            self.people_counts[camera_id] = people_count
            self.weapon_detected[camera_id] = weapon_detected

    def get_stats(self):
        """Get overall system statistics"""
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
