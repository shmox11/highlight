
#slider.py
from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor

class CustomSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super(CustomSlider, self).__init__(orientation, parent)
        self.marks = []

    def add_mark(self, position, color):
        self.marks.append((position, color))
        self.update()

    def clear_marks(self):
        self.marks = []
        self.update()

    def paintEvent(self, event):
        super(CustomSlider, self).paintEvent(event)
        painter = QPainter(self)
        for position, color in self.marks:
            rect = self.rect_for_position(position)
            painter.fillRect(rect, color)

    def rect_for_position(self, position):
        # Assuming position is a value between 0 and 1
        x = int(self.width() * position)
        y = 0
        handle_width = 5  # Width of the mark
        handle_height = self.height()
        return QRect(x, y, handle_width, handle_height)
