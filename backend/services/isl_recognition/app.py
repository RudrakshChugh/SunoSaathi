"""
ISL Recognition Service API
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import numpy as np
import uvicorn
import os
import sys

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from model import get_recognizer
from shared.utils import get_logger

logger = get_logger(__name__)

app = FastAPI(title="ISL Recognition Service", version="1.0.0")

# Request/Response models
class KeypointFrame(BaseModel):
    """Single frame of keypoints"""
    frame_id: int
    keypoints: List[List[float]]  # Shape: (num_keypoints, 3)

class RecognitionRequest(BaseModel):
    """Request for ISL recognition"""
    frames: List[KeypointFrame]
    user_id: str = "anonymous"

class Prediction(BaseModel):
    """Single prediction"""
    sign: str
    confidence: float

class RecognitionResponse(BaseModel):
    """Response from ISL recognition"""
    predictions: List[Prediction]
    text: str
    num_frames: int

@app.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    logger.info("Initializing ISL Recognition Service...")
    get_recognizer()  # Load model
    logger.info("ISL Recognition Service ready!")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "isl_recognition"}

@app.post("/recognize", response_model=RecognitionResponse)
async def recognize_sign(request: RecognitionRequest):
    """
    Recognize ISL sign from keypoint sequence
    """
    try:
        # Convert frames to numpy array
        keypoints_list = []
        for frame in sorted(request.frames, key=lambda x: x.frame_id):
            keypoints_list.append(frame.keypoints)
        
        keypoints = np.array(keypoints_list, dtype=np.float32)
        
        # Validate shape
        if keypoints.shape[0] == 0:
            raise HTTPException(status_code=400, detail="No frames provided")
        
        # Get recognizer
        recognizer = get_recognizer()
        
        # Recognize
        predictions = recognizer.recognize(keypoints, top_k=3)
        
        # Get text (top prediction if confidence > 0.5)
        text = predictions[0]["sign"] if predictions and predictions[0]["confidence"] > 0.5 else ""
        
        return RecognitionResponse(
            predictions=[Prediction(**p) for p in predictions],
            text=text,
            num_frames=len(request.frames)
        )
    
    except Exception as e:
        logger.error(f"Recognition error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Recognition failed: {str(e)}")

@app.post("/recognize_sequence")
async def recognize_sequence(request: RecognitionRequest):
    """
    Recognize a sequence of signs (for continuous recognition)
    """
    try:
        # This would be used for continuous sign recognition
        # For now, just call the single recognition
        return await recognize_sign(request)
    
    except Exception as e:
        logger.error(f"Sequence recognition error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sequence recognition failed: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("ISL_RECOGNITION_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
