"""
Shared constants used across all microservices
"""

# API Endpoints
API_VERSION = "v1"

# Supported Languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi"
}

# ISL Recognition
ISL_KEYPOINT_DIMS = {
    "pose": 33,
    "left_hand": 21,
    "right_hand": 21,
    "face": 468  # MediaPipe face mesh
}

TOTAL_KEYPOINTS = sum(ISL_KEYPOINT_DIMS.values())  # 543 keypoints
KEYPOINT_FEATURES = 3  # x, y, z coordinates

# Model Configuration
MAX_SEQUENCE_LENGTH = 64  # Maximum frames for ISL recognition
BATCH_SIZE = 1  # For real-time inference

# Safety Thresholds
TOXICITY_THRESHOLD = 0.7
MIN_CONFIDENCE_SCORE = 0.6

# WebSocket
WS_HEARTBEAT_INTERVAL = 30  # seconds
WS_MESSAGE_MAX_SIZE = 10 * 1024 * 1024  # 10MB

# Session
SESSION_TIMEOUT = 3600  # 1 hour

# Sign Dictionary
SIGN_ANIMATION_FPS = 30
DEFAULT_ANIMATION_DURATION = 2.0  # seconds
