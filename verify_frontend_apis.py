
import requests
import json

BASE_URL = "http://localhost:8000"

def verify_endpoints():
    print("Verifying Backend Endpoints...")
    
    # 1. Check Recordings Endpoints
    try:
        print("Checking GET /recordings/cameras...")
        resp = requests.get(f"{BASE_URL}/recordings/cameras")
        if resp.status_code == 200:
            print("  SUCCESS: ", resp.json())
        else:
            print(f"  FAIL: {resp.status_code}")
            
        # Check files for camera 0 (if exists)
        print("Checking GET /recordings/0/files...")
        resp = requests.get(f"{BASE_URL}/recordings/0/files")
        if resp.status_code == 200:
            files = resp.json().get('files', [])
            print(f"  SUCCESS: Found {len(files)} files")
            
            if files:
                test_file = files[0]['name']
                print(f"Checking GET /recordings/serve/0/{test_file}...")
                resp = requests.get(f"{BASE_URL}/recordings/serve/0/{test_file}", stream=True)
                if resp.status_code == 200:
                     print("  SUCCESS: Video stream accessible")
                else:
                     print(f"  FAIL: {resp.status_code}")
        else:
            print(f"  FAIL: {resp.status_code}")
            
    except Exception as e:
        print(f"  ERROR: {e}")

    # 2. Check Logs Endpoints
    try:
        print("\nChecking GET /logs/dates...")
        resp = requests.get(f"{BASE_URL}/logs/dates")
        if resp.status_code == 200:
            dates = resp.json().get('dates', [])
            print(f"  SUCCESS: Found dates {dates}")
            
            if dates:
                latest = dates[0]
                print(f"Checking GET /logs/{latest}...")
                resp = requests.get(f"{BASE_URL}/logs/{latest}")
                if resp.status_code == 200:
                    print("  SUCCESS: Log content retrieved")
                else:
                    print(f"  FAIL: {resp.status_code}")
        else:
            print(f"  FAIL: {resp.status_code}")
            
    except Exception as e:
        print(f"  ERROR: {e}")

if __name__ == "__main__":
    verify_endpoints()
