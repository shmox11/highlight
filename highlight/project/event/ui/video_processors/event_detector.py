import cv2
import os

class EventDetector:
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        self.templates = {
            "Shield Break": [cv2.imread(path, cv2.IMREAD_GRAYSCALE) for path in self._load_templates("shield_break")],
            "Down": [cv2.imread(path, cv2.IMREAD_GRAYSCALE) for path in self._load_templates("down")]
        }

    def _load_templates(self, event_type):
        template_dir = os.path.join("thumbnail", event_type)
        return [os.path.join(template_dir, file) for file in os.listdir(template_dir) if file.endswith('.png')]

    def detect_event(self, frame, event_type):
        roi_gray = self._get_roi_gray(frame)
        for template in self.templates[event_type]:
            result = cv2.matchTemplate(roi_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val > self.threshold:
                return True, max_loc
        return False, None

    def _get_roi_gray(self, frame):
        height, width = frame.shape[:2]
        roi = frame[int(height*0.45):int(height*0.55), int(width*0.45):int(width*0.55)]
        return cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
