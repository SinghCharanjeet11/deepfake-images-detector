"""
Application configuration loaded from environment variables.
Copy .env.template to .env and set your values before running.
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./database/deepfake_detector.db"

    # File storage
    UPLOAD_DIR: str = "uploads"
    THUMBNAIL_DIR: str = "thumbnails"

    # File size limit (default 500 MB)
    MAX_FILE_SIZE: int = 524_288_000

    # Allowed MIME types
    ALLOWED_MIME_TYPES: str = (
        "image/jpeg,image/png,video/mp4,video/avi,video/quicktime"
    )

    # ML model weights path
    MODEL_WEIGHTS_PATH: str = "models/deepfake_detector.pth"

    @field_validator("ALLOWED_MIME_TYPES", mode="before")
    @classmethod
    def parse_mime_types(cls, v):
        # Accept either a comma-separated string or a list
        if isinstance(v, list):
            return ",".join(v)
        return v

    def get_allowed_mime_types(self) -> List[str]:
        return [m.strip() for m in self.ALLOWED_MIME_TYPES.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Single shared instance used across the app
settings = Settings()
