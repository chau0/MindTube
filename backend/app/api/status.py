"""
Job status API endpoints
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import JobStatusResponse
from app.api.ingest import jobs_store
from app.core.logging import logger

router = APIRouter()

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the current status and progress of a processing job
    
    Returns:
    - Job status (pending, processing, completed, failed)
    - Progress percentage and current step
    - Partial results if available
    - Full results if completed
    - Error details if failed
    """
    try:
        if job_id not in jobs_store:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found"
            )
        
        job_data = jobs_store[job_id]
        
        response = JobStatusResponse(
            job_id=job_id,
            status=job_data["status"],
            progress=job_data["progress"],
            result=job_data.get("result"),
            error=job_data.get("error")
        )
        
        logger.debug("Job status retrieved", job_id=job_id, status=job_data["status"])
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get job status", job_id=job_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve job status: {str(e)}"
        )

@router.delete("/status/{job_id}")
async def cancel_job(job_id: str):
    """
    Cancel a running job
    
    Note: In MVP, this just marks the job as cancelled.
    In production, this would also stop background processing.
    """
    try:
        if job_id not in jobs_store:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found"
            )
        
        job_data = jobs_store[job_id]
        
        # Only allow cancellation of non-terminal states
        if job_data["status"] in ["completed", "failed", "cancelled"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel job in {job_data['status']} state"
            )
        
        # Mark as cancelled
        jobs_store[job_id]["status"] = "cancelled"
        jobs_store[job_id]["progress"]["current_step"] = "Cancelled by user"
        
        logger.info("Job cancelled", job_id=job_id)
        
        return {"message": f"Job {job_id} cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to cancel job", job_id=job_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel job: {str(e)}"
        )