"""Configuration constants"""

# API endpoints
NHL_BASE_URL = 'https://statsapi.web.nhl.com/api/v1'
FOOTBALL_DATA_BASE_URL = 'https://api.football-data.org/v4'
EPL_COMPETITION_ID = 2021

# Timezone
EASTERN_TZ = 'America/New_York'

# File paths
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
FRONTEND_DIR = BASE_DIR / 'frontend'
DATA_DIR = FRONTEND_DIR / 'data'
OUTPUT_FILE = DATA_DIR / 'sports_data.json'

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)
