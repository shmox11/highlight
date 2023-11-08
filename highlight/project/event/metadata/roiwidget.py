import sys
import json
import csv
import cv2
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QInputDialog, QFileDialog
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QRectF, QSize, QSizeF, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QMouseEvent, QKeyEvent

class Event:
    def __init__(self, start_time, end_time, event_type):
        self.start_time = start_time
        self.end_time = end_time
        self.event_type = event_type


class ROI(QRectF):
    def __init__(self, x=0, y=0, w=0, h=0, label=''):
        super().__init__(x, y, w, h)
        self.label = label
        self.creation_time = time.time()  # Assign the current time

        self.is_hovered = False
    def set_hover(self, hover):
        self.is_hovered = hover

    def draw(self, painter):
        # ... existing drawing code ...
        if self.is_hovered:
            # Change the drawing style to indicate hover, e.g., change the border color
            pass  

class VideoWidgetWithROIs(QVideoWidget):
    roisChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.undo_stack = []  # List of previous states of ROIs
        self.redo_stack = []
        self.rois = []  # List of ROIs as ROI objects
        self.original_video_size = QSize(1920, 1080)  # Default video size, update with actual size
        self.scaling_factor = 1.0  # Initial scaling factor
        self.selected_roi = None
        self.is_drawing = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.setFocusPolicy(Qt.StrongFocus)  # Set focus policy to accept focus
        self.resizing = None
        self.last_selected_roi_at_pos = {}
        self.frame_rois = {}  # Add this line to initialize frame_rois



        self.labels_colors = {
            'Kill': QColor('red'),
            'kill_kf': QColor('red'),
            'kill_text': QColor('red'),
            'kill_counter': QColor('red'),
            'down': QColor('blue'),
            'down_kf': QColor('blue'),
            'team_wipe': QColor('yellow'),
            'team_wipe_kf': QColor('yellow'),
            'revive': QColor('green'),
            'revive_team': QColor('green'),


            'win': QColor('gold'),
            'low_health': QColor('brown')
            # ... add more labels and their colors as needed ...
        }

    def set_video_dimensions(self, width, height):
        # This method will be called from event_label.py
        self.set_original_video_size(width, height)
        self.update_scaling_factor()  # Make sure to update the scaling factor


    def set_original_video_size(self, width, height):
        self.original_video_size = QSize(width, height)
        self.update_scaling_factor()

    def update_scaling_factor(self):
        old_scaling_factor = self.scaling_factor
        self.scaling_factor = min(self.width() / self.original_video_size.width(),
                                self.height() / self.original_video_size.height())
        print(f"Scaling factor updated from {old_scaling_factor} to {self.scaling_factor}")
        self.scale_all_rois()
        self.update()



    def scale_all_rois(self):
        for roi in self.rois:
            old_top_left = roi.topLeft()
            old_bottom_right = roi.bottomRight()
            # ... existing scaling code ...
            print(f"ROI scaled from {old_top_left}, {old_bottom_right} to {roi.topLeft()}, {roi.bottomRight()}")


    def save_state(self):
        state = json.dumps(self.rois, default=lambda o: o.__dict__)
        print(f"Saving state: {state}")
        self.undo_stack.append(state)
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.undo_stack.pop())
            self.load_state(self.undo_stack[-1] if self.undo_stack else '[]')

    def redo(self):
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.undo_stack.append(state)
            self.load_state(state)

    def load_state(self, state_json):
        rois_data = json.loads(state_json)
        self.rois = [QRectF(roi['x'], roi['y'], roi['width'], roi['height']) for roi in rois_data]
        for roi, roi_data in zip(self.rois, rois_data):
            roi.label = roi_data.get('label', '')
        self.update()

    def start_drawing(self):
        self.is_drawing = True

    def remove_selected_roi(self):
        if self.selected_roi:
            self.rois.remove(self.selected_roi)
            self.selected_roi = None
            self.update()
            self.save_state()
            self.roisChanged.emit()

    def keyPressEvent(self, event):
        print("Widget has focus:", self.hasFocus())  # Debug print
        print("Key pressed:", event.key())  # Debug print
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace, Qt.Key_D):  # Use 'in' for checking membership in the tuple
            self.remove_selected_roi()
            self.update()
        elif event.key() == Qt.Key_N:
            self.next_frame()
        elif event.key() == Qt.Key_B:
            self.previous_frame()
        # Add more elif statements for other shortcuts
        else:
            super().keyPressEvent(event)



    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            click_pos = event.pos()

            # Attempt to select an ROI
            clicked_rois = [roi for roi in self.rois if roi.contains(click_pos)]
            print(f"Clicked ROIs: {len(clicked_rois)}")  # Debugging line

            if clicked_rois:
                # If we have previously selected an ROI, find its index
                if self.selected_roi in clicked_rois:
                    last_index = clicked_rois.index(self.selected_roi)
                    print(f"Last selected ROI index: {last_index}")  # Debugging line
                else:
                    last_index = -1

                # Get the next ROI in the list
                next_index = (last_index + 1) % len(clicked_rois)
                self.selected_roi = clicked_rois[next_index]
                print(f"New selected ROI index: {next_index}")  # Debugging line

            if self.selected_roi:
                self.start_point = click_pos
                self.is_drawing = False
                self.resizing = self.is_near_corner(click_pos, self.selected_roi)
                self.update()
                return  # This return might prevent further ROIs from being selected

            # If no ROI is selected, start drawing a new one
            self.is_drawing = True
            self.start_point = self.end_point = click_pos
            self.selected_roi = QRectF(self.start_point, self.end_point)
            self.update()


    def is_near_corner(self, point, roi):
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


    def mouseMoveEvent(self, event: QMouseEvent):
        print(f"Mouse pressed at {event.pos()}")

        if self.is_drawing:
            self.end_point = event.pos()
            self.selected_roi.setBottomRight(self.end_point)
            self.update()  # Trigger a repaint to show the ROI box while drawing
                        # Check for hover state
            self.check_hover_state(event.pos())
        elif self.selected_roi and self.resizing:
            # Determine which corner is being resized and adjust accordingly
            if self.resizing == 'topLeft':
                self.selected_roi.setTopLeft(event.pos())
            elif self.resizing == 'topRight':
                self.selected_roi.setTopRight(event.pos())
            elif self.resizing == 'bottomLeft':
                self.selected_roi.setBottomLeft(event.pos())
            elif self.resizing == 'bottomRight':
                self.selected_roi.setBottomRight(event.pos())
            self.update()  # Trigger a repaint to show the updated ROI box
        elif self.selected_roi:
            # Handle moving the ROI
            delta = event.pos() - self.start_point
            self.selected_roi.translate(delta)
            self.start_point = event.pos()
            self.update()  # Trigger a repaint to show the moved ROI box
    #    print("mouseMoveEvent update called")  # Debugging line

    def check_hover_state(self, mouse_pos):
        for roi in self.rois:
            if roi.contains(mouse_pos):
                roi.set_hover(True)  # You need to implement this method in your ROI class
            else:
                roi.set_hover(False)  # You need to implement this method in your ROI class
        self.update()  # Trigger a repaint to show the hover state


    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if self.is_drawing:
                print(f"NewROI created: {self.selected_roi}")
                self.is_drawing = False
                # Create an ROI object instead of QRectF
                new_roi = ROI(self.selected_roi.x(), self.selected_roi.y(),
                            self.selected_roi.width(), self.selected_roi.height())
                self.rois.append(new_roi)
                self.selected_roi = None
                self.update()
            elif self.selected_roi and self.resizing:
                print(f"Resized ROI: {self.selected_roi}")
                # Finalize the resizing
                self.resizing = False
                self.save_state()
            elif self.selected_roi:
                print(f"Moved ROI: {self.selected_roi}")
                # Adjust the ROI position based on the final mouse position
                delta = event.pos() - self.start_point
                self.selected_roi.translate(delta)
                self.selected_roi = None
                self.update()
            self.save_state()
            self.roisChanged.emit()  # Emit signal when ROIs are changed

    def mouseDoubleClickEvent(self, event):
        # Check if an ROI is double-clicked to label it
        for roi in self.rois:
            if roi.contains(event.pos()):
                # List of predefined labels
                labels = list(self.labels_colors.keys())
                # Get the label from the user using a dropdown list
                label, ok = QInputDialog.getItem(self, 'Select Label', 'Choose a label for the ROI:', labels, 0, False)
                if ok and label:
                    roi.label = label
                    self.roisChanged.emit()  # Emit signal when label is changed
                    self.update()
                return


    def resizeEvent(self, event):
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


    def paintEvent(self, event):
      #  print("paintEvent called")  # Debugging line
        super().paintEvent(event)
        painter = QPainter(self)
        for roi in self.rois:
            if isinstance(roi, ROI):  # Check if roi is an instance of ROI
                # Determine the color based on the label
                color = self.labels_colors.get(roi.label, QColor('green'))  # Default to green if no label is set
                if roi == self.selected_roi:
                    pen = QPen(QColor('red'), 2, Qt.DotLine)  # Red dotted line for the selected ROI
                else:
                    pen = QPen(color, 2, Qt.SolidLine)  # Use the color associated with the label
                painter.setPen(pen)
                painter.drawRect(roi)
                if roi.label:
                    # Draw the label text in black for visibility
                    painter.setPen(QColor('white'))
                    painter.drawText(roi.topLeft(), roi.label)






 #   def next_frame(self):
        # Update ROIs for the next frame
  #      self.update_rois_for_new_frame()

  #  def previous_frame(self):
        # Update ROIs for the previous frame
   #     self.update_rois_for_new_frame()

   # def update_rois_for_new_frame(self):
        # Logic to update ROIs for the new frame
        # This could involve recalculating positions, checking for object movement, etc.
   #     self.update()  # Redraw the widget with the updated ROIs


   # def save_rois_to_file(self, file_path):
        # Convert ROIs and their labels to a serializable list
    #    rois_data = [{'x': roi.x(), 'y': roi.y(), 'width': roi.width(), 'height': roi.height(), 'label': roi.label}
     #               for roi in self.rois if isinstance(roi, ROI)]  # Ensure roi is an instance of ROI
      #  print("ROIs data to be saved:", rois_data)  # Debugging output
       # with open(file_path, 'w') as file:
        #    json.dump(rois_data, file, ensure_ascii=False)
       # print(f"ROIs saved to {file_path}")



    def load_rois_from_file(self, file_path):
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
    def capture_frame_rois(self, frame_number):
        print(f"Capturing ROIs for frame {frame_number}")
        # Capture the ROIs for the current frame and store them in a dictionary.
        self.frame_rois[frame_number] = [{'x': roi.x(), 'y': roi.y(), 'width': roi.width(), 'height': roi.height(), 'label': roi.label}
                                        for roi in self.rois]
        print(f"Captured {len(self.frame_rois[frame_number])} ROIs")


    def export_rois(self, file_path, export_format='json'):
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


    def label_selected(self, index):
        label = self.label_selector.itemText(index)
        if self.selected_roi:
            self.selected_roi.label = label
            self.update()

    def capture_frame_rois(self, frame_number):
        """
        Capture the ROIs for the current frame and store them in a dictionary.
        """
        self.frame_rois[frame_number] = self.get_current_roi_data()
     #   if not hasattr(self, 'frame_rois'):
      #      self.frame_rois = {}
      #  self.frame_rois[frame_number] = self.get_current_roi_data()


    def get_current_roi_data(self):
        """
        Retrieve the current ROI data from the video widget.
        This should return a list of dictionaries, with each dictionary containing
        the coordinates, size, and label for one ROI.
        """
        # Assuming self.rois is a list of ROI objects currently displayed in the widget
        roi_data_list = []
        for roi in self.rois:
            # Assuming each ROI object has x, y, width, height, and label attributes
            roi_data = {
                'x': roi.x,
                'y': roi.y,
                'width': roi.width,
                'height': roi.height,
                'label': roi.label
            }
            roi_data_list.append(roi_data)
        
        return roi_data_list

    def get_roi_data_for_frame(self, frame_number):
        """
        Retrieve the ROI data for a specific frame from the video widget.
        This should return a list of dictionaries, with each dictionary containing
        the coordinates, size, and label for one ROI at the given frame.
        """
        # Check if frame-specific ROI data is stored
        if hasattr(self, 'frame_rois') and frame_number in self.frame_rois:
            return self.frame_rois[frame_number]
        else:
            # If no frame-specific ROI data, return current ROI data
            # or handle the absence of data appropriately (e.g., return an empty list or None)
            return self.get_current_roi_data()  # or return []


    def roi_adjusted(self):


        current_frame = self.get_current_frame_number()  # You need to implement this method
        self.video_widget.capture_frame_rois(current_frame)
                # Call this method whenever the ROI is adjusted manually
        self.parent().capture_roi_data()
    # TODO: Implement methods for persistence, labeling, exporting, and other functionalities

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