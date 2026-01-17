"""
Quick test script to verify the trained ISL model works
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from model import ISLRecognizer
import numpy as np

# Initialize recognizer with trained model
model_path = "./trained_models/best_model.pth"
recognizer = ISLRecognizer(model_path=model_path, device="cpu")

print(f"Model loaded successfully!")
print(f"Vocabulary: {recognizer.vocab}")
print(f"Number of signs: {len(recognizer.vocab)}")

# Create dummy keypoints for testing (543 keypoints x 3 coordinates x 10 frames)
dummy_keypoints = np.random.rand(10, 543, 3).astype(np.float32)

# Test recognition
predictions = recognizer.recognize(dummy_keypoints, top_k=3)

print("\nTest predictions:")
for i, pred in enumerate(predictions):
    print(f"{i+1}. {pred['sign']}: {pred['confidence']:.4f}")
