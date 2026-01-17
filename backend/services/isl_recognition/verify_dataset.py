"""
Verify Processed ISL Dataset
Checks that all JSON files are valid and properly formatted
"""
import json
import numpy as np
from pathlib import Path
import argparse
from collections import Counter

def verify_dataset(data_dir):
    """
    Verify the processed dataset
    
    Args:
        data_dir: Directory containing processed data (with train/ and val/ subdirs)
    """
    
    data_dir = Path(data_dir)
    train_dir = data_dir / 'train'
    val_dir = data_dir / 'val'
    vocab_file = data_dir / 'vocabulary.json'
    
    print("=" * 70)
    print("Dataset Verification")
    print("=" * 70)
    
    # Check directories exist
    if not train_dir.exists():
        print(f"❌ Training directory not found: {train_dir}")
        return False
    
    if not val_dir.exists():
        print(f"❌ Validation directory not found: {val_dir}")
        return False
    
    if not vocab_file.exists():
        print(f"❌ Vocabulary file not found: {vocab_file}")
        return False
    
    print(f"✓ All directories found")
    
    # Load vocabulary
    with open(vocab_file, 'r') as f:
        vocabulary = json.load(f)
    
    print(f"✓ Vocabulary loaded: {len(vocabulary)} words")
    print(f"  Words: {', '.join(vocabulary[:10])}{'...' if len(vocabulary) > 10 else ''}")
    
    # Verify training data
    print("\nVerifying training data...")
    train_files = list(train_dir.glob('*.json'))
    train_labels = []
    train_errors = []
    
    for json_file in train_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Check required fields
            if 'sign_label' not in data:
                train_errors.append(f"{json_file.name}: Missing 'sign_label'")
                continue
            
            if 'frames' not in data:
                train_errors.append(f"{json_file.name}: Missing 'frames'")
                continue
            
            # Check label is in vocabulary
            if data['sign_label'] not in vocabulary:
                train_errors.append(f"{json_file.name}: Label '{data['sign_label']}' not in vocabulary")
            
            train_labels.append(data['sign_label'])
            
            # Check frames
            if len(data['frames']) == 0:
                train_errors.append(f"{json_file.name}: No frames")
                continue
            
            # Check first frame structure
            first_frame = data['frames'][0]
            if 'keypoints' not in first_frame:
                train_errors.append(f"{json_file.name}: Frame missing 'keypoints'")
                continue
            
            keypoints = np.array(first_frame['keypoints'])
            if keypoints.shape != (543, 3):
                train_errors.append(f"{json_file.name}: Invalid keypoints shape {keypoints.shape}, expected (543, 3)")
        
        except Exception as e:
            train_errors.append(f"{json_file.name}: {str(e)}")
    
    print(f"✓ Training files: {len(train_files)}")
    
    if train_errors:
        print(f"❌ Training errors: {len(train_errors)}")
        for error in train_errors[:5]:
            print(f"  - {error}")
        if len(train_errors) > 5:
            print(f"  ... and {len(train_errors) - 5} more errors")
    else:
        print(f"✓ No errors in training data")
    
    # Verify validation data
    print("\nVerifying validation data...")
    val_files = list(val_dir.glob('*.json'))
    val_labels = []
    val_errors = []
    
    for json_file in val_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            if 'sign_label' not in data or 'frames' not in data:
                val_errors.append(f"{json_file.name}: Missing required fields")
                continue
            
            if data['sign_label'] not in vocabulary:
                val_errors.append(f"{json_file.name}: Label not in vocabulary")
            
            val_labels.append(data['sign_label'])
            
            if len(data['frames']) == 0:
                val_errors.append(f"{json_file.name}: No frames")
        
        except Exception as e:
            val_errors.append(f"{json_file.name}: {str(e)}")
    
    print(f"✓ Validation files: {len(val_files)}")
    
    if val_errors:
        print(f"❌ Validation errors: {len(val_errors)}")
        for error in val_errors[:5]:
            print(f"  - {error}")
        if len(val_errors) > 5:
            print(f"  ... and {len(val_errors) - 5} more errors")
    else:
        print(f"✓ No errors in validation data")
    
    # Check label distribution
    print("\nLabel Distribution:")
    print("Training:")
    train_counts = Counter(train_labels)
    for label, count in sorted(train_counts.items()):
        print(f"  {label}: {count} samples")
    
    print("\nValidation:")
    val_counts = Counter(val_labels)
    for label, count in sorted(val_counts.items()):
        print(f"  {label}: {count} samples")
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary:")
    print("=" * 70)
    print(f"Vocabulary: {len(vocabulary)} words")
    print(f"Training samples: {len(train_files)}")
    print(f"Validation samples: {len(val_files)}")
    print(f"Total samples: {len(train_files) + len(val_files)}")
    print(f"Training errors: {len(train_errors)}")
    print(f"Validation errors: {len(val_errors)}")
    
    if len(train_errors) == 0 and len(val_errors) == 0:
        print("\n✅ Dataset is ready for training!")
        print("\nNext step:")
        print(f"python train.py \\")
        print(f"  --train_data {train_dir} \\")
        print(f"  --val_data {val_dir} \\")
        print(f"  --vocab {vocab_file} \\")
        print(f"  --epochs 50")
        return True
    else:
        print("\n❌ Dataset has errors. Please fix them before training.")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Verify processed ISL dataset')
    parser.add_argument('--data_dir', type=str, required=True,
                        help='Directory containing processed data')
    
    args = parser.parse_args()
    
    verify_dataset(args.data_dir)
