"""
Debug version - process just one video to see what's happening
"""
import cv2
import json
import mediapipe as mp
from pathlib import Path

video_path = r"C:\Users\rudra\Desktop\SunoSaathi\datasets\Greetings\48. Hello\MVI_0029.MOV"
output_file = r"C:\Users\rudra\Desktop\SunoSaathi\datasets\test_output.json"

print(f"Processing: {video_path}")

mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(video_path)
print(f"Video opened: {cap.isOpened()}")

frames = []
frame_id = 0

while cap.isOpened() and frame_id < 10:  # Just 10 frames for testing
    ret, frame = cap.read()
    if not ret:
        print(f"Can't read frame {frame_id}")
        break
    
    print(f"Processing frame {frame_id}...")
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = holistic.process(frame_rgb)
    
    keypoints = []
    
    # Pose
    if results.pose_landmarks:
        for lm in results.pose_landmarks.landmark:
            keypoints.append([float(lm.x), float(lm.y), float(lm.z)])
        print(f"  Pose: {len(keypoints)} keypoints")
    else:
        keypoints.extend([[0.0, 0.0, 0.0]] * 33)
        print(f"  Pose: None detected")
    
    # Hands
    if results.left_hand_landmarks:
        for lm in results.left_hand_landmarks.landmark:
            keypoints.append([float(lm.x), float(lm.y), float(lm.z)])
        print(f"  Left hand detected")
    else:
        keypoints.extend([[0.0, 0.0, 0.0]] * 21)
    
    if results.right_hand_landmarks:
        for lm in results.right_hand_landmarks.landmark:
            keypoints.append([float(lm.x), float(lm.y), float(lm.z)])
        print(f"  Right hand detected")
    else:
        keypoints.extend([[0.0, 0.0, 0.0]] * 21)
    
    # Face
    if results.face_landmarks:
        for lm in results.face_landmarks.landmark:
            keypoints.append([float(lm.x), float(lm.y), float(lm.z)])
    else:
        keypoints.extend([[0.0, 0.0, 0.0]] * 468)
    
    print(f"  Total keypoints: {len(keypoints)}")
    frames.append({'frame_id': frame_id, 'keypoints': keypoints})
    frame_id += 1

cap.release()
holistic.close()

print(f"\nProcessed {len(frames)} frames")

# Save
data = {
    'sign_label': 'hello',
    'frames': frames
}

with open(output_file, 'w') as f:
    json.dump(data, f)

print(f"Saved to: {output_file}")
print(f"File size: {Path(output_file).stat().st_size} bytes")
