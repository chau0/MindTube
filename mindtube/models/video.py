"""Video metadata models."""

from datetime import datetime
from enum import Enum
import re
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, validator


class VideoPrivacy(str, Enum):
    """Video privacy settings."""
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"

class VideoMetadata(BaseModel):
    """YouTube video metadata."""

    VIDEO_ID_LENGTH: ClassVar[int] = 11
    SHORT_VIDEO_THRESHOLD: ClassVar[int] = 60

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
        json_encoders: ClassVar = {
            datetime: lambda v: v.isoformat() if v else None
        }
        json_schema_extra: ClassVar = {
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
    def validate_video_id(cls, v: str) -> str:  # noqa: N805
        """Validate YouTube video ID format."""
        if not v or len(v) != cls.VIDEO_ID_LENGTH:
            raise ValueError("Video ID must be 11 characters long")
        # YouTube video IDs contain alphanumeric characters, hyphens, and underscores
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        if not all(c in allowed_chars for c in v):
            raise ValueError("Video ID contains invalid characters")
        return v

    @validator("language")
    def validate_language(cls, v: Optional[str]) -> Optional[str]:  # noqa: N805
        """Validate language code format."""
        if v and len(v) not in [2, 5]:  # ISO 639-1 (2 chars) or locale format (5 chars)
            raise ValueError("Language code must be 2 or 5 characters (e.g., 'en' or 'en-US')")
        return v

    @validator("url")
    def validate_youtube_url(cls, v: str) -> str:  # noqa: N805
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
        return self.duration_seconds is not None and self.duration_seconds < self.SHORT_VIDEO_THRESHOLD

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper serialization."""
        return self.model_dump(exclude_none=True)

    @classmethod
    def from_youtube_api(cls, api_data: Dict[str, Any]) -> "VideoMetadata":
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
            privacy=None,
            tags=snippet.get("tags", []),
            thumbnail_url=snippet.get("thumbnails", {}).get("maxresdefault", {}).get("url"),
            url=f"https://www.youtube.com/watch?v={api_data['id']}"
        )

    @staticmethod
    def _parse_iso_duration(duration_str: str) -> int:
        """Parse ISO 8601 duration to seconds."""

        # Pattern for PT1H2M3S format
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)

        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds

