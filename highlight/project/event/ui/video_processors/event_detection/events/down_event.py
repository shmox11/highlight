import os
import cv2
import sys
sys.path.append("/Users/ronschmidt/Applications/highlight/project/event/ui/video_processors/event_detection")
from template_manager import TemplateManager  # Import the TemplateManager class

class DownEvent:
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        # Create an instance of TemplateManager and access the templates for "center_down_icon"
        self.templates = TemplateManager().templates['center_down_icon']

    def _get_roi_gray(self, frame):
        """Get the region of interest (ROI) in grayscale."""
        height, width = frame.shape[:2]
        roi = frame[int(height*0.45):int(height*0.55), int(width*0.45):int(width*0.55)]
        return cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    def detect_down_event(self, frame):
        """Detect the 'Down' event using template matching."""
        roi_gray = self._get_roi_gray(frame)
        for template in self.templates:
            result = cv2.matchTemplate(roi_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val > self.threshold:
                return True, max_loc
        return False, None
