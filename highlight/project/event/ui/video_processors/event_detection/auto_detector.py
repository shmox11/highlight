# auto_detector.py

# Import necessary libraries and modules
import cv2  # OpenCV library for computer vision tasks
import json  # Library to work with JSON data
from ..event_detector import detect_all_events  # Import the function to detect all events
from ..event_detection.regions.center_roi import get_center_roi  # Import the function to get the center region of interest
import logging  # Library for logging information
from .preprocessingsettingsdialog import PreprocessingSettingsDialog
from ..event_detection.preprocess_handler import PreprocessingHandler

# Set the logging level to INFO to display informational messages
logging.basicConfig(level=logging.INFO)

class AutoEventDetector:
    # Constructor method to initialize the class
    def __init__(self, video_path, threshold=0.8, frames_to_skip=0, preprocessing_settings=None):
        self.preprocessing_settings = preprocessing_settings
        # Store the video path, threshold, and frames to skip as class attributes
        self.video_path = video_path
        self.threshold = threshold
        self.frames_to_skip = frames_to_skip

        print(f"Initialized AutoEventDetector with video_path: {self.video_path}, threshold: {self.threshold}, frames_to_skip: {self.frames_to_skip}, preprocessing_settings: {self.preprocessing_settings}")

    # Method to play and process the video
    def play_video(self):
        print("Starting play_video method...")
        cv2.namedWindow('Video Playback', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Video Playback', 800, 600)
        cv2.moveWindow('Video Playback', 0, 0)

        # Open the video file
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print("Error: Couldn't open the video file.")
            return

        # Get the frame rate of the video
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"Video FPS: {fps}")

        # Initialize the frame number to 0
        frame_number = 0

        # Loop through each frame of the video
        while cap.isOpened():
            # Increment the frame number
            frame_number += 1

            # Read the next frame from the video
            ret, frame = cap.read()
            # If there's no frame left, exit the loop
            if not ret:
                break

            # Extract the region of interest from the frame
            _, top_left, bottom_right = get_center_roi(frame)
            roi = frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

            # Draw a green rectangle around the region of interest on the frame
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

            # Detect events in the frame
            # Here, we specify the event type for which we want to apply preprocessing
            events = detect_all_events(frame, self.threshold, preprocessing_settings=self.preprocessing_settings, event_type="shield_break_event")

            # If a "down_event" is detected, draw a blue rectangle on the frame
            if "down_event" in events:
                event_top_left = events["down_event"]
                event_bottom_right = (event_top_left[0] + 50, event_top_left[1] + 50)
                cv2.rectangle(frame, event_top_left, event_bottom_right, (255, 0, 0), 2)

                # Print the timestamp of the detected event
                timestamp = frame_number / fps
                minutes = int(timestamp // 60)
                seconds = int(timestamp % 60)
                print(f"Down Event detected at {minutes}:{seconds:02}:{frame_number}")

            # If a "shield_break_event" is detected, draw a Yellow rectangle on the frame
            if "shield_break_event" in events:
                event_top_left = events["shield_break_event"]
                event_bottom_right = (event_top_left[0] + 50, event_top_left[1] + 50)
                cv2.rectangle(frame, event_top_left, event_bottom_right, (0, 255, 255), 2)

                # Print the timestamp of the detected event
                timestamp = frame_number / fps
                minutes = int(timestamp // 60)
                seconds = int(timestamp % 60)
                print(f"Shield Break Event detected at {minutes}:{seconds:02}:{frame_number}")

            # Display the frame
            cv2.imshow('Video Playback', frame)

            # If frames are being skipped, jump to the specified frame number
            if self.frames_to_skip > 0:
                frame_number += self.frames_to_skip
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

            # If the 'q' key is pressed, exit the loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exiting playback due to 'q' key press.")
                break

        # Release the video capture object and close all OpenCV windows
        cap.release()
        cv2.destroyAllWindows()
        print("Finished play_video method.")
