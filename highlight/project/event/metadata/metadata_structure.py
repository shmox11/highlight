# metadata_structure.py
import json

import sys
#add Parent directory to sys.path
sys.path.append("/Users/ronschmidt/Applications/highlight/project/event/metadata/")   


class Metadata:
    def __init__(self, event_type, timestamp, visual_elements, audio_cues, text_elements, user_interaction, file_data):
        self.event_type = event_type  # e.g. "Shield Break", "Down", "Kill", etc.
        self.timestamp = timestamp  # e.g. "00:05:23"
        self.visual_elements = visual_elements  # e.g. {"icon": {"type": "Broken Shield", "location": "center"}}
        self.audio_cues = audio_cues  # e.g. {"type": "Distinct Sound", "description": "Sound of shield breaking"}
        self.text_elements = text_elements  # e.g. {"location": "bottom", "content": "Player1 killed Player2"}
        self.user_interaction = user_interaction  # Any user interaction data
        self.file_data = file_data  # e.g. {"filename": "video.mp4", "format": "mp4"}
        
    def to_json(self):
        return json.dumps(self.__dict__, indent=4)