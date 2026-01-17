"""
Extract Keypoints from INCLUDE-50 Videos
Processes ISL videos and extracts MediaPipe keypoints
"""
import cv2
import json
import numpy as np
from pathlib import Path
import argparse
from tqdm import tqdm
import sys
import os

# Add parent directory to path for MediaPipe imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def extract_keypoints_from_video(video_path, max_frames=100):
    """
    Extract keypoints from a video using MediaPipe
    
    Args:
        video_path: Path to video file
        max_frames: Maximum number of frames to process
        
    Returns:
        List of frames with keypoints
    """
    try:
        # Import MediaPipe
        import mediapipe as mp
        
        mp_holistic = mp.solutions.holistic
        holistic = mp_holistic.Holistic(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            print(f"Error: Could not open video {video_path}")
            return None
        
        frames = []
        frame_id = 0
        
        while cap.isOpened() and frame_id < max_frames:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = holistic.process(frame_rgb)
            
            # Extract keypoints
            keypoints = []
            
            # Pose landmarks (33 points)
            if results.pose_landmarks:
                for landmark in results.pose_landmarks.landmark:
                    keypoints.append([landmark.x, landmark.y, landmark.z])
            else:
                # Add zeros if no pose detected
                for _ in range(33):
                    keypoints.append([0.0, 0.0, 0.0])
            
            # Left hand landmarks (21 points)
            if results.left_hand_landmarks:
                for landmark in results.left_hand_landmarks.landmark:
                    keypoints.append([landmark.x, landmark.y, landmark.z])
            else:
                for _ in range(21):
                    keypoints.append([0.0, 0.0, 0.0])
            
            # Right hand landmarks (21 points)
            if results.right_hand_landmarks:
                for landmark in results.right_hand_landmarks.landmark:
                    keypoints.append([landmark.x, landmark.y, landmark.z])
            else:
                for _ in range(21):
                    keypoints.append([0.0, 0.0, 0.0])
            
            # Face landmarks (468 points) - optional, can skip for performance
            if results.face_landmarks:
                for landmark in results.face_landmarks.landmark:
                    keypoints.append([landmark.x, landmark.y, landmark.z])
            else:
                for _ in range(468):
                    keypoints.append([0.0, 0.0, 0.0])
            
            frames.append({
                'frame_id': frame_id,
                'keypoints': keypoints
            })
            
            frame_id += 1
        
        cap.release()
        holistic.close()
        
        return frames
        
    except Exception as e:
        print(f"Error processing video {video_path}: {e}")
        return None


def process_dataset(input_dir, output_dir, vocab_file=None, train_split=0.8):
    """
    Process entire INCLUDE-50 dataset
    
    Args:
        input_dir: Directory containing INCLUDE-50 videos
        output_dir: Output directory for processed data
        vocab_file: Optional vocabulary file (JSON list of words to process)
        train_split: Fraction of data for training
    """
    
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    # Create output directories
    train_dir = output_dir / 'train'
    val_dir = output_dir / 'val'
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)
    
    # Load vocabulary if provided
    if vocab_file:
        with open(vocab_file, 'r') as f:
            vocabulary = json.load(f)
        print(f"Processing {len(vocabulary)} words from vocabulary file")
    else:
        # Process all subdirectories
        vocabulary = [d.name for d in input_dir.iterdir() if d.is_dir()]
        print(f"Processing all {len(vocabulary)} words found in dataset")
    
    # Process each word
    total_videos = 0
    successful_videos = 0
    
    for word in vocabulary:
        word_dir = input_dir / word
        
        if not word_dir.exists():
            print(f"Warning: Directory not found for word '{word}', skipping...")
            continue
        
        print(f"\nProcessing word: {word}")
        
        # Get all video files
        video_files = (list(word_dir.glob('*.mp4')) + list(word_dir.glob('*.avi')) + 
                      list(word_dir.glob('*.MOV')) + list(word_dir.glob('*.mov')))
        
        if not video_files:
            print(f"  No videos found for '{word}'")
            continue
        
        print(f"  Found {len(video_files)} videos")
        
        # Process each video
        for idx, video_file in enumerate(tqdm(video_files, desc=f"  {word}")):
            total_videos += 1
            
            # Extract keypoints
            frames = extract_keypoints_from_video(video_file)
            
            if frames is None or len(frames) == 0:
                print(f"  Failed to process: {video_file.name}")
                continue
            
            # Create JSON data
            data = {
                'sign_label': word,
                'frames': frames,
                'source_video': str(video_file.name)
            }
            
            # Determine train or val
            is_train = idx < int(len(video_files) * train_split)
            target_dir = train_dir if is_train else val_dir
            
            # Save JSON
            output_file = target_dir / f"{word}_{idx:03d}.json"
            with open(output_file, 'w') as f:
                json.dump(data, f)
            
            successful_videos += 1
    
    # Save vocabulary
    vocab_output = output_dir / 'vocabulary.json'
    with open(vocab_output, 'w') as f:
        json.dump(vocabulary, f, indent=2)
    
    # Print summary
    train_count = len(list(train_dir.glob('*.json')))
    val_count = len(list(val_dir.glob('*.json')))
    
    print("\n" + "=" * 70)
    print("Dataset Processing Complete!")
    print("=" * 70)
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Vocabulary size: {len(vocabulary)} words")
    print(f"Total videos processed: {total_videos}")
    print(f"Successful extractions: {successful_videos}")
    print(f"Failed extractions: {total_videos - successful_videos}")
    print(f"Training samples: {train_count}")
    print(f"Validation samples: {val_count}")
    print("=" * 70)
    print(f"\nVocabulary saved to: {vocab_output}")
    print("\nYou can now train the model with:")
    print(f"python train.py \\")
    print(f"  --train_data {train_dir} \\")
    print(f"  --val_data {val_dir} \\")
    print(f"  --vocab {vocab_output} \\")
    print(f"  --epochs 50")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract keypoints from INCLUDE-50 videos')
    parser.add_argument('--input_dir', type=str, required=True,
                        help='Directory containing INCLUDE-50 videos')
    parser.add_argument('--output_dir', type=str, required=True,
                        help='Output directory for processed data')
    parser.add_argument('--vocab_file', type=str, default=None,
                        help='Optional vocabulary file (JSON list of words to process)')
    parser.add_argument('--train_split', type=float, default=0.8,
                        help='Fraction of data for training (default: 0.8)')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("INCLUDE-50 Keypoint Extraction")
    print("=" * 70)
    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Train split: {args.train_split * 100}%")
    print("=" * 70)
    
    process_dataset(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        vocab_file=args.vocab_file,
        train_split=args.train_split
    )
