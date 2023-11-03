import torch
import torch.nn as nn
from torchvision.models.video import r3d_18

class IconDetectionModel(nn.Module):
    def __init__(self, num_classes):
        super(IconDetectionModel, self).__init__()
        self.model = r3d_18(pretrained=True)
        num_ftrs = self.model.fc.in_features
        self.model.fc = nn.Linear(num_ftrs, num_classes)

    def forward(self, x):
        return self.model(x)
