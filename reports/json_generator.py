"""
JSON report generator.
Converts a DetectionResult database record into a plain dict
suitable for returning as an API response or saving to a file.
"""

from typing import Any, Dict
from database.models import DetectionResult


def generate_json_report(record: DetectionResult) -> Dict[str, Any]:
    """
    Build a JSON-serialisable report dict from a completed DetectionResult.

    Args:
        record: A DetectionResult ORM object with status == "complete"

    Returns:
        A plain dictionary ready to be returned via JSONResponse.
    """
    confidence = record.confidence or 0.0

    return {
        "job_id": record.id,
        "filename": record.filename,
        "timestamp": record.completed_at.isoformat() if record.completed_at else None,
        "label": record.label,
        "confidence": round(confidence, 4),
        "confidence_percent": f"{confidence * 100:.2f}%",
        "file_size_bytes": record.file_size,
        "mime_type": record.mime_type,
    }
