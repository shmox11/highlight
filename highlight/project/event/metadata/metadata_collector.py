# metadata_collector.py
import sys
#add Parent directory to sys.path
sys.path.append("/Users/ronschmidt/Applications/highlight/project/event/metadata/")   

class MetadataCollector:
    def __init__(self):
        pass  # Initialize any needed variables or objects
    
    def collect_metadata(self, position, event_type):  # other parameters
        # Logic to collect metadata
       # metadata = {...}  # Construct metadata dictionary
        #return metadata
        pass


#visual_elements = {
 #   "icon": {"type": "Player Icon", "location": "left"},
  #  "counter": {"type": "Kill Counter", "location": "top right"}
#}

#audio_cues = {
 #   "type": "Distinct Sound",
  #  "description": "Sound of player being killed"
#}

#text_elements = {
 #   "location": "bottom",
  #  "content": "Player1 killed Player2"
#}

#metadata = collect_metadata("Kill", "00:05:23", visual_elements, audio_cues, text_elements, user_interaction, file_data)
