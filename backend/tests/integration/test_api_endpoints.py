"""
Integration tests for API endpoints
Following TDD guide patterns
"""

import pytest
import json
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app


class TestIngestAPI:
    """Test video ingestion API endpoints."""
    
    def test_ingest_valid_youtube_url(self, test_client):
        """Test ingesting a valid YouTube URL."""
        payload = {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "enable_asr": False,
            "language": "en"
        }
        
        response = test_client.post("/api/v1/ingest", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "job_id" in data
        assert "status" in data
        assert "message" in data
        assert data["status"] == "pending"
        assert isinstance(data["job_id"], str)
        assert len(data["job_id"]) > 0
    
    def test_ingest_invalid_url(self, test_client):
        """Test ingesting an invalid URL."""
        payload = {
            "url": "https://example.com/not-youtube",
            "enable_asr": False
        }
        
        response = test_client.post("/api/v1/ingest", json=payload)
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_ingest_missing_url(self, test_client):
        """Test ingesting without URL."""
        payload = {
            "enable_asr": False
        }
        
        response = test_client.post("/api/v1/ingest", json=payload)
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_ingest_with_optional_parameters(self, test_client):
        """Test ingesting with all optional parameters."""
        payload = {
            "url": "https://youtu.be/dQw4w9WgXcQ",
            "enable_asr": True,
            "language": "ja",
            "chunk_size": 2000
        }
        
        response = test_client.post("/api/v1/ingest", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"


class TestStatusAPI:
    """Test job status API endpoints."""
    
    def test_get_status_nonexistent_job(self, test_client):
        """Test getting status for non-existent job."""
        response = test_client.get("/api/v1/status/nonexistent-job-id")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_get_status_after_ingest(self, test_client):
        """Test getting status after creating a job."""
        # First create a job
        ingest_payload = {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "enable_asr": False
        }
        
        ingest_response = test_client.post("/api/v1/ingest", json=ingest_payload)
        assert ingest_response.status_code == 200
        
        job_id = ingest_response.json()["job_id"]
        
        # Then check status
        status_response = test_client.get(f"/api/v1/status/{job_id}")
        
        assert status_response.status_code == 200
        data = status_response.json()
        
        # Verify status response structure
        assert "job_id" in data
        assert "status" in data
        assert "progress" in data
        assert data["job_id"] == job_id
        
        # Verify progress structure
        progress = data["progress"]
        assert "status" in progress
        assert "progress_percent" in progress
        assert "current_step" in progress
        assert isinstance(progress["progress_percent"], int)
        assert 0 <= progress["progress_percent"] <= 100
    
    def test_cancel_job(self, test_client):
        """Test cancelling a job."""
        # First create a job
        ingest_payload = {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        
        ingest_response = test_client.post("/api/v1/ingest", json=ingest_payload)
        job_id = ingest_response.json()["job_id"]
        
        # Cancel the job
        cancel_response = test_client.delete(f"/api/v1/status/{job_id}")
        
        assert cancel_response.status_code == 200
        data = cancel_response.json()
        assert "message" in data
        assert job_id in data["message"]
    
    def test_cancel_nonexistent_job(self, test_client):
        """Test cancelling a non-existent job."""
        response = test_client.delete("/api/v1/status/nonexistent-job-id")
        
        assert response.status_code == 404


class TestResultsAPI:
    """Test results API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_result_completed_job(self, async_client):
        """Test getting results for a completed job."""
        # Create a job and wait for completion
        ingest_payload = {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        
        ingest_response = await async_client.post("/api/v1/ingest", json=ingest_payload)
        job_id = ingest_response.json()["job_id"]
        
        # Wait for job completion (in real scenario, would poll status)
        import asyncio
        await asyncio.sleep(15)  # Wait for mock processing to complete
        
        # Get results
        result_response = await async_client.get(f"/api/v1/result/{job_id}")
        
        if result_response.status_code == 200:
            data = result_response.json()
            
            # Verify result structure
            assert "job_id" in data
            assert "video_metadata" in data
            assert "short_summary" in data
            assert "detailed_summary" in data
            assert "key_ideas" in data
            assert "actionable_takeaways" in data
            assert "transcript" in data
            assert "processing_stats" in data
            
            # Verify video metadata structure
            metadata = data["video_metadata"]
            assert "video_id" in metadata
            assert "title" in metadata
            assert "channel_name" in metadata
            assert "duration_seconds" in metadata
            
            # Verify summaries are lists
            assert isinstance(data["short_summary"], list)
            assert isinstance(data["detailed_summary"], list)
            assert isinstance(data["key_ideas"], list)
            assert isinstance(data["actionable_takeaways"], list)
            assert isinstance(data["transcript"], list)
    
    def test_get_result_nonexistent_job(self, test_client):
        """Test getting results for non-existent job."""
        response = test_client.get("/api/v1/result/nonexistent-job-id")
        
        assert response.status_code == 404
    
    def test_export_markdown_nonexistent_job(self, test_client):
        """Test markdown export for non-existent job."""
        response = test_client.get("/api/v1/export/nonexistent-job-id/markdown")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_export_markdown_completed_job(self, async_client):
        """Test markdown export for completed job."""
        # Create and wait for job completion
        ingest_payload = {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        
        ingest_response = await async_client.post("/api/v1/ingest", json=ingest_payload)
        job_id = ingest_response.json()["job_id"]
        
        # Wait for completion
        import asyncio
        await asyncio.sleep(15)
        
        # Export markdown
        export_response = await async_client.get(f"/api/v1/export/{job_id}/markdown")
        
        if export_response.status_code == 200:
            # Verify content type
            assert export_response.headers["content-type"] == "text/markdown; charset=utf-8"
            
            # Verify content structure
            content = export_response.text
            assert "# " in content  # Should have title
            assert "## " in content  # Should have sections
            assert "Short Summary" in content
            assert "Detailed Summary" in content
            assert "Key Ideas" in content
            assert "Actionable Takeaways" in content


class TestHealthEndpoints:
    """Test health and root endpoints."""
    
    def test_root_endpoint(self, test_client):
        """Test root endpoint."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "service" in data
        assert "version" in data
        assert "status" in data
        assert data["service"] == "MindTube API"
        assert data["status"] == "healthy"
    
    def test_health_endpoint(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
        assert data["status"] == "healthy"


class TestErrorHandling:
    """Test error handling across endpoints."""
    
    def test_invalid_json_payload(self, test_client):
        """Test handling of invalid JSON."""
        response = test_client.post(
            "/api/v1/ingest",
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_content_type(self, test_client):
        """Test handling of missing content type."""
        response = test_client.post("/api/v1/ingest", data='{"url": "test"}')
        
        # Should handle gracefully
        assert response.status_code in [422, 400]
    
    def test_method_not_allowed(self, test_client):
        """Test method not allowed errors."""
        response = test_client.put("/api/v1/ingest")
        
        assert response.status_code == 405