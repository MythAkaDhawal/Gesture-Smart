
import numpy as np
from utils import calculate_distance

class GestureRecognizer:
    """
    Recognizes gestures from hand landmark data.
    It interprets the spatial relationship of landmarks to identify specific gestures.
    """
    def __init__(self, config):
        """
        Initializes the GestureRecognizer with configuration parameters.

        Args:
            config: A configuration object or module containing all necessary thresholds.
        """
        self.config = config
        self.last_gesture = "NONE"
        self.drag_started = False
        self.last_hand_y = 0
        self.last_zoom_dist = 0
        
        # Debounce counters
        self.click_debounce_counter = 0
        self.scroll_debounce_counter = 0
        self.zoom_debounce_counter = 0
        self.tab_switch_debounce_counter = 0
        self.desktop_switch_debounce_counter = 0

    def _get_finger_states(self, landmarks):
        """
        Determines if each finger is extended or curled.
        Returns a list of booleans [thumb, index, middle, ring, pinky].
        True means extended, False means curled.
        """
        states = []
        # Landmark indices for finger tips and PIP joints
        tip_ids = [4, 8, 12, 16, 20]
        pip_ids = [3, 6, 10, 14, 18] # Proximal Interphalangeal joint

        # Thumb: Compare x-coordinate of tip to PIP
        # A more robust thumb check might be needed depending on hand orientation
        if landmarks[tip_ids[0]][0] > landmarks[pip_ids[0]][0]: # Simple check for right hand
             states.append(landmarks[tip_ids[0]][0] > landmarks[tip_ids[0]-1][0])
        else: # left hand
             states.append(landmarks[tip_ids[0]][0] < landmarks[tip_ids[0]-1][0])

        # Other fingers: Compare y-coordinate of tip to PIP
        for i in range(1, 5):
            if landmarks[tip_ids[i]][1] < landmarks[pip_ids[i]][1]:
                states.append(True)
            else:
                states.append(False)
        return states

    def recognize(self, hands_data):
        """
        The main method to recognize a gesture from the current hand data.

        Args:
            hands_data (list): A list of hand information dictionaries from HandTracker.

        Returns:
            str or dict: The recognized gesture event.
        """
        # Decrement all debounce counters
        self._update_debounce_counters()

        if not hands_data:
            if self.drag_started:
                self.drag_started = False
                return "RELEASE_HOLD"
            self.last_gesture = "NONE"
            return "NONE"

        # --- Two-Hand Gestures ---
        if len(hands_data) == 2 and self.desktop_switch_debounce_counter == 0:
            return self._recognize_two_hand_gestures(hands_data)

        # --- Single-Hand Gestures ---
        hand = hands_data[0] # Focus on the first detected hand
        landmarks = hand['landmarks']
        finger_states = self._get_finger_states(landmarks)
        
        num_fingers_up = sum(finger_states)

        # Calculate relevant distances
        index_thumb_dist = calculate_distance(landmarks[4], landmarks[8])
        middle_thumb_dist = calculate_distance(landmarks[4], landmarks[12])

        # 1. Closed Fist (Drag Start) / Release Hold
        if num_fingers_up == 0:
            if not self.drag_started:
                self.drag_started = True
                return "START_DRAG"
            else:
                return "DRAG_HOLD" # Continue dragging
        
        if num_fingers_up > 3 and self.drag_started:
            self.drag_started = False
            return "RELEASE_HOLD"

        # 2. Index-Thumb Pinch (Left Click)
        if finger_states[1] and not any(finger_states[2:]): # Index up, others down
            if index_thumb_dist < self.config.PINCH_THRESHOLD and self.click_debounce_counter == 0:
                self.click_debounce_counter = self.config.DEBOUNCE_TIME
                return "LEFT_CLICK"

        # 3. Two-Finger Pinch (Right Click)
        if finger_states[2] and not finger_states[1] and not any(finger_states[3:]): # Middle up, others down
            if middle_thumb_dist < self.config.PINCH_THRESHOLD and self.click_debounce_counter == 0:
                self.click_debounce_counter = self.config.DEBOUNCE_TIME
                return "RIGHT_CLICK"

        # 4. Zoom Gesture (Pinch In/Out)
        if num_fingers_up == 2 and finger_states[0] and finger_states[1]:
            if self.zoom_debounce_counter == 0:
                zoom_change = index_thumb_dist - self.last_zoom_dist
                if abs(zoom_change) > self.config.ZOOM_SENSITIVITY:
                    self.zoom_debounce_counter = self.config.DEBOUNCE_TIME_LONG
                    if zoom_change > 0:
                        return "ZOOM_IN"
                    else:
                        return "ZOOM_OUT"
            self.last_zoom_dist = index_thumb_dist
        else:
            self.last_zoom_dist = 0

        # 5. Scrolling (Vertical Movement)
        if num_fingers_up == 5 and self.scroll_debounce_counter == 0:
            hand_y = landmarks[0][1] # Use wrist as reference
            y_delta = hand_y - self.last_hand_y
            if abs(y_delta) > self.config.SCROLL_SENSITIVITY:
                self.scroll_debounce_counter = self.config.DEBOUNCE_TIME_SHORT
                if y_delta < 0:
                    return {'gesture': 'SCROLL', 'direction': 'UP'}
                else:
                    return {'gesture': 'SCROLL', 'direction': 'DOWN'}
            self.last_hand_y = hand_y
        else:
            self.last_hand_y = landmarks[0][1]

        # 6. Open Hand (Cursor Movement)
        if num_fingers_up >= 4:
            return "CURSOR_MOVE"

        return "NONE"

    def _recognize_two_hand_gestures(self, hands_data):
        """Recognizes gestures involving two hands."""
        hand1, hand2 = hands_data[0], hands_data[1]
        center1 = np.mean(hand1['landmarks'], axis=0)
        center2 = np.mean(hand2['landmarks'], axis=0)

        # Simple horizontal swipe detection
        # A more robust implementation would track movement over several frames
        if self.desktop_switch_debounce_counter == 0:
            # This is a simplified check. A real implementation would track initial
            # and final positions to determine a clear swipe direction.
            # For now, we assume if hands are far apart horizontally, it's a prep for a swipe.
            # The actual action should be triggered on movement.
            # This part of the logic needs refinement with state tracking.
            pass # Placeholder for more complex two-hand gesture logic

        return "NONE" # Default for two hands until more logic is added

    def _update_debounce_counters(self):
        """Decrements all active debounce counters by 1 each frame."""
        if self.click_debounce_counter > 0:
            self.click_debounce_counter -= 1
        if self.scroll_debounce_counter > 0:
            self.scroll_debounce_counter -= 1
        if self.zoom_debounce_counter > 0:
            self.zoom_debounce_counter -= 1
        if self.tab_switch_debounce_counter > 0:
            self.tab_switch_debounce_counter -= 1
        if self.desktop_switch_debounce_counter > 0:
            self.desktop_switch_debounce_counter -= 1

if __name__ == '__main__':
    # This is a placeholder for a config object for testing
    class MockConfig:
        PINCH_THRESHOLD = 30
        ZOOM_SENSITIVITY = 20
        SCROLL_SENSITIVITY = 15
        DEBOUNCE_TIME = 10
        DEBOUNCE_TIME_SHORT = 5
        DEBOUNCE_TIME_LONG = 15

    # Example usage
    recognizer = GestureRecognizer(config=MockConfig())
    
    # Mock landmark data for an index-thumb pinch
    mock_landmarks = np.zeros((21, 3))
    mock_landmarks[4] = [100, 100, 0] # Thumb tip
    mock_landmarks[8] = [110, 110, 0] # Index tip (close to thumb)
    mock_landmarks[12] = [180, 200, 0] # Middle tip (far)
    mock_landmarks[6] = [150, 180, 0] # Index PIP (below tip)

    # Simulate finger states: index up, others down
    # This is a simplified mock-up. Real data is needed.
    
    mock_hand_data = [{'landmarks': mock_landmarks, 'handedness': 'Right'}]
    
    gesture = recognizer.recognize(mock_hand_data)
    print(f"Recognized Gesture: {gesture}") # Expected: LEFT_CLICK (or NONE if debouncing)

    # Mock for open hand
    mock_landmarks_open = np.zeros((21, 3))
    # Tips higher than PIPs
    mock_landmarks_open[4] = [100, 100, 0]; mock_landmarks_open[3] = [110, 120, 0]
    mock_landmarks_open[8] = [120, 80, 0]; mock_landmarks_open[6] = [125, 120, 0]
    mock_landmarks_open[12] = [140, 75, 0]; mock_landmarks_open[10] = [145, 120, 0]
    mock_landmarks_open[16] = [160, 80, 0]; mock_landmarks_open[14] = [165, 120, 0]
    mock_landmarks_open[20] = [180, 90, 0]; mock_landmarks_open[18] = [185, 130, 0]
    
    mock_hand_data_open = [{'landmarks': mock_landmarks_open, 'handedness': 'Right'}]
    gesture = recognizer.recognize(mock_hand_data_open)
    print(f"Recognized Gesture (Open Hand): {gesture}") # Expected: CURSOR_MOVE
