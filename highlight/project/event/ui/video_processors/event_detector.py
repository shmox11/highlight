# event_detector.py

# Import necessary functions and modules
from .event_detection.events.down_event import detect_down_event  # Import the function to detect the "down_event"
from .event_detection.events.shield_break import detect_shield_break_event  # Import the function to detect the "shield_break_event"
import logging  # Library for logging information
from .event_detection.preprocess_handler import PreprocessingHandler

# Set the logging level to INFO to display informational messages
logging.basicConfig(level=logging.INFO)

def detect_all_events(frame, threshold=0.8, preprocessing_settings=None, event_type=None):
    """
    Detects all events in the given frame.
    
    Args:
        frame: The video frame in which to detect events.
        threshold: The threshold for event detection.
        preprocessing_settings: The settings for preprocessing the frame.
        event_type: The type of event for which preprocessing should be applied. Default is None.
        
    Returns:
        A dictionary of detected events.
    """
    # Create an empty dictionary to store detected events
    events = {}

    # Detect the down_event without preprocessing
    is_down_event, location = detect_down_event(frame, threshold)
    if is_down_event:
        events["down_event"] = location
        print("Down event detected!")

    # Check if preprocessing should be applied for shield_break_event
    if event_type == "shield_break_event" and preprocessing_settings is not None:
        print("Applying preprocessing for shield break event...")
        handler = PreprocessingHandler(preprocessing_settings)
        processed_frame = handler.apply_preprocessing(frame)
        is_shield_break_event, location = detect_shield_break_event(processed_frame, threshold)
    else:
        is_shield_break_event, location = detect_shield_break_event(frame, threshold)

    # If a "shield_break_event" is detected, add it to the events dictionary
    if is_shield_break_event:
        events["shield_break_event"] = location
        print("Shield break event detected!")

    # Return the dictionary of detected events
    return events
