"""Configuration management for ytnote."""

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Gemini API Configuration
    gemini_api_key: Optional[str] = Field(default=None, description="Gemini API key")
    gemini_model: str = Field(default="gemini-1.5-pro", description="Gemini model to use")

    # Proxy Configuration
    http_proxy: Optional[str] = Field(default=None, description="HTTP proxy URL")
    https_proxy: Optional[str] = Field(default=None, description="HTTPS proxy URL")
    yt_proxy: Optional[str] = Field(default=None, description="YouTube-specific proxy URL")

    # Output Configuration
    output_dir: Path = Field(default=Path("data"), description="Output directory for artifacts")
    cache_enabled: bool = Field(default=True, description="Enable caching of results")

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Logging format (json or text)")

    @field_validator("output_dir", mode="before")
    @classmethod
    def resolve_output_dir(cls, v: str | Path) -> Path:
        """Resolve output directory to absolute path."""
        if isinstance(v, str):
            v = Path(v)
        return v.resolve()

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            msg = f"Log level must be one of: {valid_levels}"
            raise ValueError(msg)
        return v.upper()

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Validate log format."""
        valid_formats = {"json", "text"}
        if v.lower() not in valid_formats:
            msg = f"Log format must be one of: {valid_formats}"
            raise ValueError(msg)
        return v.lower()

    def get_proxies(self) -> dict[str, str]:
        """Get proxy configuration for requests."""
        proxies = {}
        if self.http_proxy:
            proxies["http"] = self.http_proxy
        if self.https_proxy:
            proxies["https"] = self.https_proxy
        # YouTube-specific proxy overrides others
        if self.yt_proxy:
            proxies["http"] = self.yt_proxy
            proxies["https"] = self.yt_proxy
        return proxies

    def ensure_output_dir(self) -> None:
        """Ensure output directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
