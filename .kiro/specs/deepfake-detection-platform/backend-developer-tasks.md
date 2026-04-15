# Backend Developer Tasks: Deepfake Detection Platform

## Role Overview

As the Backend Developer, you are responsible for implementing the FastAPI REST API, database layer, file handling, and report generation. You coordinate between the frontend and ML detector, ensuring data flows correctly through the system.

## Dependencies

- ML Detector interface (DeepfakeDetector class) from ML Engineer
- Frontend requirements for API response formats

## Tasks

- [ ] 1. Project setup and infrastructure
  - [ ] 1.1 Create project directory structure
    - Create directories: api/, database/, reports/, uploads/, thumbnails/, models/, scripts/, tests/
    - _Estimated time: 30 minutes_
    - _Requirements: 6.1, 6.4_
  
  - [ ] 1.2 Create requirements.txt with dependencies
    - FastAPI, uvicorn, python-multipart, SQLAlchemy, Pydantic
    - ReportLab for PDF generation
    - Other utilities (python-dotenv, etc.)
    - _Estimated time: 30 minutes_
    - _Requirements: All_
  
  - [ ] 1.3 Create .env template and configuration module
    - Define environment variables (DATABASE_URL, UPLOAD_DIR, etc.)
    - Create config.py to load environment variables
    - _Estimated time: 1 hour_
    - _Requirements: 6.1, 6.4_
  
  - [ ] 1.4 Create .gitignore file
    - Ignore uploads/, thumbnails/, models/, database/, venv/, .env
    - _Estimated time: 15 minutes_
    - _Requirements: 6.4_

- [ ] 2. Database layer implementation
  - [ ] 2.1 Create SQLAlchemy models (database/models.py)
    - Define DetectionResult model with all fields:
      - id (TEXT PRIMARY KEY)
      - filename, file_path, file_size, mime_type
      - status (processing/complete/failed)
      - label (real/fake), confidence (0.0-1.0)
      - error_message
      - created_at, completed_at
      - thumbnail_path
    - Add indexes for created_at DESC and status
    - _Estimated time: 2 hours_
    - _Requirements: 3.5, 4.1_
  
  - [ ] 2.2 Implement database connection (database/connection.py)
    - Create SQLite engine and session factory
    - Implement get_db() dependency for FastAPI
    - _Estimated time: 1 hour_
    - _Requirements: 3.5_
  
  - [ ] 2.3 Create database initialization script (scripts/init_db.py)
    - Create all tables and indexes
    - Can be run to reset database if needed
    - _Estimated time: 1 hour_
    - _Requirements: 3.5_

- [ ] 3. Pydantic models for API validation
  - [ ] 3.1 Create request/response models (api/models.py)
    - UploadResponse (job_id, status, message)
    - DetectionResultModel (label, confidence, filename, timestamp)
    - JobStatusResponse (job_id, status, progress, result, error)
    - HistoryItem (job_id, filename, timestamp, label, confidence, thumbnail_url)
    - HistoryResponse (results, total, page, pages)
    - JSONReport (filename, timestamp, label, confidence)
    - Add field validation (confidence 0.0-1.0, label enum)
    - _Estimated time: 2 hours_
    - _Requirements: 3.2, 3.4, 4.2, 4.3, 5.3_

- [ ] 4. File handling and validation
  - [ ] 4.1 Implement file validation utilities (api/file_utils.py)
    - Validate MIME type (image/jpeg, image/png, video/mp4, video/avi, video/quicktime)
    - Validate file size (max 500 MB)
    - Generate unique file identifiers (UUID)
    - Create month-based directory structure (YYYY-MM)
    - _Estimated time: 2 hours_
    - _Requirements: 2.1, 2.2, 2.3, 2.5, 2.6, 6.1, 6.2, 6.3_
  
  - [ ] 4.2 Implement file storage functions
    - Save uploaded file to uploads/YYYY-MM/ with UUID name
    - Ensure directory exists before saving
    - _Estimated time: 1 hour_
    - _Requirements: 6.1, 6.4_

- [ ] 5. FastAPI application setup
  - [ ] 5.1 Create FastAPI app (main.py)
    - Initialize FastAPI application
    - Configure static file serving for HTML/CSS/JS
    - Set up CORS if needed (localhost only, so minimal)
    - Add startup event to initialize database
    - _Estimated time: 2 hours_
    - _Requirements: 2.7_

- [ ] 6. Upload and detection endpoints
  - [ ] 6.1 Implement POST /api/upload endpoint (api/routes.py)
    - Accept multipart/form-data file upload
    - Validate file format using MIME type check
    - Validate file size (reject if > 500 MB)
    - Generate unique job_id (UUID)
    - Save file to uploads directory
    - Create detection_results record with status "processing"
    - Trigger background task for detection
    - Return UploadResponse with job_id
    - Handle errors (invalid format, size exceeded)
    - _Estimated time: 4 hours_
    - _Requirements: 2.1, 2.2, 2.3, 2.5, 2.6, 2.7, 2.8_
    - _Dependencies: ML Detector interface_
  
  - [ ] 6.2 Implement background task for detection processing
    - Create async background task function
    - Call detector.detect(file_path) to get result
    - Update detection_results record with label and confidence
    - Set status to "complete" and completed_at timestamp
    - Call detector.generate_thumbnail() for thumbnail
    - Handle errors: catch exceptions, set status to "failed", store error_message
    - _Estimated time: 3 hours_
    - _Requirements: 3.1, 3.5, 3.6, 3.7, 3.8_
    - _Dependencies: ML Detector detect() and generate_thumbnail() methods_
  
  - [ ] 6.3 Implement GET /api/jobs/{job_id} endpoint
    - Query detection_results by job_id
    - Return 404 if job not found
    - If status is "processing": return JobStatusResponse with status and progress (optional)
    - If status is "complete": return JobStatusResponse with result details
    - If status is "failed": return JobStatusResponse with error message
    - _Estimated time: 2 hours_
    - _Requirements: 3.6, 3.7, 3.8_

- [ ] 7. History and thumbnails endpoints
  - [ ] 7.1 Implement GET /api/history endpoint
    - Accept query parameters: page (default 1), limit (default 20, max 20)
    - Query detection_results where status = "complete"
    - Order by created_at DESC
    - Implement pagination (offset = (page-1) * limit)
    - Calculate total results and total pages
    - Return HistoryResponse with results array, total, page, pages
    - Each result includes thumbnail_url as /api/thumbnails/{job_id}
    - _Estimated time: 3 hours_
    - _Requirements: 4.1, 4.2, 4.3, 4.7_
  
  - [ ] 7.2 Implement GET /api/thumbnails/{job_id} endpoint
    - Query detection_results to get thumbnail_path
    - Return 404 if job not found or thumbnail_path is NULL
    - Serve thumbnail image file with Content-Type: image/jpeg
    - _Estimated time: 1 hour_
    - _Requirements: 4.4, 4.5_

- [ ] 8. Report generation
  - [ ] 8.1 Implement JSON report generation (reports/json_generator.py)
    - Create function to generate JSON report from detection result
    - Return JSONReport model with filename, timestamp, label, confidence
    - _Estimated time: 1 hour_
    - _Requirements: 5.1, 5.3, 5.4_
  
  - [ ] 8.2 Implement PDF report generation (reports/pdf_generator.py)
    - Use ReportLab to create PDF document
    - Include filename, timestamp, label, confidence score
    - Add platform watermark or header
    - Format confidence as percentage
    - _Estimated time: 3 hours_
    - _Requirements: 5.1, 5.2_
  
  - [ ] 8.3 Implement GET /api/reports/{job_id}/json endpoint
    - Query detection_results by job_id
    - Return 404 if not found
    - Return 400 if status is not "complete"
    - Generate and return JSON report
    - Set Content-Type: application/json
    - _Estimated time: 1 hour_
    - _Requirements: 5.1, 5.3_
  
  - [ ] 8.4 Implement GET /api/reports/{job_id}/pdf endpoint
    - Query detection_results by job_id
    - Return 404 if not found
    - Return 400 if status is not "complete"
    - Generate PDF report
    - Return PDF with Content-Type: application/pdf and Content-Disposition header
    - _Estimated time: 1 hour_
    - _Requirements: 5.1, 5.2_

- [ ] 9. File cleanup automation
  - [ ] 9.1 Create cleanup script (scripts/cleanup_old_files.py)
    - Query detection_results where created_at < 30 days ago
    - Delete associated files from uploads/ and thumbnails/
    - Keep detection_results records (only delete files)
    - Add command-line argument for days threshold
    - _Estimated time: 2 hours_
    - _Requirements: 6.5, 6.6_

- [ ] 10. Error handling and validation
  - [ ] 10.1 Add global exception handlers
    - Handle 404, 400, 500 errors with consistent JSON responses
    - Log errors appropriately
    - _Estimated time: 1 hour_
    - _Requirements: 8.1, 8.4_
  
  - [ ] 10.2 Add request validation error handlers
    - Return clear error messages for validation failures
    - Format errors in plain language
    - _Estimated time: 1 hour_
    - _Requirements: 8.1, 8.4_

- [ ] 11. Integration testing and bug fixes
  - [ ] 11.1 Test all endpoints with sample data
    - Upload valid and invalid files
    - Test detection flow end-to-end
    - Test history pagination
    - Test report generation
    - _Estimated time: 3 hours_
    - _Requirements: All_
  
  - [ ] 11.2 Fix any bugs discovered during testing
    - _Estimated time: 2 hours_
    - _Requirements: All_

## Total Estimated Time: 42 hours (approximately 1 week)

## Testing Checklist

- [ ] POST /api/upload accepts valid files and returns job_id
- [ ] POST /api/upload rejects invalid formats with 400 error
- [ ] POST /api/upload rejects files > 500 MB with 400 error
- [ ] GET /api/jobs/{job_id} returns correct status for processing jobs
- [ ] GET /api/jobs/{job_id} returns result for completed jobs
- [ ] GET /api/jobs/{job_id} returns error for failed jobs
- [ ] GET /api/history returns all results in descending order
- [ ] GET /api/history pagination works correctly (page, limit)
- [ ] GET /api/thumbnails/{job_id} serves thumbnail images
- [ ] GET /api/reports/{job_id}/json returns valid JSON
- [ ] GET /api/reports/{job_id}/pdf returns valid PDF
- [ ] Database records are created and updated correctly
- [ ] Files are stored with unique IDs in month-based directories
- [ ] Background detection task updates database correctly

## Notes

- Use FastAPI's BackgroundTasks for async detection processing
- All file paths should be relative to project root
- Use SQLAlchemy ORM for all database operations
- Ensure proper error handling and logging throughout
- API responses should use plain language, not technical jargon
- Coordinate with ML Engineer on detector interface contract
