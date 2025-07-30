"""Tests for transcript models."""

import pytest
from mindtube.models.transcript import TranscriptSegment, Transcript


class TestTranscriptSegment:
    """Test TranscriptSegment model."""
    
    def test_valid_segment_creation(self):
        """Test creating a valid transcript segment."""
        segment = TranscriptSegment(
            start_time=0.0,
            end_time=5.0,
            text="Hello world",
            confidence=0.95
        )
        
        assert segment.start_time == 0.0
        assert segment.end_time == 5.0
        assert segment.text == "Hello world"
        assert segment.confidence == 0.95
        assert segment.duration == 5.0
    
    def test_end_time_validation(self):
        """Test that end_time must be after start_time."""
        with pytest.raises(ValueError, match="end_time must be greater than start_time"):
            TranscriptSegment(
                start_time=5.0,
                end_time=3.0,
                text="Invalid timing"
            )
    
    def test_srt_format(self):
        """Test SRT format conversion."""
        segment = TranscriptSegment(
            start_time=61.5,
            end_time=65.25,
            text="This is a test"
        )
        
        srt = segment.to_srt_format(1)
        expected = "1\n00:01:01,500 --> 00:01:05,250\nThis is a test\n"
        assert srt == expected


class TestTranscript:
    """Test Transcript model."""
    
    def test_valid_transcript_creation(self):
        """Test creating a valid transcript."""
        segments = [
            TranscriptSegment(start_time=0.0, end_time=5.0, text="First segment"),
            TranscriptSegment(start_time=5.0, end_time=10.0, text="Second segment")
        ]
        
        transcript = Transcript(
            video_id="test123",
            language="en",
            segments=segments
        )
        
        assert transcript.video_id == "test123"
        assert transcript.language == "en"
        assert len(transcript.segments) == 2
        assert transcript.total_duration == 10.0
        assert transcript.full_text == "First segment Second segment"
    
    def test_empty_segments_validation(self):
        """Test that transcript must have segments."""
        with pytest.raises(ValueError, match="Transcript must have at least one segment"):
            Transcript(
                video_id="test123",
                segments=[]
            )
    
    def test_get_text_at_time(self):
        """Test getting text at specific timestamp."""
        segments = [
            TranscriptSegment(start_time=0.0, end_time=5.0, text="First"),
            TranscriptSegment(start_time=5.0, end_time=10.0, text="Second")
        ]
        
        transcript = Transcript(video_id="test", segments=segments)
        
        assert transcript.get_text_at_time(2.5) == "First"
        assert transcript.get_text_at_time(7.5) == "Second"
        assert transcript.get_text_at_time(15.0) is None