"""
Generate Sample ISL Dataset for Testing
Creates dummy data to test the training pipeline
"""
import json
import numpy as np
from pathlib import Path
import argparse

def generate_sample_dataset(output_dir, num_signs=10, samples_per_sign=50, train_split=0.8):
    """
    Generate a sample ISL dataset with random keypoints
    
    Args:
        output_dir: Output directory for dataset
        num_signs: Number of different signs
        samples_per_sign: Number of samples per sign
        train_split: Fraction of data for training (rest for validation)
    """
    
    output_dir = Path(output_dir)
    train_dir = output_dir / 'train'
    val_dir = output_dir / 'val'
    
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate vocabulary
    vocabulary = [f"sign_{i:03d}" for i in range(num_signs)]
    
    with open(output_dir / 'vocabulary.json', 'w') as f:
        json.dump(vocabulary, f, indent=2)
    
    print(f"Generated vocabulary with {num_signs} signs")
    
    # Generate samples for each sign
    total_samples = 0
    
    for sign_idx, sign_label in enumerate(vocabulary):
        print(f"Generating samples for '{sign_label}'...")
        
        for sample_idx in range(samples_per_sign):
            # Generate random sequence length (20-60 frames)
            seq_len = np.random.randint(20, 61)
            
            # Generate frames
            frames = []
            for frame_id in range(seq_len):
                # Generate 543 keypoints with 3 coordinates each
                # Add some pattern so it's not completely random
                base_keypoints = np.random.rand(543, 3).astype(float)
                
                # Add temporal consistency (smooth transitions)
                if frame_id > 0:
                    prev_keypoints = frames[-1]['keypoints']
                    base_keypoints = 0.7 * np.array(prev_keypoints) + 0.3 * base_keypoints
                
                keypoints = base_keypoints.tolist()
                
                frames.append({
                    'frame_id': frame_id,
                    'keypoints': keypoints
                })
            
            # Create sample
            sample = {
                'sign_label': sign_label,
                'frames': frames
            }
            
            # Determine if train or val
            is_train = sample_idx < int(samples_per_sign * train_split)
            target_dir = train_dir if is_train else val_dir
            
            # Save to JSON
            filename = f"{sign_label}_{sample_idx:03d}.json"
            with open(target_dir / filename, 'w') as f:
                json.dump(sample, f)
            
            total_samples += 1
    
    # Print summary
    train_count = len(list(train_dir.glob('*.json')))
    val_count = len(list(val_dir.glob('*.json')))
    
    print("\n" + "=" * 70)
    print("Sample Dataset Generated!")
    print("=" * 70)
    print(f"Output directory: {output_dir}")
    print(f"Vocabulary size: {num_signs} signs")
    print(f"Training samples: {train_count}")
    print(f"Validation samples: {val_count}")
    print(f"Total samples: {total_samples}")
    print("=" * 70)
    print("\nYou can now train the model with:")
    print(f"python train.py \\")
    print(f"  --train_data {train_dir} \\")
    print(f"  --val_data {val_dir} \\")
    print(f"  --vocab {output_dir / 'vocabulary.json'} \\")
    print(f"  --epochs 20")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate sample ISL dataset')
    parser.add_argument('--output', type=str, default='./sample_dataset',
                        help='Output directory for dataset')
    parser.add_argument('--num_signs', type=int, default=10,
                        help='Number of different signs')
    parser.add_argument('--samples_per_sign', type=int, default=50,
                        help='Number of samples per sign')
    parser.add_argument('--train_split', type=float, default=0.8,
                        help='Fraction of data for training')
    
    args = parser.parse_args()
    
    generate_sample_dataset(
        output_dir=args.output,
        num_signs=args.num_signs,
        samples_per_sign=args.samples_per_sign,
        train_split=args.train_split
    )
