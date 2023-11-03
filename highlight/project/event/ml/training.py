import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
import torchvision.transforms as transforms
from torchvision.transforms import Compose
from data_prep import load_config, VideoDataset
from model import IconDetectionModel
import data_prep


# At the beginning of training.py
import data_prep

# Load configuration and prepare data
config = data_prep.load_config()
train_loader, val_loader = data_prep.create_data_loaders(
    data_prep.VideoDataset(
        video_folder=config['video_directory'],
        annotation_folder=config['annotation_directory'],
        frame_width=config['frame_width'],
        frame_height=config['frame_height'],
        transform=data_prep.transform
    ),
    batch_size=config['batch_size']
)

# ... rest of training.py script ...



# Function to train the model
def train_model(model, train_loader, criterion, optimizer, num_epochs, writer, device):
    print('Training Started')
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        for batch_idx, (inputs, labels) in enumerate(train_loader):
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * inputs.size(0)
            
            # Log the loss
            writer.add_scalar('training loss', loss.item(), epoch * len(train_loader) + batch_idx)
            writer.flush()  
        
        epoch_loss = running_loss / len(train_loader.dataset)
        print(f'Epoch {epoch+1}/{num_epochs} Loss: {epoch_loss:.4f}')

        # Log the epoch loss
        writer.add_scalar('epoch training loss', epoch_loss, epoch)
    print("Training completed")
    return model

# Function to evaluate the model
def evaluate_model(model, val_loader, criterion, writer, device):
    print('Evaluating Model')
    model.eval()
    running_loss = 0.0
    with torch.no_grad():
        for batch_idx, (inputs, labels) in enumerate(val_loader):
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            running_loss += loss.item() * inputs.size(0)
            
            # Log the loss
            writer.add_scalar('validation loss', loss.item(), batch_idx)
        
    epoch_loss = running_loss / len(val_loader.dataset)
    print(f'Validation Loss: {epoch_loss:.4f}')
    
    # Log the epoch loss
    writer.add_scalar('epoch validation loss', epoch_loss, len(val_loader))
print("Evaluation completed")
# Main script
if __name__ == "__main__":
    config = load_config()
    
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
# Define the transformations
transform = Compose([
    transforms.Resize((224, 224)),  # Resize to the input size expected by the model
    transforms.ToTensor(),  # Convert to tensor
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # Normalize
])

# Hyperparameters from config
num_epochs = config['num_epochs']
learning_rate = config['learning_rate']
batch_size = config['batch_size']
num_classes = config['num_classes']  # Adjust based on your dataset

# Initialize TensorBoard writer
writer = SummaryWriter('runs/icon_detection_experiment')

# Load Data with the defined transformations
try:
    train_dataset = VideoDataset(config['train_data_path'], config['train_annotations_path'], transform=transform)
    val_dataset = VideoDataset(config['val_data_path'], config['val_annotations_path'], transform=transform)
    train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)
    print("Number of training batches:", len(train_loader))
    print("Number of validation batches:", len(val_loader))
    val_loader = DataLoader(dataset=val_dataset, batch_size=batch_size, shuffle=False)

    # Initialize model, loss, and optimizer
    model = IconDetectionModel(num_classes=num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Train and Evaluate Model
    model = train_model(model, train_loader, criterion, optimizer, num_epochs, writer, device)
    evaluate_model(model, val_loader, criterion, writer, device)

# Close the TensorBoard writer
finally:
    writer.close()

