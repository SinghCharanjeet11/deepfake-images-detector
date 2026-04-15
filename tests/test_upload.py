"""
Tests for POST /api/upload endpoint.
"""

import io
import pytest
from fastapi.testclient import TestClient


def make_image_file(filename="test.jpg", content=b"fake-image-bytes"):
    """Helper to create a fake upload file."""
    return ("file", (filename, io.BytesIO(content), "image/jpeg"))


def test_upload_valid_image(client: TestClient):
    """A valid JPEG upload should return 202 with a job_id."""
    response = client.post(
        "/api/upload",
        files=[make_image_file()],
    )
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "processing"


def test_upload_invalid_mime_type(client: TestClient):
    """A non-image file should be rejected with 400."""
    response = client.post(
        "/api/upload",
        files=[("file", ("test.txt", io.BytesIO(b"hello"), "text/plain"))],
    )
    assert response.status_code == 400
    assert "not supported" in response.json()["detail"].lower()


def test_upload_png(client: TestClient):
    """PNG files should also be accepted."""
    response = client.post(
        "/api/upload",
        files=[("file", ("test.png", io.BytesIO(b"fake-png"), "image/png"))],
    )
    assert response.status_code == 202


def test_upload_returns_unique_job_ids(client: TestClient):
    """Each upload should get a different job_id."""
    r1 = client.post("/api/upload", files=[make_image_file()])
    r2 = client.post("/api/upload", files=[make_image_file()])
    assert r1.json()["job_id"] != r2.json()["job_id"]
