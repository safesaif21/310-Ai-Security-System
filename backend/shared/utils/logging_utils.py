"""Shared logging utilities"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

# Use environment variable if in Docker, else default to localhost for native services
LOG_SERVICE_URL = os.getenv("LOG_SERVICE_URL", "http://localhost:8043")

def send_log(message: str, log_type: str = "info"):
    """
    Send a log message to the centralized Log Service (port 8043).
    """
    try:
        url = f"{LOG_SERVICE_URL}/logs/events"
        # Using print so it definitely shows up in 'docker logs'
        print(f"DEBUG: Sending Log -> {message}")
        
        response = requests.post(
            url,
            json={"message": message, "type": log_type},
            timeout=1.0
        )
        if response.status_code != 200:
            print(f"WARNING: Log Service Error {response.status_code} for {url}")
    except Exception as e:
        print(f"ERROR: Could not reach Log Service at {LOG_SERVICE_URL}: {e}")
