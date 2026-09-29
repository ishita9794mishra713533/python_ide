"""Centralized logging configuration for SmartIDE."""
import logging
import sys
from pathlib import Path
from utils.constants import LOG_FILE_PATH, APP_DATA_DIR


def setup_logger(log_level: int = logging.INFO) -> logging.Logger:
    """Configure and return the root application logger."""
    try:
        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create app data dir: {e}", file=sys.stderr)

    logger = logging.getLogger("SmartIDE")
    logger.setLevel(log_level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)

    try:
        file_handler = logging.FileHandler(str(LOG_FILE_PATH), encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning("Could not set up file logging: %s", e)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Obtain a child logger for a specific module."""
    return logging.getLogger(f"SmartIDE.{name}")
