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
from video_processors.clip_extractor import ClipExtractor
from slider import CustomSlider
from event_list_dialog import EventListDialog
from metadata import MetadataManager
from roiwidget import VideoWidgetWithROIs, ROI, Event

sys.path.append("/Users/ronschmidt/Applications/highlight/project/")

def get_video_dimensions(video_path):
    """Get the dimensions of the video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open the video file.")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return QSize(width, height)
 #   self.video_widget.set_video_dimensions(self.video_dimensions.width(), self.video_dimensions.height())


class VideoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = self.setup_logger()
        self.video_path = None
        self.video_dimensions = QSize()
        self.setup_ui()
        self.setup_media_player()
        self.setup_signals_slots()
        self.events = []
        self.is_frame_skip_button_pressed = False
        self.frame_skip_timer = QTimer(self)
        self.frame_skip_timer.timeout.connect(self.skip_frame)
        self.skip_direction = 0
        self.frame_skip_amount = 40
        self.metadata_manager = MetadataManager()
        self.event_start = None
        self.video_widget = VideoWidgetWithROIs(self)
        self.create_menu_bar()
        # self.setCentralWidget(self.video_widget)  # Uncomment if this should be part of the initialization

    def setup_logger(self):
        """Set up logging for the application."""
        logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        return logging.getLogger(__name__)

    def setup_ui(self):
        """Set up the user interface elements."""
        self.setWindowTitle("Video Processing Application")
        self.setGeometry(100, 100, 1250, 800)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Replace the QVideoWidget with VideoWidgetWithROIs
        self.video_widget = VideoWidgetWithROIs(self.central_widget)
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.video_widget)

        self.position_slider = CustomSlider(Qt.Horizontal, self.central_widget)
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
        self.layout.addWidget(self.event_type_radio_buttons)

        self.event_list_btn = GenericButton("Show Event List", self)
        self.control_bar.addWidget(self.event_list_btn)

        self.extract_event_btn = GenericButton("Extract Event", self)
        self.control_bar.addWidget(self.extract_event_btn)

        self.store_roi_data_btn = QPushButton("Store ROI Data", self)
        self.control_bar.addWidget(self.store_roi_data_btn)
     #   self.store_roi_data_btn.clicked.connect(self.store_roi_data_button_clicked)


        # Add a button to start drawing an ROI
        self.draw_roi_btn = QPushButton("Draw ROI", self)
        self.control_bar.addWidget(self.draw_roi_btn)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

    def setup_media_player(self):
        """Set up the media player."""
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

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

        # Connect the button to the method to start drawing
        self.draw_roi_btn.clicked.connect(self.video_widget.start_drawing)

    def show_event_list(self):
        """Display the list of marked events."""
        dialog = EventListDialog(self.events, self)
        if dialog.exec_() == QDialog.Accepted:
            print("User confirmed the event list")

    def start_drawing_roi(self):
        self.drawing = True
        self.video_widget.start_drawing()
        self.update()

    def reset_button_styles(self):
        self.mark_start_btn.setStyleSheet("")
        self.mark_end_btn.setStyleSheet("")

    def mark_start(self):
        self.event_start = self.media_player.position()
        self.position_slider.add_mark(self.event_start, QColor("red"))
        print(f"Marked Start at {self.event_start} ms")
        self.mark_start_btn.setStyleSheet("background-color: red; color: white;")

    def get_current_frame_number(self):
        # Get the current playback position in milliseconds
        current_time_ms = self.media_player.position()

        # Get the FPS using the get_fps method
        fps = self.get_fps()

        # Calculate the current frame number
        current_frame = (current_time_ms / 1000) * fps
        return int(current_frame)



    def get_fps(self):
        # Assuming self.video_path is the path to your video file
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print("Error: Could not open video.")
            return None
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        return fps


    def mark_end(self):
        if not hasattr(self, 'event_start'):
            QMessageBox.warning(self, "Warning", "Please mark the start of the event first.")
            return

        self.event_end = self.media_player.position()
        self.position_slider.add_mark(self.event_end, QColor("green"))
        print(f"Marked End at {self.event_end} ms")

        selected_event_type = self.event_type_radio_buttons.selected_event_type
        if selected_event_type is None:
            QMessageBox.warning(self, "Warning", "Please select an event type.")
            return

        self.events.append(Event(self.event_start, self.event_end, selected_event_type))
        self.metadata_manager.add_metadata("clip", "event_type", selected_event_type)
        self.metadata_manager.add_metadata("clip", "end_time", self.event_end)
        duration = self.event_end - self.event_start
        self.metadata_manager.add_metadata("clip", "duration", duration)
        delattr(self, 'event_start')
        self.reset_button_styles()

    def extract_all_events(self):
        """Extract all marked events."""
        for event in self.events:
            self.extract_event(event)
        self.events = []  





    def extract_event(self, event):
        """Extract a specific event."""
        clip_extractor = ClipExtractor(self.video_path)
        clip_path = clip_extractor.extract_clip(event.start_time, event.end_time, event.event_type.lower().replace(" ", "_"))
        self.logger.info(f"Clip extracted to: {clip_path}")
        event_info = {
            "event_type": event.event_type,
            "video_path": self.video_path,
            "timestamp": event.start_time,
            "duration": event.end_time - event.start_time,
            "clip_path": clip_path,
            "status": "Clip Extracted"
        }
     #   event_metadata = self.metadata_manager.get_metadata(event.start_time)
     #   event_info.update(event_metadata)
        self.logger.info("Event added to the list: %s", event_info)

        clip_metadata = {
                "start_time": event.start_time,
                "end_time": event.end_time,
                "duration": event.end_time - event.start_time,
                "event_type": event.event_type,
                "clip_path": clip_path
        }
        self.metadata_manager.add_metadata("clip", "clip_info", clip_metadata)
        self.metadata_manager.save_metadata("metadata.json")


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
        self.position_slider.setValue(position)

    def load_video(self):
        """Load a video file."""
        print("Loading Video")
        video_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov);;All Files (*)")
        
        if video_path:
            file_name = os.path.basename(video_path)  # Extract the file name from the path
            print(f"Loading Video: {file_name}")
            print(f"Video Path: {video_path}")
            self.video_path = video_path  # Store the video path
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
            self.media_player.mediaStatusChanged.connect(self.handle_media_status)
       #     self.media_player.metaDataAvailableChanged.connect(self.on_meta_data_available)

            self.status_bar.showMessage(f"Loaded Video: {file_name}")
            self.media_player.durationChanged.connect(self.update_slider_range)
            # The rest of your code...
            if not self.video_dimensions.isValid():
                try:
                    self.video_dimensions = get_video_dimensions(video_path)
                    print(f"Video dimensions set to: {self.video_dimensions}")
                    self.video_widget.set_video_dimensions(self.video_dimensions.width(), self.video_dimensions.height())
                except ValueError as e:
                    print(f"Error getting video dimensions: {e}")
                    # Handle the error, perhaps set a default size or show an error message

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
#            self.update_rois_for_new_frame()

    def start_frame_skip_backward(self):
        """Start skipping frames backward."""
        if not self.is_frame_skip_button_pressed:
            self.skip_direction = -1
            self.skip_frame()
            self.frame_skip_timer.start(83)
            self.is_frame_skip_button_pressed = True
 #           self.update_rois_for_new_frame()

    def stop_frame_skip(self):
        """Stop skipping frames."""
        self.frame_skip_timer.stop()
        self.skip_direction = 0
        self.is_frame_skip_button_pressed = False
 #       self.update_rois_for_new_frame()

    def skip_frame(self):
        """Skip a single frame."""
        current_position = self.media_player.position()
        new_position = current_position + (self.frame_skip_amount * self.skip_direction)
        self.media_player.setPosition(new_position)
 #       self.update_rois_for_new_frame()


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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec_())