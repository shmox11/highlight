# clip_extractor.py

import cv2
import os
from metadata import MetadataManager

class ClipExtractor:
    def __init__(self, video_path, metadata_manager):
        self.video_path = video_path
        self.metadata_manager = metadata_manager

    def frame_to_time(self, frame_number):
        cap = cv2.VideoCapture(self.video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        return (frame_number / fps) * 1000

    def extract_clip(self, start_frame, end_frame, event_type):
        start_time = self.frame_to_time(start_frame)
        end_time = self.frame_to_time(end_frame)
        cap = cv2.VideoCapture(self.video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Keep the codec as 'mp4v' for MP4 format
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # Changed to 'avc1' based on your error message
        
        # Create a directory for each event type inside the clips directory
        event_dir = os.path.join("clips", event_type)
        os.makedirs(event_dir, exist_ok=True)
        
        # Determine the next clip number for the given event type
        existing_files = os.listdir(event_dir)
        existing_numbers = [int(f.split('_')[-1].split('.')[0]) for f in existing_files if f.startswith(event_type) and f.endswith('.mp4') and f.split('_')[-1].split('.')[0].isdigit()]
        
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
        
        # Provide the file path to the save_metadata method
        # Replace 'metadata.json' with the actual path to your metadata file if it's different
        self.metadata_manager.save_metadata('metadata.json')
        
        cap.release()
        out.release()
        return output_path