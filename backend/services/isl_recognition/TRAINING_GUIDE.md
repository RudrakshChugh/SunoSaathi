# ISL Model Training Guide

## 📚 Overview

This guide will help you train the ISL Recognition Model on your own Indian Sign Language dataset.

---

## 🎯 Prerequisites

### 1. Dataset Requirements

You need ISL video recordings with labels. The dataset should contain:

- **Videos**: Sign language gestures performed by signers
- **Labels**: Text labels for each sign (e.g., "hello", "thank you", "water")
- **Format**: MP4, AVI, or any video format

### 2. Recommended Dataset Sources

**Option A: Use Existing ISL Datasets**
- **INCLUDE Dataset**: Indian Sign Language dataset
- **ISL-CSLRT**: Continuous Sign Language Recognition
- Search for "Indian Sign Language dataset" on:
  - Kaggle
  - GitHub
  - Academic repositories

**Option B: Create Your Own Dataset**
- Record videos of people performing ISL signs
- Minimum 50-100 samples per sign
- 20-30 different signs to start
- Consistent lighting and background

---

## 📁 Data Format

### Expected Directory Structure

```
isl_dataset/
├── train/
│   ├── hello_001.json
│   ├── hello_002.json
│   ├── thankyou_001.json
│   ├── water_001.json
│   └── ...
├── val/
│   ├── hello_050.json
│   ├── thankyou_050.json
│   └── ...
└── vocabulary.json
```

### JSON File Format

Each JSON file should contain:

```json
{
  "sign_label": "hello",
  "frames": [
    {
      "frame_id": 0,
      "keypoints": [
        [0.5, 0.3, 0.1],  // Keypoint 1 (x, y, z)
        [0.6, 0.4, 0.2],  // Keypoint 2
        ...               // 543 keypoints total
      ]
    },
    {
      "frame_id": 1,
      "keypoints": [ ... ]
    }
  ]
}
```

### Vocabulary File Format

`vocabulary.json`:
```json
[
  "hello",
  "thank you",
  "water",
  "food",
  "help",
  ...
]
```

---

## 🔧 Step 1: Prepare Your Dataset

### Option A: If You Have Videos

1. **Extract keypoints from videos** using the provided script:

```bash
cd backend/services/isl_recognition
python extract_keypoints.py --input_dir /path/to/videos --output_dir /path/to/dataset
```

This will:
- Process each video
- Extract MediaPipe keypoints
- Save as JSON files
- Create vocabulary.json automatically

### Option B: If You Already Have Keypoints

1. Organize your data in the format shown above
2. Create `vocabulary.json` with all unique sign labels
3. Split data into train (80%) and val (20%)

---

## 🚀 Step 2: Train the Model

### Basic Training

```bash
cd backend/services/isl_recognition

# Activate virtual environment
..\..\..\venv\Scripts\activate  # Windows
source ../../../venv/bin/activate  # Linux/Mac

# Train the model
python train.py \
  --train_data /path/to/dataset/train \
  --val_data /path/to/dataset/val \
  --vocab /path/to/dataset/vocabulary.json \
  --output ./trained_models \
  --epochs 50 \
  --batch_size 32 \
  --lr 0.001 \
  --device cpu
```

### Training on GPU (if available)

```bash
python train.py \
  --train_data /path/to/dataset/train \
  --val_data /path/to/dataset/val \
  --vocab /path/to/dataset/vocabulary.json \
  --output ./trained_models \
  --epochs 100 \
  --batch_size 64 \
  --lr 0.001 \
  --device cuda
```

### Parameters Explained

- `--train_data`: Path to training data directory
- `--val_data`: Path to validation data directory
- `--vocab`: Path to vocabulary JSON file
- `--output`: Where to save trained models
- `--epochs`: Number of training epochs (50-100 recommended)
- `--batch_size`: Batch size (32 for CPU, 64+ for GPU)
- `--lr`: Learning rate (0.001 is a good starting point)
- `--device`: 'cpu' or 'cuda'

---

## 📊 Step 3: Monitor Training

During training, you'll see:

```
==================================================================
ISL Recognition Model Training
==================================================================

Vocabulary size: 50 signs

Loading datasets...
Training samples: 2000
Validation samples: 500

Initializing model on cpu...

Starting training...
==================================================================
Epoch [1/50] Batch [10/63] Loss: 3.9124
Epoch [1/50] Batch [20/63] Loss: 3.7856
...

Epoch [1/50] Summary:
  Train Loss: 3.5234 | Train Acc: 12.50%
  Val Loss: 3.4123 | Val Acc: 15.20%
----------------------------------------------------------------------
✓ Saved best model (Val Acc: 15.20%)
```

### What to Look For

- **Loss decreasing**: Both train and val loss should decrease
- **Accuracy increasing**: Should reach 70-90% for good dataset
- **Overfitting**: If train acc >> val acc, reduce model complexity
- **Underfitting**: If both accuracies are low, train longer or increase model size

---

## 💾 Step 4: Use the Trained Model

### Update the Service

Once training is complete, update the ISL Recognition service to use your trained model:

1. **Copy the trained model**:
```bash
cp trained_models/best_model.pth models/isl_model.pth
```

2. **Update `app.py`** to load the trained model:

```python
# In app.py, update the model loading
checkpoint = torch.load('models/isl_model.pth', map_location=device)
model.load_state_dict(checkpoint['model_state_dict'])
vocabulary = checkpoint['vocab']
```

3. **Restart the ISL Recognition service**:
```bash
python app.py
```

---

## 🧪 Step 5: Test the Model

### Test in the Application

1. Open http://localhost:5174
2. Select "Deaf User"
3. Grant camera access
4. Start MediaPipe
5. Record a sign from your vocabulary
6. Check if it recognizes correctly!

### Test with Script

```bash
python test_model.py \
  --model trained_models/best_model.pth \
  --test_data /path/to/test/sample.json
```

---

## 📈 Improving Model Performance

### If Accuracy is Low (< 60%)

1. **Collect more data**: 100+ samples per sign
2. **Balance dataset**: Equal samples for each sign
3. **Increase epochs**: Train for 100+ epochs
4. **Data augmentation**: Add noise, rotation, scaling
5. **Tune hyperparameters**: Try different learning rates

### If Model is Overfitting

1. **Add dropout**: Increase dropout rate in model
2. **Reduce model size**: Fewer LSTM layers/units
3. **More training data**: Collect diverse samples
4. **Early stopping**: Stop when val loss stops improving

### If Training is Slow

1. **Use GPU**: Much faster than CPU
2. **Reduce batch size**: If running out of memory
3. **Reduce sequence length**: Trim long videos
4. **Use fewer keypoints**: Skip face landmarks (468 points)

---

## 🎓 Advanced Tips

### Data Augmentation

Add variations to increase dataset size:
- Mirror horizontally (for symmetric signs)
- Add small random noise to keypoints
- Time stretching (speed up/slow down)
- Random frame dropping

### Transfer Learning

If you have a small dataset:
1. Pre-train on a larger sign language dataset (ASL, BSL)
2. Fine-tune on ISL dataset
3. Freeze early layers, train only final layers

### Ensemble Models

Train multiple models and combine predictions:
- Different random seeds
- Different architectures (LSTM, GRU, Transformer)
- Vote or average predictions

---

## 🐛 Troubleshooting

### Error: "CUDA out of memory"
**Solution**: Reduce batch size or use CPU

### Error: "Keypoints shape mismatch"
**Solution**: Check that all samples have 543 keypoints

### Error: "Vocabulary mismatch"
**Solution**: Ensure vocabulary.json matches your labels

### Low accuracy after many epochs
**Solution**: 
- Check data quality
- Verify labels are correct
- Try different hyperparameters
- Collect more diverse data

---

## 📚 Next Steps

After training your model:

1. ✅ **Test thoroughly** with real sign language
2. ✅ **Integrate IndicTrans2** for better translation
3. ✅ **Add TTS engine** for speech output
4. ✅ **Build Hearing User Pipeline**
5. ✅ **Deploy to production**

---

## 💡 Quick Start Example

If you want to test with dummy data:

```bash
# Generate sample dataset
python generate_sample_data.py --output sample_dataset --num_signs 10 --samples_per_sign 50

# Train on sample data
python train.py \
  --train_data sample_dataset/train \
  --val_data sample_dataset/val \
  --vocab sample_dataset/vocabulary.json \
  --epochs 20

# Test the model
python app.py  # Start service
# Then test in browser at http://localhost:5174
```

---

## 📞 Need Help?

- Check the model architecture in `model.py`
- Review training logs for errors
- Verify data format matches examples
- Start with a small dataset (5-10 signs) to test

---

**Good luck with training! 🚀**
