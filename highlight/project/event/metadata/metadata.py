import json
import os
import cv2
from PyQt5.QtCore import QSize


class MetadataManager:
    def __init__(self):
        self.metadata = {
            "video_info": {"video_name": "", "fps": 0, "video_dimensions": ""},
            "events": [],
            "clips": []
        }
        self.current_event = None
        print("MetadataManager initialized.")

    def start_event(self, event_type, start_frame):
        print("def start event called")
        new_event = {
            "event_type": event_type,
            "start_frame": start_frame,
            "end_frame": None,
            "total_frames": None,
            "roi_data": []  # Initialize an empty list for ROI data
        }
        self.metadata["events"].append(new_event)
        print(f"New event started: {new_event}")
        self.current_event = new_event
        print(f"Current event started: {self.current_event}")

    def end_event(self, end_frame):
        if self.current_event:
            self.current_event["end_frame"] = end_frame
            self.current_event["total_frames"] = end_frame - self.current_event["start_frame"]
            # Finalize ROI data for the event
            # This assumes ROI data has been continuously updated during the event
            self.current_event = None

    def update_roi_data(self, roi_id = None, start_frame = None, end_frame = None, x = None, y = None, width = None, height = None, label = None):
        if not self.current_event:
            print("No active event to add ROI data.")
            return

        # Adjust start_frame and end_frame relative to the event's start_frame
        event_start_frame = self.current_event["start_frame"]
        adjusted_start_frame = start_frame - event_start_frame
        adjusted_end_frame = end_frame - event_start_frame if end_frame is not None else None

        # Update the end_frame of the last entry for the same roi_id
        if self.current_event["roi_data"]:
            for entry in reversed(self.current_event["roi_data"]):
                if entry["roi_id"] == roi_id:
                    if entry["x"] != x or entry["y"] != y or entry["width"] != width or entry["height"] != height:
                        entry["end_frame"] = adjusted_start_frame - 1
                        entry["total_frames"] = entry["end_frame"] - entry["start_frame"]
                    break

        # Create a new ROI entry
        new_roi = {
            "roi_id": roi_id,
            "start_frame": adjusted_start_frame,
            "end_frame": adjusted_end_frame,
            "total_frames": adjusted_end_frame - adjusted_start_frame if adjusted_end_frame is not None else None,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "label": label
        }
        self.current_event["roi_data"].append(new_roi)  # Add the new ROI entry
        self.metadata["clips"].append(new_roi)

    def update_last_roi_end_frame(self, end_frame):
        if not self.current_event or not self.current_event.get("roi_data"):
            print("No current event or ROI data to update.")
            return

        # Debugging: Print current roi_data
        print("ROI Data before updating end frame:", self.current_event["roi_data"])

        last_roi_entry = self.current_event["roi_data"][-1]
        adjusted_end_frame = end_frame - self.current_event["start_frame"]
        print(f"Updating end frame from {last_roi_entry['end_frame']} to {adjusted_end_frame}")
        
        last_roi_entry["end_frame"] = adjusted_end_frame
        last_roi_entry["total_frames"] = adjusted_end_frame - last_roi_entry["start_frame"]

        # Debugging: Print updated roi_data
        print("ROI Data after updating end frame:", self.current_event["roi_data"])

    def add_clip_data(self, clip_data):
        # Temporarily store ROI data
        temp_roi_data = self.metadata["clips"].copy()

        # Clear the clips list and add the clip entry first
        self.metadata["clips"].clear()
        self.metadata["clips"].append(clip_data)

        # Add the stored ROI data back to clips
        self.metadata["clips"].extend(temp_roi_data)

    def save_metadata(self, filename="metadata.json"):
        with open(filename, 'w') as file:
            json.dump(self.metadata, file, indent=4)

    def get_all_events(self):
        # return self.metadata["events"]
        return self.metadata.get("events", [])

    def set_video_info(self, video_name, fps, dimensions):
        # Convert QSize object to a string or tuple
        if isinstance(dimensions, QSize):
            dimensions_str = f"{dimensions.width()} x {dimensions.height()}"
        else:
            dimensions_str = dimensions  # assuming dimensions is already in a suitable format

        self.metadata["video_info"] = {
            "video_name": video_name,
            "fps": fps,
            "video_dimensions": dimensions_str
        }