# TASK-019: Core Engine Integration

## Task Information
- **ID**: TASK-019
- **Phase**: 3 - Core Processing Engine
- **Estimate**: 75 minutes
- **Dependencies**: TASK-018
- **Status**: 🔴 Backlog

## Description
Implement the main MindTubeEngine orchestrator that integrates all pipeline stages and provides the primary interface for video analysis operations.

## Acceptance Criteria
- [ ] Create MindTubeEngine class
- [ ] Integrate all pipeline stages
- [ ] Implement async processing
- [ ] Add progress tracking
- [ ] Implement error recovery
- [ ] Add performance monitoring
- [ ] Create comprehensive unit tests
- [ ] Add end-to-end integration tests

## Implementation Details

### MindTubeEngine Class
```python
from typing import List, Dict, Any, Optional, Callable
from mindtube.pipeline.base import Pipeline, ProcessingRequest, ProcessingResult
from mindtube.pipeline.validation import InputValidationStage
from mindtube.pipeline.transcript import TranscriptStage
from mindtube.pipeline.analysis import AnalysisStage
from mindtube.pipeline.output import OutputStage
from mindtube.models.analysis import VideoAnalysis

class MindTubeEngine:
    def __init__(self, config: Config):
        self.config = config
        self.pipeline = Pipeline()
        self._setup_pipeline()
    
    async def analyze_video(
        self, 
        video_url: str, 
        options: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> VideoAnalysis:
        """Main entry point for video analysis"""
        pass
    
    async def get_transcript_only(self, video_url: str) -> Transcript:
        """Get only the transcript without analysis"""
        pass
    
    async def analyze_transcript(self, transcript: Transcript) -> VideoAnalysis:
        """Analyze an existing transcript"""
        pass
    
    def _setup_pipeline(self) -> None:
        """Initialize and configure pipeline stages"""
        pass
```

### Progress Tracking
```python
class ProgressTracker:
    def __init__(self, callback: Optional[Callable[[str, float], None]] = None):
        self.callback = callback
        self.stages = [
            ("Validating input", 0.1),
            ("Fetching transcript", 0.3),
            ("Analyzing content", 0.7),
            ("Formatting output", 0.9),
            ("Complete", 1.0)
        ]
    
    async def update(self, stage_name: str, progress: float) -> None:
        """Update progress and notify callback"""
        if self.callback:
            self.callback(stage_name, progress)
```

### Error Recovery Strategies
- Retry failed stages with exponential backoff
- Graceful degradation (e.g., skip mindmap if LLM fails)
- Partial results return when possible
- Detailed error reporting with context

### Performance Monitoring
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    async def track_stage(self, stage_name: str, operation):
        """Track execution time and resource usage"""
        start_time = time.time()
        try:
            result = await operation()
            self.metrics[stage_name] = {
                'duration': time.time() - start_time,
                'success': True
            }
            return result
        except Exception as e:
            self.metrics[stage_name] = {
                'duration': time.time() - start_time,
                'success': False,
                'error': str(e)
            }
            raise
```

### Configuration Options
```python
@dataclass
class AnalysisOptions:
    output_formats: List[OutputFormat] = field(default_factory=lambda: [OutputFormat.JSON])
    language_preference: str = "en"
    include_transcript: bool = True
    include_summary: bool = True
    include_key_ideas: bool = True
    include_mindmap: bool = True
    save_to_file: bool = False
    output_directory: Optional[Path] = None
```

### File Structure
```
mindtube/core/engine.py
mindtube/core/progress.py
mindtube/core/monitoring.py
tests/unit/core/test_engine.py
tests/integration/test_engine_e2e.py
```

## Testing Requirements
- Test complete end-to-end workflows
- Test error recovery mechanisms
- Test progress tracking functionality
- Test performance monitoring
- Test partial failure scenarios
- Integration tests with real YouTube videos
- Load testing with multiple concurrent requests

## Definition of Done
- [ ] All acceptance criteria completed
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Performance benchmarks documented
- [ ] Error handling comprehensive
- [ ] Code follows project standards
- [ ] Documentation updated