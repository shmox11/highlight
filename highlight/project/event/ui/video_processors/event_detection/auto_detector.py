#auto_detector.py

import cv2
import os

class AutoEventDetector:
    def __init__(self, video_path, detector, skip_frames=20):
        self.video_path = video_path
        self.detector = detector
        self.skip_frames = skip_frames

    def detect_events(self):
        cap = cv2.VideoCapture(self.video_path)
        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        detected_events = []
        i = 0

        while i < total_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                event, loc = self.detector.detect_event(frame)
                if event:
                    timestamp = i / frame_rate
                    detected_events.append((timestamp, event))
                    
                    # Highlight the detected event on the frame
                    if loc:  # If a location is returned
                        cv2.rectangle(frame, loc, (loc[0] + 50, loc[1] + 50), (0, 255, 0), 2)  # Adjust size as needed
                        if event:
                            print(f"Detected {event} at location {loc}")

                    # Display the frame
                    cv2.imshow("Event Detection", frame)
                    cv2.waitKey(1)  # Display for a short duration
                    
                    # Analyze the next 5 frames more closely
                    i += 5
                    continue
                
            i += self.skip_frames
        
        cap.release()
        cv2.destroyAllWindows()
        return detected_events