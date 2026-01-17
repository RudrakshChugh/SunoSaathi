"""
Main API Gateway for SunoSaathi
Orchestrates all microservices and handles WebSocket connections
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, List, Optional
import httpx
import json
import os
from dotenv import load_dotenv
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from shared.utils import get_logger
from database.connection import get_db, init_db
from database.models import User, Session, ConsentLog

load_dotenv()

logger = get_logger(__name__)

app = FastAPI(
    title="SunoSaathi API Gateway",
    description="Real-time communication platform for hearing and deaf users",
    version="1.0.0"
)

# Mount datasets for frontend processing
app.mount("/datasets", StaticFiles(directory=r"C:\Users\rudra\Desktop\SunoSaathi\datasets"), name="datasets")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SERVICES = {
    "isl_recognition": f"http://localhost:{os.getenv('ISL_RECOGNITION_PORT', 8001)}",
    "translation": f"http://localhost:{os.getenv('TRANSLATION_PORT', 8002)}",
    "tts": f"http://localhost:{os.getenv('TTS_PORT', 8003)}",
    "safety": f"http://localhost:{os.getenv('SAFETY_PORT', 8004)}",
}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()

# Request/Response models
class UserPreferences(BaseModel):
    user_id: str
    preferred_language: str = "en"
    is_deaf: bool = False

class ConsentRequest(BaseModel):
    user_id: str
    consent_type: str  # "camera" or "microphone"
    granted: bool

class DeafUserMessage(BaseModel):
    """Message from deaf user (ISL keypoints)"""
    user_id: str
    session_id: str
    frames: List[dict]
    target_language: str = "en"

class HearingUserMessage(BaseModel):
    """Message from hearing user (audio/text)"""
    user_id: str
    session_id: str
    text: str
    source_language: str = "en"
    target_language: str = "en"

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and services"""
    logger.info("Starting SunoSaathi API Gateway...")
    init_db()
    logger.info("Database initialized!")
    
    # Check service health
    async with httpx.AsyncClient() as client:
        for service_name, service_url in SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                if response.status_code == 200:
                    logger.info(f"✓ {service_name} service is healthy")
                else:
                    logger.warning(f"✗ {service_name} service returned status {response.status_code}")
            except Exception as e:
                logger.warning(f"✗ {service_name} service is not available: {e}")
    
    logger.info("SunoSaathi API Gateway ready!")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api_gateway"}

# User management
@app.post("/users/preferences")
async def set_user_preferences(prefs: UserPreferences, db = Depends(get_db)):
    """Set user preferences"""
    user = db.query(User).filter(User.user_id == prefs.user_id).first()
    
    if not user:
        user = User(
            user_id=prefs.user_id,
            preferred_language=prefs.preferred_language,
            is_deaf=prefs.is_deaf
        )
        db.add(user)
    else:
        user.preferred_language = prefs.preferred_language
        user.is_deaf = prefs.is_deaf
    
    db.commit()
    return {"status": "success", "user_id": prefs.user_id}

@app.post("/users/consent")
async def log_consent(consent: ConsentRequest, db = Depends(get_db)):
    """Log user consent"""
    consent_log = ConsentLog(
        user_id=consent.user_id,
        consent_type=consent.consent_type,
        granted=consent.granted
    )
    db.add(consent_log)
    db.commit()
    
    return {"status": "success", "consent_logged": True}

    return {"status": "success", "consent_logged": True}

class TrainingSample(BaseModel):
    sign_label: str
    frames: List[dict]
    source_video: str

@app.post("/save_training_sample")
async def save_training_sample(sample: TrainingSample):
    """Save processed training sample from frontend"""
    # Use 80/20 split based on hash of filename
    video_hash = hash(sample.source_video) % 10
    is_train = video_hash < 8
    
    base_dir = r"C:\Users\rudra\Desktop\SunoSaathi\datasets\Greetings-processed"
    output_dir = Path(base_dir) / ("train" if is_train else "val")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    name = sample.source_video.replace('.MOV', '').replace('.mp4', '').replace('.avi', '')
    filename = f"{sample.sign_label}_{name}.json"
    file_path = output_dir / filename
    
    with open(file_path, 'w') as f:
        json.dump(sample.dict(), f)
    
    logger.info(f"Saved sample: {file_path}")
    return {"status": "success", "file": str(file_path)}
@app.post("/deaf-user/process")
async def process_deaf_user_message(message: DeafUserMessage):
    """
    Process message from deaf user:
    1. ISL Recognition (keypoints → text)
    2. Translation (ISL text → target language)
    3. TTS (text → speech)
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: ISL Recognition
            isl_response = await client.post(
                f"{SERVICES['isl_recognition']}/recognize",
                json={
                    "frames": message.frames,
                    "user_id": message.user_id
                }
            )
            isl_data = isl_response.json()
            recognized_text = isl_data.get("text", "")
            
            if not recognized_text:
                return {
                    "status": "error",
                    "message": "Could not recognize sign",
                    "predictions": isl_data.get("predictions", [])
                }
            
            # Step 2: Translation
            translation_response = await client.post(
                f"{SERVICES['translation']}/translate",
                json={
                    "text": recognized_text,
                    "source_lang": "en",  # ISL is typically glossed in English
                    "target_lang": message.target_language
                }
            )
            translation_data = translation_response.json()
            translated_text = translation_data.get("translated_text", recognized_text)
            
            # Step 3: TTS (optional - can be done on frontend)
            # For now, just return the text
            
            return {
                "status": "success",
                "recognized_text": recognized_text,
                "translated_text": translated_text,
                "predictions": isl_data.get("predictions", []),
                "num_frames": isl_data.get("num_frames", 0)
            }
    
    except Exception as e:
        logger.error(f"Error processing deaf user message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Hearing User Pipeline
@app.post("/hearing-user/process")
async def process_hearing_user_message(message: HearingUserMessage):
    """
    Process message from hearing user:
    1. Safety Filter
    2. Translation
    3. Sign Mapping (for avatar display)
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Safety Filter
            safety_response = await client.post(
                f"{SERVICES['safety']}/check",
                json={
                    "text": message.text,
                    "user_id": message.user_id,
                    "session_id": message.session_id
                }
            )
            safety_data = safety_response.json()
            
            if not safety_data.get("is_safe", True):
                return {
                    "status": "filtered",
                    "original_text": message.text,
                    "translated_text": "[Content filtered for safety]",
                    "is_safe": False,
                    "signs": [],
                    "toxicity_score": safety_data.get("toxicity_score", 0)
                }
            
            # Step 2: Translation
            translation_response = await client.post(
                f"{SERVICES['translation']}/translate",
                json={
                    "text": message.text,
                    "source_lang": message.source_language,
                    "target_lang": message.target_language
                }
            )
            translation_data = translation_response.json()
            translated_text = translation_data.get("translated_text", message.text)
            
            # Step 3: Map to available signs (for demo)
            # This is a simple word matching - in production, use proper ISL generation
            available_signs = [
                "hello", "thank you", "please", "yes", "no",
                "good morning", "good afternoon", "how are you",
                "alright", "how_are_you", "good_morning", "good_afternoon"
            ]
            
            # Tokenize and match
            text_lower = message.text.lower()
            signs = []
            
            # Check for multi-word phrases first
            multi_word_signs = ["good morning", "good afternoon", "how are you", "thank you"]
            for phrase in multi_word_signs:
                if phrase in text_lower:
                    signs.append(phrase.replace(" ", "_"))
            
            # Then check individual words
            words = text_lower.split()
            for word in words:
                if word in available_signs and word not in [s.replace("_", " ") for s in signs]:
                    signs.append(word)
            
            # Default to hello if no signs found
            if not signs:
                signs = ["hello"]
            
            # Limit to 3 signs for demo
            signs = signs[:3]
            
            return {
                "status": "success",
                "original_text": message.text,
                "translated_text": translated_text,
                "is_safe": True,
                "signs": signs,
                "num_signs": len(signs)
            }
    
    except Exception as e:
        logger.error(f"Error processing hearing user message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time communication
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            # Route based on message type
            if message_type == "deaf_user_message":
                # Process deaf user message
                result = await process_deaf_user_message(
                    DeafUserMessage(**data.get("payload"))
                )
                await manager.send_personal_message(
                    {"type": "deaf_user_response", "payload": result},
                    user_id
                )
            
            elif message_type == "hearing_user_message":
                # Process hearing user message
                result = await process_hearing_user_message(
                    HearingUserMessage(**data.get("payload"))
                )
                await manager.send_personal_message(
                    {"type": "hearing_user_response", "payload": result},
                    user_id
                )
            
            elif message_type == "ping":
                # Heartbeat
                await manager.send_personal_message(
                    {"type": "pong"},
                    user_id
                )
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        logger.info(f"User {user_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)


# ==========================================
# DATASET PROCESSING ENDPOINTS (Hackathon Fix)
# ==========================================
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import json

# Mount datasets directory
try:
    datasets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "datasets")
    if os.path.exists(datasets_path):
        app.mount("/datasets", StaticFiles(directory=datasets_path), name="datasets")
        logger.info(f"Mounted datasets from {datasets_path}")
except Exception as e:
    logger.error(f"Could not mount datasets: {e}")

@app.get("/api/list-videos")
async def list_videos():
    """List all videos in Greetings dataset for processing"""
    try:
        datasets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "datasets", "Greetings")
        videos = []
        if os.path.exists(datasets_path):
            for root, dirs, files in os.walk(datasets_path):
                for file in files:
                    if file.lower().endswith(('.mov', '.mp4', '.avi')):
                        # Create relative path for URL
                        abs_path = os.path.join(root, file)
                        rel_path = os.path.relpath(abs_path, datasets_path)
                        # Use forward slashes for URL
                        url_path = rel_path.replace("\\", "/")
                        
                        # Extract sign label from parent folder name (e.g., "48. Hello" -> "hello")
                        parent_folder = os.path.basename(root)
                        # Simple extraction: take part after ". " or just the whole thing if no dot
                        if ". " in parent_folder:
                             sign_label = parent_folder.split('. ', 1)[1].lower().replace(' ', '_')
                        else:
                             sign_label = parent_folder.lower().replace(' ', '_')
                        
                        videos.append({
                            "url": f"/datasets/Greetings/{url_path}",
                            "filename": file,
                            "sign_label": sign_label
                        })
        return {"videos": videos, "count": len(videos)}
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        return {"error": str(e)}

class KeypointData(BaseModel):
    filename: str
    sign_label: str
    frames: list
    source_video: str

@app.post("/api/save-processed-data")
async def save_processed_data(data: KeypointData):
    """Save processed keypoints from frontend"""
    try:
        # Define output directory
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "datasets", "Greetings-browser-processed")
        
        # Simple train/val split logic (hash based or random)
        is_val = hash(data.filename) % 5 == 0  # 20% val
        
        target_dir = os.path.join(base_dir, "val" if is_val else "train")
        os.makedirs(target_dir, exist_ok=True)
        
        # Save JSON file
        output_filename = f"{data.sign_label}_{data.filename.split('.')[0]}.json"
        output_path = os.path.join(target_dir, output_filename)
        
        with open(output_path, "w") as f:
            json.dump(data.dict(), f)
            
        # Also ensure vocabulary exists
        vocab_path = os.path.join(base_dir, "vocabulary.json")
        vocab = ["hello", "how_are_you", "alright", "good_morning", "good_afternoon"]
        if not os.path.exists(vocab_path):
             with open(vocab_path, "w") as f:
                 json.dump(vocab, f)

        return {"status": "success", "path": output_path}
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_GATEWAY_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
