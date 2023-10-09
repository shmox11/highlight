# kill_notification_text.py
import os
import cv2
import pytesseract

class KillNotificationText:
    def __init__(self):
        pass

    def _get_roi_gray(self, frame, coords):
        x_start, y_start, x_end, y_end = coords
        roi = frame[y_start:y_end, x_start:x_end]
        return cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    def extract_kill_notification_text(self, frame):
        # Define the ROI coordinates for kill_notification_text
        coords = (520, 880, 1385, 960)
        
        # Extract the grayscale ROI
        roi_gray = self._get_roi_gray(frame, coords)
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(roi_gray)
        
        return text

    def detect_kill_notification_event(self, frame):
        # Extract text from the kill_notification_text region
        text = self.extract_kill_notification_text(frame)
        
        # Check if the text contains the keyword "KILLED:"
        if "KILLED:" in text:
            return True, text
        return False, text
