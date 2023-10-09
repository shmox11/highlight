# utils.py

import cv2
import numpy as np
import pytesseract

class Preprocessor:
    def __init__(self):
        pass

    def preprocess_roi(self, roi):
        # Convert to Grayscale
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian Blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Otsu's Thresholding
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return binary

    def isolate_colors(self, roi):
        # Convert to HSV for better color segmentation
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Define range for blue color (player name)
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([140, 255, 255])
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Define range for red color (downed player name)
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = red_mask1 + red_mask2

        # Combine the masks
        combined_mask = cv2.bitwise_or(blue_mask, red_mask)

        return combined_mask
