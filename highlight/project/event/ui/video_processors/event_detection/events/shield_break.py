# shield_break.py
import cv2
import os

class ShieldBreakEvent:
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        self.templates = self._load_templates("shield_break")

    def _load_templates(self, event_type):
        template_dir = os.path.join("thumbnail", event_type)
        return [cv2.imread(os.path.join(template_dir, file), cv2.IMREAD_GRAYSCALE) for file in os.listdir(template_dir) if file.endswith('.png')]

    def detect(self, frame):
        roi_gray = self._get_roi_gray(frame)
        for template in self.templates:
            result = cv2.matchTemplate(roi_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val > self.threshold:
                return True, max_loc
        return False, None

    def _get_roi_gray(self, frame):
        height, width = frame.shape[:2]
        roi = frame[int(height*0.45):int(height*0.55), int(width*0.45):int(width*0.55)]
        return cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)