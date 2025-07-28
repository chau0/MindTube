# TASK-025: Analysis Endpoints

## Task Information
- **ID**: TASK-025
- **Phase**: 5 - REST API
- **Estimate**: 90 minutes
- **Dependencies**: TASK-024
- **Status**: 🔴 Backlog

## Description
Implement REST API endpoints for video analysis operations including transcript extraction, summarization, key ideas extraction, and mindmap generation. These endpoints provide the core functionality through HTTP API.

## Acceptance Criteria
- [ ] Create transcript extraction endpoint
- [ ] Create summarization endpoint
- [ ] Create key ideas extraction endpoint
- [ ] Create mindmap generation endpoint
- [ ] Implement request validation
- [ ] Add response models
- [ ] Handle async processing
- [ ] Create comprehensive API tests
- [ ] Add proper error handling
- [ ] Implement request/response logging

## Implementation Details

### API Endpoints Structure
```python
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from mindtube.core.engine import MindTubeEngine
from mindtube.models.analysis import AnalysisResult

router = APIRouter(prefix="/api/v1", tags=["analysis"])

class VideoAnalysisRequest(BaseModel):
    url: HttpUrl
    language: Optional[str] = "en"
    include_transcript: bool = True
    include_summary: bool = True
    include_key_ideas: bool = True
    include_mindmap: bool = False

class VideoAnalysisResponse(BaseModel):
    video_id: str
    title: str
    duration: int
    transcript: Optional[str] = None
    summary: Optional[str] = None
    key_ideas: Optional[List[str]] = None
    mindmap: Optional[str] = None
    processing_time: float
```

### Transcript Endpoint
```python
@router.post("/transcript", response_model=TranscriptResponse)
async def extract_transcript(
    request: TranscriptRequest,
    background_tasks: BackgroundTasks
) -> TranscriptResponse:
    """Extract transcript from YouTube video."""
    try:
        engine = MindTubeEngine()
        result = await engine.extract_transcript(
            url=str(request.url),
            language=request.language
        )
        
        return TranscriptResponse(
            video_id=result.video_metadata.video_id,
            title=result.video_metadata.title,
            duration=result.video_metadata.duration,
            transcript=result.transcript.to_text(),
            segments=result.transcript.segments,
            processing_time=result.processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Analysis Endpoint
```python
@router.post("/analyze", response_model=VideoAnalysisResponse)
async def analyze_video(
    request: VideoAnalysisRequest,
    background_tasks: BackgroundTasks
) -> VideoAnalysisResponse:
    """Perform comprehensive video analysis."""
    try:
        engine = MindTubeEngine()
        
        # Start analysis
        result = await engine.analyze_video(
            url=str(request.url),
            options={
                "language": request.language,
                "include_transcript": request.include_transcript,
                "include_summary": request.include_summary,
                "include_key_ideas": request.include_key_ideas,
                "include_mindmap": request.include_mindmap
            }
        )
        
        return VideoAnalysisResponse(
            video_id=result.video_metadata.video_id,
            title=result.video_metadata.title,
            duration=result.video_metadata.duration,
            transcript=result.transcript.to_text() if request.include_transcript else None,
            summary=result.summary if request.include_summary else None,
            key_ideas=result.key_ideas if request.include_key_ideas else None,
            mindmap=result.mindmap if request.include_mindmap else None,
            processing_time=result.processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Summary Endpoint
```python
@router.post("/summarize", response_model=SummaryResponse)
async def summarize_video(
    request: SummaryRequest
) -> SummaryResponse:
    """Generate video summary."""
    try:
        engine = MindTubeEngine()
        result = await engine.summarize_video(
            url=str(request.url),
            length=request.length,
            style=request.style
        )
        
        return SummaryResponse(
            video_id=result.video_metadata.video_id,
            title=result.video_metadata.title,
            summary=result.summary,
            key_points=result.key_points,
            processing_time=result.processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Key Ideas Endpoint
```python
@router.post("/key-ideas", response_model=KeyIdeasResponse)
async def extract_key_ideas(
    request: KeyIdeasRequest
) -> KeyIdeasResponse:
    """Extract key ideas from video."""
    try:
        engine = MindTubeEngine()
        result = await engine.extract_key_ideas(
            url=str(request.url),
            max_ideas=request.max_ideas,
            category_filter=request.categories
        )
        
        return KeyIdeasResponse(
            video_id=result.video_metadata.video_id,
            title=result.video_metadata.title,
            key_ideas=result.key_ideas,
            categories=result.categories,
            processing_time=result.processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Mindmap Endpoint
```python
@router.post("/mindmap", response_model=MindmapResponse)
async def generate_mindmap(
    request: MindmapRequest
) -> MindmapResponse:
    """Generate mindmap from video content."""
    try:
        engine = MindTubeEngine()
        result = await engine.generate_mindmap(
            url=str(request.url),
            format=request.format,
            max_nodes=request.max_nodes
        )
        
        return MindmapResponse(
            video_id=result.video_metadata.video_id,
            title=result.video_metadata.title,
            mindmap=result.mindmap,
            format=request.format,
            processing_time=result.processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Request/Response Models
```python
class TranscriptRequest(BaseModel):
    url: HttpUrl
    language: Optional[str] = "en"

class TranscriptResponse(BaseModel):
    video_id: str
    title: str
    duration: int
    transcript: str
    segments: List[dict]
    processing_time: float

class SummaryRequest(BaseModel):
    url: HttpUrl
    length: Optional[str] = "medium"  # short, medium, long
    style: Optional[str] = "bullet"  # bullet, paragraph, structured

class SummaryResponse(BaseModel):
    video_id: str
    title: str
    summary: str
    key_points: List[str]
    processing_time: float

class KeyIdeasRequest(BaseModel):
    url: HttpUrl
    max_ideas: Optional[int] = 10
    categories: Optional[List[str]] = None

class KeyIdeasResponse(BaseModel):
    video_id: str
    title: str
    key_ideas: List[str]
    categories: List[str]
    processing_time: float

class MindmapRequest(BaseModel):
    url: HttpUrl
    format: Optional[str] = "mermaid"  # mermaid, json
    max_nodes: Optional[int] = 20

class MindmapResponse(BaseModel):
    video_id: str
    title: str
    mindmap: str
    format: str
    processing_time: float
```

### Error Handling
```python
from fastapi import HTTPException
from mindtube.core.exceptions import (
    VideoNotFoundError,
    TranscriptNotAvailableError,
    AnalysisError
)

async def handle_analysis_errors(func):
    """Decorator for handling analysis errors."""
    try:
        return await func()
    except VideoNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Video not found: {e}")
    except TranscriptNotAvailableError as e:
        raise HTTPException(status_code=422, detail=f"Transcript not available: {e}")
    except AnalysisError as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
```

### File Structure
```
mindtube/api/endpoints/analysis.py
mindtube/api/models/requests.py
mindtube/api/models/responses.py
tests/unit/api/test_analysis_endpoints.py
tests/integration/api/test_analysis_flow.py
```

## Testing Requirements
- Test all endpoint request/response cycles
- Test error handling for invalid URLs
- Test async processing behavior
- Test request validation
- Test response serialization
- Integration tests with real YouTube videos
- Performance tests for concurrent requests
- Test rate limiting behavior

## Definition of Done
- [ ] All acceptance criteria completed
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests passing
- [ ] API documentation generated
- [ ] Error handling comprehensive
- [ ] Performance meets requirements
- [ ] Code follows project standards
- [ ] OpenAPI schema validated