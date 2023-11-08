# clip_extractor.py
import cv2
import os

class ClipExtractor:
    def __init__(self, video_path):
        self.video_path = video_path

    def extract_clip(self, start_time, end_time, event_type):
        cap = cv2.VideoCapture(self.video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Keep the codec as 'mp4v' for MP4 format
        fourcc = cv2.VideoWriter_fourcc(*'h264')
        
        # Create a directory for each event type inside the clips directory
        event_dir = os.path.join("clips", event_type)
        os.makedirs(event_dir, exist_ok=True)
        
        # Determine the next clip number for the given event type
        existing_files = os.listdir(event_dir)
        existing_numbers = []
        for f in existing_files:
            if f.startswith(event_type) and f.endswith('.mp4'):
                try:
                    number = int(f.split('_')[-1].split('.')[0])
                    existing_numbers.append(number)
                except ValueError:
                    # Handle the case where the conversion to int fails
                    continue  # Skip this file and continue with the next
        
        next_clip_number = max(existing_numbers, default=0) + 1
        
        # Construct the output path
        output_path = os.path.join(event_dir, f"{event_type}_{next_clip_number}.mp4")
        
        out = cv2.VideoWriter(output_path, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time)
        
        while cap.get(cv2.CAP_PROP_POS_MSEC) < end_time:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                break  # If no frame is returned, break out of the loop
        
        cap.release()
        out.release()
        return output_path
