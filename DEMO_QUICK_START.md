# 🚀 Quick Start Guide for Demo

## Start All Services (5 minutes)

### Terminal 1: API Gateway
```bash
cd backend/api_gateway
../venv/Scripts/python.exe main.py
```
**Expected**: Server running on http://localhost:8000

### Terminal 2: ISL Recognition
```bash
cd backend/services/isl_recognition
../../venv/Scripts/python.exe app.py
```
**Expected**: Server running on http://localhost:8001

### Terminal 3: Translation
```bash
cd backend/services/translation
../../venv/Scripts/python.exe app.py
```
**Expected**: Server running on http://localhost:8002

### Terminal 4: TTS
```bash
cd backend/services/tts
../../venv/Scripts/python.exe app.py
```
**Expected**: Server running on http://localhost:8003

### Terminal 5: Safety
```bash
cd backend/services/safety
../../venv/Scripts/python.exe app.py
```
**Expected**: Server running on http://localhost:8004

### Terminal 6: Frontend
```bash
cd frontend
npm run dev
```
**Expected**: Server running on http://localhost:5173

---

## Quick Health Check

```bash
cd backend
venv/Scripts/python.exe test_services.py
```

Should show: ✅ ALL SERVICES READY FOR DEMO!

---

## Demo Flow (5 minutes)

### 1. Landing Page (10 seconds)
- Open http://localhost:5173
- Show clean, modern interface
- Explain: "SunoSaathi - Breaking communication barriers"

### 2. Deaf User Demo (2 minutes)
- Click "Deaf User"
- Allow camera access
- Perform sign language gesture (or use demo video)
- Show:
  - ✅ Real-time keypoint detection
  - ✅ Sign recognition
  - ✅ Translation to Hindi/Tamil
  - ✅ Text-to-speech output

### 3. Hearing User Demo (2 minutes)
- Go back, click "Hearing User"
- Click microphone OR type: "Hello, how are you?"
- Show:
  - ✅ Speech recognition
  - ✅ Safety filter (all safe)
  - ✅ Translation
  - ✅ Sign detection
  - ✅ 3D avatar animation

### 4. Technology Highlight (30 seconds)
- LSTM model for ISL recognition
- MediaPipe for keypoint extraction
- Multi-language support (10 Indian languages)
- Responsible AI with safety filters
- Three.js for 3D avatar

### 5. Impact Statement (30 seconds)
- "18 million deaf people in India"
- "First ISL-focused platform with Indian language support"
- "Making communication accessible for all"

---

## Backup Plan

If live demo fails:
1. Show demo video (record one beforehand!)
2. Show code walkthrough
3. Explain architecture with slides

---

## Common Issues & Fixes

### Issue: Service won't start
**Fix**: Check if port is already in use
```bash
netstat -ano | findstr :8000
```

### Issue: Camera not working
**Fix**: Use demo video or show pre-recorded demo

### Issue: Frontend won't connect
**Fix**: Check CORS settings in backend/api_gateway/main.py

---

## Key Talking Points

1. **Problem**: 18M deaf people in India lack ISL support
2. **Solution**: AI-powered real-time ISL recognition & translation
3. **Innovation**: First to combine ISL + Indian languages + 3D avatar
4. **Tech**: LSTM, MediaPipe, React, Three.js, Microservices
5. **Impact**: Accessibility for millions, education, employment

---

## Questions You'll Get

**Q: How accurate is the model?**
A: "Currently trained on 5 signs with 100% training accuracy. Expanding to 50+ signs using INCLUDE-50 dataset."

**Q: Real-time performance?**
A: "Processing in <2 seconds end-to-end. Optimized for low latency."

**Q: Privacy concerns?**
A: "No video data stored. All processing in-memory. Responsible AI principles."

**Q: Scalability?**
A: "Microservices architecture. Each service scales independently."

**Q: What's next?**
A: "Mobile app, 50+ signs, real-time video calls, integration with Zoom/Teams."

---

## Time Remaining: ~7 hours

✅ Hour 1 DONE: Backend fixed, services ready
⏰ Hour 2-3: Polish UI, add landing page
⏰ Hour 4: Practice demo
⏰ Hour 5: Create slides
⏰ Hour 6-7: Final testing
⏰ Hour 8: Final prep

**You're on track! 🚀**
