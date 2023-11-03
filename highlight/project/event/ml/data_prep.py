import cv2
import json
import os
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import torchvision

import numpy as np
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)

class VideoDataset(Dataset):
    def __init__(self, video_folder, annotation_folder, frame_width, frame_height, transform=None):
        self.video_folder = video_folder
        self.annotation_folder = annotation_folder
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.transform = transform
        self.videos = self._load_videos()  # Make sure this is correctly initialized
        self.annotations = self._load_annotations()

    def _load_videos(self):
        videos = []
        for event_name in os.listdir(self.video_folder):  # Corrected from self.video_dir
            event_path = os.path.join(self.video_folder, event_name)

            if os.path.isdir(event_path):
                for video_file in os.listdir(event_path):
                    if video_file.endswith('.mp4'):
                        video_path = os.path.join(event_path, video_file)
                        videos.append((event_name, video_path))
        return videos

    def _load_annotations(self):
        annotations = {}
        for annotation_file in os.listdir(self.annotation_folder):  # Use the correct attribute here
            if annotation_file.endswith('.json'):
                event_name = os.path.splitext(annotation_file)[0]
                annotation_path = os.path.join(self.annotation_folder, annotation_file)  # And here
                with open(annotation_path, 'r') as f:
                    annotations[event_name] = json.load(f)
        return annotations


    def __len__(self):
        return len(self.videos)

    def __getitem__(self, idx):
        event_name, video_path = self.videos[idx]
        frames = self._load_video_frames(video_path)
        annotation = self.annotations.get(event_name, {})

        # Apply transformations to each frame
        if self.transform is not None:
            frames = [self.transform(frame) for frame in frames]

        sample = {'frames': torch.stack(frames), 'annotation': annotation}  # Stack frames to create a batch dimension
        return sample


    def _load_video_frames(self, video_path):
        cap = cv2.VideoCapture(video_path)
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            frames.append(frame)
        cap.release()
        return frames

def load_config(config_path='config.json'):
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

def validate_data(dataloader):
    for i, sample in enumerate(dataloader):
        video = sample['frames']  # Assuming this is a batch of tensors after transformation
        annotation = sample['annotation']
        
        # Visual Inspection
        show_batch(video, annotation)

        # Check Data Ranges
        check_data_ranges(video, annotation)

        # Log shapes and data types
        logging.info(f"Batch {i}: Video shape: {video.shape}, Video dtype: {video.dtype}")
        # Annotation shape and dtype logging might need to be adjusted based on the actual structure of annotations

        if i >= 0:  # Validate only the first batch for quick inspection
            break


def show_batch(video, annotation):
    # Assuming video is a tensor of shape (batch_size, channels, height, width)
    batch_size = video.size(0)
    grid = torchvision.utils.make_grid(video)
    plt.imshow(grid.numpy().transpose((1, 2, 0)))
    plt.title("Batch of Video Frames")
    plt.show()

    # Add logic here to display annotations if they are not visualized on the frames directly

def check_data_ranges(video, annotation):
    # Assuming video pixel values are normalized to [0, 1] or [-1, 1]
    video_min, video_max = video.min().item(), video.max().item()
    logging.info(f"Video pixel value range: [{video_min}, {video_max}]")

    # Add logic here to check annotation ranges if necessary

def create_data_loaders(dataset, batch_size):
    train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    return train_loader, val_loader


transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    # Add any other required transformations here
])


if __name__ == "__main__":
    config = load_config()

    
    # Initialize dataset and dataloader using paths from config
    dataset = VideoDataset(
        video_folder=config['video_directory'],
        annotation_folder=config['annotation_directory'],
        frame_width=config['frame_width'],
        frame_height=config['frame_height'],
        transform=transform
    )
    
    # Validate data
    validate_data(dataset)
    
    # Create data loaders
    train_loader, val_loader = create_data_loaders(dataset, batch_size=config['batch_size'])
