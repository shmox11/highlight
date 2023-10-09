# template_manager.py

import cv2
import os

class TemplateManager:
    def __init__(self):
        self.templates = self._load_all_templates()

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

