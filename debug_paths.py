import os
import sys

# Simulate the logic in main.py
current_file = os.path.join(os.getcwd(), "backend", "api_gateway", "main.py")
datasets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_file))), "datasets", "Greetings")

print(f"Simulated datasets path: {datasets_path}")
print(f"Exists: {os.path.exists(datasets_path)}")

videos = []
if os.path.exists(datasets_path):
    for root, dirs, files in os.walk(datasets_path):
        for file in files:
            if file.lower().endswith(('.mov', '.mp4', '.avi')):
                videos.append(file)
                
print(f"Found {len(videos)} videos")
if len(videos) > 0:
    print(f"Sample: {videos[0]}")
