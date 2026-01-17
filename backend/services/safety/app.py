"""
Safety Filter Service using HuggingFace Toxicity Classifier
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import uvicorn
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from shared.utils import get_logger
from shared.constants import TOXICITY_THRESHOLD

logger = get_logger(__name__)

app = FastAPI(title="Safety Filter Service", version="1.0.0")

class SafetyRequest(BaseModel):
    text: str
    user_id: str = "anonymous"
    session_id: str = None

class SafetyResponse(BaseModel):
    is_safe: bool
    toxicity_score: float
    filtered_text: str
    categories: Dict[str, float]

class SafetyFilter:
    """
    Safety filter using toxicity detection
    """
    
    def __init__(self):
        logger.info("Initializing safety filter...")
        try:
            from detoxify import Detoxify
            self.model = Detoxify('original')
            logger.info("Loaded Detoxify model")
        except Exception as e:
            logger.warning(f"Could not load Detoxify: {e}. Using rule-based filter.")
            self.model = None
        
        # Rule-based bad words list (basic example)
        self.bad_words = set([
            # Add inappropriate words here
            # This is a placeholder - use a proper profanity filter
        ])
    
    def check_toxicity(self, text: str) -> Dict[str, float]:
        """Check text for toxicity"""
        if self.model:
            try:
                results = self.model.predict(text)
                return results
            except Exception as e:
                logger.error(f"Toxicity check error: {e}")
                return self._rule_based_check(text)
        else:
            return self._rule_based_check(text)
    
    def _rule_based_check(self, text: str) -> Dict[str, float]:
        """Simple rule-based toxicity check"""
        text_lower = text.lower()
        
        # Check for bad words
        has_bad_words = any(word in text_lower for word in self.bad_words)
        
        return {
            "toxicity": 0.8 if has_bad_words else 0.1,
            "severe_toxicity": 0.0,
            "obscene": 0.8 if has_bad_words else 0.0,
            "threat": 0.0,
            "insult": 0.0,
            "identity_attack": 0.0
        }
    
    def filter_text(self, text: str, scores: Dict[str, float]) -> str:
        """Filter text if toxic"""
        if scores["toxicity"] > TOXICITY_THRESHOLD:
            return "[Content filtered for safety]"
        return text

safety_filter = SafetyFilter()

@app.on_event("startup")
async def startup_event():
    logger.info("Safety Filter Service ready!")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "safety"}

@app.post("/check", response_model=SafetyResponse)
async def check_safety(request: SafetyRequest):
    """Check text for safety and filter if necessary"""
    try:
        # Check toxicity
        scores = safety_filter.check_toxicity(request.text)
        
        # Determine if safe
        is_safe = scores["toxicity"] <= TOXICITY_THRESHOLD
        
        # Filter if necessary
        filtered_text = safety_filter.filter_text(request.text, scores)
        
        return SafetyResponse(
            is_safe=is_safe,
            toxicity_score=scores["toxicity"],
            filtered_text=filtered_text,
            categories=scores
        )
    
    except Exception as e:
        logger.error(f"Safety check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Safety check failed: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("SAFETY_PORT", 8004))
    uvicorn.run(app, host="0.0.0.0", port=port)
