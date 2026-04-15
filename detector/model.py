"""
DeepfakeDetector class for inference.
"""
import torch
import torch.nn as nn
from torchvision import transforms
from efficientnet_pytorch import EfficientNet
from PIL import Image
from dataclasses import dataclass

@dataclass
class DetectionResult:
    """Result from deepfake detection."""
    label: str  # "real" or "fake"
    confidence: float  # 0.0 to 1.0

class DeepfakeDetector:
    """Deepfake detection model for image inference."""
    
    def __init__(self, model_path: str, device: str = "cpu"):
        """
        Initialize the detector.
        
        Args:
            model_path: Path to the trained model (.pth file)
            device: "cpu" or "cuda"
        """
        self.device = torch.device(device)
        self.image_size = 224  # EfficientNet-B4 uses 224x224
        
        # Load model
        self.model = EfficientNet.from_pretrained('efficientnet-b4', num_classes=2)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # Transform
        self.transform = transforms.Compose([
            transforms.Resize((self.image_size, self.image_size)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        print(f"Model loaded from {model_path}")
    
    def detect(self, file_path: str) -> DetectionResult:
        """
        Detect if an image is real or fake.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            DetectionResult with label and confidence
            
        Raises:
            ProcessingError: If image cannot be processed
        """
        try:
            # Load and preprocess image
            image = Image.open(file_path).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Inference
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                predicted_class = outputs.argmax(dim=1).item()
                confidence = probabilities[0][predicted_class].item()
            
            # Map class index to label
            # Class 0 = fake, Class 1 = real (based on ImageFolder alphabetical order)
            label = "real" if predicted_class == 1 else "fake"
            
            return DetectionResult(label=label, confidence=confidence)
            
        except Exception as e:
            raise ProcessingError(f"Failed to process image: {str(e)}")
    
    def generate_thumbnail(self, file_path: str, output_path: str) -> None:
        """
        Generate a thumbnail for an image.
        
        Args:
            file_path: Path to the input image
            output_path: Path to save the thumbnail
        """
        try:
            image = Image.open(file_path).convert('RGB')
            image.thumbnail((200, 200))
            image.save(output_path, "JPEG")
        except Exception as e:
            print(f"Warning: Failed to generate thumbnail: {e}")

class ProcessingError(Exception):
    """Exception raised when image processing fails."""
    pass
