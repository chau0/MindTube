# TASK-017: Analysis Stage

## Task Information
- **ID**: TASK-017
- **Phase**: 3 - Core Processing Engine
- **Estimate**: 90 minutes
- **Dependencies**: TASK-016, TASK-011
- **Status**: 🔴 Backlog

## Description
Implement LLM-based content analysis stage that generates summaries, extracts key ideas, and creates mindmaps using Azure OpenAI integration.

## Acceptance Criteria
- [ ] Create AnalysisStage class
- [ ] Integrate with AzureOpenAIAdapter
- [ ] Implement summary generation
- [ ] Implement key ideas extraction
- [ ] Implement mindmap generation
- [ ] Add prompt management
- [ ] Handle large transcripts (chunking)
- [ ] Create unit tests
- [ ] Add integration tests

## Implementation Details

### AnalysisStage Class
```python
from mindtube.pipeline.base import PipelineStage, ProcessingRequest, ProcessingResult
from mindtube.adapters.azure_openai import AzureOpenAIAdapter
from mindtube.models.transcript import Transcript
from mindtube.models.analysis import VideoAnalysis, Summary, KeyIdea, Mindmap

class AnalysisStage(PipelineStage):
    def __init__(self, llm_adapter: AzureOpenAIAdapter):
        self.llm_adapter = llm_adapter
        self.max_chunk_size = 4000  # tokens
        self.chunk_overlap = 200    # tokens
    
    async def process(self, request: ProcessingRequest) -> ProcessingResult:
        """Perform LLM analysis on transcript"""
        pass
    
    async def generate_summary(self, transcript: Transcript) -> Summary:
        """Generate concise summary"""
        pass
    
    async def extract_key_ideas(self, transcript: Transcript) -> List[KeyIdea]:
        """Extract main ideas and takeaways"""
        pass
    
    async def generate_mindmap(self, transcript: Transcript) -> Mindmap:
        """Create visual mindmap in Mermaid format"""
        pass
    
    def chunk_transcript(self, transcript: Transcript) -> List[str]:
        """Split large transcripts into manageable chunks"""
        pass
```

### Prompt Templates
```python
SUMMARY_PROMPT = """
Analyze the following video transcript and create a concise summary.
Focus on the main points, key insights, and actionable takeaways.

Transcript:
{transcript_text}

Summary:
"""

KEY_IDEAS_PROMPT = """
Extract the key ideas and main concepts from this video transcript.
Identify the most important points that viewers should remember.

Transcript:
{transcript_text}

Key Ideas:
"""

MINDMAP_PROMPT = """
Create a mindmap in Mermaid format for this video transcript.
Organize the content hierarchically with main topics and subtopics.

Transcript:
{transcript_text}

Mindmap (Mermaid format):
"""
```

### Chunking Strategy
- Split on sentence boundaries
- Maintain context with overlap
- Preserve semantic coherence
- Merge results from multiple chunks

### File Structure
```
mindtube/pipeline/analysis.py
mindtube/pipeline/prompts.py
tests/unit/pipeline/test_analysis.py
tests/integration/test_analysis_llm.py
```

## Testing Requirements
- Test each analysis type independently
- Test chunking for large transcripts
- Test prompt template rendering
- Test error handling for LLM failures
- Test result merging from multiple chunks
- Integration tests with real Azure OpenAI

## Definition of Done
- [ ] All acceptance criteria completed
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Prompt templates optimized
- [ ] Code follows project standards
- [ ] Documentation updated