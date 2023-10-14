# shield_break.py
import cv2
import os
from ..regions.center_region import CenterRegion

class ShieldBreakEvent:
    def __init__(self, threshold=0.7, templates=None):
        self.threshold = threshold
        self.templates = templates if templates else self._load_templates("shield_break")

    def _load_templates(self, event_type):
        """Load templates for the given event type."""
        template_dir = os.path.join("thumbnail", event_type)
        print(f"Attempting to access directory: {template_dir}")
        return [cv2.imread(path, cv2.IMREAD_GRAYSCALE) for path in os.listdir(template_dir) if path.endswith('.png')]
    
    def detect_shield_break_event(self, frame):
        """Detect the 'Shield Break' event using template matching."""
        self.location = None
        roi_gray = CenterRegion.get_roi(frame)
        for template in self.templates:
            result = cv2.matchTemplate(roi_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val > self.threshold:
                self.location = max_loc
        return False