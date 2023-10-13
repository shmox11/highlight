import os
import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QCheckBox, QSlider, QLabel, QPushButton, QHBoxLayout, QToolTip)
from PyQt5.QtCore import Qt
from .preprocess_handler import PreprocessingHandler
from . import preprocessing

class PreprocessingSettingsDialog(QDialog):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Create a dictionary to store checkboxes and their associated widgets
        self.checkboxes = {}
        self.widgets = {}

        # Define the order of preprocessing steps
        ordered_steps = [
            ("normalize_image", "Normalize the image to [0, 255] range."),
            ("reduce_noise", "Reduce noise using Gaussian blur. Adjust the kernel size; larger kernels will blur more, reducing more noise but also reducing detail."),
            ("enhance_contrast", "Enhance the contrast using histogram equalization."),
            ("adaptive_histogram_equalization", "Enhance contrast using adaptive histogram equalization. Adjust the tile grid size and clip limit."),
            ("adaptive_thresholding", "Apply adaptive thresholding. Adjust block size and C value."),
            ("detect_edges", "Detect edges using Canny edge detection. Adjust low and high thresholds."),
            ("morphological_dilation", "Apply morphological dilation. Adjust the kernel size."),
            ("morphological_closing", "Apply morphological closing. Adjust the kernel size."),
            # ... Add other functions here in the order they should be applied
        ]

        # Create checkboxes and associated widgets for each preprocessing function
        for func_name, tooltip in ordered_steps:
            checkbox = QCheckBox(func_name.replace("_", " ").capitalize())
            checkbox.setToolTip(tooltip)
            layout.addWidget(checkbox)
            self.checkboxes[func_name] = checkbox

            # Create widgets for functions that require them
            if func_name == "adaptive_thresholding":
                block_size_slider = QSlider(Qt.Horizontal)
                block_size_slider.setRange(3, 51)
                block_size_slider.setValue(11)
                block_size_slider.setSingleStep(2)
                block_size_slider.setToolTip("Adjust the block size. Larger block sizes smooth over larger areas.")
                layout.addWidget(QLabel("Block Size:"))
                layout.addWidget(block_size_slider)
                self.widgets["block_size"] = block_size_slider

                C_slider = QSlider(Qt.Horizontal)
                C_slider.setRange(0, 10)
                C_slider.setValue(2)
                C_slider.setToolTip("Adjust the C value. A higher C subtracts more from the mean, making the thresholding more aggressive.")
                layout.addWidget(QLabel("C Value:"))
                layout.addWidget(C_slider)
                self.widgets["C_value"] = C_slider

            elif func_name == "reduce_noise":
                kernel_size_slider = QSlider(Qt.Horizontal)
                kernel_size_slider.setRange(3, 51)
                kernel_size_slider.setValue(5)
                kernel_size_slider.setSingleStep(2)
                kernel_size_slider.setToolTip("Adjust the kernel size for Gaussian blur. Larger kernels will blur more, reducing more noise but also reducing detail.")
                layout.addWidget(QLabel("Kernel Size:"))
                layout.addWidget(kernel_size_slider)
                self.widgets["kernel_size"] = kernel_size_slider

            # ... Add widgets for other functions as needed

        # Buttons
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        reset_button = QPushButton("Reset to Default")
        reset_button.clicked.connect(self.reset_to_default)

        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(reset_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def reset_to_default(self):
        """Reset settings to default values."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
        if "block_size" in self.widgets:
            self.widgets["block_size"].setValue(11)
        if "C_value" in self.widgets:
            self.widgets["C_value"].setValue(2)
        if "kernel_size" in self.widgets:
            self.widgets["kernel_size"].setValue(5)
        # ... Reset other settings to their default values

    def get_selected_settings(self):
        """Return the selected preprocessing methods and parameters."""
        selected_methods = [method for method, checkbox in self.checkboxes.items() if checkbox.isChecked()]

        settings = {}
        for method in selected_methods:
            if method == "adaptive_thresholding":
                block_size = self.widgets["block_size"].value()
                C_value = self.widgets["C_value"].value()
                settings[method] = {"block_size": block_size, "C_value": C_value}


            elif method == "reduce_noise":
                kernel_size = self.widgets["kernel_size"].value()
                settings[method] = {"kernel_size": kernel_size}

          # Add more conditions for other methods as needed...
            # For instance:
            # elif method == "another_method_name":
            #     some_parameter = self.widgets["some_widget_name"].value()
            #     settings[method] = {"some_parameter": some_parameter}

        return settings

    def on_btnApply_clicked(self):
        # Gather preprocessing settings
        settings = self.get_selected_settings()

        # Apply the selected preprocessing methods
        for method, params in settings.items():
            if method in [func.__name__ for func in preprocessing.PREPROCESSING_PIPELINE]:
                function_to_apply = getattr(preprocessing, method)
                # Assuming 'video' is your image or frame you want to preprocess
                if params:
                    video = function_to_apply(video, **params)
                else:
                    video = function_to_apply(video)
            else:
                print(f"Error: Unknown preprocessing method '{method}'")










    def on_btnApply_clicked(self):
        # Gather preprocessing settings
        method, block_size, C_value = self.get_selected_settings()

        # Apply the selected preprocessing method
        if method in preprocessing.PREPROCESSING_PIPELINE:
            function_to_apply = getattr(preprocessing, method)
            video = function_to_apply(video, block_size, C_value)
        else:
            print(f"Error: Unknown preprocessing method '{method}'")

#    def on_btnApply_clicked(self):
#        # Gather preprocessing settings
#        resize_value = self.resizeInput.value()
#        brightness_value = self.brightnessInput.value()
#        contrast_value = self.contrastInput.value()
#        grayscale = self.grayscaleCheckbox.isChecked()

        # Call preprocessing functions
#        video = preprocessing.resize_video(video, resize_value)
#        video = preprocessing.adjust_brightness_contrast(video, brightness_value, contrast_value)
#        if grayscale:
#            video = preprocessing.apply_grayscale(video)

        # You can now pass this preprocessed video to shield_break.py logic
