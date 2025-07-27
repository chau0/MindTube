"""
Configuration settings for MindTube backend
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys (optional for development)
    YOUTUBE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_API_VERSION: str = "2024-02-01"
    
    # Backend Configuration
    BACKEND_HOST: str = "localhost"
    BACKEND_PORT: int = 8000
    DEBUG: bool = True
    LOG_LEVEL: str = "info"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "sqlite:///./mindtube.db"
    
    # Redis (optional)
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    
    # Processing Limits
    MAX_VIDEO_DURATION_MINUTES: int = 90
    MAX_CONCURRENT_JOBS: int = 3
    DEFAULT_CHUNK_SIZE_TOKENS: int = 1500
    
    # LLM Configuration (Azure deployment names)
    DEFAULT_MAP_MODEL: str = "gpt-4o-mini"  # Azure deployment name
    DEFAULT_REDUCE_MODEL: str = "gpt-4o-mini"  # Azure deployment name
    MAX_TOKENS_PER_REQUEST: int = 4000
    TEMPERATURE: float = 0.1
    
    # ASR Configuration
    ENABLE_ASR_FALLBACK: bool = True
    WHISPER_MODEL: str = "small"
    MAX_ASR_DURATION_MINUTES: int = 120
    
    # Storage
    ARTIFACTS_DIR: str = "./data/artifacts"
    CACHE_DIR: str = "./data/cache"
    LOGS_DIR: str = "./data/logs"
    
    # Cache settings
    CACHE_TTL_HOURS: int = 168  # 7 days
    MAX_CACHE_SIZE_MB: int = 1000
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Privacy
    STORE_TRANSCRIPTS: bool = False
    STORE_USER_DATA: bool = False
    ENABLE_ANALYTICS: bool = False
    
    # Development
    ENABLE_CORS: bool = True
    ENABLE_DOCS: bool = True
    ENABLE_METRICS_ENDPOINT: bool = True
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ENABLE_PERFORMANCE_MONITORING: bool = False
    
    # Cost & Rate Limiting
    MAX_COST_PER_VIDEO_USD: float = 0.50
    DAILY_BUDGET_USD: float = 10.00
    ENABLE_COST_TRACKING: bool = True
    REQUESTS_PER_MINUTE: int = 30
    REQUESTS_PER_HOUR: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()