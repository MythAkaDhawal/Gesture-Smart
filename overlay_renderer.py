# overlay_renderer.py
# Lightweight OpenCV HUD overlay optimized for low CPU usage.
# Functions:
#   render_overlay(frame_bgr, landmarks, gesture_name, action_state, fps, debug=False)
#
# landmarks: list of (x,y) normalized coordinates (0..1) OR None
# gesture_name: short string like "Pinch", "OpenHand", "Drag"
# action_state: dict with booleans e.g. {"click":True, "drag":False, "scroll":False}
# fps: float
# debug: if True prints extra minimal info on image

import cv2
import math

_FONT = cv2.FONT_HERSHEY_SIMPLEX

# Colors (BGR)
_BG = (20, 20, 20)
_TEXT_COLOR = (230, 230, 230)
_GOOD = (57, 180, 75)
_WARN = (0, 215, 255)
_BAD = (30, 60, 200)

def _draw_transparent_rect(img, tl, br, color=(0,0,0), alpha=0.45):
    x1,y1 = tl; x2,y2 = br
    overlay = img.copy()
    cv2.rectangle(overlay, (x1,y1), (x2,y2), color, -1)
    cv2.addWeighted(overlay, alpha, img, 1-alpha, 0, img)

def _norm_to_px(norm_x, norm_y, w, h):
    return int(norm_x * w), int(norm_y * h)

def render_overlay(frame_bgr, landmarks, gesture_name, action_state, fps, debug=False):
    """
    frame_bgr: BGR image (numpy)
    landmarks: list of (x,y) normalized (0..1) or None
    gesture_name: string
    action_state: dict with keys like 'click','drag','scroll' => booleans
    fps: float
    """
    h, w = frame_bgr.shape[:2]

    # draw a small translucent panel at top-left with FPS and gesture name
    pad_x, pad_y = 12, 12
    panel_w, panel_h = 320, 86
    _draw_transparent_rect(frame_bgr, (pad_x, pad_y), (pad_x + panel_w, pad_y + panel_h), color=_BG, alpha=0.55)

    # FPS
    fps_text = f"FPS: {fps:.1f}"
    cv2.putText(frame_bgr, fps_text, (pad_x + 12, pad_y + 26), _FONT, 0.7, _TEXT_COLOR, 2, cv2.LINE_AA)

    # Gesture name
    gtext = f"Gesture: {gesture_name or 'Idle'}"
    cv2.putText(frame_bgr, gtext, (pad_x + 12, pad_y + 52), _FONT, 0.7, _TEXT_COLOR, 2, cv2.LINE_AA)

    # Action icons (click/drag/scroll) as small circles
    icon_x = pad_x + 12
    icon_y = pad_y + 72
    spacing = 62

    # Click
    click_on = bool(action_state.get("click", False))
    color = _GOOD if click_on else (180,180,180)
    cv2.circle(frame_bgr, (icon_x, icon_y), 10, color, -1)
    cv2.putText(frame_bgr, "Click", (icon_x + 18, icon_y + 6), _FONT, 0.5, _TEXT_COLOR, 1, cv2.LINE_AA)

    # Drag
    drag_on = bool(action_state.get("drag", False))
    color = _GOOD if drag_on else (180,180,180)
    cv2.circle(frame_bgr, (icon_x + spacing, icon_y), 10, color, -1)
    cv2.putText(frame_bgr, "Drag", (icon_x + spacing + 18, icon_y + 6), _FONT, 0.5, _TEXT_COLOR, 1, cv2.LINE_AA)

    # Scroll
    scroll_on = bool(action_state.get("scroll", False))
    color = _GOOD if scroll_on else (180,180,180)
    cv2.circle(frame_bgr, (icon_x + spacing*2, icon_y), 10, color, -1)
    cv2.putText(frame_bgr, "Scroll", (icon_x + spacing*2 + 18, icon_y + 6), _FONT, 0.5, _TEXT_COLOR, 1, cv2.LINE_AA)

    # Draw landmarks if provided (normalized coords list)
    if landmarks:
        # draw light skeleton: small circle for each landmark and thin lines for a finger grouping
        # to keep CPU low we draw only key landmarks (tips and some connections)
        key_indices = [
            0, 1, 2, 3, 4,     # thumb
            5, 6, 7, 8,        # index
            9, 10, 11, 12,     # middle
            13, 14, 15, 16,    # ring
            17, 18, 19, 20     # pinky
        ]
        # draw connections for each finger (simple)
        finger_conns = [
            (0,1,2,3,4),
            (5,6,7,8),
            (9,10,11,12),
            (13,14,15,16),
            (17,18,19,20)
        ]
        # scale factor for circles
        r = max(2, int(min(w,h) * 0.006))
        for fidxs in finger_conns:
            pts = []
            for idx in fidxs:
                if idx < len(landmarks):
                    x,y = landmarks[idx]
                    px,py = _norm_to_px(x,y,w,h)
                    pts.append((px,py))
                    cv2.circle(frame_bgr, (px,py), r, (0,255,0), -1)
            # draw polyline for the finger
            if len(pts) >= 2:
                cv2.polylines(frame_bgr, [np.array(pts, dtype=np.int32)], False, (0,200,80), 1, cv2.LINE_AA)

    # Debug tiny caption bottom-left
    if debug:
        debug_text = "DEBUG MODE"
        cv2.putText(frame_bgr, debug_text, (12, h - 12), _FONT, 0.5, _WARN, 1, cv2.LINE_AA)

    return frame_bgr


# To avoid a top-level heavy import (numpy) if not needed, import lazily
import numpy as np
file_path:
d:\Motion Control System\overlay_renderer.py
