# windows.py
import sys
#add Parent directory to sys.path
sys.path.append("/Users/ronschmidt/Applications/highlight/project/")   

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QToolBar, QStatusBar, QFileDialog, QLabel, QMessageBox)
from PyQt5.QtCore import QUrl, Qt  
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from widgets import (PlayPauseButton, SpeedButton, FrameSkipButton, MarkButton, PositionSlider, VolumeSlider, EventTypeComboBox, TimerLabel, LoadVideoAction, GenericButton)
from PyQt5.QtCore import QT_VERSION_STR
print(QT_VERSION_STR)


#from event.metadata.metadata_collector import MetadataCollector
#from event.metadata.metadata_validator import MetadataValidator
#from event.metadata.metadata_storage import MetadataStorage 
#from event.metadata.metadata_collector import collect_metadata
#from event.metadata.metadata_validator import validate_metadata
#from event.metadata.metadata_storage import store_metadata
#from metadata import collect_metadata

#metadata = collect_metadata(event_type, timestamp, visual_elements, user_interaction, file_data)

class VideoApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main Window Properties
        self.setWindowTitle("Video Processing Application")
        self.setGeometry(100, 100, 800, 600)

        # Central Widget and Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Video Widget and Media Player
        self.video_widget = QVideoWidget()
        self.video_widget.setFixedSize(640, 480)
        self.video_widget.setStyleSheet("background-color: red;")
        self.layout.addWidget(self.video_widget)
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        self.central_widget.setLayout(self.layout)

        # Control Bar
        self.control_bar = QToolBar()
        self.addToolBar(Qt.BottomToolBarArea, self.control_bar)

        # Load Video Icon
        self.load_video_action = LoadVideoAction(self)
        self.control_bar.addAction(self.load_video_action)
        self.load_video_action.triggered.connect(self.load_video)

        # Play/Pause Button
        self.play_pause_btn = PlayPauseButton()
        self.control_bar.addWidget(self.play_pause_btn)
        self.play_pause_btn.clicked.connect(self.play_pause_video)

        # Speed Control Buttons
        self.decrease_speed_btn = SpeedButton("-")
        self.control_bar.addWidget(self.decrease_speed_btn)
        self.increase_speed_btn = SpeedButton("+")
        self.control_bar.addWidget(self.increase_speed_btn)

        # Frame Skip Buttons
        self.frame_skip_backward_btn = FrameSkipButton("<<")
        self.control_bar.addWidget(self.frame_skip_backward_btn)
        self.frame_skip_forward_btn = FrameSkipButton(">>")
        self.control_bar.addWidget(self.frame_skip_forward_btn)

        # Mark Event Start and End Buttons
        self.mark_start_btn = MarkButton("Mark Start")
        self.control_bar.addWidget(self.mark_start_btn)
        self.mark_end_btn = MarkButton("Mark End")
        self.control_bar.addWidget(self.mark_end_btn)

        # Video Position Slider and Timer
        self.position_slider = PositionSlider()
        self.layout.addWidget(self.position_slider)
        self.timer_label = TimerLabel()
        self.control_bar.addWidget(self.timer_label)

        # Volume Control Slider
        self.volume_slider = VolumeSlider()
        self.control_bar.addWidget(self.volume_slider)

        # Event Type Dropdown and Extract Button
        self.event_type_combo_box = EventTypeComboBox()
        self.layout.addWidget(self.event_type_combo_box)
        self.extract_event_btn = GenericButton("Extract Event")
        self.layout.addWidget(self.extract_event_btn)

        self.media_player.error.connect(self.handle_error)
        self.media_player.mediaStatusChanged.connect(self.handle_media_status)


        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Metadata Components
        #self.metadata_collector = MetadataCollector()
        #self.metadata_validator = MetadataValidator()
        #self.metadata_storage = MetadataStorage()
        #self.metadata_display = MetadataDisplayWidget()
        #self.metadata_display.setPlainText(str(metadata))  # or any other suitable representation of metadata

        # Add MetadataDisplayWidget to the layout
        #self.metadata_display = MetadataDisplayWidget()
        #self.layout.addWidget(self.metadata_display)

        # Add a button to initiate metadata collection
       # self.collect_metadata_btn = GenericButton("Collect Metadata")
       # self.layout.addWidget(self.collect_metadata_btn)
      #  gst-inspect-1.0 <media-type>gst-inspect-1.0 <media-type>self.collect_metadata_btn.clicked.connect(self.collect_metadata)

    def load_video(self):
        # This function will be used to load the video
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov)")
        if file_name != '':
            print(f"Loading Video: {file_name}")
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_name)))
            self.status_bar.showMessage(f"Loaded Video: {file_name}")

    def play_pause_video(self):
        # This function will be used to play or pause the video
        if self.media_player.state() == QMediaPlayer.PlayingState:
            print("Pausing Video")
            self.media_player.pause()
            self.play_pause_btn.setText("Play")
        else:
            print("Playing Video")
            self.media_player.play()
            self.play_pause_btn.setText("Pause")

    def handle_media_status(self, status):
        print(f"Media Status: {status}")  # Debug print

   # def extract_metadata(self):
    # Use metadata_collector to collect metadata
     #   metadata = self.metadata_collector.collect_metadata(position, event_type, ...)  # other parameters
        
        # Use metadata_validator to validate metadata
      #  if not self.metadata_validator.validate_metadata(metadata):
       #     QMessageBox.warning(self, 'Validation Error', 'Metadata is not valid!')
        #    return
        
        # Use metadata_storage to store metadata
       # self.metadata_storage.store_metadata(metadata)
        
        # Update the metadata_display widget with the collected metadata
        #self.metadata_display.setPlainText(json.dumps(metadata, indent=4))

    #def handle_event(self, event_type, timestamp, visual_elements, user_interaction, file_data):
     #   metadata = collect_metadata(event_type, timestamp, visual_elements, user_interaction, file_data)
      #  if validate_metadata(metadata):
       #     store_metadata(metadata)
            # Update UI to inform user about successful metadata storage
        #else:
            # Update UI to inform user about validation failure
         #   pass

    #def collect_metadata(self):
    # Get the current position, event type, and any other required parameters
     #   position = self.position_slider.value()  # or any other method to get the current position
      #  event_type = self.event_type_combo_box.currentText()  # or any other method to get the selected event type
        
        # Use metadata_collector to collect metadata
       # metadata = self.metadata_collector.collect_metadata(position, event_type, ...)  # other parameters
        
        # Display the collected metadata in MetadataDisplayWidget
       # self.metadata_display.setPlainText(str(metadata))  # or any other suitable representation of metadata    
   
    def handle_error(self):
        error_message = self.media_player.errorString()
        print(f"Error: {error_message}")  # Debug print
        self.status_bar.showMessage(f"Error: {error_message}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec_())
