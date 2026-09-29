"""
Logging Configuration and Utilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Centralized logging system for HAMELIN with:
- Rotating file handlers (10MB max per file)
- Console and file output with different formats
- Automatic timestamp and module tracking
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

Usage:
    from hamelin.utils.logger import log
    
    log.info("Application started")
    log.warning("Configuration file not found, using defaults")
    log.error("Failed to load dataset", exc_info=True)
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from hamelin.utils.paths import workspace_dir
from typing import Optional
from datetime import datetime


LOG_RETENTION_DAYS = 30


def _prune_old_logs(log_dir: Path, days: int = LOG_RETENTION_DAYS) -> None:
    """Delete daily technical logs (hamelin_YYYY-MM-DD.log and their
    rotated .1-.5 copies) older than *days*; one file per day would
    otherwise pile up forever. usage_log.csv is study data and is never
    touched."""
    import time

    cutoff = time.time() - days * 86400
    for f in log_dir.glob("hamelin_*.log*"):
        try:
            if f.is_file() and f.stat().st_mtime < cutoff:
                f.unlink()
        except OSError:
            pass


class HamelinLogger:
    """
    Centralized logger for HAMELIN application.
    
    Features:
    - Rotating file handler (max 10MB, keeps 5 backup files)
    - Console handler for development
    - Colored output (if available)
    - Automatic module name detection
    - Context information in logs
    """
    
    _instance: Optional['HamelinLogger'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern to ensure one logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the logger if not already initialized."""
        if not HamelinLogger._initialized:
            self._setup_logger()
            HamelinLogger._initialized = True
    
    def _setup_logger(self):
        """Configure the logging system."""
        # Create logs directory if it doesn't exist
        log_dir = workspace_dir() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("HAMELIN")
        self.logger.setLevel(logging.DEBUG)
        # Don't propagate to the root logger - third-party libraries (e.g.
        # ludwig, which calls logging.basicConfig() on import) can attach
        # their own handler there, causing every message to print twice.
        self.logger.propagate = False

        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        _prune_old_logs(log_dir)

        # File handler with rotation (max 10MB, keep 5 backups)
        log_file = log_dir / f"hamelin_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatters
        file_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Initial log message
        self.logger.info("=" * 80)
        self.logger.info(f"HAMELIN Logger initialized - Session: {datetime.now()}")
        self.logger.info("=" * 80)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """
        Log error message.
        
        Args:
            message: Error message
            exc_info: Include exception traceback
            **kwargs: Additional logging parameters
        """
        self.logger.error(message, exc_info=exc_info, **kwargs)
    
    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """
        Log critical message.
        
        Args:
            message: Critical message
            exc_info: Include exception traceback
            **kwargs: Additional logging parameters
        """
        self.logger.critical(message, exc_info=exc_info, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """
        Log exception with full traceback.
        
        Should be called from an exception handler.
        """
        self.logger.exception(message, **kwargs)
    
    def set_level(self, level: str):
        """
        Change logging level.
        
        Args:
            level: One of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        if level.upper() in level_map:
            self.logger.setLevel(level_map[level.upper()])
            self.info(f"Log level changed to {level.upper()}")
        else:
            self.warning(f"Invalid log level: {level}. Using current level.")


# Singleton instance for easy import
log = HamelinLogger()


# Convenience functions for backward compatibility
def debug(message: str, **kwargs):
    """Log debug message."""
    log.debug(message, **kwargs)


def info(message: str, **kwargs):
    """Log info message."""
    log.info(message, **kwargs)


def warning(message: str, **kwargs):
    """Log warning message."""
    log.warning(message, **kwargs)


def error(message: str, exc_info: bool = False, **kwargs):
    """Log error message."""
    log.error(message, exc_info=exc_info, **kwargs)


def critical(message: str, exc_info: bool = False, **kwargs):
    """Log critical message."""
    log.critical(message, exc_info=exc_info, **kwargs)


def exception(message: str, **kwargs):
    """Log exception with traceback."""
    log.exception(message, **kwargs)


if __name__ == "__main__":
    # Test the logger
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    log.critical("This is a critical message")
    
    # Test exception logging
    try:
        raise ValueError("Test exception")
    except ValueError:
        log.exception("Caught an exception:")
    
    print("\n✓ Logger test complete. Check logs/ directory for output.")
