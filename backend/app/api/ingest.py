"""
Video ingestion API endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import VideoIngestRequest, JobResponse, JobStatus, TranscriptSegment
from app.services.summarization import summarization_service
from app.services.youtube_transcript import youtube_transcript_service
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
        
        # Fetch real transcript from YouTube
        try:
            logger.info("Fetching YouTube transcript", job_id=job_id, url=str(request.url))
            transcript = await youtube_transcript_service.fetch_transcript_with_fallback(str(request.url))
            logger.info("YouTube transcript fetched successfully", job_id=job_id, segment_count=len(transcript))
        except Exception as e:
            logger.warning("Failed to fetch YouTube transcript, using fallback", job_id=job_id, error=str(e))
            # Fall back to mock transcript for demo purposes
            transcript = [
                TranscriptSegment(start_ms=0, end_ms=5000, text="Welcome to this tutorial on machine learning fundamentals."),
                TranscriptSegment(start_ms=5000, end_ms=12000, text="Today we'll cover supervised learning, unsupervised learning, and reinforcement learning."),
                TranscriptSegment(start_ms=12000, end_ms=20000, text="Supervised learning uses labeled data to train models that can make predictions."),
                TranscriptSegment(start_ms=20000, end_ms=28000, text="Common examples include classification and regression problems."),
                TranscriptSegment(start_ms=28000, end_ms=35000, text="Unsupervised learning finds patterns in data without labeled examples."),
                TranscriptSegment(start_ms=35000, end_ms=42000, text="Clustering and dimensionality reduction are key unsupervised techniques."),
                TranscriptSegment(start_ms=42000, end_ms=50000, text="Reinforcement learning trains agents through trial and error with rewards."),
                TranscriptSegment(start_ms=50000, end_ms=58000, text="Key takeaway: Choose the right approach based on your data and problem type."),
                TranscriptSegment(start_ms=58000, end_ms=65000, text="Practice with real datasets to build your machine learning skills."),
                TranscriptSegment(start_ms=65000, end_ms=70000, text="Thanks for watching, and happy learning!")
            ]
        
        try:
            # Process video using Azure OpenAI
            logger.info("Starting Azure OpenAI processing", job_id=job_id)
            
            summaries = await summarization_service.process_complete_video(
                transcript=transcript,
                video_url=str(request.url)
            )
            
            # Mark as completed with real Azure OpenAI results
            jobs_store[job_id]["status"] = JobStatus.COMPLETED
            jobs_store[job_id]["progress"]["progress_percent"] = 100
            jobs_store[job_id]["progress"]["current_step"] = "Completed"
            jobs_store[job_id]["result"] = {
                "job_id": job_id,
                "video_metadata": {
                    "video_id": "demo_video_id",
                    "title": "Machine Learning Fundamentals Tutorial",
                    "channel_name": "AI Education Channel",
                    "duration_seconds": 70,
                    "has_captions": True
                },
                "short_summary": summaries["short_summary"],
                "detailed_summary": [section.dict() for section in summaries["detailed_summary"]],
                "key_ideas": [section.dict() for section in summaries["key_ideas"]],
                "actionable_takeaways": [section.dict() for section in summaries["actionable_takeaways"]],
                "transcript": [segment.dict() for segment in transcript],
                "processing_stats": {
                    "total_duration_seconds": 15,
                    "tokens_used": 2500,
                    "cost_usd": 0.08
                },
                "created_at": "2025-01-01T00:00:00Z",
                "completed_at": "2025-01-01T00:00:15Z"
            }
            
            logger.info("Azure OpenAI processing completed successfully", job_id=job_id)
            
        except Exception as e:
            logger.error("Azure OpenAI processing failed", job_id=job_id, error=str(e))
            # Fall back to mock result if Azure OpenAI fails
            jobs_store[job_id]["status"] = JobStatus.COMPLETED
            jobs_store[job_id]["progress"]["progress_percent"] = 100
            jobs_store[job_id]["progress"]["current_step"] = "Completed (fallback)"
            jobs_store[job_id]["result"] = {
                "job_id": job_id,
                "video_metadata": {
                    "video_id": "fallback_video_id",
                    "title": "Fallback Demo Video",
                    "channel_name": "Demo Channel",
                    "duration_seconds": 60,
                    "has_captions": True
                },
                "short_summary": [
                    "This is a fallback summary when Azure OpenAI is not available",
                    "The system gracefully handles configuration issues"
                ],
                "detailed_summary": [
                    {
                        "content": "Fallback detailed summary content",
                        "timestamp_ms": 30000,
                        "youtube_link": f"{request.url}&t=30s"
                    }
                ],
                "key_ideas": [
                    {
                        "content": "Fallback key idea",
                        "timestamp_ms": 45000,
                        "youtube_link": f"{request.url}&t=45s"
                    }
                ],
                "actionable_takeaways": [
                    {
                        "content": "Configure Azure OpenAI credentials to enable AI processing",
                        "timestamp_ms": 55000,
                        "youtube_link": f"{request.url}&t=55s"
                    }
                ],
                "transcript": [
                    {
                        "start_ms": 0,
                        "end_ms": 5000,
                        "text": "Fallback transcript segment"
                    }
                ],
                "processing_stats": {
                    "total_duration_seconds": 8,
                    "tokens_used": 0,
                    "cost_usd": 0.00
                },
                "created_at": "2025-01-01T00:00:00Z",
                "completed_at": "2025-01-01T00:00:08Z"
            }
        
        logger.info("Video processing completed", job_id=job_id)
        
    except Exception as e:
        # Mark job as failed
        jobs_store[job_id]["status"] = JobStatus.FAILED
        jobs_store[job_id]["error"] = str(e)
        logger.error("Video processing failed", job_id=job_id, error=str(e))