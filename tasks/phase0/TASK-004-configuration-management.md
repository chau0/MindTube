# TASK-004: Configuration Management

## Task Information
- **ID**: TASK-004
- **Phase**: 0 - Project Foundation
- **Estimate**: 45 minutes
- **Dependencies**: TASK-003
- **Status**: 🟢 Done

## Description
Implement configuration management system using environment variables and configuration files. This provides a flexible way to manage settings across different environments (development, testing, production).

## Acceptance Criteria
- [x] Create Config dataclass with Pydantic validation
- [x] Support environment variables with .env file
- [x] Add Azure OpenAI configuration
- [x] Add YouTube API configuration
- [x] Add cache and storage configuration
- [x] Implement configuration validation
- [x] Add default values and documentation
- [x] Create unit tests for configuration loading
- [x] Add configuration examples

## Configuration Structure

### Step 1: Create mindtube/core/config.py

```python
from typing import Optional
from pydantic import BaseSettings, Field, validator
from pathlib import Path

class MindTubeConfig(BaseSettings):
    """MindTube application configuration."""
    
    # Azure OpenAI Configuration
    azure_openai_endpoint: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(..., env="AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = Field("2023-12-01-preview", env="AZURE_OPENAI_API_VERSION")
    azure_openai_deployment_name: str = Field("gpt-4", env="AZURE_OPENAI_DEPLOYMENT_NAME")
    
    # Cache Configuration
    cache_enabled: bool = Field(True, env="MINDTUBE_CACHE_ENABLED")
    cache_dir: Path = Field(Path.home() / ".mindtube" / "cache", env="MINDTUBE_CACHE_DIR")
    cache_ttl_hours: int = Field(24, env="MINDTUBE_CACHE_TTL_HOURS")
    
    # Storage Configuration
    output_dir: Path = Field(Path.cwd() / "output", env="MINDTUBE_OUTPUT_DIR")
    output_format: str = Field("json", env="MINDTUBE_OUTPUT_FORMAT")
    
    # Processing Configuration
    max_transcript_length: int = Field(50000, env="MINDTUBE_MAX_TRANSCRIPT_LENGTH")
    request_timeout: int = Field(30, env="MINDTUBE_REQUEST_TIMEOUT")
    max_retries: int = Field(3, env="MINDTUBE_MAX_RETRIES")
    
    # Logging Configuration
    log_level: str = Field("INFO", env="MINDTUBE_LOG_LEVEL")
    log_file: Optional[Path] = Field(None, env="MINDTUBE_LOG_FILE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator("cache_dir", "output_dir", pre=True)
    def ensure_path(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()
    
    @validator("output_format")
    def validate_output_format(cls, v):
        valid_formats = ["json", "markdown", "html"]
        if v.lower() not in valid_formats:
            raise ValueError(f"output_format must be one of {valid_formats}")
        return v.lower()

# Global configuration instance
config = MindTubeConfig()
```

### Step 2: Create .env.example

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2023-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Cache Configuration
MINDTUBE_CACHE_ENABLED=true
MINDTUBE_CACHE_DIR=~/.mindtube/cache
MINDTUBE_CACHE_TTL_HOURS=24

# Storage Configuration
MINDTUBE_OUTPUT_DIR=./output
MINDTUBE_OUTPUT_FORMAT=json

# Processing Configuration
MINDTUBE_MAX_TRANSCRIPT_LENGTH=50000
MINDTUBE_REQUEST_TIMEOUT=30
MINDTUBE_MAX_RETRIES=3

# Logging Configuration
MINDTUBE_LOG_LEVEL=INFO
# MINDTUBE_LOG_FILE=./logs/mindtube.log
```

### Step 3: Create tests/test_config.py

```python
import pytest
import os
from pathlib import Path
from mindtube.core.config import MindTubeConfig

def test_config_defaults():
    """Test configuration with default values."""
    # Set required environment variables
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com/"
    os.environ["AZURE_OPENAI_API_KEY"] = "test-key"
    
    config = MindTubeConfig()
    
    assert config.azure_openai_api_version == "2023-12-01-preview"
    assert config.azure_openai_deployment_name == "gpt-4"
    assert config.cache_enabled is True
    assert config.cache_ttl_hours == 24
    assert config.output_format == "json"
    assert config.log_level == "INFO"

def test_config_validation():
    """Test configuration validation."""
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com/"
    os.environ["AZURE_OPENAI_API_KEY"] = "test-key"
    os.environ["MINDTUBE_LOG_LEVEL"] = "INVALID"
    
    with pytest.raises(ValueError, match="log_level must be one of"):
        MindTubeConfig()

def test_config_path_conversion():
    """Test path string to Path conversion."""
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com/"
    os.environ["AZURE_OPENAI_API_KEY"] = "test-key"
    os.environ["MINDTUBE_CACHE_DIR"] = "/tmp/test"
    
    config = MindTubeConfig()
    
    assert isinstance(config.cache_dir, Path)
    assert str(config.cache_dir) == "/tmp/test"
```

## Implementation Steps

### Step 1: Install Additional Dependencies
Add to pyproject.toml dependencies:
```toml
"pydantic[dotenv]>=2.0.0,<3.0.0",
```

### Step 2: Create Configuration Module
Implement the configuration class with proper validation and environment variable support.

### Step 3: Create Environment File Template
Provide .env.example with all configuration options documented.

### Step 4: Add Configuration Tests
Test default values, validation, and environment variable loading.

### Step 5: Update .gitignore
Ensure .env files are ignored:
```
# Environment files
.env
.env.local
.env.*.local
```

## Testing

### Unit Tests
```bash
make test tests/test_config.py
```

### Manual Testing
```bash
# Test configuration loading
python -c "from mindtube.core.config import config; print(config.dict())"

# Test with custom environment
MINDTUBE_LOG_LEVEL=DEBUG python -c "from mindtube.core.config import config; print(config.log_level)"
```

## Common Issues

### Issue 1: Missing Required Environment Variables
**Problem**: Configuration fails to load due to missing Azure OpenAI credentials
**Solution**: Copy .env.example to .env and fill in required values

### Issue 2: Path Resolution Issues
**Problem**: Relative paths not resolving correctly
**Solution**: Use Path.resolve() for absolute paths when needed

### Issue 3: Validation Errors
**Problem**: Invalid configuration values
**Solution**: Check validator methods and provide clear error messages