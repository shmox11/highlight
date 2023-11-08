# metadata.py

import cv2
import json
from PyQt5.QtCore import QSize
class MetadataManager:
    def __init__(self):
        self.metadata = {
            "video_info": {},
            "clips": [],
            "events": [],
            "roi_data_per_frame": {}  # Added to store ROI data
        }
        self.capture_roi_data_flag = False  # Flag to control the capturing of ROI data

#    def add_roi_metadata(self, frame_number, roi_data):
        # Adjusted to accept a dictionary with 'x', 'y', 'width', 'height', 'label'
 #       if frame_number not in self.metadata["roi_data_per_frame"]:
  #          self.metadata["roi_data_per_frame"][frame_number] = []
   #     self.metadata["roi_data_per_frame"][frame_number].append(roi_data)

   # def get_current_roi_data(self, current_frame_number):
    #    # Retrieve ROI data for the current frame
     #   return self.metadata["roi_data_per_frame"].get(current_frame_number, [])


 #   def start_capturing_roi_data(self):
  #      self.capture_roi_data_flag = True

  #  def stop_capturing_roi_data(self):
   #     self.capture_roi_data_flag = False

  #  def is_capturing_roi_data(self):
   #     return self.capture_roi_data_flag

    # Modify the add_metadata method to handle 'roi' category with labels
    def add_metadata(self, category, key, value, label=None):
        if category == "video_info":
            self.metadata["video_info"][key] = value
        elif category == "clip":
            self.metadata["clips"].append({key: value})
        elif category == "event":
            self.metadata["events"].append({key: value})
        elif category == "roi" and self.is_capturing_roi_data():
            if label is not None:
                self.add_roi_metadata(key, value, label)  # 'key' is the frame number, 'value' is the coordinates, 'label' is the ROI label
            else:
                print("ROI label is missing.")
        else:
            print("Invalid category or ROI data capturing is not started. Please use 'video_info', 'clip', 'event', or 'roi'.")

  #  def get_metadata(self, category=None):
    #    if category:
     #       return self.metadata.get(category, {})
      #  return self.metadata

   # def get_all_metadata(self):
        # Assuming self.metadata is a dictionary containing all the metadata
    #    return self.metadata

    def save_metadata(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.metadata, f)

#    def load_metadata(self, file_path):
 #       try:
  #          with open(file_path, 'r') as f:
   #             self.metadata = json.load(f)
    #    except FileNotFoundError:
     #       print("Metadata file not found. Starting with empty metadata.")
      #  except json.JSONDecodeError:
       #     print("Error decoding metadata. Starting with empty metadata.")


 #   def set_video_path(self, video_path):
  #      self.add_metadata('video_info', 'path', video_path)

   # def get_video_dimensions(self):
        # This method should return a QSize object or similar with video dimensions
    #    video_info = self.get_metadata('video_info')
     #   width = video_info.get('width')
      #  height = video_info.get('height')
       # if width and height:
        #    return QSize(width, height)
       # return QSize()  # Return an invalid QSize if dimensions are not available

    def add_event_clip(self, event_type, event_metadata):
        # This method adds the metadata for an event clip
        self.metadata['events'].append({
            'event_type': event_type,
            **event_metadata
        })

    def add_event_end(self, end_time, event_type, duration):
        # This method adds the end time and duration for an event
        for event in self.metadata['events']:
            if event['event_type'] == event_type and 'end_time' not in event:
                event['end_time'] = end_time
                event['duration'] = duration
                break
        else:
            print(f"No event start found for {event_type} to mark the end.")

 #   def save_roi_data(self, roi_data_per_frame, start_time, end_time):
        # This method saves the ROI data for an event
  #      for frame_number, rois in roi_data_per_frame.items():
  #          for roi_data in rois:
  #              self.add_roi_metadata(frame_number, roi_data['coordinates'], roi_data['label'])
        # Optionally, you could also save the start and end times of the event here


  #  def save_rois_to_file(self, file_path):
        # Assuming you have a dictionary that maps frame numbers to lists of ROI objects
   #     frame_to_rois = self.get_frame_to_rois_mapping()  # You need to implement this method

    #    rois_data = {frame: [{'x': roi.x(), 'y': roi.y(), 'width': roi.width(), 'height': roi.height(), 'label': roi.label}
     #                       for roi in rois]
      #              for frame, rois in frame_to_rois.items()}

       # print("ROIs data to be saved:", rois_data)  # Debugging output
        #with open(file_path, 'w') as file:
         #   json.dump(rois_data, file, ensure_ascii=False)
       # print(f"ROIs saved to {file_path}")

   # def load_video_metadata(self, video_path):
        # Use OpenCV to load video metadata
    #    video_capture = cv2.VideoCapture(video_path)
     #   if not video_capture.isOpened():
      #      print(f"Error: Could not open video at {video_path}")
       #     return False

        # Extract metadata and store it
     #   self.metadata['video_info']['fps'] = video_capture.get(cv2.CAP_PROP_FPS)
      #  self.metadata['video_info']['width'] = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
       # self.metadata['video_info']['height'] = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        #video_capture.release()

        # You might want to save this metadata to a file or use it directly
        # self.save_metadata('path_to_save_video_metadata.json')

       # return True
