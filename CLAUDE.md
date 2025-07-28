# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MindTube is a YouTube learning assistant that extracts structured knowledge from YouTube videos through transcripts, summaries, key ideas, and visual mindmaps. The system is designed as a modular, extensible platform supporting both CLI and API interfaces.

## Development Commands

### Project Setup
```bash
# Initialize project and install dependencies
make init
make install-deps
make install-dev-deps
```

### Testing
```bash
# Run all tests
make test

# Run specific test types
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/e2e/          # End-to-end tests
pytest tests/performance/  # Performance tests

# Run tests with coverage
pytest --cov=mindtube --cov-report=html
```

### Code Quality
```bash
# Linting and formatting
make lint
ruff check .
ruff format .

# Type checking
make typecheck
mypy mindtube/

# Security scanning
safety check
bandit -r mindtube/
```

### Development Server
```bash
# Start API server
make serve
# or
uvicorn mindtube.api.app:create_app --reload --host 0.0.0.0 --port 8000
```

### Build and Deployment
```bash
# Build Docker image
make docker-build

# Deploy to staging
make deploy-staging

# Create release
make release
```

## Architecture Overview

The project follows a modular architecture with clear separation of concerns:

```
mindtube/
├── core/           # Central orchestration engine
├── models/         # Data models (video, transcript, analysis, errors)
├── adapters/       # External service interfaces (YouTube, Azure OpenAI, Cache, Storage)
├── pipeline/       # Processing stages (validation, transcript, analysis, output)
├── cli/            # Command-line interface
├── api/            # REST API and WebSocket endpoints
└── cache/          # Multi-level caching system
```

### Key Components

- **Core Engine** (`mindtube/core/`): Central orchestration of all processing operations
- **Processing Pipeline** (`mindtube/pipeline/`): Sequential processing through validation, transcript acquisition, analysis, and output stages
- **Adapter Layer** (`mindtube/adapters/`): Abstraction for external services including YouTube API, Azure OpenAI, and caching
- **Data Models** (`mindtube/models/`): Structured data representations for video metadata, transcripts, summaries, and analysis results

### External Dependencies

- **YouTube Transcript API**: Uses `youtube_transcript_api` for transcript extraction with fallback to manual and auto-generated captions
- **Azure OpenAI**: Primary LLM service for content analysis, summarization, and key idea extraction
- **FastAPI**: Web framework for REST API endpoints
- **Typer**: CLI framework for command-line interface
- **Redis** (optional): Caching layer for improved performance

## Development Workflow

### Task Structure
The project uses a phase-based task system documented in `/tasks/`. Each phase builds upon previous work:
- **Phase 0**: Project foundation and setup
- **Phase 1**: Core data models
- **Phase 2**: External service adapters
- **Phase 3**: Processing pipeline
- **Phase 4**: CLI interface
- **Phase 5**: API endpoints
- **Phase 6**: Testing suite
- **Phase 7**: Documentation and deployment

### Configuration Management
- Environment variables for Azure OpenAI credentials (`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`)
- Configuration file at `~/.mindtube/config.yaml`
- Example configuration in `.env.example`

### Error Handling Strategy
The system implements graceful degradation with fallback mechanisms:
- Cached results when services fail
- Alternative transcript sources (manual → auto-generated → ASR)
- Retry mechanisms with exponential backoff
- Structured error responses with specific error codes

### Performance Considerations
- **Async Processing**: Non-blocking I/O operations throughout
- **Multi-level Caching**: Memory, file system, and optional database layers
- **Intelligent Caching**: TTL management and smart invalidation
- **Performance Targets**: Transcript extraction <5s, complete analysis <60s

### Security Measures
- Secure API key management for Azure OpenAI
- Input validation and sanitization
- Rate limiting to prevent abuse
- HTTPS-only communication
- No storage of personal information

## Testing Philosophy

- **Unit Tests**: Individual component testing with mocking
- **Integration Tests**: Service interaction testing
- **End-to-End Tests**: Complete workflow testing
- **Performance Tests**: Load and response time testing
- **Security Tests**: Vulnerability assessment

Test fixtures include sample transcripts, mock API responses, and deterministic LLM responses for consistent testing.

## Code Conventions

- **Async/Await**: Use async patterns throughout for I/O operations
- **Type Hints**: Full type annotation required (enforced by mypy)
- **Error Handling**: Structured exceptions with specific error types
- **Logging**: Structured logging with correlation IDs
- **Documentation**: Docstrings required for all public methods

## Common Development Patterns

### Adapter Pattern
All external services use the adapter pattern for consistent interfaces:
```python
class YouTubeAdapter:
    async def get_transcript(self, video_id: str) -> Transcript:
        # Implementation details
```

### Pipeline Stages
Processing stages follow a consistent interface:
```python
class ProcessingStage:
    async def process(self, request: ProcessingRequest) -> ProcessingResult:
        # Stage-specific processing
```

### Configuration Access
```python
from mindtube.core.config import get_config
config = get_config()
```

## Important Notes

- Always test with real YouTube videos during development but use mocked responses in automated tests
- Azure OpenAI credentials are required for LLM functionality
- The system is designed to handle rate limits and API failures gracefully
- Cache invalidation strategies are crucial for maintaining data consistency
- Performance monitoring is built into the pipeline for optimization insights
- **IMPORTANT**: Always update CHANGELOG.md when completing tasks - document what was implemented, changed, or fixed