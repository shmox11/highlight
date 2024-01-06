#roiwidget.py:
############### Chunk 1 of 5 ################
##### Class ROI, update_end_frame, update_history, set_hover, draw, update_coordinates, convert_roi_to_dict #####
import sys
import json
import csv
import cv2
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QInputDialog, QFileDialog, QMenu, QAction
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QRectF, QSize, QSizeF, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QMouseEvent, QKeyEvent
from functools import partial
from metadata import MetadataManager

def generate_roi_id(roi_type, label_number):
    return f"{roi_type}_{label_number}"

class ROI(QRectF):
    print("ROI class called")
    def __init__(self, x=0, y=0, w=0, h=0, label='', start_frame=0, roi_id='', metadata_manager=None):
        super().__init__(x, y, w, h)
        self.label = label
        self.start_frame = start_frame
        self.end_frame = None  # Updated when the ROI is moved or deleted
        self.is_hovered = False
        self.history = [{'start_frame': start_frame, 'x': x, 'y': y, 'width': w, 'height': h}]
        self.metadata_manager = metadata_manager
        self.roi_id = roi_id  # Assign the passed roi_id

    def update_end_frame(self, end_frame):
        print("def update end frame called")
        self.end_frame = end_frame
        print("end frame updated")

    def update_history(self, current_frame, x=None, y=None, width=None, height=None):
        # Update the last entry's end_frame
        self.history[-1]['end_frame'] = current_frame - 1

        # Add a new entry
        new_entry = {
            'start_frame': current_frame,
            'end_frame': None,  # Initially None, to be updated later
            'x': x if x is not None else self.x(),
            'y': y if y is not None else self.y(),
            'width': width if width is not None else self.width(),
            'height': height if height is not None else self.height(),
            'label': self.label
        }
        self.history.append(new_entry)

    def set_hover(self, hover):
        self.is_hovered = hover

    def draw(self, painter):
        # ... existing drawing code ...
        if self.is_hovered:
            # Change the drawing style to indicate hover, e.g., change the border color
            print('Drawing hover')
            pass  

    def update_coordinates(self, new_x, new_y, new_width, new_height, current_frame):
        print("def update coordinates called")
        self.setRect(new_x, new_y, new_width, new_height)
        self.update_history(current_frame, new_x, new_y, new_width, new_height)
        self.update_end_frame(current_frame)
        print("ROI coordinates, history, and end frame updated")

        # Return updated ROI data, handling of metadata update is shifted outside this class
        return {
            "start_frame": self.start_frame,
            "end_frame": self.end_frame,
            "x": new_x,
            "y": new_y,
            "width": new_width,
            "height": new_height,
            "label": self.label
        }

    def convert_roi_to_dict(self):
        return {
            "start_frame": self.start_frame,
            "end_frame": self.end_frame,  # this might be None if the ROI is not yet ended
            "x": self.x(),
            "y": self.y(),
            "width": self.width(),
            "height": self.height(),
            "label": self.label
        }
        
############### Chunk 2 of 5 ################
##### Class VideoWidgetWithROIs, get_current_frame_number, on_roi_moved, createROI, update_roi_position, current_frame, get_roi_data_for_frame #####

class VideoWidgetWithROIs(QVideoWidget):
    MIN_ROI_WIDTH = 10  # Minimum width of the ROI, in pixels
    MIN_ROI_HEIGHT = 10  # Minimum height of the ROI, in pixels
    roisChanged = pyqtSignal()

    def __init__(self, media_player, metadata_manager, parent=None, frame_rate=30):
        super().__init__(parent)
        self.media_player = media_player
        self.metadata_manager = metadata_manager
        self.frame_rate = frame_rate
        self.undo_stack = []
        self.redo_stack = []
        self.rois = []
        self.original_video_size = QSize(1920, 1080)
        self.scaling_factor = 1.0
        self.selected_roi = None
        self.is_drawing = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.setFocusPolicy(Qt.StrongFocus)
        self.resizing = None
        self.last_selected_roi_at_pos = {}
        self.frame_rois = {}
        self.roi_counter = 0  # Initialize the ROI counter


        self.roi_types = {
            'Kill': {'x': 100, 'y': 100, 'width': 50, 'height': 50, 'color': 'red'},
            'kill_kf': {'x': 138.0, 'y': 302.0, 'width': 23.0, 'height': 17.0, 'color': 'red'},
            'kill_text': {'x': 501.0, 'y': 496.0, 'width': 38.0, 'height': 22.0, 'color': 'red'},
            'kill_counter': {'x': 1090.0, 'y': 16.0, 'width': 16.0, 'height': 27.0, 'color': 'red'},
            'down': {'x': 630.0, 'y': 315.0, 'width': 31.0, 'height': 20.0, 'color': 'blue'},
            'down_kf': {'x': 138.0, 'y': 302.0, 'width': 23.0, 'height': 17.0, 'color': 'blue'},
            'team_wipe': {'x': 701.0, 'y': 260.0, 'width': 66.0, 'height': 18.0, 'color': 'yellow'},
            'team_wipe_kf': {'x': 95.0, 'y': 307.0, 'width': 66.0, 'height': 18.0, 'color': 'yellow'},
            'revive': {'x': 579, 'y': 392, 'width': 66, 'height': 66, 'color': 'green'},
            'revive_team': {'x': 533.0, 'y': 219.0, 'width': 159.0, 'height': 33.0, 'color': 'green'},
            'shield_break': {'x': 628.0, 'y': 317.0, 'width': 32, 'height': 37, 'color': 'orange'},
            'win': {'x': 100, 'y': 100, 'width': 50, 'height': 50, 'color': 'gold'},
            'low_health': {'x': 96.0, 'y': 551.0, 'width': 111.0, 'height': 31.0, 'color': 'brown'}

            # Add more labels with their default ROI dimensions and positions
        }

    def createROI(self, roi_type, click_position):
        print("def create roi called")
        print(f"Current event in create ROI: {self.metadata_manager.current_event}")
        # Check if there is an active event before creating ROI
        if self.metadata_manager.current_event is None:
            print("Cannot create ROI. No active event.")
            return

        roi_properties = self.roi_types.get(roi_type, None)
        if not roi_properties:
            print(f"ROI type {roi_type} not found.")
            return

        x, y = roi_properties['x'], roi_properties['y']
        width, height = roi_properties['width'], roi_properties['height']
        current_frame_number = self.get_current_frame_number()
        print(f"Current frame number: {current_frame_number}")

        label_number = self.get_next_label_number(roi_type)
        roi_id = generate_roi_id(roi_type, label_number)

        new_roi = ROI(x, y, width, height, label=roi_type, start_frame=current_frame_number, roi_id=roi_id, metadata_manager=self.metadata_manager)
        if 'color' in roi_properties:
            new_roi.color = QColor(roi_properties['color'])
        else:
            new_roi.color = QColor(255, 255, 255)  # Default color

        self.rois.append(new_roi)

        # Update metadata with the new ROI
        roi_data_dict = {
            "roi_id": roi_id,
            "start_frame": current_frame_number,
            "end_frame": None,  # End frame is None when first created
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "label": roi_type
        }
        self.metadata_manager.update_roi_data(**roi_data_dict)
        print(f"ROI data updated: {roi_data_dict}")

    def get_current_frame_number(self):
        print("def get current frame number called")
        if self.media_player is not None:
            current_time_ms = self.media_player.position()
            current_frame_number = (current_time_ms / 1000) * self.frame_rate
            return int(current_frame_number)
            print(f"Current frame number: {current_frame_number}")
        return 0  # Default frame number if media player is not available

    def get_next_label_number(self, roi_type):
        # Ensure there is a label_counters dictionary
        if not hasattr(self, 'label_counters'):
            self.label_counters = {}  # Initialize the counters dictionary
        if roi_type not in self.label_counters:
            self.label_counters[roi_type] = 0
        self.label_counters[roi_type] += 1
        return self.label_counters[roi_type]
       
    def current_frame(self):
        print("def current frame called")
        current_time_ms = self.media_player.position()  # Get the current playback position in milliseconds
        print("current time ms retrieved")
        frame_rate = self.frame_rate  # Frame rate of the video
        print("frame rate retrieved")
        current_frame = (current_time_ms / 1000) * frame_rate
        print("current frame retrieved")
        return int(current_frame)
        print("current frame returned")

    def get_roi_data_for_frame(self, frame_number):
        print("def get_roi_data_for_frame called")
        roi_data_list = []

        for roi in self.rois:
            # Check if the ROI is relevant for the given frame
            if frame_number >= roi.start_frame and (roi.end_frame is None or frame_number <= roi.end_frame):
                roi_data = {
                    "label": roi.label,
                    "start_frame": roi.start_frame,
                    "end_frame": roi.end_frame,
                    "x": roi.x(),
                    "y": roi.y(),
                    "width": roi.width(),
                    "height": roi.height()
                }
                roi_data_list.append(roi_data)
        
        print(f"ROI data for frame {frame_number}: {roi_data_list}")
        return roi_data_list
    
############### Chunk 3 of 5 ################
##### Class VideoWidgetWithROIs, next_frame, previous_frame, update_frame_rois, update_roi, set_current_frame_number_function, remove_selected_roi, remove_roi, resizeEvent, resizeROI, mouseMoveEvent, mouseReleaseEvent, mouseDoubleClickEvent, keyPressEvent, mousePressEvent, check_hover_state, store_current_frame_roi_data, update_frame_rois, update_roi, is_near_corner, paintEvent #####

    def set_current_frame_number_function(self, func):
        print("def set current frame number function called")
        self.get_current_frame_number = func
        print("current frame number function set")

    def remove_selected_roi(self):
        if self.selected_roi:
            current_frame = self.get_current_frame_number()
            self.selected_roi.update_end_frame(current_frame)

            # Convert ROI to a dictionary and ensure all required data is included
            removed_roi_data = self.selected_roi.convert_roi_to_dict()
            
            # Check if 'roi_id' is part of removed_roi_data, if not, add it
            if 'roi_id' not in removed_roi_data:
                removed_roi_data['roi_id'] = self.selected_roi.roi_id  # or any logic to get the roi_id

            # Update the metadata
            self.metadata_manager.update_roi_data(**removed_roi_data)

            # Remove the ROI from the list and reset the selected_roi
            self.rois.remove(self.selected_roi)
            self.selected_roi = None

    def remove_roi(self, roi):
        print("def remove roi called")
        current_frame = self.get_current_frame_number()
        print("current frame retrieved")
        roi.update_end_frame(current_frame)
        print("end frame updated")
        self.metadata_manager.update_roi_metadata(roi)
        print("metadata updated")
        self.rois.remove(roi)
        print("roi removed")

    def resizeEvent(self, event):
        print("def resize event called")
        # Calculate the new scaling factor based on the new size
        new_scaling_factor = min(self.width() / self.original_video_size.width(),
                                self.height() / self.original_video_size.height())
        
        # Apply the new scaling factor to all ROIs
        for roi in self.rois:
            # Calculate the new size based on the new scaling factor
            new_top_left = roi.topLeft() * new_scaling_factor / self.scaling_factor
            new_bottom_right = roi.bottomRight() * new_scaling_factor / self.scaling_factor
            
            # Update the ROI with the new size
            roi.setTopLeft(new_top_left)
            roi.setBottomRight(new_bottom_right)
        
        # Update the scaling factor to the new value
        self.scaling_factor = new_scaling_factor
        self.update()  # Refresh the display

        super().resizeEvent(event)  # Call the parent class's resize event

    def resizeROI(self, roi, corner, event_pos):
        print("def resize roi called")
        if corner == 'topLeft':
            new_width = roi.bottomRight().x() - event_pos.x()
            new_height = roi.bottomRight().y() - event_pos.y()
            new_x = min(roi.bottomRight().x() - self.MIN_ROI_WIDTH, event_pos.x())
            new_y = min(roi.bottomRight().y() - self.MIN_ROI_HEIGHT, event_pos.y())

        elif corner == 'topRight':
            new_width = event_pos.x() - roi.bottomLeft().x()
            new_height = roi.bottomLeft().y() - event_pos.y()
            new_x = roi.bottomLeft().x()
            new_y = min(roi.bottomLeft().y() - self.MIN_ROI_HEIGHT, event_pos.y())

        elif corner == 'bottomLeft':
            new_width = roi.topRight().x() - event_pos.x()
            new_height = event_pos.y() - roi.topRight().y()
            new_x = min(roi.topRight().x() - self.MIN_ROI_WIDTH, event_pos.x())
            new_y = roi.topRight().y()

        elif corner == 'bottomRight':
            new_width = event_pos.x() - roi.topLeft().x()
            new_height = event_pos.y() - roi.topLeft().y()
            new_x = roi.topLeft().x()
            new_y = roi.topLeft().y()

        # Enforce minimum width and height
        new_width = max(new_width, self.MIN_ROI_WIDTH)
        new_height = max(new_height, self.MIN_ROI_HEIGHT)

        # Update ROI coordinates and size
        roi.setRect(new_x, new_y, new_width, new_height)
        print(f"ROI resized to x={new_x}, y={new_y}, w={new_width}, h={new_height}")
        self.update()
        print("update called")

############### Chunk 4 of 5 ################
##### Class VideoWidgetWithROIs, mouseMoveEvent, mouseReleaseEvent, mouseDoubleClickEvent, keyPressEvent, mousePressEvent, check_hover_state, is_near_corner, paintEvent #####

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_drawing:
            self.end_point = event.pos()
            self.selected_roi.setBottomRight(self.end_point)
            self.update()  # Trigger a repaint to show the ROI box while drawing

        elif self.selected_roi and self.resizing:
            if self.resizing == 'topLeft':
                self.resizeROI(self.selected_roi, 'topLeft', event.pos())
            elif self.resizing == 'topRight':
                self.resizeROI(self.selected_roi, 'topRight', event.pos())
            elif self.resizing == 'bottomLeft':
                self.resizeROI(self.selected_roi, 'bottomLeft', event.pos())
            elif self.resizing == 'bottomRight':
                self.resizeROI(self.selected_roi, 'bottomRight', event.pos())

        elif self.selected_roi:
            # Handle moving the ROI
            delta = event.pos() - self.start_point
            self.selected_roi.translate(delta)
            self.start_point = event.pos()
            self.update()  # Trigger a repaint to show the moved ROI box

        self.check_hover_state(event.pos())  # Update hover state if you have such functionality

    def mouseReleaseEvent(self, event):
        print("def mouse release event called")
        if event.button() == Qt.LeftButton:
            print("left button")
            current_frame = self.get_current_frame_number()
            if self.selected_roi:
                # Update the ROI's end frame
                self.selected_roi.update_end_frame(current_frame)

                # Check if the ROI was moved
                delta = event.pos() - self.start_point
                if delta:
                    self.selected_roi.translate(delta)
                    self.selected_roi.update_end_frame(current_frame)

                # Gather ROI data
                x, y, width, height = self.selected_roi.x(), self.selected_roi.y(), self.selected_roi.width(), self.selected_roi.height()
                label = self.selected_roi.label
                start_frame = current_frame  # Assuming the start frame is the current frame after moving
                end_frame = current_frame  # Assuming the end frame is the current frame after moving

                # Update metadata
                self.metadata_manager.update_roi_data(self.selected_roi.roi_id, start_frame, end_frame, x, y, width, height, label)
                print(f"ROI data updated: {self.selected_roi.roi_id}, {start_frame}, {end_frame}, {x}, {y}, {width}, {height}, {label}")

                self.selected_roi = None
                print("selected roi set to none")

            self.update()  # Redraw the widget
            self.roisChanged.emit()  # Emit signal that ROIs have changed
            print("rois changed emitted")

    def mouseDoubleClickEvent(self, event):
        # Check if an ROI is double-clicked to label it
        for roi in self.rois:
            if roi.contains(event.pos()):
                # List of predefined labels
                labels = list(self.roi_types.keys())
                # Get the label from the user using a dropdown list
                label, ok = QInputDialog.getItem(self, 'Select Label', 'Choose a label for the ROI:', labels, 0, False)
                if ok and label:
                    roi.label = label
                    self.roisChanged.emit()  # Emit signal when label is changed
                    self.update()
                return

    def keyPressEvent(self, event):
        print("def key press event called")
        print("Widget has focus:", self.hasFocus())  # Debug print
        print("Key pressed:", event.key())  # Debug print
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace, Qt.Key_D):  # Use 'in' for checking membership in the tuple
            print("Removing selected ROI")
            self.remove_selected_roi()
            print("selected roi removed")
            self.update()
            print("update called")
        elif event.key() == Qt.Key_ArrowRight:
            print("Going to next frame")
            self.next_frame()
        elif event.key() == Qt.Key_ArrowLeft:
            print("Going to previous frame")
            self.previous_frame()
        # Add more elif statements for other shortcuts
        else:
            print("Unhandled key press event")
            super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        print("def mouse press event called")
        if event.button() == Qt.LeftButton:
            print("left button pressed")
            click_pos = event.pos()
            print("click position retrieved")

            # Attempt to select an ROI
            clicked_rois = [roi for roi in self.rois if roi.contains(click_pos)]
            print(f"Clicked ROIs: {len(clicked_rois)}")  # Debugging line

            if clicked_rois:
                # If we have previously selected an ROI, find its index
                if self.selected_roi in clicked_rois:
                    last_index = clicked_rois.index(self.selected_roi)
                else:
                    last_index = -1

                # Get the next ROI in the list
                next_index = (last_index + 1) % len(clicked_rois)
                self.selected_roi = clicked_rois[next_index]

            if self.selected_roi:
                self.start_point = click_pos
                self.is_drawing = False
                self.resizing = self.is_near_corner(click_pos, self.selected_roi)
                self.update()
                return  # This return might prevent further ROIs from being selected

            self.update()

    def check_hover_state(self, mouse_pos):
        for roi in self.rois:
            if roi.contains(mouse_pos):
                roi.set_hover(True)  # You need to implement this method in your ROI class
            else:
                roi.set_hover(False)  # You need to implement this method in your ROI class
        self.update()  # Trigger a repaint to show the hover state

    def is_near_corner(self, point, roi):
        print("def is near corner called")
        # Define a threshold for how close the mouse needs to be to a corner to count as a resize
        threshold = 10
        corners = {
            'topLeft': roi.topLeft(),
            'topRight': roi.topRight(),
            'bottomLeft': roi.bottomLeft(),
            'bottomRight': roi.bottomRight()
        }
        for corner_name, corner_point in corners.items():
            if (corner_point - point).manhattanLength() < threshold:
                return corner_name
        return None

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        for roi in self.rois:
            if isinstance(roi, ROI):
                color = QColor(roi.color)  # Use the color associated with the label
                if roi == self.selected_roi:
                    pen = QPen(color, 2, Qt.SolidLine)
                else:
                    pen = QPen(color, 2, Qt.SolidLine)  # Use the color associated with the label
                painter.setPen(pen)
                painter.drawRect(roi)
                if roi.label:
                    # Draw the label text in black for visibility
                    painter.setPen(QColor('white'))
                    painter.drawText(roi.topLeft(), roi.label)

############### Chunk 5 of 5 ################
##### Class VideoWidgetWithROIs, load_rois_from_file, export_rois, undo, redo, load_state, save_state, start_drawing, contextMenuEvent, label_selected, get_label_for_new_roi, set_video_dimensions, set_original_video_size, update_scaling_factor #####

    def load_rois_from_file(self, file_path):
        print("def load rois from file called")
        try:
            with open(file_path, 'r') as file:
                rois_data = json.load(file)
            self.rois = [ROI(roi['x'], roi['y'], roi['width'], roi['height'], roi['label']) for roi in rois_data]
            self.update()
            print(f"ROIs loaded from {file_path}")
        except FileNotFoundError:
            print(f"No saved ROIs found at {file_path}")
        self.video_widget.load_rois_from_file('rois.json')
        print(f"Loaded ROIs: {self.rois}")

    def export_rois(self, file_path, export_format='json'):
        print("def export rois called")
        # Use the accessor methods to get the ROI data
        rois_data = [{'x': roi.x(), 'y': roi.y(), 'width': roi.width(), 'height': roi.height(), 'label': roi.label}
                    for roi in self.rois]  # Ensure you're exporting the current ROIs
        print(f"Exporting ROIs to {file_path} as {export_format}")

        if export_format == 'json':
            with open(file_path, 'w') as file:
                json.dump(rois_data, file)  # Dump the rois_data, not self.frame_rois
                json.dump(self.frame_rois, file, indent=4)

            print(f"ROIs exported to {file_path} in JSON format")
        elif export_format == 'csv':
            with open(file_path, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['x', 'y', 'width', 'height', 'label'])
                writer.writeheader()
                for roi_data in rois_data:
                    writer.writerow(roi_data)
            print(f"ROIs exported to {file_path} in CSV format")
        else:
            print("Unsupported export format")

    def undo(self):
        print("def undo called")
        # Existing undo logic
        if self.undo_stack:
            self.redo_stack.append(self.undo_stack.pop())
            self.load_state(self.undo_stack[-1] if self.undo_stack else '[]')
            self.update_metadata_after_state_change()  # Update metadata after undo
            print("undo stack updated")

    def redo(self):
        print("def redo called")
        # Existing redo logic
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.undo_stack.append(state)
            self.load_state(state)
            self.update_metadata_after_state_change()  # Update metadata after redo
            print("redo stack updated")

    def load_state(self, state_json):
        print("def load state called")
        rois_data = json.loads(state_json)
        print("rois data retrieved")
        self.rois = [QRectF(roi['x'], roi['y'], roi['width'], roi['height']) for roi in rois_data]
        print("rois updated")
        for roi, roi_data in zip(self.rois, rois_data):
            roi.label = roi_data.get('label', '')
            print("roi label updated")
        self.update()
        print("update called")

    def save_state(self):
        print("def save state called")
        state = json.dumps(self.rois, default=lambda o: o.__dict__)
        print(f"Saving state: {state}")
        self.undo_stack.append(state)
        print("state appended to undo stack")
        self.redo_stack.clear()
        print("redo stack cleared")

    def start_drawing(self):
        print("def start drawing called")
        self.is_drawing = True

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)

        for roi_type in self.roi_types:
            action = QAction(roi_type, self)

            # Use functools.partial to correctly capture the roi_type
            action.triggered.connect(partial(self.createROI, roi_type, event.pos()))
            
            contextMenu.addAction(action)

        contextMenu.exec_(event.globalPos())

    def label_selected(self, index):
        print("def label selected called")
        label = self.label_selector.itemText(index)
        print(f"Label selected: {label}")
        if self.selected_roi:
            print("selected roi")
            self.selected_roi.label = label
            print("label set")
            self.update()
            print("update called")

    def get_label_for_new_roi(self):
        print("def get label for new roi called")
        """
        Prompt the user to enter a label for the new ROI.
        """
        labels = list(self.roi_types.keys())  # Assuming roi_types contains your labels
        print("labels retrieved")
        label, ok = QInputDialog.getItem(self, 'Label new ROI', 'Select label:', labels, 0, False)
        print("label retrieved")
        if ok:
            return label
            print("label returned")
        return ''  # Default label if user cancels the dialog
        print("default label returned")

    def set_video_dimensions(self, width, height):
        # This method will be called from event_label.py
        self.set_original_video_size(width, height)
        self.update_scaling_factor()  # Make sure to update the scaling factor

    def set_original_video_size(self, width, height):
        self.original_video_size = QSize(width, height)
        self.update_scaling_factor()

    def update_scaling_factor(self):
        print("def update scaling factor called")
        old_scaling_factor = self.scaling_factor
        self.scaling_factor = min(self.width() / self.original_video_size.width(),
                                self.height() / self.original_video_size.height())
        print(f"Scaling factor updated from {old_scaling_factor} to {self.scaling_factor}")
        self.scale_all_rois()
        self.update()

    def scale_all_rois(self):
        print("def scale all rois called")
        for roi in self.rois:
            old_top_left = roi.topLeft()
            old_bottom_right = roi.bottomRight()
            # ... existing scaling code ...
            print(f"ROI scaled from {old_top_left}, {old_bottom_right} to {roi.topLeft()}, {roi.bottomRight()}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROI Annotation Tool")
        self.video_widget = VideoWidgetWithROIs()
        self.setCentralWidget(self.video_widget)
        self.init_ui()

    def init_ui(self):
        # Set up the video player and other UI components
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.player.setVideoOutput(self.video_widget)
        # TODO: Load video content and set up controls





if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())