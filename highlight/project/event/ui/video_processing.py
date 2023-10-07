import cv2
from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt

def extract_thumbnails(video_file):
    cap = cv2.VideoCapture(video_file)
    
    # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Get the frame rate of the video
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    # Calculate the duration of the video in milliseconds
    duration = total_frames * (1000/fps)
    
    thumbnails = []

    for i in range(0, int(duration), 60000):  # 10-second intervals
        cap.set(cv2.CAP_PROP_POS_MSEC, i)
        ret, frame = cap.read()
        if ret:
            # Convert the frame to QImage for PyQt
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            q_img = q_img.scaled(q_img.width() // 20, q_img.height() // 20, Qt.KeepAspectRatio)
            thumbnails.append(q_img)
        print(f"Extracting thumbnail at {i} milliseconds")
    cap.release()
    return thumbnails
