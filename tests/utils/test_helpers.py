"""Test helper utilities."""

import json
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock


def load_test_fixture(filename: str) -> Dict[str, Any]:
    """Load a test fixture from the fixtures directory."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / filename
    if not fixture_path.exists():
        raise FileNotFoundError(f"Test fixture not found: {fixture_path}")
    
    with open(fixture_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_mock_transcript_response(segments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a mock transcript response for testing."""
    return {
        "video_id": "test_video_id",
        "language": "en",
        "segments": segments
    }


def assert_valid_json_output(output_path: Path) -> Dict[str, Any]:
    """Assert that a file contains valid JSON and return the data."""
    assert output_path.exists(), f"Output file {output_path} does not exist"
    
    with open(output_path, 'r', encoding='utf-8') as f:
        data = json.load(f)  # This will raise if invalid JSON
    
    assert isinstance(data, dict), "Output should be a JSON object"
    return data


def assert_valid_markdown_output(output_path: Path) -> str:
    """Assert that a file contains valid markdown and return the content."""
    assert output_path.exists(), f"Output file {output_path} does not exist"
    
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert content.strip(), "Markdown file should not be empty"
    assert isinstance(content, str), "Content should be a string"
    return content


class MockResponse:
    """Mock HTTP response for testing."""
    
    def __init__(self, json_data: Dict[str, Any], status_code: int = 200, text: str = None):
        self.json_data = json_data
        self.status_code = status_code
        self.text = text or json.dumps(json_data)
        self.headers = {'content-type': 'application/json'}
    
    def json(self) -> Dict[str, Any]:
        """Return JSON data."""
        return self.json_data
    
    def raise_for_status(self) -> None:
        """Raise HTTPError for bad status codes."""
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")
    
    @property
    def ok(self) -> bool:
        """Return True if status code is less than 400."""
        return self.status_code < 400


class MockYouTubeTranscriptApi:
    """Mock YouTube Transcript API for testing."""
    
    def __init__(self, transcript_data: List[Dict[str, Any]] = None):
        self.transcript_data = transcript_data or []
    
    def get_transcript(self, video_id: str, languages: List[str] = None) -> List[Dict[str, Any]]:
        """Mock get_transcript method."""
        return self.transcript_data
    
    def list_transcripts(self, video_id: str):
        """Mock list_transcripts method."""
        mock_transcript_list = Mock()
        mock_transcript_list.find_transcript.return_value.fetch.return_value = self.transcript_data
        return mock_transcript_list


class MockAzureOpenAIClient:
    """Mock Azure OpenAI client for testing."""
    
    def __init__(self, response_content: str = "Test response"):
        self.response_content = response_content
        self.chat = Mock()
        self.completions = Mock()
        
        # Set up the mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = response_content
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150
        
        self.chat.completions.create.return_value = mock_response


def create_sample_transcript_segments(count: int = 4) -> List[Dict[str, Any]]:
    """Create sample transcript segments for testing."""
    segments = []
    current_time = 0.0
    
    sample_texts = [
        "Hello everyone and welcome to this tutorial",
        "Today we're going to learn about machine learning",
        "Machine learning is a subset of artificial intelligence",
        "It allows computers to learn without being explicitly programmed",
        "This technology is used in many applications today",
        "From recommendation systems to autonomous vehicles",
        "Understanding the basics is important for everyone",
        "Let's dive deeper into the concepts"
    ]
    
    for i in range(min(count, len(sample_texts))):
        duration = 3.0 + (i * 0.5)  # Varying durations
        segments.append({
            "text": sample_texts[i],
            "start": current_time,
            "duration": duration
        })
        current_time += duration
    
    return segments


def assert_transcript_structure(transcript_data: Dict[str, Any]) -> None:
    """Assert that transcript data has the expected structure."""
    required_fields = ["video_id", "language", "segments"]
    
    for field in required_fields:
        assert field in transcript_data, f"Missing required field: {field}"
    
    assert isinstance(transcript_data["segments"], list), "Segments should be a list"
    
    for segment in transcript_data["segments"]:
        assert isinstance(segment, dict), "Each segment should be a dict"
        assert "text" in segment, "Segment should have text"
        assert "start" in segment, "Segment should have start time"
        assert "duration" in segment, "Segment should have duration"


def assert_analysis_structure(analysis_data: Dict[str, Any]) -> None:
    """Assert that analysis data has the expected structure."""
    required_fields = ["summary", "key_ideas"]
    
    for field in required_fields:
        assert field in analysis_data, f"Missing required field: {field}"
    
    assert isinstance(analysis_data["summary"], str), "Summary should be a string"
    assert analysis_data["summary"].strip(), "Summary should not be empty"
    
    if "key_ideas" in analysis_data:
        assert isinstance(analysis_data["key_ideas"], list), "Key ideas should be a list"


def create_mock_cache_dir(temp_dir: Path) -> Path:
    """Create a mock cache directory structure for testing."""
    cache_dir = temp_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Create some sample cache files
    (cache_dir / "transcripts").mkdir(exist_ok=True)
    (cache_dir / "analyses").mkdir(exist_ok=True)
    
    return cache_dir


def create_mock_output_dir(temp_dir: Path) -> Path:
    """Create a mock output directory structure for testing."""
    output_dir = temp_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir