# event_detector.py

# Import necessary functions and modules
from .event_detection.events.down_event import detect_down_event  # Import the function to detect the "down_event"
from .event_detection.events.shield_break import detect_shield_break_event  # Import the function to detect the "shield_break_event"
import logging  # Library for logging information

# Set the logging level to INFO to display informational messages
logging.basicConfig(level=logging.INFO)
print("Logging level set to INFO.")

def detect_all_events(frame, threshold=0.8):
    """
    Detects all events in the given frame..
    
    Args:
        frame: The video frame in which to detect events.
        threshold: The threshold for event detection.
        
    Returns:
        A dictionary of detected events.
    """
#    print("Entering detect_all_events function...")
    
    # Create an empty dictionary to store detected events
    events = {}
 #   print("Initialized empty events dictionary.")

    # Detect the down_event
 #   print("Detecting down_event...")
    is_down_event, location = detect_down_event(frame, threshold)
    if is_down_event:
        events["down_event"] = location
        print("Down event detected!")

    # Detect the shield_break_event
 #   print("Detecting shield_break_event...")
    is_shield_break_event, location = detect_shield_break_event(frame, threshold)
    # If a "shield_break_event" is detected, add it to the events dictionary
    if is_shield_break_event:
        events["shield_break_event"] = location
        print("Shield break event detected!")

    # Return the dictionary of detected events
 #   print("Returning detected events dictionary.")
 # Inside detect_all_events function
    print(f"Down event detected: {is_down_event}, Location: {location}")
    print(f"Shield break event detected: {is_shield_break_event}, Location: {location}")

    return events
