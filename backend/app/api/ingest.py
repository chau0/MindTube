"""
Video ingestion API endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import VideoIngestRequest, JobResponse, JobStatus
from app.core.logging import logger
import uuid
import asyncio

router = APIRouter()

# In-memory job storage for MVP (will be replaced with Redis/DB)
jobs_store = {}

@router.post("/ingest", response_model=JobResponse)
async def ingest_video(
    request: VideoIngestRequest,
    background_tasks: BackgroundTasks
):
    """
    Ingest a YouTube video for processing
    
    Creates a new job and starts background processing pipeline:
    1. Fetch video metadata
    2. Extract transcript (captions or ASR)
    3. Chunk transcript
    4. Generate summaries using LLM
    5. Return structured results
    """
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job in store
        jobs_store[job_id] = {
            "job_id": job_id,
            "status": JobStatus.PENDING,
            "request": request.dict(),
            "progress": {
                "status": JobStatus.PENDING,
                "progress_percent": 0,
                "current_step": "Initializing job",
                "estimated_completion_seconds": None,
                "partial_results": None
            },
            "result": None,
            "error": None,
            "created_at": "2025-01-01T00:00:00Z"  # Will be dynamic
        }
        
        # Start background processing
        background_tasks.add_task(process_video_pipeline, job_id, request)
        
        logger.info("Video ingestion job created", job_id=job_id, url=request.url)
        
        return JobResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            message="Job created successfully. Processing started.",
            estimated_completion_seconds=30  # Rough estimate
        )
        
    except Exception as e:
        logger.error("Failed to create ingestion job", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create job: {str(e)}"
        )

async def process_video_pipeline(job_id: str, request: VideoIngestRequest):
    """
    Background task to process video through the complete pipeline
    This is a mock implementation for Phase 0 - will be implemented in Phase 3-4
    """
    try:
        # Update job status through pipeline stages
        stages = [
            (JobStatus.FETCHING_METADATA, "Fetching video metadata", 10),
            (JobStatus.FETCHING_TRANSCRIPT, "Extracting transcript", 25),
            (JobStatus.CHUNKING, "Chunking transcript", 40),
            (JobStatus.MAPPING, "Generating initial summaries", 65),
            (JobStatus.REDUCING, "Creating final summaries", 85),
            (JobStatus.FINALIZING, "Finalizing results", 95),
        ]
        
        for status, step, progress in stages:
            # Update job progress
            jobs_store[job_id]["status"] = status
            jobs_store[job_id]["progress"].update({
                "status": status,
                "progress_percent": progress,
                "current_step": step
            })
            
            logger.info("Pipeline progress", job_id=job_id, status=status, progress=progress)
            
            # Simulate processing time
            await asyncio.sleep(2)
        
        # Mark as completed with mock result
        jobs_store[job_id]["status"] = JobStatus.COMPLETED
        jobs_store[job_id]["progress"]["progress_percent"] = 100
        jobs_store[job_id]["progress"]["current_step"] = "Completed"
        jobs_store[job_id]["result"] = {
            "job_id": job_id,
            "video_metadata": {
                "video_id": "mock_video_id",
                "title": "Mock Video Title",
                "channel_name": "Mock Channel",
                "duration_seconds": 600,
                "has_captions": True
            },
            "short_summary": [
                "This is a mock short summary line 1",
                "This is a mock short summary line 2"
            ],
            "detailed_summary": [
                {
                    "content": "Mock detailed summary paragraph 1",
                    "timestamp_ms": 30000,
                    "youtube_link": f"{request.url}&t=30s"
                }
            ],
            "key_ideas": [
                {
                    "content": "Mock key idea 1",
                    "timestamp_ms": 60000,
                    "youtube_link": f"{request.url}&t=60s"
                }
            ],
            "actionable_takeaways": [
                {
                    "content": "Mock actionable takeaway 1",
                    "timestamp_ms": 90000,
                    "youtube_link": f"{request.url}&t=90s"
                }
            ],
            "transcript": [
                {
                    "start_ms": 0,
                    "end_ms": 5000,
                    "text": "Mock transcript segment 1"
                }
            ],
            "processing_stats": {
                "total_duration_seconds": 12,
                "tokens_used": 1500,
                "cost_usd": 0.05
            },
            "created_at": "2025-01-01T00:00:00Z",
            "completed_at": "2025-01-01T00:00:12Z"
        }
        
        logger.info("Video processing completed", job_id=job_id)
        
    except Exception as e:
        # Mark job as failed
        jobs_store[job_id]["status"] = JobStatus.FAILED
        jobs_store[job_id]["error"] = str(e)
        logger.error("Video processing failed", job_id=job_id, error=str(e))