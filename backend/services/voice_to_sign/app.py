"""
Voice to Sign Language Translation Service
Uses Whisper for speech recognition + spaCy for keyword extraction
"""
from fastapi import FastAPI, UploadFile, File
import whisper
import spacy
import re
import tempfile
import os

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # for demo only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models
print("Voice-to-Sign Service v2.0 - Loaded 35+ words")
whisper_model = whisper.load_model("base")
nlp = spacy.load("en_core_web_sm")

# Sign language dictionary
SIGN_DICT = {
    "me": "me",
    "you": "you",
    "your": "you",
    "doctor": "doctor",
    "hospital": "hospital",
    "help": "help",
    "water": "water",
    "meet": "meet",
    "need": "need",
    "thank": "thankyou",
    "right": "right",
    "left": "left",
    "stop": "stop",
    "go": "go",
    "bus": "bus",
    "train": "train",
    "food": "food",
    "home": "home",
    "lawyer": "lawyer",
    "toilet": "toilet",
    "washroom": "toilet",
    "house": "home",
    # New additions
    "fever": "fever",
    "pain": "pain",
    "medicine": "medicine",
    "emergency": "emergency",
    "call": "call",
    "family": "family",
    "please": "please",
    "yes": "yes",
    "no": "no",
    "where": "where",
    "when": "when",
    "why": "why",
    "name": "name",
    "good": "good",
    "bad": "bad",
    "stomach": "stomach",
    "head": "head",
    "leg": "leg",
    "hand": "hand",
    "wait": "wait"
}

IMPORTANT_WORDS = set(SIGN_DICT.keys())

def clean_text(text):
    """Clean and normalize text"""
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()

@app.post("/translate")
async def translate(file: UploadFile = File(...)):
    """
    Translate audio to sign language sequence
    Expects audio file upload
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # Transcribe audio using Whisper
        result = whisper_model.transcribe(tmp_path, task="translate")
        raw_text = result["text"]
        clean = clean_text(raw_text)

        # Extract keywords
        keywords = []
        if "i" in clean or "me" in clean:
            keywords.append("me")

        doc = nlp(clean)
        for token in doc:
            lemma = token.lemma_
            if lemma in IMPORTANT_WORDS and lemma not in keywords:
                keywords.append(lemma)

        return {
            "raw_text": raw_text,
            "clean_text": clean,
            "keywords": keywords,
            "sequence": [SIGN_DICT[k] for k in keywords]
        }

    finally:
        os.remove(tmp_path)

@app.post("/translate-text")
async def translate_text(data: dict):
    """
    Translate text to sign language sequence (for testing without audio)
    Expects: {"text": "your text here"}
    """
    text = data.get("text", "")
    if not text:
        return {"error": "No text provided"}
    
    raw_text = text
    clean = clean_text(raw_text)

    # Extract keywords
    keywords = []
    if "i" in clean or "me" in clean:
        keywords.append("me")

    doc = nlp(clean)
    for token in doc:
        lemma = token.lemma_
        if lemma in IMPORTANT_WORDS and lemma not in keywords:
            keywords.append(lemma)

    return {
        "raw_text": raw_text,
        "clean_text": clean,
        "keywords": keywords,
        "sequence": [SIGN_DICT[k] for k in keywords]
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "voice-to-sign",
        "whisper_model": "base",
        "spacy_model": "en_core_web_sm"
    }

# WebSocket for real-time streaming
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import base64

@app.websocket("/ws/stream-audio")
async def websocket_stream_audio(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio streaming
    Client sends: {"audio": base64_audio_chunk}
    Server responds: {"type": "interim"|"final", "text": "...", "keywords": [...]}
    """
    await websocket.accept()
    
    audio_buffer = []
    
    try:
        while True:
            # Receive audio chunk from client
            data = await websocket.receive_json()
            
            if data.get("action") == "stop":
                # Process accumulated audio
                if audio_buffer:
                    # Combine all chunks
                    full_audio = b''.join(audio_buffer)
                    
                    # Save to temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                        tmp.write(full_audio)
                        tmp_path = tmp.name
                    
                    try:
                        # Transcribe
                        result = whisper_model.transcribe(tmp_path, task="translate")
                        raw_text = result["text"]
                        clean = clean_text(raw_text)
                        
                        # Extract keywords
                        keywords = []
                        if "i" in clean or "me" in clean:
                            keywords.append("me")
                        
                        doc = nlp(clean)
                        for token in doc:
                            lemma = token.lemma_
                            if lemma in IMPORTANT_WORDS and lemma not in keywords:
                                keywords.append(lemma)
                        
                        # Send final result
                        await websocket.send_json({
                            "type": "final",
                            "raw_text": raw_text,
                            "clean_text": clean,
                            "keywords": keywords,
                            "sequence": [SIGN_DICT[k] for k in keywords]
                        })
                    finally:
                        os.remove(tmp_path)
                        audio_buffer = []
                
                continue
            
            # Accumulate audio chunks
            if "audio" in data:
                audio_chunk = base64.b64decode(data["audio"])
                audio_buffer.append(audio_chunk)
                
                # Send acknowledgment
                await websocket.send_json({
                    "type": "ack",
                    "chunks_received": len(audio_buffer)
                })
    
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("VOICE_TO_SIGN_PORT", 8005))
    uvicorn.run(app, host="0.0.0.0", port=port)
