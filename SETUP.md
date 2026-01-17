# SunoSaathi Development Setup Guide

## Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+

### Step 1: Setup Environment

```bash
# Copy environment file
copy .env.example .env

# Edit .env and update database credentials if needed
```

### Step 2: Setup Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python database/connection.py
```

### Step 3: Setup Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install
```

### Step 4: Run Services

You'll need multiple terminal windows:

**Terminal 1 - API Gateway:**
```bash
cd backend/api_gateway
python main.py
```

**Terminal 2 - ISL Recognition Service:**
```bash
cd backend/services/isl_recognition
python app.py
```

**Terminal 3 - Translation Service:**
```bash
cd backend/services/translation
python app.py
```

**Terminal 4 - TTS Service:**
```bash
cd backend/services/tts
python app.py
```

**Terminal 5 - Safety Filter Service:**
```bash
cd backend/services/safety
python app.py
```

**Terminal 6 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 5: Access Application

Open your browser and navigate to:
- Frontend: http://localhost:5173
- API Gateway: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Docker Deployment (Recommended for Production)

```bash
# Build and start all services
docker-compose up --build

# Stop all services
docker-compose down
```

## Project Structure

```
SunoSaathi/
├── backend/
│   ├── api_gateway/          # Main API gateway
│   ├── services/             # Microservices
│   │   ├── isl_recognition/  # ISL recognition
│   │   ├── translation/      # Translation
│   │   ├── tts/              # Text-to-speech
│   │   └── safety/           # Safety filter
│   ├── database/             # Database models
│   └── shared/               # Shared utilities
├── frontend/
│   └── src/
│       ├── components/       # React components
│       └── services/         # API services
└── data/                     # Sign dictionary
```

## Development Notes

### ISL Recognition Model
- Currently uses a lightweight LSTM model
- Optimized for CPU inference on laptops
- For production, train on actual ISL dataset
- Model path: `backend/services/isl_recognition/model.py`

### Translation Service
- Currently uses placeholder translations
- TODO: Integrate IndicTrans2 for production
- File: `backend/services/translation/app.py`

### TTS Service
- Currently returns placeholder audio
- TODO: Integrate proper TTS engine (pyttsx3, gTTS, or Coqui TTS)
- File: `backend/services/tts/app.py`

### Safety Filter
- Uses HuggingFace Detoxify model
- Falls back to rule-based filtering
- File: `backend/services/safety/app.py`

## Next Steps

1. **Train ISL Recognition Model**: Collect ISL dataset and train the model
2. **Integrate IndicTrans2**: Replace placeholder translator
3. **Add TTS Engine**: Integrate proper text-to-speech
4. **Build Hearing User Pipeline**: Add speech recognition and 3D avatar
5. **Create Sign Dictionary**: Build JSON-based sign animations
6. **Testing**: Add comprehensive tests

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Run `python backend/database/connection.py` to initialize

### MediaPipe Issues
- Ensure camera permissions are granted
- Check browser console for errors
- MediaPipe requires HTTPS in production

### Service Not Starting
- Check if port is already in use
- Verify all dependencies are installed
- Check logs for specific errors

## Support

For issues or questions, please refer to the documentation or create an issue.
