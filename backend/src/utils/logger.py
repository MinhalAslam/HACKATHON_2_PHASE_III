import logging
from datetime import datetime
import sys
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: str = "app.log"):
    """
    Set up application-wide logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Name of the file to write logs to
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create full path for log file
    log_path = logs_dir / log_file

    # Define log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Create file handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Also configure the security logger
    from .logging import security_logger
    security_logger.logger.setLevel(getattr(logging, log_level.upper()))


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Name of the logger

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Application logger instance
app_logger = get_logger(__name__)

if __name__ == "__main__":
    # Example usage
    setup_logging()
    app_logger.info("Logging setup completed")
    app_logger.warning("This is a warning message")
    app_logger.error("This is an error message")