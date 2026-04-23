"""
All API route handlers for the deepfake detection platform.

Endpoints:
    POST   /api/upload                  — upload a file for detection
    GET    /api/jobs/{job_id}           — poll job status / get result
    GET    /api/history                 — paginated list of past results
    GET    /api/thumbnails/{job_id}     — serve thumbnail image
    GET    /api/reports/{job_id}/json   — download JSON report
    GET    /api/reports/{job_id}/pdf    — download PDF report
"""

import os
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import DetectionResult
from api.models import (
    UploadResponse,
    JobStatusResponse,
    DetectionResultModel,
    HistoryItem,
    HistoryResponse,
    JSONReport,
    StatusEnum,
    LabelEnum,
)
from api.file_utils import (
    validate_mime_type,
    validate_file_size,
    generate_job_id,
    save_upload,
    read_file_size,
)
from reports.json_generator import generate_json_report
from reports.pdf_generator import generate_pdf_report

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


# ------------------------------------------------------------------ #
# Background detection task
# ------------------------------------------------------------------ #

def run_detection(job_id: str, file_path: str, db: Session) -> None:
    """
    Background task: runs the ML detector and updates the database.
    Called after the upload response has already been sent to the client.
    """
    from models.detector import DeepfakeDetector  # ML team provides this

    try:
        detector = DeepfakeDetector()

        # Run inference — returns {"label": "real"|"fake", "confidence": 0.0-1.0}
        result = detector.detect(file_path)

        # Generate thumbnail
        thumbnail_path = detector.generate_thumbnail(file_path, job_id)

        # Update the database record
        record = db.query(DetectionResult).filter(DetectionResult.id == job_id).first()
        if record:
            record.status = "complete"
            record.label = result["label"]
            record.confidence = result["confidence"]
            record.thumbnail_path = thumbnail_path
            record.completed_at = datetime.now(timezone.utc)
            db.commit()

    except Exception as exc:
        logger.error("Detection failed for job %s: %s", job_id, exc, exc_info=True)
        record = db.query(DetectionResult).filter(DetectionResult.id == job_id).first()
        if record:
            record.status = "failed"
            record.error_message = str(exc)
            record.completed_at = datetime.now(timezone.utc)
            db.commit()


# ------------------------------------------------------------------ #
# Upload
# ------------------------------------------------------------------ #

@router.post("/upload", response_model=UploadResponse, status_code=202)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Accept an image or video file for deepfake detection.

    - Validates file type and size
    - Saves the file to disk
    - Creates a database record with status "processing"
    - Kicks off background detection
    - Returns a job_id to poll for results
    """
    # 1. Validate MIME type
    validate_mime_type(file)

    # 2. Validate file size (read size without loading into memory permanently)
    size = await read_file_size(file)
    validate_file_size(size)

    # 3. Generate unique job ID and save file
    job_id = generate_job_id()
    file_path, file_size = save_upload(file, job_id)

    # 4. Create database record
    record = DetectionResult(
        id=job_id,
        filename=file.filename or "unknown",
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type,
        status="processing",
    )
    db.add(record)
    db.commit()

    # 5. Queue background detection (non-blocking)
    background_tasks.add_task(run_detection, job_id, file_path, db)

    return UploadResponse(
        job_id=job_id,
        status=StatusEnum.processing,
        message="Your file has been received and is being analysed. Use the job_id to check progress.",
    )


# ------------------------------------------------------------------ #
# Job status
# ------------------------------------------------------------------ #

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Poll the status of a detection job.

    Returns:
        - status "processing" while the model is running
        - status "complete" with the result when done
        - status "failed" with an error message if something went wrong
    """
    record = db.query(DetectionResult).filter(DetectionResult.id == job_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Job not found.")

    if record.status == "processing":
        return JobStatusResponse(
            job_id=job_id,
            status=StatusEnum.processing,
            progress=None,
        )

    if record.status == "complete":
        result = DetectionResultModel(
            label=LabelEnum(record.label),
            confidence=record.confidence,
            filename=record.filename,
            timestamp=record.completed_at,
        )
        return JobStatusResponse(
            job_id=job_id,
            status=StatusEnum.complete,
            result=result,
        )

    # status == "failed"
    return JobStatusResponse(
        job_id=job_id,
        status=StatusEnum.failed,
        error=record.error_message or "An unknown error occurred during detection.",
    )


# ------------------------------------------------------------------ #
# History
# ------------------------------------------------------------------ #

@router.get("/history", response_model=HistoryResponse)
def get_history(
    page: int = 1,
    page_size: int = 10,
    label: str = None,
    search: str = None,
    db: Session = Depends(get_db),
):
    """
    Return a paginated list of completed detections, newest first.

    Query params:
        page      — page number (default 1)
        page_size — results per page (default 10, max 20)
        label     — filter by "real" or "fake" (optional)
        search    — filter by filename substring (optional)
    """
    # Clamp page_size to max 20
    page_size = min(page_size, 20)
    if page < 1:
        page = 1

    base_query = (
        db.query(DetectionResult)
        .filter(DetectionResult.status == "complete")
        .order_by(DetectionResult.created_at.desc())
    )

    # Optional label filter
    if label in ("real", "fake"):
        base_query = base_query.filter(DetectionResult.label == label)

    # Optional filename search
    if search:
        base_query = base_query.filter(
            DetectionResult.filename.ilike(f"%{search}%")
        )

    total = base_query.count()
    total_pages = max(1, -(-total // page_size))  # ceiling division

    records = base_query.offset((page - 1) * page_size).limit(page_size).all()

    results = [
        {
            "job_id": r.id,
            "filename": r.filename,
            "timestamp": r.created_at.isoformat() if r.created_at else None,
            "label": r.label,
            "confidence": r.confidence,
        }
        for r in records
    ]

    return {
        "results": results,
        "total": total,
        "page": page,
        "pages": total_pages,
    }


# ------------------------------------------------------------------ #
# Thumbnails
# ------------------------------------------------------------------ #

@router.get("/thumbnails/{job_id}")
def get_thumbnail(job_id: str, db: Session = Depends(get_db)):
    """Serve the thumbnail image for a completed detection job."""
    record = db.query(DetectionResult).filter(DetectionResult.id == job_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Job not found.")
    if not record.thumbnail_path:
        raise HTTPException(status_code=404, detail="Thumbnail not available for this job.")
    if not os.path.exists(record.thumbnail_path):
        raise HTTPException(status_code=404, detail="Thumbnail file is missing from disk.")

    return FileResponse(record.thumbnail_path, media_type="image/jpeg")


# ------------------------------------------------------------------ #
# Reports
# ------------------------------------------------------------------ #

@router.get("/reports/{job_id}/json")
def download_json_report(job_id: str, db: Session = Depends(get_db)):
    """Download a JSON report for a completed detection job."""
    record = db.query(DetectionResult).filter(DetectionResult.id == job_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Job not found.")
    if record.status != "complete":
        raise HTTPException(
            status_code=400,
            detail="Report is only available for completed jobs.",
        )

    report = generate_json_report(record)
    return JSONResponse(content=report)


# ------------------------------------------------------------------ #
# Dashboard stats
# ------------------------------------------------------------------ #

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """
    Return summary statistics for the dashboard.
    Counts total, real, fake, processing, and failed jobs.
    Also returns the 5 most recent completed detections.
    """
    from sqlalchemy import func

    total      = db.query(DetectionResult).count()
    complete   = db.query(DetectionResult).filter(DetectionResult.status == "complete").count()
    processing = db.query(DetectionResult).filter(DetectionResult.status == "processing").count()
    failed     = db.query(DetectionResult).filter(DetectionResult.status == "failed").count()
    real_count = db.query(DetectionResult).filter(
        DetectionResult.status == "complete", DetectionResult.label == "real"
    ).count()
    fake_count = db.query(DetectionResult).filter(
        DetectionResult.status == "complete", DetectionResult.label == "fake"
    ).count()

    avg_confidence = (
        db.query(func.avg(DetectionResult.confidence))
        .filter(DetectionResult.status == "complete")
        .scalar()
    )

    recent = (
        db.query(DetectionResult)
        .filter(DetectionResult.status == "complete")
        .order_by(DetectionResult.completed_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total": total,
        "complete": complete,
        "processing": processing,
        "failed": failed,
        "real": real_count,
        "fake": fake_count,
        "avg_confidence": round(avg_confidence * 100, 1) if avg_confidence else 0,
        "recent": [
            {
                "job_id": r.id,
                "filename": r.filename,
                "label": r.label,
                "confidence": r.confidence,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in recent
        ],
    }


# ------------------------------------------------------------------ #
# Reports
# ------------------------------------------------------------------ #

@router.get("/reports/{job_id}/pdf")
def download_pdf_report(job_id: str, db: Session = Depends(get_db)):
    """Download a PDF report for a completed detection job."""
    record = db.query(DetectionResult).filter(DetectionResult.id == job_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Job not found.")
    if record.status != "complete":
        raise HTTPException(
            status_code=400,
            detail="Report is only available for completed jobs.",
        )

    pdf_path = generate_pdf_report(record)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="report_{job_id[:8]}.pdf"'
        },
    )
