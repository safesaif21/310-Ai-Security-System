"""Video processing utilities"""

import cv2
from datetime import datetime

def draw_timestamp(frame):
    """Draw timestamp with transparent background in top-left"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.5
    thickness = 1
    color = (255, 255, 255)
    bg_color = (0, 0, 0)
    padding = 5
    
    (text_w, text_h), baseline = cv2.getTextSize(timestamp, font, scale, thickness)
    x, y = 10, 20
    bg_x1, bg_y1 = x - padding, y - text_h - padding
    bg_x2, bg_y2 = x + text_w + padding, y + padding
    
    overlay = frame.copy()
    cv2.rectangle(overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), bg_color, -1)
    alpha = 0.6
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    cv2.putText(frame, timestamp, (x, y), font, scale, color, thickness, cv2.LINE_AA)
