# windows.py
import sys
import cv2
import os
sys.path.append("/Users/ronschmidt/Applications/highlight/project/")   
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QToolBar, QStatusBar, QFileDialog, QLabel, QMessageBox, QSizePolicy)
from PyQt5.QtCore import QUrl, Qt, pyqtSignal  
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from widgets import (PlayPauseButton, SpeedButton, FrameSkipButton, MarkButton, PositionSlider, VolumeSlider, EventTypeComboBox, TimerLabel, LoadVideoAction, GenericButton, ScrubbedPreview)
from video_processing import extract_thumbnails
import pytesseract

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
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.setStretchFactor(self.video_widget, 1)
        self.video_widget.setAspectRatioMode(Qt.KeepAspectRatio)
        self.video_widget.setStyleSheet("background-color: red;")
        self.layout.addWidget(self.video_widget)
        
        # Initialize the media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

        # Thumbnail Layout Initialization
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

        # Initialize event markers
        self.event_start = None
        self.event_end = None

        # Connect the mark buttons
        self.mark_start_btn.clicked.connect(self.mark_start)
        self.mark_end_btn.clicked.connect(self.mark_end)
        self.frame_skip_forward_btn.clicked.connect(self.frame_skip_forward)
        self.frame_skip_backward_btn.clicked.connect(self.frame_skip_backward)
        self.increase_speed_btn.clicked.connect(self.increase_speed)
        self.decrease_speed_btn.clicked.connect(self.decrease_speed)
        self.volume_slider.valueChanged.connect(self.adjust_volume)


        # Signal Slots
        self.media_player.positionChanged.connect(self.update_slider_position)
        self.position_slider.sliderMoved.connect(self.seek_video)
        self.media_player.positionChanged.connect(self.update_timer_label)
     #   self.scrubbed_preview = ScrubbedPreview()
        self.layout.addWidget(self.scrubbed_preview)
        self.media_player.error.connect(self.handle_error)
        self.media_player.mediaStatusChanged.connect(self.handle_media_status)
        self.extract_event_btn.clicked.connect(self.extract_event)

        self.events = []

      #  # Initialize event markers
       # self.event_start = None
       # self.event_end = None

      #  # Connect the mark buttons
      #  self.mark_start_btn.marked.connect(self.mark_start)
      #  self.mark_end_btn.marked.connect(self.mark_end)
      #  self.icon_rel_x = 0.45
      #  self.icon_rel_y = 0.45
      #  self.icon_rel_w = 0.10
      #  self.icon_rel_h = 0.10

      #  self.feed_rel_x = 0.15
      #  self.feed_rel_y = 0.35
      #  self.feed_rel_w = 0.10
      #  self.feed_rel_h = 0.20



  #  self.events = []
    
    def mark_start(self):
        if self.event_end and not self.event_start:
            QMessageBox.warning(self, "Warning", "Please mark the end of the event before marking a new start.")
            return
        self.event_start = self.media_player.position()
        print(f"Marked Start at {self.event_start} ms")

    def mark_end(self):
        if not self.event_start:
            QMessageBox.warning(self, "Warning", "Please mark the start of the event first.")
            return
        self.event_end = self.media_player.position()
        print(f"Marked End at {self.event_end} ms")
        self.events.append((self.event_start, self.event_end))
        self.event_start = None
        self.event_end = None

    def extract_event(self):
        for event_start, event_end in self.events:
            # Temporal Metadata
            duration = event_end - event_start
            print(f"Event from {event_start} ms to {event_end} ms with duration {duration} ms")

            # Extract video snippet (pseudo-code, actual extraction depends on video processing library)
            # video_snippet = extract_video_snippet(self.media_player.media(), event_start, event_end)

            # Extract thumbnails or keyframes from the video snippet
            # For demonstration, let's assume you extract one thumbnail at the midpoint of the event
            midpoint = (event_start + event_end) // 2
            thumbnail = self.get_frame_at(self.video_path, midpoint)
            thumbnail_path = os.path.join("thumbnails", f"thumbnail_{midpoint}.png")
            cv2.imwrite(thumbnail_path, thumbnail)
            print(f"Saved thumbnail at {thumbnail_path}")

            # TODO: Add extraction of other metadata (audio, icons, OCR, etc.)

        # Clear the events list after extraction
        self.events.clear()
    
    def extract_video_snippet(self, video_path, start_time, end_time, output_path):
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))
        
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time)
        while cap.get(cv2.CAP_PROP_POS_MSEC) < end_time:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
        
        cap.release()
        out.release()


    def get_frame_at(self, video_path, timestamp):
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp)
        ret, frame = cap.read()
        cap.release()
        if ret:
            return frame
        return None

    def extract_metadata(self, video_path, start_time, end_time):
        metadata = {}
        metadata['start_time'] = start_time
        metadata['end_time'] = end_time
        metadata['duration'] = end_time - start_time
        # Add more metadata extraction logic here
        return metadata

    def extract_text_from_frame(self, frame):
        text = pytesseract.image_to_string(frame)
        return text

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
        self.media_player.setPosition(current_position + 10)  # Skip forward by 1 second

    def frame_skip_backward(self):
        current_position = self.media_player.position()
        self.media_player.setPosition(current_position - 10)  # Skip backward by 1 second

    def increase_speed(self):
        current_rate = self.media_player.playbackRate()
        self.media_player.setPlaybackRate(current_rate + 0.5)  # Increase speed by 0.5x

    def decrease_speed(self):
        current_rate = self.media_player.playbackRate()
        if current_rate > 0.05:  # Ensure we don't go below 0.5x speed
            self.media_player.setPlaybackRate(current_rate - 0.05)  # Decrease speed by 0.5x

    def adjust_volume(self, value):
        self.media_player.setVolume(value)

    def update_slider_range(self, duration):
        self.position_slider.setRange(0, duration)

    #def get_absolute_coordinates(self, frame, rel_x, rel_y, rel_w, rel_h):
     #   frame_height, frame_width = frame.shape[:2]
      #  x = int(rel_x * frame_width)
       # y = int(rel_y * frame_height)
       # w = int(rel_w * frame_width)
       # h = int(rel_h * frame_height)
       # return x, y, w, h

   # def detect_down_event(self, frame):
    #    # Load the templates
     #   down_icon_template = cv2.imread('down_icon.png', 0)
      #  kill_feed_template = cv2.imread('kill_feed.png', 0)

        # Convert the frame to grayscale
       # gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Extract regions of interest
     #   icon_x, icon_y, icon_w, icon_h = self.get_absolute_coordinates(frame, self.icon_rel_x, self.icon_rel_y, self.icon_rel_w, self.icon_rel_h)
     #   icon_roi = gray_frame[icon_y:icon_y+icon_h, icon_x:icon_x+icon_w]

     #   feed_x, feed_y, feed_w, feed_h = self.get_absolute_coordinates(frame, self.feed_rel_x, self.feed_rel_y, self.feed_rel_w, self.feed_rel_h)
     #   feed_roi = gray_frame[feed_y:feed_y+feed_h, feed_x:feed_x+feed_w]

        # Visualize the ROIs
    #    cv2.rectangle(frame, (icon_x, icon_y), (icon_x+icon_w, icon_y+icon_h), (0, 255, 0), 2)
    #    cv2.rectangle(frame, (feed_x, feed_y), (feed_x+feed_w, feed_y+feed_h), (0, 0, 255), 2)
     #   cv2.imshow("ROIs", frame)
     #   cv2.waitKey(0)

        # Template matching for down icon
     #   result_icon = cv2.matchTemplate(icon_roi, down_icon_template, cv2.TM_CCOEFF_NORMED)
     #   _, max_val_icon, _, _ = cv2.minMaxLoc(result_icon)

        # OCR for kill feed
     #   text = pytesseract.image_to_string(feed_roi)
     #   print(f"OCR Output: {text}")  # Debugging the OCR output

     #   if max_val_icon > 0.01 and "down" in text.lower():
      #      print("Down event detected!")
      #  else:
       #     print(f"Max Val Icon: {max_val_icon}")  # Debugging the template matching result

    def handle_media_status(self, status):
        print(f"Media Status: {status}")  # Debug print

    def handle_error(self):
        error_message = self.media_player.errorString()
        print(f"Error: {error_message}")  # Debug print
        self.status_bar.showMessage(f"Error: {error_message}")






if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec_())
