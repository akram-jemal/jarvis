"""
Simple logging utility for Lamp of Knowledge.
"""
import logging
import sys
from pathlib import Path
from config.settings import LOG_LEVEL, LOG_FILE

# Ensure log directory exists
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Configure logger
logger = logging.getLogger("lamp_of_knowledge")
logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

# Remove existing handlers
logger.handlers.clear()

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# File handler
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

def get_logger():
    """Get the configured logger instance."""
    return logger

