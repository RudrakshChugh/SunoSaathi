"""
ISL Recognition Service - ResNet18 Image-based Model
Trained on ISL_CSLRT_TrainReady_Word dataset with 79% accuracy
"""
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
from typing import List, Dict, Any
import sys
import os
import json
import io
import base64

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.utils import get_logger

logger = get_logger(__name__)

class ISLResNet18(nn.Module):
    """
    ResNet18 model for ISL word recognition
    Matches the architecture from training script
    """
    
    def __init__(self, num_classes: int = 5):
        super(ISLResNet18, self).__init__()
        
        # Load pretrained ResNet18
        self.model = models.resnet18(weights=None)  # We'll load our trained weights
        
        # Replace final layer to match our num_classes
        self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
    
    def forward(self, x):
        return self.model(x)


class ISLRecognizerResNet:
    """
    ISL Recognition inference class for ResNet18 image-based model
    """
    
    def __init__(self, model_path: str = None, device: str = "cpu"):
        self.device = torch.device(device)
        self.model_path = model_path
        
        # Load vocabulary
        self.vocab = self._load_vocabulary()
        
        # Initialize model with correct number of classes
        num_classes = len(self.vocab)
        self.model = ISLResNet18(num_classes=num_classes).to(self.device)
        
        # Load pre-trained weights
        if model_path and os.path.exists(model_path):
            try:
                # Load the state dict
                state_dict = torch.load(model_path, map_location=self.device)
                self.model.load_state_dict(state_dict)
                logger.info(f"✅ Loaded ResNet18 model from {model_path}")
                logger.info(f"📚 Vocabulary: {self.vocab}")
                logger.info(f"🎯 Model accuracy: 79% (on test set)")
            except Exception as e:
                logger.error(f"❌ Could not load model weights: {e}")
                raise RuntimeError(f"Failed to load model: {e}")
        else:
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        self.model.eval()
        
        # Define image transforms (matching training script)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def _load_vocabulary(self) -> List[str]:
        """Load ISL vocabulary from vocabulary.json"""
        vocab_paths = [
            os.path.join(os.path.dirname(__file__), '..', '..', 'trained_models', 'vocabulary.json'),
            os.path.join(os.path.dirname(self.model_path), 'vocabulary.json') if self.model_path else None,
        ]
        
        for vocab_path in vocab_paths:
            if vocab_path and os.path.exists(vocab_path):
                try:
                    with open(vocab_path, 'r') as f:
                        vocab = json.load(f)
                    logger.info(f"Loaded vocabulary from {vocab_path}: {len(vocab)} words")
                    return vocab
                except Exception as e:
                    logger.warning(f"Could not load vocab from {vocab_path}: {e}")
        
        # Fallback vocabulary (should match training)
        logger.warning("Using fallback vocabulary")
        return ["alright", "good_afternoon", "good_morning", "hello", "how_are_you"]
    
    def preprocess_image(self, image_data: Any) -> torch.Tensor:
        """
        Preprocess image for model input
        
        Args:
            image_data: Can be PIL Image, numpy array, or base64 string
        
        Returns:
            Preprocessed tensor of shape (1, 3, 224, 224)
        """
        # Convert to PIL Image if needed
        if isinstance(image_data, str):
            # Base64 encoded image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        elif isinstance(image_data, np.ndarray):
            # Numpy array
            image = Image.fromarray(image_data).convert('RGB')
        elif isinstance(image_data, Image.Image):
            # Already PIL Image
            image = image.convert('RGB')
        else:
            raise ValueError(f"Unsupported image type: {type(image_data)}")
        
        # Apply transforms
        tensor = self.transform(image).unsqueeze(0)  # Add batch dimension
        
        return tensor.to(self.device)
    
    @torch.no_grad()
    def recognize(self, image_data: Any, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Recognize ISL sign from image
        
        Args:
            image_data: Image data (PIL Image, numpy array, or base64 string)
            top_k: Number of top predictions to return
        
        Returns:
            List of predictions with sign and confidence
        """
        # Preprocess
        input_tensor = self.preprocess_image(image_data)
        
        # Inference
        logits = self.model(input_tensor)
        probs = torch.softmax(logits, dim=-1)
        
        # Get top-k predictions
        top_probs, top_indices = torch.topk(probs, k=min(top_k, len(self.vocab)), dim=-1)
        
        # Format results
        predictions = []
        for prob, idx in zip(top_probs[0].cpu().numpy(), top_indices[0].cpu().numpy()):
            predictions.append({
                "sign": self.vocab[idx],
                "confidence": float(prob)
            })
        
        return predictions
    
    def recognize_from_frame(self, frame: np.ndarray, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Recognize ISL sign from video frame (numpy array)
        
        Args:
            frame: Video frame as numpy array (H, W, 3) in RGB or BGR
            top_k: Number of top predictions to return
        
        Returns:
            List of predictions with sign and confidence
        """
        # Convert BGR to RGB if needed (OpenCV uses BGR)
        if frame.shape[2] == 3:
            # Assume it might be BGR, convert to RGB
            frame_rgb = frame[:, :, ::-1]
        else:
            frame_rgb = frame
        
        return self.recognize(frame_rgb, top_k=top_k)


# Initialize global recognizer
recognizer = None

def get_recognizer() -> ISLRecognizerResNet:
    """Get or create ISL recognizer instance"""
    global recognizer
    if recognizer is None:
        # Default to trained ResNet18 model path
        default_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'trained_models', 
            'resnet18_word_best.pth'
        )
        model_path = os.getenv("ISL_MODEL_PATH", default_path)
        
        logger.info(f"🚀 Initializing ResNet18 ISL Recognizer...")
        logger.info(f"📁 Model path: {model_path}")
        
        recognizer = ISLRecognizerResNet(model_path=model_path, device="cpu")
        
        logger.info("✅ ResNet18 ISL Recognizer ready!")
    
    return recognizer
