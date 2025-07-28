"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
from mindtube.core.config import MindTubeConfig


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    with patch.dict(os.environ, {
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "test-key",
        "MINDTUBE_CACHE_ENABLED": "false",
        "MINDTUBE_LOG_LEVEL": "DEBUG"
    }):
        from mindtube.core.config import get_config
        yield get_config()


@pytest.fixture
def sample_youtube_url():
    """Sample YouTube URL for testing."""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture
def sample_video_id():
    """Sample YouTube video ID for testing."""
    return "dQw4w9WgXcQ"


@pytest.fixture
def mock_youtube_transcript():
    """Mock YouTube transcript data."""
    return [
        {"text": "Hello everyone", "start": 0.0, "duration": 2.5},
        {"text": "Welcome to this video", "start": 2.5, "duration": 3.0},
        {"text": "Today we'll learn about", "start": 5.5, "duration": 2.8},
        {"text": "artificial intelligence", "start": 8.3, "duration": 3.2}
    ]


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [{
            "message": {
                "content": "This is a test summary of the video content."
            }
        }],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }


@pytest.fixture
def clean_environment():
    """Clean environment variables for testing."""
    # Store original environment
    original_env = os.environ.copy()
    
    # Clear test-related variables
    test_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "MINDTUBE_CACHE_ENABLED",
        "MINDTUBE_CACHE_DIR",
        "MINDTUBE_CACHE_TTL_HOURS",
        "MINDTUBE_OUTPUT_DIR",
        "MINDTUBE_OUTPUT_FORMAT",
        "MINDTUBE_MAX_TRANSCRIPT_LENGTH",
        "MINDTUBE_REQUEST_TIMEOUT",
        "MINDTUBE_MAX_RETRIES",
        "MINDTUBE_LOG_LEVEL",
        "MINDTUBE_LOG_FILE",
    ]
    
    for var in test_vars:
        if var in os.environ:
            del os.environ[var]
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_azure_openai_client():
    """Mock Azure OpenAI client for testing."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Test response from Azure OpenAI"
    mock_response.usage.prompt_tokens = 100
    mock_response.usage.completion_tokens = 50
    mock_response.usage.total_tokens = 150
    
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def sample_transcript_text():
    """Sample transcript text for testing."""
    return """Hello everyone and welcome to this tutorial. Today we're going to learn about machine learning. Machine learning is a subset of artificial intelligence. It allows computers to learn without being explicitly programmed."""


@pytest.fixture
def sample_video_metadata():
    """Sample video metadata for testing."""
    return {
        "video_id": "dQw4w9WgXcQ",
        "title": "Sample Video Title",
        "description": "This is a sample video description for testing purposes.",
        "duration": 180,  # 3 minutes
        "upload_date": "2023-01-01",
        "uploader": "Test Channel",
        "view_count": 1000000,
        "like_count": 10000,
        "language": "en"
    }