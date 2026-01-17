import requests
import json

url = "http://localhost:8000/save_training_sample"
data = {
    "sign_label": "test_sign",
    "frames": [{"frame_id": 0, "keypoints": []}],
    "source_video": "test_video.mp4"
}

try:
    print(f"Sending to {url}...")
    resp = requests.post(url, json=data)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
