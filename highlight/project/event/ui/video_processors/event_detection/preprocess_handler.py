import os
import sys
import json  # Ensure json is imported

# Import the necessary preprocessing functions.
# These are the functions you've defined in your preprocessing.py module.
from .preprocessing import (
    enhance_contrast,
    reduce_noise,
    detect_edges,
    adaptive_histogram_equalization,
    adaptive_thresholding,
    normalize_image,
    sharpen_image,
    convert_to_hsv,
    morphological_dilation,
    morphological_closing,
    histogram_backprojection,
    # ... Add other preprocessing functions as needed
)

# ... [same imports as before]

"""class PreprocessingHandler:
    CONFIG_FILE = 'settings.json'
    def __init__(self, settings=None):
        """
       # Initialize the PreprocessingHandler with optional settings.

       # :param settings: A dictionary containing preprocessing settings.
"""        self.settings = settings or {}
        print("Initialized PreprocessingHandler with settings:", self.settings)
    @staticmethod
    def load_preprocessing_settings():
        if os.path.exists(PreprocessingSettingsDialog.CONFIG_FILE):
            with open(PreprocessingSettingsDialog.CONFIG_FILE, 'r') as file:
                print("Loaded preprocessing settings from config file.")
                return json.load(file)
        print("No preprocessing settings found in config file.")
        return {}

    def apply_preprocessing(self, frame):
        """
       # Apply preprocessing methods to the frame based on the settings.

       # :param frame: The input frame (image) to be preprocessed.
       # :return: The preprocessed frame.

"""       # Example: If 'enhance_contrast' is a method selected in the settings dialog:
        if self.settings.get("method") == "enhance_contrast":
            frame = enhance_contrast(frame)
            print("Applied enhance_contrast.")
        
        # If 'reduce_noise' is selected and has parameters:
        if self.settings.get("method") == "reduce_noise":
            kernel_size = self.settings.get("kernel_size", (5, 5))  # Default value if not provided
            frame = reduce_noise(frame, kernel_size)
            print(f"Applied reduce_noise with kernel size: {kernel_size}.")
        
        # ... Similarly, add conditions for other preprocessing methods.
        
        return frame
"""

class PreprocessingHandler:
    CONFIG_FILE = 'settings.json'

    def __init__(self):
        """
        Initialize the PreprocessingHandler and load the settings.
        """
        self.settings = self.load_preprocessing_settings()
        print("Initialized PreprocessingHandler with settings:", self.settings)

    @staticmethod
    def load_preprocessing_settings():
        if os.path.exists(PreprocessingHandler.CONFIG_FILE):
            with open(PreprocessingHandler.CONFIG_FILE, 'r') as file:
                print("Loaded preprocessing settings from config file.")
                return json.load(file)
        print("No preprocessing settings found in config file.")
        return {}

    def apply_preprocessing(self, frame):
        """
        Apply preprocessing methods to the frame based on the settings.

        :param frame: The input frame (image) to be preprocessed.
        :return: The preprocessed frame.
        """
        for method, params in self.settings.items():
            if method in dir(preprocessing):  # Check if the method exists in the preprocessing module
                func = getattr(preprocessing, method)
                if params:
                    frame = func(frame, **params)
                    print(f"Applied {method} with parameters: {params}.")
                else:
                    frame = func(frame)
                    print(f"Applied {method}.")
            else:
                print(f"Warning: Unknown preprocessing method '{method}' in settings.")
        
        return frame
