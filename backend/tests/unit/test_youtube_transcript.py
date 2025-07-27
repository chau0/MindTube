"""
Unit tests for YouTube Transcript Service
Following TDD guide patterns
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import List

from app.services.youtube_transcript import YouTubeTranscriptService, youtube_transcript_service
from app.models.schemas import TranscriptSegment
from youtube_transcript_api._errors import (
    TranscriptsDisabled, 
    NoTranscriptFound, 
    VideoUnavailable,
    RequestBlocked,
    IpBlocked
)


class TestYouTubeTranscriptService:
    """Test YouTube Transcript Service functionality."""
    
    def test_extract_video_id_standard_url(self):
        """Test extracting video ID from standard YouTube URL."""
        service = YouTubeTranscriptService()
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = service.extract_video_id(url)
        
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_short_url(self):
        """Test extracting video ID from short YouTube URL."""
        service = YouTubeTranscriptService()
        
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = service.extract_video_id(url)
        
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_embed_url(self):
        """Test extracting video ID from embed YouTube URL."""
        service = YouTubeTranscriptService()
        
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        video_id = service.extract_video_id(url)
        
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_mobile_url(self):
        """Test extracting video ID from mobile YouTube URL."""
        service = YouTubeTranscriptService()
        
        url = "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = service.extract_video_id(url)
        
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_with_parameters(self):
        """Test extracting video ID from URL with additional parameters."""
        service = YouTubeTranscriptService()
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s&list=PLrAXtmRdnEQy"
        video_id = service.extract_video_id(url)
        
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_already_id(self):
        """Test when input is already a video ID."""
        service = YouTubeTranscriptService()
        
        video_id = "dQw4w9WgXcQ"
        result = service.extract_video_id(video_id)
        
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_video_id_invalid_url(self):
        """Test extracting video ID from invalid URL."""
        service = YouTubeTranscriptService()
        
        with pytest.raises(ValueError, match="Could not extract video ID"):
            service.extract_video_id("https://example.com/invalid")
    
    def test_extract_video_id_empty_string(self):
        """Test extracting video ID from empty string."""
        service = YouTubeTranscriptService()
        
        with pytest.raises(ValueError, match="Could not extract video ID"):
            service.extract_video_id("")
    
    @patch('app.services.youtube_transcript.YouTubeTranscriptApi')
    def test_initialization_without_proxy(self, mock_api_class):
        """Test service initialization without proxy configuration."""
        mock_api_instance = Mock()
        mock_api_class.return_value = mock_api_instance
        
        # Create service without proxy settings
        with patch('app.services.youtube_transcript.settings') as mock_settings:
            mock_settings.WEBSHARE_PROXY_USERNAME = None
            mock_settings.WEBSHARE_PROXY_PASSWORD = None
            mock_settings.HTTP_PROXY_URL = None
            mock_settings.HTTPS_PROXY_URL = None
            
            service = YouTubeTranscriptService()
        
        # Should initialize without proxy config
        mock_api_class.assert_called_once_with()
        assert service.api_client == mock_api_instance
    
    @patch('app.services.youtube_transcript.YouTubeTranscriptApi')
    @patch('app.services.youtube_transcript.WebshareProxyConfig')
    def test_initialization_with_webshare_proxy(self, mock_proxy_config, mock_api_class):
        """Test service initialization with Webshare proxy configuration."""
        mock_api_instance = Mock()
        mock_api_class.return_value = mock_api_instance
        mock_proxy_instance = Mock()
        mock_proxy_config.return_value = mock_proxy_instance
        
        # Create service with Webshare proxy settings
        with patch('app.services.youtube_transcript.settings') as mock_settings:
            mock_settings.WEBSHARE_PROXY_USERNAME = "test_user"
            mock_settings.WEBSHARE_PROXY_PASSWORD = "test_pass"
            mock_settings.HTTP_PROXY_URL = None
            mock_settings.HTTPS_PROXY_URL = None
            
            service = YouTubeTranscriptService()
        
        # Should initialize with Webshare proxy config
        mock_proxy_config.assert_called_once_with(
            proxy_username="test_user",
            proxy_password="test_pass"
        )
        mock_api_class.assert_called_once_with(proxy_config=mock_proxy_instance)
        assert service.api_client == mock_api_instance
    
    @patch('app.services.youtube_transcript.YouTubeTranscriptApi')
    @patch('app.services.youtube_transcript.GenericProxyConfig')
    def test_initialization_with_generic_proxy(self, mock_proxy_config, mock_api_class):
        """Test service initialization with generic proxy configuration."""
        mock_api_instance = Mock()
        mock_api_class.return_value = mock_api_instance
        mock_proxy_instance = Mock()
        mock_proxy_config.return_value = mock_proxy_instance
        
        # Create service with generic proxy settings
        with patch('app.services.youtube_transcript.settings') as mock_settings:
            mock_settings.WEBSHARE_PROXY_USERNAME = None
            mock_settings.WEBSHARE_PROXY_PASSWORD = None
            mock_settings.HTTP_PROXY_URL = "http://proxy:8080"
            mock_settings.HTTPS_PROXY_URL = "https://proxy:8080"
            
            service = YouTubeTranscriptService()
        
        # Should initialize with generic proxy config
        mock_proxy_config.assert_called_once_with(
            http_url="http://proxy:8080",
            https_url="https://proxy:8080"
        )
        mock_api_class.assert_called_once_with(proxy_config=mock_proxy_instance)
        assert service.api_client == mock_api_instance
    
    @pytest.mark.asyncio
    @patch('app.services.youtube_transcript.YouTubeTranscriptApi')
    async def test_fetch_transcript_success(self, mock_api_class):
        """Test successful transcript fetching."""
        # Setup mock transcript data
        mock_snippet_1 = Mock()
        mock_snippet_1.start = 0.0
        mock_snippet_1.duration = 5.0
        mock_snippet_1.text = "Hello world"
        
        mock_snippet_2 = Mock()
        mock_snippet_2.start = 5.0
        mock_snippet_2.duration = 3.0
        mock_snippet_2.text = "This is a test"
        
        mock_transcript = [mock_snippet_1, mock_snippet_2]
        
        mock_api_instance = Mock()
        mock_api_instance.fetch.return_value = mock_transcript
        mock_api_class.return_value = mock_api_instance
        
        service = YouTubeTranscriptService()
        
        # Test transcript fetching
        result = await service.fetch_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        # Verify API was called correctly
        mock_api_instance.fetch.assert_called_once_with(
            video_id="dQw4w9WgXcQ",
            languages=['en', 'en-US', 'en-GB'],
            preserve_formatting=False
        )
        
        # Verify result format
        assert len(result) == 2
        assert isinstance(result[0], TranscriptSegment)
        assert result[0].start_ms == 0
        assert result[0].end_ms == 5000
        assert result[0].text == "Hello world"
        assert result[1].start_ms == 5000
        assert result[1].end_ms == 8000
        assert result[1].text == "This is a test"
    
    @pytest.mark.asyncio
    @patch('app.services.youtube_transcript.YouTubeTranscriptApi')
    async def test_fetch_transcript_with_custom_languages(self, mock_api_class):
        """Test transcript fetching with custom language preferences."""
        mock_transcript = []
        mock_api_instance = Mock()
        mock_api_instance.fetch.return_value = mock_transcript
        mock_api_class.return_value = mock_api_instance
        
        service = YouTubeTranscriptService()
        
        # Test with custom languages
        await service.fetch_transcript(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            languages=['es', 'fr'],
            preserve_formatting=True
        )
        
        # Verify API was called with custom parameters
        mock_api_instance.fetch.assert_called_once_with(
            video_id="dQw4w9WgXcQ",
            languages=['es', 'fr'],
            preserve_formatting=True
        )
    
    @pytest.mark.asyncio
    @patch('app.services.youtube_transcript.YouTubeTranscriptApi')
    async def test_fetch_transcript_request_blocked(self, mock_api_class):
        """Test handling of RequestBlocked exception."""
        mock_api_instance = Mock()
        mock_api_instance.fetch.side_effect = RequestBlocked("Request blocked")
        mock_api_class.return_value = mock_api_instance
        
        service = YouTubeTranscriptService()
        
        with pytest.raises(ValueError, match="Request blocked by YouTube"):
            await service.fetch_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    @pytest.mark.asyncio
    @patch('app.services.youtube_transcript.YouTubeTranscriptApi')
    async def test_fetch_transcript_ip_blocked(self, mock_api_class):
        """Test handling of IpBlocked exception."""
        mock_api_instance = Mock()
        mock_api_instance.fetch.side_effect = IpBlocked("IP blocked")
        mock_api_class.return_value = mock_api_instance
        
        service = YouTubeTranscriptService()
        
        with pytest.raises(ValueError, match="Request blocked by YouTube"):
            await service.fetch_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    @pytest.mark.asyncio
    @patch('app.services.youtube_transcript.YouTubeTranscriptApi')
    async def test_fetch_transcript_transcripts_disabled(self, mock_api_class):
        """Test handling of TranscriptsDisabled exception."""
        mock_api_instance = Mock()
        mock_api_instance.fetch.side_effect = TranscriptsDisabled("Transcripts disabled")
        mock_api_class.return_value = mock_api_instance
        
        service = YouTubeTranscriptService()
        
        with pytest.raises(ValueError, match="Transcripts are disabled"):
            await service.fetch_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    @pytest.mark.asyncio
    @patch('app.services.youtube_transcript.YouTubeTranscriptApi')
    async def test_fetch_transcript_no_transcript_found(self, mock_api_class):
        """Test handling of NoTranscriptFound exception."""
        mock_api_instance = Mock()
        mock_api_instance.fetch.side_effect = NoTranscriptFound(
            video_id="test_video_id",
            requested_language_codes=["en"],
            transcript_data=Mock()
        )
        mock_api_class.return_value = mock_api_instance
        
        service = YouTubeTranscriptService()
        
        with pytest.raises(ValueError, match="No transcript found"):
            await service.fetch_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    @pytest.mark.asyncio
    @patch('app.services.youtube_transcript.YouTubeTranscriptApi')
    async def test_fetch_transcript_video_unavailable(self, mock_api_class):
        """Test handling of VideoUnavailable exception."""
        mock_api_instance = Mock()
        mock_api_instance.fetch.side_effect = VideoUnavailable("Video unavailable")
        mock_api_class.return_value = mock_api_instance
        
        service = YouTubeTranscriptService()
        
        with pytest.raises(ValueError, match="Video is not available"):
            await service.fetch_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    @pytest.mark.asyncio
    @patch('app.services.youtube_transcript.YouTubeTranscriptApi')
    async def test_get_available_transcripts(self, mock_api_class):
        """Test getting available transcript information."""
        # Setup mock transcript list
        mock_transcript_1 = Mock()
        mock_transcript_1.language = "English"
        mock_transcript_1.language_code = "en"
        mock_transcript_1.is_generated = False
        mock_transcript_1.is_translatable = True
        mock_transcript_1.translation_languages = ["es", "fr"]
        
        mock_transcript_2 = Mock()
        mock_transcript_2.language = "Spanish"
        mock_transcript_2.language_code = "es"
        mock_transcript_2.is_generated = True
        mock_transcript_2.is_translatable = False
        mock_transcript_2.translation_languages = []
        
        mock_transcript_list = [mock_transcript_1, mock_transcript_2]
        
        mock_api_instance = Mock()
        mock_api_instance.list.return_value = mock_transcript_list
        mock_api_class.return_value = mock_api_instance
        
        service = YouTubeTranscriptService()
        
        # Test getting available transcripts
        result = await service.get_available_transcripts("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        # Verify API was called correctly
        mock_api_instance.list.assert_called_once_with("dQw4w9WgXcQ")
        
        # Verify result format
        assert result["video_id"] == "dQw4w9WgXcQ"
        assert len(result["available_transcripts"]) == 2
        
        transcript_1 = result["available_transcripts"][0]
        assert transcript_1["language"] == "English"
        assert transcript_1["language_code"] == "en"
        assert transcript_1["is_generated"] == False
        assert transcript_1["is_translatable"] == True
        assert transcript_1["translation_languages"] == ["es", "fr"]
        
        transcript_2 = result["available_transcripts"][1]
        assert transcript_2["language"] == "Spanish"
        assert transcript_2["language_code"] == "es"
        assert transcript_2["is_generated"] == True
        assert transcript_2["is_translatable"] == False
        assert transcript_2["translation_languages"] == []
    
    @pytest.mark.asyncio
    @patch('app.services.youtube_transcript.YouTubeTranscriptService.fetch_transcript')
    async def test_fetch_transcript_with_fallback_preferred_success(self, mock_fetch):
        """Test fallback method when preferred languages work."""
        mock_segments = [
            TranscriptSegment(start_ms=0, end_ms=1000, text="Test segment")
        ]
        mock_fetch.return_value = mock_segments
        
        service = YouTubeTranscriptService()
        
        result = await service.fetch_transcript_with_fallback(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            preferred_languages=['en']
        )
        
        # Should call fetch_transcript with preferred languages
        mock_fetch.assert_called_once_with(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            ['en']
        )
        assert result == mock_segments
    
    @pytest.mark.asyncio
    @patch('app.services.youtube_transcript.YouTubeTranscriptService.get_available_transcripts')
    @patch('app.services.youtube_transcript.YouTubeTranscriptService.fetch_transcript')
    async def test_fetch_transcript_with_fallback_to_available(self, mock_fetch, mock_get_available):
        """Test fallback method when preferred languages fail but others are available."""
        # Setup mock for preferred language failure
        mock_fetch.side_effect = [
            ValueError("No transcript found for languages ['de']"),  # First call fails
            [TranscriptSegment(start_ms=0, end_ms=1000, text="Fallback segment")]  # Second call succeeds
        ]
        
        # Setup mock for available transcripts
        mock_get_available.return_value = {
            "video_id": "dQw4w9WgXcQ",
            "available_transcripts": [
                {
                    "language": "English",
                    "language_code": "en",
                    "is_generated": False
                },
                {
                    "language": "Spanish", 
                    "language_code": "es",
                    "is_generated": True
                }
            ]
        }
        
        service = YouTubeTranscriptService()
        
        result = await service.fetch_transcript_with_fallback(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            preferred_languages=['de']
        )
        
        # Should try preferred language first, then fallback to manual transcript
        assert mock_fetch.call_count == 2
        mock_fetch.assert_any_call("https://www.youtube.com/watch?v=dQw4w9WgXcQ", ['de'])
        mock_fetch.assert_any_call("https://www.youtube.com/watch?v=dQw4w9WgXcQ", ['en'])
        
        assert len(result) == 1
        assert result[0].text == "Fallback segment"
    
    @pytest.mark.asyncio
    @patch('app.services.youtube_transcript.YouTubeTranscriptService.get_available_transcripts')
    async def test_fetch_transcript_with_fallback_no_transcripts(self, mock_get_available):
        """Test fallback method when no transcripts are available."""
        # Setup mock for no available transcripts
        mock_get_available.return_value = {
            "video_id": "dQw4w9WgXcQ",
            "available_transcripts": []
        }
        
        service = YouTubeTranscriptService()
        
        with pytest.raises(ValueError, match="No transcripts available"):
            await service.fetch_transcript_with_fallback("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    def test_global_service_instance(self):
        """Test that global service instance is properly initialized."""
        assert youtube_transcript_service is not None
        assert isinstance(youtube_transcript_service, YouTubeTranscriptService)
        assert youtube_transcript_service.api_client is not None