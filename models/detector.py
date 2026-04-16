"""
DeepfakeDetector — ML inference wrapper.
"""

import os
from config import settings


class DeepfakeDetector:
    """
    Wraps the ML model for inference.
    """

    def __init__(self, weights_path: str = None):
        """Load model weights."""
        from detector.model import DeepfakeDetector as MLDetector
        
        self.weights_path = weights_path or settings.MODEL_WEIGHTS_PATH
        self.detector = MLDetector(self.weights_path, device="cpu")

    def detect(self, file_path: str) -> dict:
        """
        Run inference on an image file.

        Returns:
            {
                "label":      "real" | "fake",
                "confidence": float between 0.0 and 1.0
            }
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Use the real ML detector
        result = self.detector.detect(file_path)
        
        return {
            "label": result.label,
            "confidence": result.confidence
        }

    def generate_thumbnail(self, file_path: str, job_id: str) -> str:
        """
        Generate a thumbnail image.

        Returns:
            Path to the saved thumbnail file (JPEG).
        """
        os.makedirs(settings.THUMBNAIL_DIR, exist_ok=True)
        thumbnail_path = os.path.join(settings.THUMBNAIL_DIR, f"{job_id}_thumb.jpg")

        # Use the detector's thumbnail generation
        self.detector.generate_thumbnail(file_path, thumbnail_path)
        
        return thumbnail_path
