import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logger():
    """Setup logger with both file and console handlers"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Format for our log messages
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler with rotation
    file_handler = RotatingFileHandler(
        'discord_bot.log',
        maxBytes=5000000,  # 5MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
