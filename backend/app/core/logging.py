"""
Centralized structured logging configuration.
Provides consistent, readable, and configurable logs across all application modules.
"""

import logging
import sys


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configures the root application logger with standard formatting.
    Avoids duplicate handlers and supports configurable log level.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    logger = logging.getLogger("dsa_tutor")
    logger.setLevel(numeric_level)

    # Avoid adding duplicate handlers if setup_logging is called multiple times
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)

        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


# Global logger instance
logger = setup_logging()
