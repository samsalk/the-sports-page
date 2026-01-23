"""EPL (Premier League) API Integration via football-data.org"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
import pytz

logger = logging.getLogger(__name__)

# Timezone constants
UTC_TZ = pytz.UTC
ET_TZ = pytz.timezone('America/New_York')

BASE_URL = 'https://api.football-data.org/v4'
COMPETITION_ID = 2021  # Premier League
API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY')

# Team abbreviation mapping
TEAM_ABBR = {
    'Arsenal FC': 'ARS',
    'Aston Villa FC': 'AVL',
    'AFC Bournemouth': 'BOU',
    'Brentford FC': 'BRE',
    'Brighton & Hove Albion FC': 'BHA',
    'Chelsea FC': 'CHE',
    'Crystal Palace FC': 'CRY',
    'Everton FC': 'EVE',
    'Fulham FC': 'FUL',
    'Liverpool FC': 'LIV',
    'Luton Town FC': 'LUT',
    'Manchester City FC': 'MCI',
    'Manchester United FC': 'MUN',
    'Newcastle United FC': 'NEW',
    'Nottingham Forest FC': 'NFO',
    'Sheffield United FC': 'SHU',
    'Tottenham Hotspur FC': 'TOT',
    'West Ham United FC': 'WHU',
    'Wolverhampton Wanderers FC': 'WOL',
    'Burnley FC': 'BUR',
    'Ipswich Town FC': 'IPS',
    'Leicester City FC': 'LEI',
    'Southampton FC': 'SOU'
}

def get_headers() -> Dict[str, str]:
    """Get headers with API key"""
    if not API_KEY:
        logger.warning("FOOTBALL_DATA_API_KEY not set, EPL data will be unavailable")
        return {}
    return {'X-Auth-Token': API_KEY}

def fetch_all_data(yesterday_date) -> Dict[str, Any]:
    """Fetch all EPL data"""
    if not API_KEY:
        raise ValueError("FOOTBALL_DATA_API_KEY environment variable not set")

    logger.info(f"Fetching EPL data for {yesterday_date}")
    return {
        'yesterday': fetch_yesterday_matches(yesterday_date),
        'standings': fetch_standings(),
        'leaders': fetch_top_scorers(),
        'schedule': fetch_week_schedule(yesterday_date)
    }

def fetch_yesterday_matches(date) -> Dict[str, Any]:
    """Fetch yesterday's match results"""
    date_str = date.strftime('%Y-%m-%d')
    url = f"{BASE_URL}/competitions/{COMPETITION_ID}/matches"
    params = {
        'dateFrom': date_str,
        'dateTo': date_str
    }

    try:
        response = requests.get(url, headers=get_headers(), params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"Failed to fetch yesterday's matches: {e}")
        return {'date': date_str, 'games': []}

    games = []
    for match in data.get('matches', []):
        if match['status'] not in ['FINISHED', 'IN_PLAY']:
            continue

        home_score = match['score']['fullTime']['home']
        away_score = match['score']['fullTime']['away']
        ht_home = match['score']['halfTime']['home']
        ht_away = match['score']['halfTime']['away']

        games.append({
            'match_id': match['id'],
            'home_team': {
                'abbr': TEAM_ABBR.get(match['homeTeam']['name'], 'UNK'),
                'name': match['homeTeam']['name'],
                'score': home_score if home_score is not None else 0
            },
            'away_team': {
                'abbr': TEAM_ABBR.get(match['awayTeam']['name'], 'UNK'),
                'name': match['awayTeam']['name'],
                'score': away_score if away_score is not None else 0
            },
            'status': match['status'],
            'half_time_score': f"{ht_home}-{ht_away}" if ht_home is not None else "0-0",
            'box_score': None  # Would need separate match details API
        })

    return {
        'date': date_str,
        'games': games
    }

def fetch_standings() -> Dict[str, List[Dict]]:
    """Fetch Premier League standings"""
    url = f"{BASE_URL}/competitions/{COMPETITION_ID}/standings"

    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"Failed to fetch standings: {e}")
        return {}

    teams = []
    for standing in data['standings'][0]['table']:
        teams.append({
            'rank': standing['position'],
            'team': TEAM_ABBR.get(standing['team']['name'], 'UNK'),
            'team_name': standing['team']['name'],
            'played': standing['playedGames'],
            'wins': standing['won'],
            'draws': standing['draw'],
            'losses': standing['lost'],
            'goals_for': standing['goalsFor'],
            'goals_against': standing['goalsAgainst'],
            'goal_diff': standing['goalDifference'],
            'points': standing['points'],
            'form': standing.get('form', '')
        })

    return {'Premier League': teams}

def fetch_top_scorers() -> Dict[str, List[Dict]]:
    """Fetch top scorers"""
    url = f"{BASE_URL}/competitions/{COMPETITION_ID}/scorers"

    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"Failed to fetch top scorers: {e}")
        return {'goals': [], 'assists': []}

    goals = []
    for idx, scorer in enumerate(data.get('scorers', [])[:10], 1):
        goals.append({
            'rank': idx,
            'player': scorer['player']['name'],
            'team': TEAM_ABBR.get(scorer['team']['name'], 'UNK'),
            'value': scorer.get('goals', 0)
        })

    return {
        'goals': goals,
        'assists': []  # Not available in free tier
    }

def fetch_week_schedule(start_date) -> List[Dict]:
    """Fetch upcoming week of matches"""
    start = (start_date + timedelta(days=1)).strftime('%Y-%m-%d')
    end = (start_date + timedelta(days=7)).strftime('%Y-%m-%d')

    url = f"{BASE_URL}/competitions/{COMPETITION_ID}/matches"
    params = {
        'dateFrom': start,
        'dateTo': end
    }

    try:
        response = requests.get(url, headers=get_headers(), params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"Failed to fetch schedule: {e}")
        return []

    # Group by date
    schedule_by_date = {}
    for match in data.get('matches', []):
        match_date = match['utcDate'][:10]
        if match_date not in schedule_by_date:
            schedule_by_date[match_date] = []

        match_time_utc = datetime.strptime(match['utcDate'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=UTC_TZ)
        match_time_et = match_time_utc.astimezone(ET_TZ)
        schedule_by_date[match_date].append({
            'time': match_time_et.strftime('%H:%M'),
            'time_label': match_time_et.strftime('%I:%M %p ET'),
            'home': TEAM_ABBR.get(match['homeTeam']['name'], 'UNK'),
            'away': TEAM_ABBR.get(match['awayTeam']['name'], 'UNK'),
            'broadcast': ''
        })

    # Convert to list format
    schedule = []
    for date_str, games in sorted(schedule_by_date.items()):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        schedule.append({
            'date': date_str,
            'day_label': date_obj.strftime('%a'),
            'games': games
        })

    return schedule
