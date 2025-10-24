import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import websocket
import threading
import json
import base64
import io
import numpy as np

class SecuritySystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Security System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e293b')
        
        # State
        self.ws = None
        self.connected = False
        self.camera_active = False
        self.current_frame = None
        
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
        header = tk.Label(
            main_frame,
            text="🔒 AI Security System",
            font=("Arial", 32, "bold"),
            bg='#1e293b',
            fg='#8b5cf6'
        )
        header.pack(pady=(0, 20))
        
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
            text="▶️ Start Camera",
            command=self.start_camera,
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
            command=self.stop_camera,
            bg='#ef4444',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Video display
        self.video_label = tk.Label(left_frame, bg='#0f172a')
        self.video_label.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Right column - Stats
        right_frame = tk.Frame(content, bg='#1e293b', width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_frame.pack_propagate(False)
        
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
    
    def connect_to_server(self):
        """Connect to WebSocket server"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                
                if data['type'] == 'frame':
                    # Decode frame
                    img_bytes = base64.b64decode(data['frame'])
                    img = Image.open(io.BytesIO(img_bytes))
                    self.current_frame = img
                    
                    # Update detections
                    detections = data['detections']
                    self.threat_level = detections['threat_level']
                    self.people_count = detections['people_count']
                    self.detected_weapons = detections['weapons']
                    
                    if len(detections['weapons']) > 0:
                        self.alert_count += 1
                    
                    # Update UI in main thread
                    self.root.after(0, self.update_display)
            except Exception as e:
                print(f"Error: {e}")
        
        def on_open(ws):
            self.connected = True
            self.root.after(0, self.update_connection_status)
        
        def on_close(ws, close_status_code, close_msg):
            self.connected = False
            self.camera_active = False
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
    
    def start_camera(self):
        """Send start camera command"""
        if self.ws and self.connected:
            self.ws.send(json.dumps({'command': 'start_camera'}))
            self.camera_active = True
            self.update_connection_status()
    
    def stop_camera(self):
        """Send stop camera command"""
        if self.ws and self.connected:
            self.ws.send(json.dumps({'command': 'stop_camera'}))
            self.camera_active = False
            self.update_connection_status()
    
    def update_connection_status(self):
        """Update button states based on connection"""
        if self.connected:
            self.connect_btn.config(state=tk.DISABLED)
            self.start_btn.config(state=tk.NORMAL if not self.camera_active else tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL if self.camera_active else tk.DISABLED)
            
            if self.camera_active:
                self.status_emoji.config(text="🟢")
                self.status_label.config(text="ACTIVE")
            else:
                self.status_emoji.config(text="🟡")
                self.status_label.config(text="CONNECTED")
        else:
            self.connect_btn.config(state=tk.NORMAL)
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_emoji.config(text="🔴")
            self.status_label.config(text="INACTIVE")
    
    def update_display(self):
        """Update the display with current frame and stats"""
        # Update video frame
        if self.current_frame:
            # Resize to fit display
            display_img = self.current_frame.copy()
            display_img.thumbnail((800, 600), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(display_img)
            self.video_label.config(image=photo)
            self.video_label.image = photo
        
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

if __name__ == "__main__":
    root = tk.Tk()
    app = SecuritySystemGUI(root)
    root.mainloop()