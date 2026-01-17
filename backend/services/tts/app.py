"""
Text-to-Speech Service
Using lightweight TTS for laptop deployment
"""
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import uvicorn
import os
import sys
import io

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from shared.utils import get_logger

logger = get_logger(__name__)

app = FastAPI(title="TTS Service", version="1.0.0")

class TTSRequest(BaseModel):
    text: str
    language: str = "en"
    voice: str = "default"

class TTSEngine:
    """
    Text-to-Speech Engine using pyttsx3 (offline) with gTTS fallback
    """
    
    def __init__(self):
        logger.info("Initializing TTS engine...")
        
        # Try to initialize pyttsx3 (offline TTS)
        self.pyttsx3_engine = None
        try:
            import pyttsx3
            self.pyttsx3_engine = pyttsx3.init()
            self.pyttsx3_engine.setProperty('rate', 150)
            self.pyttsx3_engine.setProperty('volume', 0.9)
            logger.info("pyttsx3 TTS engine initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize pyttsx3: {e}")
        
        # gTTS as fallback (requires internet)
        self.use_gtts = False
        try:
            from gtts import gTTS
            self.gtts = gTTS
            logger.info("gTTS available as fallback")
        except Exception as e:
            logger.warning(f"gTTS not available: {e}")
            self.gtts = None
    
    def synthesize(self, text: str, language: str = "en") -> bytes:
        """
        Synthesize speech from text
        Returns audio bytes (WAV format)
        """
        logger.info(f"TTS request: '{text}' in {language}")
        
        # Try pyttsx3 first (offline, fast)
        if self.pyttsx3_engine and language == "en":
            try:
                import tempfile
                import os
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    temp_path = tmp_file.name
                
                # Save to file
                self.pyttsx3_engine.save_to_file(text, temp_path)
                self.pyttsx3_engine.runAndWait()
                
                # Read the file
                with open(temp_path, 'rb') as f:
                    audio_bytes = f.read()
                
                # Clean up
                os.unlink(temp_path)
                
                logger.info(f"Generated TTS audio using pyttsx3: {len(audio_bytes)} bytes")
                return audio_bytes
                
            except Exception as e:
                logger.warning(f"pyttsx3 synthesis failed: {e}")
        
        # Try gTTS (online, better quality, supports more languages)
        if self.gtts:
            try:
                import io
                
                # Map language codes for gTTS
                lang_map = {
                    'en': 'en', 'hi': 'hi', 'bn': 'bn', 'ta': 'ta',
                    'te': 'te', 'mr': 'mr', 'gu': 'gu', 'kn': 'kn',
                    'ml': 'ml', 'pa': 'pa'
                }
                
                tts_lang = lang_map.get(language, 'en')
                tts = self.gtts(text=text, lang=tts_lang, slow=False)
                
                # Save to BytesIO
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                
                audio_bytes = audio_buffer.read()
                logger.info(f"Generated TTS audio using gTTS: {len(audio_bytes)} bytes")
                return audio_bytes
                
            except Exception as e:
                logger.warning(f"gTTS synthesis failed: {e}")
        
        # Final fallback: return empty WAV file
        logger.warning("All TTS engines failed. Returning empty audio.")
        return self._create_empty_wav()
    
    def _create_empty_wav(self) -> bytes:
        """Create a minimal WAV file with silence"""
        import struct
        
        sample_rate = 16000
        duration = 1  # 1 second
        num_samples = sample_rate * duration
        num_channels = 1
        bits_per_sample = 16
        byte_rate = sample_rate * num_channels * bits_per_sample // 8
        block_align = num_channels * bits_per_sample // 8
        data_size = num_samples * num_channels * bits_per_sample // 8
        
        header = struct.pack('<4sI4s', b'RIFF', 36 + data_size, b'WAVE')
        header += struct.pack('<4sIHHIIHH', b'fmt ', 16, 1, num_channels, 
                             sample_rate, byte_rate, block_align, bits_per_sample)
        header += struct.pack('<4sI', b'data', data_size)
        
        audio_data = b'\x00' * (num_samples * 2)  # 16-bit silence
        
        return header + audio_data

tts_engine = TTSEngine()

@app.on_event("startup")
async def startup_event():
    logger.info("TTS Service ready!")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "tts"}

@app.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    """Synthesize speech from text"""
    try:
        audio_bytes = tts_engine.synthesize(request.text, request.language)
        
        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=speech.wav"
            }
        )
    
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("TTS_PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port)
