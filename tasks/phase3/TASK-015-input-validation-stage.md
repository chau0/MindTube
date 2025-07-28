# TASK-015: Input Validation Stage

## Task Information
- **ID**: TASK-015
- **Phase**: 3 - Core Processing Engine
- **Estimate**: 60 minutes
- **Dependencies**: TASK-014
- **Status**: 🔴 Backlog

## Description
Implement URL validation and video metadata extraction stage. This is the first stage in the processing pipeline that validates YouTube URLs and extracts basic video information.

## Acceptance Criteria
- [ ] Create InputValidationStage class
- [ ] Validate YouTube URL formats
- [ ] Extract video ID from various URL formats
- [ ] Check video accessibility
- [ ] Gather basic metadata
- [ ] Implement comprehensive error handling
- [ ] Create unit tests with various URL formats
- [ ] Add integration tests

## Implementation Details

### InputValidationStage Class
```python
import re
from urllib.parse import urlparse, parse_qs
from mindtube.pipeline.base import PipelineStage, ProcessingRequest, ProcessingResult

class InputValidationStage(PipelineStage):
    def __init__(self):
        self.youtube_url_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        ]
    
    async def process(self, request: ProcessingRequest) -> ProcessingResult:
        """Validate URL and extract video metadata"""
        pass
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats"""
        pass
    
    def validate_video_id(self, video_id: str) -> bool:
        """Validate video ID format"""
        pass
    
    async def check_video_accessibility(self, video_id: str) -> bool:
        """Check if video is accessible"""
        pass
```

### Supported URL Formats
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://m.youtube.com/watch?v=VIDEO_ID`
- URLs with additional parameters

### Validation Rules
- Video ID must be exactly 11 characters
- Video ID can contain letters, numbers, hyphens, and underscores
- URL must be from YouTube domain
- Video must be publicly accessible

### File Structure
```
mindtube/pipeline/validation.py
tests/unit/pipeline/test_validation.py
tests/integration/test_validation_real_urls.py
```

## Testing Requirements
- Test all supported URL formats
- Test invalid URL handling
- Test video accessibility checking
- Test error message clarity
- Test edge cases (private videos, deleted videos)
- Integration tests with real YouTube URLs

## Definition of Done
- [ ] All acceptance criteria completed
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Error handling comprehensive
- [ ] Code follows project standards
- [ ] Documentation updated