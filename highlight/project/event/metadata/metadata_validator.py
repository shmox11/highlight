# metadata_validator.py

import sys
#add Parent directory to sys.path
sys.path.append("/Users/ronschmidt/Applications/highlight/project/event/metadata/")   

from metadata_structure import Metadata

class MetadataValidator:
    def __init__(self):
        pass  # Initialize any needed variables or objects
   

    def validate_metadata(metadata):
        if not isinstance(metadata, Metadata):
            return False
        if not metadata.event_type or not metadata.timestamp or not metadata.visual_elements or not metadata.file_data:
            return False
        # Add more validations as per your requirements
        return True