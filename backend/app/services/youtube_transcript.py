"""
YouTube Transcript Service
Handles fetching transcripts from YouTube videos with proxy support
"""

import re
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
import structlog

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig, GenericProxyConfig
from youtube_transcript_api._errors import (
    TranscriptsDisabled, 
    NoTranscriptFound, 
    VideoUnavailable,
    RequestBlocked,
    IpBlocked
)

from app.models.schemas import TranscriptSegment
from app.core.config import settings

logger = structlog.get_logger(__name__)


class YouTubeTranscriptService:
    """Service for fetching YouTube video transcripts with proxy support"""
    
    def __init__(self):
        self.api_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize YouTube Transcript API client with proxy configuration"""
        try:
            proxy_config = self._get_proxy_config()
            
            if proxy_config:
                self.api_client = YouTubeTranscriptApi(proxy_config=proxy_config)
                logger.info("YouTube Transcript API initialized with proxy")
            else:
                self.api_client = YouTubeTranscriptApi()
                logger.info("YouTube Transcript API initialized without proxy")
                
        except Exception as e:
            logger.error("Failed to initialize YouTube Transcript API", error=str(e))
            # Fall back to basic client
            self.api_client = YouTubeTranscriptApi()
    
    def _get_proxy_config(self) -> Optional[Any]:
        """Get proxy configuration from environment variables"""
        # Check for Webshare proxy credentials
        webshare_username = getattr(settings, 'WEBSHARE_PROXY_USERNAME', None)
        webshare_password = getattr(settings, 'WEBSHARE_PROXY_PASSWORD', None)
        
        if webshare_username and webshare_password:
            logger.info("Using Webshare proxy configuration")
            return WebshareProxyConfig(
                proxy_username=webshare_username,
                proxy_password=webshare_password
            )
        
        # Check for generic HTTP/HTTPS proxy
        http_proxy = getattr(settings, 'HTTP_PROXY_URL', None)
        https_proxy = getattr(settings, 'HTTPS_PROXY_URL', None)
        
        if http_proxy or https_proxy:
            logger.info("Using generic proxy configuration")
            return GenericProxyConfig(
                http_url=http_proxy,
                https_url=https_proxy
            )
        
        return None
    
    def extract_video_id(self, url: str) -> str:
        """
        Extract YouTube video ID from various URL formats
        
        Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://m.youtube.com/watch?v=VIDEO_ID
        """
        # Remove any whitespace
        url = url.strip()
        
        # Pattern for different YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|m\.youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/.*[?&]v=([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                logger.info("Extracted video ID", video_id=video_id, url=url)
                return video_id
        
        # If no pattern matches, check if it's already a video ID
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            logger.info("Input is already a video ID", video_id=url)
            return url
        
        raise ValueError(f"Could not extract video ID from URL: {url}")
    
    async def fetch_transcript(
        self, 
        video_url: str, 
        languages: Optional[List[str]] = None,
        preserve_formatting: bool = False
    ) -> List[TranscriptSegment]:
        """
        Fetch transcript for a YouTube video
        
        Args:
            video_url: YouTube video URL or video ID
            languages: List of preferred language codes (e.g., ['en', 'es'])
            preserve_formatting: Whether to preserve HTML formatting
            
        Returns:
            List of transcript segments with timing information
            
        Raises:
            ValueError: If video ID cannot be extracted
            TranscriptsDisabled: If transcripts are disabled for the video
            NoTranscriptFound: If no transcript is available in requested languages
            VideoUnavailable: If the video is not available
            RequestBlocked/IpBlocked: If requests are blocked (proxy may help)
        """
        try:
            # Extract video ID from URL
            video_id = self.extract_video_id(video_url)
            
            # Set default languages if not provided
            if languages is None:
                languages = ['en', 'en-US', 'en-GB']
            
            logger.info(
                "Fetching transcript", 
                video_id=video_id, 
                languages=languages,
                preserve_formatting=preserve_formatting
            )
            
            # Fetch transcript using the API
            transcript = self.api_client.fetch(
                video_id=video_id,
                languages=languages,
                preserve_formatting=preserve_formatting
            )
            
            # Convert to our TranscriptSegment format
            segments = []
            for snippet in transcript:
                segment = TranscriptSegment(
                    start_ms=int(snippet.start * 1000),  # Convert seconds to milliseconds
                    end_ms=int((snippet.start + snippet.duration) * 1000),
                    text=snippet.text.strip()
                )
                segments.append(segment)
            
            logger.info(
                "Transcript fetched successfully", 
                video_id=video_id, 
                segment_count=len(segments),
                total_duration_ms=segments[-1].end_ms if segments else 0
            )
            
            return segments
            
        except (RequestBlocked, IpBlocked) as e:
            logger.error(
                "Request blocked - consider using proxy", 
                video_id=video_id if 'video_id' in locals() else 'unknown',
                error=str(e)
            )
            raise ValueError(f"Request blocked by YouTube. Consider configuring a proxy: {str(e)}")
            
        except TranscriptsDisabled as e:
            logger.error("Transcripts disabled for video", video_id=video_id, error=str(e))
            raise ValueError(f"Transcripts are disabled for this video: {str(e)}")
            
        except NoTranscriptFound as e:
            logger.error("No transcript found", video_id=video_id, languages=languages, error=str(e))
            raise ValueError(f"No transcript found for languages {languages}: {str(e)}")
            
        except VideoUnavailable as e:
            logger.error("Video unavailable", video_id=video_id, error=str(e))
            raise ValueError(f"Video is not available: {str(e)}")
            
        except Exception as e:
            logger.error("Unexpected error fetching transcript", video_id=video_id if 'video_id' in locals() else 'unknown', error=str(e))
            raise ValueError(f"Failed to fetch transcript: {str(e)}")
    
    async def get_available_transcripts(self, video_url: str) -> Dict[str, Any]:
        """
        Get information about available transcripts for a video
        
        Args:
            video_url: YouTube video URL or video ID
            
        Returns:
            Dictionary with available transcript information
        """
        try:
            video_id = self.extract_video_id(video_url)
            
            logger.info("Getting available transcripts", video_id=video_id)
            
            transcript_list = self.api_client.list(video_id)
            
            available_transcripts = []
            for transcript in transcript_list:
                available_transcripts.append({
                    'language': transcript.language,
                    'language_code': transcript.language_code,
                    'is_generated': transcript.is_generated,
                    'is_translatable': transcript.is_translatable,
                    'translation_languages': transcript.translation_languages
                })
            
            logger.info(
                "Available transcripts retrieved", 
                video_id=video_id, 
                transcript_count=len(available_transcripts)
            )
            
            return {
                'video_id': video_id,
                'available_transcripts': available_transcripts
            }
            
        except Exception as e:
            logger.error("Failed to get available transcripts", video_id=video_id if 'video_id' in locals() else 'unknown', error=str(e))
            raise ValueError(f"Failed to get available transcripts: {str(e)}")
    
    async def fetch_transcript_with_fallback(
        self, 
        video_url: str,
        preferred_languages: Optional[List[str]] = None
    ) -> List[TranscriptSegment]:
        """
        Fetch transcript with automatic fallback to available languages
        
        Args:
            video_url: YouTube video URL or video ID
            preferred_languages: List of preferred language codes
            
        Returns:
            List of transcript segments
        """
        try:
            # First try with preferred languages
            if preferred_languages:
                try:
                    return await self.fetch_transcript(video_url, preferred_languages)
                except ValueError as e:
                    if "No transcript found" not in str(e):
                        raise  # Re-raise if it's not a language issue
                    
                    logger.warning(
                        "Preferred languages not available, trying fallback", 
                        preferred_languages=preferred_languages,
                        error=str(e)
                    )
            
            # Get available transcripts and try the first available one
            available_info = await self.get_available_transcripts(video_url)
            available_transcripts = available_info['available_transcripts']
            
            if not available_transcripts:
                raise ValueError("No transcripts available for this video")
            
            # Try manually created transcripts first, then generated ones
            manual_transcripts = [t for t in available_transcripts if not t['is_generated']]
            if manual_transcripts:
                fallback_language = manual_transcripts[0]['language_code']
            else:
                fallback_language = available_transcripts[0]['language_code']
            
            logger.info(
                "Using fallback language", 
                fallback_language=fallback_language,
                is_generated=not bool(manual_transcripts)
            )
            
            return await self.fetch_transcript(video_url, [fallback_language])
            
        except Exception as e:
            logger.error("All transcript fetch attempts failed", error=str(e))
            raise


# Global service instance
youtube_transcript_service = YouTubeTranscriptService()