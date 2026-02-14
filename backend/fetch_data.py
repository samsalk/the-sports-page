#!/usr/bin/env python3
"""
The Sports Page - Data Fetcher
Runs daily at 3:00 AM ET to fetch sports data and generate JSON
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
import pytz

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import league-specific modules
from apis import nhl, nba, mlb, epl
from utils import setup_logging

# Configuration
OUTPUT_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_FILE = OUTPUT_DIR / 'sports_data.json'
TIMEZONE = pytz.timezone('America/New_York')

def main():
    """Main execution function"""
    logger = setup_logging()
    logger.info(f"Starting data fetch...")

    # Calculate yesterday's date (ET)
    now_et = datetime.now(TIMEZONE)
    yesterday = (now_et - timedelta(days=1)).date()

    # Initialize data structure
    data = {
        'generated_at': now_et.isoformat(),
        'date_label': now_et.strftime('%A, %B %d, %Y'),
        'leagues': {}
    }

    # Fetch MLB data (first - primary sport)
    try:
        logger.info("Fetching MLB data...")
        data['leagues']['mlb'] = mlb.fetch_all_data(yesterday)
        logger.info("✓ MLB data fetched successfully")
    except Exception as e:
        logger.error(f"✗ MLB fetch failed: {e}")
        data['leagues']['mlb'] = create_error_structure(str(e))

    # Fetch NHL data
    try:
        logger.info("Fetching NHL data...")
        data['leagues']['nhl'] = nhl.fetch_all_data(yesterday)
        logger.info("✓ NHL data fetched successfully")
    except Exception as e:
        logger.error(f"✗ NHL fetch failed: {e}")
        data['leagues']['nhl'] = create_error_structure(str(e))

    # Fetch NBA data
    try:
        logger.info("Fetching NBA data...")
        data['leagues']['nba'] = nba.fetch_all_data(yesterday)
        logger.info("✓ NBA data fetched successfully")
    except Exception as e:
        logger.error(f"✗ NBA fetch failed: {e}")
        data['leagues']['nba'] = create_error_structure(str(e))

    # Fetch EPL data
    try:
        logger.info("Fetching EPL data...")
        data['leagues']['epl'] = epl.fetch_all_data(yesterday)
        logger.info("✓ EPL data fetched successfully")
    except Exception as e:
        logger.error(f"✗ EPL fetch failed: {e}")
        data['leagues']['epl'] = create_error_structure(str(e))

    # Write to JSON file
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Data written to {OUTPUT_FILE}")
        logger.info(f"Data fetch complete!")
        return 0
    except Exception as e:
        logger.error(f"✗ Failed to write output file: {e}")
        return 1

def create_error_structure(error_msg):
    """Create empty data structure with error message"""
    return {
        'error': error_msg,
        'yesterday': {'date': '', 'games': []},
        'standings': {},
        'leaders': {},
        'schedule': []
    }

if __name__ == '__main__':
    sys.exit(main())
