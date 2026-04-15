# Deepfake Detection Platform — Backend

FastAPI backend for detecting AI-generated and manipulated images.

## Quick Start

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.template .env

# 4. Initialise the database
python scripts/init_db.py

# 5. Start the server
uvicorn main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

## Project Structure

```
├── main.py                  # FastAPI app entry point
├── config.py                # Environment variable config
├── requirements.txt
├── .env.template            # Copy to .env and fill in values
│
├── api/
│   ├── routes.py            # All API endpoints
│   ├── models.py            # Pydantic request/response models
│   └── file_utils.py        # File validation and storage helpers
│
├── database/
│   ├── models.py            # SQLAlchemy ORM models
│   └── connection.py        # DB engine, session, get_db()
│
├── models/
│   └── detector.py          # ML detector stub (ML team fills this in)
│
├── reports/
│   ├── json_generator.py    # JSON report generation
│   └── pdf_generator.py     # PDF report generation (ReportLab)
│
├── scripts/
│   ├── init_db.py           # Create/reset database tables
│   └── cleanup_old_files.py # Delete files older than N days
│
├── tests/
│   ├── conftest.py          # Shared pytest fixtures
│   ├── test_upload.py
│   ├── test_jobs.py
│   └── test_history.py
│
├── uploads/                 # Uploaded files (git-ignored)
├── thumbnails/              # Generated thumbnails (git-ignored)
└── database/                # SQLite .db file (git-ignored)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload image for detection |
| GET | `/api/jobs/{job_id}` | Poll job status / get result |
| GET | `/api/history` | Paginated list of past results |
| GET | `/api/thumbnails/{job_id}` | Serve thumbnail image |
| GET | `/api/reports/{job_id}/json` | Download JSON report |
| GET | `/api/reports/{job_id}/pdf` | Download PDF report |
| GET | `/health` | Server health check |

## Running Tests

```bash
pytest tests/ -v
```

## For the ML Team (Charanjeet / Chirag)

Open `models/detector.py` and implement:
- `detect(file_path)` → `{"label": "real"|"fake", "confidence": 0.0-1.0}`
- `generate_thumbnail(file_path, job_id)` → path to saved thumbnail

**Do not change the method signatures** — the backend depends on them.
