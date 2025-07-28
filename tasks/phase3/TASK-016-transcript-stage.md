# TASK-016: Transcript Acquisition Stage

## Task Information
- **ID**: TASK-016
- **Phase**: 3 - Core Processing Engine
- **Estimate**: 75 minutes
- **Dependencies**: TASK-015, TASK-010, TASK-012
- **Status**: 🔴 Backlog

## Description
Implement transcript acquisition stage with caching support. This stage retrieves video transcripts using the YouTube adapter and implements intelligent caching strategies.

## Acceptance Criteria
- [ ] Create TranscriptStage class
- [ ] Integrate with YouTubeAdapter
- [ ] Implement cache checking
- [ ] Add fallback mechanisms
- [ ] Handle multiple languages
- [ ] Implement transcript quality scoring
- [ ] Create unit tests
- [ ] Add integration tests with caching

## Implementation Details

### TranscriptStage Class
```python
from mindtube.pipeline.base import PipelineStage, ProcessingRequest, ProcessingResult
from mindtube.adapters.youtube import YouTubeAdapter
from mindtube.adapters.cache import CacheAdapter
from mindtube.models.transcript import Transcript, TranscriptSource

class TranscriptStage(PipelineStage):
    def __init__(self, youtube_adapter: YouTubeAdapter, cache_adapter: CacheAdapter):
        self.youtube_adapter = youtube_adapter
        self.cache_adapter = cache_adapter
        self.preferred_languages = ['en', 'en-US', 'en-GB']
    
    async def process(self, request: ProcessingRequest) -> ProcessingResult:
        """Acquire transcript with caching"""
        pass
    
    async def get_cached_transcript(self, video_id: str, language: str) -> Optional[Transcript]:
        """Check cache for existing transcript"""
        pass
    
    async def fetch_transcript(self, video_id: str, language: str) -> Transcript:
        """Fetch transcript from YouTube"""
        pass
    
    def score_transcript_quality(self, transcript: Transcript) -> float:
        """Score transcript quality (0.0 to 1.0)"""
        pass
```

### Caching Strategy
- Cache key format: `transcript:{video_id}:{language}:{source}`
- TTL: 7 days for manual transcripts, 1 day for auto-generated
- Compression for large transcripts
- Cache invalidation on errors

### Language Fallback Logic
1. Try user-specified language
2. Try English variants (en, en-US, en-GB)
3. Try any available language
4. Return error if no transcripts available

### Quality Scoring Factors
- Manual vs auto-generated (manual = +0.3)
- Language match with preference (+0.2)
- Transcript completeness (+0.3)
- Timing accuracy (+0.2)

### File Structure
```
mindtube/pipeline/transcript.py
tests/unit/pipeline/test_transcript.py
tests/integration/test_transcript_caching.py
```

## Testing Requirements
- Test cache hit/miss scenarios
- Test language fallback logic
- Test quality scoring algorithm
- Test error handling for unavailable transcripts
- Test integration with YouTube adapter
- Performance tests with caching

## Definition of Done
- [ ] All acceptance criteria completed
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Caching performance verified
- [ ] Code follows project standards
- [ ] Documentation updated