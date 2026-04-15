"""
Pydantic models for API request/response validation.
These define the exact shape of data going in and out of every endpoint.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class LabelEnum(str, Enum):
    real = "real"
    fake = "fake"


class StatusEnum(str, Enum):
    processing = "processing"
    complete = "complete"
    failed = "failed"


# ------------------------------------------------------------------ #
# Upload
# ------------------------------------------------------------------ #

class UploadResponse(BaseModel):
    """Returned immediately after a file is accepted for processing."""
    job_id: str
    status: StatusEnum
    message: str


# ------------------------------------------------------------------ #
# Detection result
# ------------------------------------------------------------------ #

class DetectionResultModel(BaseModel):
    """The actual prediction output once processing is complete."""
    label: LabelEnum
    confidence: float = Field(..., ge=0.0, le=1.0)
    filename: str
    timestamp: datetime

    @field_validator("confidence")
    @classmethod
    def round_confidence(cls, v: float) -> float:
        return round(v, 4)


# ------------------------------------------------------------------ #
# Job status (polling endpoint)
# ------------------------------------------------------------------ #

class JobStatusResponse(BaseModel):
    """
    Returned by GET /api/jobs/{job_id}.
    - While processing: result is None, error is None
    - On success:       result is filled, error is None
    - On failure:       result is None,  error is filled
    """
    job_id: str
    status: StatusEnum
    progress: Optional[int] = Field(
        default=None,
        description="Estimated progress 0-100 (optional, may be None)",
    )
    result: Optional[DetectionResultModel] = None
    error: Optional[str] = None


# ------------------------------------------------------------------ #
# History
# ------------------------------------------------------------------ #

class HistoryItem(BaseModel):
    """One row in the history list."""
    job_id: str
    filename: str
    timestamp: datetime
    label: Optional[LabelEnum] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    thumbnail_url: Optional[str] = None


class HistoryResponse(BaseModel):
    """Paginated list of completed detections."""
    results: List[HistoryItem]
    total: int
    page: int
    pages: int


# ------------------------------------------------------------------ #
# Reports
# ------------------------------------------------------------------ #

class JSONReport(BaseModel):
    """Structured data for the JSON export endpoint."""
    job_id: str
    filename: str
    timestamp: datetime
    label: LabelEnum
    confidence: float = Field(..., ge=0.0, le=1.0)
    confidence_percent: str  # e.g. "91.23%"

    @classmethod
    def from_detection(
        cls,
        job_id: str,
        filename: str,
        timestamp: datetime,
        label: str,
        confidence: float,
    ) -> "JSONReport":
        return cls(
            job_id=job_id,
            filename=filename,
            timestamp=timestamp,
            label=LabelEnum(label),
            confidence=confidence,
            confidence_percent=f"{confidence * 100:.2f}%",
        )
