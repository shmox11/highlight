# Import necessary libraries
import sys  # Library for interacting with the Python runtime
import os  # Library for interacting with the operating system

# The following line is commented out, but if uncommented, it would add the parent directory of the current script to the system path.
# This can be useful if you want to import modules from the parent directory.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Define a function to get the center region of interest (ROI) from a video frame
def get_center_roi(frame):
    # Define the top-left and bottom-right coordinates of the ROI
    top_left = (950, 525)
    bottom_right = (1100, 715)
    
    # Extract the ROI from the frame using the defined coordinates
    roi = frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
    
    # Return the extracted ROI and its coordinates
    return roi, top_left, bottom_right
