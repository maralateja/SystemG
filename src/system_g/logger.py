# Centralized logging module for System-G

import logging


def setup_logger(log_file, level=logging.INFO):
    """
    Create and configure the main application logger.
    
    Args:
        log_file: Path to the log file
        level: Logging level (default: logging.INFO)
    
    Returns:
        Configured logger object
    """
    # Create logger
    logger = logging.getLogger("system_g")
    logger.setLevel(level)
    
    # Prevent duplicate handlers if setup_logger is called multiple times
    if logger.handlers:
        return logger
    
    # Define log format
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(module)s - %(message)s"
    )
    
    # File Handler - writes to log file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Stream Handler - prints to console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger
