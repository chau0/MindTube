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
        json_str = metadata.model_dump_json()
        assert "dQw4w9WgXcQ" in json_str
        assert "2023-01-01T12:00:00" in json_str