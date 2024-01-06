#event_label.py
#################### Chunk 1 of 3 ####################
###### get_video_dimensions, VideoApp, load_video_metadata, get_current_label, get_video_fps, get_frame_number, get_current_frame_number, mark_start, mark_end, extract_all_events, extract_event ######
import sys
import os
import logging
import json
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QFileDialog, QRadioButton, 
QVBoxLayout, QDialog, QLabel, QMessageBox, QSizePolicy, QToolBar, QWidget, QStatusBar, QComboBox, QPushButton, QAction)
from PyQt5.QtCore import QUrl, Qt, QTimer, QRect, QSize, QPoint
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaMetaData
from PyQt5.QtMultimediaWidgets import QVideoWidget
# Import custom widgets and video processing functions
from widgets import PlayPauseButton, SpeedButton, FrameSkipButton, MarkButton, EventTypeRadioButtons, PositionSlider, TimerLabel, LoadVideoAction, GenericButton
from clip_extractor import ClipExtractor
from slider import CustomSlider
from event_list_dialog import EventListDialog
from metadata import MetadataManager
from roiwidget import *

sys.path.append("/Users/ronschmidt/Applications/highlight/project/")

metadata_manager = MetadataManager()

def get_video_dimensions(video_path):
    """Get the dimensions of the video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open the video file.")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Video dimensions: {width} x {height}")
    cap.release()
    return QSize(width, height)

class VideoApp(QMainWindow):
    def __init__(self, metadata_manager):  # Accept metadata_manager as an argument
        super().__init__()
        self.metadata_manager = metadata_manager
        self.logger = self.setup_logger()
        self.video_path = None
        self.video_dimensions = QSize()

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
      #  self.video_widget = VideoWidgetWithROIs(self.media_player, self)
        self.video_widget = VideoWidgetWithROIs(self.media_player, metadata_manager, self)
        self.video_widget.set_current_frame_number_function(self.get_current_frame_number)
        self.media_player.setVideoOutput(self.video_widget)
        self.setup_ui()
        self.setup_signals_slots()
        self.events = []
        
        self.frame_skip_amount = 33  # Assuming a frame rate of 30 fps
        self.skip_direction = 0
        self.is_frame_skip_button_pressed = False
        self.frame_skip_timer = QTimer(self)
        self.frame_skip_timer.timeout.connect(self.skip_frame)

        self.frame_rate = 30
        self.event_start = None
        self.current_frame_number = None  # Added for current frame tracking

    def load_video_metadata(self, video_path):
        print("def load_video_metadata(self, video_path):")
        self.metadata_manager.load_video_info(video_path)

    def get_current_label(self):
        # Example: return the currently selected item in a dropdown
        print("def get_current_label(self):")
        return self.labelDropdown.currentText()

    def get_video_fps(self, video_path):
        cap = cv2.VideoCapture(video_path)
        print(f"cap: {cap}")
        print("def get_video_fps(self, video_path):")
        if not cap.isOpened():
            print("Error opening video file")
            return 0
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        return fps

    def get_frame_number(self, time_in_seconds):
        print("def get_frame_number(self, time_in_seconds):")
        return int(time_in_seconds * self.frame_rate)

    def get_current_frame_number(self):
        current_time_ms = self.media_player.position()
        current_frame = (current_time_ms / 1000) * self.frame_rate
     #   print(f"Current Frame Number: {current_frame}")
     #   print("def get_current_frame_number(self):")
        return int(current_frame)

    def mark_start(self):
        """Mark the start of an event."""
        if self.current_event_type is None:
            QMessageBox.warning(self, "Warning", "No event type selected.")
            return

        start_frame = self.get_current_frame_number()
        print(f"Start Frame Number: {start_frame}")

        # Start a new event
        self.metadata_manager.start_event(self.current_event_type, start_frame)

        # Update button styles
        self.mark_start_btn.setStyleSheet("background-color: green")
        self.mark_end_btn.setStyleSheet("")

    def mark_end(self):
        """Mark the end of an event."""
        if not self.metadata_manager.metadata["events"]:
            QMessageBox.warning(self, "Warning", "No event has been started.")
            return

        end_frame = self.get_current_frame_number()
        print(f"End Frame Number: {end_frame}")

        # End the event with only the end frame
        self.metadata_manager.update_last_roi_end_frame(end_frame)
        self.metadata_manager.end_event(end_frame)


        self.reset_button_styles()

    def extract_all_events(self):
        print("def extract_all_events(self):")
        all_events = self.metadata_manager.get_all_events()
        for event in all_events:
            self.extract_event(event)
        self.metadata_manager.save_metadata()

    def extract_event(self, event):
        print("def extract_event(self, event):")
        event_type = event.get('event_type')
        start_frame = event.get('start_frame')
        end_frame = event.get('end_frame')

        # Handle missing data
        if start_frame is None or end_frame is None or event_type is None:
            self.logger.warning(f"Missing data for event: {event}")
            print(f"Missing data for event: {event}")
            return

        # Convert frame numbers to time
        fps = self.metadata_manager.metadata["video_info"]["fps"]
        start_time = start_frame / fps
        end_time = end_frame / fps

        # Extract the clip
        clip_extractor = ClipExtractor(self.video_path, self.metadata_manager)
        clip_path = clip_extractor.extract_clip(start_time, end_time, event_type.lower().replace(" ", "_"))

        # Compile ROI data for the clip
        roi_data_for_clip = []
        for roi_data in event['roi_data']:
            roi_data_for_clip.append(roi_data)

        # Prepare clip data
        clip_data = {
            "clip_file_name": os.path.basename(clip_path),
            "event_type": event_type,
            "start_frame": start_frame,
            "end_frame": end_frame,
            "total_frames": end_frame - start_frame + 1,
            "roi_data": roi_data_for_clip
        }

        self.metadata_manager.add_clip_data(clip_data)

 #################### Chunk 2 of 3 ####################
 ###### def load_video, is_video_ended, setup_logger, create_menu_bar, setup_ui, setup_signals_slots, setup_media_player, update_timer_label, seek_video, update_slider_position ######

    def load_video(self):
        """Load a video file."""
        video_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov);;All Files (*)")     
        if video_path:
            # Extract the file name and FPS from the video path
            video_name = os.path.basename(video_path)
            fps = self.get_video_fps(video_path)
            dimensions =  get_video_dimensions(video_path)
            


            self.video_path = video_path  # Store the video path
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
            self.media_player.mediaStatusChanged.connect(self.handle_media_status)
            self.status_bar.showMessage(f"Loaded Video: {video_name}")

            # Update MetadataManager with video info
            self.metadata_manager.set_video_info(video_name, fps, dimensions)
            self.media_player.durationChanged.connect(self.update_slider_range)
            # Additional code for setting up the video...
            if not self.video_dimensions.isValid():
                try:
                    self.video_dimensions = get_video_dimensions(video_path)
                    print(f"Video dimensions set to: {self.video_dimensions}")
                    self.video_widget.set_video_dimensions(self.video_dimensions.width(), self.video_dimensions.height())
                except ValueError as e:
                    print(f"Error getting video dimensions: {e}")
                    # Handle the error, perhaps set a default size or show an error message

    def is_video_ended(self):
        # Determine if the video has ended
        return self.media_player.state() == QMediaPlayer.EndOfMedia

    def setup_logger(self):
        """Set up logging for the application."""
        logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        return logging.getLogger(__name__)

    def create_menu_bar(self):
        # Create the menu bar
        menu_bar = self.menuBar()

        # Create File menu and add actions
        file_menu = menu_bar.addMenu("&File")

        # Add 'Save ROIs' action
        save_action = QAction("&Save ROIs", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(lambda: self.video_widget.save_rois_to_file('rois.json'))
        file_menu.addAction(save_action)

        # Add 'Load ROIs' action
        load_action = QAction("&Load ROIs", self)
        load_action.setShortcut("Ctrl+L")
        load_action.triggered.connect(lambda: self.video_widget.load_rois_from_file('rois.json'))
        file_menu.addAction(load_action)

        # Add 'Export ROIs' action
        export_action = QAction("&Export ROIs", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(lambda: self.video_widget.export_rois('rois_export.json', 'json'))
        file_menu.addAction(export_action)

        # Create Edit menu and add actions
        edit_menu = menu_bar.addMenu("&Edit")

        # Add 'Undo' action
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.video_widget.undo)
        edit_menu.addAction(undo_action)

        # Add 'Redo' action
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.video_widget.redo)
        edit_menu.addAction(redo_action)
        
    def setup_ui(self):
        """Set up the user interface elements."""
        self.setWindowTitle("Video Processing Application")
        self.setGeometry(100, 100, 1250, 800)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Add the video widget to the layout
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.video_widget)

        self.position_slider = CustomSlider(Qt.Horizontal, self)
        self.layout.addWidget(self.position_slider)

        self.timer_label = TimerLabel(self.central_widget)
        self.layout.addWidget(self.timer_label)

        self.control_bar = QToolBar(self)
        self.addToolBar(Qt.BottomToolBarArea, self.control_bar)

        self.load_video_action = LoadVideoAction(self)
        self.control_bar.addAction(self.load_video_action)

        self.play_pause_btn = PlayPauseButton(self)
        self.control_bar.addWidget(self.play_pause_btn)

        self.decrease_speed_btn = SpeedButton("-", self)
        self.control_bar.addWidget(self.decrease_speed_btn)

        self.increase_speed_btn = SpeedButton("+", self)
        self.control_bar.addWidget(self.increase_speed_btn)

        self.frame_skip_backward_btn = FrameSkipButton("<<", self)
        self.control_bar.addWidget(self.frame_skip_backward_btn)

        self.frame_skip_forward_btn = FrameSkipButton(">>", self)
        self.control_bar.addWidget(self.frame_skip_forward_btn)

        self.mark_start_btn = MarkButton("Mark Start", self)
        self.control_bar.addWidget(self.mark_start_btn)

        self.mark_end_btn = MarkButton("Mark End", self)
        self.control_bar.addWidget(self.mark_end_btn)

        self.event_type_radio_buttons = EventTypeRadioButtons(self)
        self.event_type_radio_buttons.event_type_selected.connect(self.on_event_type_selected)
        self.layout.addWidget(self.event_type_radio_buttons)

        self.event_list_btn = GenericButton("Show Event List", self)
        self.control_bar.addWidget(self.event_list_btn)

        self.extract_event_btn = GenericButton("Extract Event", self)
        self.control_bar.addWidget(self.extract_event_btn)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

    def setup_signals_slots(self):
        """Set up signals and slots for the application."""
        self.load_video_action.triggered.connect(self.load_video)
        self.play_pause_btn.clicked.connect(self.play_pause_video)
        self.mark_start_btn.clicked.connect(self.mark_start)
        self.mark_end_btn.clicked.connect(self.mark_end)
        self.frame_skip_forward_btn.pressed.connect(self.start_frame_skip_forward)
        self.frame_skip_forward_btn.released.connect(self.stop_frame_skip)
        self.frame_skip_backward_btn.pressed.connect(self.start_frame_skip_backward)
        self.frame_skip_backward_btn.released.connect(self.stop_frame_skip)
        self.increase_speed_btn.clicked.connect(self.increase_speed)
        self.decrease_speed_btn.clicked.connect(self.decrease_speed)
        self.extract_event_btn.clicked.connect(self.extract_all_events)
        self.media_player.positionChanged.connect(self.update_slider_position)
        self.position_slider.sliderMoved.connect(self.seek_video)
        self.media_player.positionChanged.connect(self.update_timer_label)
        self.media_player.error.connect(self.handle_error)
        self.media_player.mediaStatusChanged.connect(self.handle_media_status)
        self.event_list_btn.clicked.connect(self.show_event_list)
        self.media_player.positionChanged.connect(self.on_position_changed)

    def setup_media_player(self):
        """Set up the media player."""
        self.media_player.setVideoOutput(self.video_widget)

    def update_timer_label(self, position):
        """Update the timer label."""
        total_time = self.media_player.duration()
        elapsed_minutes, elapsed_seconds = divmod(position // 1000, 60)
        total_minutes, total_seconds = divmod(total_time // 1000, 60)
        self.timer_label.setText(f"{elapsed_minutes:02}:{elapsed_seconds:02} / {total_minutes:02}:{total_seconds:02}")

    def seek_video(self, position):
        """Seek the video to a specific position."""
        self.media_player.setPosition(position)

    def update_slider_position(self, position):
        """Update the slider position."""
        if self.position_slider:
            self.position_slider.setValue(position)

#################### Chunk 3 of 3 ####################
###### play_pause_video, start_frame_skip_forward, start_frame_skip_backward, stop_frame_skip, skip_frame, increase_speed, decrease_speed, update_slider_range, handle_media_status, handle_error, show_event_list, start_drawing_roi, reset_button_styles, on_event_type_selected, on_position_changed ######
    def play_pause_video(self):
        """Play or pause the video."""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_pause_btn.setText("Play")
        else:
            self.media_player.play()
            self.play_pause_btn.setText("Pause")

    def start_frame_skip_forward(self):
        """Start skipping frames forward."""
        if not self.is_frame_skip_button_pressed:
            self.skip_direction = 1
            self.skip_frame()
            self.frame_skip_timer.start(83)
            self.is_frame_skip_button_pressed = True

    def start_frame_skip_backward(self):
        """Start skipping frames backward."""
        if not self.is_frame_skip_button_pressed:
            self.skip_direction = -1
            self.skip_frame()
            self.frame_skip_timer.start(83)
            self.is_frame_skip_button_pressed = True

    def stop_frame_skip(self):
        """Stop skipping frames."""
        self.frame_skip_timer.stop()
        self.skip_direction = 0
        self.is_frame_skip_button_pressed = False

    def skip_frame(self):
        """Skip a single frame."""
        current_position = self.media_player.position()
        new_position = current_position + (self.frame_skip_amount * self.skip_direction)
        self.media_player.setPosition(new_position)

    def increase_speed(self):
        """Increase the playback speed."""
        current_rate = self.media_player.playbackRate()
        self.media_player.setPlaybackRate(current_rate + 0.5)

    def decrease_speed(self):
        """Decrease the playback speed."""
        current_rate = self.media_player.playbackRate()
        if current_rate > 0.5:
            self.media_player.setPlaybackRate(current_rate - 0.5)

    def update_slider_range(self, duration):
        """Update the slider range."""
        self.position_slider.setRange(0, duration)

    def handle_media_status(self, status):
        """Handle media status changes."""
        print(f"Media Status: {status}")

    def handle_error(self):
        """Handle media player errors."""
        error_message = self.media_player.errorString()
        print(f"Error: {error_message}")
        self.status_bar.showMessage(f"Error: {error_message}")

    def show_event_list(self):
        print("def show_event_list(self):")
        dialog = EventListDialog(self.events, self)
        if dialog.exec_() == QDialog.Accepted:
            print("User confirmed the event list")

    def start_drawing_roi(self):
        self.drawing = True
        self.video_widget.start_drawing()
        self.update()
        print("def start_drawing_roi(self):")

    def reset_button_styles(self):
        """Reset the styles of start and end buttons."""
        self.mark_start_btn.setStyleSheet("")
        self.mark_end_btn.setStyleSheet("")
        print("def reset_button_styles(self):")

    def on_event_type_selected(self, event_type):
        self.current_event_type = event_type

    def on_position_changed(self, position):
        if self.media_player.state() == QMediaPlayer.PlayingState or self.is_frame_skip_button_pressed:
            self.current_frame_number = self.get_current_frame_number()
       #     print(f"Current Frame Number: {self.current_frame_number}")  # Debugging statement


if __name__ == "__main__":
    app = QApplication(sys.argv)
    video_app = VideoApp(metadata_manager)
    video_app.show()
    sys.exit(app.exec_())