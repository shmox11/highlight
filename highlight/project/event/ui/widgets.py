from PyQt5.QtWidgets import QPushButton, QSlider, QComboBox, QLabel, QAction
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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