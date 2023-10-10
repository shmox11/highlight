import sys
import cv2
import os
import pytesseract
import numpy as np

sys.path.append("/Users/ronschmidt/Applications/highlight/project/event/ui/video_processors")

from event_detection.utils import Preprocessor
from event_detection.template_manager import TemplateManager
from event_detection.auto_detector import AutoEventDetector

from event_detection.events.shield_break import ShieldBreakEvent
from event_detection.events.kill_event import KillEvent
from event_detection.events.down_event import DownEvent

from event_detection.regions.kill_notification import KillNotificationText
from event_detection.regions.killcounter import KillCounter
from event_detection.regions.center_region import CenterRegion
from event_detection.regions.kill_feed_extractor import KillFeedExtractor

class EventDetector:
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        self.templates = TemplateManager().load_all_templates()
        self.kill_feed_extractor = KillFeedExtractor()

    def detect_event(self, frame):
        # Use the new classes for detection
        down_event_detector = DownEvent(threshold=self.threshold, templates=self.templates["center_down_icon"])
        if down_event_detector.detect_down_event(frame):
            return 'down', down_event_detector.location

        shield_break_event = ShieldBreakEvent(threshold=self.threshold, templates=self.templates["shield_break"])
        if shield_break_event.detect_shield_break_event(frame):
            return 'shield_break', shield_break_event.location

        kill_event = KillEvent(threshold=self.threshold, templates=self.templates)  # Pass the entire templates dictionary
        if kill_event.detect_kill_event(frame):
            return 'kill', kill_event.location

        # If no event is detected
        return None, None

        # For other events, you can continue in a similar fashion:
        # other_event = OtherEvent(frame, self.templates)
        # if other_event.is_detected():
        #     return 'other', other_event.location

        # If no event is detected

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
