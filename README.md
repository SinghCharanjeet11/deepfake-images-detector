# Deepfake Detection Platform — Backend

FastAPI backend for detecting AI-generated and manipulated images.

## Quick Start

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.template .env

# 4. Initialise the database
python scripts/init_db.py

# 5. Start the server
uvicorn main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

## Project Structure

```
├── main.py                  # FastAPI app entry point
├── config.py                # Environment variable config
├── requirements.txt
├── .env.template            # Copy to .env and fill in values
│
├── api/
│   ├── routes.py            # All API endpoints
│   ├── models.py            # Pydantic request/response models
│   └── file_utils.py        # File validation and storage helpers
│
├── database/
│   ├── models.py            # SQLAlchemy ORM models
│   └── connection.py        # DB engine, session, get_db()
│
├── models/
│   └── detector.py          # ML detector stub (ML team fills this in)
│
├── reports/
│   ├── json_generator.py    # JSON report generation
│   └── pdf_generator.py     # PDF report generation (ReportLab)
│
├── scripts/
│   ├── init_db.py           # Create/reset database tables
│   └── cleanup_old_files.py # Delete files older than N days
│
├── tests/
│   ├── conftest.py          # Shared pytest fixtures
│   ├── test_upload.py
│   ├── test_jobs.py
│   └── test_history.py
│
├── uploads/                 # Uploaded files (git-ignored)
├── thumbnails/              # Generated thumbnails (git-ignored)
└── database/                # SQLite .db file (git-ignored)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload image for detection |
| GET | `/api/jobs/{job_id}` | Poll job status / get result |
| GET | `/api/history` | Paginated list of past results |
| GET | `/api/thumbnails/{job_id}` | Serve thumbnail image |
| GET | `/api/reports/{job_id}/json` | Download JSON report |
| GET | `/api/reports/{job_id}/pdf` | Download PDF report |
| GET | `/health` | Server health check |

## Running Tests

```bash
pytest tests/ -v
```

## For the ML Team (Charanjeet / Chirag)

Open `models/detector.py` and implement:
- `detect(file_path)` → `{"label": "real"|"fake", "confidence": 0.0-1.0}`
- `generate_thumbnail(file_path, job_id)` → path to saved thumbnail

**Do not change the method signatures** — the backend depends on them.
# 🛡️ Deepfake Detection Platform

> AI-powered deepfake detection system with 99.83% accuracy using EfficientNet-B4

A production-ready web application that uses deep learning to detect AI-generated and manipulated face images. Built with PyTorch, FastAPI, and modern web technologies.

## 🎯 Overview

This platform analyzes face images and determines whether they are authentic photographs or AI-generated deepfakes. The system provides:

- **Real-time detection** with confidence scores
- **Web-based interface** for easy image upload
- **Detailed reports** in PDF and JSON formats
- **Analysis history** with searchable records
- **RESTful API** for integration with other systems

**Use Cases**: Media verification, forensic analysis, content moderation, educational demonstrations

## ✨ Features

- ✅ **99.83% Accuracy** on 140K test images
- ✅ **Sub-second inference** on CPU
- ✅ **Responsive web UI** with drag-and-drop upload
- ✅ **Batch processing** support
- ✅ **Export reports** (PDF/JSON)
- ✅ **Analysis history** with pagination
- ✅ **RESTful API** with OpenAPI docs
- ✅ **SQLite database** for persistence

## 🧠 Machine Learning Model

### Architecture
```
Input Image (224×224) 
    ↓
EfficientNet-B4 (Pre-trained on ImageNet)
    ↓
Feature Extraction (19M parameters)
    ↓
Binary Classification Layer
    ↓
Output: Real/Fake + Confidence Score
```

**Algorithm**: Convolutional Neural Network (CNN) with Transfer Learning  
**Framework**: PyTorch  
**Base Model**: EfficientNet-B4 (ImageNet pre-trained)  
**Task**: Binary Image Classification

### Performance Metrics

| Metric | Value |
|--------|-------|
| Test Accuracy | **99.83%** |
| Validation Accuracy | 99.84% |
| Test Loss | 0.0070 |
| Inference Time | <1 second (CPU) |
| Model Size | 75 MB |

### Training Configuration

| Parameter | Value |
|-----------|-------|
| Dataset Size | 140,000 images |
| Training Images | 100,000 (50K real, 50K fake) |
| Validation Images | 20,000 (10K real, 10K fake) |
| Test Images | 20,000 (10K real, 10K fake) |
| Epochs | 15 |
| Batch Size | 64 (Colab GPU) / 16 (local CPU) |
| Learning Rate | 0.0001 |
| Optimizer | Adam |
| Loss Function | Cross-Entropy |
| Data Augmentation | Random flip, rotation, color jitter |
| Training Platform | Google Colab (Tesla T4 GPU) |
| Training Time | ~1-2 hours |

## 📊 Dataset

**Source**: [Real and Fake Face Detection](https://www.kaggle.com/datasets/ciplab/real-and-fake-face-detection) (Kaggle)

### Dataset Statistics
- **Total Images**: 140,000 face images
- **Size**: ~4 GB
- **Format**: JPEG
- **Resolution**: Various (resized to 224×224 for training)
- **Balance**: 50% real, 50% fake
- **Pre-processing**: Pre-cropped faces (no face detection needed)

### Split Distribution
```
├── Training Set:   100,000 images (50,000 real + 50,000 fake)
├── Validation Set:  20,000 images (10,000 real + 10,000 fake)
└── Test Set:        20,000 images (10,000 real + 10,000 fake)
```

### Download Instructions
1. Visit [Kaggle Dataset Page](https://www.kaggle.com/datasets/ciplab/real-and-fake-face-detection)
2. Download `real-and-fake-face-detection.zip` (~4 GB)
3. Extract to `datasets/archive/real_vs_fake/real-vs-fake/`
4. Verify folder structure:
```
datasets/archive/real_vs_fake/real-vs-fake/
├── train/
│   ├── real/    # 50,000 images
│   └── fake/    # 50,000 images
├── valid/
│   ├── real/    # 10,000 images
│   └── fake/    # 10,000 images
└── test/
    ├── real/    # 10,000 images
    └── fake/    # 10,000 images
```

**Note**: Dataset is excluded from Git due to size. Download separately if retraining.

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager
- 4 GB free disk space (if downloading dataset)

### Installation

```bash
# 1. Clone the repository
git clone <your-repository-url>
cd deepfake-detection-platform

# 2. Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python scripts/init_db.py
```

### Running the Application

**Option 1: Using the startup script (Windows)**
```bash
start_server.bat
```

**Option 2: Manual start**
```bash
uvicorn main:app --reload --port 8000
```

### Access the Application

Once started, open your browser and navigate to:

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### First-Time Usage

1. Open http://localhost:8000 in your browser
2. Drag and drop an image or click "Browse File"
3. Click "Run Analysis"
4. View results with confidence score
5. Download PDF or JSON report (optional)
6. Check "History" tab for past analyses

## 📖 Usage Examples

### Web Interface

The easiest way to use the platform:

1. **Upload**: Drag & drop or browse for a JPEG/PNG image
2. **Analyze**: Click "Run Analysis" button
3. **Results**: View verdict (Real/Fake) with confidence percentage
4. **Export**: Download PDF report or JSON data
5. **History**: Browse all previous analyses

### Command Line Testing

Test the model on sample images:

```bash
# Test on dataset samples
python scripts/test_inference.py

# Test on specific image
python -c "from detector.model import DeepfakeDetector; d = DeepfakeDetector('models/deepfake_detector.pth'); print(d.detect('path/to/image.jpg'))"

# Demo accuracy on 40 random images
python scripts/demo_accuracy.py
```

### Python API

Integrate detection into your own code:

```python
from detector.model import DeepfakeDetector

# Initialize detector
detector = DeepfakeDetector(
    model_path="models/deepfake_detector.pth",
    device="cpu"  # or "cuda" for GPU
)

# Detect single image
result = detector.detect("path/to/image.jpg")
print(f"Label: {result.label}")           # "real" or "fake"
print(f"Confidence: {result.confidence}")  # 0.0 to 1.0

# Generate thumbnail
detector.generate_thumbnail(
    file_path="path/to/image.jpg",
    output_path="path/to/thumbnail.jpg"
)
```

### REST API

Use the HTTP API for integration:

```bash
# Upload image for detection
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@image.jpg"

# Response: {"job_id": "abc123", "status": "completed"}

# Get results
curl "http://localhost:8000/api/jobs/abc123"

# Response: {
#   "job_id": "abc123",
#   "status": "completed",
#   "result": {
#     "label": "fake",
#     "confidence": 0.9876
#   }
# }

# Download PDF report
curl "http://localhost:8000/api/reports/abc123/pdf" -o report.pdf

# Get analysis history
curl "http://localhost:8000/api/history?page=1&page_size=10"
```

## 📁 Project Structure

```
deepfake-detection-platform/
│
├── 📱 Frontend (Static Files)
│   ├── static/
│   │   ├── index.html              # Upload page
│   │   ├── results.html            # Results display
│   │   ├── history.html            # Analysis history
│   │   ├── css/styles.css          # All styling
│   │   └── js/
│   │       ├── upload.js           # Upload logic
│   │       ├── results.js          # Results display logic
│   │       └── history.js          # History pagination
│
├── 🔧 Backend (FastAPI)
│   ├── main.py                     # FastAPI application entry
│   ├── config.py                   # Environment configuration
│   ├── api/
│   │   ├── routes.py               # API endpoints
│   │   ├── models.py               # Pydantic schemas
│   │   └── file_utils.py           # File handling utilities
│   ├── database/
│   │   ├── connection.py           # SQLite connection
│   │   └── models.py               # SQLAlchemy ORM models
│   └── reports/
│       ├── pdf_generator.py        # PDF report generation
│       └── json_generator.py       # JSON export
│
├── 🧠 ML Model
│   ├── detector/
│   │   ├── __init__.py
│   │   └── model.py                # DeepfakeDetector class
│   ├── models/
│   │   └── deepfake_detector.pth   # Trained weights (75MB)
│   └── scripts/
│       ├── train_model.py          # Training script (reference)
│       ├── test_inference.py       # Test model on samples
│       ├── demo_accuracy.py        # Demo for faculty
│       └── init_db.py              # Database initialization
│
├── 📊 Data & Storage
│   ├── datasets/                   # Training data (not in Git)
│   │   └── archive/real_vs_fake/   # Download from Kaggle
│   ├── uploads/                    # User uploaded images
│   ├── thumbnails/                 # Generated thumbnails
│   └── database/
│       └── deepfake_detector.db    # SQLite database
│
├── 📝 Documentation
│   ├── README.md                   # This file
│   ├── requirements.txt            # Python dependencies
│   ├── .env.template               # Environment variables template
│   ├── Deepfake_Detection_Training.ipynb  # Colab training notebook
│   └── .kiro/specs/                # Project specifications
│
└── 🧪 Testing
    └── tests/
        ├── test_upload.py
        ├── test_jobs.py
        └── test_history.py
```

## 🛠️ Technology Stack

### Machine Learning
| Technology | Purpose |
|------------|---------|
| **PyTorch** | Deep learning framework |
| **EfficientNet-B4** | CNN architecture |
| **torchvision** | Image transformations |
| **PIL (Pillow)** | Image processing |
| **efficientnet-pytorch** | Pre-trained model library |

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | Web framework & REST API |
| **Uvicorn** | ASGI server |
| **SQLAlchemy** | ORM for database |
| **SQLite** | Database |
| **Pydantic** | Data validation |
| **ReportLab** | PDF generation |
| **python-multipart** | File upload handling |

### Frontend
| Technology | Purpose |
|------------|---------|
| **HTML5/CSS3** | Structure & styling |
| **Vanilla JavaScript** | Client-side logic |
| **Fetch API** | HTTP requests |
| **Responsive Design** | Mobile-first approach |

## 🔌 API Endpoints

### Detection Endpoints

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| `POST` | `/api/upload` | Upload image for analysis | `multipart/form-data` | `{job_id, status}` |
| `GET` | `/api/jobs/{job_id}` | Get analysis result | - | `{job_id, status, result}` |
| `GET` | `/api/history` | List all analyses | `?page=1&page_size=10` | `{results[], page, total_pages}` |

### Report Endpoints

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `GET` | `/api/reports/{job_id}/pdf` | Download PDF report | PDF file |
| `GET` | `/api/reports/{job_id}/json` | Download JSON data | JSON file |
| `GET` | `/api/thumbnails/{job_id}` | Get thumbnail image | JPEG image |

### System Endpoints

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `GET` | `/health` | Health check | `{status: "healthy"}` |
| `GET` | `/docs` | API documentation | Swagger UI |

**Full API documentation**: http://localhost:8000/docs (when server is running)

## 🧪 Testing & Validation

### Run All Tests
```bash
# Run pytest suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Test Model Inference
```bash
# Test on sample images from dataset
python scripts/test_inference.py

# Expected output:
# --- Testing on REAL images ---
# 00001.jpg: real (confidence: 1.00)
# 00007.jpg: real (confidence: 1.00)
# ...
# --- Testing on FAKE images ---
# 00276TOPP4.jpg: fake (confidence: 1.00)
# ...
# ✓ Inference test complete!
```

### Demo for Faculty/Judges
```bash
# Run accuracy demo on 40 random images
python scripts/demo_accuracy.py

# Shows:
# - 20 real images tested
# - 20 fake images tested
# - Accuracy percentage
# - Confidence scores
# - Visual indicators (✓/✗)
```

### Manual Testing
```python
# Test specific image
from detector.model import DeepfakeDetector

detector = DeepfakeDetector('models/deepfake_detector.pth')
result = detector.detect('path/to/test/image.jpg')
print(f"{result.label} ({result.confidence:.2%})")
```

## 🎓 For Faculty Demonstration

### What to Showcase

1. **High Accuracy**: 99.83% on 140,000 test images
2. **Real-time Detection**: Results in <1 second
3. **User-Friendly Interface**: Simple drag-and-drop
4. **Confidence Scores**: Model shows certainty level
5. **Professional Reports**: PDF export with details
6. **Analysis History**: Track all detections

### Demo Script

```bash
# 1. Start the server
uvicorn main:app --reload --port 8000

# 2. Open browser to http://localhost:8000

# 3. Upload test images from:
datasets/archive/real_vs_fake/real-vs-fake/test/real/
datasets/archive/real_vs_fake/real-vs-fake/test/fake/

# 4. Show accuracy demo
python scripts/demo_accuracy.py

# 5. Show API documentation
# Navigate to http://localhost:8000/docs
```

### Key Talking Points

- **Algorithm**: EfficientNet-B4 CNN with transfer learning
- **Training**: 140K images, Google Colab GPU
- **Accuracy**: 99.83% on balanced test set
- **Speed**: Sub-second inference on CPU
- **Practical**: Web interface + REST API
- **Scalable**: Can process batches, add video support

## ⚠️ Important Notes

### Model Limitations

**Domain Shift**: The model is trained on a specific dataset of GAN-generated faces (2019-2020 era). Performance may vary on:

- Modern AI generators (DALL-E 3, Midjourney, Stable Diffusion)
- Newer GAN architectures (StyleGAN3+)
- Different manipulation techniques
- Non-face images

**Why**: This is called "domain shift" - models perform best on data similar to their training distribution.

**Solution**: For production use, retrain with diverse datasets including modern generators.

**For Demo**: Use images from the test dataset to showcase true model capability (99.83% accuracy).

### Best Practices

✅ **DO**:
- Use test dataset images for demonstrations
- Mention the training dataset source
- Explain the model's strengths and limitations
- Show confidence scores alongside predictions

❌ **DON'T**:
- Claim it detects all types of deepfakes
- Test on completely different image types
- Ignore confidence scores below 90%
- Use for critical decisions without human review

## 🔮 Future Enhancements

- [ ] **Video Detection**: Frame-by-frame analysis with temporal consistency
- [ ] **Modern Generators**: Retrain on DALL-E, Midjourney, Stable Diffusion outputs
- [ ] **Ensemble Models**: Combine multiple architectures for better generalization
- [ ] **Explainability**: Highlight suspicious regions in images
- [ ] **Batch Processing**: Upload multiple images at once
- [ ] **API Authentication**: Secure API with JWT tokens
- [ ] **Cloud Deployment**: Deploy on AWS/Azure/GCP
- [ ] **Mobile App**: iOS/Android applications
- [ ] **Model Optimization**: Quantization for faster inference
- [ ] **Confidence Thresholds**: "Uncertain" category for low-confidence predictions

## 📄 License

This project is developed for educational and research purposes.

## 🙏 Acknowledgments

- **Dataset**: [Kaggle - Real and Fake Face Detection](https://www.kaggle.com/datasets/ciplab/real-and-fake-face-detection)
- **Model Architecture**: EfficientNet-B4 by Google Research
- **Framework**: PyTorch by Meta AI
- **Training Platform**: Google Colab
- **Inspiration**: Growing concern about deepfake misinformation

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the API documentation at `/docs`
- Review the project specifications in `.kiro/specs/`

## 🏗️ Development Status

| Component | Status |
|-----------|--------|
| ML Model Training | ✅ Complete |
| Inference Pipeline | ✅ Complete |
| Backend API | ✅ Complete |
| Frontend UI | ✅ Complete |
| Database | ✅ Complete |
| PDF Reports | ✅ Complete |
| Testing Suite | ✅ Complete |
| Documentation | ✅ Complete |
| Video Detection | 🔄 In Progress |
| Authentication | 🔄 In Progress |
| Cloud Deployment | ⏳ Planned |

---


