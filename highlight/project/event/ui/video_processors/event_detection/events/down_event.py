import os
import cv2
from ..regions.center_region import CenterRegion

class DownEvent:
    def __init__(self, threshold=0.7, templates=None):
        self.threshold = threshold
        self.templates = templates if templates else self._load_templates("center_down_icon")

    def _load_templates(self, event_type):
        """Load templates for the given event type."""
        template_dir = os.path.join("thumbnail", event_type)
        print(f"Attempting to access directory: {template_dir}")
        return [(cv2.imread(os.path.join(template_dir, path), cv2.IMREAD_GRAYSCALE), os.path.join(template_dir, path)) for path in os.listdir(template_dir) if path.endswith('.png')]

    def detect_down_event(self, frame):
        """Detect the 'Down' event using template matching."""
        self.location = None  # Initialize location to None
        roi_gray = CenterRegion.get_roi(frame)  # Get the grayscale ROI using the CenterRegion class
        for template, template_path in self.templates:
            result = cv2.matchTemplate(roi_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val > self.threshold:
                self.location = max_loc  # Store the location
                print(f"Matched with template: {template_path}")  # Print the path of the matched template
                return True
        return False
