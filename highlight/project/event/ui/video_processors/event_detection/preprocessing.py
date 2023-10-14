import os
import cv2
import numpy as np

def convert_to_uint8(img):
    """Convert the image to uint8 format."""
    if img.dtype != np.uint8:
        img = (img * 255).astype(np.uint8)
    print("Converted image to uint8 format.")
    return img

def normalize_image(img):
    """Normalize the image to [0, 255] range."""
    normalized_img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
    print("Applied normalization.")
    return convert_to_uint8(normalized_img)

def enhance_contrast(img):
    """Enhance the contrast of the image using histogram equalization."""
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    equalized_img = cv2.equalizeHist(img_gray)
    print("Enhanced contrast using histogram equalization.")
    return convert_to_uint8(equalized_img)

def reduce_noise(img, kernel_size=(5, 5)):
    """Reduce noise in the image using Gaussian blur."""
    blurred_img = cv2.GaussianBlur(img, kernel_size, 0)
    print("Reduced noise using Gaussian blur.")
    return convert_to_uint8(blurred_img)

def detect_edges(img, low_threshold=50, high_threshold=150):
    """Detect edges in the image using Canny edge detection."""
    edges = cv2.Canny(img, low_threshold, high_threshold)
    print("Detected edges using Canny edge detection.")
    return convert_to_uint8(edges)

def adaptive_histogram_equalization(img, tile_grid_size=(8, 8), clip_limit=2.0):
    """Enhance the contrast of the image using adaptive histogram equalization."""
    if len(img.shape) == 3 and img.shape[2] == 3:  # Check if the image is BGR
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img  # Image is already grayscale
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    clahe_img = clahe.apply(img_gray)
    print("Applied adaptive histogram equalization.")
    return convert_to_uint8(clahe_img)

def adaptive_thresholding(img, max_value=255, block_size=11, C=2):
    """Apply adaptive thresholding to the image."""
    if len(img.shape) == 3 and img.shape[2] == 3:  # Check if the image is BGR
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img  # Image is already grayscale
    thresholded_img = cv2.adaptiveThreshold(img_gray, max_value, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, C)
    print("Applied adaptive thresholding.")
    return convert_to_uint8(thresholded_img)

def morphological_dilation(img, kernel_size=(5, 5)):
    """Apply morphological dilation to the image."""
    kernel = np.ones(kernel_size, np.uint8)
    dilated_img = cv2.dilate(img, kernel, iterations=1)
    print("Applied morphological dilation.")
    return convert_to_uint8(dilated_img)

def morphological_closing(img, kernel_size=(5, 5)):
    """Apply morphological closing to the image."""
    kernel = np.ones(kernel_size, np.uint8)
    closed_img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    print("Applied morphological closing.")
    return convert_to_uint8(closed_img)

def histogram_backprojection(img, template):
    """Apply histogram backprojection."""
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv_template = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
    hist_template = cv2.calcHist([hsv_template], [0, 1], None, [180, 256], [0, 180, 0, 256])
    cv2.normalize(hist_template, hist_template, 0, 255, cv2.NORM_MINMAX)
    backprojected_img = cv2.calcBackProject([hsv_img], [0, 1], hist_template, [0, 180, 0, 256], 1)
    print("Applied histogram backprojection.")
    return convert_to_uint8(backprojected_img)

def sharpen_image(img):
    """Sharpen the image."""
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    sharpened_img = cv2.filter2D(img, -1, kernel)
    print("Sharpened the image.")
    return convert_to_uint8(sharpened_img)

def convert_to_hsv(img):
    """Convert the image to HSV color space."""
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    print("Converted image to HSV color space.")
    return convert_to_uint8(hsv_img)


# Note: For each function, I've added a print statement for debugging and 
# called the convert_to_uint8 function at the end to ensure the image is in the right format.

# Inline Notation:
# 1. When adding a new preprocessing function, ensure to add a print statement for debugging.
# 2. Call the convert_to_uint8 function at the end of each preprocessing function to ensure the image is in the right format.
# 3. If the new preprocessing function requires parameters, ensure to provide default values and allow them to be overridden when the function is called.


# Define a preprocessing pipeline
# This can be modified as needed without changing the core logic

PREPROCESSING_PIPELINE = [
    normalize_image,
    enhance_contrast,
    reduce_noise,  # Comment out or add back in as needed
    detect_edges,
    adaptive_histogram_equalization,
    morphological_dilation,
    sharpen_image,
    convert_to_hsv,
    adaptive_thresholding,
    morphological_closing,
    histogram_backprojection
]

def apply_preprocessing(img, pipeline=PREPROCESSING_PIPELINE):
    """Apply a series of preprocessing steps to an image."""
    for func in pipeline:
        img = func(img)
    print("Completed preprocessing pipeline.")
    return convert_to_uint8(img)