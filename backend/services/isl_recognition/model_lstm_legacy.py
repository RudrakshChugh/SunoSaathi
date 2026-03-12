"""
ISL Recognition Service - Lightweight LSTM-based model for laptop deployment
"""
import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.constants import MAX_SEQUENCE_LENGTH, TOTAL_KEYPOINTS, KEYPOINT_FEATURES
from shared.utils import normalize_keypoints, pad_sequence, get_logger

logger = get_logger(__name__)

class ISLRecognitionModel(nn.Module):
    """
    Lightweight LSTM-based model for ISL recognition
    Optimized for CPU inference on laptops
    """
    
    def __init__(
        self,
        input_dim: int = TOTAL_KEYPOINTS * KEYPOINT_FEATURES,
        hidden_dim: int = 256,
        num_layers: int = 2,
        num_classes: int = 5,  # Default to 5 for Greetings dataset
        dropout: float = 0.3
    ):
        super(ISLRecognitionModel, self).__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_classes = num_classes
        
        # Bidirectional LSTM
        self.lstm = nn.LSTM(
            input_dim,
            hidden_dim,
            num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Attention mechanism
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1)
        )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes)
        )
    
    def forward(self, x, lengths=None):
        """
        Forward pass
        
        Args:
            x: Input tensor of shape (batch, seq_len, input_dim)
            lengths: Actual sequence lengths (optional)
        
        Returns:
            logits: Output tensor of shape (batch, num_classes)
        """
        # LSTM encoding
        lstm_out, _ = self.lstm(x)  # (batch, seq_len, hidden_dim * 2)
        
        # Attention weights
        attention_weights = self.attention(lstm_out)  # (batch, seq_len, 1)
        attention_weights = torch.softmax(attention_weights, dim=1)
        
        # Weighted sum
        context = torch.sum(attention_weights * lstm_out, dim=1)  # (batch, hidden_dim * 2)
        
        # Classification
        logits = self.classifier(context)  # (batch, num_classes)
        
        return logits

class ISLRecognizer:
    """
    ISL Recognition inference class
    """
    
    def __init__(self, model_path: str = None, device: str = "cpu"):
        self.device = torch.device(device)
        self.model_path = model_path  # Store model path first
        
        # Load vocabulary (will try to load from checkpoint if available)
        self.vocab = self._load_vocabulary()
        
        # Initialize model with correct number of classes
        num_classes = len(self.vocab)
        self.model = ISLRecognitionModel(num_classes=num_classes).to(self.device)
        
        # Load pre-trained weights if available
        if model_path and os.path.exists(model_path):
            try:
                checkpoint = torch.load(model_path, map_location=self.device)
                self.model.load_state_dict(checkpoint['model_state_dict'])
                logger.info(f"Loaded model weights from {model_path}")
            except Exception as e:
                logger.warning(f"Could not load model weights: {e}")
                logger.info("Using randomly initialized weights.")
        else:
            logger.warning("No pre-trained model found. Using randomly initialized weights.")
            logger.info("For production, you should train the model on ISL dataset.")
        
        self.model.eval()
    
    def _load_vocabulary(self) -> List[str]:
        """Load ISL vocabulary from checkpoint or file"""
        # Try to load from checkpoint first (if model was trained)
        if hasattr(self, 'model_path') and self.model_path and os.path.exists(self.model_path):
            try:
                checkpoint = torch.load(self.model_path, map_location=self.device)
                if 'vocab' in checkpoint:
                    logger.info(f"Loaded vocabulary from checkpoint: {len(checkpoint['vocab'])} signs")
                    return checkpoint['vocab']
            except Exception as e:
                logger.warning(f"Could not load vocab from checkpoint: {e}")
        
        # Try to load from vocabulary file in trained_models first
        vocab_paths = [
            os.path.join(os.path.dirname(__file__), '..', '..', 'trained_models', 'vocabulary.json'),
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 
                        'datasets', 'Greetings-processed', 'vocabulary.json'),
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 
                        'datasets', 'selected_vocabulary.json'),
        ]
        
        for vocab_path in vocab_paths:
            if os.path.exists(vocab_path):
                try:
                    import json
                    with open(vocab_path, 'r') as f:
                        vocab = json.load(f)
                    logger.info(f"Loaded vocabulary from {vocab_path}: {len(vocab)} signs")
                    return vocab
                except Exception as e:
                    logger.warning(f"Could not load vocab from {vocab_path}: {e}")
        
        # Final fallback to hardcoded vocabulary
        logger.warning("Using hardcoded vocabulary. For production, train the model on ISL dataset.")
        common_signs = [
            "hello", "thank you", "please", "yes", "no", "help", "sorry",
            "good", "bad", "eat", "drink", "water", "food", "home", "work",
            "family", "friend", "love", "happy", "sad", "angry", "tired",
            "morning", "afternoon", "evening", "night", "today", "tomorrow",
            "yesterday", "now", "later", "here", "there", "what", "when",
            "where", "who", "why", "how", "can", "cannot", "want", "need",
            "like", "dislike", "understand", "not understand", "repeat",
            "slow", "fast", "big", "small", "hot", "cold", "new", "old",
            "good morning", "good night", "how are you", "fine", "okay",
            "excuse me", "welcome", "goodbye", "see you", "take care",
            "mother", "father", "brother", "sister", "child", "baby",
            "man", "woman", "boy", "girl", "doctor", "teacher", "student",
            "hospital", "school", "shop", "restaurant", "bathroom",
            "one", "two", "three", "four", "five", "six", "seven", "eight",
            "nine", "ten", "hundred", "thousand", "money", "expensive", "cheap"
        ]
        return common_signs[:100]  # Limit to 100 for now
    
    def preprocess_keypoints(self, keypoints: np.ndarray) -> torch.Tensor:
        """
        Preprocess keypoints for model input
        
        Args:
            keypoints: Array of shape (num_frames, num_keypoints, 3)
        
        Returns:
            Preprocessed tensor of shape (1, max_seq_len, input_dim)
        """
        # Normalize keypoints - SKIP (Model trained on raw 0-1 coordinates)
        # normalized = normalize_keypoints(keypoints)
        normalized = keypoints

        
        # Flatten keypoints: (num_frames, num_keypoints * 3)
        flattened = normalized.reshape(normalized.shape[0], -1)
        
        # Pad to max sequence length
        padded = pad_sequence(flattened, MAX_SEQUENCE_LENGTH)
        
        # Convert to tensor and add batch dimension
        tensor = torch.from_numpy(padded).float().unsqueeze(0)
        
        return tensor.to(self.device)
    
    @torch.no_grad()
    def recognize(self, keypoints: np.ndarray, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Recognize ISL sign from keypoints
        
        Args:
            keypoints: Array of shape (num_frames, num_keypoints, 3)
            top_k: Number of top predictions to return
        
        Returns:
            List of predictions with sign and confidence
        """
        # Preprocess
        input_tensor = self.preprocess_keypoints(keypoints)
        
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
    
    def recognize_sequence(self, keypoints_sequence: List[np.ndarray]) -> str:
        """
        Recognize a sequence of signs and convert to text
        
        Args:
            keypoints_sequence: List of keypoint arrays
        
        Returns:
            Recognized text
        """
        recognized_signs = []
        
        for keypoints in keypoints_sequence:
            predictions = self.recognize(keypoints, top_k=1)
            if predictions and predictions[0]["confidence"] > 0.5:
                recognized_signs.append(predictions[0]["sign"])
        
        # Join signs into sentence
        text = " ".join(recognized_signs)
        
        return text

# Initialize global recognizer
recognizer = None

def get_recognizer() -> ISLRecognizer:
    """Get or create ISL recognizer instance"""
    global recognizer
    if recognizer is None:
        # Default to trained model path
        default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'trained_models', 'best_model.pth')
        model_path = os.getenv("ISL_MODEL_PATH", default_path)
        recognizer = ISLRecognizer(model_path=model_path, device="cpu")
    return recognizer
