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
    'Southampton FC': 'SOU',
    'Sunderland AFC': 'SUN',
    'Leeds United FC': 'LEE'
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
        'yesterday': fetch_last_matchday(yesterday_date),
        'standings': fetch_standings(),
        'leaders': fetch_top_scorers(),
        'schedule': fetch_week_schedule(yesterday_date)
    }

def fetch_last_matchday(date) -> Dict[str, Any]:
    """Fetch the most recent completed matchday (EPL games are mainly on weekends)"""
    # Look back up to 14 days to find the last matchday with completed games
    for days_back in range(0, 15):
        check_date = date - timedelta(days=days_back)
        date_str = check_date.strftime('%Y-%m-%d')
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
            logger.error(f"Failed to fetch matches for {date_str}: {e}")
            continue

        # Check if there are finished games on this date
        finished_games = [m for m in data.get('matches', []) if m['status'] == 'FINISHED']
        if finished_games:
            logger.info(f"Found {len(finished_games)} completed EPL games on {date_str}")
            return parse_matchday_games(data, date_str)

    # No games found in the last 14 days
    logger.warning("No completed EPL games found in the last 14 days")
    return {'date': date.strftime('%Y-%m-%d'), 'games': [], 'matchday_label': 'No recent games'}


def parse_matchday_games(data, date_str) -> Dict[str, Any]:
    """Parse match data into game structures"""

    games = []
    for match in data.get('matches', []):
        if match['status'] not in ['FINISHED', 'IN_PLAY']:
            continue

        home_score = match['score']['fullTime']['home']
        away_score = match['score']['fullTime']['away']
        ht_home = match['score']['halfTime']['home']
        ht_away = match['score']['halfTime']['away']

        # Fetch detailed match info including goal scorers
        box_score = fetch_match_details(match['id'])

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
            'box_score': box_score
        })

    return {
        'date': date_str,
        'games': games
    }


def fetch_match_details(match_id: int) -> Dict[str, Any]:
    """Fetch detailed match info including goal scorers and assists"""
    url = f"{BASE_URL}/matches/{match_id}"

    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"Failed to fetch match details for {match_id}: {e}")
        return None

    home_team_id = data.get('homeTeam', {}).get('id')
    away_team_id = data.get('awayTeam', {}).get('id')
    home_abbr = TEAM_ABBR.get(data.get('homeTeam', {}).get('name', ''), 'UNK')
    away_abbr = TEAM_ABBR.get(data.get('awayTeam', {}).get('name', ''), 'UNK')

    # Parse goals into home/away lists
    home_goals = []
    away_goals = []

    for goal in data.get('goals', []):
        scorer_name = goal.get('scorer', {}).get('name', 'Unknown')
        minute = goal.get('minute', 0)
        injury_time = goal.get('injuryTime')
        goal_type = goal.get('type', 'REGULAR')
        assist = goal.get('assist', {})
        assist_name = assist.get('name') if assist else None

        # Format the minute display (e.g., "45+2'" for injury time)
        if injury_time:
            minute_display = f"{minute}+{injury_time}'"
        else:
            minute_display = f"{minute}'"

        # Add penalty/own goal indicator
        if goal_type == 'PENALTY':
            scorer_display = f"{scorer_name} (pen)"
        elif goal_type == 'OWN':
            scorer_display = f"{scorer_name} (og)"
        else:
            scorer_display = scorer_name

        goal_entry = {
            'scorer': scorer_display,
            'minute': minute_display,
            'assist': assist_name
        }

        # Determine which team scored
        team_id = goal.get('team', {}).get('id')
        if team_id == home_team_id:
            home_goals.append(goal_entry)
        elif team_id == away_team_id:
            away_goals.append(goal_entry)

    return {
        'home_goals': home_goals,
        'away_goals': away_goals,
        'home_abbr': home_abbr,
        'away_abbr': away_abbr
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
