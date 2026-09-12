"""
Logging utility for PhonePe Expense Tracker
"""
import logging
from pathlib import Path
from backend.config.setting import LOG_FILE_PATH

def setup_logger() -> logging.Logger:
    """Setup and return centralized application logger"""
    LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("PhonePeTracker")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Write logs to file with UTF-8 encoding
        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Stream handler for console output
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
