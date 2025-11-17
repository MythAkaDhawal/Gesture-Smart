import cv2
import config
from hand_tracking import HandTracker
from gesture_recognizer import GestureRecognizer
from system_control import SystemController
from utils import FPS

def main():
    """
    The main function to run the hand gesture control system.
    """
    # --- Initialization ---
    DEBUG = True  # Set to True to print debug information

    # Initialize utilities and modules
    fps_counter = FPS()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_HEIGHT)

    tracker = HandTracker(
        max_hands=config.MAX_HANDS,
        detection_con=config.DETECTION_CONFIDENCE,
        track_con=config.TRACKING_CONFIDENCE,
        smoothing_factor=config.LANDMARK_SMOOTHING_FACTOR
    )
    recognizer = GestureRecognizer(config)
    controller = SystemController(config)

    print("Hand Gesture Control System activated. Press 'q' to quit.")

    # --- Main Loop ---
    while True:
        success, frame = cap.read()
        if not success:
            print("Warning: Could not read frame from camera. Skipping.")
            continue

        # Flip the frame horizontally for a more intuitive mirror-like view
        frame = cv2.flip(frame, 1)

        # 1. Find and process hands
        frame, hands_data = tracker.find_hands(frame)

        # 2. Recognize gesture
        gesture = recognizer.recognize(hands_data)
        
        if DEBUG and gesture != "NONE":
            print(f"Gesture: {gesture}")

        # 3. Handle gesture with system controller
        controller.handle_gesture(gesture, hands_data, frame.shape)

        # 4. Update and display FPS
        fps_counter.update()
        fps_counter.display_fps(frame)

        # 5. Display the frame
        cv2.imshow("Gesture Control", frame)

        # Exit condition
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # --- Cleanup ---
    cap.release()
    cv2.destroyAllWindows()
    print("System deactivated.")

if __name__ == '__main__':
    main()
file_path:
d:\Motion Control System\main.py