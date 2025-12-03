"""Log management with file persistence"""

import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

class LogManager:
    def __init__(self, logs_folder: str = "logs"):
        self.logs: List[dict] = []
        self.lock = threading.Lock()
        self.max_logs = 1000
        self.logs_folder = Path(logs_folder)
        
        if not self.logs_folder.exists():
            self.logs_folder.mkdir(parents=True)

    def _write_to_file(self, entry: dict):
        """Write log entry to daily file"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = self.logs_folder / f"{today}.txt"
            
            timestamp = entry["timestamp"].split()[1]
            log_line = f"[{timestamp}] [{entry['type'].upper()}] {entry['message']}\n"
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_line)
        except Exception as e:
            logger.error(f"Error writing to log file: {e}")

    def add_log(self, message: str, type: str = "info"):
        with self.lock:
            entry = {
                "id": f"{int(time.time()*1000)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message": message,
                "type": type
            }
            self.logs.insert(0, entry)
            if len(self.logs) > self.max_logs:
                self.logs.pop()
            logger.info(f"[{type.upper()}] {message}")
            self._write_to_file(entry)

    def get_logs(self, limit: int = 50):
        with self.lock:
            return self.logs[:limit]
