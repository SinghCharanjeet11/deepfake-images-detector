"""
Deepfake Detection Platform — FastAPI application entry point.

Start the server:
    uvicorn main:app --reload --port 8000

API docs (auto-generated):
    http://localhost:8000/docs
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from database.connection import init_db
from api.routes import router
from config import settings

# ------------------------------------------------------------------ #
# Logging
# ------------------------------------------------------------------ #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
# Startup / shutdown lifecycle
# ------------------------------------------------------------------ #
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables and required directories on startup
    logger.info("Initialising database...")
    init_db()

    for directory in [settings.UPLOAD_DIR, settings.THUMBNAIL_DIR, "models"]:
        os.makedirs(directory, exist_ok=True)
        logger.info("Directory ready: %s", directory)

    logger.info("Server ready.")
    yield
    logger.info("Server shutting down.")


# ------------------------------------------------------------------ #
# FastAPI app
# ------------------------------------------------------------------ #
app = FastAPI(
    title="Deepfake Detection Platform",
    description=(
        "Detects whether an image is real, AI-generated, or manipulated. "
        "Provides confidence scores and Grad-CAM heatmap explanations."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — localhost only during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------ #
# API routes
# ------------------------------------------------------------------ #
app.include_router(router)


# ------------------------------------------------------------------ #
# Global error handlers
# ------------------------------------------------------------------ #
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "The requested resource was not found."},
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    logger.error("Unhandled server error: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on our end. Please try again."},
    )


# ------------------------------------------------------------------ #
# Static files — frontend served by FastAPI
# ------------------------------------------------------------------ #
# Uncomment once Ayush provides the frontend build:
# app.mount("/", StaticFiles(directory="static", html=True), name="static")


# ------------------------------------------------------------------ #
# Health check
# ------------------------------------------------------------------ #
@app.get("/health", tags=["System"])
def health_check():
    """Quick check that the server is running."""
    return {"status": "ok", "version": "1.0.0"}
