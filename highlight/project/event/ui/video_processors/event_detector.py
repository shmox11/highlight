import cv2
import os
import pytesseract
import numpy as np


class KillFeedExtractor:
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

    def extract_kill_feed(self, frame):
        # Using the provided coordinates for the blue box (ROI)
        x_start, y_start = 5, 500
        x_end, y_end = 435, 830
        roi = frame[y_start:y_end, x_start:x_end]

        # Preprocess the ROI
        binary = self.preprocess_roi(roi)
        
        # Isolate colors (blue and red)
        color_mask = self.isolate_colors(roi)
        
        # Combine the binary and color masks
        combined_mask = cv2.bitwise_or(binary, color_mask)

        # Save the processed ROI for visual inspection
        cv2.imwrite("processed_roi.png", combined_mask)
        cv2.imshow("Processed ROI", combined_mask)
        cv2.waitKey(0)  # Wait until a key is pressed
        cv2.destroyAllWindows()  # Close the window

        # Extract text using Tesseract with a custom configuration
        custom_config = r'--oem 3 --psm 6 outputbase digits'  # Adjust as needed
        kill_feed_text = pytesseract.image_to_string(combined_mask, config=custom_config)

        # Print the extracted text for debugging
        print(f"Extracted Kill Feed Text: {kill_feed_text}")

        return kill_feed_text



class EventDetector:
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        self.templates = self._load_all_templates()
        self.kill_feed_extractor = KillFeedExtractor()  # Initialize the KillFeedExtractor here

    def _load_all_templates(self):
        print("Loading all templates...")
        templates = {}
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.realpath(__file__))
        # Construct the path to the thumbnail directory
        thumbnail_dir = os.path.join(script_dir, 'thumbnail')
        
        # Load templates for 'down' event
        templates['down'] = [cv2.imread(path, cv2.IMREAD_GRAYSCALE) for path in self._load_templates('center_down_icon', thumbnail_dir)]
   

        for event_type in os.listdir(thumbnail_dir):
            event_dir = os.path.join(thumbnail_dir, event_type)
            if os.path.isdir(event_dir):
                templates[event_type] = [cv2.imread(path, cv2.IMREAD_GRAYSCALE) for path in self._load_templates(event_type, thumbnail_dir)]
        print("Templates loaded.")
        return templates

    def _load_templates(self, event_type, thumbnail_dir):
        print(f"Loading templates for {event_type}...")
        template_dir = os.path.join(thumbnail_dir, event_type)
        return [os.path.join(template_dir, file) for file in os.listdir(template_dir) if file.endswith('.png')]


    def detect_text_over_frames(self, video_path, target_timestamp, frame_count=5):
        cap = cv2.VideoCapture(video_path)
        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
        start_time = max(0, target_timestamp - (frame_count // 2) * frame_rate)
        
        texts = []
        for i in range(frame_count):
            cap.set(cv2.CAP_PROP_POS_MSEC, start_time + i * frame_rate)
            ret, frame = cap.read()
            if ret:
                roi = self.extract_roi(frame)
                binary = self.preprocess_roi(roi)
                red_text_mask = self.isolate_red_text(roi)
                
                # Combine binary and red text mask
                combined_mask = cv2.bitwise_or(binary, red_text_mask)
                
                text = pytesseract.image_to_string(combined_mask)
                texts.append(text)
        
        cap.release()
        
        # Use a simple voting mechanism to determine the most common text
        most_common_text = max(set(texts), key=texts.count)
        
        return most_common_text

    def _get_roi_gray(self, frame, coords):
        x_start, y_start, x_end, y_end = coords
        roi = frame[y_start:y_end, x_start:x_end]
        return cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)


    def _get_kill_feed_gray(self, frame):
        # Get the kill feed ROI directly from the extractor
        roi, _ = self.kill_feed_extractor.extract_kill_feed(frame)
        return cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    def visualize_rois(self, frame):
        """Visualize the ROIs on the frame."""
        # Define the ROIs
        rois = {
            "center": (900, 440, 1140, 730),
            "kill_feed": (5, 500, 435, 830),
            "kill_counter": (1685, 5, 1910, 100),
            "kill_notification_text": (520, 880, 1385, 960)
        }

        # Draw rectangles for each ROI
        for roi_name, coords in rois.items():
            x_start, y_start, x_end, y_end = coords
            cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
            cv2.putText(frame, roi_name, (x_start, y_start - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display the frame with ROIs
        cv2.imshow("ROIs Visualization", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    def detect_event(self, frame):
        print("Detecting event...")
        self.visualize_rois(frame.copy())  # Use a copy of the frame to avoid modifying the original

        # For 'down' event
        center_roi_gray = self._get_roi_gray(frame, (900, 440, 1140, 730))
        kill_feed_gray = self._get_roi_gray(frame, (5, 500, 435, 830))  # Assuming this is the kill feed ROI

        for template in self.templates['down']:
            # Check the center ROI
            result_center = cv2.matchTemplate(center_roi_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val_center, _, max_loc_center = cv2.minMaxLoc(result_center)

            # Check the kill feed ROI
            result_kill_feed = cv2.matchTemplate(kill_feed_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val_kill_feed, _, max_loc_kill_feed = cv2.minMaxLoc(result_kill_feed)

            if max_val_center > self.threshold or max_val_kill_feed > self.threshold:
                print(f"Detected 'down' event.")
                return 'down', max_loc_center if max_val_center > max_val_kill_feed else max_loc_kill_feed

        # For 'shield break' event
        center_roi_gray = self._get_roi_gray(frame, (900, 440, 1140, 730))
        for template in self.templates['shield_break']:
            result = cv2.matchTemplate(center_roi_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val > self.threshold:
                print(f"Detected 'shield break' event.")
                return 'shield_break', max_loc

        # For 'kill' event
        kill_counter_gray = self._get_roi_gray(frame, (1685, 5, 1910, 100))
        kill_feed_kill_gray = self._get_roi_gray(frame, (5, 500, 435, 830))
        kill_notification_text_gray = self._get_roi_gray(frame, (520, 880, 1385, 960))

        for template in self.templates['kill_counter']:
            result = cv2.matchTemplate(kill_counter_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val > self.threshold:
                print(f"Detected 'kill' event in kill counter.")
                return 'kill', max_loc

        for template in self.templates['kill_feed_kill']:
                # Check if the template is larger than the ROI
            if template.shape[0] > kill_feed_kill_gray.shape[0] or template.shape[1] > kill_feed_kill_gray.shape[1]:
                print(f"Skipping template with dimensions: {template.shape} as it's larger than the ROI.")
                continue  # Skip this iteration

            result = cv2.matchTemplate(kill_feed_kill_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val > self.threshold:
                print(f"Detected 'kill' event in kill feed.")
                return 'kill', max_loc

        # Text detection for kill_notification_text region
        text = pytesseract.image_to_string(kill_notification_text_gray)
        if "KILLED:" in text:
            print(f"Detected 'kill' event in kill notification text.")
            return 'kill', None  # No specific location for text detection

        # ... [detect other events similarly]

        print("No event detected.")
        return None, None

    def get_frame_at(self, video_path, timestamp):
        print(f"Getting frame at timestamp {timestamp}...")
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp)
        ret, frame = cap.read()
        cap.release()
        if ret:
            print("Frame extracted successfully.")
            return frame
        print("Failed to extract frame.")
        return None

    def detect_kill_feed_events(self, frame):
        print("Detecting kill feed events...")
        kill_feed_text = self.kill_feed_extractor.extract_kill_feed(frame)
        # Further processing of kill_feed_text to detect individual events
        # This will be our next step
        return kill_feed_text

    def extract_text_from_frame(self, frame):
        print("Extracting text from frame...")
        return self.kill_feed_extractor.extract_kill_feed(frame)[1]


class AutoEventDetector:
    def __init__(self, video_path, detector, skip_frames=20):
        self.video_path = video_path
        self.detector = detector
        self.skip_frames = skip_frames

    def detect_events(self):
        cap = cv2.VideoCapture(self.video_path)
        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        detected_events = []
        i = 0

        while i < total_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                event, loc = self.detector.detect_event(frame)
                if event:
                    timestamp = i / frame_rate
                    detected_events.append((timestamp, event))
                    
                    # Highlight the detected event on the frame
                    if loc:  # If a location is returned
                        cv2.rectangle(frame, loc, (loc[0] + 50, loc[1] + 50), (0, 255, 0), 2)  # Adjust size as needed
                        if event:
                            print(f"Detected {event} at location {loc}")

                    # Display the frame
                    cv2.imshow("Event Detection", frame)
                    cv2.waitKey(1)  # Display for a short duration
                    
                    # Analyze the next 5 frames more closely
                    i += 5
                    continue
                
            i += self.skip_frames
        
        cap.release()
        cv2.destroyAllWindows()
        return detected_events


if __name__ == "__main__":
    # Assuming you've already loaded the video and have its path in video_path variable
    detector = EventDetector()
    auto_detector = AutoEventDetector(video_path, detector)
    
    detected_events = auto_detector.detect_events()
    
    # Print detected events
    for timestamp, event in detected_events:
        print(f"Detected {event} at {timestamp} seconds.")


