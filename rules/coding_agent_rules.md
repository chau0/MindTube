# MindTube Coding Agent Rules

**Version:** 1.0  
**Last Updated:** 2025-01-27  
**Project:** MindTube - AI-Powered YouTube Video Summarizer

## 🎯 Project Overview

MindTube is an MVP-focused YouTube summarization tool that transforms long videos into actionable insights with timestamped summaries, key ideas, and takeaways. The architecture consists of:

- **Backend**: FastAPI (Python) with Azure OpenAI integration
- **Frontend**: Next.js 14 (TypeScript) with App Router
- **Architecture**: API-first design with clear separation of concerns

## 📁 Project Structure Rules

### Backend Structure (`backend/`)
```
backend/
├── app/
│   ├── api/           # API route handlers (ingest, status, results)
│   ├── core/          # Core configuration and logging
│   ├── services/      # Business logic services (LLM, summarization)
│   └── models/        # Data models and schemas (when created)
├── tests/
│   ├── unit/          # Unit tests for individual components
│   ├── integration/   # Integration tests for API endpoints
│   └── e2e/           # End-to-end workflow tests
└── data/              # Local data storage (artifacts, cache, logs)
```

### Frontend Structure (`frontend/src/`)
```
src/
├── app/               # Next.js App Router pages
├── components/        # Reusable React components
├── lib/               # Utilities (API client, store)
├── types/             # TypeScript type definitions
└── styles/            # Global styles (if needed)
```

## 🛠 Development Workflow Rules

### 1. Environment Setup
- **Always check for `.env` files** before running commands
- Use `make setup` for backend initialization
- Use `npm install` for frontend dependencies
- Run `./scripts/dev.sh` for full development environment

### 2. Package Management
- **Backend**: Use `uv` for Python package management (NOT pip)
- **Frontend**: Use `npm` for Node.js dependencies
- Update `pyproject.toml` for Python dependencies
- Update `package.json` for Node.js dependencies

### 3. Development Commands

#### Backend Commands (use Makefile)
```bash
cd backend
make setup          # Initial setup
make run            # Start development server
make test           # Run all tests
make test-unit      # Unit tests only
make test-integration # Integration tests only
make test-e2e       # End-to-end tests only
make lint           # Code linting
make format         # Code formatting
make build          # Validate application
```

#### Frontend Commands
```bash
cd frontend
npm run dev         # Development server
npm run build       # Production build
npm run test        # Run tests
npm run lint        # ESLint
npm run type-check  # TypeScript checking
```

## 🧪 Testing Rules

### Test-Driven Development (TDD)
- **Follow TDD cycle**: Red → Green → Refactor
- Write failing tests first, then implement code
- Use `make test-tdd` for TDD test runner
- Reference `docs/tdd_guide_be.md` for detailed TDD patterns

### Test Organization
- **Unit tests**: Test individual functions/classes in isolation
- **Integration tests**: Test API endpoints and service interactions
- **E2E tests**: Test complete user workflows
- Use fixtures from `tests/conftest.py` for common test data

### Test Naming Conventions
```python
# Test files: test_*.py
# Test classes: Test*
# Test functions: test_*

def test_should_create_job_when_valid_url_provided():
    # Given
    # When  
    # Then
```

### Mock Usage
- Use `MockAzureOpenAIClient` for LLM testing
- Mock external APIs (YouTube, Azure OpenAI) in tests
- Provide realistic test data via fixtures

## 🏗 Architecture Rules

### API Design
- **Follow REST conventions** for endpoint design
- Use Pydantic models for request/response validation
- Implement proper error handling with standardized error payloads
- Include CORS middleware for frontend communication

### Backend Services
- **Dependency Injection**: Services accept dependencies via constructor
- **Async/Await**: Use async patterns for I/O operations
- **Error Handling**: Use structured logging with job_id context
- **Configuration**: Use Pydantic BaseSettings for environment variables

### Frontend Components
- **Component Structure**: One component per file
- **TypeScript**: Strict typing for all props and state
- **State Management**: Use Zustand store for global state
- **API Integration**: Use centralized API client (`lib/api.ts`)

## 📝 Code Style Rules

### Python (Backend)
- **Formatting**: Use Black (line length: 88)
- **Import Sorting**: Use isort with Black profile
- **Type Hints**: Required for all function signatures
- **Docstrings**: Use Google-style docstrings
- **Linting**: flake8, mypy, bandit for security

```python
async def process_video(
    video_url: str, 
    enable_asr: bool = False
) -> ProcessingResult:
    """Process a YouTube video and generate summaries.
    
    Args:
        video_url: Valid YouTube URL
        enable_asr: Whether to use ASR fallback
        
    Returns:
        Complete processing result with summaries
        
    Raises:
        ValueError: If URL is invalid
        ProcessingError: If processing fails
    """
```

### TypeScript (Frontend)
- **Strict TypeScript**: Enable all strict mode options
- **Interface Definitions**: Define interfaces for all data structures
- **Component Props**: Type all component props
- **API Responses**: Use typed API client responses

```typescript
interface VideoIngestRequest {
  url: string;
  enable_asr?: boolean;
  language?: string;
}

const VideoUrlInput: React.FC = () => {
  // Component implementation
};
```

## 🔧 Configuration Rules

### Environment Variables
- **Backend**: Store in `backend/.env`
- **Frontend**: Store in `frontend/.env` with `NEXT_PUBLIC_` prefix
- **Required Keys**: Azure OpenAI credentials, YouTube API key
- **Optional Keys**: Mark clearly in configuration classes

### Settings Management
- Use `app.core.config.Settings` for backend configuration
- Use environment variables for frontend configuration
- Provide sensible defaults for development

## 🚀 Feature Development Rules

### Feature Implementation Process
1. **Check Feature Table**: Reference `docs/features.md` for requirements
2. **Write Tests First**: Follow TDD approach
3. **Implement Backend**: API → Service → Integration
4. **Implement Frontend**: Component → Integration → UI
5. **Test Integration**: End-to-end workflow testing

### API Endpoint Patterns
```python
# Standard endpoint structure
@router.post("/ingest")
async def ingest_video(
    request: VideoIngestRequest,
    background_tasks: BackgroundTasks
) -> JobResponse:
    # Validation
    # Job creation
    # Background processing
    # Response
```

### Component Patterns
```typescript
// Standard component structure
export const ComponentName: React.FC<Props> = ({ prop1, prop2 }) => {
  // Hooks
  // Event handlers
  // Render logic
  
  return (
    <div className="component-container">
      {/* JSX */}
    </div>
  );
};
```

## 🐛 Error Handling Rules

### Backend Error Handling
- Use structured logging with context
- Return standardized error responses
- Handle external API failures gracefully
- Implement fallback mechanisms

```python
try:
    result = await external_service.call()
except ExternalServiceError as e:
    logger.error("External service failed", job_id=job_id, error=str(e))
    # Implement fallback or re-raise with context
```

### Frontend Error Handling
- Display user-friendly error messages
- Use toast notifications for temporary errors
- Implement error boundaries for component errors
- Log errors for debugging

## 📊 Performance Rules

### Backend Performance
- **Async Operations**: Use async/await for I/O
- **Background Tasks**: Use FastAPI BackgroundTasks for long operations
- **Caching**: Implement transcript hash-based caching
- **Resource Limits**: Respect token limits and processing timeouts

### Frontend Performance
- **Code Splitting**: Use dynamic imports for large components
- **State Updates**: Minimize unnecessary re-renders
- **API Calls**: Implement proper loading states
- **Bundle Size**: Monitor and optimize bundle size

## 🔒 Security Rules

### API Security
- **Input Validation**: Validate all inputs with Pydantic
- **URL Validation**: Only accept valid YouTube URLs
- **Rate Limiting**: Implement request rate limiting
- **Secret Management**: Never log API keys or secrets

### Frontend Security
- **XSS Prevention**: Sanitize user inputs
- **HTTPS**: Use HTTPS in production
- **Environment Variables**: Use NEXT_PUBLIC_ prefix appropriately
- **Content Security Policy**: Implement CSP headers

## 📚 Documentation Rules

### Code Documentation
- **README Files**: Keep project README up-to-date
- **API Documentation**: Use FastAPI automatic docs
- **Component Documentation**: Document complex components
- **Architecture Docs**: Update design documents when architecture changes

### Commit Messages
```
feat: add video duration validation to ingest endpoint
fix: resolve Azure OpenAI timeout handling
docs: update API documentation for new endpoints
test: add integration tests for summarization service
refactor: extract common validation logic
```

## 🔄 Deployment Rules

### Local Development
- Use `./scripts/dev.sh` for full environment setup
- Ensure both backend and frontend start correctly
- Test API endpoints via `/docs` interface
- Verify frontend-backend communication

### Production Considerations
- **Environment Variables**: Set production values
- **Database**: Configure production database
- **Monitoring**: Enable structured logging
- **Performance**: Monitor token usage and costs

## ⚠️ Common Pitfalls to Avoid

1. **Don't use pip directly** - Always use `uv` for Python packages
2. **Don't skip tests** - Maintain test coverage above 80%
3. **Don't hardcode values** - Use configuration for all settings
4. **Don't ignore TypeScript errors** - Fix all type issues
5. **Don't commit secrets** - Use environment variables
6. **Don't break API contracts** - Maintain backward compatibility
7. **Don't skip error handling** - Handle all failure cases
8. **Don't ignore performance** - Monitor resource usage

## 🎯 MVP Focus Rules

### Priority Guidelines
- **P0 Features**: Must be implemented for MVP
- **P1 Features**: Nice-to-have for MVP window
- **Post-MVP**: Backlog items for future releases

### Quality Standards
- **Latency**: ≤15s for first summary (≤10min video with captions)
- **Completion Rate**: ≥95% jobs complete without retry
- **Test Coverage**: ≥80% for critical paths
- **Cost**: ≤$0.50 per video processing

## 🔧 Tool-Specific Rules

### VS Code / Cursor / Windsurf
- Use workspace settings for consistent formatting
- Enable TypeScript strict mode
- Configure Python path to use uv environment
- Use recommended extensions for Python and TypeScript

### Git Workflow
- Create feature branches for new development
- Use conventional commit messages
- Run tests before committing
- Keep commits focused and atomic

---

## 📞 Getting Help

When stuck or unsure:
1. Check existing documentation in `docs/`
2. Review similar implementations in the codebase
3. Run tests to understand expected behavior
4. Use `make help` for available backend commands
5. Check the TDD guide for testing patterns

Remember: **This is an MVP project** - focus on core functionality, maintain quality, and keep it simple!