"""
Pytest configuration and fixtures for MindTube tests
Following the TDD guide structure
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient
import tempfile
import os

from app.main import app
from app.core.config import settings


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    original_env = os.environ.copy()
    
    # Set test environment variables
    test_env = {
        "ENVIRONMENT": "test",
        "DEBUG": "true",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_KEY": "test-key-123",
        "AZURE_OPENAI_API_VERSION": "2024-02-01",
        "DEFAULT_MAP_MODEL": "gpt-4o-mini",
        "DEFAULT_REDUCE_MODEL": "gpt-4o-mini",
    }
    
    os.environ.update(test_env)
    
    yield test_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_transcript_segments():
    """Sample transcript segments for testing."""
    from app.models.schemas import TranscriptSegment
    
    return [
        TranscriptSegment(
            start_ms=0,
            end_ms=5000,
            text="Welcome to this tutorial on machine learning."
        ),
        TranscriptSegment(
            start_ms=5000,
            end_ms=12000,
            text="Today we'll cover supervised and unsupervised learning."
        ),
        TranscriptSegment(
            start_ms=12000,
            end_ms=20000,
            text="Supervised learning uses labeled data to train models."
        ),
        TranscriptSegment(
            start_ms=20000,
            end_ms=28000,
            text="The key is to practice with real datasets."
        ),
    ]


@pytest.fixture
def sample_video_metadata():
    """Sample video metadata for testing."""
    from app.models.schemas import VideoMetadata
    
    return VideoMetadata(
        video_id="test_video_123",
        title="Test Machine Learning Tutorial",
        channel_name="Test Channel",
        duration_seconds=30,
        has_captions=True
    )


class MockAzureOpenAIClient:
    """Mock Azure OpenAI client for testing."""
    
    def __init__(self):
        self.call_count = 0
        self.last_request = None
    
    def count_tokens(self, text: str, model: str = "gpt-4") -> int:
        """Mock token counting."""
        return len(text.split()) * 1.3  # Rough approximation
    
    async def generate_summary(self, text: str, summary_type: str = "detailed") -> str:
        """Mock summary generation."""
        self.call_count += 1
        self.last_request = {"text": text, "summary_type": summary_type}
        
        mock_responses = {
            "short": "• This is a mock short summary\n• Key point about the content\n• Final important insight",
            "detailed": "This is a detailed mock summary that covers the main points of the content in a comprehensive way.",
            "key_ideas": "• Important concept 1\n• Key insight 2\n• Critical understanding 3",
            "takeaways": "• Actionable step 1\n• Practical advice 2\n• Next step recommendation 3"
        }
        
        return mock_responses.get(summary_type, "Mock summary content")
    
    async def process_transcript_chunks(self, chunks: list[str], summary_type: str = "detailed") -> list[str]:
        """Mock chunk processing."""
        return [await self.generate_summary(chunk, summary_type) for chunk in chunks]
    
    async def reduce_summaries(self, summaries: list[str], summary_type: str = "detailed") -> str:
        """Mock summary reduction."""
        return f"Combined {summary_type} summary from {len(summaries)} parts"


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing."""
    return MockAzureOpenAIClient()


@pytest.fixture
def mock_youtube_url():
    """Sample YouTube URL for testing."""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"