"""
Quick test script to extract keypoints from one video
"""
import cv2
import json
import mediapipe as mp
from pathlib import Path

# Test video
video_path = r"C:\Users\rudra\Desktop\SunoSaathi\datasets\Greetings\48. Hello\MVI_0029.MOV"

print(f"Testing extraction on: {video_path}")
print(f"File exists: {Path(video_path).exists()}")

# Initialize MediaPipe
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Open video
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("ERROR: Could not open video!")
    exit(1)

print(f"Video opened successfully")
print(f"FPS: {cap.get(cv2.CAP_PROP_FPS)}")
print(f"Frame count: {cap.get(cv2.CAP_PROP_FRAME_COUNT)}")

frames_data = []
frame_id = 0
max_frames = 10  # Just test first 10 frames

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
    
    # Pose (33)
    if results.pose_landmarks:
        for landmark in results.pose_landmarks.landmark:
            keypoints.append([landmark.x, landmark.y, landmark.z])
    else:
        for _ in range(33):
            keypoints.append([0.0, 0.0, 0.0])
    
    # Left hand (21)
    if results.left_hand_landmarks:
        for landmark in results.left_hand_landmarks.landmark:
            keypoints.append([landmark.x, landmark.y, landmark.z])
    else:
        for _ in range(21):
            keypoints.append([0.0, 0.0, 0.0])
    
    # Right hand (21)
    if results.right_hand_landmarks:
        for landmark in results.right_hand_landmarks.landmark:
            keypoints.append([landmark.x, landmark.y, landmark.z])
    else:
        for _ in range(21):
            keypoints.append([0.0, 0.0, 0.0])
    
    # Face (468)
    if results.face_landmarks:
        for landmark in results.face_landmarks.landmark:
            keypoints.append([landmark.x, landmark.y, landmark.z])
    else:
        for _ in range(468):
            keypoints.append([0.0, 0.0, 0.0])
    
    frames_data.append({
        'frame_id': frame_id,
        'keypoints': keypoints
    })
    
    print(f"Frame {frame_id}: {len(keypoints)} keypoints extracted")
    frame_id += 1

cap.release()
holistic.close()

print(f"\nTotal frames processed: {len(frames_data)}")
print(f"Keypoints per frame: {len(frames_data[0]['keypoints']) if frames_data else 0}")

# Save test output
output_file = r"C:\Users\rudra\Desktop\SunoSaathi\datasets\test_output.json"
data = {
    'sign_label': 'hello',
    'frames': frames_data,
    'source_video': 'MVI_0029.MOV'
}

with open(output_file, 'w') as f:
    json.dump(data, f)

print(f"\nSaved to: {output_file}")
print("SUCCESS!")
