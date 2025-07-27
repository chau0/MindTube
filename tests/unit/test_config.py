"""Unit tests for configuration management."""

import pytest
from pathlib import Path
from mindtube.config import Config


class TestConfig:
    """Test configuration management."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.app_name == "MindTube"
        assert config.app_version == "0.1.0"
        assert config.environment == "development"
        assert config.is_development is True
        assert config.is_production is False

    def test_environment_override(self, monkeypatch):
        """Test environment variable override."""
        monkeypatch.setenv("APP_NAME", "TestTube")
        monkeypatch.setenv("ENVIRONMENT", "production")
        
        config = Config()
        
        assert config.app_name == "TestTube"
        assert config.environment == "production"
        assert config.is_development is False
        assert config.is_production is True

    def test_directory_creation(self, tmp_path):
        """Test that directories are created."""
        data_dir = tmp_path / "test_data"
        
        config = Config(data_dir=data_dir)
        
        assert config.data_dir.exists()
        assert config.cache_dir.exists()
        assert config.export_dir.exists()
        assert config.log_dir.exists()

    def test_azure_openai_config(self, monkeypatch):
        """Test Azure OpenAI configuration."""
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
        
        config = Config()
        
        assert config.azure_openai_endpoint == "https://test.openai.azure.com/"
        assert config.azure_openai_api_key == "test-key"
        assert config.azure_openai_api_version == "2024-02-15-preview"