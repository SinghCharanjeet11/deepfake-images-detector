# Deepfake Detection Platform

A machine learning-powered platform for detecting deepfake images with 99.83% accuracy.

## 🎯 Project Overview

This platform uses deep learning to identify whether a face image is real or AI-generated/manipulated. Built for educational purposes and faculty demonstration.

## 🏆 Current Status

- ✅ **Image Detection**: Fully functional with 99.83% test accuracy
- ⏳ **Video Detection**: Coming soon
- ⏳ **Web Interface**: In development by team

## 🧠 Machine Learning Model

### Model Architecture
- **Algorithm**: EfficientNet-B4 with Transfer Learning
- **Framework**: PyTorch
- **Pre-training**: ImageNet weights
- **Task**: Binary Classification (Real vs Fake)

### Performance Metrics
- **Test Accuracy**: 99.83%
- **Validation Accuracy**: 99.84%
- **Training Accuracy**: 99.10%
- **Test Loss**: 0.0070
- **Inference Time**: <1 second per image (CPU)

### Training Details
- **Epochs**: 2 (early stopping - model converged quickly)
- **Batch Size**: 16
- **Learning Rate**: 0.0001
- **Optimizer**: Adam
- **Loss Function**: Cross-Entropy
- **Training Platform**: Google Colab (GPU: Tesla T4)
- **Training Time**: ~1 hour

## 📊 Dataset

### Source
**140K Real and Fake Faces**
- **Platform**: Kaggle
- **Link**: [Real and Fake Face Detection](https://www.kaggle.com/datasets/ciplab/real-and-fake-face-detection)
- **Size**: ~4GB
- **Total Images**: 140,000 face images

### Dataset Structure
```
datasets/archive/real_vs_fake/real-vs-fake/
├── train/          # 100,000 images (50K real, 50K fake)
│   ├── real/
│   └── fake/
├── valid/          # 20,000 images (10K real, 10K fake)
│   ├── real/
│   └── fake/
└── test/           # 20,000 images (10K real, 10K fake)
    ├── real/
    └── fake/
```

### Dataset Characteristics
- **Pre-cropped faces**: All images are centered on faces (no face detection needed)
- **Balanced**: 50/50 split between real and fake images
- **Resolution**: Various sizes, resized to 224×224 for training
- **Format**: JPEG images

### How to Download Dataset
1. Go to [Kaggle Dataset Page](https://www.kaggle.com/datasets/ciplab/real-and-fake-face-detection)
2. Download `real-and-fake-face-detection.zip`
3. Extract to `datasets/archive/real_vs_fake/real-vs-fake/`
4. Verify structure matches above

**Note**: Dataset is excluded from Git repository due to size (4GB). Download separately if you want to retrain the model.

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.10+
pip install -r requirements.txt
```

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd deepfake-detect

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### Test Image Detection
```bash
python scripts/test_inference.py
```

#### Use in Your Code
```python
from detector.model import DeepfakeDetector

# Initialize detector
detector = DeepfakeDetector("models/deepfake_detector.pth", device="cpu")

# Detect image
result = detector.detect("path/to/image.jpg")
print(f"Label: {result.label}")           # "real" or "fake"
print(f"Confidence: {result.confidence}")  # 0.0 to 1.0
```

## 📁 Project Structure

```
deepfake-detect/
├── detector/                    # ML inference module
│   ├── __init__.py
│   └── model.py                # DeepfakeDetector class
├── models/                      # Trained model weights
│   └── deepfake_detector.pth   # EfficientNet-B4 model (75MB)
├── scripts/                     # Utility scripts
│   ├── train_model.py          # Local training script (reference)
│   └── test_inference.py       # Test inference on samples
├── datasets/                    # Training data (not in Git)
│   └── archive/real_vs_fake/   # Download from Kaggle
├── .kiro/specs/                 # Project specifications
│   └── deepfake-detection-platform/
│       ├── requirements.md
│       ├── design.md
│       └── *-tasks.md          # Task files for each role
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🛠️ Tech Stack

### Machine Learning
- **PyTorch**: Deep learning framework
- **EfficientNet-PyTorch**: Pre-trained model library
- **torchvision**: Image transformations
- **PIL**: Image loading and processing

### Backend (In Development)
- **FastAPI**: Web framework
- **SQLite**: Database
- **Uvicorn**: ASGI server

### Frontend (In Development)
- **HTML5/CSS3/JavaScript**: UI
- **Vanilla JS**: No framework (keeping it simple)

## 👥 Team Roles

- **ML Engineer**: Model training, inference pipeline (YOU)
- **Backend Developer**: FastAPI, database, API endpoints
- **Frontend Developer**: UI/UX, image upload interface
- **QA/Integration Engineer**: Testing, integration, deployment

## 📝 Development Workflow

### For ML Engineer (You)
1. ✅ Train model (DONE)
2. ✅ Create inference pipeline (DONE)
3. ✅ Test on sample images (DONE)
4. ⏳ Add video detection (TOMORROW)

### For Integration Engineer
1. Pull this ML code
2. Build FastAPI backend
3. Create upload endpoints
4. Integrate `DeepfakeDetector` class
5. Build frontend UI
6. Test end-to-end

## 🧪 Testing

### Run Tests
```bash
# Test on sample images from dataset
python scripts/test_inference.py

# Test on specific image
python -c "from detector.model import DeepfakeDetector; d = DeepfakeDetector('models/deepfake_detector.pth'); print(d.detect('path/to/image.jpg'))"
```

### Expected Output
```
--- Testing on REAL images ---
00001.jpg: real (confidence: 1.00)
00007.jpg: real (confidence: 1.00)
...

--- Testing on FAKE images ---
00276TOPP4.jpg: fake (confidence: 1.00)
008BYSE725.jpg: fake (confidence: 1.00)
...

✓ Inference test complete!
```

## 📚 Documentation

- **Training Guide**: `COLAB_TRAINING_GUIDE.md` (local only, not in Git)
- **Training Notebook**: `Deepfake_Detection_Training.ipynb` (local only)
- **API Documentation**: See `detector/model.py` docstrings
- **Project Specs**: `.kiro/specs/deepfake-detection-platform/`

## 🎓 Faculty Demo

### What to Show
1. **Model Performance**: 99.83% accuracy on 140K images
2. **Live Detection**: Upload image → Get result in <1 second
3. **Confidence Scores**: Model shows how confident it is
4. **Dataset**: Show Kaggle dataset source and structure

### Demo Script
```bash
# Show model working
python scripts/test_inference.py

# Show accuracy on multiple samples
python -c "from detector.model import DeepfakeDetector; import glob; d = DeepfakeDetector('models/deepfake_detector.pth'); real = glob.glob('datasets/archive/real_vs_fake/real-vs-fake/test/real/*.jpg')[:20]; fake = glob.glob('datasets/archive/real_vs_fake/real-vs-fake/test/fake/*.jpg')[:20]; real_correct = sum(1 for img in real if d.detect(img).label == 'real'); fake_correct = sum(1 for img in fake if d.detect(img).label == 'fake'); print(f'Real: {real_correct}/20 correct'); print(f'Fake: {fake_correct}/20 correct'); print(f'Overall: {(real_correct+fake_correct)/40*100:.1f}% accuracy')"
```

## 🔮 Future Work

- [ ] Video detection support
- [ ] Web interface deployment
- [ ] Batch processing
- [ ] API rate limiting
- [ ] Model optimization (quantization)
- [ ] Support for more deepfake types

## 📄 License

Educational project for faculty demonstration.

## 🙏 Acknowledgments

- **Dataset**: Kaggle - Real and Fake Face Detection
- **Model**: EfficientNet-B4 by Google Research
- **Framework**: PyTorch by Meta AI
- **Training Platform**: Google Colab

---

**Last Updated**: April 2026  
**Status**: Image Detection Complete ✅ | Video Detection In Progress ⏳
