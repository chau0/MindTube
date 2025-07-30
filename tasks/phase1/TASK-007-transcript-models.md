# TASK-007: Transcript Models

## Task Information
- **ID**: TASK-007
- **Phase**: 1 - Data Models
- **Estimate**: 30 minutes
- **Dependencies**: TASK-006
- **Status**: ✅ Completed

## Description
Implement TranscriptSegment and Transcript dataclasses with Pydantic validation. These models represent transcript data with timing information and text content.

## Acceptance Criteria
- [x] Create TranscriptSegment dataclass with timing and text
- [x] Create Transcript dataclass as collection of segments
- [x] Add JSON serialization/deserialization
- [x] Implement field validation for timing constraints
- [x] Create unit tests
- [x] Add docstrings and type hints
- [x] Support optional confidence scores

## Implementation

### Step 1: Create mindtube/models/transcript.py

```python
"""Transcript models for video content."""

from datetime import timedelta
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class TranscriptSegment(BaseModel):
    """A single segment of transcript with timing information."""
    
    start_time: float = Field(..., description="Start time in seconds", ge=0)
    end_time: float = Field(..., description="End time in seconds", ge=0)
    text: str = Field(..., description="Transcript text content", min_length=1)
    confidence: Optional[float] = Field(None, description="Confidence score", ge=0, le=1)
    
    @validator('end_time')
    def end_time_must_be_after_start(cls, v, values):
        """Ensure end_time is after start_time."""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be greater than start_time')
        return v
    
    @property
    def duration(self) -> float:
        """Duration of the segment in seconds."""
        return self.end_time - self.start_time
    
    def to_srt_format(self, index: int) -> str:
        """Convert to SRT subtitle format."""
        start = self._seconds_to_srt_time(self.start_time)
        end = self._seconds_to_srt_time(self.end_time)
        return f"{index}\n{start} --> {end}\n{self.text}\n"
    
    @staticmethod
    def _seconds_to_srt_time(seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


class Transcript(BaseModel):
    """Complete transcript for a video."""
    
    video_id: str = Field(..., description="YouTube video ID")
    language: str = Field("en", description="Language code")
    segments: List[TranscriptSegment] = Field(..., description="Transcript segments")
    source: str = Field("youtube", description="Transcript source")
    
    @validator('segments')
    def segments_must_not_be_empty(cls, v):
        """Ensure transcript has at least one segment."""
        if not v:
            raise ValueError('Transcript must have at least one segment')
        return v
    
    @property
    def total_duration(self) -> float:
        """Total duration of the transcript in seconds."""
        if not self.segments:
            return 0.0
        return max(segment.end_time for segment in self.segments)
    
    @property
    def full_text(self) -> str:
        """Complete transcript text."""
        return " ".join(segment.text for segment in self.segments)
    
    def get_text_at_time(self, timestamp: float) -> Optional[str]:
        """Get transcript text at a specific timestamp."""
        for segment in self.segments:
            if segment.start_time <= timestamp <= segment.end_time:
                return segment.text
        return None
    
    def to_srt(self) -> str:
        """Export transcript as SRT subtitle format."""
        return "\n".join(
            segment.to_srt_format(i + 1) 
            for i, segment in enumerate(self.segments)
        )
```

### Step 2: Create tests/unit/models/test_transcript.py

```python
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
```

## Implementation Steps

1. **Create transcript models file**
   - Implement TranscriptSegment with timing validation
   - Implement Transcript as collection of segments
   - Add utility methods for SRT export and text search

2. **Add validation logic**
   - Ensure timing constraints are met
   - Validate required fields
   - Add confidence score validation

3. **Create comprehensive tests**
   - Test model creation and validation
   - Test timing constraints
   - Test utility methods

4. **Integration with existing models**
   - Ensure compatibility with VideoMetadata
   - Add foreign key relationships where needed

## Notes

- Transcript segments should be ordered by start_time
- Consider adding methods for merging overlapping segments
- SRT export functionality for subtitle generation
- Support for multiple languages and sources

## Potential Issues

**Issue**: Overlapping transcript segments
**Solution**: Add validation or merging logic for overlapping segments

**Issue**: Large transcript memory usage
**Solution**: Consider lazy loading or chunking for very long videos