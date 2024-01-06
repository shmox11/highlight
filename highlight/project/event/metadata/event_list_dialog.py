from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox

class EventListDialog(QDialog):
    def __init__(self, events, parent=None):
        super(EventListDialog, self).__init__(parent)
        self.events = events
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.list_widget = QListWidget(self)
        for event in self.events:
            self.list_widget.addItem(f"Start: {event['start_time']}, End: {event['end_time']}, Type: {event.get('event_type', 'N/A')}")
        self.layout.addWidget(self.list_widget)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok, self)
        self.button_box.accepted.connect(self.accept)
        self.layout.addWidget(self.button_box)

        self.setWindowTitle("Event List")
        self.setGeometry(100, 100, 400, 300)