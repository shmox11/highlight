#shield_break.py

# Import necessary libraries and modules
import cv2  # OpenCV library for computer vision tasks
import os  # Library for interacting with the operating system
import numpy as np  # Library for mathematical operations
from ...event_detection.regions.center_roi import get_center_roi  # Import the function to get the center region of interest (ROI)
from ...event_detection.preprocessingsettingsdialog import PreprocessingSettingsDialog
from ...event_detection import preprocessing
from ...event_detection.preprocess_handler import PreprocessingHandler 
import logging  # Library for logging information

# Set the logging level to INFO to display informational messages
logging.basicConfig(level=logging.INFO)

# Define a function to get templates of the "shield break" icon
def get_shield_break_templates():
    # Get the directory path of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to the directory containing "shield break" icon templates
    template_dir = os.path.join(script_dir, 'thumbnail', 'shield_break')
    
    # Read all the image templates from the directory and store them in a list
    templates = [cv2.imread(os.path.join(template_dir, f)) for f in os.listdir(template_dir) if f.endswith('.png')]
    
    # Return the list of templates
    return templates

# Define a function to detect the "shield break" event in a video frame
def detect_shield_break_event(frame, threshold=0.8, preprocessing_settings=None):
    # Extract the center region of interest (ROI) from the frame
    roi, top_left, bottom_right = get_center_roi(frame)
    roi = frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

    # Apply preprocessing if settings are provided
    if preprocessing_settings:
        roi = apply_preprocessing(roi, preprocessing_settings)  # Apply preprocessing to the ROI
        print(f"Applied preprocessing to ROI")
    else:
        print(f"Skipped preprocessing for ROI")

    # Get the list of "shield break" icon templates
    templates = get_shield_break_templates()

    # Initialize variables to store the best match value and location
    best_match_val = -1
    best_match_loc = None


    # Define a range of scales to resize the templates for matching
    scales = [i for i in range(50, 151, 10)]  # Scales from 0.5x to 1.5x in steps of 0.1x

    if roi.dtype != np.uint8:
        roi = (roi * 255).astype(np.uint8)

    # Loop through each scale and template to find the best match
    for scale in scales:
        for template in templates:
            # Resize the template based on the current scale
            resized_template = cv2.resize(template, (int(template.shape[1] * scale / 100), int(template.shape[0] * scale / 100)))

            # Apply preprocessing to the template if settings are provided
            if preprocessing_settings:
                processed_template = apply_preprocessing(resized_template, preprocessing_settings)
                print(f"Applied preprocessing to template {template}")
            else:
                processed_template = resized_template
                print(f"Skipped preprocessing for template {template}")
            # Skip the template if it's larger than the ROI
            if roi.shape[0] < template.shape[0] or roi.shape[1] < template.shape[1]:
                continue
            


            if processed_template.dtype != np.uint8:
                processed_template = (processed_template * 255).astype(np.uint8)



            # Perform template matching to find the location of the template in the ROI
            result = cv2.matchTemplate(roi, processed_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            # Update the best match value and location if the current match is better
            if max_val > best_match_val:
                best_match_val = max_val
                best_match_loc = (max_loc[0] + top_left[0], max_loc[1] + top_left[1])

    # Check if the best match value exceeds the given threshold
    if best_match_val > threshold:
        # Print the location and confidence of the detected event
        print(f"Shield Break detected at location: {best_match_loc}")
        print(f"Match confidence: {best_match_val*100:.2f}%")
        return True, best_match_loc  # Return True and the location if the event is detected
    else:
        return False, None  # Return False and None if the event is not detected

# Modify the apply_preprocessing function to handle the settings format
def apply_preprocessing(img, settings):
    for method, params in settings.items():
        func = getattr(preprocessing, method)
        img = func(img, **params)
    return img

