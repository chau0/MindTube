# TASK-018: Output Formatting Stage

## Task Information
- **ID**: TASK-018
- **Phase**: 3 - Core Processing Engine
- **Estimate**: 60 minutes
- **Dependencies**: TASK-017, TASK-013
- **Status**: 🔴 Backlog

## Description
Implement output formatting and saving stage that converts analysis results into multiple formats and saves them using the storage adapter.

## Acceptance Criteria
- [ ] Create OutputStage class
- [ ] Support JSON output format
- [ ] Support Markdown output format
- [ ] Support HTML output format
- [ ] Implement template system
- [ ] Add file saving capabilities
- [ ] Create unit tests
- [ ] Add format validation tests

## Implementation Details

### OutputStage Class
```python
from mindtube.pipeline.base import PipelineStage, ProcessingRequest, ProcessingResult
from mindtube.adapters.storage import StorageAdapter, OutputFormat
from mindtube.models.analysis import VideoAnalysis
from jinja2 import Environment, FileSystemLoader

class OutputStage(PipelineStage):
    def __init__(self, storage_adapter: StorageAdapter):
        self.storage_adapter = storage_adapter
        self.template_env = Environment(loader=FileSystemLoader('templates'))
    
    async def process(self, request: ProcessingRequest) -> ProcessingResult:
        """Format and save analysis results"""
        pass
    
    def format_as_json(self, analysis: VideoAnalysis) -> str:
        """Convert to JSON format"""
        pass
    
    def format_as_markdown(self, analysis: VideoAnalysis) -> str:
        """Convert to Markdown format"""
        pass
    
    def format_as_html(self, analysis: VideoAnalysis) -> str:
        """Convert to HTML format"""
        pass
```

### Template System
```
templates/
├── markdown/
│   ├── summary.md.j2
│   ├── analysis.md.j2
│   └── mindmap.md.j2
├── html/
│   ├── summary.html.j2
│   ├── analysis.html.j2
│   └── mindmap.html.j2
└── base.html.j2
```

### Markdown Template Example
```markdown
# Video Analysis: {{ video_metadata.title }}

**Channel:** {{ video_metadata.channel_name }}
**Duration:** {{ video_metadata.duration }}
**Published:** {{ video_metadata.published_date }}

## Summary
{{ summary.content }}

## Key Ideas
{% for idea in key_ideas %}
- **{{ idea.title }}**: {{ idea.description }}
{% endfor %}

## Mindmap
```mermaid
{{ mindmap.mermaid_content }}
```
```

### HTML Template Features
- Responsive design
- Syntax highlighting for code
- Interactive mindmap rendering
- Print-friendly styles
- Dark/light theme support

### File Structure
```
mindtube/pipeline/output.py
mindtube/templates/
tests/unit/pipeline/test_output.py
tests/integration/test_output_formats.py
```

## Testing Requirements
- Test each output format independently
- Test template rendering
- Test file saving operations
- Validate generated HTML/Markdown syntax
- Test error handling for template errors
- Integration tests with storage adapter

## Definition of Done
- [ ] All acceptance criteria completed
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Template validation tests passing
- [ ] Output format validation complete
- [ ] Code follows project standards
- [ ] Documentation updated