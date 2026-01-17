"""
Quick extraction script for Greetings dataset
Handles folder names with numbers like "48. Hello"
"""
import cv2
import json
import numpy as np
from pathlib import Path
from tqdm import tqdm
import mediapipe as mp

def extract_keypoints_from_video(video_path):
    """Extract keypoints from a single video"""
    mp_holistic = mp.solutions.holistic
    holistic = mp_holistic.Holistic(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    cap = cv2.VideoCapture(str(video_path))
    frames = []
    frame_id = 0
    
    while cap.isOpened() and frame_id < 100:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(frame_rgb)
        
        keypoints = []
        
        # Pose (33)
        if results.pose_landmarks:
            for lm in results.pose_landmarks.landmark:
                keypoints.append([lm.x, lm.y, lm.z])
        else:
            keypoints.extend([[0.0, 0.0, 0.0]] * 33)
        
        # Left hand (21)
        if results.left_hand_landmarks:
            for lm in results.left_hand_landmarks.landmark:
                keypoints.append([lm.x, lm.y, lm.z])
        else:
            keypoints.extend([[0.0, 0.0, 0.0]] * 21)
        
        # Right hand (21)
        if results.right_hand_landmarks:
            for lm in results.right_hand_landmarks.landmark:
                keypoints.append([lm.x, lm.y, lm.z])
        else:
            keypoints.extend([[0.0, 0.0, 0.0]] * 21)
        
        # Face (468)
        if results.face_landmarks:
            for lm in results.face_landmarks.landmark:
                keypoints.append([lm.x, lm.y, lm.z])
        else:
            keypoints.extend([[0.0, 0.0, 0.0]] * 468)
        
        frames.append({'frame_id': frame_id, 'keypoints': keypoints})
        frame_id += 1
    
    cap.release()
    holistic.close()
    return frames

# Process Greetings dataset
input_dir = Path(r"C:\Users\rudra\Desktop\SunoSaathi\datasets\Greetings")
output_dir = Path(r"C:\Users\rudra\Desktop\SunoSaathi\datasets\Greetings-processed")

train_dir = output_dir / 'train'
val_dir = output_dir / 'val'
train_dir.mkdir(parents=True, exist_ok=True)
val_dir.mkdir(parents=True, exist_ok=True)

# Get all sign folders
sign_folders = [d for d in input_dir.iterdir() if d.is_dir()]
vocabulary = []

print(f"Found {len(sign_folders)} sign folders")

for sign_folder in sign_folders:
    # Extract sign name (remove number prefix)
    sign_name = sign_folder.name.split('. ', 1)[-1].lower().replace(' ', '_')
    vocabulary.append(sign_name)
    
    print(f"\nProcessing: {sign_folder.name} -> {sign_name}")
    
    # Get all videos
    videos = list(sign_folder.glob('*.MOV')) + list(sign_folder.glob('*.mp4')) + list(sign_folder.glob('*.avi'))
    print(f"  Found {len(videos)} videos")
    
    # Process each video
    for idx, video_path in enumerate(tqdm(videos, desc=f"  {sign_name}")):
        try:
            frames = extract_keypoints_from_video(video_path)
            
            if len(frames) == 0:
                continue
            
            data = {
                'sign_label': sign_name,
                'frames': frames
            }
            
            # 80/20 split
            target_dir = train_dir if idx < len(videos) * 0.8 else val_dir
            output_file = target_dir / f"{sign_name}_{idx:03d}.json"
            
            with open(output_file, 'w') as f:
                json.dump(data, f)
        
        except Exception as e:
            print(f"    Error processing {video_path.name}: {e}")

# Save vocabulary
with open(output_dir / 'vocabulary.json', 'w') as f:
    json.dump(vocabulary, f, indent=2)

# Summary
train_count = len(list(train_dir.glob('*.json')))
val_count = len(list(val_dir.glob('*.json')))

print("\n" + "="*70)
print("Processing Complete!")
print("="*70)
print(f"Vocabulary: {vocabulary}")
print(f"Training samples: {train_count}")
print(f"Validation samples: {val_count}")
print(f"Total: {train_count + val_count}")
print("="*70)
