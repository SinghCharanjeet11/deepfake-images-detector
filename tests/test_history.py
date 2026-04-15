"""
Tests for GET /api/history endpoint.
"""

from datetime import datetime, timezone
from database.models import DetectionResult


def _insert_complete_record(db, job_id="test-job-1", label="real", confidence=0.9):
    record = DetectionResult(
        id=job_id,
        filename="test.jpg",
        file_path="uploads/test.jpg",
        file_size=1024,
        mime_type="image/jpeg",
        status="complete",
        label=label,
        confidence=confidence,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()
    return record


def test_history_empty(client):
    """History should return an empty list when there are no completed jobs."""
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert data["results"] == []
    assert data["total"] == 0


def test_history_returns_completed_jobs(client, db):
    """Completed jobs should appear in history."""
    _insert_complete_record(db, job_id="job-1")
    _insert_complete_record(db, job_id="job-2", label="fake", confidence=0.75)

    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["results"]) == 2


def test_history_excludes_processing_jobs(client, db):
    """Jobs still processing should NOT appear in history."""
    record = DetectionResult(
        id="processing-job",
        filename="test.jpg",
        file_path="uploads/test.jpg",
        file_size=1024,
        mime_type="image/jpeg",
        status="processing",
    )
    db.add(record)
    db.commit()

    response = client.get("/api/history")
    assert response.json()["total"] == 0


def test_history_pagination(client, db):
    """Pagination should correctly split results across pages."""
    for i in range(5):
        _insert_complete_record(db, job_id=f"job-{i}")

    page1 = client.get("/api/history?page=1&limit=3").json()
    page2 = client.get("/api/history?page=2&limit=3").json()

    assert len(page1["results"]) == 3
    assert len(page2["results"]) == 2
    assert page1["pages"] == 2
