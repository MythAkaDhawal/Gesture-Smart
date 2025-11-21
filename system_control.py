import pyautogui
import platform
import time
import threading


class SystemController:
    """
    Controls the PC based on recognized gestures.
    Integrated with API start/stop/recalibrate commands.
    """

    def __init__(self, config=None):
        self.config = config

        # Screen info
        self.screen_width, self.screen_height = pyautogui.size()

        # Real-time responsiveness
        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = False

        # Mouse smoothing
        self.prev_x, self.prev_y = self.screen_width / 2, self.screen_height / 2

        # System state
        self.status = "idle"           # idle | running | stopped
        self.running = False           # internal boolean lock
        self.recalibrated = False

        # Thread lock
        self._lock = threading.Lock()

    # ----------------------------------------------------
    # API INTEGRATION FUNCTIONS
    # ----------------------------------------------------

    def start_system(self):
        """Activate gesture-based system."""
        with self._lock:
            self.running = True
            self.status = "running"
        print("[SYSTEM] Gesture control started.")

    def stop_system(self):
        """Deactivate gesture-based system."""
        with self._lock:
            self.running = False
            self.status = "stopped"
        print("[SYSTEM] Gesture control stopped.")

    def recalibrate(self):
        """Reset internal smoothing + positions."""
        with self._lock:
            self.prev_x, self.prev_y = self.screen_width / 2, self.screen_height / 2
            self.recalibrated = True
        print("[SYSTEM] Recalibration completed.")
        return "Recalibration successful."

    # ----------------------------------------------------
    # UTILITY FUNCTIONS
    # ----------------------------------------------------

    def _map_coordinates(self, x, y, frame_width, frame_height):
        """Convert camera coordinates → screen coordinates with margin."""
        if not self.config:
            raise ValueError("Config object missing.")

        x = frame_width - x  # Mirror horizontally

        x = max(self.config.FRAME_MARGIN, min(frame_width - self.config.FRAME_MARGIN, x))
        y = max(self.config.FRAME_MARGIN, min(frame_height - self.config.FRAME_MARGIN, y))

        screen_x = (x - self.config.FRAME_MARGIN) * self.screen_width / (frame_width - 2 * self.config.FRAME_MARGIN)
        screen_y = (y - self.config.FRAME_MARGIN) * self.screen_height / (frame_height - 2 * self.config.FRAME_MARGIN)

        return screen_x, screen_y

    def move_mouse(self, x, y, frame_width, frame_height):
        """Move mouse smoothly."""
        if not self.running:
            return

        target_x, target_y = self._map_coordinates(x, y, frame_width, frame_height)

        smooth_x = self.config.CURSOR_SMOOTHING * self.prev_x + (1 - self.config.CURSOR_SMOOTHING) * target_x
        smooth_y = self.config.CURSOR_SMOOTHING * self.prev_y + (1 - self.config.CURSOR_SMOOTHING) * target_y

        pyautogui.moveTo(smooth_x, smooth_y)
        self.prev_x, self.prev_y = smooth_x, smooth_y

    # ----------------------------------------------------
    # BASIC INPUT FUNCTIONS
    # ----------------------------------------------------

    def left_click(self):
        if self.running:
            pyautogui.click(button='left')

    def right_click(self):
        if self.running:
            pyautogui.click(button='right')

    def start_drag(self):
        if self.running:
            pyautogui.mouseDown(button='left')

    def release_hold(self):
        if self.running:
            pyautogui.mouseUp(button='left')

    def scroll(self, direction):
        if not self.running:
            return

        amount = self.config.SCROLL_SPEED
        if direction == 'UP':
            pyautogui.scroll(amount)
        elif direction == 'DOWN':
            pyautogui.scroll(-amount)

    def zoom(self, direction):
        if not self.running:
            return

        modifier = 'command' if platform.system() == "Darwin" else 'ctrl'

        pyautogui.keyDown(modifier)
        if direction == 'IN':
            pyautogui.scroll(1)
        elif direction == 'OUT':
            pyautogui.scroll(-1)
        pyautogui.keyUp(modifier)

    # ----------------------------------------------------
    # ADVANCED NAVIGATION
    # ----------------------------------------------------

    def switch_tabs(self, direction):
        if not self.running:
            return

        if direction == 'NEXT':
            pyautogui.hotkey('ctrl', 'tab')
        elif direction == 'PREV':
            pyautogui.hotkey('ctrl', 'shift', 'tab')

    def switch_desktops(self, direction):
        if not self.running:
            return

        os_type = platform.system()
        if os_type == "Windows":
            if direction == 'LEFT':
                pyautogui.hotkey('win', 'ctrl', 'left')
            elif direction == 'RIGHT':
                pyautogui.hotkey('win', 'ctrl', 'right')

        elif os_type == "Darwin":  # macOS
            if direction == 'LEFT':
                pyautogui.hotkey('ctrl', 'left')
            elif direction == 'RIGHT':
                pyautogui.hotkey('ctrl', 'right')

    # ----------------------------------------------------
    # GESTURE DISPATCH
    # ----------------------------------------------------

    def handle_gesture(self, gesture, hands_data, frame_shape):
        """Main gesture dispatcher."""
        if not self.running:
            return

        frame_height, frame_width, _ = frame_shape

        # Cursor movement
        if gesture in ["CURSOR_MOVE", "DRAG_HOLD"]:
            if hands_data:
                lm = hands_data[0]['landmarks'][self.config.CURSOR_LANDMARK]
                self.move_mouse(lm[0], lm[1], frame_width, frame_height)

        # Simple actions
        elif gesture == "LEFT_CLICK":
            self.left_click()
        elif gesture == "RIGHT_CLICK":
            self.right_click()
        elif gesture == "START_DRAG":
            self.start_drag()
        elif gesture == "RELEASE_HOLD":
            self.release_hold()

        # Scroll
        elif isinstance(gesture, dict) and gesture.get("gesture") == "SCROLL":
            self.scroll(gesture['direction'])

        # Zoom
        elif gesture in ["ZOOM_IN", "ZOOM_OUT"]:
            self.zoom(gesture.split('_')[1])

        # Tab switching
        elif isinstance(gesture, dict) and gesture.get("gesture") == "SWITCH_TABS":
            self.switch_tabs(gesture['direction'])

        # Desktop navigation
        elif isinstance(gesture, dict) and gesture.get("gesture") == "SWITCH_DESKTOPS":
            self.switch_desktops(gesture['direction'])

        # Unknown gestures ignored safely
        else:
            pass
