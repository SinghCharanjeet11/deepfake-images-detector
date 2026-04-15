# ML Engineer Tasks: Deepfake Detection Platform

## Role Overview

As the ML Engineer, you are responsible for training the deepfake detection model, implementing the inference pipeline, preprocessing media files, and generating thumbnails. Your work provides the core detection functionality that the backend integrates with.

## Dependencies

- Access to training datasets (DeepFake-TIMIT, FaceForensics++, Google DFD, Celeb-DF, Facebook DFDC)
- Backend API requirements for detector interface

## Tasks

- [ ] 1. Dataset preparation
  - [ ] 1.1 Download and organize training datasets
    - Download DeepFake-TIMIT, FaceForensics++, Google DFD, Celeb-DF, Facebook DFDC
    - Organize into datasets/ directory with subdirectories for each dataset
    - Verify dataset integrity (checksums, file counts)
    - _Estimated time: 4 hours (depends on download speed)_
    - _Requirements: 3.1_
  
  - [ ] 1.2 Create dataset loading and preprocessing scripts
    - Write data loader to read images/videos from all datasets
    - Implement train/validation split (80/20)
    - Balance real vs fake samples
    - _Estimated time: 3 hours_
    - _Requirements: 3.1_

- [ ] 2. Face detection and preprocessing pipeline
  - [ ] 2.1 Implement face detection (detector/preprocessing.py)
    - Integrate MTCNN or RetinaFace for face detection
    - Handle cases: no face detected, multiple faces (use largest)
    - Return bounding box coordinates
    - _Estimated time: 3 hours_
    - _Requirements: 3.1_
  
  - [ ] 2.2 Implement face alignment and normalization
    - Align faces to standard pose using facial landmarks
    - Resize to 224×224 pixels
    - Normalize pixel values to [0, 1]
    - _Estimated time: 2 hours_
    - _Requirements: 3.1_
  
  - [ ] 2.3 Implement data augmentation for training
    - Random rotation (±15 degrees)
    - Random horizontal flip
    - Random brightness/contrast adjustment
    - _Estimated time: 2 hours_
    - _Requirements: 3.1_

- [ ] 3. Model architecture and training
  - [ ] 3.1 Implement model architecture (detector/model.py)
    - Choose architecture: EfficientNet-B4 (recommended), Xception, or ViT
    - Load pre-trained weights from ImageNet
    - Modify final layer for binary classification (real vs fake)
    - _Estimated time: 3 hours_
    - _Requirements: 3.1, 3.2_
  
  - [ ] 3.2 Implement training loop (scripts/train_model.py)
    - Set up PyTorch training loop
    - Use AdamW optimizer with learning rate 1e-4
    - Binary cross-entropy loss
    - Batch size 32
    - Early stopping based on validation loss
    - Save best model checkpoint
    - _Estimated time: 4 hours_
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ] 3.3 Train model on combined datasets
    - Run training for 20-30 epochs
    - Monitor training/validation accuracy, loss, AUC-ROC
    - Save final model to models/deepfake_detector.pth
    - _Estimated time: 8-24 hours (GPU training time, mostly unattended)_
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ] 3.4 Evaluate model performance
    - Calculate accuracy, precision, recall, F1-score, AUC-ROC on validation set
    - Document performance metrics
    - _Estimated time: 2 hours_
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 4. Inference pipeline for images
  - [ ] 4.1 Implement image inference (detector/inference.py)
    - Load image from file path
    - Detect and extract face using preprocessing pipeline
    - Handle error if no face detected
    - Resize and normalize face
    - Convert to PyTorch tensor
    - Run model inference (forward pass)
    - Apply sigmoid to get probability
    - Apply threshold 0.5 (fake if > 0.5, real if ≤ 0.5)
    - Calculate confidence: abs(probability - 0.5) * 2
    - Return label ("real" or "fake") and confidence (0.0 to 1.0)
    - _Estimated time: 3 hours_
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.9_

- [ ] 5. Inference pipeline for videos
  - [ ] 5.1 Implement video frame extraction
    - Use OpenCV to load video
    - Extract frames at 1 FPS (or every 30th frame)
    - Handle different video formats (MP4, AVI, MOV)
    - _Estimated time: 2 hours_
    - _Requirements: 3.1, 3.10_
  
  - [ ] 5.2 Implement video inference with frame aggregation
    - For each extracted frame:
      - Detect and extract face
      - Run inference to get probability
    - Aggregate predictions: average probability across all frames
    - Apply threshold to average probability
    - Calculate confidence from average
    - Return label and confidence
    - _Estimated time: 3 hours_
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.10_
  
  - [ ] 5.3 Optimize video inference performance
    - Implement batch processing for video frames
    - Use GPU acceleration if available (CUDA)
    - Ensure processing completes within time limits (120s for 2-min video)
    - _Estimated time: 2 hours_
    - _Requirements: 3.10_

- [ ] 6. DeepfakeDetector class implementation
  - [ ] 6.1 Create DeepfakeDetector class (detector/model.py)
    - Implement __init__(model_path, device) to load model
    - Set model to eval mode
    - Initialize face detector (MTCNN)
    - _Estimated time: 1 hour_
    - _Requirements: 3.1_
  
  - [ ] 6.2 Implement detect() method
    - Accept file_path as input
    - Detect file type (image vs video) from extension or MIME type
    - Call image inference or video inference accordingly
    - Return DetectionResult dataclass with label and confidence
    - Raise ProcessingError if file cannot be processed
    - _Estimated time: 2 hours_
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.8_
  
  - [ ] 6.3 Create DetectionResult dataclass
    - Define dataclass with label (str) and confidence (float) fields
    - _Estimated time: 15 minutes_
    - _Requirements: 3.2, 3.4_

- [ ] 7. Thumbnail generation
  - [ ] 7.1 Implement thumbnail generation for images
    - Load image using PIL or OpenCV
    - Resize to 200×200 pixels (maintain aspect ratio, crop if needed)
    - Save as JPEG to output_path
    - _Estimated time: 1 hour_
    - _Requirements: 4.4_
  
  - [ ] 7.2 Implement thumbnail generation for videos
    - Extract first frame using OpenCV
    - Resize to 200×200 pixels
    - Save as JPEG to output_path
    - _Estimated time: 1 hour_
    - _Requirements: 4.5_
  
  - [ ] 7.3 Implement generate_thumbnail() method in DeepfakeDetector
    - Accept file_path and output_path
    - Detect file type (image vs video)
    - Call appropriate thumbnail generation function
    - Handle errors gracefully (return without raising if thumbnail fails)
    - _Estimated time: 1 hour_
    - _Requirements: 4.4, 4.5_

- [ ] 8. Error handling and edge cases
  - [ ] 8.1 Handle no face detected error
    - Raise ProcessingError with clear message
    - _Estimated time: 30 minutes_
    - _Requirements: 3.8_
  
  - [ ] 8.2 Handle multiple faces in image/video
    - Use largest face by bounding box area
    - _Estimated time: 30 minutes_
    - _Requirements: 3.1_
  
  - [ ] 8.3 Handle corrupted or unreadable files
    - Catch exceptions during file loading
    - Raise ProcessingError with descriptive message
    - _Estimated time: 1 hour_
    - _Requirements: 3.8_
  
  - [ ] 8.4 Handle GPU/CPU device selection
    - Auto-detect CUDA availability
    - Fall back to CPU if GPU not available
    - _Estimated time: 30 minutes_
    - _Requirements: 3.1_

- [ ] 9. Testing and validation
  - [ ] 9.1 Test inference on sample images
    - Test with known real images
    - Test with known fake images
    - Verify label and confidence are correct
    - _Estimated time: 1 hour_
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ] 9.2 Test inference on sample videos
    - Test with known real videos
    - Test with known fake videos
    - Verify processing time is within limits
    - _Estimated time: 2 hours_
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.10_
  
  - [ ] 9.3 Test thumbnail generation
    - Verify thumbnails are created for images and videos
    - Verify thumbnail dimensions (200×200)
    - _Estimated time: 1 hour_
    - _Requirements: 4.4, 4.5_
  
  - [ ] 9.4 Test error handling
    - Test with no face in image
    - Test with corrupted files
    - Test with unsupported formats
    - _Estimated time: 1 hour_
    - _Requirements: 3.8_

- [ ] 10. Performance optimization and documentation
  - [ ] 10.1 Optimize model inference speed
    - Profile inference time
    - Apply model quantization if needed
    - Ensure image inference < 10 seconds
    - Ensure video inference < 120 seconds for 2-min video
    - _Estimated time: 3 hours_
    - _Requirements: 3.9, 3.10_
  
  - [ ] 10.2 Document model performance and usage
    - Document accuracy, precision, recall, F1, AUC-ROC
    - Document inference time benchmarks
    - Create README for detector module
    - _Estimated time: 2 hours_
    - _Requirements: 3.1_

## Total Estimated Time: 60-76 hours (approximately 1.5-2 weeks, including training time)

## Testing Checklist

- [ ] Model trains successfully on combined datasets
- [ ] Model achieves reasonable accuracy (>80% on validation set)
- [ ] Face detection works on sample images
- [ ] Image inference returns label and confidence in correct format
- [ ] Video inference processes frames and aggregates results
- [ ] Confidence scores are always in range [0.0, 1.0]
- [ ] Labels are always "real" or "fake"
- [ ] Thumbnails are generated for images (200×200 JPEG)
- [ ] Thumbnails are generated for videos (first frame, 200×200 JPEG)
- [ ] Error handling works for no face, corrupted files
- [ ] Image inference completes within 10 seconds
- [ ] Video inference completes within 120 seconds for 2-min video
- [ ] GPU acceleration works if CUDA available
- [ ] CPU fallback works if GPU not available

## Notes

- Use PyTorch as the deep learning framework
- EfficientNet-B4 is recommended for good accuracy/speed balance
- Training requires GPU (8+ GB VRAM recommended)
- Inference can run on CPU but GPU is faster
- Face detection uses MTCNN (included in facenet-pytorch package)
- Model file (deepfake_detector.pth) should be ~75-100 MB
- Coordinate with Backend Developer on detector interface contract
- Ensure DetectionResult dataclass matches backend expectations
- Document any deviations from design document
