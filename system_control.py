import pyautogui
import platform
import time

class SystemController:
    """
    Maps recognized gestures to system actions using pyautogui.
    Handles mouse movement, clicks, scrolling, and keyboard shortcuts.
    """
    def __init__(self, config):
        """
        Initializes the SystemController.

        Args:
            config: A configuration object with control parameters.
        """
        self.config = config
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Disable pyautogui pause for real-time control
        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = False

        # For mouse movement smoothing
        self.prev_x, self.prev_y = self.screen_width / 2, self.screen_height / 2

    def _map_coordinates(self, x, y, frame_width, frame_height):
        """
        Maps hand coordinates from the camera frame to screen coordinates.
        Includes a margin to prevent hitting screen edges unintentionally.
        """
        # Invert x-axis because the camera image is flipped
        x = frame_width - x

        # Apply margin
        x = max(self.config.FRAME_MARGIN, min(frame_width - self.config.FRAME_MARGIN, x))
        y = max(self.config.FRAME_MARGIN, min(frame_height - self.config.FRAME_MARGIN, y))

        # Map to screen coordinates
        screen_x = (x - self.config.FRAME_MARGIN) * self.screen_width / (frame_width - 2 * self.config.FRAME_MARGIN)
        screen_y = (y - self.config.FRAME_MARGIN) * self.screen_height / (frame_height - 2 * self.config.FRAME_MARGIN)

        return screen_x, screen_y

    def move_mouse(self, x, y, frame_width, frame_height):
        """
        Moves the mouse to the specified coordinates with smoothing.

        Args:
            x (float): The x-coordinate from the hand landmark.
            y (float): The y-coordinate from the hand landmark.
            frame_width (int): The width of the camera frame.
            frame_height (int): The height of the camera frame.
        """
        target_x, target_y = self._map_coordinates(x, y, frame_width, frame_height)

        # Apply exponential moving average for smoothing
        smooth_x = self.config.CURSOR_SMOOTHING * self.prev_x + (1 - self.config.CURSOR_SMOOTHING) * target_x
        smooth_y = self.config.CURSOR_SMOOTHING * self.prev_y + (1 - self.config.CURSOR_SMOOTHING) * target_y

        pyautogui.moveTo(smooth_x, smooth_y)
        self.prev_x, self.prev_y = smooth_x, smooth_y

    def left_click(self):
        pyautogui.click(button='left')

    def right_click(self):
        pyautogui.click(button='right')

    def start_drag(self):
        pyautogui.mouseDown(button='left')

    def release_hold(self):
        pyautogui.mouseUp(button='left')

    def scroll(self, direction):
        amount = self.config.SCROLL_SPEED
        if direction == 'UP':
            pyautogui.scroll(amount)
        elif direction == 'DOWN':
            pyautogui.scroll(-amount)

    def zoom(self, direction):
        if platform.system() == "Darwin": # macOS uses 'command' key
            modifier = 'command'
        else: # Windows/Linux use 'ctrl'
            modifier = 'ctrl'
            
        if direction == 'IN':
            pyautogui.hotkey(modifier, '+')
        elif direction == 'OUT':
            pyautogui.hotkey(modifier, '-')

    def switch_tabs(self, direction):
        if direction == 'NEXT':
            pyautogui.hotkey('ctrl', 'tab')
        elif direction == 'PREV':
            pyautogui.hotkey('ctrl', 'shift', 'tab')

    def switch_desktops(self, direction):
        if platform.system() == "Windows":
            if direction == 'LEFT':
                pyautogui.hotkey('win', 'ctrl', 'left')
            elif direction == 'RIGHT':
                pyautogui.hotkey('win', 'ctrl', 'right')
        # macOS desktop switching can be more complex (e.g., 'ctrl', 'left'/'right')
        # and often needs to be enabled in System Preferences.
        elif platform.system() == "Darwin":
            if direction == 'LEFT':
                pyautogui.hotkey('ctrl', 'left')
            elif direction == 'RIGHT':
                pyautogui.hotkey('ctrl', 'right')

    def handle_gesture(self, gesture, hands_data, frame_shape):
        """
        Dispatches the recognized gesture to the appropriate system action.

        Args:
            gesture (str or dict): The gesture event from GestureRecognizer.
            hands_data (list): The list of hand data from HandTracker.
            frame_shape (tuple): The (height, width) of the camera frame.
        """
        frame_height, frame_width, _ = frame_shape

        if gesture == "NONE":
            return

        if gesture == "CURSOR_MOVE":
            if hands_data:
                # Use index finger tip for cursor control
                landmark_pos = hands_data[0]['landmarks'][8]
                self.move_mouse(landmark_pos[0], landmark_pos[1], frame_width, frame_height)
        elif gesture == "LEFT_CLICK":
            self.left_click()
        elif gesture == "RIGHT_CLICK":
            self.right_click()
        elif gesture == "START_DRAG":
            self.start_drag()
        elif gesture == "DRAG_HOLD":
            # While dragging, keep updating mouse position
            if hands_data:
                landmark_pos = hands_data[0]['landmarks'][8]
                self.move_mouse(landmark_pos[0], landmark_pos[1], frame_width, frame_height)
        elif gesture == "RELEASE_HOLD":
            self.release_hold()
        elif isinstance(gesture, dict) and gesture.get('gesture') == 'SCROLL':
            self.scroll(gesture['direction'])
        elif gesture in ["ZOOM_IN", "ZOOM_OUT"]:
            self.zoom(gesture.split('_')[1])
        elif isinstance(gesture, dict) and gesture.get('gesture') == 'SWITCH_TABS':
            self.switch_tabs(gesture['direction'])
        elif isinstance(gesture, dict) and gesture.get('gesture') == 'SWITCH_DESKTOPS':
            self.switch_desktops(gesture['direction'])


if __name__ == '__main__':
    # This is a placeholder for a config object for testing
    class MockConfig:
        CURSOR_SMOOTHING = 0.7
        FRAME_MARGIN = 100
        SCROLL_SPEED = 20

    controller = SystemController(config=MockConfig())

    print("Testing SystemController. Move your mouse to see the script take over.")
    print("Testing mouse movement for 3 seconds...")
    
    # Mock frame dimensions
    frame_w, frame_h = 640, 480
    
    # Simulate moving mouse in a square
    start_time = time.time()
    while time.time() - start_time < 3:
        controller.move_mouse(200, 200, frame_w, frame_h) # Top-left
        time.sleep(0.1)
        controller.move_mouse(440, 200, frame_w, frame_h) # Top-right
        time.sleep(0.1)
        controller.move_mouse(440, 280, frame_w, frame_h) # Bottom-right
        time.sleep(0.1)
        controller.move_mouse(200, 280, frame_w, frame_h) # Bottom-left
        time.sleep(0.1)

    print("\nTesting click...")
    controller.left_click()
    print("A left click was performed.")
    time.sleep(1)

    print("\nTesting scroll...")
    controller.scroll('UP')
    print("Scrolled up.")
    time.sleep(1)

    print("\nTesting zoom...")
    controller.zoom('IN')
    print("Zoomed in (Ctrl+).")
    time.sleep(1)

    print("\nTest complete.")
file_path:
d:\Motion Control System\system_control.py