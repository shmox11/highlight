# metadata_manager.py

import json

class MetadataManager:
    def __init__(self):
        self.metadata = {
            "video_info": {},
            "clips": [],
            "events": []
        }

    def add_roi_metadata(self, frame_number, roi_data):
        # This assumes you want to store ROI data per frame
        if "roi_data_per_frame" not in self.metadata:
            self.metadata["roi_data_per_frame"] = {}
        self.metadata["roi_data_per_frame"][frame_number] = roi_data

    # Modify the add_metadata method to handle 'roi' category
    def add_metadata(self, category, key, value):
        if category == "video_info":
            self.metadata["video_info"][key] = value
        elif category == "clip":
            self.metadata["clips"].append({key: value})
        elif category == "event":
            self.metadata["events"].append({key: value})
        elif category == "roi":
            self.add_roi_metadata(key, value)  # 'key' here would be the frame number
        else:
            print("Invalid category. Please use 'video_info', 'clip', 'event', or 'roi'.")
    def get_metadata(self, category=None):
        if category:
            return self.metadata.get(category, {})
        return self.metadata

    def get_all_metadata(self):
        # Assuming self.metadata is a dictionary containing all the metadata
        return self.metadata

    def save_metadata(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.metadata, f)

    def load_metadata(self, file_path):
        try:
            with open(file_path, 'r') as f:
                self.metadata = json.load(f)
        except FileNotFoundError:
            print("Metadata file not found. Starting with empty metadata.")
        except json.JSONDecodeError:
            print("Error decoding metadata. Starting with empty metadata.")
