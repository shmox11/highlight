import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QToolBar, QStatusBar, QFileDialog, QLabel)
from PyQt5.QtCore import QUrl, Qt  
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from widgets import (PlayPauseButton, SpeedButton, FrameSkipButton, MarkButton, PositionSlider, VolumeSlider, EventTypeComboBox, TimerLabel, LoadVideoAction, GenericButton)

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
        self.layout.addWidget(self.video_widget)
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

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

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)


    def load_video(self):
        # This function will be used to load the video
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov *.wmv *.wav)")
        if file_name != '':
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_name)))
            self.status_bar.showMessage(f"Loaded Video: {file_name}")

    def play_pause_video(self):
        # This function will be used to play or pause the video
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_pause_btn.setText("Play")
        else:
            self.media_player.play()
            self.play_pause_btn.setText("Pause")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec_())
