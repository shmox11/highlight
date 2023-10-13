# Import necessary functions and modules
from .event_detection.events.down_event import detect_down_event  # Import the function to detect the "down_event"
from .event_detection.events.shield_break import detect_shield_break_event  # Import the function to detect the "shield_break_event"
import logging  # Library for logging information
from .event_detection.preprocess_handler import PreprocessingHandler



# Set the logging level to INFO to display informational messages
logging.basicConfig(level=logging.INFO)

def detect_all_events(frame, threshold=0.8, preprocessing_settings=None):
    # Create an empty dictionary to store detected events
    events = {}

    # Detect the down_event without preprocessing
    is_down_event, location = detect_down_event(frame, threshold)
    if is_down_event:
        events["down_event"] = location

    # Apply preprocessing to the frame for shield_break_event
    handler = PreprocessingHandler(preprocessing_settings)
    processed_frame_for_shield_break_event = handler.apply_preprocessing(frame)
    is_shield_break_event, location = detect_shield_break_event(processed_frame_for_shield_break_event, threshold, preprocessing_settings)

    # If a "shield_break_event" is detected, add it to the events dictionary
    if is_shield_break_event:
        events["shield_break_event"] = location

    # Return the dictionary of detected events
    return events
