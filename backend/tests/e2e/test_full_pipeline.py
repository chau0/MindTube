"""
End-to-end tests for the complete MindTube pipeline
Following TDD guide patterns
"""

import pytest
import asyncio
from httpx import AsyncClient

from app.main import app


class TestFullPipeline:
    """Test the complete video processing pipeline end-to-end."""
    
    @pytest.mark.asyncio
    async def test_complete_video_processing_workflow(self):
        """Test the complete workflow from ingest to results."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            
            # Step 1: Submit video for processing
            ingest_payload = {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "enable_asr": False,
                "language": "en"
            }
            
            ingest_response = await client.post("/api/v1/ingest", json=ingest_payload)
            assert ingest_response.status_code == 200
            
            job_data = ingest_response.json()
            job_id = job_data["job_id"]
            assert job_data["status"] == "pending"
            
            # Step 2: Monitor job progress
            max_wait_time = 30  # seconds
            wait_interval = 2   # seconds
            elapsed_time = 0
            
            while elapsed_time < max_wait_time:
                status_response = await client.get(f"/api/v1/status/{job_id}")
                assert status_response.status_code == 200
                
                status_data = status_response.json()
                current_status = status_data["status"]
                progress_percent = status_data["progress"]["progress_percent"]
                
                print(f"Job {job_id}: {current_status} ({progress_percent}%)")
                
                if current_status == "completed":
                    break
                elif current_status == "failed":
                    pytest.fail(f"Job failed: {status_data.get('error', 'Unknown error')}")
                
                await asyncio.sleep(wait_interval)
                elapsed_time += wait_interval
            
            # Verify job completed
            assert current_status == "completed", f"Job did not complete within {max_wait_time}s"
            assert progress_percent == 100
            
            # Step 3: Retrieve and validate results
            result_response = await client.get(f"/api/v1/result/{job_id}")
            assert result_response.status_code == 200
            
            result_data = result_response.json()
            
            # Validate result structure
            self._validate_result_structure(result_data)
            
            # Step 4: Test markdown export
            export_response = await client.get(f"/api/v1/export/{job_id}/markdown")
            assert export_response.status_code == 200
            assert export_response.headers["content-type"] == "text/markdown; charset=utf-8"
            
            markdown_content = export_response.text
            self._validate_markdown_content(markdown_content, result_data)
            
            print("✅ Complete pipeline test passed!")
    
    def _validate_result_structure(self, result_data):
        """Validate the structure of processing results."""
        # Required top-level fields
        required_fields = [
            "job_id", "video_metadata", "short_summary", "detailed_summary",
            "key_ideas", "actionable_takeaways", "transcript", "processing_stats",
            "created_at", "completed_at"
        ]
        
        for field in required_fields:
            assert field in result_data, f"Missing required field: {field}"
        
        # Validate video metadata
        metadata = result_data["video_metadata"]
        metadata_fields = ["video_id", "title", "channel_name", "duration_seconds", "has_captions"]
        for field in metadata_fields:
            assert field in metadata, f"Missing metadata field: {field}"
        
        # Validate summaries are non-empty lists
        summary_fields = ["short_summary", "detailed_summary", "key_ideas", "actionable_takeaways"]
        for field in summary_fields:
            assert isinstance(result_data[field], list), f"{field} should be a list"
            assert len(result_data[field]) > 0, f"{field} should not be empty"
        
        # Validate transcript structure
        transcript = result_data["transcript"]
        assert isinstance(transcript, list), "Transcript should be a list"
        assert len(transcript) > 0, "Transcript should not be empty"
        
        for segment in transcript:
            assert "start_ms" in segment
            assert "end_ms" in segment
            assert "text" in segment
            assert isinstance(segment["start_ms"], int)
            assert isinstance(segment["end_ms"], int)
            assert segment["start_ms"] <= segment["end_ms"]
        
        # Validate processing stats
        stats = result_data["processing_stats"]
        stats_fields = ["total_duration_seconds", "tokens_used", "cost_usd"]
        for field in stats_fields:
            assert field in stats, f"Missing stats field: {field}"
            assert isinstance(stats[field], (int, float)), f"{field} should be numeric"
    
    def _validate_markdown_content(self, markdown_content, result_data):
        """Validate the markdown export content."""
        # Should contain title
        title = result_data["video_metadata"]["title"]
        assert title in markdown_content, "Markdown should contain video title"
        
        # Should contain section headers
        expected_sections = [
            "Short Summary",
            "Detailed Summary", 
            "Key Ideas",
            "Actionable Takeaways",
            "Transcript"
        ]
        
        for section in expected_sections:
            assert section in markdown_content, f"Markdown should contain {section} section"
        
        # Should contain some summary content
        for summary_item in result_data["short_summary"]:
            assert summary_item in markdown_content, "Markdown should contain short summary content"
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_url(self):
        """Test error handling with invalid YouTube URL."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            
            ingest_payload = {
                "url": "https://example.com/not-youtube-video"
            }
            
            response = await client.post("/api/v1/ingest", json=ingest_payload)
            
            # Should return validation error
            assert response.status_code == 422
            error_data = response.json()
            assert "detail" in error_data
    
    @pytest.mark.asyncio
    async def test_job_cancellation(self):
        """Test job cancellation functionality."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            
            # Start a job
            ingest_payload = {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
            
            ingest_response = await client.post("/api/v1/ingest", json=ingest_payload)
            job_id = ingest_response.json()["job_id"]
            
            # Cancel the job quickly (before it completes)
            cancel_response = await client.delete(f"/api/v1/status/{job_id}")
            
            if cancel_response.status_code == 200:
                # Verify job was cancelled
                status_response = await client.get(f"/api/v1/status/{job_id}")
                status_data = status_response.json()
                
                # Job should be in cancelled state or completed (if it finished before cancellation)
                assert status_data["status"] in ["cancelled", "completed"]
    
    @pytest.mark.asyncio
    async def test_concurrent_job_processing(self):
        """Test processing multiple jobs concurrently."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            
            # Submit multiple jobs
            job_urls = [
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "https://youtu.be/dQw4w9WgXcQ",
                "https://www.youtube.com/watch?v=oHg5SJYRHA0"
            ]
            
            job_ids = []
            
            # Submit all jobs
            for url in job_urls:
                ingest_payload = {"url": url}
                response = await client.post("/api/v1/ingest", json=ingest_payload)
                assert response.status_code == 200
                job_ids.append(response.json()["job_id"])
            
            # Wait for all jobs to complete
            max_wait_time = 45  # seconds for multiple jobs
            completed_jobs = set()
            
            start_time = asyncio.get_event_loop().time()
            
            while len(completed_jobs) < len(job_ids):
                current_time = asyncio.get_event_loop().time()
                if current_time - start_time > max_wait_time:
                    break
                
                for job_id in job_ids:
                    if job_id not in completed_jobs:
                        status_response = await client.get(f"/api/v1/status/{job_id}")
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            if status_data["status"] in ["completed", "failed"]:
                                completed_jobs.add(job_id)
                
                await asyncio.sleep(2)
            
            # Verify at least some jobs completed
            assert len(completed_jobs) > 0, "At least one job should have completed"
            
            print(f"✅ Concurrent processing test: {len(completed_jobs)}/{len(job_ids)} jobs completed")


class TestPerformanceBaseline:
    """Test performance baselines for the system."""
    
    @pytest.mark.asyncio
    async def test_processing_time_baseline(self):
        """Test that processing completes within reasonable time."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            
            start_time = asyncio.get_event_loop().time()
            
            # Submit job
            ingest_payload = {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
            
            ingest_response = await client.post("/api/v1/ingest", json=ingest_payload)
            job_id = ingest_response.json()["job_id"]
            
            # Wait for completion
            while True:
                status_response = await client.get(f"/api/v1/status/{job_id}")
                status_data = status_response.json()
                
                if status_data["status"] == "completed":
                    break
                elif status_data["status"] == "failed":
                    pytest.fail("Job failed during performance test")
                
                current_time = asyncio.get_event_loop().time()
                if current_time - start_time > 60:  # 1 minute timeout
                    pytest.fail("Processing took longer than 60 seconds")
                
                await asyncio.sleep(1)
            
            end_time = asyncio.get_event_loop().time()
            processing_time = end_time - start_time
            
            print(f"✅ Processing completed in {processing_time:.2f} seconds")
            
            # Performance assertion (adjust based on requirements)
            assert processing_time < 30, f"Processing took {processing_time:.2f}s, expected < 30s"
    
    @pytest.mark.asyncio
    async def test_api_response_times(self):
        """Test API response times are reasonable."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            
            # Test health endpoint response time
            start_time = asyncio.get_event_loop().time()
            response = await client.get("/health")
            end_time = asyncio.get_event_loop().time()
            
            assert response.status_code == 200
            response_time = end_time - start_time
            assert response_time < 1.0, f"Health endpoint took {response_time:.3f}s, expected < 1s"
            
            # Test ingest endpoint response time
            start_time = asyncio.get_event_loop().time()
            ingest_payload = {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
            response = await client.post("/api/v1/ingest", json=ingest_payload)
            end_time = asyncio.get_event_loop().time()
            
            assert response.status_code == 200
            response_time = end_time - start_time
            assert response_time < 2.0, f"Ingest endpoint took {response_time:.3f}s, expected < 2s"
            
            print("✅ API response times within acceptable limits")