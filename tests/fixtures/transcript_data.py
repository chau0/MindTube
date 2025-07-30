"""Test fixtures for transcript data and API responses."""

from typing import Any

# Sample transcript data as returned by youtube-transcript-api
SAMPLE_TRANSCRIPT_RAW = [
    {"text": "Hello and welcome to this video", "start": 0.0, "duration": 3.5},
    {"text": "Today we're going to talk about", "start": 3.5, "duration": 2.8},
    {"text": "the importance of testing in software development", "start": 6.3, "duration": 4.2},
    {"text": "Testing helps us catch bugs early", "start": 10.5, "duration": 3.1},
    {"text": "and ensures our code works as expected", "start": 13.6, "duration": 3.9},
    {"text": "Let's start with unit testing", "start": 17.5, "duration": 2.7},
    {"text": "Unit tests verify individual components", "start": 20.2, "duration": 3.4},
    {"text": "in isolation from the rest of the system", "start": 23.6, "duration": 3.8},
    {"text": "Thank you for watching", "start": 27.4, "duration": 2.1},
    {"text": "Don't forget to subscribe", "start": 29.5, "duration": 2.3},
]

# Expected normalized transcript format
SAMPLE_TRANSCRIPT_NORMALIZED = [
    {"start": 0.0, "end": 3.5, "text": "Hello and welcome to this video", "lang": "en"},
    {"start": 3.5, "end": 6.3, "text": "Today we're going to talk about", "lang": "en"},
    {"start": 6.3, "end": 10.5, "text": "the importance of testing in software development", "lang": "en"},
    {"start": 10.5, "end": 13.6, "text": "Testing helps us catch bugs early", "lang": "en"},
    {"start": 13.6, "end": 17.5, "text": "and ensures our code works as expected", "lang": "en"},
    {"start": 17.5, "end": 20.2, "text": "Let's start with unit testing", "lang": "en"},
    {"start": 20.2, "end": 23.6, "text": "Unit tests verify individual components", "lang": "en"},
    {"start": 23.6, "end": 27.4, "text": "in isolation from the rest of the system", "lang": "en"},
    {"start": 27.4, "end": 29.5, "text": "Thank you for watching", "lang": "en"},
    {"start": 29.5, "end": 31.8, "text": "Don't forget to subscribe", "lang": "en"},
]

# Sample VTT format for fallback testing
SAMPLE_VTT_CONTENT = """WEBVTT

00:00:00.000 --> 00:00:03.500
Hello and welcome to this video

00:00:03.500 --> 00:00:06.300
Today we're going to talk about

00:00:06.300 --> 00:00:10.500
the importance of testing in software development

00:00:10.500 --> 00:00:13.600
Testing helps us catch bugs early

00:00:13.600 --> 00:00:17.500
and ensures our code works as expected

00:00:17.500 --> 00:00:20.200
Let's start with unit testing

00:00:20.200 --> 00:00:23.600
Unit tests verify individual components

00:00:23.600 --> 00:00:27.400
in isolation from the rest of the system

00:00:27.400 --> 00:00:29.500
Thank you for watching

00:00:29.500 --> 00:00:31.800
Don't forget to subscribe
"""

# Error responses from YouTube API
YOUTUBE_API_ERRORS = {
    "no_transcript": {"error": "TranscriptsDisabled", "message": "Transcripts are disabled for this video"},
    "video_unavailable": {"error": "VideoUnavailable", "message": "Video is unavailable"},
    "transcript_not_found": {"error": "NoTranscriptFound", "message": "No transcripts were found for this video"},
    "too_many_requests": {"error": "TooManyRequests", "message": "YouTube is receiving too many requests"},
}

# Language codes for testing
LANGUAGE_PREFERENCES = ["en", "en-US", "en-GB", "es", "fr", "de"]

# Mock metadata for transcript files
SAMPLE_TRANSCRIPT_METADATA = {
    "video_id": "dQw4w9WgXcQ",
    "title": "Sample Video Title",
    "duration": 31.8,
    "language": "en",
    "auto_generated": False,
    "fetched_at": "2024-01-15T10:30:00Z",
    "method": "youtube_transcript_api",
}

# Multiple language transcript availability
MULTI_LANGUAGE_AVAILABILITY = [
    {"language": "en", "language_code": "en", "is_generated": False, "is_translatable": True},
    {"language": "Spanish", "language_code": "es", "is_generated": False, "is_translatable": True},
    {"language": "French", "language_code": "fr", "is_generated": True, "is_translatable": True},
    {"language": "German", "language_code": "de", "is_generated": True, "is_translatable": True},
]


def create_mock_transcript_response(
    video_id: str = "dQw4w9WgXcQ",
    language: str = "en",
    auto_generated: bool = False,
    segments: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create a mock transcript response for testing."""
    if segments is None:
        segments = SAMPLE_TRANSCRIPT_RAW

    return {
        "video_id": video_id,
        "language": language,
        "auto_generated": auto_generated,
        "segments": segments,
        "fetched_at": "2024-01-15T10:30:00Z",
    }
