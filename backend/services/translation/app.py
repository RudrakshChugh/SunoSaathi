"""
Translation Service using IndicTrans2
Note: For laptop deployment, we'll use a lighter translation approach initially
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from shared.utils import get_logger
from shared.constants import SUPPORTED_LANGUAGES

logger = get_logger(__name__)

app = FastAPI(title="Translation Service", version="1.0.0")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "en"
    target_lang: str = "hi"

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str

# Translation engine with caching
class GoogleTranslator:
    """
    Google Translate-based translator with caching
    Provides quick translation for common phrases
    """
    
    def __init__(self):
        logger.info("Initializing Google Translator...")
        try:
            from googletrans import Translator
            self.translator = Translator()
            logger.info("Google Translator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Translator: {e}")
            self.translator = None
        
        # Cache for common translations
        self.cache = {}
        
        # Hardcoded fallbacks for common ISL phrases
        self.fallback_translations = {
            "hello": {"hi": "नमस्ते", "ta": "வணக்கம்", "bn": "হ্যালো", "te": "హలో", "mr": "नमस्कार"},
            "thank you": {"hi": "धन्यवाद", "ta": "நன்றி", "bn": "ধন্যবাদ", "te": "ధన్యవాదాలు", "mr": "धन्यवाद"},
            "please": {"hi": "कृपया", "ta": "தயவுசெய்து", "bn": "দয়া করে", "te": "దయచేసి", "mr": "कृपया"},
            "yes": {"hi": "हाँ", "ta": "ஆம்", "bn": "হ্যাঁ", "te": "అవును", "mr": "होय"},
            "no": {"hi": "नहीं", "ta": "இல்லை", "bn": "না", "te": "కాదు", "mr": "नाही"},
            "help": {"hi": "मदद", "ta": "உதவி", "bn": "সাহায্য", "te": "సహాయం", "mr": "मदत"},
            "sorry": {"hi": "माफ़ करना", "ta": "மன்னிக்கவும்", "bn": "দুঃখিত", "te": "క్షమించండి", "mr": "माफ करा"},
            "good morning": {"hi": "सुप्रभात", "ta": "காலை வணக்கம்", "bn": "সুপ্রভাত", "te": "శుభోదయం", "mr": "सुप्रभात"},
            "good afternoon": {"hi": "शुभ दोपहर", "ta": "மதிய வணக்கம்", "bn": "শুভ অপরাহ্ন", "te": "శుభ మధ్యాహ్నం", "mr": "शुभ दुपार"},
            "how are you": {"hi": "आप कैसे हैं", "ta": "எப்படி இருக்கிறீர்கள்", "bn": "আপনি কেমন আছেন", "te": "మీరు ఎలా ఉన్నారు", "mr": "तुम्ही कसे आहात"},
        }
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text with caching and fallback"""
        # If source and target are same, return original
        if source_lang == target_lang:
            return text
        
        # Check cache first
        cache_key = f"{text}:{source_lang}:{target_lang}"
        if cache_key in self.cache:
            logger.debug(f"Cache hit for: {text}")
            return self.cache[cache_key]
        
        # Check hardcoded fallbacks
        text_lower = text.lower().strip()
        if text_lower in self.fallback_translations:
            if target_lang in self.fallback_translations[text_lower]:
                result = self.fallback_translations[text_lower][target_lang]
                self.cache[cache_key] = result
                logger.info(f"Fallback translation: '{text}' -> '{result}'")
                return result
        
        # Try Google Translate
        if self.translator:
            try:
                # Map language codes (googletrans uses different codes)
                lang_map = {
                    'en': 'en', 'hi': 'hi', 'bn': 'bn', 'ta': 'ta',
                    'te': 'te', 'mr': 'mr', 'gu': 'gu', 'kn': 'kn',
                    'ml': 'ml', 'pa': 'pa'
                }
                
                src = lang_map.get(source_lang, source_lang)
                tgt = lang_map.get(target_lang, target_lang)
                
                result = self.translator.translate(text, src=src, dest=tgt)
                translated = result.text
                
                # Cache the result
                self.cache[cache_key] = translated
                logger.info(f"Translated: '{text}' -> '{translated}' ({source_lang} -> {target_lang})")
                return translated
                
            except Exception as e:
                logger.warning(f"Translation failed: {e}")
        
        # Final fallback: return original text
        logger.warning(f"No translation available for '{text}'. Returning original.")
        return text

translator = GoogleTranslator()

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Translation Service ready!")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "translation"}

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Translate text between languages"""
    try:
        # Validate languages
        if request.source_lang not in SUPPORTED_LANGUAGES:
            raise HTTPException(status_code=400, detail=f"Unsupported source language: {request.source_lang}")
        
        if request.target_lang not in SUPPORTED_LANGUAGES:
            raise HTTPException(status_code=400, detail=f"Unsupported target language: {request.target_lang}")
        
        # Translate
        translated = translator.translate(request.text, request.source_lang, request.target_lang)
        
        return TranslationResponse(
            original_text=request.text,
            translated_text=translated,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {"languages": SUPPORTED_LANGUAGES}

if __name__ == "__main__":
    port = int(os.getenv("TRANSLATION_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
