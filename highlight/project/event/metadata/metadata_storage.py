# metadata_storage.py
import os
import json
import sys
#add Parent directory to sys.path
sys.path.append("/Users/ronschmidt/Applications/highlight/project/event/metadata/")   


class MetadataStorage:
    def __init__(self):
        pass  # Initialize any needed variables or objects
    

def store_metadata(metadata):
    if not os.path.exists('data/metadata'):
        os.makedirs('data/metadata')
    filename = f"data/metadata/{metadata.timestamp.replace(':', '-')}-{metadata.event_type}.json"
    with open(filename, 'w') as file:
        file.write(metadata.to_json())
