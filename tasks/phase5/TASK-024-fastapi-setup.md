# TASK-024: FastAPI Application Setup

## Task Information
- **ID**: TASK-024
- **Phase**: 5 - REST API
- **Estimate**: 60 minutes
- **Dependencies**: TASK-019
- **Status**: 🔴 Backlog

## Description
Set up FastAPI application with basic configuration, middleware, error handling, and documentation. This provides the foundation for the REST API interface.

## Acceptance Criteria
- [ ] Create FastAPI app factory
- [ ] Configure CORS
- [ ] Add request/response middleware
- [ ] Implement error handlers
- [ ] Add health check endpoint
- [ ] Configure OpenAPI documentation
- [ ] Add request logging
- [ ] Create basic API tests

## Implementation Details

### FastAPI App Factory
```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import uuid

def create_app(config: Config) -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="MindTube API",
        description="YouTube Learning Assistant API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Configure middleware
    setup_middleware(app, config)
    
    # Configure error handlers
    setup_error_handlers(app)
    
    # Add routes
    setup_routes(app)
    
    return app

def setup_middleware(app: FastAPI, config: Config) -> None:
    """Configure application middleware"""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.api.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware
    if config.api.trusted_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=config.api.trusted_hosts
        )
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        logger = logging.getLogger("mindtube.api")
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host
            }
        )
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time": process_time
            }
        )
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
```

### Error Handlers
```python
def setup_error_handlers(app: FastAPI) -> None:
    """Configure global error handlers"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "http_error",
                    "message": exc.detail,
                    "status_code": exc.status_code,
                    "request_id": getattr(request.state, "request_id", None)
                }
            }
        )
    
    @app.exception_handler(MindTubeException)
    async def mindtube_exception_handler(request: Request, exc: MindTubeException):
        status_code = 400
        if isinstance(exc, TranscriptNotAvailableError):
            status_code = 404
        elif isinstance(exc, RateLimitExceededError):
            status_code = 429
        elif isinstance(exc, ConfigurationError):
            status_code = 500
        
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "type": exc.__class__.__name__,
                    "message": exc.message,
                    "code": exc.error_code,
                    "details": exc.details,
                    "request_id": getattr(request.state, "request_id", None)
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger = logging.getLogger("mindtube.api")
        logger.exception(
            "Unhandled exception",
            extra={"request_id": getattr(request.state, "request_id", None)}
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "internal_error",
                    "message": "An internal error occurred",
                    "request_id": getattr(request.state, "request_id", None)
                }
            }
        )
```

### Health Check and Basic Routes
```python
def setup_routes(app: FastAPI) -> None:
    """Setup basic application routes"""
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    @app.get("/health/detailed", tags=["Health"])
    async def detailed_health_check():
        """Detailed health check with dependency status"""
        
        checks = {}
        overall_status = "healthy"
        
        # Check Azure OpenAI connectivity
        try:
            # Test Azure OpenAI connection
            checks["azure_openai"] = {"status": "healthy", "response_time": 0.1}
        except Exception as e:
            checks["azure_openai"] = {"status": "unhealthy", "error": str(e)}
            overall_status = "unhealthy"
        
        # Check cache system
        try:
            # Test cache connectivity
            checks["cache"] = {"status": "healthy"}
        except Exception as e:
            checks["cache"] = {"status": "unhealthy", "error": str(e)}
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "checks": checks
        }
    
    @app.get("/", tags=["Root"])
    async def root():
        """API root endpoint"""
        return {
            "name": "MindTube API",
            "version": "1.0.0",
            "description": "YouTube Learning Assistant API",
            "docs_url": "/docs",
            "health_url": "/health"
        }
```

### OpenAPI Configuration
```python
def configure_openapi(app: FastAPI) -> None:
    """Configure OpenAPI documentation"""
    
    app.openapi_tags = [
        {
            "name": "Health",
            "description": "Health check endpoints"
        },
        {
            "name": "Analysis",
            "description": "Video analysis operations"
        },
        {
            "name": "Transcript",
            "description": "Transcript extraction operations"
        }
    ]
    
    # Custom OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title="MindTube API",
            version="1.0.0",
            description="YouTube Learning Assistant API for extracting insights from videos",
            routes=app.routes,
        )
        
        # Add custom schema elements
        openapi_schema["info"]["contact"] = {
            "name": "MindTube Support",
            "email": "support@mindtube.com"
        }
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi
```

### Application Startup and Shutdown
```python
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger = logging.getLogger("mindtube.api")
    logger.info("Starting MindTube API")
    
    # Initialize services
    # - Database connections
    # - Cache connections
    # - External service health checks

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger = logging.getLogger("mindtube.api")
    logger.info("Shutting down MindTube API")
    
    # Cleanup tasks
    # - Close database connections
    # - Close cache connections
    # - Cleanup temporary files
```

### File Structure
```
mindtube/api/app.py
mindtube/api/middleware.py
mindtube/api/exceptions.py
mindtube/api/__init__.py
tests/unit/api/test_app.py
tests/integration/api/test_health.py
```

## Testing Requirements
- Test app factory creation
- Test middleware functionality
- Test error handler responses
- Test health check endpoints
- Test CORS configuration
- Test request logging
- Integration tests with real HTTP requests

## Definition of Done
- [ ] All acceptance criteria completed
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests passing
- [ ] OpenAPI documentation complete
- [ ] Error handling comprehensive
- [ ] Code follows project standards
- [ ] Documentation updated