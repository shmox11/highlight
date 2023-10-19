# Import necessary libraries and modules
import cv2  # OpenCV library for computer vision tasks
import os  # Library for interacting with the operating system
from ...event_detection.regions.center_roi import get_center_roi  # Import the function to get the center region of interest (ROI)
import logging  # Library for logging information

# Set the logging level to INFO to display informational messages
logging.basicConfig(level=logging.INFO)

# Define a function to get templates of the "down" icon
def get_down_icon_templates():
    # Get the directory path of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to the directory containing "down" icon templates
    template_dir = os.path.join(script_dir, 'thumbnail', 'center_down_icon')
    
    # Read all the image templates from the directory and store them in a list
    templates = [cv2.imread(os.path.join(template_dir, f)) for f in os.listdir(template_dir) if f.endswith('.png')]

    # Return the list of templates
    return templates

# Define a function to detect the "down" event in a video frame
def detect_down_event(frame, threshold=0.8, frame_number=0):
    # Check if the frame is valid
    if frame is None or frame.size == 0:
        print("Warning: Input frame is empty or None!")
        return False, None

    # Print the dimensions of the frame
    print(f"Frame dimensions: {frame.shape}")

    # Extract the center region of interest (ROI) from the frame
    roi, top_left, bottom_right = get_center_roi(frame)

    # Check the dimensions of the extracted ROI
    if roi.size == 0 or roi.shape[0] <= 0 or roi.shape[1] <= 0:
        print(f"Warning: Invalid ROI dimensions! Top-left: {top_left}, Bottom-right: {bottom_right}")
        return False, None
    else:
        print(f"ROI dimensions: {roi.shape}")
    
    #Save the ROI for debugging
    cv2.imwrite(f"debug_roi_frame_{frame_number}.png", roi)  # Save the ROI
    # Get the list of "down" icon templates
    templates = get_down_icon_templates()
    print(f"Number of templates loaded: {len(templates)}")

    # Initialize variables to store the best match value and location
    best_match_val = -1
    best_match_loc = None

    # Define a range of scales to resize the templates for matching
    scales = [i for i in range(25, 251, 10)]  # Scales from 0.5x to 1.5x in steps of 0.1x

    # Loop through each scale and template to find the best match
    for scale in scales:
        for template in templates:
            # Resize the template based on the current scale
            resized_template = cv2.resize(template, (int(template.shape[1] * scale / 100), int(template.shape[0] * scale / 100)))

            # Skip the template if it's larger than the ROI
            if roi.shape[0] < resized_template.shape[0] or roi.shape[1] < resized_template.shape[1]:
                print(f"Warning: Skipping template with shape {resized_template.shape} because it's larger than the ROI with shape {roi.shape}")
                continue

            # Perform template matching to find the location of the template in the ROI
            result = cv2.matchTemplate(roi, resized_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            # Update the best match value and location if the current match is better
            if max_val > best_match_val:
                best_match_val = max_val
                best_match_loc = (max_loc[0] + top_left[0], max_loc[1] + top_left[1])

    # Check if the best match value exceeds the given threshold
    if best_match_val > threshold:
        # Print the location and confidence of the detected event
        print(f"Down event detected at location: {best_match_loc}")
        print(f"Match confidence: {best_match_val*100:.2f}%")
        return True, best_match_loc  # Return True and the location if the event is detected
    else:
        return False, None  # Return False and None if the event is not detected
