"""
Logging utilities for the OpenModelica Agent
"""
import logging
import colorlog
from pathlib import Path

def setup_logger(name: str, log_file: Path = None, level=logging.INFO):
    """Set up a logger with color output and optional file logging"""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler with colors
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(level)
    
    console_format = colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)-8s%(reset)s %(blue)s[%(name)s]%(reset)s %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler if log_file is provided
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger