"""
SQLAlchemy ORM models for the deepfake detection platform.
All detection results are stored in a single table.
"""

from sqlalchemy import Column, String, Float, DateTime, Integer, Index
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class DetectionResult(Base):
    """
    Stores every image/video upload and its detection outcome.

    Lifecycle:
        upload  → status = "processing"
        success → status = "complete",  label + confidence filled in
        failure → status = "failed",    error_message filled in
    """

    __tablename__ = "detection_results"

    # Primary key — UUID string generated at upload time
    id = Column(String, primary_key=True, index=True)

    # File metadata
    filename = Column(String, nullable=False)          # original filename
    file_path = Column(String, nullable=False)         # path on disk
    file_size = Column(Integer, nullable=False)        # bytes
    mime_type = Column(String, nullable=False)         # e.g. image/jpeg

    # Processing state
    status = Column(String, nullable=False, default="processing")
    # status values: "processing" | "complete" | "failed"

    # Detection output (NULL until processing is complete)
    label = Column(String, nullable=True)              # "real" | "fake"
    confidence = Column(Float, nullable=True)          # 0.0 – 1.0

    # Error info (NULL unless status = "failed")
    error_message = Column(String, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Thumbnail generated after detection
    thumbnail_path = Column(String, nullable=True)

    # ------------------------------------------------------------------ #
    # Indexes for the two most common query patterns
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_detection_results_created_at", "created_at"),
        Index("ix_detection_results_status", "status"),
    )

    def __repr__(self) -> str:
        return (
            f"<DetectionResult id={self.id!r} "
            f"status={self.status!r} label={self.label!r}>"
        )
