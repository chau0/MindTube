"""Tests for configuration management."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from mindtube.core.config import MindTubeConfig, get_config


class TestMindTubeConfig:
    """Test MindTubeConfig class."""
    
    def setup_method(self):
        """Set up test environment."""
        # Clear environment variables
        env_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY", 
            "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_DEPLOYMENT_NAME",
            "MINDTUBE_CACHE_ENABLED",
            "MINDTUBE_CACHE_DIR",
            "MINDTUBE_CACHE_TTL_HOURS",
            "MINDTUBE_OUTPUT_DIR",
            "MINDTUBE_OUTPUT_FORMAT",
            "MINDTUBE_MAX_TRANSCRIPT_LENGTH",
            "MINDTUBE_REQUEST_TIMEOUT",
            "MINDTUBE_MAX_RETRIES",
            "MINDTUBE_LOG_LEVEL",
            "MINDTUBE_LOG_FILE",
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
    
    def test_config_with_required_fields(self):
        """Test configuration with only required fields."""
        config = MindTubeConfig(
            azure_openai_endpoint="https://test.openai.azure.com/",
            azure_openai_api_key="test-key"
        )
        
        # Check required fields
        assert config.azure_openai_endpoint == "https://test.openai.azure.com/"
        assert config.azure_openai_api_key == "test-key"
        
        # Check defaults
        assert config.azure_openai_api_version == "2024-02-15-preview"
        assert config.azure_openai_deployment_name == "gpt-35-turbo"
        assert config.cache_enabled is True
        assert config.cache_ttl_hours == 24
        assert config.output_format == "json"
        assert config.log_level == "INFO"
        assert config.max_transcript_length == 50000
        assert config.request_timeout == 30
        assert config.max_retries == 3
    
    def test_config_path_validation(self):
        """Test path validation and conversion."""
        config = MindTubeConfig(
            azure_openai_endpoint="https://test.openai.azure.com/",
            azure_openai_api_key="test-key",
            cache_dir="/tmp/test",
            output_dir="./output",
            log_file="~/logs/test.log"
        )
        
        assert isinstance(config.cache_dir, Path)
        assert str(config.cache_dir) == "/tmp/test"
        
        assert isinstance(config.output_dir, Path)
        assert str(config.output_dir) == "output"
        
        assert isinstance(config.log_file, Path)
        assert str(config.log_file) == str(Path("~/logs/test.log").expanduser())
    
    def test_log_level_validation(self):
        """Test log level validation."""
        # Valid log level
        config = MindTubeConfig(
            azure_openai_endpoint="https://test.openai.azure.com/",
            azure_openai_api_key="test-key",
            log_level="debug"
        )
        assert config.log_level == "DEBUG"
        
        # Invalid log level
        with pytest.raises(ValueError, match="log_level must be one of"):
            MindTubeConfig(
                azure_openai_endpoint="https://test.openai.azure.com/",
                azure_openai_api_key="test-key",
                log_level="INVALID"
            )
    
    def test_output_format_validation(self):
        """Test output format validation."""
        # Valid format
        config = MindTubeConfig(
            azure_openai_endpoint="https://test.openai.azure.com/",
            azure_openai_api_key="test-key",
            output_format="MARKDOWN"
        )
        assert config.output_format == "markdown"
        
        # Invalid format
        with pytest.raises(ValueError, match="output_format must be one of"):
            MindTubeConfig(
                azure_openai_endpoint="https://test.openai.azure.com/",
                azure_openai_api_key="test-key",
                output_format="pdf"
            )
    
    def test_positive_integer_validation(self):
        """Test positive integer validation."""
        # Valid values
        config = MindTubeConfig(
            azure_openai_endpoint="https://test.openai.azure.com/",
            azure_openai_api_key="test-key",
            cache_ttl_hours=1,
            max_transcript_length=1000,
            request_timeout=60,
            max_retries=5
        )
        assert config.cache_ttl_hours == 1
        assert config.max_transcript_length == 1000
        assert config.request_timeout == 60
        assert config.max_retries == 5
        
        # Invalid values (zero or negative)
        with pytest.raises(ValueError, match="Value must be positive"):
            MindTubeConfig(
                azure_openai_endpoint="https://test.openai.azure.com/",
                azure_openai_api_key="test-key",
                cache_ttl_hours=0
            )
        
        with pytest.raises(ValueError, match="Value must be positive"):
            MindTubeConfig(
                azure_openai_endpoint="https://test.openai.azure.com/",
                azure_openai_api_key="test-key",
                max_retries=-1
            )
    
    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        with pytest.raises(ValueError):
            MindTubeConfig()
        
        with pytest.raises(ValueError):
            MindTubeConfig(azure_openai_endpoint="https://test.openai.azure.com/")


class TestGetConfig:
    """Test get_config function."""
    
    def setup_method(self):
        """Set up test environment."""
        # Clear environment variables
        env_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY", 
            "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_DEPLOYMENT_NAME",
            "MINDTUBE_CACHE_ENABLED",
            "MINDTUBE_CACHE_DIR",
            "MINDTUBE_CACHE_TTL_HOURS",
            "MINDTUBE_OUTPUT_DIR",
            "MINDTUBE_OUTPUT_FORMAT",
            "MINDTUBE_MAX_TRANSCRIPT_LENGTH",
            "MINDTUBE_REQUEST_TIMEOUT",
            "MINDTUBE_MAX_RETRIES",
            "MINDTUBE_LOG_LEVEL",
            "MINDTUBE_LOG_FILE",
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
    
    @patch.dict(os.environ, {
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "test-key"
    })
    def test_get_config_with_minimal_env(self):
        """Test get_config with minimal environment variables."""
        config = get_config()
        
        assert config.azure_openai_endpoint == "https://test.openai.azure.com/"
        assert config.azure_openai_api_key == "test-key"
        assert config.azure_openai_api_version == "2024-02-15-preview"
        assert config.azure_openai_deployment_name == "gpt-35-turbo"
    
    @patch.dict(os.environ, {
        "AZURE_OPENAI_ENDPOINT": "https://custom.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "custom-key",
        "AZURE_OPENAI_API_VERSION": "2023-12-01-preview",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4",
        "MINDTUBE_CACHE_ENABLED": "false",
        "MINDTUBE_CACHE_DIR": "/tmp/custom-cache",
        "MINDTUBE_CACHE_TTL_HOURS": "48",
        "MINDTUBE_OUTPUT_DIR": "/tmp/output",
        "MINDTUBE_OUTPUT_FORMAT": "markdown",
        "MINDTUBE_MAX_TRANSCRIPT_LENGTH": "75000",
        "MINDTUBE_REQUEST_TIMEOUT": "60",
        "MINDTUBE_MAX_RETRIES": "5",
        "MINDTUBE_LOG_LEVEL": "DEBUG",
        "MINDTUBE_LOG_FILE": "/tmp/test.log"
    })
    def test_get_config_with_full_env(self):
        """Test get_config with all environment variables set."""
        config = get_config()
        
        # Azure OpenAI config
        assert config.azure_openai_endpoint == "https://custom.openai.azure.com/"
        assert config.azure_openai_api_key == "custom-key"
        assert config.azure_openai_api_version == "2023-12-01-preview"
        assert config.azure_openai_deployment_name == "gpt-4"
        
        # Cache config
        assert config.cache_enabled is False
        assert str(config.cache_dir) == "/tmp/custom-cache"
        assert config.cache_ttl_hours == 48
        
        # Storage config
        assert str(config.output_dir) == "/tmp/output"
        assert config.output_format == "markdown"
        
        # Processing config
        assert config.max_transcript_length == 75000
        assert config.request_timeout == 60
        assert config.max_retries == 5
        
        # Logging config
        assert config.log_level == "DEBUG"
        assert str(config.log_file) == "/tmp/test.log"
    
    @patch.dict(os.environ, {
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "test-key",
        "MINDTUBE_CACHE_ENABLED": "1"  # Test alternative true value
    })
    def test_cache_enabled_boolean_conversion(self):
        """Test boolean conversion for cache_enabled."""
        config = get_config()
        assert config.cache_enabled is True
        
        # Test with "yes"
        with patch.dict(os.environ, {"MINDTUBE_CACHE_ENABLED": "yes"}):
            config = get_config()
            assert config.cache_enabled is True
        
        # Test with "false"
        with patch.dict(os.environ, {"MINDTUBE_CACHE_ENABLED": "false"}):
            config = get_config()
            assert config.cache_enabled is False
        
        # Test with "0"
        with patch.dict(os.environ, {"MINDTUBE_CACHE_ENABLED": "0"}):
            config = get_config()
            assert config.cache_enabled is False
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('dotenv.load_dotenv')
    def test_get_config_missing_required_env(self, mock_load_dotenv):
        """Test get_config with missing required environment variables."""
        with pytest.raises(ValueError, match="AZURE_OPENAI_ENDPOINT environment variable is required"):
            get_config()
    
    @patch.dict(os.environ, {
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "test-key",
        "MINDTUBE_LOG_LEVEL": "INVALID"
    })
    def test_get_config_invalid_values(self):
        """Test get_config with invalid environment values."""
        with pytest.raises(ValueError, match="log_level must be one of"):
            get_config()


class TestConfigIntegration:
    """Integration tests for configuration."""
    
    @patch.dict(os.environ, {
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "test-key"
    })
    def test_config_directories_creation(self):
        """Test that config can be created with directories that don't exist."""
        config = get_config()
        
        # The config should be created successfully even if directories don't exist
        assert isinstance(config.cache_dir, Path)
        assert isinstance(config.output_dir, Path)
        
        # Path expansion should work
        home_path = Path("~/test").expanduser()
        config_with_home = MindTubeConfig(
            azure_openai_endpoint="https://test.openai.azure.com/",
            azure_openai_api_key="test-key",
            cache_dir="~/test"
        )
        assert config_with_home.cache_dir == home_path