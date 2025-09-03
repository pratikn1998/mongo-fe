"""Logging Module."""

import logging
import sys

logger = logging.getLogger("my_app")
logger.setLevel(logging.DEBUG)


if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    
    
def get_logger(name: str = None):
    """Get a logger with the same config but a different namespace."""
    return logger if not name else logger.getChild(name)
