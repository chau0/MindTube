# TASK-009: Error Models

## Task Information
- **ID**: TASK-009
- **Phase**: 1 - Data Models
- **Estimate**: 30 minutes
- **Dependencies**: TASK-008
- **Status**: ✅ Completed

## Description
Implement custom exception classes and error models for the MindTube application. This provides structured error handling and consistent error responses across the system.

## Acceptance Criteria
- [x] Create custom exception hierarchy
- [x] Implement error response models
- [x] Add error codes and messages
- [x] Create error handling utilities
- [x] Add unit tests for error scenarios
- [x] Document error handling patterns

## Implementation

### Step 1: Create mindtube/models/errors.py

```python
"""Error models and custom exceptions."""

from typing import Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum

class ErrorCode(str, Enum):
    """Standard error codes."""
    INVALID_URL = "INVALID_URL"
    VIDEO_NOT_FOUND = "VIDEO_NOT_FOUND"
    TRANSCRIPT_UNAVAILABLE = "TRANSCRIPT_UNAVAILABLE"
    API_ERROR = "API_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    PROCESSING_ERROR = "PROCESSING_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"

class ErrorResponse(BaseModel):
    """Standard error response model."""
    error_code: ErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None

class MindTubeError(Exception):
    """Base exception for MindTube application."""
    
    def __init__(
        self, 
        message: str, 
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_response(self, request_id: Optional[str] = None) -> ErrorResponse:
        """Convert to error response model."""
        return ErrorResponse(
            error_code=self.error_code,
            message=self.message,
            details=self.details,
            request_id=request_id
        )

class ValidationError(MindTubeError):
    """Validation error."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else None
        super().__init__(message, ErrorCode.VALIDATION_ERROR, details)

class VideoNotFoundError(MindTubeError):
    """Video not found error."""
    
    def __init__(self, video_id: str):
        super().__init__(
            f"Video not found: {video_id}",
            ErrorCode.VIDEO_NOT_FOUND,
            {"video_id": video_id}
        )

class TranscriptUnavailableError(MindTubeError):
    """Transcript unavailable error."""
    
    def __init__(self, video_id: str, reason: Optional[str] = None):
        message = f"Transcript unavailable for video: {video_id}"
        if reason:
            message += f" - {reason}"
        super().__init__(
            message,
            ErrorCode.TRANSCRIPT_UNAVAILABLE,
            {"video_id": video_id, "reason": reason}
        )

class APIError(MindTubeError):
    """External API error."""
    
    def __init__(self, service: str, message: str, status_code: Optional[int] = None):
        super().__init__(
            f"{service} API error: {message}",
            ErrorCode.API_ERROR,
            {"service": service, "status_code": status_code}
        )

class RateLimitError(MindTubeError):
    """Rate limit exceeded error."""
    
    def __init__(self, service: str, retry_after: Optional[int] = None):
        message = f"Rate limit exceeded for {service}"
        if retry_after:
            message += f" - retry after {retry_after} seconds"
        super().__init__(
            message,
            ErrorCode.RATE_LIMITED,
            {"service": service, "retry_after": retry_after}
        )

class ProcessingError(MindTubeError):
    """Processing pipeline error."""
    
    def __init__(self, stage: str, message: str):
        super().__init__(
            f"Processing error in {stage}: {message}",
            ErrorCode.PROCESSING_ERROR,
            {"stage": stage}
        )

class ConfigurationError(MindTubeError):
    """Configuration error."""
    
    def __init__(self, setting: str, message: str):
        super().__init__(
            f"Configuration error for {setting}: {message}",
            ErrorCode.CONFIGURATION_ERROR,
            {"setting": setting}
        )
```

### Step 2: Create tests/unit/models/test_errors.py

```python
"""Tests for error models."""

import pytest
from mindtube.models.errors import (
    ErrorCode, ErrorResponse, MindTubeError, ValidationError,
    VideoNotFoundError, TranscriptUnavailableError, APIError,
    RateLimitError, ProcessingError, ConfigurationError
)

class TestErrorResponse:
    """Test ErrorResponse model."""
    
    def test_error_response_creation(self):
        """Test creating error response."""
        response = ErrorResponse(
            error_code=ErrorCode.INVALID_URL,
            message="Invalid URL provided",
            details={"url": "invalid"},
            request_id="req-123"
        )
        
        assert response.error_code == ErrorCode.INVALID_URL
        assert response.message == "Invalid URL provided"
        assert response.details == {"url": "invalid"}
        assert response.request_id == "req-123"
    
    def test_error_response_minimal(self):
        """Test creating minimal error response."""
        response = ErrorResponse(
            error_code=ErrorCode.API_ERROR,
            message="API error occurred"
        )
        
        assert response.error_code == ErrorCode.API_ERROR
        assert response.message == "API error occurred"
        assert response.details is None
        assert response.request_id is None

class TestMindTubeError:
    """Test base MindTubeError."""
    
    def test_base_error_creation(self):
        """Test creating base error."""
        error = MindTubeError(
            "Test error",
            ErrorCode.PROCESSING_ERROR,
            {"key": "value"}
        )
        
        assert str(error) == "Test error"
        assert error.error_code == ErrorCode.PROCESSING_ERROR
        assert error.details == {"key": "value"}
    
    def test_to_response(self):
        """Test converting to response."""
        error = MindTubeError("Test error", ErrorCode.API_ERROR)
        response = error.to_response("req-456")
        
        assert response.error_code == ErrorCode.API_ERROR
        assert response.message == "Test error"
        assert response.request_id == "req-456"

class TestSpecificErrors:
    """Test specific error types."""
    
    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Invalid field", "email")
        
        assert error.error_code == ErrorCode.VALIDATION_ERROR
        assert error.details["field"] == "email"
    
    def test_video_not_found_error(self):
        """Test VideoNotFoundError."""
        error = VideoNotFoundError("abc123")
        
        assert error.error_code == ErrorCode.VIDEO_NOT_FOUND
        assert "abc123" in str(error)
        assert error.details["video_id"] == "abc123"
    
    def test_transcript_unavailable_error(self):
        """Test TranscriptUnavailableError."""
        error = TranscriptUnavailableError("abc123", "Private video")
        
        assert error.error_code == ErrorCode.TRANSCRIPT_UNAVAILABLE
        assert "abc123" in str(error)
        assert "Private video" in str(error)
        assert error.details["reason"] == "Private video"
    
    def test_api_error(self):
        """Test APIError."""
        error = APIError("YouTube", "Service unavailable", 503)
        
        assert error.error_code == ErrorCode.API_ERROR
        assert "YouTube" in str(error)
        assert error.details["service"] == "YouTube"
        assert error.details["status_code"] == 503
    
    def test_rate_limit_error(self):
        """Test RateLimitError."""
        error = RateLimitError("OpenAI", 60)
        
        assert error.error_code == ErrorCode.RATE_LIMITED
        assert "OpenAI" in str(error)
        assert "60 seconds" in str(error)
        assert error.details["retry_after"] == 60
    
    def test_processing_error(self):
        """Test ProcessingError."""
        error = ProcessingError("analysis", "Failed to parse response")
        
        assert error.error_code == ErrorCode.PROCESSING_ERROR
        assert "analysis" in str(error)
        assert error.details["stage"] == "analysis"
    
    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("api_key", "Missing required setting")
        
        assert error.error_code == ErrorCode.CONFIGURATION_ERROR
        assert "api_key" in str(error)
        assert error.details["setting"] == "api_key"
```

## Implementation Steps

1. **Create error models file**
   - Define error codes enum
   - Implement base exception class
   - Create specific exception types
   - Add error response model

2. **Add error handling utilities**
   - Create error conversion helpers
   - Add logging integration
   - Implement error formatting

3. **Create comprehensive tests**
   - Test all error types
   - Verify error response conversion
   - Test error details handling

4. **Update imports**
   - Add to models/__init__.py
   - Export public error classes

## Testing

```bash
# Run error model tests
pytest tests/unit/models/test_errors.py -v

# Test error handling integration
pytest tests/unit/models/ -k "error" -v
```

## Common Issues

### Issue: Error details not serializable
**Solution**: Ensure all error details are JSON-serializable types

### Issue: Error messages not user-friendly
**Solution**: Provide clear, actionable error messages with context