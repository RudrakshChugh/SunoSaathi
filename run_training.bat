@echo off
echo Starting ISL Model Training...

:: Set paths
set BASE_DIR=%~dp0
set DATA_ROOT=%BASE_DIR%\datasets\Greetings-browser-processed
set TRAIN_DIR=%DATA_ROOT%\train
set VAL_DIR=%DATA_ROOT%\val
set VOCAB_FILE=%DATA_ROOT%\vocabulary.json
set OUTPUT_DIR=%BASE_DIR%\backend\trained_models

:: Ensure directories exist
if not exist "%TRAIN_DIR%" (
    echo Error: Training directory not found at %TRAIN_DIR%
    pause
    exit /b 1
)

:: Run training script (Using Virtual Environment)
%BASE_DIR%\backend\venv\Scripts\python.exe backend\services\isl_recognition\train.py ^
    --train_data "%TRAIN_DIR%" ^
    --val_data "%VAL_DIR%" ^
    --vocab "%VOCAB_FILE%" ^
    --output "%OUTPUT_DIR%" ^
    --epochs 50 ^
    --batch_size 4

echo.
echo Training complete!
pause
