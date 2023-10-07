#widgets.py

from PyQt5.QtWidgets import QPushButton, QSlider, QComboBox, QLabel, QAction, QPlainTextEdit, QProgressBar, QMessageBox, QWidget, QLabel
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

class PlayPauseButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__('Play', *args, **kwargs)

class SpeedButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class FrameSkipButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class MarkButton(QPushButton):
    marked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clicked.connect(self.emit_marked_signal)

    def emit_marked_signal(self):
        self.marked.emit()

class PositionSlider(QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(Qt.Horizontal, *args, **kwargs)

class VolumeSlider(QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(Qt.Horizontal, *args, **kwargs)
        self.setRange(0, 100)

class EventTypeComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addItems(["Shield Break", "Down", "Kill", "Revive", "Near Death Moment", "Player Down", "Player Shield Break", "Teammate Death", "Teammate Down", "Team Wipe", "Laugh Moments"])

class TimerLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__('00:00', *args, **kwargs)

class LoadVideoAction(QAction):
    def __init__(self, *args, **kwargs):
        super().__init__(QIcon("resources/icons/load_video_icon.png"), "Load Video", *args, **kwargs)

class GenericButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class MetadataDisplayWidget(QPlainTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)  # To prevent editing of the metadata display

class ProgressIndicatorWidget(QProgressBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ProgressIndicatorWidget(QProgressBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ScrubbedPreview(QWidget):
    def __init__(self):
        super().__init__()
        self.thumbnail_label = QLabel(self)
        
        # Thumbnail Label Setup
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setScaledContents(True)
        # If you want to set a fixed size for the thumbnail label, you can do so here:
        # self.thumbnail_label.setFixedSize(100, 100)  # Example size

    def set_thumbnail(self, thumbnail_image):
        """
        Set the thumbnail image for the preview.
        
        Args:
            thumbnail_image (QImage): Thumbnail image to display.
        """
        pixmap = QPixmap.fromImage(thumbnail_image)
        self.thumbnail_label.setPixmap(pixmap)

