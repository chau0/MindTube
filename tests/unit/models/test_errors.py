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
    
    def test_error_response_json_serialization(self):
        """Test JSON serialization of error response."""
        response = ErrorResponse(
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Validation failed",
            details={"field": "email", "value": "invalid"}
        )
        
        json_data = response.model_dump()
        assert json_data["error_code"] == "VALIDATION_ERROR"
        assert json_data["message"] == "Validation failed"
        assert json_data["details"]["field"] == "email"


class TestErrorCode:
    """Test ErrorCode enum."""
    
    def test_error_code_values(self):
        """Test error code enum values."""
        assert ErrorCode.INVALID_URL == "INVALID_URL"
        assert ErrorCode.VIDEO_NOT_FOUND == "VIDEO_NOT_FOUND"
        assert ErrorCode.TRANSCRIPT_UNAVAILABLE == "TRANSCRIPT_UNAVAILABLE"
        assert ErrorCode.API_ERROR == "API_ERROR"
        assert ErrorCode.RATE_LIMITED == "RATE_LIMITED"
        assert ErrorCode.PROCESSING_ERROR == "PROCESSING_ERROR"
        assert ErrorCode.VALIDATION_ERROR == "VALIDATION_ERROR"
        assert ErrorCode.CONFIGURATION_ERROR == "CONFIGURATION_ERROR"
    
    def test_error_code_enum_membership(self):
        """Test error code enum membership."""
        all_codes = [
            ErrorCode.INVALID_URL,
            ErrorCode.VIDEO_NOT_FOUND,
            ErrorCode.TRANSCRIPT_UNAVAILABLE,
            ErrorCode.API_ERROR,
            ErrorCode.RATE_LIMITED,
            ErrorCode.PROCESSING_ERROR,
            ErrorCode.VALIDATION_ERROR,
            ErrorCode.CONFIGURATION_ERROR
        ]
        assert len(all_codes) == 8
        assert len(set(all_codes)) == 8  # All unique


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
        assert error.message == "Test error"
        assert error.error_code == ErrorCode.PROCESSING_ERROR
        assert error.details == {"key": "value"}
    
    def test_base_error_minimal(self):
        """Test creating base error with minimal params."""
        error = MindTubeError("Simple error", ErrorCode.API_ERROR)
        
        assert str(error) == "Simple error"
        assert error.error_code == ErrorCode.API_ERROR
        assert error.details == {}
    
    def test_to_response(self):
        """Test converting to response."""
        error = MindTubeError("Test error", ErrorCode.API_ERROR, {"service": "test"})
        response = error.to_response("req-456")
        
        assert response.error_code == ErrorCode.API_ERROR
        assert response.message == "Test error"
        assert response.details == {"service": "test"}
        assert response.request_id == "req-456"
    
    def test_to_response_without_request_id(self):
        """Test converting to response without request ID."""
        error = MindTubeError("Test error", ErrorCode.VALIDATION_ERROR)
        response = error.to_response()
        
        assert response.error_code == ErrorCode.VALIDATION_ERROR
        assert response.message == "Test error"
        assert response.request_id is None


class TestValidationError:
    """Test ValidationError."""
    
    def test_validation_error_with_field(self):
        """Test ValidationError with field."""
        error = ValidationError("Invalid email format", "email")
        
        assert error.error_code == ErrorCode.VALIDATION_ERROR
        assert error.message == "Invalid email format"
        assert error.details["field"] == "email"
        assert "Invalid email format" in str(error)
    
    def test_validation_error_without_field(self):
        """Test ValidationError without field."""
        error = ValidationError("General validation error")
        
        assert error.error_code == ErrorCode.VALIDATION_ERROR
        assert error.message == "General validation error"
        assert error.details == {}


class TestVideoNotFoundError:
    """Test VideoNotFoundError."""
    
    def test_video_not_found_error(self):
        """Test VideoNotFoundError."""
        error = VideoNotFoundError("abc123")
        
        assert error.error_code == ErrorCode.VIDEO_NOT_FOUND
        assert "Video not found: abc123" == error.message
        assert "abc123" in str(error)
        assert error.details["video_id"] == "abc123"
    
    def test_video_not_found_error_response(self):
        """Test VideoNotFoundError response conversion."""
        error = VideoNotFoundError("xyz789")
        response = error.to_response("req-001")
        
        assert response.error_code == ErrorCode.VIDEO_NOT_FOUND
        assert "xyz789" in response.message
        assert response.details["video_id"] == "xyz789"
        assert response.request_id == "req-001"


class TestTranscriptUnavailableError:
    """Test TranscriptUnavailableError."""
    
    def test_transcript_unavailable_error_with_reason(self):
        """Test TranscriptUnavailableError with reason."""
        error = TranscriptUnavailableError("abc123", "Private video")
        
        assert error.error_code == ErrorCode.TRANSCRIPT_UNAVAILABLE
        assert "abc123" in str(error)
        assert "Private video" in str(error)
        assert error.details["video_id"] == "abc123"
        assert error.details["reason"] == "Private video"
    
    def test_transcript_unavailable_error_without_reason(self):
        """Test TranscriptUnavailableError without reason."""
        error = TranscriptUnavailableError("xyz789")
        
        assert error.error_code == ErrorCode.TRANSCRIPT_UNAVAILABLE
        assert "xyz789" in str(error)
        assert error.details["video_id"] == "xyz789"
        assert error.details["reason"] is None


class TestAPIError:
    """Test APIError."""
    
    def test_api_error_with_status_code(self):
        """Test APIError with status code."""
        error = APIError("YouTube", "Service unavailable", 503)
        
        assert error.error_code == ErrorCode.API_ERROR
        assert "YouTube API error: Service unavailable" == error.message
        assert "YouTube" in str(error)
        assert "Service unavailable" in str(error)
        assert error.details["service"] == "YouTube"
        assert error.details["status_code"] == 503
    
    def test_api_error_without_status_code(self):
        """Test APIError without status code."""
        error = APIError("OpenAI", "Rate limit exceeded")
        
        assert error.error_code == ErrorCode.API_ERROR
        assert "OpenAI API error: Rate limit exceeded" == error.message
        assert error.details["service"] == "OpenAI"
        assert error.details["status_code"] is None


class TestRateLimitError:
    """Test RateLimitError."""
    
    def test_rate_limit_error_with_retry_after(self):
        """Test RateLimitError with retry_after."""
        error = RateLimitError("OpenAI", 60)
        
        assert error.error_code == ErrorCode.RATE_LIMITED
        assert "Rate limit exceeded for OpenAI - retry after 60 seconds" == error.message
        assert "OpenAI" in str(error)
        assert "60 seconds" in str(error)
        assert error.details["service"] == "OpenAI"
        assert error.details["retry_after"] == 60
    
    def test_rate_limit_error_without_retry_after(self):
        """Test RateLimitError without retry_after."""
        error = RateLimitError("YouTube")
        
        assert error.error_code == ErrorCode.RATE_LIMITED
        assert "Rate limit exceeded for YouTube" == error.message
        assert error.details["service"] == "YouTube"
        assert error.details["retry_after"] is None


class TestProcessingError:
    """Test ProcessingError."""
    
    def test_processing_error(self):
        """Test ProcessingError."""
        error = ProcessingError("analysis", "Failed to parse response")
        
        assert error.error_code == ErrorCode.PROCESSING_ERROR
        assert "Processing error in analysis: Failed to parse response" == error.message
        assert "analysis" in str(error)
        assert "Failed to parse response" in str(error)
        assert error.details["stage"] == "analysis"
    
    def test_processing_error_different_stage(self):
        """Test ProcessingError with different stage."""
        error = ProcessingError("transcript", "Invalid format")
        
        assert error.error_code == ErrorCode.PROCESSING_ERROR
        assert error.details["stage"] == "transcript"
        assert "transcript" in str(error)


class TestConfigurationError:
    """Test ConfigurationError."""
    
    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("api_key", "Missing required setting")
        
        assert error.error_code == ErrorCode.CONFIGURATION_ERROR
        assert "Configuration error for api_key: Missing required setting" == error.message
        assert "api_key" in str(error)
        assert "Missing required setting" in str(error)
        assert error.details["setting"] == "api_key"
    
    def test_configuration_error_different_setting(self):
        """Test ConfigurationError with different setting."""
        error = ConfigurationError("cache_path", "Path does not exist")
        
        assert error.error_code == ErrorCode.CONFIGURATION_ERROR
        assert error.details["setting"] == "cache_path"
        assert "cache_path" in str(error)


class TestErrorInheritance:
    """Test error inheritance and polymorphism."""
    
    def test_all_errors_are_mindtube_errors(self):
        """Test that all specific errors inherit from MindTubeError."""
        errors = [
            ValidationError("test"),
            VideoNotFoundError("test"),
            TranscriptUnavailableError("test"),
            APIError("test", "test"),
            RateLimitError("test"),
            ProcessingError("test", "test"),
            ConfigurationError("test", "test")
        ]
        
        for error in errors:
            assert isinstance(error, MindTubeError)
            assert isinstance(error, Exception)
    
    def test_error_response_conversion(self):
        """Test that all errors can be converted to ErrorResponse."""
        errors = [
            ValidationError("test", "field"),
            VideoNotFoundError("test123"),
            TranscriptUnavailableError("test123", "reason"),
            APIError("service", "message", 500),
            RateLimitError("service", 30),
            ProcessingError("stage", "message"),
            ConfigurationError("setting", "message")
        ]
        
        for error in errors:
            response = error.to_response("test-request")
            assert isinstance(response, ErrorResponse)
            assert response.request_id == "test-request"
            assert isinstance(response.error_code, ErrorCode)