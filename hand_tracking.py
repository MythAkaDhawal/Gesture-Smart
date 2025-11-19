# d:\Motion Control System\hand_tracking.py
import cv2
import mediapipe as mp
import numpy as np

class HandTracker:
    """
    A class to track hands using MediaPipe and apply smoothing.
    """
    def __init__(self, static_image_mode=False, max_hands=2, model_complexity=1, 
                 detection_con=0.7, track_con=0.7, smoothing_factor=0.5):
        """
        Initializes the HandTracker.

        Args:
            static_image_mode (bool): Whether to treat the input images as a batch of static
                                      and possibly unrelated images, or a video stream.
            max_hands (int): Maximum number of hands to detect.
            model_complexity (int): Complexity of the hand landmark model: 0 or 1.
            min_detection_confidence (float): Minimum confidence value ([0.0, 1.0]) for hand
                                              detection to be considered successful.
            min_tracking_confidence (float): Minimum confidence value ([0.0, 1.0]) for the
                                             hand landmarks to be considered tracked successfully.
            smoothing_factor (float): Factor for exponential moving average smoothing (0.0-1.0).
                                      Lower values mean more smoothing.
        """
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_hands,
            model_complexity=model_complexity,
            min_detection_confidence=detection_con,
            min_tracking_confidence=track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.smoothing_factor = smoothing_factor
        self.previous_landmarks = [None] * max_hands

    def find_hands(self, frame, draw=True):
        """
        Finds hands in a BGR frame, processes them, and optionally draws landmarks.

        Args:
            frame (np.ndarray): The input image in BGR format.
            draw (bool): Whether to draw the hand landmarks and connections on the frame.

        Returns:
            tuple: A tuple containing:
                - np.ndarray: The frame with or without drawings.
                - list: A list of dictionaries, where each dictionary represents a
                        detected hand and contains its landmarks, bounding box, and handedness.
        """
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        all_hands = []
        h, w, _ = frame.shape

        if self.results.multi_hand_landmarks:
            for i, hand_landmarks in enumerate(self.results.multi_hand_landmarks):
                # Apply smoothing
                if self.previous_landmarks[i] is not None:
                    for j, landmark in enumerate(hand_landmarks.landmark):
                        prev_lm = self.previous_landmarks[i].landmark[j]
                        landmark.x = self.smoothing_factor * landmark.x + (1 - self.smoothing_factor) * prev_lm.x
                        landmark.y = self.smoothing_factor * landmark.y + (1 - self.smoothing_factor) * prev_lm.y
                        landmark.z = self.smoothing_factor * landmark.z + (1 - self.smoothing_factor) * prev_lm.z

                self.previous_landmarks[i] = hand_landmarks

                # Get landmark coordinates and bounding box
                landmarks = []
                x_list = []
                y_list = []
                for lm in hand_landmarks.landmark:
                    px, py = int(lm.x * w), int(lm.y * h)
                    landmarks.append([px, py, lm.z])
                    x_list.append(px)
                    y_list.append(py)
                
                xmin, xmax = min(x_list), max(x_list)
                ymin, ymax = min(y_list), max(y_list)
                bbox = (xmin, ymin, xmax, ymax)

                # Get handedness
                handedness = self.results.multi_handedness[i].classification[0].label

                hand_info = {
                    'landmarks': landmarks,
                    'bbox': bbox,
                    'handedness': handedness
                }
                all_hands.append(hand_info)

                if draw:
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    cv2.rectangle(frame, (bbox[0] - 20, bbox[1] - 20), 
                                  (bbox[2] + 20, bbox[3] + 20), (0, 255, 0), 2)
                    cv2.putText(frame, handedness, (bbox[0] - 30, bbox[1] - 30),
                                cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        else:
            # Reset previous landmarks if no hands are detected
            self.previous_landmarks = [None] * self.hands.max_num_hands

        return frame, all_hands

if __name__ == '__main__':
    # Example Usage
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        frame = cv2.flip(frame, 1)
        frame, hands = tracker.find_hands(frame)

        if hands:
            # Example: Get landmarks for the first hand
            hand1 = hands[0]
            lm_list1 = hand1['lm_list']
            print(f"Hand 1 (Total {len(lm_list1)} landmarks):")
            # print(lm_list1)

            if len(hands) == 2:
                hand2 = hands[1]
                lm_list2 = hand2['lm_list']
                print(f"Hand 2 (Total {len(lm_list2)} landmarks):")
                # print(lm_list2)

        cv2.imshow('Hand Tracking', frame)

        if cv2.waitKey(5) & 0xFF == 27: # Press Esc to exit
            break
            
    cap.release()
    cv2.destroyAllWindows()
    
