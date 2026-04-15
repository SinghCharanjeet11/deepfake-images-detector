"""
Test script to verify the trained model works correctly.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector.model import DeepfakeDetector
import glob

# Paths
MODEL_PATH = "models/deepfake_detector.pth"
TEST_DIR = "datasets/archive/real_vs_fake/real-vs-fake/test"

def test_model():
    """Test the model on a few sample images."""
    
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model not found at {MODEL_PATH}")
        print("Please train the model first using: python scripts/train_model.py")
        return
    
    # Load detector
    print("Loading model...")
    detector = DeepfakeDetector(MODEL_PATH, device="cpu")
    
    # Test on a few real images
    print("\n--- Testing on REAL images ---")
    real_images = glob.glob(os.path.join(TEST_DIR, "real", "*.jpg"))[:5]
    for img_path in real_images:
        result = detector.detect(img_path)
        print(f"{os.path.basename(img_path)}: {result.label} (confidence: {result.confidence:.2f})")
    
    # Test on a few fake images
    print("\n--- Testing on FAKE images ---")
    fake_images = glob.glob(os.path.join(TEST_DIR, "fake", "*.jpg"))[:5]
    for img_path in fake_images:
        result = detector.detect(img_path)
        print(f"{os.path.basename(img_path)}: {result.label} (confidence: {result.confidence:.2f})")
    
    print("\n✓ Inference test complete!")

if __name__ == "__main__":
    test_model()
