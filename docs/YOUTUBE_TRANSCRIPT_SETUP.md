# YouTube Transcript Setup Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Environment** (Optional - for proxy support)
   ```bash
   cp .env.example .env
   # Edit .env and add your proxy credentials if needed
   ```

3. **Test the Service**
   ```bash
   python3 -c "
   from app.services.youtube_transcript import youtube_transcript_service
   print('✅ Service ready!')
   "
   ```

## Proxy Configuration for Production

### Why Use a Proxy?

YouTube blocks many cloud provider IPs (AWS, GCP, Azure) and may rate limit requests. Using a residential proxy helps avoid these blocks.

### Webshare Setup (Recommended)

1. **Sign up**: [Webshare.io](https://www.webshare.io/?referral_code=w0xno53eb50g)
2. **Purchase**: "Residential" proxy package (NOT "Proxy Server")
3. **Get credentials**: From [Proxy Settings](https://dashboard.webshare.io/proxy/settings)
4. **Configure**:
   ```bash
   WEBSHARE_PROXY_USERNAME=your-username
   WEBSHARE_PROXY_PASSWORD=your-password
   ```

## Testing

Run the comprehensive test suite:

```bash
cd backend
python3 -m pytest tests/unit/test_youtube_transcript.py -v
```

## Usage Examples

### Basic Transcript Fetching

```python
from app.services.youtube_transcript import youtube_transcript_service

# Fetch transcript with automatic fallback
transcript = await youtube_transcript_service.fetch_transcript_with_fallback(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
)

for segment in transcript:
    print(f"{segment.start_ms}ms: {segment.text}")
```

### Error Handling

```python
try:
    transcript = await youtube_transcript_service.fetch_transcript(video_url)
except ValueError as e:
    if "Request blocked" in str(e):
        print("⚠️  Configure proxy to avoid IP blocking")
    elif "No transcript found" in str(e):
        print("⚠️  Try different languages or use fallback method")
    else:
        print(f"❌ Error: {e}")
```

## Integration Status

✅ **Implemented Features:**
- Video ID extraction from various YouTube URL formats
- Multi-language transcript fetching with fallback
- Webshare and generic proxy support
- Comprehensive error handling
- Integration with MindTube processing pipeline
- Full unit test coverage

✅ **API Integration:**
- Updated `ingest.py` to use real YouTube transcripts
- Fallback to mock data when YouTube fetch fails
- Proper error logging and handling

✅ **Configuration:**
- Environment variable support for proxy settings
- Language preference configuration
- Updated `.env.example` with all options

## Next Steps

1. **Production Deployment**: Configure Webshare proxy for production
2. **Monitoring**: Set up alerts for transcript fetch failures
3. **Caching**: Consider adding Redis caching for frequently accessed transcripts
4. **Rate Limiting**: Monitor YouTube API usage and implement backoff strategies

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "Request blocked" | Configure Webshare proxy |
| "No transcript found" | Use `fetch_transcript_with_fallback()` |
| "Video unavailable" | Check video is public and accessible |
| Import errors | Ensure `youtube-transcript-api` is installed |

### Debug Commands

```bash
# Test video ID extraction
python3 -c "
from app.services.youtube_transcript import YouTubeTranscriptService
service = YouTubeTranscriptService()
print(service.extract_video_id('https://www.youtube.com/watch?v=dQw4w9WgXcQ'))
"

# Test service initialization
python3 -c "
from app.services.youtube_transcript import youtube_transcript_service
print('Service initialized:', youtube_transcript_service.api_client is not None)
"
```