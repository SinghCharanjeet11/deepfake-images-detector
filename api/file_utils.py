"""
File validation and storage utilities.
Handles MIME type checking, size limits, UUID naming, and directory layout.
"""

import os
import uuid
import shutil
from datetime import datetime, timezone
from fastapi import UploadFile, HTTPException

from config import settings


def validate_mime_type(file: UploadFile) -> None:
    """
    Reject files whose content type is not in the allowed list.
    Raises HTTP 400 if the type is not allowed.
    """
    allowed = settings.get_allowed_mime_types()
    if file.content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File type '{file.content_type}' is not supported. "
                f"Please upload one of: {', '.join(allowed)}."
            ),
        )


def validate_file_size(size_bytes: int) -> None:
    """
    Reject files larger than MAX_FILE_SIZE.
    Raises HTTP 400 if the file is too large.
    """
    max_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
    if size_bytes > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File is too large ({size_bytes / (1024*1024):.1f} MB). "
                f"Maximum allowed size is {max_mb:.0f} MB."
            ),
        )


def generate_job_id() -> str:
    """Return a new UUID4 string to use as the job/file identifier."""
    return str(uuid.uuid4())


def get_upload_dir_for_today() -> str:
    """
    Return the month-based upload subdirectory path (YYYY-MM).
    Creates the directory if it does not exist.

    Example: uploads/2025-04/
    """
    month_folder = datetime.now(timezone.utc).strftime("%Y-%m")
    path = os.path.join(settings.UPLOAD_DIR, month_folder)
    os.makedirs(path, exist_ok=True)
    return path


def save_upload(file: UploadFile, job_id: str) -> tuple[str, int]:
    """
    Save an uploaded file to disk.

    Returns:
        (file_path, file_size_bytes)

    The file is stored as:
        uploads/YYYY-MM/<job_id>.<original_extension>
    """
    # Preserve the original file extension
    _, ext = os.path.splitext(file.filename or "")
    dest_dir = get_upload_dir_for_today()
    dest_path = os.path.join(dest_dir, f"{job_id}{ext}")

    # Reset stream position in case it was partially read during validation
    file.file.seek(0)

    with open(dest_path, "wb") as out:
        shutil.copyfileobj(file.file, out)

    file_size = os.path.getsize(dest_path)
    return dest_path, file_size


async def read_file_size(file: UploadFile) -> int:
    """
    Read the entire file into memory to determine its size, then reset
    the stream so it can be saved afterwards.

    Note: For very large files this is memory-intensive. A streaming
    approach can replace this if needed.
    """
    content = await file.read()
    await file.seek(0)
    return len(content)
