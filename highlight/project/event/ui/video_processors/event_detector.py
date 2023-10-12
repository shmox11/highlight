# Import necessary functions and modules
from .event_detection.events.down_event import detect_down_event  # Import the function to detect the "down_event"
from .event_detection.events.shield_break import detect_shield_break_event  # Import the function to detect the "shield_break_event"
import logging  # Library for logging information

# Set the logging level to INFO to display informational messages
logging.basicConfig(level=logging.INFO)

# Define the function to detect all events in a frame
def detect_all_events(frame, threshold=0.8):
    # Create an empty dictionary to store detected events
    events = {}
    
    # Call the detect_down_event function to check if a "down_event" is detected in the frame
    is_down_event, location = detect_down_event(frame, threshold)
    
    # If a "down_event" is detected, add it to the events dictionary
    if is_down_event:
        events["down_event"] = location
    
    is_shield_break_event, location = detect_shield_break_event(frame, threshold, shield_break_preprocessing)

    # If a "shield_event" is detected, add it to the events dictionary
    if is_shield_break_event:
        events["shield_break_event"] = location
    # Placeholder for adding other event detection functions in the future
    # ...
    
    # Return the dictionary of detected events
    return events
