"""Shared utility functions"""

import logging
from pathlib import Path

def setup_logging():
    """Set up logging configuration"""
    LOG_DIR = Path(__file__).parent.parent / 'logs'
    LOG_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_DIR / 'fetch_data.log'),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(__name__)
