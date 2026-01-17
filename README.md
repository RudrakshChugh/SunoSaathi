# SunoSaathi 🤝

**Real-time communication platform enabling seamless interaction between hearing and deaf users across different languages.**

## Overview

SunoSaathi bridges the communication gap between hearing and deaf communities using AI-powered translation, sign language recognition, and 3D avatar-based sign language generation.

## Features

- 🎥 **Real-time ISL Recognition**: MediaPipe-based keypoint extraction with Transformer models
- 🗣️ **Multilingual Speech Recognition**: Whisper-powered ASR supporting Indian languages
- 🌐 **Translation**: IndicTrans2 for cross-language communication
- 🛡️ **Safety First**: Toxicity filtering and content moderation
- 🤖 **3D Avatar**: Three.js-based sign language animation
- 🔒 **Privacy-Focused**: No storage of raw audio/video data

## Tech Stack

### Frontend
- React 18+
- Three.js (3D Avatar)
- MediaPipe (Keypoint extraction)
- WebSocket (Real-time communication)

### Backend
- FastAPI (API Gateway)
- Python Microservices
- PostgreSQL
- WebSocket Server

### AI/ML Models
- **ISL Recognition**: Lightweight Transformer (LSTM-based for laptop compatibility)
- **Speech Recognition**: OpenAI Whisper (tiny/base models)
- **Translation**: IndicTrans2
- **Text Normalization**: spaCy, IndicBART
- **Safety**: HuggingFace Toxicity Classifier

## Project Structure

```
SunoSaathi/
├── backend/              # Backend services
│   ├── api_gateway/      # Main API gateway
│   ├── services/         # Microservices
│   └── database/         # Database models
├── frontend/             # React application
│   ├── src/
│   │   ├── components/   # React components
│   │   └── services/     # API services
│   └── public/
├── data/                 # Sign dictionary & datasets
└── docker-compose.yml    # Container orchestration
```

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- GPU optional (CPU-optimized models included)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd SunoSaathi
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Database Setup**
```bash
# Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE sunosaathi;"
# Run migrations
python backend/database/init_db.py
```

5. **Start Services**
```bash
# Terminal 1: Start backend
cd backend/api_gateway
uvicorn main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev
```

## Development Roadmap

- [x] Phase 1: Project Setup
- [ ] Phase 2: Deaf User Pipeline (In Progress)
- [ ] Phase 3: Hearing User Pipeline
- [ ] Phase 4: Integration & Testing
- [ ] Phase 5: Deployment

## Responsible AI Principles

✅ **No Raw Data Storage**: Audio/video processed in real-time, not stored  
✅ **Consent-Based**: Explicit user consent for camera/microphone access  
✅ **Cultural Appropriateness**: Context-aware translations and sign language  
✅ **Safety Filtering**: Toxicity detection and content moderation  
✅ **Transparency**: Clear communication about AI limitations

## License

[Add your license here]

## Contributors

[Add contributors]
