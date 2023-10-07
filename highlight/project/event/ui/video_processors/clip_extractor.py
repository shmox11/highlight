import cv2
import os

class ClipExtractor:
    def __init__(self, video_path):
        self.video_path = video_path

    def extract_clip(self, start_time, end_time, event_type):
        cap = cv2.VideoCapture(self.video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        
        clip_dir = os.path.join("clips", event_type)
        os.makedirs(clip_dir, exist_ok=True)
        
        base_output_path = os.path.join(clip_dir, f"{start_time}_{end_time}.avi")
        output_path = base_output_path
        
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(clip_dir, f"{start_time}_{end_time}_{counter}.avi")
            counter += 1
        
        out = cv2.VideoWriter(output_path, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time)
        
        while cap.get(cv2.CAP_PROP_POS_MSEC) < end_time:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
        
        cap.release()
        out.release()
        return output_path
