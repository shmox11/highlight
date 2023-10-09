# center_region.py
import os
import cv2

class CenterRegion:
    def __init__(self):
        pass

    def _get_roi_gray(self, frame):
        """Extract the center region of interest (ROI) from the frame and convert it to grayscale."""
        height, width = frame.shape[:2]
        roi = frame[int(height*0.45):int(height*0.55), int(width*0.45):int(width*0.55)]
        return cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    def detect_shield_break(self, frame, templates):
        """Detect the 'shield break' event in the center region."""
        roi_gray = self._get_roi_gray(frame)
        for template in templates:
            result = cv2.matchTemplate(roi_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val > self.threshold:
                return True, max_loc
        return False, None

    def detect_down_icon(self, frame, templates):
        """Detect the 'down' icon in the center region."""
        roi_gray = self._get_roi_gray(frame)
        for template in templates:
            result = cv2.matchTemplate(roi_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val > self.threshold:
                return True, max_loc
        return False, None