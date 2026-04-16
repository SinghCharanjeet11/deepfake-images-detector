@echo off
echo Starting Deepfake Detection Platform...
echo.
echo Server will be available at:
echo   - http://localhost:8000
echo   - http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop the server
echo.
uvicorn main:app --reload --port 8000
