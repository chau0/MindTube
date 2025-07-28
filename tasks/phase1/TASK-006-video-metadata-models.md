# TASK-006: Video Metadata Models

## Task Information
- **ID**: TASK-006
- **Phase**: 1 - Data Models
- **Estimate**: 45 minutes
- **Dependencies**: TASK-005
- **Status**: 🔴 Backlog

## Description
Implement VideoMetadata dataclass and validation using Pydantic. This model represents YouTube video information and metadata required for processing.

## Acceptance Criteria
- [ ] Create VideoMetadata dataclass with Pydantic validation
- [ ] Include all fields from design document
- [ ] Add JSON serialization/deserialization
- [ ] Implement field validation
- [ ] Create unit tests
- [ ] Add docstrings and type hints
- [ ] Support optional fields appropriately

## Implementation

### Step 1: Create mindtube/models/video.py

```python
"""Video metadata models."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator, HttpUrl
from enum import Enum

class VideoPrivacy(str, Enum):
    """Video privacy settings."""
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"

class VideoMetadata(BaseModel):
    """YouTube video metadata."""
    
    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Video title")
    description: Optional[str] = Field(None, description="Video description")
    channel_id: str = Field(..., description="YouTube channel ID")
    channel_name: str = Field(..., description="Channel display name")
    duration_seconds: Optional[int] = Field(None, description="Video duration in seconds", ge=0)
    view_count: Optional[int] = Field(None, description="Number of views", ge=0)
    like_count: Optional[int] = Field(None, description="Number of likes", ge=0)
    upload_date: Optional[datetime] = Field(None, description="Video upload date")
    language: Optional[str] = Field(None, description="Video language code")
    privacy: Optional[VideoPrivacy] = Field(None, description="Video privacy setting")
    tags: List[str] = Field(default_factory=list, description="Video tags")
    thumbnail_url: Optional[HttpUrl] = Field(None, description="Video thumbnail URL")
    url: str = Field(..., description="Full YouTube URL")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "title": "Rick Astley - Never Gonna Give You Up",
                "description": "The official video for Rick Astley's 'Never Gonna Give You Up'",
                "channel_id": "UCuAXFkgsw1L7xaCfnd5JJOw",
                "channel_name": "Rick Astley",
                "duration_seconds": 213,
                "view_count": 1000000000,
                "like_count": 10000000,
                "upload_date": "2009-10-25T06:57:33Z",
                "language": "en",
                "privacy": "public",
                "tags": ["rick astley", "never gonna give you up", "music"],
                "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
        }
    
    @validator("video_id")
    def validate_video_id(cls, v):
        """Validate YouTube video ID format."""
        if not v or len(v) != 11:
            raise ValueError("Video ID must be 11 characters long")
        # YouTube video IDs contain alphanumeric characters, hyphens, and underscores
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        if not all(c in allowed_chars for c in v):
            raise ValueError("Video ID contains invalid characters")
        return v
    
    @validator("language")
    def validate_language(cls, v):
        """Validate language code format."""
        if v and len(v) not in [2, 5]:  # ISO 639-1 (2 chars) or locale format (5 chars)
            raise ValueError("Language code must be 2 or 5 characters (e.g., 'en' or 'en-US')")
        return v
    
    @validator("url")
    def validate_youtube_url(cls, v):
        """Validate that URL is a YouTube URL."""
        if not v:
            raise ValueError("URL is required")
        
        valid_domains = [
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "youtu.be"
        ]
        
        if not any(domain in v for domain in valid_domains):
            raise ValueError("URL must be a valid YouTube URL")
        
        return v
    
    @property
    def duration_formatted(self) -> Optional[str]:
        """Get duration in HH:MM:SS format."""
        if not self.duration_seconds:
            return None
        
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    @property
    def is_short_video(self) -> bool:
        """Check if video is a YouTube Short (< 60 seconds)."""
        return self.duration_seconds is not None and self.duration_seconds < 60
    
    def to_dict(self) -> dict:
        """Convert to dictionary with proper serialization."""
        return self.dict(exclude_none=True)
    
    @classmethod
    def from_youtube_api(cls, api_data: dict) -> "VideoMetadata":
        """Create VideoMetadata from YouTube API response."""
        snippet = api_data.get("snippet", {})
        statistics = api_data.get("statistics", {})
        content_details = api_data.get("contentDetails", {})
        
        # Parse duration from ISO 8601 format (PT4M13S -> 253 seconds)
        duration_str = content_details.get("duration", "")
        duration_seconds = cls._parse_iso_duration(duration_str) if duration_str else None
        
        # Parse upload date
        upload_date_str = snippet.get("publishedAt")
        upload_date = datetime.fromisoformat(upload_date_str.replace("Z", "+00:00")) if upload_date_str else None
        
        return cls(
            video_id=api_data["id"],
            title=snippet.get("title", ""),
            description=snippet.get("description"),
            channel_id=snippet.get("channelId", ""),
            channel_name=snippet.get("channelTitle", ""),
            duration_seconds=duration_seconds,
            view_count=int(statistics.get("viewCount", 0)) if statistics.get("viewCount") else None,
            like_count=int(statistics.get("likeCount", 0)) if statistics.get("likeCount") else None,
            upload_date=upload_date,
            language=snippet.get("defaultLanguage") or snippet.get("defaultAudioLanguage"),
            tags=snippet.get("tags", []),
            thumbnail_url=snippet.get("thumbnails", {}).get("maxresdefault", {}).get("url"),
            url=f"https://www.youtube.com/watch?v={api_data['id']}"
        )
    
    @staticmethod
    def _parse_iso_duration(duration_str: str) -> int:
        """Parse ISO 8601 duration to seconds."""
        import re
        
        # Pattern for PT1H2M3S format
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
```

### Step 2: Create tests/unit/models/test_video.py

```python
"""Tests for video metadata models."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from mindtube.models.video import VideoMetadata, VideoPrivacy

class TestVideoMetadata:
    """Test VideoMetadata model."""
    
    def test_valid_video_metadata(self):
        """Test creating valid video metadata."""
        metadata = VideoMetadata(
            video_id="dQw4w9WgXcQ",
            title="Test Video",
            channel_id="UCtest",
            channel_name="Test Channel",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        
        assert metadata.video_id == "dQw4w9WgXcQ"
        assert metadata.title == "Test Video"
        assert metadata.channel_id == "UCtest"
        assert metadata.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    def test_video_id_validation(self):
        """Test video ID validation."""
        # Valid video ID
        metadata = VideoMetadata(
            video_id="dQw4w9WgXcQ",
            title="Test",
            channel_id="UC123",
            channel_name="Test",
            url="https://youtube.com/watch?v=dQw4w9WgXcQ"
        )
        assert metadata.video_id == "dQw4w9WgXcQ"
        
        # Invalid video ID - too short
        with pytest.raises(ValidationError, match="Video ID must be 11 characters"):
            VideoMetadata(
                video_id="short",
                title="Test",
                channel_id="UC123",
                channel_name="Test",
                url="https://youtube.com/watch?v=short"
            )
        
        # Invalid video ID - invalid characters
        with pytest.raises(ValidationError, match="Video ID contains invalid characters"):
            VideoMetadata(
                video_id="invalid@#$%",
                title="Test",
                channel_id="UC123",
                channel_name="Test",
                url="https://youtube.com/watch?v=invalid"
            )
    
    def test_url_validation(self):
        """Test YouTube URL validation."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            metadata = VideoMetadata(
                video_id="dQw4w9WgXcQ",
                title="Test",
                channel_id="UC123",
                channel_name="Test",
                url=url
            )
            assert metadata.url == url
        
        # Invalid URL
        with pytest.raises(ValidationError, match="URL must be a valid YouTube URL"):
            VideoMetadata(
                video_id="dQw4w9WgXcQ",
                title="Test",
                channel_id="UC123",
                channel_name="Test",
                url="https://vimeo.com/123456"
            )
    
    def test_duration_formatted(self):
        """Test duration formatting."""
        # Test with hours
        metadata = VideoMetadata(
            video_id="dQw4w9WgXcQ",
            title="Test",
            channel_id="UC123",
            channel_name="Test",
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            duration_seconds=3661  # 1:01:01
        )
        assert metadata.duration_formatted == "01:01:01"
        
        # Test without hours
        metadata.duration_seconds = 125  # 2:05
        assert metadata.duration_formatted == "02:05"
        
        # Test None duration
        metadata.duration_seconds = None
        assert metadata.duration_formatted is None
    
    def test_is_short_video(self):
        """Test YouTube Shorts detection."""
        metadata = VideoMetadata(
            video_id="dQw4w9WgXcQ",
            title="Test",
            channel_id="UC123",
            channel_name="Test",
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            duration_seconds=30
        )
        assert metadata.is_short_video is True
        
        metadata.duration_seconds = 120
        assert metadata.is_short_video is False
        
        metadata.duration_seconds = None
        assert metadata.is_short_video is False
    
    def test_from_youtube_api(self):
        """Test creating metadata from YouTube API response."""
        api_data = {
            "id": "dQw4w9WgXcQ",
            "snippet": {
                "title": "Test Video",
                "description": "Test description",
                "channelId": "UCtest",
                "channelTitle": "Test Channel",
                "publishedAt": "2009-10-25T06:57:33Z",
                "defaultLanguage": "en",
                "tags": ["test", "video"],
                "thumbnails": {
                    "maxresdefault": {
                        "url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
                    }
                }
            },
            "statistics": {
                "viewCount": "1000000",
                "likeCount": "50000"
            },
            "contentDetails": {
                "duration": "PT3M33S"
            }
        }
        
        metadata = VideoMetadata.from_youtube_api(api_data)
        
        assert metadata.video_id == "dQw4w9WgXcQ"
        assert metadata.title == "Test Video"
        assert metadata.duration_seconds == 213  # 3:33
        assert metadata.view_count == 1000000
        assert metadata.language == "en"
        assert "test" in metadata.tags
    
    def test_parse_iso_duration(self):
        """Test ISO 8601 duration parsing."""
        assert VideoMetadata._parse_iso_duration("PT3M33S") == 213
        assert VideoMetadata._parse_iso_duration("PT1H2M3S") == 3723
        assert VideoMetadata._parse_iso_duration("PT45S") == 45
        assert VideoMetadata._parse_iso_duration("PT2M") == 120
        assert VideoMetadata._parse_iso_duration("PT1H") == 3600
        assert VideoMetadata._parse_iso_duration("") == 0
        assert VideoMetadata._parse_iso_duration("invalid") == 0
    
    def test_json_serialization(self):
        """Test JSON serialization."""
        metadata = VideoMetadata(
            video_id="dQw4w9WgXcQ",
            title="Test Video",
            channel_id="UC123",
            channel_name="Test Channel",
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            upload_date=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        data = metadata.to_dict()
        assert data["video_id"] == "dQw4w9WgXcQ"
        assert data["title"] == "Test Video"
        
        # Test JSON encoding
        json_str = metadata.json()
        assert "dQw4w9WgXcQ" in json_str
        assert "2023-01-01T12:00:00" in json_str
```

## Implementation Steps

### Step 1: Create Models Package
Ensure the models package structure exists:
```bash
mkdir -p mindtube/models
touch mindtube/models/__init__.py
```

### Step 2: Implement VideoMetadata Model
Create the video.py file with the complete VideoMetadata class.

### Step 3: Add Model to Package Init
Update `mindtube/models/__init__.py`:
```python
"""MindTube data models."""

from .video import VideoMetadata, VideoPrivacy

__all__ = ["VideoMetadata", "VideoPrivacy"]
```

### Step 4: Create Unit Tests
Implement comprehensive tests for the VideoMetadata model.

### Step 5: Test Implementation
```bash
make test tests/unit/models/test_video.py
```

## Testing

### Unit Tests
```bash
# Run video model tests
make test tests/unit/models/test_video.py

# Test specific functionality
python -c "
from mindtube.models.video import VideoMetadata
metadata = VideoMetadata(
    video_id='dQw4w9WgXcQ',
    title='Test',
    channel_id='UC123',
    channel_name='Test',
    url='https://youtube.com/watch?v=dQw4w9WgXcQ'
)
print(metadata.json(indent=2))
"
```

## Common Issues

### Issue 1: Validation Errors
**Problem**: Pydantic validation fails for certain inputs
**Solution**: Check validator methods and ensure proper error messages

### Issue 2: JSON Serialization Issues
**Problem**: DateTime objects not serializing properly
**Solution**: Use json_encoders in Config class

### Issue 3: YouTube API Integration
**Problem**: API response format doesn't match expected structure
**Solution**: Add defensive programming in from_youtube_api method