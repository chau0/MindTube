"""
MindTube FastAPI Application Entry Point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

from app.api import ingest, status, results
from app.core.config import settings
from app.core.logging import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="MindTube API",
    description="AI-powered YouTube video summarization service",
    version="0.1.0",
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
)

# CORS middleware
if settings.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routers
app.include_router(ingest.router, prefix="/api/v1", tags=["ingest"])
app.include_router(status.router, prefix="/api/v1", tags=["status"])
app.include_router(results.router, prefix="/api/v1", tags=["results"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "MindTube API",
        "version": "0.1.0",
        "status": "healthy",
        "docs": "/docs" if settings.ENABLE_DOCS else "disabled"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": "2025-01-01T00:00:00Z",  # Will be dynamic
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )