"""
Tests for GET /api/jobs/{job_id} endpoint.
"""

from datetime import datetime, timezone
from database.models import DetectionResult


def test_job_not_found(client):
    """Non-existent job_id should return 404."""
    response = client.get("/api/jobs/does-not-exist")
    assert response.status_code == 404


def test_job_processing_status(client, db):
    """A job still processing should return status 'processing'."""
    record = DetectionResult(
        id="proc-job",
        filename="test.jpg",
        file_path="uploads/test.jpg",
        file_size=1024,
        mime_type="image/jpeg",
        status="processing",
    )
    db.add(record)
    db.commit()

    response = client.get("/api/jobs/proc-job")
    assert response.status_code == 200
    assert response.json()["status"] == "processing"
    assert response.json()["result"] is None


def test_job_complete_status(client, db):
    """A completed job should return status 'complete' with result."""
    record = DetectionResult(
        id="done-job",
        filename="test.jpg",
        file_path="uploads/test.jpg",
        file_size=1024,
        mime_type="image/jpeg",
        status="complete",
        label="fake",
        confidence=0.87,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()

    response = client.get("/api/jobs/done-job")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "complete"
    assert data["result"]["label"] == "fake"
    assert data["result"]["confidence"] == 0.87


def test_job_failed_status(client, db):
    """A failed job should return status 'failed' with an error message."""
    record = DetectionResult(
        id="fail-job",
        filename="test.jpg",
        file_path="uploads/test.jpg",
        file_size=1024,
        mime_type="image/jpeg",
        status="failed",
        error_message="Model weights not found.",
        completed_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()

    response = client.get("/api/jobs/fail-job")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert "Model weights" in data["error"]
