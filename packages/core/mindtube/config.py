"""Configuration management for MindTube."""

import os
from pathlib import Path
from typing import Optional


class Config:
    """MindTube configuration settings."""

    def __init__(self, **kwargs):
        """Initialize configuration from environment variables and kwargs."""
        # Application settings
        self.app_name = kwargs.get('app_name') or os.getenv("APP_NAME", "MindTube")
        self.app_version = kwargs.get('app_version') or os.getenv("APP_VERSION", "0.1.0")
        self.environment = kwargs.get('environment') or os.getenv("ENVIRONMENT", "development")
        self.debug = kwargs.get('debug') or os.getenv("DEBUG", "false").lower() == "true"

        # Azure OpenAI settings
        self.azure_openai_endpoint = kwargs.get('azure_openai_endpoint') or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_api_key = kwargs.get('azure_openai_api_key') or os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_api_version = kwargs.get('azure_openai_api_version') or os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.azure_openai_chat_model = kwargs.get('azure_openai_chat_model') or os.getenv("AZURE_OPENAI_CHAT_MODEL", "gpt-4")

        # Database settings
        self.database_url = kwargs.get('database_url') or os.getenv("DATABASE_URL", "sqlite:///./data/mindtube.db")

        # Redis settings
        self.redis_url = kwargs.get('redis_url') or os.getenv("REDIS_URL", "redis://localhost:6379/0")

        # File storage settings
        self.data_dir = Path(kwargs.get('data_dir') or os.getenv("DATA_DIR", "./data"))
        self.cache_dir = Path(kwargs.get('cache_dir') or os.getenv("CACHE_DIR", "./data/cache"))
        self.export_dir = Path(kwargs.get('export_dir') or os.getenv("EXPORT_DIR", "./data/exports"))
        self.log_dir = Path(kwargs.get('log_dir') or os.getenv("LOG_DIR", "./data/logs"))

        self._create_directories()

    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        for directory in [self.data_dir, self.cache_dir, self.export_dir, self.log_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"