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
        details = {"field": field} if field else {}
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