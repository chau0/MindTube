"""Test helper utilities for ytnote tests."""

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock


def create_temp_transcript_file(transcript_data: list[dict[str, Any]], suffix: str = ".json") -> Path:
    """Create a temporary transcript file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
        json.dump(transcript_data, f, indent=2)
        return Path(f.name)


def create_temp_vtt_file(vtt_content: str) -> Path:
    """Create a temporary VTT file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".vtt", delete=False) as f:
        f.write(vtt_content)
        return Path(f.name)


def mock_youtube_transcript_api_success(transcript_data: list[dict[str, Any]]):
    """Create a mock for successful youtube_transcript_api response."""
    mock_transcript = MagicMock()
    mock_transcript.fetch.return_value = transcript_data
    return mock_transcript


def mock_youtube_transcript_api_error(error_class, error_message: str = "API Error"):
    """Create a mock for youtube_transcript_api error response."""
    mock_transcript = MagicMock()
    mock_transcript.fetch.side_effect = error_class(error_message)
    return mock_transcript


def mock_subprocess_success(stdout: str = "", stderr: str = "", returncode: int = 0):
    """Create a mock for successful subprocess call."""
    mock_result = Mock()
    mock_result.stdout = stdout
    mock_result.stderr = stderr
    mock_result.returncode = returncode
    return mock_result


def mock_subprocess_error(stderr: str = "Command failed", returncode: int = 1):
    """Create a mock for failed subprocess call."""
    return mock_subprocess_success(stderr=stderr, returncode=returncode)


def assert_transcript_schema(transcript_data: list[dict[str, Any]]) -> None:
    """Assert that transcript data matches expected schema."""
    assert isinstance(transcript_data, list), "Transcript should be a list"

    for segment in transcript_data:
        assert isinstance(segment, dict), "Each segment should be a dict"
        assert "start" in segment, "Segment should have 'start' field"
        assert "end" in segment, "Segment should have 'end' field"
        assert "text" in segment, "Segment should have 'text' field"
        assert "lang" in segment, "Segment should have 'lang' field"

        assert isinstance(segment["start"], (int, float)), "Start should be numeric"
        assert isinstance(segment["end"], (int, float)), "End should be numeric"
        assert isinstance(segment["text"], str), "Text should be string"
        assert isinstance(segment["lang"], str), "Lang should be string"

        assert segment["start"] >= 0, "Start time should be non-negative"
        assert segment["end"] > segment["start"], "End time should be after start time"
        assert len(segment["text"].strip()) > 0, "Text should not be empty"
        assert len(segment["lang"]) >= 2, "Language code should be at least 2 characters"


def assert_video_id_format(video_id: str) -> None:
    """Assert that video ID matches YouTube's format."""
    assert isinstance(video_id, str), "Video ID should be a string"
    assert len(video_id) == 11, f"Video ID should be 11 characters, got {len(video_id)}"

    # YouTube video IDs contain only alphanumeric characters, hyphens, and underscores
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
    video_id_chars = set(video_id)
    assert video_id_chars.issubset(allowed_chars), (
        f"Video ID contains invalid characters: {video_id_chars - allowed_chars}"
    )


def create_mock_config(
    output_dir: str = "test_data",
    cache_enabled: bool = True,
    fallback_enabled: bool = False,
    language_preference: list[str] | None = None,
) -> Mock:
    """Create a mock configuration for testing."""
    if language_preference is None:
        language_preference = ["en", "en-US"]

    mock_config = Mock()
    mock_config.output_dir = Path(output_dir)
    mock_config.cache_enabled = cache_enabled
    mock_config.fallback_enabled = fallback_enabled
    mock_config.language_preference = language_preference
    mock_config.ensure_output_dir.return_value = None

    return mock_config


def cleanup_temp_files(*file_paths: Path) -> None:
    """Clean up temporary files created during testing."""
    for file_path in file_paths:
        try:
            if file_path.exists():
                file_path.unlink()
        except (OSError, PermissionError):
            pass  # Ignore cleanup errors in tests
