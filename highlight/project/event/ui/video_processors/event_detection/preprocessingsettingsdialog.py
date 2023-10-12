from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QRadioButton, QSlider, QLabel, QPushButton, QHBoxLayout, QComboBox, QToolTip)
from PyQt5.QtCore import Qt

from preprocessing import (adaptive_thresholding, adaptive_histogram_equalization, reduce_noise, enhance_contrast, normalize_image, detect_edges, morphological_dilation, sharpen_image, convert_to_hsv, histogram_backprojection, morphological_closing, PREPROCESSING_PIPELINE)

class PreprocessingSettingsDialog(QDialog):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Combo box for preprocessing methods
        self.methods_combo = QComboBox()
        self.methods_combo.addItems(["adaptive_thresholding", "enhance_contrast", "reduce_noise"])  # Add more methods as needed
        self.methods_combo.setToolTip("Select a preprocessing method.")
        layout.addWidget(self.methods_combo)

        # Sliders for parameters
        self.block_size_slider = QSlider(Qt.Horizontal)
        self.block_size_slider.setRange(3, 51)
        self.block_size_slider.setValue(11)
        self.block_size_slider.setSingleStep(2)
        self.block_size_slider.setToolTip("Adjust the block size for adaptive thresholding.")
        layout.addWidget(QLabel("Block Size:"))
        layout.addWidget(self.block_size_slider)

        self.C_slider = QSlider(Qt.Horizontal)
        self.C_slider.setRange(0, 10)
        self.C_slider.setValue(2)
        self.C_slider.setToolTip("Adjust the C value for adaptive thresholding.")
        layout.addWidget(QLabel("C Value:"))
        layout.addWidget(self.C_slider)

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
        self.methods_combo.setCurrentIndex(0)  # Default to the first method
        self.block_size_slider.setValue(11)
        self.C_slider.setValue(2)

    def get_selected_settings(self):
        """Return the selected preprocessing method and parameters."""
        method = self.methods_combo.currentText()
        block_size = self.block_size_slider.value()
        C_value = self.C_slider.value()
        return method, block_size, C_value
