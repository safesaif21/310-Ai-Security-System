#!/usr/bin/env python3
"""
AI Security System - Streamlit Dashboard modern UI for real-time threat detection and monitoring
"""

import streamlit as st
import cv2
import numpy as np
from datetime import datetime
import time
from PIL import Image
import websocket
from streamlit_autorefresh import st_autorefresh

# Initialize session state
if "ws_connected" not in st.session_state:
    st.session_state.ws_connected = False
if "ws" not in st.session_state:
    st.session_state.ws = None
if "last_message" not in st.session_state:
    st.session_state.last_message = None

# Connect to WebSocket (non-blocking)
if st.session_state.ws is None:
    st.session_state.ws = websocket.WebSocket()
    try:
        st.session_state.ws.connect("ws://localhost:8765", timeout=1)
        print("websocket connected")
        st.session_state.ws_connected = True
    except:
        st.session_state.ws_connected = False

# Poll for messages
if st.session_state.ws_connected:
    try:
        msg = st.session_state.ws.recv()  # non-blocking if you set timeout
        if msg:
            st.session_state.last_message = msg
    except websocket.WebSocketTimeoutException:
        pass  # no new messages, continue

# Page configuration
st.set_page_config(
    page_title="AI Security System",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        border: 1px solid #334155;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        display: inline-block;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
        font-size: 0.875rem;
        letter-spacing: 0.5px;
        margin-left: 1rem;
    }
    
    .status-safe {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 2px solid #10b981;
    }
    
    .status-low {
        background: rgba(34, 197, 94, 0.2);
        color: #22c55e;
        border: 2px solid #22c55e;
    }
    
    .status-moderate {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        border: 2px solid #f59e0b;
    }
    
    .status-high {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 2px solid #ef4444;
    }
    
    .status-critical {
        background: rgba(220, 38, 38, 0.2);
        color: #dc2626;
        border: 2px solid #dc2626;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #f1f5f9;
        line-height: 1;
    }
    
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    /* Threat level display */
    .threat-display {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 1rem;
        border: 1px solid #334155;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }
    
    .threat-number {
        font-size: 5rem;
        font-weight: 700;
        line-height: 1;
        margin: 1rem 0;
    }
    
    .threat-max {
        font-size: 2rem;
        color: #64748b;
    }
    
    /* Weapon alert */
    .weapon-alert {
        background: rgba(239, 68, 68, 0.1);
        border: 2px solid #ef4444;
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
        animation: shake 0.5s;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
    
    .weapon-item {
        background: #1e293b;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 3px solid #ef4444;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Video container */
    .video-container {
        border-radius: 1rem;
        overflow: hidden;
        border: 1px solid #334155;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }
    
    /* Stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Adjust spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# COCO class names
COCO_CLASSES = {
    0: 'person', 43: 'knife', 34: 'baseball bat', 76: 'scissors'
}

WEAPON_CLASSES = {43: 'Knife', 34: 'Baseball Bat', 76: 'Scissors'}

# Initialize session state
if 'model' not in st.session_state:
    st.session_state.model = None
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'alert_count' not in st.session_state:
    st.session_state.alert_count = 0
if 'threat_level' not in st.session_state:
    st.session_state.threat_level = 0
if 'people_count' not in st.session_state:
    st.session_state.people_count = 0
if 'detected_weapons' not in st.session_state:
    st.session_state.detected_weapons = []

def get_threat_color(level):
    """Get color based on threat level"""
    if level == 0:
        return "#10b981"  # Green
    elif level <= 3:
        return "#22c55e"  # Light green
    elif level <= 6:
        return "#f59e0b"  # Yellow
    elif level <= 8:
        return "#ef4444"  # Red
    else:
        return "#dc2626"  # Dark red


def get_threat_status(level):
    """Get status text and class"""
    if level == 0:
        return "SAFE", "status-safe"
    elif level <= 3:
        return "LOW", "status-low"
    elif level <= 6:
        return "MODERATE", "status-moderate"
    elif level <= 8:
        return "HIGH", "status-high"
    else:
        return "CRITICAL", "status-critical"


# Main UI
def main():

    # Refresh every 1000 ms (1 second)
    # st_autorefresh(interval=1000, limit=None, key="ws_refresh")

    status_text = "CONNECTED" if st.session_state.ws_connected else "DISCONNECTED"
    status_class = "status-safe" if st.session_state.ws_connected else "status-critical"

    # HEADER
    st.markdown(f"""
    <div class="main-header">
        <h1 class="header-title">🔒 AI Security System</h1>
        <span class="status-badge {status_class}">SYSTEM {status_text}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:

        st.markdown("### 📹 Live Camera Feed")
        
        # Camera controls
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
        with col_btn1:
            start_camera = st.button("🎥 Start Camera", use_container_width=True)
        with col_btn2:
            stop_camera = st.button("⏹️ Stop Camera", use_container_width=True)
        
        if start_camera:
            st.session_state.camera_active = True
        if stop_camera:
            st.session_state.camera_active = False
        
        # Video frame placeholder
        video_placeholder = st.empty()
        
        if st.session_state.camera_active:
            
            print("camera active")
            if st.session_state.last_message:
                st.write(f"Last message: {st.session_state.last_message}")
            #connect to websocket for camera request here
        else:
            # Show placeholder image
            placeholder_img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(placeholder_img, "Click 'Start Camera' to begin", (100, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            video_placeholder.image(placeholder_img, channels="RGB", use_container_width=True)
    
    with col2:
        # Threat Level Display
        st.markdown("### ⚠️ Threat Level")
        
        threat_level = 0 #get from websocket
        threat_color = get_threat_color(threat_level)
        status_text, status_class = get_threat_status(threat_level)
        
        st.markdown(f"""
        <div class="threat-display">
            <div style="font-size: 1rem; color: #94a3b8; margin-bottom: 1rem;">CURRENT THREAT LEVEL</div>
            <div class="threat-number" style="color: {threat_color};">
                {threat_level}<span class="threat-max">/10</span>
            </div>
            <div class="status-badge {status_class}" style="margin-top: 1rem;">
                {status_text}
            </div>
            <div style="color: #94a3b8; margin-top: 1rem; font-size: 0.875rem;">
                {"No threats detected" if threat_level == 0 else 
                 "Minimal threat" if threat_level <= 3 else
                 "Moderate threat level" if threat_level <= 6 else
                 "High threat detected!" if threat_level <= 8 else
                 "CRITICAL THREAT!"}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Weapon Detection
        st.markdown("### 🔪 Weapon Detection")
        
        if st.session_state.detected_weapons:
            st.markdown('<div class="weapon-alert">', unsafe_allow_html=True)
            st.markdown("#### ⚠️ WEAPON DETECTED!")
            st.markdown(f"**{len(st.session_state.detected_weapons)} weapon(s) identified**")
            
            for weapon in st.session_state.detected_weapons:
                st.markdown(f"""
                <div class="weapon-item">
                    <span style="font-weight: 600; color: #f1f5f9;">{weapon['name']}</span>
                    <span style="color: #ef4444; font-weight: 600;">{weapon['confidence']*100:.1f}%</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card" style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">✅</div>
                <div style="font-size: 1.125rem; font-weight: 600; color: #f1f5f9;">No Weapon Detected</div>
                <div style="color: #94a3b8; margin-top: 0.5rem; font-size: 0.875rem;">System is monitoring</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Statistics
        st.markdown("### 📊 Statistics")
        
        stat_col1, stat_col2 = st.columns(2)
        
        with stat_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">👥</div>
                <div class="metric-label">People Detected</div>
                <div class="metric-value">{st.session_state.people_count}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">⏰</div>
                <div class="metric-label">Last Update</div>
                <div class="metric-value" style="font-size: 1.25rem;">
                    {datetime.now().strftime('%H:%M:%S')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with stat_col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🚨</div>
                <div class="metric-label">Alerts Today</div>
                <div class="metric-value">{st.session_state.alert_count}</div>
            </div>
            """, unsafe_allow_html=True)
            
            status_emoji = "🟢" if st.session_state.camera_active else "🔴"
            status_text = "ACTIVE" if st.session_state.camera_active else "INACTIVE"
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">{status_emoji}</div>
                <div class="metric-label">System Status</div>
                <div class="metric-value" style="font-size: 1.25rem;">
                    {status_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

