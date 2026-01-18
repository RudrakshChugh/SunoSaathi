# ISL-CSLTR Image-Based Training Guide

## Overview

This guide explains how to train both **word-level** and **sentence-level** ISL recognition models using the ISL-CSLTR Kaggle dataset images.

---

## Dataset Preparation

### 1. Download ISL-CSLTR Dataset

Download from: https://www.kaggle.com/datasets/drblack00/isl-csltr-indian-sign-language-dataset

The dataset contains:
- **1,036 word-level images**
- **18,863 sentence-level frames**

### 2. Expected Directory Structure

#### Word-Level (1,036 images)
```
datasets/isl_csltr/words/
├── hello/
│   ├── img001.jpg
│   ├── img002.jpg
│   └── ...
├── thank_you/
│   ├── img001.jpg
│   └── ...
└── ...
```

#### Sentence-Level (18,863 frames)
```
datasets/isl_csltr/sentences/
├── sentence_001/
│   ├── frame_001.jpg
│   ├── frame_002.jpg
│   └── ...
├── sentence_002/
    └── ...
```

You also need a labels file for sentences:
```json
// datasets/isl_csltr/sentence_labels.json
{
  "sentence_001": "hello how are you",
  "sentence_002": "good morning",
  ...
}
```

---

## Training Word-Level Model

### Basic Training
```bash
python train_word_model.py \
  --data_dir "datasets/isl_csltr/words" \
  --output_dir "trained_models" \
  --epochs 50 \
  --batch_size 32
```

### Advanced Options
```bash
python train_word_model.py \
  --data_dir "datasets/isl_csltr/words" \
  --output_dir "trained_models" \
  --vocab_file "trained_models/word_vocabulary.json" \
  --backbone resnet50 \
  --epochs 50 \
  --batch_size 32 \
  --lr 0.001 \
  --val_split 0.2 \
  --device cuda
```

**Parameters:**
- `--data_dir`: Directory with word images (organized by word folders)
- `--output_dir`: Where to save trained models
- `--vocab_file`: Vocabulary JSON (auto-generated if not provided)
- `--backbone`: CNN architecture (`resnet34`, `resnet50`, `efficientnet_b0`, `mobilenet_v3_small`)
- `--epochs`: Number of training epochs
- `--batch_size`: Batch size
- `--lr`: Learning rate
- `--val_split`: Validation split (0.2 = 20%)
- `--device`: `cuda` or `cpu`

### Output
- `trained_models/best_word_model.pth` - Best model based on validation accuracy
- `trained_models/word_vocabulary.json` - Vocabulary (word list)

---

## Training Sentence-Level Model

### Basic Training
```bash
python train_sentence_model.py \
  --data_dir "datasets/isl_csltr/sentences" \
  --labels_file "datasets/isl_csltr/sentence_labels.json" \
  --output_dir "trained_models" \
  --epochs 50 \
  --batch_size 8
```

### Advanced Options
```bash
python train_sentence_model.py \
  --data_dir "datasets/isl_csltr/sentences" \
  --labels_file "datasets/isl_csltr/sentence_labels.json" \
  --output_dir "trained_models" \
  --vocab_file "trained_models/sentence_vocabulary.json" \
  --backbone resnet34 \
  --hidden_dim 512 \
  --epochs 50 \
  --batch_size 8 \
  --lr 0.0005 \
  --max_frames 100 \
  --val_split 0.2 \
  --device cuda
```

**Parameters:**
- `--data_dir`: Directory with sentence frame sequences
- `--labels_file`: JSON mapping sentence IDs to text
- `--output_dir`: Where to save trained models
- `--vocab_file`: Vocabulary JSON (auto-generated if not provided)
- `--backbone`: CNN architecture (`resnet18`, `resnet34`, `mobilenet_v3_small`)
- `--hidden_dim`: LSTM hidden dimension
- `--epochs`: Number of training epochs
- `--batch_size`: Batch size (smaller for sequences)
- `--lr`: Learning rate
- `--max_frames`: Maximum frames per sequence
- `--val_split`: Validation split
- `--device`: `cuda` or `cpu`

### Output
- `trained_models/best_sentence_model.pth` - Best model
- `trained_models/sentence_vocabulary.json` - Vocabulary (sentences)

---

## Model Checkpoints Structure

Both training scripts save checkpoints with:
```python
{
    'epoch': int,
    'model_state_dict': dict,  # Model weights
    'optimizer_state_dict': dict,
    'val_loss': float,
    'val_acc': float,
    'vocab': list,  # Vocabulary
    'config': {
        'backbone': str,
        'num_classes': int,
        'image_size': int
    }
}
```

---

## Hardware Requirements

### Word-Level Training
- **GPU**: Optional but recommended (NVIDIA with 4GB+ VRAM)
- **RAM**: 8GB minimum
- **Time**: ~1-2 hours on GPU (50 epochs)

### Sentence-Level Training
- **GPU**: Highly recommended (NVIDIA with 8GB+ VRAM)
- **RAM**: 16GB minimum
- **Time**: ~3-5 hours on GPU (50 epochs)

---

## Testing Models

### Test Word Model
```python
import torch
from model_image import ISLWordRecognizer

# Load checkpoint
checkpoint = torch.load('trained_models/best_word_model.pth')
vocab = checkpoint['vocab']

# Create model
model = ISLWordRecognizer(num_classes=len(vocab))
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

print(f"Word model loaded with {len(vocab)} classes")
```

### Test Sentence Model
```python
import torch
from model_image import ISLSentenceRecognizer

# Load checkpoint
checkpoint = torch.load('trained_models/best_sentence_model.pth')
vocab = checkpoint['vocab']
config = checkpoint['config']

# Create model
model = ISLSentenceRecognizer(
    num_classes=len(vocab),
    backbone=config['backbone'],
    hidden_dim=config.get('hidden_dim', 512)
)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

print(f"Sentence model loaded with {len(vocab)} classes")
```

---

## Next Steps

After training:
1. Copy `.pth` files to `backend/trained_models/`
2. Update backend API (`app.py`) to load these models
3. Update frontend to capture images instead of keypoints
4. Test integration

See `isl_csltr_migration_plan.md` for complete migration guide!
