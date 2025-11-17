import cv2
import numpy as np
import time

class FPS:
    """
    A simple class to calculate and display the Frames Per Second.
    """
    def __init__(self):
        self.start_time = time.time()
        self.frame_count = 0
        self.fps = 0

    def update(self):
        """
        Update the frame count. Call this once per frame.
        """
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 1.0:
            self.fps = self.frame_count / elapsed_time
            self.start_time = time.time()
            self.frame_count = 0

    def get_fps(self):
        """
        Returns the current FPS value.
        """
        return self.fps

    def display_fps(self, img, origin=(10, 30), font=cv2.FONT_HERSHEY_SIMPLEX, scale=1, color=(0, 255, 0), thickness=2):
        """
        Draws the FPS count on the given image.

        Args:
            img (np.ndarray): The image to draw on.
            origin (tuple): Top-left corner of the text.
            font: The font to use.
            scale (float): The font scale.
            color (tuple): The text color in BGR.
            thickness (int): The line thickness.
        """
        fps_text = f"FPS: {self.fps:.2f}"
        cv2.putText(img, fps_text, origin, font, scale, color, thickness)


def calculate_distance(p1, p2):
    """
    Calculates the Euclidean distance between two 2D or 3D points.

    Args:
        p1 (np.ndarray or list/tuple): The first point (x, y) or (x, y, z).
        p2 (np.ndarray or list/tuple): The second point (x, y) or (x, y, z).

    Returns:
        float: The Euclidean distance.
    """
    return np.linalg.norm(np.array(p1) - np.array(p2))


def get_center_point(landmarks):
    """
    Calculates the geometric center (centroid) of a set of landmarks.

    Args:
        landmarks (np.ndarray): A (N, 2) or (N, 3) array of landmark points.

    Returns:
        np.ndarray: The center point (x, y) or (x, y, z).
    """
    return np.mean(landmarks, axis=0)

if __name__ == '__main__':
    # --- Test FPS Class ---
    print("Testing FPS class...")
    fps_counter = FPS()
    for i in range(60):
        fps_counter.update()
        # Simulate a 60 FPS stream
        time.sleep(1/60)
    print(f"Calculated FPS should be close to 60: {fps_counter.get_fps():.2f}")

    # --- Test Utility Functions ---
    print("\nTesting utility functions...")
    point1 = [0, 0, 0]
    point2 = [3, 4, 0]
    dist = calculate_distance(point1, point2)
    print(f"Distance between {point1} and {point2} should be 5.0: {dist}")

    test_landmarks = np.array([
        [0, 0],
        [10, 0],
        [10, 10],
        [0, 10]
    ])
    center = get_center_point(test_landmarks)
    print(f"Center of the square should be [5, 5]: {center}")
    
    print("\nTests complete.")
file_path:
d:\Motion Control System\utils.py