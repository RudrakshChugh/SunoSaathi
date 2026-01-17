"""
Generate Video Manifest for Frontend Processing
Creates a JSON list of all videos to be processed by the React app
"""
import os
import json
from pathlib import Path

DATASET_ROOT = r"C:\Users\rudra\Desktop\SunoSaathi\datasets\Greetings"
OUTPUT_FILE = r"C:\Users\rudra\Desktop\SunoSaathi\frontend\public\video_manifest.json"

def generate_manifest():
    videos = []
    
    root_path = Path(DATASET_ROOT)
    
    # Iterate through sign folders
    for sign_folder in root_path.iterdir():
        if not sign_folder.is_dir():
            continue
            
        # Parse sign name (e.g., "48. Hello" -> "hello")
        try:
            sign_name = sign_folder.name.split('. ', 1)[-1].lower().replace(' ', '_')
        except:
            sign_name = sign_folder.name.lower()
            
        print(f"Found sign: {sign_name}")
        
        # Get videos
        for video_file in sign_folder.glob('*'):
            if video_file.suffix.lower() in ['.mov', '.mp4', '.avi']:
                # Create web-accessible path
                # We will serve "C:\Users\rudra\Desktop\SunoSaathi\datasets" at "/datasets"
                # So "datasets/Greetings/48. Hello/MVI.MOV" becomes "/datasets/Greetings/48. Hello/MVI.MOV"
                
                relative_path = video_file.relative_to(r"C:\Users\rudra\Desktop\SunoSaathi\datasets")
                web_path = f"/datasets/{relative_path.as_posix()}"
                
                videos.append({
                    "url": web_path,
                    "sign_label": sign_name,
                    "filename": video_file.name
                })
    
    # Save manifest to frontend public dir so it can be fetched
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(videos, f, indent=2)
        
    print(f"Generated manifest with {len(videos)} videos")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_manifest()
