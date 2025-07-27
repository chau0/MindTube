# YouTube Transcript Integration Guide

## Overview

MindTube now includes robust YouTube transcript fetching capabilities using the `youtube-transcript-api` library with built-in proxy support to avoid IP blocking issues.

## Features

- **Automatic Video ID Extraction**: Supports various YouTube URL formats
- **Multi-language Support**: Fetches transcripts in preferred languages with fallback
- **Proxy Support**: Built-in Webshare and generic proxy support to avoid IP blocks
- **Error Handling**: Comprehensive error handling for various YouTube API issues
- **Fallback Mechanisms**: Graceful fallback when preferred languages aren't available

## Installation

The YouTube transcript functionality is included in the main requirements:

```bash
pip install youtube-transcript-api==0.6.2
```

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# YouTube Transcript API Proxy Configuration (Optional - for avoiding IP blocks)
# Webshare Proxy (Recommended for production)
WEBSHARE_PROXY_USERNAME=your-webshare-username
WEBSHARE_PROXY_PASSWORD=your-webshare-password

# Generic HTTP/HTTPS Proxy (Alternative to Webshare)
HTTP_PROXY_URL=http://user:pass@proxy.example.com:8080
HTTPS_PROXY_URL=https://user:pass@proxy.example.com:8080

# YouTube Transcript Preferences
YOUTUBE_TRANSCRIPT_LANGUAGES=["en", "en-US", "en-GB"]
```

### Proxy Setup

#### Webshare Proxy (Recommended)

1. Create a [Webshare account](https://www.webshare.io/?referral_code=w0xno53eb50g)
2. Purchase a "Residential" proxy package (NOT "Proxy Server" or "Static Residential")
3. Get your credentials from [Proxy Settings](https://dashboard.webshare.io/proxy/settings)
4. Set environment variables:
   ```bash
   WEBSHARE_PROXY_USERNAME=your-username
   WEBSHARE_PROXY_PASSWORD=your-password
   ```

#### Generic HTTP/HTTPS Proxy

For other proxy providers:
```bash
HTTP_PROXY_URL=http://user:pass@proxy.example.com:8080
HTTPS_PROXY_URL=https://user:pass@proxy.example.com:8080
```

## Usage

### Basic Usage

```python
from app.services.youtube_transcript import youtube_transcript_service

# Fetch transcript with automatic fallback
transcript = await youtube_transcript_service.fetch_transcript_with_fallback(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
)

# Each segment contains:
for segment in transcript:
    print(f"{segment.start_ms}ms - {segment.end_ms}ms: {segment.text}")
```

### Advanced Usage

```python
# Fetch with specific languages
transcript = await youtube_transcript_service.fetch_transcript(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    languages=['es', 'en'],  # Try Spanish first, then English
    preserve_formatting=True
)

# Get available transcript information
info = await youtube_transcript_service.get_available_transcripts(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
)
print(f"Available languages: {[t['language_code'] for t in info['available_transcripts']]}")
```

## Supported URL Formats

The service automatically extracts video IDs from various YouTube URL formats:

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://m.youtube.com/watch?v=VIDEO_ID`
- `VIDEO_ID` (direct video ID)

## Error Handling

The service handles various YouTube API errors gracefully:

### Common Errors

| Error | Description | Solution |
|-------|-------------|----------|
| `RequestBlocked` | IP blocked by YouTube | Configure proxy |
| `IpBlocked` | IP address banned | Use residential proxy |
| `TranscriptsDisabled` | Video has no transcripts | Try different video |
| `NoTranscriptFound` | Requested language unavailable | Use fallback method |
| `VideoUnavailable` | Video is private/deleted | Check video accessibility |

### Error Examples

```python
try:
    transcript = await youtube_transcript_service.fetch_transcript(video_url)
except ValueError as e:
    if "Request blocked" in str(e):
        print("Configure proxy to avoid IP blocking")
    elif "No transcript found" in str(e):
        print("Try different languages or use fallback method")
    else:
        print(f"Other error: {e}")
```

## Integration with MindTube Pipeline

The YouTube transcript service is integrated into the main video processing pipeline:

1. **Video Ingestion**: Extract video ID from submitted URL
2. **Transcript Fetching**: Fetch transcript with automatic language fallback
3. **Processing**: Convert to `TranscriptSegment` format for summarization
4. **Fallback**: Use mock transcript if YouTube fetch fails

## Testing

Run the comprehensive test suite:

```bash
cd backend
python -m pytest tests/unit/test_youtube_transcript.py -v
```

### Test Coverage

- Video ID extraction from various URL formats
- Proxy configuration (Webshare and generic)
- Transcript fetching with different languages
- Error handling for all YouTube API exceptions
- Fallback mechanisms
- Available transcript information retrieval

## Performance Considerations

### Proxy Usage

- **Webshare Residential**: Best for production, rotating IPs
- **Generic Proxy**: Good for development, static IP
- **No Proxy**: Works for limited requests, may get blocked

### Rate Limiting

YouTube may rate limit requests. The service includes:
- Automatic retry logic (built into youtube-transcript-api)
- Graceful error handling
- Fallback to mock data for development

## Troubleshooting

### Common Issues

1. **"Request blocked by YouTube"**
   - Solution: Configure Webshare or generic proxy
   - Check proxy credentials and connectivity

2. **"No transcript found"**
   - Use `get_available_transcripts()` to check available languages
   - Try `fetch_transcript_with_fallback()` for automatic language selection

3. **"Video is not available"**
   - Check if video is public and accessible
   - Verify video URL format

4. **Proxy connection errors**
   - Verify proxy credentials and URLs
   - Test proxy connectivity outside the application

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import structlog
logger = structlog.get_logger(__name__)
logger.setLevel("DEBUG")
```

## Security Considerations

- Store proxy credentials securely in environment variables
- Don't commit proxy credentials to version control
- Use residential proxies for production to avoid detection
- Monitor proxy usage and costs

## Cost Considerations

### Webshare Pricing

- Residential proxies: ~$2.99/GB
- Typical transcript fetch: ~10-50KB
- Estimate: ~1000-5000 transcripts per $1

### Alternatives

- Free tier: Limited requests without proxy
- Generic proxy: Lower cost but higher block risk
- Self-hosted proxy: Technical complexity but cost control

## Future Enhancements

- [ ] Caching layer for frequently accessed transcripts
- [ ] Support for subtitle translation
- [ ] Batch processing for multiple videos
- [ ] Integration with YouTube Data API for metadata
- [ ] Custom formatter support for different output formats