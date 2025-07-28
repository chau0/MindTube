# TASK-032: API Documentation

## Task Information
- **ID**: TASK-032
- **Phase**: 7 - Documentation & Deployment
- **Estimate**: 60 minutes
- **Dependencies**: TASK-027
- **Status**: 🔴 Backlog

## Description
Create comprehensive API documentation including OpenAPI specification, endpoint examples, error responses, and interactive documentation. This ensures developers can easily integrate with the MindTube API.

## Acceptance Criteria
- [ ] Complete OpenAPI 3.0 specification
- [ ] Add detailed endpoint examples with request/response samples
- [ ] Document all error responses and status codes
- [ ] Create authentication and authorization guide
- [ ] Add rate limiting documentation
- [ ] Include WebSocket documentation
- [ ] Test documentation accuracy against actual API

## Implementation Details

### OpenAPI Specification

#### Enhanced API Schema
```python
# mindtube/api/docs.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def custom_openapi_schema(app: FastAPI):
    """Generate comprehensive OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="MindTube API",
        version="1.0.0",
        description="""
        # MindTube - YouTube Learning Assistant API
        
        Extract transcripts, summaries, key ideas, and mindmaps from YouTube videos.
        
        ## Features
        - 🎥 YouTube transcript extraction
        - 📝 AI-powered summarization
        - 💡 Key ideas extraction
        - 🗺️ Mindmap generation
        - ⚡ Real-time processing updates via WebSocket
        - 💾 Caching for improved performance
        
        ## Authentication
        API key authentication required for most endpoints.
        Include your API key in the Authorization header:
        ```
        Authorization: Bearer your_api_key_here
        ```
        
        ## Rate Limiting
        - 100 requests per hour per API key
        - Rate limit headers included in responses
        - WebSocket connections limited to 10 concurrent per key
        """,
        routes=app.routes,
        servers=[
            {"url": "https://api.mindtube.com", "description": "Production server"},
            {"url": "https://staging-api.mindtube.com", "description": "Staging server"},
            {"url": "http://localhost:8000", "description": "Development server"}
        ]
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "API key authentication. Format: 'Bearer your_api_key'"
        }
    }
    
    # Add common response schemas
    openapi_schema["components"]["schemas"].update({
        "ErrorResponse": {
            "type": "object",
            "properties": {
                "error": {"type": "string", "description": "Error type"},
                "message": {"type": "string", "description": "Human-readable error message"},
                "details": {"type": "object", "description": "Additional error details"},
                "request_id": {"type": "string", "description": "Unique request identifier"}
            },
            "required": ["error", "message"]
        },
        "RateLimitResponse": {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "rate_limit_exceeded"},
                "message": {"type": "string", "example": "Rate limit exceeded. Try again in 3600 seconds."},
                "retry_after": {"type": "integer", "description": "Seconds until rate limit resets"}
            }
        }
    })
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema
```

#### Detailed Endpoint Documentation
```python
# mindtube/api/endpoints.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List

class AnalyzeRequest(BaseModel):
    """Request model for video analysis"""
    url: str = Field(
        ..., 
        description="YouTube video URL",
        example="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        regex=r"^https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]{11}"
    )
    options: Optional[AnalysisOptions] = Field(
        default=AnalysisOptions(),
        description="Analysis configuration options"
    )

class AnalysisOptions(BaseModel):
    """Analysis configuration options"""
    include_summary: bool = Field(True, description="Include AI-generated summary")
    include_key_ideas: bool = Field(True, description="Extract key ideas")
    include_takeaways: bool = Field(True, description="Generate actionable takeaways")
    include_mindmap: bool = Field(True, description="Create mindmap visualization")
    summary_length: str = Field("medium", description="Summary length", regex="^(short|medium|long)$")
    format: str = Field("markdown", description="Output format", regex="^(markdown|json|text)$")

@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze YouTube Video",
    description="""
    Perform comprehensive analysis of a YouTube video including:
    
    - **Transcript extraction**: Get the full video transcript
    - **AI summarization**: Generate concise summary using Azure OpenAI
    - **Key ideas**: Extract main concepts and themes
    - **Takeaways**: Generate actionable insights
    - **Mindmap**: Create visual knowledge map in Mermaid format
    
    ### Processing Time
    - Short videos (< 10 min): ~30 seconds
    - Medium videos (10-30 min): ~60 seconds  
    - Long videos (> 30 min): ~120 seconds
    
    ### Caching
    Results are cached for 24 hours. Subsequent requests for the same video
    will return cached results immediately.
    """,
    responses={
        200: {
            "description": "Analysis completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "video_id": "dQw4w9WgXcQ",
                        "title": "Rick Astley - Never Gonna Give You Up",
                        "duration": 213,
                        "summary": "A classic 1980s pop song about unwavering commitment...",
                        "key_ideas": ["Commitment", "Loyalty", "80s Pop Culture"],
                        "takeaways": ["Never give up on your goals", "Stay committed to relationships"],
                        "mindmap": "```mermaid\nmindmap\n  root((Never Gonna Give You Up))\n    Themes\n      Commitment\n      Loyalty\n```",
                        "processing_time": 45.2,
                        "cached": False
                    }
                }
            }
        },
        400: {
            "description": "Invalid request",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_url": {
                            "summary": "Invalid YouTube URL",
                            "value": {
                                "error": "invalid_url",
                                "message": "The provided URL is not a valid YouTube video URL",
                                "details": {"url": "https://example.com/not-youtube"}
                            }
                        },
                        "video_not_found": {
                            "summary": "Video not accessible",
                            "value": {
                                "error": "video_not_found", 
                                "message": "Video is private, deleted, or does not exist",
                                "details": {"video_id": "invalid123"}
                            }
                        }
                    }
                }
            }
        },
        429: {
            "description": "Rate limit exceeded",
            "model": RateLimitResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    },
    tags=["Analysis"]
)
async def analyze_video(
    request: AnalyzeRequest,
    api_key: str = Depends(get_api_key)
):
    """Analyze YouTube video endpoint implementation"""
    pass
```

### Interactive Documentation

#### Swagger UI Customization
```python
# mindtube/api/app.py
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="MindTube API",
    docs_url=None,  # Disable default docs
    redoc_url=None  # Disable default redoc
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with enhanced styling"""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="MindTube API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.15.5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.15.5/swagger-ui.css",
        swagger_ui_parameters={
            "deepLinking": True,
            "displayRequestDuration": True,
            "docExpansion": "list",
            "operationsSorter": "method",
            "filter": True,
            "tryItOutEnabled": True
        }
    )

# Mount static files for custom documentation assets
app.mount("/static", StaticFiles(directory="static"), name="static")
```

### WebSocket Documentation

#### WebSocket API Guide
```markdown
# docs/websocket-api.md

## WebSocket API

### Connection
Connect to WebSocket endpoint for real-time processing updates:

```javascript
const ws = new WebSocket('wss://api.mindtube.com/ws');

// Authentication
ws.onopen = function() {
    ws.send(JSON.stringify({
        type: 'auth',
        api_key: 'your_api_key_here'
    }));
};
```

### Message Types

#### 1. Authentication
```json
{
    "type": "auth",
    "api_key": "your_api_key"
}
```

#### 2. Start Analysis
```json
{
    "type": "analyze",
    "url": "https://youtube.com/watch?v=VIDEO_ID",
    "options": {
        "include_summary": true,
        "include_mindmap": true
    }
}
```

#### 3. Progress Updates
```json
{
    "type": "progress",
    "stage": "transcript_extraction",
    "progress": 0.3,
    "message": "Extracting transcript..."
}
```

#### 4. Completion
```json
{
    "type": "complete",
    "result": {
        "summary": "...",
        "key_ideas": [...],
        "mindmap": "..."
    }
}
```

#### 5. Error
```json
{
    "type": "error",
    "error": "video_not_found",
    "message": "Video is not accessible"
}
```

### Example Client Implementation

```javascript
class MindTubeClient {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.ws = null;
    }
    
    connect() {
        this.ws = new WebSocket('wss://api.mindtube.com/ws');
        
        this.ws.onopen = () => {
            this.authenticate();
        };
        
        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };
    }
    
    authenticate() {
        this.send({
            type: 'auth',
            api_key: this.apiKey
        });
    }
    
    analyzeVideo(url, options = {}) {
        this.send({
            type: 'analyze',
            url: url,
            options: options
        });
    }
    
    handleMessage(message) {
        switch(message.type) {
            case 'progress':
                console.log(`Progress: ${message.progress * 100}% - ${message.message}`);
                break;
            case 'complete':
                console.log('Analysis complete:', message.result);
                break;
            case 'error':
                console.error('Error:', message.message);
                break;
        }
    }
    
    send(message) {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }
}
```
```

### Code Examples Collection

#### SDK Examples
```python
# docs/examples/python_sdk.py
"""
MindTube Python SDK Examples
"""
import asyncio
from mindtube_client import MindTubeClient

async def basic_analysis():
    """Basic video analysis example"""
    client = MindTubeClient(api_key="your_api_key")
    
    result = await client.analyze(
        url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        options={
            "include_summary": True,
            "include_mindmap": True,
            "summary_length": "medium"
        }
    )
    
    print(f"Title: {result.title}")
    print(f"Summary: {result.summary}")
    print(f"Key Ideas: {', '.join(result.key_ideas)}")

async def batch_analysis():
    """Batch processing example"""
    client = MindTubeClient(api_key="your_api_key")
    
    urls = [
        "https://youtube.com/watch?v=video1",
        "https://youtube.com/watch?v=video2",
        "https://youtube.com/watch?v=video3"
    ]
    
    tasks = [client.analyze(url) for url in urls]
    results = await asyncio.gather(*tasks)
    
    for result in results:
        print(f"Processed: {result.title}")

if __name__ == "__main__":
    asyncio.run(basic_analysis())
```

### Documentation Testing

#### API Documentation Tests
```python
# tests/docs/test_api_documentation.py
import pytest
import requests
from fastapi.testclient import TestClient
from mindtube.api.app import app

class TestAPIDocumentation:
    
    def test_openapi_schema_valid(self):
        """Test that OpenAPI schema is valid"""
        client = TestClient(app)
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        # Validate required OpenAPI fields
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        assert schema["openapi"].startswith("3.")
    
    def test_docs_accessible(self):
        """Test that documentation pages are accessible"""
        client = TestClient(app)
        
        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()
        
        # Test ReDoc (if enabled)
        response = client.get("/redoc")
        if response.status_code == 200:
            assert "redoc" in response.text.lower()
    
    def test_example_requests_valid(self):
        """Test that example requests in docs are valid"""
        client = TestClient(app)
        
        # Get OpenAPI schema
        schema_response = client.get("/openapi.json")
        schema = schema_response.json()
        
        # Test examples from analyze endpoint
        analyze_examples = schema["paths"]["/analyze"]["post"]["requestBody"]["content"]["application/json"]["examples"]
        
        for example_name, example_data in analyze_examples.items():
            # Validate example against actual endpoint
            response = client.post("/analyze", json=example_data["value"])
            # Should not fail due to schema validation
            assert response.status_code != 422, f"Example {example_name} has invalid schema"
```

## Documentation Structure

### File Organization
```
docs/
├── api/
│   ├── openapi.json
│   ├── endpoints.md
│   ├── authentication.md
│   ├── rate-limiting.md
│   └── websocket.md
├── examples/
│   ├── python_sdk.py
│   ├── javascript_client.js
│   ├── curl_examples.sh
│   └── postman_collection.json
├── guides/
│   ├── quick-start.md
│   ├── error-handling.md
│   └── best-practices.md
└── static/
    ├── logo.png
    ├── architecture.png
    └── custom.css
```

## Definition of Done
- [ ] All acceptance criteria completed
- [ ] OpenAPI specification complete and valid
- [ ] Interactive documentation accessible
- [ ] All endpoints documented with examples
- [ ] WebSocket API documented
- [ ] Code examples tested and working
- [ ] Documentation accuracy verified