
import pyautogui

# Get screen dimensions dynamically
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# --- Camera and Frame Settings ---
# Set the resolution of the camera capture
CAM_WIDTH = 1280
CAM_HEIGHT = 720
# Margin from the edge of the camera frame to start mapping coordinates.
# This creates a dead zone, making it easier to reach screen edges.
FRAME_MARGIN = 100


# --- Hand Tracking Settings (MediaPipe) ---
MAX_HANDS = 2
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.7
# Smoothing factor for the hand landmarks. Higher values mean more smoothing
# but also more latency. (0.0 - 1.0)
LANDMARK_SMOOTHING_FACTOR = 0.6


# --- System Control Settings ---
# Smoothing for the final cursor movement. Higher values mean smoother
# but slower cursor response. (0.0 - 1.0)
CURSOR_SMOOTHING = 0.7
# The amount to scroll per gesture. Larger values mean faster scrolling.
SCROLL_SPEED = 30


# --- Gesture Recognition Settings ---
# The maximum distance (in pixels) between thumb and index finger to be
# considered a pinch.
PINCH_THRESHOLD = 35

# The minimum vertical distance (in pixels) the hand must move to trigger a scroll.
SCROLL_SENSITIVITY = 20

# The minimum change in pinch distance to trigger a zoom action.
ZOOM_SENSITIVITY = 25


# --- Debounce Settings (in frames) ---
# General time to wait before allowing the same gesture again.
DEBOUNCE_TIME = 10
# Shorter debounce for actions that can be repeated quickly.
DEBOUNCE_TIME_SHORT = 5
# Longer debounce for actions that should not be rapidly repeated.
DEBOUNCE_TIME_LONG = 15
