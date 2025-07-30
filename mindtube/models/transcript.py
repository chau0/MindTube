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