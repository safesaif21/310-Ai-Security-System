
import requests
import time
import subprocess
import sys
import os
from pathlib import Path

def verify():
    # Start backend
    print("Starting backend...")
    process = subprocess.Popen([sys.executable, "-m", "backend.main"], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE,
                             cwd=os.getcwd(),
                             creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    try:
        # Wait for startup
        print("Waiting for startup (10s)...")
        time.sleep(10)
        
        try:
            # Check status
            resp = requests.get("http://localhost:8000/debug/status")
            if resp.status_code != 200:
                print(f"Failed to get status: {resp.status_code}")
                return
            
            data = resp.json()
            print(f"Status: {data}")
            
            if not data["recording_enabled"]:
                print("FAIL: Recording not enabled")
            elif not data["master_recording"]:
                print("FAIL: Master recording not active")
            elif not data["active_recordings"]:
                print("FAIL: No active camera recordings")
            else:
                print("SUCCESS: Recording started automatically")
                    
        except Exception as e:
            print(f"Connection failed: {e}")
            return

        # Check files
        print("Checking initial files...")
        rec_dir = Path("recordings")
        master_dir = Path("master")
        
        camera_dirs = list(rec_dir.glob("camera_*"))
        if not camera_dirs:
            print("FAIL: No camera folders created")
        else:
            for d in camera_dirs:
                files = list(d.glob("*.mp4"))
                print(f"  {d.name}: {len(files)} files")
        
        master_files = list(master_dir.glob("*.mp4"))
        print(f"  Master: {len(master_files)} files")

    finally:
        print("Killing backend...")
        # Start a thread or something? No, simple kill
        subprocess.call(["taskkill", "/F", "/T", "/PID", str(process.pid)])

if __name__ == "__main__":
    verify()
