import logging
import os
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
log_directory = "/app/logs"
os.makedirs(log_directory, exist_ok=True)

def setup_logger():
    # Create a custom formatter with more detailed information
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Configure root logger to DEBUG level
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Console handler (Docker logs) with INFO level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler with DEBUG level and rotation
    file_handler = RotatingFileHandler(
        filename=f"{log_directory}/app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Create a specific logger for your application
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Ensure DEBUG level for your app logger

    return logger

# Initialize the logger
logger = setup_logger()

# Optional: Add a function to dynamically change log levels
def set_log_level(level):
    """
    Change the log level dynamically.
    :param level: Can be 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    logger.setLevel(numeric_level)
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setLevel(numeric_level)