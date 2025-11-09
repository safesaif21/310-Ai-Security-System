import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import websocket
import asyncio
import threading
import json
import base64
import io
import numpy as np
import os

num_of_cameras = 0  # Placeholder for number of cameras

class SecuritySystemGUI:
    def __init__(self, root, num_of_cameras):
        self.root = root
        self.root.title("AI Security System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e293b')
        self.num_of_cameras = num_of_cameras
        
        # State
        self.ws = None
        self.connected = False
        self.cameras_active = False
        self.current_frames = [None] * num_of_cameras  # support multiple feeds
        self.available_models = []
        self.current_model_path = None
        
        # Stats
        self.threat_level = 0
        self.people_count = 0
        self.detected_weapons = []
        self.alert_count = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#1e293b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                
        # Header
        tk.Label(
            main_frame,
            text=f"🔒 AI Security System — {self.num_of_cameras} camera(s) detected",
            font=("Arial", 24, "bold"),
            bg='#1e293b',
            fg='#8b5cf6'
        ).pack(pady=(0, 20))
        
        # Content area (2 columns)
        content = tk.Frame(main_frame, bg='#1e293b')
        content.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Video
        left_frame = tk.Frame(content, bg='#334155', bd=2, relief=tk.RAISED)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Video title
        video_title = tk.Label(
            left_frame,
            text="📹 Live Camera Feed",
            font=("Arial", 16, "bold"),
            bg='#334155',
            fg='white'
        )
        video_title.pack(pady=10)

        # Control buttons
        btn_frame = tk.Frame(left_frame, bg='#334155')
        btn_frame.pack(pady=10)
        
        self.connect_btn = tk.Button(
            btn_frame,
            text="🔌 Connect",
            command=self.connect_to_server,
            bg='#6366f1',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.start_btn = tk.Button(
            btn_frame,
            text="▶️ Start Camera(s)",
            command=self.start_cameras,
            bg='#22c55e',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            btn_frame,
            text="⏹️ Stop Camera",
            command=self.stop_cameras,
            bg='#ef4444',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # --- 🧩 Dynamic Camera Grid ---
        self.video_grid = tk.Frame(left_frame, bg='#0f172a')
        self.video_grid.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.create_camera_grid()
        
        # Right column - Stats
        right_frame = tk.Frame(content, bg='#1e293b', width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        # Model Selection
        model_frame = tk.Frame(right_frame, bg='#334155', bd=2, relief=tk.RAISED)
        model_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            model_frame,
            text="🤖 YOLO Model",
            font=("Arial", 14, "bold"),
            bg='#334155',
            fg='white'
        ).pack(pady=10)
        
        # Model dropdown
        model_select_frame = tk.Frame(model_frame, bg='#334155')
        model_select_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        tk.Label(
            model_select_frame,
            text="Select Model:",
            font=("Arial", 10),
            bg='#334155',
            fg='#94a3b8'
        ).pack(anchor=tk.W)
        
        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(
            model_select_frame,
            textvariable=self.model_var,
            state="readonly",
            font=("Arial", 10),
            width=25
        )
        self.model_dropdown.pack(pady=5, fill=tk.X)
        self.model_dropdown.bind("<<ComboboxSelected>>", self.on_model_selected)
        
        self.model_status_label = tk.Label(
            model_frame,
            text="Not connected",
            font=("Arial", 9),
            bg='#334155',
            fg='#94a3b8',
            wraplength=300
        )
        self.model_status_label.pack(pady=(0, 10))
        
        # Threat Level
        threat_frame = tk.Frame(right_frame, bg='#334155', bd=2, relief=tk.RAISED)
        threat_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            threat_frame,
            text="⚠️ Threat Level",
            font=("Arial", 14, "bold"),
            bg='#334155',
            fg='white'
        ).pack(pady=10)
        
        self.threat_label = tk.Label(
            threat_frame,
            text="0/10",
            font=("Arial", 48, "bold"),
            bg='#334155',
            fg='#10b981'
        )
        self.threat_label.pack(pady=20)
        
        self.threat_status = tk.Label(
            threat_frame,
            text="SAFE",
            font=("Arial", 16, "bold"),
            bg='#334155',
            fg='#10b981'
        )
        self.threat_status.pack(pady=(0, 20))
        
        # Weapon Detection
        weapon_frame = tk.Frame(right_frame, bg='#334155', bd=2, relief=tk.RAISED)
        weapon_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            weapon_frame,
            text="🔪 Weapon Detection",
            font=("Arial", 14, "bold"),
            bg='#334155',
            fg='white'
        ).pack(pady=10)
        
        self.weapon_label = tk.Label(
            weapon_frame,
            text="✅ No Weapon Detected",
            font=("Arial", 12),
            bg='#334155',
            fg='#10b981',
            wraplength=300
        )
        self.weapon_label.pack(pady=20)
        
        # Statistics
        stats_frame = tk.Frame(right_frame, bg='#334155', bd=2, relief=tk.RAISED)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            stats_frame,
            text="📊 Statistics",
            font=("Arial", 14, "bold"),
            bg='#334155',
            fg='white'
        ).pack(pady=10)
        
        # People count
        people_stat = tk.Frame(stats_frame, bg='#1e293b', bd=1, relief=tk.RAISED)
        people_stat.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(people_stat, text="👥", font=("Arial", 20), bg='#1e293b', fg='white').pack(pady=5)
        tk.Label(people_stat, text="PEOPLE DETECTED", font=("Arial", 9), bg='#1e293b', fg='#94a3b8').pack()
        self.people_label = tk.Label(people_stat, text="0", font=("Arial", 24, "bold"), bg='#1e293b', fg='white')
        self.people_label.pack(pady=5)
        
        # Alert count
        alert_stat = tk.Frame(stats_frame, bg='#1e293b', bd=1, relief=tk.RAISED)
        alert_stat.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(alert_stat, text="🚨", font=("Arial", 20), bg='#1e293b', fg='white').pack(pady=5)
        tk.Label(alert_stat, text="ALERTS TODAY", font=("Arial", 9), bg='#1e293b', fg='#94a3b8').pack()
        self.alert_label = tk.Label(alert_stat, text="0", font=("Arial", 24, "bold"), bg='#1e293b', fg='white')
        self.alert_label.pack(pady=5)
        
        # Status
        status_stat = tk.Frame(stats_frame, bg='#1e293b', bd=1, relief=tk.RAISED)
        status_stat.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_emoji = tk.Label(status_stat, text="🔴", font=("Arial", 20), bg='#1e293b', fg='white')
        self.status_emoji.pack(pady=5)
        tk.Label(status_stat, text="SYSTEM STATUS", font=("Arial", 9), bg='#1e293b', fg='#94a3b8').pack()
        self.status_label = tk.Label(status_stat, text="INACTIVE", font=("Arial", 16, "bold"), bg='#1e293b', fg='white')
        self.status_label.pack(pady=5)
    
    def create_camera_grid(self):
        """Create dynamic camera feed grid based on number of cameras"""
        cams = self.num_of_cameras

        # Determine grid layout
        if cams == 1:
            rows, cols = 1, 1
        elif cams <= 4:
            rows, cols = 2, 2
        elif cams <= 6:
            rows, cols = 2, 4
        elif cams <= 8:
            rows, cols = 3, 4
        else:
            rows, cols = (cams // 4) + 1, 4

        self.video_labels = []
        index = 0
        for r in range(rows):
            for c in range(cols):
                if index < cams:
                    label = tk.Label(
                        self.video_grid,
                        bg="#0f172a",
                        relief=tk.SOLID,
                        bd=1,
                        text=f"Camera {index+1}",
                        fg="white",
                        font=("Arial", 10)
                    )
                    label.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
                    self.video_labels.append(label)
                    index += 1
                else:
                    # fill empty slots so grid is balanced
                    tk.Label(self.video_grid, bg="#1e293b").grid(
                        row=r, column=c, padx=5, pady=5, sticky="nsew"
                    )

        # Make the grid expand evenly
        for r in range(rows):
            self.video_grid.rowconfigure(r, weight=1)
        for c in range(cols):
            self.video_grid.columnconfigure(c, weight=1)

    def connect_to_server(self):
        """Connect to WebSocket server"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                
                if data['type'] == 'frame':
                    cam_id = data.get('camera_id', 0)
                    img_bytes = base64.b64decode(data['frame'])
                    img = Image.open(io.BytesIO(img_bytes))
                    self.current_frames[cam_id] = img  # store per camera
                    
                    # Update detections (for global stats)
                    detections = data['detections']
                    self.threat_level = detections['threat_level']
                    self.people_count = detections['people_count']
                    self.detected_weapons = detections['weapons']

                    if len(detections['weapons']) > 0:
                        self.alert_count += 1

                    self.root.after(0, self.update_display)
                    
                if data['type'] == 'camera_list':
                    cameras = data.get('cameras', [])
                    self.num_of_cameras = len(cameras)
                    print(f"Activated {len(cameras)} cameras: {cameras}")
                    self.root.after(0, lambda: self.refresh_camera_grid(len(cameras)))
                if data['type'] == 'innit':
                    global num_of_cameras
                    num_of_cameras = data['cameras']
                    # Handle available models
                    available_models = data.get('available_models', [])
                    current_model = data.get('current_model', '')
                    self.root.after(0, lambda: self.update_model_list(available_models, current_model))
                
                if data['type'] == 'model_switched':
                    model_path = data.get('model_path', '')
                    message = data.get('message', 'Model switched')
                    self.root.after(0, lambda: self.on_model_switched_success(model_path, message))
                
                if data['type'] == 'error' and 'model' in data.get('message', '').lower():
                    error_msg = data.get('message', 'Error switching model')
                    self.root.after(0, lambda: self.on_model_switch_error(error_msg))
            except Exception as e:
                print(f"Error: {e}")
        
        def on_open(ws):
            self.connected = True
            self.root.after(0, self.update_connection_status)

            # Send init command
            init_msg = json.dumps({"command": "innit"})
            ws.send(init_msg)
        
        def on_close(ws, close_status_code, close_msg):
            self.connected = False
            self.cameras_active = False
            self.root.after(0, self.update_connection_status)
        
        def on_error(ws, error):
            print(f"WebSocket error: {error}")
        
        def run_ws():
            self.ws = websocket.WebSocketApp(
                "ws://localhost:8765",
                on_message=on_message,
                on_open=on_open,
                on_close=on_close,
                on_error=on_error
            )
            self.ws.run_forever(ping_interval=30, ping_timeout=10)
        
        thread = threading.Thread(target=run_ws, daemon=True)
        thread.start()
    
    def start_cameras(self):
        """Send start cameras command"""
        if self.ws and self.connected:
            self.ws.send(json.dumps({'command': 'start_cameras'}))
            self.cameras_active = True
            self.update_connection_status()
    
    def stop_cameras(self):
        """Send stop camera command"""
        if self.ws and self.connected:
            self.ws.send(json.dumps({'command': 'stop_cameras'}))
            self.cameras_active = False
            self.update_connection_status()
    
    def update_model_list(self, available_models, current_model):
        """Update the model dropdown with available models"""
        self.available_models = available_models
        self.current_model_path = current_model
        
        if available_models:
            # Create display names for dropdown (just show the model name)
            model_names = [m['name'] for m in available_models]
            self.model_dropdown['values'] = model_names
            
            # Set current selection
            for model in available_models:
                if model['path'] == current_model:
                    self.model_var.set(model['name'])
                    break
            
            # Update status with model name and path
            model_name = os.path.basename(current_model).replace('.pt', '')
            self.model_status_label.config(
                text=f"✅ Active: {model_name}",
                fg='#10b981'
            )
        else:
            self.model_status_label.config(
                text="No models found",
                fg='#ef4444'
            )
    
    def on_model_selected(self, event=None):
        """Handle model selection from dropdown"""
        if not self.connected or not self.ws:
            return
        
        selection = self.model_var.get()
        if not selection:
            return
        
        # Find the selected model (dropdown shows just the name)
        for model in self.available_models:
            if model['name'] == selection:
                # Don't switch if it's already the current model
                if model['path'] == self.current_model_path:
                    return
                
                # Send switch model command
                self.model_status_label.config(
                    text=f"⏳ Switching to {model['name']}...",
                    fg='#f59e0b'
                )
                if self.ws:
                    self.ws.send(json.dumps({
                        'command': 'switch_model',
                        'model_path': model['path']
                    }))
                break
    
    def on_model_switched_success(self, model_path, message):
        """Handle successful model switch"""
        self.current_model_path = model_path
        model_name = os.path.basename(model_path)
        self.model_status_label.config(
            text=f"✅ Active: {model_name}",
            fg='#10b981'
        )
        print(f"Model switched: {message}")
    
    def on_model_switch_error(self, error_msg):
        """Handle model switch error"""
        self.model_status_label.config(
            text=f"❌ Error: {error_msg[:50]}",
            fg='#ef4444'
        )
        print(f"Model switch error: {error_msg}")
    
    def update_connection_status(self):
        """Update button states based on connection"""
        if self.connected:
            self.connect_btn.config(state=tk.DISABLED)
            self.start_btn.config(state=tk.NORMAL if not self.cameras_active else tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL if self.cameras_active else tk.DISABLED)
            # Enable model dropdown when connected
            if hasattr(self, 'model_dropdown'):
                self.model_dropdown.config(state="readonly")
            
            if self.cameras_active:
                self.status_emoji.config(text="🟢")
                self.status_label.config(text="ACTIVE")
            else:
                self.status_emoji.config(text="🟡")
                self.status_label.config(text="CONNECTED")
        else:
            self.connect_btn.config(state=tk.NORMAL)
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.DISABLED)
            # Disable model dropdown when not connected
            if hasattr(self, 'model_dropdown'):
                self.model_dropdown.config(state="disabled")
                self.model_status_label.config(text="Not connected", fg='#94a3b8')
            
            self.status_emoji.config(text="🔴")
            self.status_label.config(text="INACTIVE")
    
    def update_display(self):
        """Update all camera feeds and stats"""
        for i, frame in enumerate(self.current_frames):
            if frame is not None:
                display_img = frame.copy()
                display_img.thumbnail((400, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(display_img)
                self.video_labels[i].config(image=photo, text=f"Camera {i+1}")
                self.video_labels[i].image = photo
        
        # Update threat level
        self.threat_label.config(text=f"{self.threat_level}/10")
        
        # Color and status based on threat level
        if self.threat_level == 0:
            color = '#10b981'
            status = 'SAFE'
        elif self.threat_level <= 3:
            color = '#22c55e'
            status = 'LOW'
        elif self.threat_level <= 6:
            color = '#f59e0b'
            status = 'MODERATE'
        elif self.threat_level <= 8:
            color = '#ef4444'
            status = 'HIGH'
        else:
            color = '#dc2626'
            status = 'CRITICAL'
        
        self.threat_label.config(fg=color)
        self.threat_status.config(text=status, fg=color)
        
        # Update weapon detection
        if self.detected_weapons:
            weapon_text = f"⚠️ {len(self.detected_weapons)} WEAPON(S) DETECTED!\n\n"
            for weapon in self.detected_weapons:
                weapon_text += f"{weapon['name']}: {weapon['confidence']*100:.1f}%\n"
            self.weapon_label.config(text=weapon_text, fg='#ef4444')
        else:
            self.weapon_label.config(text="✅ No Weapon Detected", fg='#10b981')
        
        # Update stats
        self.people_label.config(text=str(self.people_count))
        self.alert_label.config(text=str(self.alert_count))

    def refresh_camera_grid(self, new_count):
        """Recreate grid if number of active cameras changed"""
        for widget in self.video_grid.winfo_children():
            widget.destroy()
        self.num_of_cameras = new_count
        self.create_camera_grid()

def get_num_of_cameras(timeout=60):
    """Fetch number of cameras from backend before starting GUI."""
    global num_of_cameras
    num_of_cameras = None
    event = threading.Event()

    def on_message(ws, message):
        global num_of_cameras
        try:
            data = json.loads(message)
            if data.get("type") == "innit":
                num_of_cameras = data["cameras"]
                event.set()  # signal that we got the data
                ws.close()
        except Exception as e:
            print(f"Error receiving camera count: {e}")

    def on_open(ws):
        ws.send(json.dumps({"command": "innit"}))

    ws = websocket.WebSocketApp(
        "ws://localhost:8765",
        on_message=on_message,
        on_open=on_open
    )

    # Run websocket in a thread
    thread = threading.Thread(target=ws.run_forever, daemon=True)
    thread.start()

    # Wait until event is set or timeout occurs
    if not event.wait(timeout):
        print(f"⚠️ Timeout reached, defaulting to 1 camera.")
        num_of_cameras = 1


if __name__ == "__main__":

    get_num_of_cameras()
    print(f"Camera count received before GUI start: {num_of_cameras}")

    root = tk.Tk()
    app = SecuritySystemGUI(root, num_of_cameras)
    root.mainloop()