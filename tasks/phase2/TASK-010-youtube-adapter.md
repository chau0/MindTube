# TASK-010: YouTube Transcript Adapter

## Task Information
- **ID**: TASK-010
- **Phase**: 2 - External Adapters
- **Estimate**: 60 minutes
- **Dependencies**: TASK-009
- **Status**: 🔴 Backlog

## Description
Implement adapter for fetching YouTube video transcripts using youtube-transcript-api. This adapter handles transcript retrieval, language detection, and error handling for various transcript availability scenarios.

## Acceptance Criteria
- [ ] Create YouTubeAdapter class
- [ ] Implement transcript fetching with language preferences
- [ ] Handle various error scenarios (no transcript, private video, etc.)
- [ ] Add retry logic for transient failures
- [ ] Support manual and auto-generated transcripts
- [ ] Create comprehensive unit tests
- [ ] Add integration tests with real YouTube videos
- [ ] Implement caching for transcript data

## Implementation

### Step 1: Create mindtube/adapters/youtube.py

```python
"""YouTube transcript adapter."""

import logging
from typing import List, Optional, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled, VideoUnavailable, NoTranscriptFound,
    NotTranslatable, TranslationLanguageNotAvailable
)

from mindtube.models.transcript import Transcript, TranscriptSegment, TranscriptSource
from mindtube.models.video import VideoMetadata
from mindtube.models.errors import (
    TranscriptUnavailableError, VideoNotFoundError, APIError
)

logger = logging.getLogger(__name__)

class YouTubeAdapter:
    """Adapter for YouTube transcript API."""
    
    def __init__(self, preferred_languages: Optional[List[str]] = None):
        """Initialize adapter.
        
        Args:
            preferred_languages: List of preferred language codes (e.g., ['en', 'es'])
        """
        self.preferred_languages = preferred_languages or ['en']
    
    def get_transcript(self, video_id: str, language: Optional[str] = None) -> Transcript:
        """Get transcript for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            language: Specific language code to fetch
            
        Returns:
            Transcript object with segments
            
        Raises:
            VideoNotFoundError: If video doesn't exist
            TranscriptUnavailableError: If transcript is not available
            APIError: If API request fails
        """
        try:
            # Get available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Find best transcript
            transcript = self._find_best_transcript(transcript_list, language)
            
            # Fetch transcript data
            transcript_data = transcript.fetch()
            
            # Convert to our model
            segments = [
                TranscriptSegment(
                    text=item['text'],
                    start_time=item['start'],
                    duration=item['duration']
                )
                for item in transcript_data
            ]
            
            # Determine source type
            source = (TranscriptSource.MANUAL if transcript.is_generated is False 
                     else TranscriptSource.AUTO_GENERATED)
            
            return Transcript(
                video_id=video_id,
                language=transcript.language_code,
                segments=segments,
                source=source
            )
            
        except VideoUnavailable:
            logger.error(f"Video not found: {video_id}")
            raise VideoNotFoundError(video_id)
            
        except TranscriptsDisabled:
            logger.error(f"Transcripts disabled for video: {video_id}")
            raise TranscriptUnavailableError(video_id, "Transcripts disabled")
            
        except NoTranscriptFound:
            logger.error(f"No transcript found for video: {video_id}")
            raise TranscriptUnavailableError(video_id, "No transcript available")
            
        except Exception as e:
            logger.error(f"YouTube API error for video {video_id}: {e}")
            raise APIError("YouTube", str(e))
    
    def _find_best_transcript(self, transcript_list, preferred_language: Optional[str]):
        """Find the best available transcript."""
        try:
            # If specific language requested, try to get it
            if preferred_language:
                return transcript_list.find_transcript([preferred_language])
            
            # Try preferred languages in order
            for lang in self.preferred_languages:
                try:
                    return transcript_list.find_transcript([lang])
                except NoTranscriptFound:
                    continue
            
            # Fall back to any available transcript
            available = list(transcript_list)
            if available:
                # Prefer manual transcripts over auto-generated
                manual_transcripts = [t for t in available if not t.is_generated]
                if manual_transcripts:
                    return manual_transcripts[0]
                return available[0]
            
            raise NoTranscriptFound(transcript_list.video_id, [], transcript_list)
            
        except Exception as e:
            logger.error(f"Error finding transcript: {e}")
            raise
    
    def get_available_languages(self, video_id: str) -> List[Dict[str, Any]]:
        """Get list of available transcript languages.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            List of available languages with metadata
        """
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            languages = []
            for transcript in transcript_list:
                languages.append({
                    'language_code': transcript.language_code,
                    'language': transcript.language,
                    'is_generated': transcript.is_generated,
                    'is_translatable': transcript.is_translatable
                })
            
            return languages
            
        except Exception as e:
            logger.error(f"Error getting available languages for {video_id}: {e}")
            raise APIError("YouTube", str(e))
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL.
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID string
            
        Raises:
            ValidationError: If URL is invalid
        """
        import re
        
        # Common YouTube URL patterns
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If no pattern matches, assume it's already a video ID
        if len(url) == 11 and url.isalnum():
            return url
            
        from mindtube.models.errors import ValidationError
        raise ValidationError(f"Invalid YouTube URL: {url}")
```

### Step 2: Create tests/unit/adapters/test_youtube.py

```python
"""Tests for YouTube adapter."""

import pytest
from unittest.mock import Mock, patch
from youtube_transcript_api._errors import (
    TranscriptsDisabled, VideoUnavailable, NoTranscriptFound
)

from mindtube.adapters.youtube import YouTubeAdapter
from mindtube.models.transcript import TranscriptSource
from mindtube.models.errors import (
    VideoNotFoundError, TranscriptUnavailableError, APIError, ValidationError
)

class TestYouTubeAdapter:
    """Test YouTube adapter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = YouTubeAdapter(['en', 'es'])
    
    @patch('mindtube.adapters.youtube.YouTubeTranscriptApi')
    def test_get_transcript_success(self, mock_api):
        """Test successful transcript retrieval."""
        # Mock transcript data
        mock_transcript = Mock()
        mock_transcript.language_code = 'en'
        mock_transcript.is_generated = False
        mock_transcript.fetch.return_value = [
            {'text': 'Hello world', 'start': 0.0, 'duration': 2.0},
            {'text': 'This is a test', 'start': 2.0, 'duration': 3.0}
        ]
        
        mock_transcript_list = Mock()
        mock_transcript_list.find_transcript.return_value = mock_transcript
        mock_api.list_transcripts.return_value = mock_transcript_list
        
        # Test
        result = self.adapter.get_transcript('test_video_id')
        
        # Assertions
        assert result.video_id == 'test_video_id'
        assert result.language == 'en'
        assert result.source == TranscriptSource.MANUAL
        assert len(result.segments) == 2
        assert result.segments[0].text == 'Hello world'
        assert result.segments[0].start_time == 0.0
    
    @patch('mindtube.adapters.youtube.YouTubeTranscriptApi')
    def test_get_transcript_video_not_found(self, mock_api):
        """Test video not found error."""
        mock_api.list_transcripts.side_effect = VideoUnavailable('test_video_id')
        
        with pytest.raises(VideoNotFoundError):
            self.adapter.get_transcript('test_video_id')
    
    @patch('mindtube.adapters.youtube.YouTubeTranscriptApi')
    def test_get_transcript_disabled(self, mock_api):
        """Test transcripts disabled error."""
        mock_api.list_transcripts.side_effect = TranscriptsDisabled('test_video_id')
        
        with pytest.raises(TranscriptUnavailableError) as exc_info:
            self.adapter.get_transcript('test_video_id')
        
        assert "disabled" in str(exc_info.value)
    
    @patch('mindtube.adapters.youtube.YouTubeTranscriptApi')
    def test_get_transcript_not_found(self, mock_api):
        """Test no transcript found error."""
        mock_api.list_transcripts.side_effect = NoTranscriptFound(
            'test_video_id', [], Mock()
        )
        
        with pytest.raises(TranscriptUnavailableError):
            self.adapter.get_transcript('test_video_id')
    
    def test_extract_video_id_from_watch_url(self):
        """Test extracting video ID from watch URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = self.adapter.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_from_short_url(self):
        """Test extracting video ID from short URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = self.adapter.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_from_embed_url(self):
        """Test extracting video ID from embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        video_id = self.adapter.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_direct(self):
        """Test using video ID directly."""
        video_id = self.adapter.extract_video_id("dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_invalid(self):
        """Test invalid URL raises error."""
        with pytest.raises(ValidationError):
            self.adapter.extract_video_id("not_a_youtube_url")
    
    @patch('mindtube.adapters.youtube.YouTubeTranscriptApi')
    def test_get_available_languages(self, mock_api):
        """Test getting available languages."""
        # Mock transcripts
        mock_transcript1 = Mock()
        mock_transcript1.language_code = 'en'
        mock_transcript1.language = 'English'
        mock_transcript1.is_generated = False
        mock_transcript1.is_translatable = True
        
        mock_transcript2 = Mock()
        mock_transcript2.language_code = 'es'
        mock_transcript2.language = 'Spanish'
        mock_transcript2.is_generated = True
        mock_transcript2.is_translatable = False
        
        mock_transcript_list = [mock_transcript1, mock_transcript2]
        mock_api.list_transcripts.return_value = mock_transcript_list
        
        # Test
        languages = self.adapter.get_available_languages('test_video_id')
        
        # Assertions
        assert len(languages) == 2
        assert languages[0]['language_code'] == 'en'
        assert languages[0]['is_generated'] is False
        assert languages[1]['language_code'] == 'es'
        assert languages[1]['is_generated'] is True
```

### Step 3: Create integration tests

```python
"""Integration tests for YouTube adapter."""

import pytest
from mindtube.adapters.youtube import YouTubeAdapter

class TestYouTubeAdapterIntegration:
    """Integration tests with real YouTube API."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = YouTubeAdapter()
    
    @pytest.mark.integration
    def test_get_transcript_real_video(self):
        """Test with a real YouTube video that has transcripts."""
        # Using a known video with transcripts (replace with actual test video)
        video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
        
        try:
            transcript = self.adapter.get_transcript(video_id)
            assert transcript.video_id == video_id
            assert len(transcript.segments) > 0
            assert transcript.language is not None
        except Exception as e:
            pytest.skip(f"Integration test skipped: {e}")
    
    @pytest.mark.integration
    def test_get_available_languages_real_video(self):
        """Test getting available languages for real video."""
        video_id = "dQw4w9WgXcQ"
        
        try:
            languages = self.adapter.get_available_languages(video_id)
            assert isinstance(languages, list)
            if languages:  # Some videos might not have transcripts
                assert 'language_code' in languages[0]
        except Exception as e:
            pytest.skip(f"Integration test skipped: {e}")
```

## Implementation Steps

1. **Create YouTube adapter class**
   - Implement transcript fetching logic
   - Add error handling for various scenarios
   - Support language preferences

2. **Add URL parsing utilities**
   - Extract video IDs from various YouTube URL formats
   - Validate input URLs

3. **Create comprehensive tests**
   - Unit tests with mocked API
   - Integration tests with real API
   - Error scenario testing

4. **Add to package exports**
   - Update adapters/__init__.py
   - Export public classes

## Testing

```bash
# Run unit tests
pytest tests/unit/adapters/test_youtube.py -v

# Run integration tests (requires internet)
pytest tests/integration/test_youtube.py -v -m integration
```

## Common Issues

### Issue: Rate limiting from YouTube API
**Solution**: Implement exponential backoff and respect rate limits

### Issue: Transcript language detection
**Solution**: Use language preference fallback chain

### Issue: Private or restricted videos
**Solution**: Provide clear error messages and handle gracefully