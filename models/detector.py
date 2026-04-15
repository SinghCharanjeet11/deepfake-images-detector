"""
DeepfakeDetector — stub interface for the ML team.

Charanjeet / Chirag: replace the body of detect() and generate_thumbnail()
with the real EfficientNet / Xception + Grad-CAM implementation.

The backend calls ONLY these two methods:
    detector.detect(file_path)          → {"label": str, "confidence": float}
    detector.generate_thumbnail(...)    → str (path to saved thumbnail)

Do NOT change the method signatures or return types — the backend depends on them.
"""

import os
import shutil
from config import settings


class DeepfakeDetector:
    """
    Wraps the ML model for inference.

    Usage:
        detector = DeepfakeDetector()
        result = detector.detect("uploads/2025-04/abc123.jpg")
        # → {"label": "real", "confidence": 0.91}
    """

    def __init__(self, weights_path: str = None):
        """
        Load model weights.

        Args:
            weights_path: Path to .pth / .h5 weights file.
                          Defaults to MODEL_WEIGHTS_PATH from config.
        """
        self.weights_path = weights_path or settings.MODEL_WEIGHTS_PATH
        # TODO (ML team): load EfficientNet / Xception weights here
        # Example:
        #   self.model = torch.load(self.weights_path)
        #   self.model.eval()

    def detect(self, file_path: str) -> dict:
        """
        Run inference on an image or video file.

        Args:
            file_path: Absolute or relative path to the uploaded file.

        Returns:
            {
                "label":      "real" | "fake",
                "confidence": float between 0.0 and 1.0
            }

        Raises:
            FileNotFoundError: if file_path does not exist.
            RuntimeError:      if inference fails.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # ------------------------------------------------------------------ #
        # TODO (ML team): replace this stub with real inference
        #
        # Steps:
        #   1. Load and preprocess image (resize 224x224, normalize [0,1])
        #   2. Run forward pass through EfficientNet / Xception
        #   3. Apply Softmax → get probabilities for [real, ai-generated, manipulated]
        #   4. Return the winning label and its confidence score
        #
        # Example skeleton:
        #   image = preprocess(file_path)          # → tensor [1, 3, 224, 224]
        #   with torch.no_grad():
        #       logits = self.model(image)
        #   probs = torch.softmax(logits, dim=1)
        #   label_idx = probs.argmax().item()
        #   labels = ["real", "ai-generated", "manipulated"]
        #   return {
        #       "label": labels[label_idx],
        #       "confidence": probs[0][label_idx].item()
        #   }
        # ------------------------------------------------------------------ #

        # Stub: always returns "real" with 0.5 confidence until ML is integrated
        return {"label": "real", "confidence": 0.5}

    def generate_thumbnail(self, file_path: str, job_id: str) -> str:
        """
        Generate a thumbnail image for display in the history panel.

        Args:
            file_path: Path to the original uploaded file.
            job_id:    The job UUID (used to name the thumbnail file).

        Returns:
            Path to the saved thumbnail file (JPEG).

        Raises:
            RuntimeError: if thumbnail generation fails.
        """
        os.makedirs(settings.THUMBNAIL_DIR, exist_ok=True)
        thumbnail_path = os.path.join(settings.THUMBNAIL_DIR, f"{job_id}_thumb.jpg")

        # ------------------------------------------------------------------ #
        # TODO (ML team): replace with real thumbnail generation
        #
        # Example using OpenCV:
        #   import cv2
        #   img = cv2.imread(file_path)
        #   img_resized = cv2.resize(img, (256, 256))
        #   cv2.imwrite(thumbnail_path, img_resized)
        # ------------------------------------------------------------------ #

        # Stub: copy the original file as the thumbnail
        shutil.copy2(file_path, thumbnail_path)
        return thumbnail_path
