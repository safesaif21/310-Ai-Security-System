# Docker Deployment Guide

## 1. Local Testing (Single Machine)

To test the entire microservices architecture on your development machine:

1.  **Build and Run**:
    ```bash
    docker-compose up --build
    ```
2.  **Access Services**:
    *   **Auth Service**: `http://localhost:8040/docs`
    *   **Camera Service**: `http://localhost:8041/docs` (Note: USB Camera access on Windows Docker is tricky. You might see "No cameras detected").
    *   **Analysis Service**: `http://localhost:8042/docs`

## 2. Distributed Deployment (Two Laptops)

This setup allows you to run the heavy AI processing on one machine and the recording/camera logic on another.

### Step 1: Network Prep
Docker Compose requires a file named exactly **`.env`** (not `.env.docker`) in the root folder for IP interpolation to work.

**Create a `.env` file on BOTH laptops:**
```bash
# Laptop A IP (Frontend/AI)
FRONT_SERVER_IP=192.168.1.10

# Laptop B IP (DVR/Cameras)
BACK_SERVER_IP=192.168.1.20
```

### Step 2: Laptop B Setup (SECURITY-BACK)
1. Run the DVR service:
   ```bash
   docker-compose -f docker-compose.security-back.yml up --build -d
   ```
2. Start the local cameras:
   Run `start_camera.bat`

### Step 3: Laptop A Setup (SECURITY-FRONT)
1. Run the Frontend & AI:
   ```bash
   docker-compose -f docker-compose.security-front.yml up --build -d
   ```
2. Open `http://localhost` (on Laptop A) or `http://[FRONT_SERVER_IP]` from any device on your network.
*   **Network**: Both must be on same LAN (Ethernet recommended).

### Step 1: Prepare Node 1 (Server)
1.  Copy the project codebase to Node 1.
2.  Edit `docker-compose.yml`:
    *   Comment out `camera-service`.
    *   Update `analysis-service` environment:
        ```yaml
        environment:
          - CAMERA_SERVICE_URL=http://<IP_OF_NODE_2>:8041
        ```
3.  Run:
    ```bash
    docker-compose up --build -d mongo auth-service analysis-service
    ```

### Step 2: Prepare Node 2 (Camera)
1.  Copy the project codebase to Node 2.
2.  Edit `docker-compose.yml`:
    *   Comment out `mongo`, `auth`, `analysis`.
3.  Run:
    ```bash
    docker-compose up --build -d camera-service
    ```

### Step 3: Verify Connection
*   Check Analysis logs on Node 1:
    ```bash
    docker logs -f security_analysis
    ```
    It should say `Connecting to stream: http://<NODE_2_IP>:8041...`

## 3. Advanced: Native Camera Service on Ubuntu Server (Node 2)

If you prefer running the Camera Service natively (without Docker) on Node 2 (e.g., to ensure direct hardware access or lower overhead), follow these steps.

### Option A: Quick Background Run (nohup)
Good for testing, but stops if you reboot.

1.  **Install System Dependencies**:
    ```bash
    sudo apt-get update && sudo apt-get install -y python3-pip python3-opencv libgl1-mesa-glx libglib2.0-0
    ```
2.  **Install Python Dependencies**:
    ```bash
    cd backend/services/camera
    pip3 install -r requirements.txt
    cd ../../.. # Go back to root
    ```
3.  **Run in Background**:
    ```bash
    nohup python3 -m backend.services.camera.main > camera.log 2>&1 &
    ```
    *   `nohup` ... `&`: Runs the command in the background and keeps it running even if you disconnect.
    *   `> camera.log`: Saves output to a file.
    *   You can now use your terminal freely!

### Option B: Robust Service (systemd) - **RECOMMENDED**
Ensures the camera service starts automatically on boot and crashes are restarted.

1.  **Create Service File**:
    ```bash
    sudo nano /etc/systemd/system/camera-service.service
    ```
2.  **Paste Configuration** (Adjust paths to match your setup):
    ```ini
    [Unit]
    Description=AI Security Camera Service
    After=network.target

    [Service]
    User=ubuntu
    WorkingDirectory=/home/ubuntu/310-Ai-Security-System
    Environment="PYTHONPATH=/home/ubuntu/310-Ai-Security-System"
    ExecStart=/usr/bin/python3 -m backend.services.camera.main
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
3.  **Enable and Start**:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable camera-service
    sudo systemctl start camera-service
    ```
4.  **Check Status**:
    ```bash
    sudo systemctl status camera-service
    ```

---

## 4. Architecture & Connectivity Example

To help you visualize how everything connects, let's use example IP addresses.

### Setup
-   **Node 1 (Laptop 1 - Server)**: `192.168.1.100`
    *   Runs: Frontend, Auth Service (8040), Analysis Service (8042), MongoDB.
-   **Node 2 (Laptop 2 - Camera)**: `192.168.1.101`
    *   Runs: Camera Service (8041).

### Connectivity Flow

1.  **Frontend (Your Browser)**  
    *You open `http://192.168.1.100`*
    *   **Login**: Browser calls `http://192.168.1.100:8040/login` (Auth Service).
    *   **View Camera**: Browser directly fetches video from `http://192.168.1.101:8041/camera/0` (Camera Service on Node 2).
    *   **Dashboard**: Browser checks status from `http://192.168.1.100:8042/status` (Analysis Service).

2.  **Analysis Service (on Node 1)**
    *   **Consuming Video**: Connects to `http://192.168.1.101:8041/camera/0` to get frames for YOLO.
    *   **Logging Events**: Sends POST requests to `http://192.168.1.101:8041/logs/events` when a person/weapon is detected.

3.  **Camera Service (on Node 2)**
    *   **Captures Video**: Directly accesses `/dev/video0`.
    *   **Serves Stream**: Provides MJPEG at port `8041`.
    *   **Saves Recordings**: Writes `.mp4` files to local disk on Node 2.
    *   **Saves Logs**: Appends logs to local files on Node 2.

### Summary Diagram
```text
[ Browser (You) ]
       |
       |  1. Request App
       v
[ Node 1 (192.168.1.100) ] <-----------------------+
|  [ Frontend Container ]                          |
|  [ Auth Service :8040 ]                          | 2. Fetch Video Stream
|  [ Analysis Service :8042 ] --(Get Video)-----> [ Node 2 (192.168.1.101) ]
|           |                                     |  [ Camera Service :8041 ]
|           +-----(POST /logs/events)-----------> |         |
|                                                 |     [ USB Camera ]
+-------------------------------------------------+     [ HDD (Logs/Recs) ]
```
