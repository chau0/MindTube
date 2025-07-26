"""
Logging configuration for MindTube backend
"""

import logging
import structlog
import sys
from pathlib import Path
from app.core.config import settings

def setup_logging():
    """Configure structured logging for the application"""
    
    # Ensure logs directory exists
    logs_dir = Path(settings.LOGS_DIR)
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # File handler for persistent logs
    file_handler = logging.FileHandler(logs_dir / "mindtube.log")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    
    # Add file handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

# Create logger instance
logger = structlog.get_logger(__name__)