# Voice to Sign Language Service

This service translates spoken language to sign language using:
- **Whisper**: OpenAI's speech recognition model
- **spaCy**: For keyword extraction and lemmatization

## Setup

```bash
cd backend/services/voice_to_sign
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Running

```bash
python app.py
```

Server runs on `http://localhost:8000`

## API Endpoints

### POST /translate
Upload audio file for translation to sign language sequence

**Request:**
- Audio file (WAV, MP3, etc.)

**Response:**
```json
{
  "raw_text": "I need to see a doctor",
  "clean_text": "i need to see a doctor",
  "keywords": ["me", "need", "doctor"],
  "sequence": ["me", "need", "doctor"]
}
```

### GET /health
Health check endpoint

## Sign Dictionary

Currently supports ~25 common signs including:
- Personal: me, you
- Places: hospital, home, toilet
- Actions: help, meet, stop, go
- Transport: bus, train
- Basic needs: food, water

Add more signs in `SIGN_DICT` in `app.py`.
