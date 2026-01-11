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
            
        self._load_from_file()
        
        # Start date monitor thread
        threading.Thread(target=self._monitor_date_change, daemon=True).start()

    def _monitor_date_change(self):
        """Monitor for day changes/rollover"""
        while True:
            try:
                self._ensure_todays_log_file()
                time.sleep(60)
            except Exception as e:
                logger.error(f"Error in date monitor: {e}")
                time.sleep(60)

    def _ensure_todays_log_file(self):
        """Ensure the log file for today exists"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = self.logs_folder / f"{today}.txt"
            if not log_file.exists():
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write(f"--- Log Start {today} ---\n")
                logger.info(f"Initialized new daily log file: {log_file.name}")
        except Exception as e:
            logger.error(f"Error creating daily log file: {e}")

    def _load_from_file(self):
        """Load recent logs from the latest file to populate memory"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = self.logs_folder / f"{today}.txt"
            
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    # Parse the last 100 lines
                    for line in lines[-100:]:
                        try:
                            # Format: [HH:MM:SS] [LEVEL] Message
                            if "]" in line:
                                parts = line.split("] ", 2)
                                if len(parts) >= 3:
                                    ts_raw = parts[0].strip("[")
                                    lvl = parts[1].strip("[")
                                    msg = parts[2].strip()
                                    
                                    self.logs.insert(0, {
                                        "id": f"load_{int(time.time()*1000)}",
                                        "timestamp": f"{datetime.now().strftime('%Y-%m-%d')} {ts_raw}",
                                        "message": msg,
                                        "type": lvl.lower()
                                    })
                        except: continue
        except Exception as e:
            logger.error(f"Error loading logs from file: {e}")

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

    def get_logs(self, limit: int = 100):
        with self.lock:
            return self.logs[:limit]

    def get_available_dates(self) -> List[str]:
        """List all dates that have log files"""
        try:
            files = list(self.logs_folder.glob("*.txt"))
            dates = [os.path.splitext(f.name)[0] for f in files]
            return sorted(dates, reverse=True)
        except Exception as e:
            logger.error(f"Error listing log dates: {e}")
            return []

    def get_logs_by_date(self, date_str: str) -> List[dict]:
        """Fetch logs from a specific file"""
        historical_logs = []
        try:
            log_file = self.logs_folder / f"{date_str}.txt"
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for idx, line in enumerate(reversed(lines)):
                        try:
                            if "]" in line:
                                parts = line.split("] ", 2)
                                if len(parts) >= 3:
                                    ts_raw = parts[0].strip("[")
                                    lvl = parts[1].strip("[")
                                    msg = parts[2].strip()
                                    historical_logs.append({
                                        "id": f"hist_{date_str}_{idx}",
                                        "timestamp": f"{date_str} {ts_raw}",
                                        "message": msg,
                                        "type": lvl.lower()
                                    })
                        except: continue
            return historical_logs
        except Exception as e:
            logger.error(f"Error reading logs for {date_str}: {e}")
            return []
