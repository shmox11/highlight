import cv2
import os
import pytesseract
import numpy as np

# Importing necessary modules
from utils import Preprocessor
from template_extractor import TemplateExtractor
from auto_detector import AutoEventDetector

from event_detection.regions.kill_notification_text import KillNotificationText
from event_detection.regions.kill_counter import KillCounter
from event_detection.regions.center_region import CenterRegion
from event_detection.regions.kill_feed_extractor import KillFeedExtractor

from events.shield_break_event import ShieldBreakEvent
from events.kill_event import KillEvent
from events.down_event import DownEvent

class EventDetector:
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        self.templates = TemplateExtractor().load_all_templates()
        self.kill_feed_extractor = KillFeedExtractor()

    def detect_event(self, frame):
        # Use the new classes for detection
        down_event = DownEvent(frame, self.templates)
        if down_event.is_detected():
            return 'down', down_event.location

        shield_break_event = ShieldBreakEvent(frame, self.templates)
        if shield_break_event.is_detected():
            return 'shield_break', shield_break_event.location

        kill_event = KillEvent(frame, self.templates)
        if kill_event.is_detected():
            return 'kill', kill_event.location

        # For other events, you can continue in a similar fashion:
        # other_event = OtherEvent(frame, self.templates)
        # if other_event.is_detected():
        #     return 'other', other_event.location

        # If no event is detected
        return None, None

    def get_frame_at(self, video_path, timestamp):
        print(f"Getting frame at timestamp {timestamp}...")
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp)
        ret, frame = cap.read()
        cap.release()
        if ret:
            print("Frame extracted successfully.")
            return frame
        print("Failed to extract frame.")
        return None

    def detect_kill_feed_events(self, frame):
        print("Detecting kill feed events...")
        kill_feed_text = self.kill_feed_extractor.extract_kill_feed(frame)
        # Further processing of kill_feed_text to detect individual events
        # This will be our next step
        return kill_feed_text

    def extract_text_from_frame(self, frame):
        print("Extracting text from frame...")
        return self.kill_feed_extractor.extract_kill_feed(frame)[1]

if __name__ == "__main__":
    # Assuming you've already loaded the video and have its path in video_path variable
    video_path = "path_to_your_video.mp4"
    detector = EventDetector()
    auto_detector = AutoEventDetector(video_path, detector)
    
    detected_events = auto_detector.detect_events()
    
    # Print detected events
    for timestamp, event in detected_events:
        print(f"Detected {event} at {timestamp} seconds.")
