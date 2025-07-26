"""
Pydantic models for MindTube API
"""

from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
import re

class JobStatus(str, Enum):
    """Job processing status"""
    PENDING = "pending"
    FETCHING_METADATA = "fetching_metadata"
    FETCHING_TRANSCRIPT = "fetching_transcript"
    CHUNKING = "chunking"
    MAPPING = "mapping"
    REDUCING = "reducing"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class VideoIngestRequest(BaseModel):
    """Request model for video ingestion"""
    url: str = Field(..., description="YouTube video URL")
    enable_asr: bool = Field(default=False, description="Enable ASR fallback if no captions")
    language: Optional[str] = Field(default=None, description="Preferred language (en, ja)")
    chunk_size: Optional[int] = Field(default=None, description="Custom chunk size in tokens")
    
    @validator('url')
    def validate_youtube_url(cls, v):
        """Validate YouTube URL format"""
        youtube_patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'https?://youtu\.be/([a-zA-Z0-9_-]{11})',
            r'https?://(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        ]
        
        if not any(re.match(pattern, v) for pattern in youtube_patterns):
            raise ValueError('Invalid YouTube URL format')
        return v

class VideoMetadata(BaseModel):
    """Video metadata from YouTube API"""
    video_id: str
    title: str
    channel_name: str
    duration_seconds: int
    view_count: Optional[int] = None
    published_at: Optional[datetime] = None
    description: Optional[str] = None
    language: Optional[str] = None
    has_captions: bool = False

class TranscriptSegment(BaseModel):
    """Individual transcript segment with timing"""
    start_ms: int
    end_ms: int
    text: str
    confidence: Optional[float] = None

class ProcessingProgress(BaseModel):
    """Progress information for a job"""
    status: JobStatus
    progress_percent: int = Field(ge=0, le=100)
    current_step: str
    estimated_completion_seconds: Optional[int] = None
    partial_results: Optional[Dict[str, Any]] = None

class SummarySection(BaseModel):
    """Summary section with optional timestamps"""
    content: str
    timestamp_ms: Optional[int] = None
    youtube_link: Optional[str] = None

class ProcessingResult(BaseModel):
    """Complete processing result"""
    job_id: str
    video_metadata: VideoMetadata
    short_summary: List[str]
    detailed_summary: List[SummarySection]
    key_ideas: List[SummarySection]
    actionable_takeaways: List[SummarySection]
    transcript: List[TranscriptSegment]
    processing_stats: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None

class JobResponse(BaseModel):
    """Response for job creation"""
    job_id: str
    status: JobStatus
    message: str
    estimated_completion_seconds: Optional[int] = None

class JobStatusResponse(BaseModel):
    """Response for job status check"""
    job_id: str
    status: JobStatus
    progress: ProcessingProgress
    result: Optional[ProcessingResult] = None
    error: Optional[str] = None

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: bool = True
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    environment: str
    debug: bool