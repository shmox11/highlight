import sys
import cv2
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QToolBar, QSlider, QStatusBar, QFileDialog, QLabel, QMessageBox, QSizePolicy, QPushButton)
from PyQt5.QtCore import QUrl, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from widgets import (PlayPauseButton, SpeedButton, FrameSkipButton, MarkButton, PositionSlider, EventTypeComboBox, TimerLabel, LoadVideoAction, GenericButton, ScrubbedPreview)
from video_processing import extract_thumbnails
import pytesseract

# Import the necessary modules
from video_processors.event_detector import EventDetector, KillFeedExtractor, AutoEventDetector
from video_processors.clip_extractor import ClipExtractor
from video_processors.logger import setup_logger

sys.path.append("/Users/ronschmidt/Applications/highlight/project/")

class VideoApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize logger
        self.logger = setup_logger()
        self.logger.info("Application started.")

        self.setup_ui()
        self.setup_media_player()
        self.setup_signals_slots()
        self.event_start = None
        self.event_end = None
        self.events = []
        self.initialize_event_detector()  # Initialize the event detector

    def setup_ui(self):
        # Main Window Properties
        self.setWindowTitle("Video Processing Application")
        self.setGeometry(100, 100, 800, 600)

        # Central Widget and Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Video Widget
        self.video_widget = QVideoWidget()
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.setStretchFactor(self.video_widget, 1)
        self.video_widget.setAspectRatioMode(Qt.KeepAspectRatio)
        self.video_widget.setStyleSheet("background-color: red;")
        self.layout.addWidget(self.video_widget)

        # Thumbnail Layout
        self.thumbnail_layout = QHBoxLayout()
        self.layout.addLayout(self.thumbnail_layout)
        print("Thumbnail Layout Initialized")

        # Video Position Slider and Timer
        self.position_slider = PositionSlider()
        self.layout.addWidget(self.position_slider)
        self.timer_label = TimerLabel()
        self.layout.addWidget(self.timer_label)

        # Scrubbed Preview (Thumbnail Display)
        self.scrubbed_preview = ScrubbedPreview()
        self.layout.addWidget(self.scrubbed_preview)
        print("Scrubbed Preview Initialized")

        # Control Bar
        self.control_bar = QToolBar()
        self.addToolBar(Qt.BottomToolBarArea, self.control_bar)

        # Load Video Icon
        self.load_video_action = LoadVideoAction(self)
        self.control_bar.addAction(self.load_video_action)

        # Play/Pause Button
        self.play_pause_btn = PlayPauseButton()
        self.control_bar.addWidget(self.play_pause_btn)

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

        # Threshold Slider
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(0, 100)  # Represents 0.00 to 1.00
        self.threshold_slider.valueChanged.connect(self.adjust_threshold)  # Connect to adjust_threshold
        self.control_bar.addWidget(self.threshold_slider)
        self.threshold_label = QLabel("Threshold: 0.50")
        self.control_bar.addWidget(self.threshold_label)



        # Event Type Dropdown and Extract Button
        self.event_type_combo_box = EventTypeComboBox()
        self.layout.addWidget(self.event_type_combo_box)
        self.extract_event_btn = GenericButton("Extract Event")
        self.layout.addWidget(self.extract_event_btn)

        # Auto Detect Events Button
        self.auto_detect_btn = GenericButton("Auto Detect Events")
        self.layout.addWidget(self.auto_detect_btn)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def setup_media_player(self):
        # Initialize the media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

    def setup_signals_slots(self):
        # Connect signals and slots
        self.load_video_action.triggered.connect(self.load_video)
        self.play_pause_btn.clicked.connect(self.play_pause_video)
        self.mark_start_btn.clicked.connect(self.mark_start)
        self.mark_end_btn.clicked.connect(self.mark_end)
        self.frame_skip_forward_btn.clicked.connect(self.frame_skip_forward)
        self.frame_skip_backward_btn.clicked.connect(self.frame_skip_backward)
        self.increase_speed_btn.clicked.connect(self.increase_speed)
        self.decrease_speed_btn.clicked.connect(self.decrease_speed)
        self.extract_event_btn.clicked.connect(self.extract_event)
        self.media_player.positionChanged.connect(self.update_slider_position)
        self.position_slider.sliderMoved.connect(self.seek_video)
        self.media_player.positionChanged.connect(self.update_timer_label)
        self.media_player.error.connect(self.handle_error)
        self.media_player.mediaStatusChanged.connect(self.handle_media_status)
     #   self.threshold_slider.valueChanged.connect(self.adjust_threshold)
        self.auto_detect_btn.clicked.connect(self.auto_detect_events)
        self.events = []

  
    def mark_start(self):
        self.event_start = self.media_player.position()
        print(f"Marked Start at {self.event_start} ms")

    def mark_end(self):
        if not self.event_start:
            QMessageBox.warning(self, "Warning", "Please mark the start of the event first.")
            return
        self.event_end = self.media_player.position()
        print(f"Marked End at {self.event_end} ms")
        self.events.append((self.event_start, self.event_end))
        # Removed the lines that reset self.event_start and self.event_end to None

 #   def initialize_event_detector(self):
  #      if hasattr(self, 'video_path'):
   #         self.detector = EventDetector(self.threshold_slider.value() / 100.0)
    #    else:
     #       # Handle the case where video_path is not set, e.g., show an error message or prompt user to load a video.
      #      pass

    def extract_event(self):
        # Debug print to check the values and their types
        print(f"Event Start: {self.event_start}, Type: {type(self.event_start)}")
        print(f"Event End: {self.event_end}, Type: {type(self.event_end)}")

        # Check if both event_start and event_end are set
        if self.event_start is None or self.event_end is None:
            QMessageBox.warning(self, "Warning", "Please mark both the start and end of the event.")
            return

        # Fetch the event type from the dropdown box
        selected_event_type = self.event_type_combo_box.currentText().lower().replace(" ", "_")

        # Use ClipExtractor to extract the event clip for the entire marked segment
        clip_extractor = ClipExtractor(self.video_path)
        clip_path = clip_extractor.extract_clip(self.event_start, self.event_end, selected_event_type)

        # Log the results
        self.logger.info(f"Clip extracted to: {clip_path}")

        # Extract a frame at the event start time
        frame = self.detector.get_frame_at(self.video_path, self.event_start)
        if frame is not None:
            # Call the detect_kill_feed_events method and print the results
            kill_feed_events = self.detector.detect_kill_feed_events(frame)
            print(f"Kill Feed Events: {kill_feed_events}")

        # Reset the marked start and end times
        self.event_start = None
        self.event_end = None

    def update_timer_label(self, position):
        total_time = self.media_player.duration()
        
        # Calculate elapsed time components
        elapsed_minutes = position // 60000
        elapsed_seconds = (position % 60000) // 1000
        elapsed_hundredths = (position % 1000) // 10
        
        # Calculate total time components
        total_minutes = total_time // 60000
        total_seconds = (total_time % 60000) // 1000
        total_hundredths = (total_time % 1000) // 10
        
        # Update the timer label with zero-padded values
        self.timer_label.setText(f"{elapsed_minutes:02}:{elapsed_seconds:02}:{elapsed_hundredths:02} / {total_minutes:02}:{total_seconds:02}:{total_hundredths:02}")

    def adjust_threshold(self, value):
        threshold = value / 100.0
        self.threshold_label.setText(f"Threshold: {threshold:.2f}")
        # Use the detector object to adjust the threshold
        if hasattr(self, 'detector'):
            self.detector.threshold = threshold
            print(f"Threshold set to: {threshold}")

    def seek_video(self, position):
        self.media_player.setPosition(position)

    def update_slider_position(self, position):
        self.position_slider.setValue(position)

    def load_video(self):
        print("Loading Video")
        video_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov);;All Files (*)")
        if video_path:
            file_name = os.path.basename(video_path)  # Extract the file name from the path
            print(f"Loading Video: {file_name}")
            self.video_path = video_path  # Store the video path
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
            self.status_bar.showMessage(f"Loaded Video: {file_name}")
            self.media_player.durationChanged.connect(self.update_slider_range)
            self.media_player.play()
            
            # Extract thumbnails
            thumbnails = extract_thumbnails(file_name)
            for thumb in thumbnails:
                pixmap = QPixmap.fromImage(thumb)
                label = QLabel()
                label.setPixmap(pixmap)
                self.thumbnail_layout.addWidget(label)
                print(f"Thumbnail added to layout: {thumb}")
            if thumbnails:
                self.scrubbed_preview.set_thumbnail(thumbnails[0])
                print("Scrubbed Preview Updated With First Thumbnail")

            # Initialize the event detector after loading the video
            self.initialize_event_detector()

    def initialize_event_detector(self):
        if hasattr(self, 'video_path') and self.video_path:
            self.detector = EventDetector(self.threshold_slider.value() / 100.0)
        else:
            print("Warning: Video path not set. Event detector not initialized.")

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

    def frame_skip_forward(self):
        current_position = self.media_player.position()
        self.media_player.setPosition(current_position + 20)  # Skip forward by 1 second

    def frame_skip_backward(self):
        current_position = self.media_player.position()
        self.media_player.setPosition(current_position - 20)  # Skip backward by 1 second

    def increase_speed(self):
        current_rate = self.media_player.playbackRate()
        self.media_player.setPlaybackRate(current_rate + 0.5)  # Increase speed by 0.5x

    def decrease_speed(self):
        current_rate = self.media_player.playbackRate()
        if current_rate > 0.05:  # Ensure we don't go below 0.5x speed
            self.media_player.setPlaybackRate(current_rate - 0.5)  # Decrease speed by 0.5x

    def update_slider_range(self, duration):
        self.position_slider.setRange(0, duration)



    def handle_media_status(self, status):
        print(f"Media Status: {status}")  # Debug print

    def handle_error(self):
        error_message = self.media_player.errorString()
        print(f"Error: {error_message}")  # Debug print
        self.status_bar.showMessage(f"Error: {error_message}")

    def auto_detect_events(self):
        # Instantiate the AutoEventDetector class
        autodetect = AutoEventDetector(self.video_path)
        
        # Call the appropriate method to detect events (assuming it's named detect_events)
        detected_events = autodetect.detect_events()
        
        # Process the detected events (e.g., display them in the UI, log them, etc.)
        for event in detected_events:
            print(event)  # Placeholder: replace with actual processing logic





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec_())
