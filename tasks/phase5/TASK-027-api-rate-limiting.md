# TASK-027: API Rate Limiting

## Task Information
- **ID**: TASK-027
- **Phase**: 5 - REST API
- **Estimate**: 45 minutes
- **Dependencies**: TASK-026
- **Status**: 🔴 Backlog

## Description
Implement rate limiting and request throttling for the FastAPI application to prevent abuse and ensure fair usage. This includes per-endpoint limits, user-based limiting, and proper error handling.

## Acceptance Criteria
- [ ] Add rate limiting middleware
- [ ] Configure limits per endpoint
- [ ] Implement user-based limiting
- [ ] Add rate limit headers
- [ ] Handle rate limit exceeded errors
- [ ] Create rate limiting tests
- [ ] Add monitoring metrics

## Implementation Details

### Rate Limiting Middleware
```python
# mindtube/api/middleware/rate_limit.py
from typing import Dict, Optional
import time
import asyncio
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window algorithm"""
    
    def __init__(
        self,
        app,
        calls: int = 100,
        period: int = 60,
        per_user: bool = True,
        storage: Optional[object] = None
    ):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.per_user = per_user
        self.storage = storage or InMemoryStorage()
        
    async def dispatch(self, request: Request, call_next):
        # Get client identifier
        client_id = self._get_client_id(request)
        endpoint = f"{request.method}:{request.url.path}"
        
        # Check rate limit
        allowed, remaining, reset_time = await self._check_rate_limit(
            client_id, endpoint
        )
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(self.calls),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset_time)),
                    "Retry-After": str(int(reset_time - time.time()))
                }
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_time))
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        if self.per_user:
            # Try to get user ID from auth
            user_id = getattr(request.state, 'user_id', None)
            if user_id:
                return f"user:{user_id}"
        
        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"
        
        return f"ip:{request.client.host}"
    
    async def _check_rate_limit(
        self, 
        client_id: str, 
        endpoint: str
    ) -> tuple[bool, int, float]:
        """Check if request is within rate limit"""
        key = f"{client_id}:{endpoint}"
        now = time.time()
        window_start = now - self.period
        
        # Get request timestamps
        timestamps = await self.storage.get_timestamps(key, window_start)
        
        # Add current request
        timestamps.append(now)
        await self.storage.set_timestamps(key, timestamps, self.period)
        
        # Check if within limit
        request_count = len(timestamps)
        remaining = max(0, self.calls - request_count)
        reset_time = now + self.period
        
        return request_count <= self.calls, remaining, reset_time


class InMemoryStorage:
    """In-memory storage for rate limiting (development only)"""
    
    def __init__(self):
        self._data: Dict[str, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()
    
    async def get_timestamps(self, key: str, window_start: float) -> list[float]:
        async with self._lock:
            timestamps = self._data[key]
            # Remove old timestamps
            while timestamps and timestamps[0] < window_start:
                timestamps.popleft()
            return list(timestamps)
    
    async def set_timestamps(self, key: str, timestamps: list[float], ttl: int):
        async with self._lock:
            self._data[key] = deque(timestamps)


class RedisStorage:
    """Redis storage for rate limiting (production)"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def get_timestamps(self, key: str, window_start: float) -> list[float]:
        # Remove old timestamps
        await self.redis.zremrangebyscore(key, 0, window_start)
        
        # Get current timestamps
        timestamps = await self.redis.zrange(key, 0, -1)
        return [float(ts) for ts in timestamps]
    
    async def set_timestamps(self, key: str, timestamps: list[float], ttl: int):
        if not timestamps:
            return
        
        # Add new timestamp
        latest = timestamps[-1]
        await self.redis.zadd(key, {str(latest): latest})
        await self.redis.expire(key, ttl)
```

### Rate Limit Configuration
```python
# mindtube/api/config/rate_limits.py
from typing import Dict, NamedTuple

class RateLimit(NamedTuple):
    calls: int
    period: int  # seconds

# Rate limits per endpoint
RATE_LIMITS: Dict[str, RateLimit] = {
    # Analysis endpoints - more restrictive
    "POST:/api/v1/analyze": RateLimit(calls=10, period=60),
    "POST:/api/v1/summarize": RateLimit(calls=15, period=60),
    "POST:/api/v1/mindmap": RateLimit(calls=5, period=60),
    
    # Transcript endpoints - moderate
    "POST:/api/v1/transcript": RateLimit(calls=30, period=60),
    
    # Status endpoints - lenient
    "GET:/api/v1/status": RateLimit(calls=100, period=60),
    "GET:/api/v1/health": RateLimit(calls=200, period=60),
    
    # WebSocket - connection based
    "WS:/api/v1/ws": RateLimit(calls=5, period=300),  # 5 connections per 5 minutes
}

# Default rate limit
DEFAULT_RATE_LIMIT = RateLimit(calls=60, period=60)

def get_rate_limit(method: str, path: str) -> RateLimit:
    """Get rate limit for specific endpoint"""
    key = f"{method}:{path}"
    return RATE_LIMITS.get(key, DEFAULT_RATE_LIMIT)
```

### Enhanced Middleware with Per-Endpoint Limits
```python
# mindtube/api/middleware/enhanced_rate_limit.py
from .rate_limit import RateLimitMiddleware
from ..config.rate_limits import get_rate_limit

class EnhancedRateLimitMiddleware(RateLimitMiddleware):
    """Rate limiting with per-endpoint configuration"""
    
    async def dispatch(self, request: Request, call_next):
        # Get endpoint-specific rate limit
        rate_limit = get_rate_limit(request.method, request.url.path)
        
        # Temporarily override instance limits
        original_calls = self.calls
        original_period = self.period
        
        self.calls = rate_limit.calls
        self.period = rate_limit.period
        
        try:
            response = await super().dispatch(request, call_next)
            return response
        finally:
            # Restore original limits
            self.calls = original_calls
            self.period = original_period
```

### FastAPI Integration
```python
# mindtube/api/app.py
from fastapi import FastAPI
from .middleware.enhanced_rate_limit import EnhancedRateLimitMiddleware
from .config.settings import get_settings

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="MindTube API")
    
    # Add rate limiting middleware
    if settings.enable_rate_limiting:
        app.add_middleware(
            EnhancedRateLimitMiddleware,
            per_user=True,
            storage=get_rate_limit_storage(settings)
        )
    
    return app

def get_rate_limit_storage(settings):
    """Get appropriate storage backend for rate limiting"""
    if settings.redis_url:
        import redis.asyncio as redis
        from .middleware.rate_limit import RedisStorage
        
        redis_client = redis.from_url(settings.redis_url)
        return RedisStorage(redis_client)
    else:
        from .middleware.rate_limit import InMemoryStorage
        return InMemoryStorage()
```

### Error Handling
```python
# mindtube/api/exceptions.py
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

class RateLimitExceeded(HTTPException):
    """Rate limit exceeded exception"""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(retry_after)}
        )

async def rate_limit_exception_handler(request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "rate_limit_exceeded",
            "message": exc.detail,
            "retry_after": exc.headers.get("Retry-After"),
            "timestamp": time.time()
        },
        headers=exc.headers
    )
```

## Testing

### Unit Tests
```python
# tests/test_rate_limiting.py
import pytest
import time
import asyncio
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from mindtube.api.middleware.rate_limit import RateLimitMiddleware, InMemoryStorage

@pytest.fixture
def app_with_rate_limit():
    app = FastAPI()
    app.add_middleware(
        RateLimitMiddleware,
        calls=3,
        period=60,
        per_user=False
    )
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}
    
    return app

def test_rate_limit_allows_requests_within_limit(app_with_rate_limit):
    """Test that requests within limit are allowed"""
    client = TestClient(app_with_rate_limit)
    
    # First 3 requests should succeed
    for i in range(3):
        response = client.get("/test")
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers

def test_rate_limit_blocks_excess_requests(app_with_rate_limit):
    """Test that requests exceeding limit are blocked"""
    client = TestClient(app_with_rate_limit)
    
    # First 3 requests succeed
    for i in range(3):
        response = client.get("/test")
        assert response.status_code == 200
    
    # 4th request should be rate limited
    response = client.get("/test")
    assert response.status_code == 429
    assert "Retry-After" in response.headers

def test_rate_limit_headers():
    """Test that rate limit headers are present"""
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, calls=10, period=60)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}
    
    client = TestClient(app)
    response = client.get("/test")
    
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers
    assert response.headers["X-RateLimit-Limit"] == "10"

@pytest.mark.asyncio
async def test_in_memory_storage():
    """Test in-memory storage functionality"""
    storage = InMemoryStorage()
    key = "test:endpoint"
    now = time.time()
    
    # Test empty storage
    timestamps = await storage.get_timestamps(key, now - 60)
    assert timestamps == []
    
    # Add timestamps
    await storage.set_timestamps(key, [now], 60)
    timestamps = await storage.get_timestamps(key, now - 60)
    assert len(timestamps) == 1
    assert timestamps[0] == now
```

### Integration Tests
```python
# tests/integration/test_api_rate_limiting.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from mindtube.api.app import create_app

@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)

def test_analyze_endpoint_rate_limiting(client):
    """Test rate limiting on analyze endpoint"""
    # This would require actual endpoint implementation
    # and proper test data
    pass

def test_different_endpoints_separate_limits(client):
    """Test that different endpoints have separate rate limits"""
    # Test that hitting limit on one endpoint doesn't affect others
    pass

def test_user_based_rate_limiting(client):
    """Test that rate limiting is per-user when authenticated"""
    # Test with different user tokens
    pass
```

## Monitoring and Metrics

### Rate Limit Metrics
```python
# mindtube/api/monitoring/rate_limit_metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Metrics
rate_limit_requests = Counter(
    'rate_limit_requests_total',
    'Total rate limit checks',
    ['endpoint', 'client_type', 'result']
)

rate_limit_exceeded = Counter(
    'rate_limit_exceeded_total',
    'Total rate limit violations',
    ['endpoint', 'client_type']
)

rate_limit_remaining = Gauge(
    'rate_limit_remaining',
    'Remaining requests in current window',
    ['endpoint', 'client_id']
)

def record_rate_limit_check(endpoint: str, client_type: str, allowed: bool):
    """Record rate limit check metrics"""
    result = "allowed" if allowed else "denied"
    rate_limit_requests.labels(
        endpoint=endpoint,
        client_type=client_type,
        result=result
    ).inc()
    
    if not allowed:
        rate_limit_exceeded.labels(
            endpoint=endpoint,
            client_type=client_type
        ).inc()
```

## Configuration

### Environment Variables
```bash
# Rate limiting configuration
ENABLE_RATE_LIMITING=true
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT_STORAGE=redis  # or "memory"

# Default rate limits
DEFAULT_RATE_LIMIT_CALLS=60
DEFAULT_RATE_LIMIT_PERIOD=60

# Per-endpoint overrides
ANALYZE_RATE_LIMIT_CALLS=10
ANALYZE_RATE_LIMIT_PERIOD=60
```

## Verification Steps
1. [ ] Middleware correctly identifies clients
2. [ ] Rate limits are enforced per endpoint
3. [ ] Proper HTTP headers are returned
4. [ ] Rate limit exceeded returns 429 status
5. [ ] Storage backend works correctly
6. [ ] Metrics are recorded properly
7. [ ] Configuration is flexible
8. [ ] Tests pass and cover edge cases

## Dependencies
- FastAPI middleware system
- Redis (optional, for production)
- Prometheus client (for metrics)
- TASK-026 (WebSocket support) for complete API

## Notes
- Use in-memory storage for development
- Use Redis for production deployments
- Consider implementing distributed rate limiting for multiple API instances
- Monitor rate limit metrics to adjust limits as needed
- Implement graceful degradation when storage is unavailable