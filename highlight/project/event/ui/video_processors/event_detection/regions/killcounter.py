# killcounter.py
import os
import cv2

class KillCounter:
    def __init__(self):
        pass

    def _get_roi_gray(self, frame, coords):
        x_start, y_start, x_end, y_end = coords
        roi = frame[y_start:y_end, x_start:x_end]
        return cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    def detect_kill_event(self, frame):
        # Define the kill_counter region
        kill_counter_coords = (1685, 5, 1910, 100)
        kill_counter_gray = self._get_roi_gray(frame, kill_counter_coords)

        # Here, you can add the template matching or any other logic specific to the kill_counter region
        # For now, I'm just returning the grayscale ROI for the kill_counter
        return kill_counter_gray

    def visualize_roi(self, frame):
        """Visualize the kill_counter ROI on the frame."""
        x_start, y_start, x_end, y_end = (1685, 5, 1910, 100)
        cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
        cv2.putText(frame, "kill_counter", (x_start, y_start - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display the frame with ROI
        cv2.imshow("Kill Counter ROI Visualization", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
