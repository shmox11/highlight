#kill_feed_extractor.py
import cv2

class KillFeedExtractor:

    def __init__(self):
        pass

    def extract_kill_feed(self, frame):
        """
        Extract the kill feed region of interest (ROI) from the frame and return the ROI and its grayscale version.
        """
        # Define the coordinates for the kill feed ROI
        x_start, y_start, x_end, y_end = (5, 500, 435, 830)
        roi = frame[y_start:y_end, x_start:x_end]
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        return roi, roi_gray

    def extract_text_from_frame(self, frame):
        """
        Extract text from the kill feed ROI of the frame.
        """
        roi_gray = self.extract_kill_feed(frame)[1]
        text = cv2.image_to_string(roi_gray)
        return text
