"""
ISL Recognition Model Training Script
Trains the LSTM model on Indian Sign Language dataset
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import json
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import ISLRecognitionModel

class ISLDataset(Dataset):
    """
    Dataset for ISL recognition training
    Expects data in format:
    {
        "sign_label": "hello",
        "frames": [
            {
                "frame_id": 0,
                "keypoints": [[x, y, z], [x, y, z], ...]  # 543 keypoints
            },
            ...
        ]
    }
    """
    def __init__(self, data_path, vocab_path, max_sequence_length=100, create_vocab=False):
        self.data_path = Path(data_path)
        self.max_sequence_length = max_sequence_length
        self.samples = []
        
        # Load all data files first to determine labels if needed
        self._load_data()
        
        # Handle vocabulary
        if create_vocab:
            # Generate from data
            labels = set(sample['sign_label'] for sample in self.samples)
            self.vocab = sorted(list(labels))
            # Save it
            with open(vocab_path, 'w') as f:
                json.dump(self.vocab, f, indent=2)
            print(f"Generated and saved vocabulary with {len(self.vocab)} signs")
        else:
            # Load existing
            if os.path.exists(vocab_path):
                with open(vocab_path, 'r') as f:
                    self.vocab = json.load(f)
            else:
                # Fallback: Generate from data if file missing
                 print(f"Vocabulary file {vocab_path} not found. Generating from data...")
                 labels = set(sample['sign_label'] for sample in self.samples)
                 self.vocab = sorted(list(labels))
                 with open(vocab_path, 'w') as f:
                    json.dump(self.vocab, f, indent=2)
        
        self.label_to_idx = {label: idx for idx, label in enumerate(self.vocab)}
        self.idx_to_label = {idx: label for label, idx in self.label_to_idx.items()}
    
    def _load_data(self):
        """Load all JSON files from data directory"""
        for json_file in self.data_path.glob('*.json'):
            with open(json_file, 'r') as f:
                data = json.load(f)
                self.samples.append(data)
        
        print(f"Loaded {len(self.samples)} samples from {self.data_path}")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        # Extract keypoints from frames
        keypoints_sequence = []
        for frame in sample['frames']:
            keypoints = np.array(frame['keypoints'], dtype=np.float32)
            # keypoints shape: (543, 3)
            keypoints_sequence.append(keypoints)
        
        # Convert to numpy array: (num_frames, 543, 3)
        # Use stack to ensure 3D shape even with 1 frame
        if len(keypoints_sequence) > 0:
            keypoints_sequence = np.stack(keypoints_sequence, axis=0)
        else:
            keypoints_sequence = np.zeros((0, 543, 3), dtype=np.float32)
        
        # Pad or truncate to max_sequence_length
        seq_len = len(keypoints_sequence)
        if seq_len < self.max_sequence_length:
            # Pad with zeros: need shape (max_seq_len - seq_len, 543, 3)
            padding = np.zeros((self.max_sequence_length - seq_len, 543, 3), dtype=np.float32)
            keypoints_sequence = np.concatenate([keypoints_sequence, padding], axis=0)
        else:
            # Truncate
            keypoints_sequence = keypoints_sequence[:self.max_sequence_length]
        
        # Flatten keypoints (543 * 3 = 1629)
        # Shape: (max_sequence_length, 1629)
        keypoints_sequence = keypoints_sequence.reshape(self.max_sequence_length, -1)
        
        # Get label index
        label = sample['sign_label']
        label_idx = self.label_to_idx.get(label, 0)  # Default to 0 if unknown
        
        return {
            'keypoints': torch.FloatTensor(keypoints_sequence),
            'label': torch.LongTensor([label_idx])[0],  # Remove extra dimension
            'seq_len': min(seq_len, self.max_sequence_length)
        }


def train_model(
    train_data_path,
    val_data_path,
    vocab_path,
    output_dir,
    num_epochs=50,
    batch_size=32,
    learning_rate=0.001,
    device='cpu'
):
    """
    Train the ISL recognition model
    
    Args:
        train_data_path: Path to training data directory
        val_data_path: Path to validation data directory
        vocab_path: Path to vocabulary JSON file
        output_dir: Directory to save model checkpoints
        num_epochs: Number of training epochs
        batch_size: Batch size for training
        learning_rate: Learning rate for optimizer
        device: 'cpu' or 'cuda'
    """
    
    print("=" * 70)
    print("ISL Recognition Model Training")
    print("=" * 70)
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load vocabulary
    with open(vocab_path, 'r') as f:
        vocab = json.load(f)
    
    vocab_size = len(vocab)
    print(f"\nVocabulary size: {vocab_size} signs")
    
    # Create datasets
    print("\nLoading datasets...")
    # Allow training set to create/update vocabulary
    train_dataset = ISLDataset(train_data_path, vocab_path, create_vocab=True)
    val_dataset = ISLDataset(val_data_path, vocab_path, create_vocab=False)
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0
    )
    
    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")
    
    # Initialize model
    print(f"\nInitializing model on {device}...")
    model = ISLRecognitionModel(num_classes=vocab_size)
    model = model.to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5
    )
    
    # Training loop
    best_val_loss = float('inf')
    best_val_acc = 0.0
    
    print("\nStarting training...")
    print("=" * 70)
    
    for epoch in range(num_epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for batch_idx, batch in enumerate(train_loader):
            keypoints = batch['keypoints'].to(device)
            labels = batch['label'].to(device)  # Don't squeeze, already correct shape
            
            # Forward pass
            optimizer.zero_grad()
            outputs = model(keypoints)
            loss = criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            # Statistics
            train_loss += loss.item()
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += predicted.eq(labels).sum().item()
            
            if (batch_idx + 1) % 10 == 0:
                print(f"Epoch [{epoch+1}/{num_epochs}] "
                      f"Batch [{batch_idx+1}/{len(train_loader)}] "
                      f"Loss: {loss.item():.4f}")
        
        train_loss /= len(train_loader)
        train_acc = 100. * train_correct / train_total
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for batch in val_loader:
                keypoints = batch['keypoints'].to(device)
                labels = batch['label'].to(device)  # Don't squeeze
                
                outputs = model(keypoints)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()
        
        val_loss /= len(val_loader)
        val_acc = 100. * val_correct / val_total
        
        # Update learning rate
        scheduler.step(val_loss)
        
        # Print epoch summary
        print(f"\nEpoch [{epoch+1}/{num_epochs}] Summary:")
        print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"  Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
        print("-" * 70)
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_val_loss = val_loss
            
            checkpoint = {
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'val_acc': val_acc,
                'vocab': vocab
            }
            
            torch.save(checkpoint, output_dir / 'best_model.pth')
            print(f"✓ Saved best model (Val Acc: {val_acc:.2f}%)")
        
        # Save checkpoint every 10 epochs
        if (epoch + 1) % 10 == 0:
            checkpoint = {
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'val_acc': val_acc,
                'vocab': vocab
            }
            torch.save(checkpoint, output_dir / f'checkpoint_epoch_{epoch+1}.pth')
    
    print("\n" + "=" * 70)
    print("Training Complete!")
    print(f"Best Validation Accuracy: {best_val_acc:.2f}%")
    print(f"Best Validation Loss: {best_val_loss:.4f}")
    print(f"Model saved to: {output_dir / 'best_model.pth'}")
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train ISL Recognition Model')
    parser.add_argument('--train_data', type=str, required=True,
                        help='Path to training data directory')
    parser.add_argument('--val_data', type=str, required=True,
                        help='Path to validation data directory')
    parser.add_argument('--vocab', type=str, required=True,
                        help='Path to vocabulary JSON file')
    parser.add_argument('--output', type=str, default='./trained_models',
                        help='Output directory for model checkpoints')
    parser.add_argument('--epochs', type=int, default=50,
                        help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=32,
                        help='Batch size')
    parser.add_argument('--lr', type=float, default=0.001,
                        help='Learning rate')
    parser.add_argument('--device', type=str, default='cpu',
                        choices=['cpu', 'cuda'],
                        help='Device to use for training')
    
    args = parser.parse_args()
    
    train_model(
        train_data_path=args.train_data,
        val_data_path=args.val_data,
        vocab_path=args.vocab,
        output_dir=args.output,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        device=args.device
    )
