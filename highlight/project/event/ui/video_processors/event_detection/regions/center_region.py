#center_region.py
import cv2

class CenterRegion:
    @staticmethod
    def get_roi(frame, grayscale=True):
        """Extract the center region of interest (ROI) from the frame."""
        top_left_x, top_left_y, bottom_right_x, bottom_right_y = 900, 440, 1140, 730
        roi = frame[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
        
        if grayscale:
            return cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY), (top_left_x, top_left_y)
        return roi, (top_left_x, top_left_y)
