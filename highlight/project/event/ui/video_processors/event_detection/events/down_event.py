# down_event.py
import os
import cv2

class DownEventDetector:
    def __init__(self, threshold=0.8):
        self.templates = self._load_templates("down")
        self.threshold = threshold

    def _load_templates(self, event_type):
        """Load templates for the given event type."""
        template_dir = os.path.join("thumbnail", event_type)
        return [cv2.imread(path, cv2.IMREAD_GRAYSCALE) for path in os.listdir(template_dir) if path.endswith('.png')]

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