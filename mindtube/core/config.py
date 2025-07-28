"""Configuration management for MindTube application."""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class MindTubeConfig(BaseModel):
    """MindTube application configuration."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Azure OpenAI Configuration
    azure_openai_endpoint: str = Field(..., description="Azure OpenAI endpoint URL")
    azure_openai_api_key: str = Field(..., description="Azure OpenAI API key")
    azure_openai_api_version: str = Field(
        "2024-02-15-preview", 
        description="Azure OpenAI API version"
    )
    azure_openai_deployment_name: str = Field(
        "gpt-35-turbo", 
        description="Azure OpenAI deployment name"
    )
    
    # Cache Configuration  
    cache_enabled: bool = Field(True, description="Enable caching")
    cache_dir: Path = Field(
        Path.home() / ".mindtube" / "cache",
        description="Cache directory path"
    )
    cache_ttl_hours: int = Field(24, description="Cache TTL in hours")
    
    # Storage Configuration
    output_dir: Path = Field(
        Path.cwd() / "output",
        description="Output directory path"
    )
    output_format: str = Field("json", description="Output format")
    
    # Processing Configuration
    max_transcript_length: int = Field(
        50000, 
        description="Maximum transcript length in characters"
    )
    request_timeout: int = Field(30, description="Request timeout in seconds")
    max_retries: int = Field(3, description="Maximum number of retries")
    
    # Logging Configuration
    log_level: str = Field("INFO", description="Logging level")
    log_file: Optional[Path] = Field(None, description="Log file path")
    
    @field_validator("cache_dir", "output_dir", "log_file", mode="before")
    @classmethod
    def ensure_path(cls, v):
        """Convert string paths to Path objects."""
        if v is None:
            return v
        if isinstance(v, str):
            return Path(v).expanduser()
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()
    
    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v):
        """Validate output format."""
        valid_formats = ["json", "markdown", "html"]
        if v.lower() not in valid_formats:
            raise ValueError(f"output_format must be one of {valid_formats}")
        return v.lower()
    
    @field_validator("cache_ttl_hours", "max_transcript_length", "request_timeout", "max_retries")
    @classmethod
    def validate_positive_int(cls, v):
        """Validate positive integers."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v


def get_config() -> MindTubeConfig:
    """Get configuration instance with environment variables loaded."""
    import os
    from dotenv import load_dotenv
    
    # Load .env file if it exists
    load_dotenv()
    
    # Check for required environment variables
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    if not endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
    if not api_key:
        raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
    
    # Create config with environment variables
    return MindTubeConfig(
        azure_openai_endpoint=endpoint,
        azure_openai_api_key=api_key,
        azure_openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_openai_deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-35-turbo"),
        cache_enabled=os.getenv("MINDTUBE_CACHE_ENABLED", "true").lower() in ("true", "1", "yes"),
        cache_dir=os.getenv("MINDTUBE_CACHE_DIR", str(Path.home() / ".mindtube" / "cache")),
        cache_ttl_hours=int(os.getenv("MINDTUBE_CACHE_TTL_HOURS", "24")),
        output_dir=os.getenv("MINDTUBE_OUTPUT_DIR", str(Path.cwd() / "output")),
        output_format=os.getenv("MINDTUBE_OUTPUT_FORMAT", "json"),
        max_transcript_length=int(os.getenv("MINDTUBE_MAX_TRANSCRIPT_LENGTH", "50000")),
        request_timeout=int(os.getenv("MINDTUBE_REQUEST_TIMEOUT", "30")),
        max_retries=int(os.getenv("MINDTUBE_MAX_RETRIES", "3")),
        log_level=os.getenv("MINDTUBE_LOG_LEVEL", "INFO"),
        log_file=os.getenv("MINDTUBE_LOG_FILE", None),
    )


# Global configuration instance
config = get_config()