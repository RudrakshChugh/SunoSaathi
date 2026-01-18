@echo off
echo ========================================
echo Starting SunoSaathi Services
echo ========================================
echo.

echo Starting API Gateway...
start "API Gateway" cmd /k "cd backend\api_gateway && ..\venv\Scripts\python.exe main.py"
timeout /t 3 /nobreak >nul

echo Starting ISL Recognition...
start "ISL Recognition" cmd /k "cd backend\services\isl_recognition && ..\..\venv\Scripts\python.exe app.py"
timeout /t 2 /nobreak >nul

echo Starting Translation...
start "Translation" cmd /k "cd backend\services\translation && ..\..\venv\Scripts\python.exe app.py"
timeout /t 2 /nobreak >nul

echo Starting TTS...
start "TTS" cmd /k "cd backend\services\tts && ..\..\venv\Scripts\python.exe app.py"
timeout /t 2 /nobreak >nul

echo Starting Voice-to-Sign...
start "Voice-to-Sign" cmd /k "cd backend\services\voice_to_sign && ..\..\venv\Scripts\python.exe app.py"
timeout /t 2 /nobreak >nul

echo Starting Safety...
start "Safety" cmd /k "cd backend\services\safety && ..\..\venv\Scripts\python.exe app.py"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo Wait 10 seconds for services to initialize...
timeout /t 10 /nobreak >nul

echo.
echo Starting Frontend...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo ========================================
echo SunoSaathi is starting!
echo ========================================
echo.
echo API Gateway:      http://localhost:8000
echo ISL Recognition:  http://localhost:8001
echo Translation:      http://localhost:8002
echo TTS:              http://localhost:8003
echo Safety:           http://localhost:8004
echo Voice-to-Sign:    http://localhost:8005 (Whisper + spaCy)
echo Frontend:         http://localhost:5173
echo.
echo Press any key to exit...
pause >nul
