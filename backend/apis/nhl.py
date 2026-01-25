"""NHL Stats API Integration - Updated for new api-web.nhle.com API"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
import pytz

logger = logging.getLogger(__name__)

# Timezone constants
UTC_TZ = pytz.UTC
ET_TZ = pytz.timezone('America/New_York')

BASE_URL = 'https://api-web.nhle.com/v1'

# Team abbreviation mapping (team IDs remain the same)
TEAM_ABBR = {
    1: 'NJD', 2: 'NYI', 3: 'NYR', 4: 'PHI', 5: 'PIT', 6: 'BOS',
    7: 'BUF', 8: 'MTL', 9: 'OTT', 10: 'TOR', 12: 'CAR', 13: 'FLA',
    14: 'TBL', 15: 'WSH', 16: 'CHI', 17: 'DET', 18: 'NSH', 19: 'STL',
    20: 'CGY', 21: 'COL', 22: 'EDM', 23: 'VAN', 24: 'ANA', 25: 'DAL',
    26: 'LAK', 28: 'SJS', 29: 'CBJ', 30: 'MIN', 52: 'WPG', 53: 'ARI',
    54: 'VGK', 55: 'SEA', 56: 'UTA'
}

def fetch_all_data(yesterday_date) -> Dict[str, Any]:
    """Fetch all NHL data for the sports page"""
    logger.info(f"Fetching NHL data for {yesterday_date}")
    return {
        'yesterday': fetch_yesterday_scores(yesterday_date),
        'standings': fetch_standings(),
        'leaders': fetch_stat_leaders(),
        'schedule': fetch_week_schedule(yesterday_date)
    }

def fetch_yesterday_scores(date) -> Dict[str, Any]:
    """Fetch scores from yesterday with box scores using new scoreboard API"""
    date_str = date.strftime('%Y-%m-%d')
    url = f"{BASE_URL}/scoreboard/now"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        scoreboard_data = response.json()
    except Exception as e:
        logger.error(f"Failed to fetch yesterday's scores: {e}")
        return {'date': date_str, 'games': []}

    games = []
    # Find games for yesterday's date
    for game_date_obj in scoreboard_data.get('gamesByDate', []):
        if game_date_obj.get('date') != date_str:
            continue

        for game in game_date_obj.get('games', []):
            # Only include finished games
            game_state = game.get('gameState', '')
            if game_state not in ['OFF', 'FINAL']:
                continue

            game_id = game.get('id')
            away_team = game.get('awayTeam', {})
            home_team = game.get('homeTeam', {})

            # Fetch detailed box score for completed games
            box_score = fetch_box_score(game_id) if game_id else None

            # Determine status (Final, Final/OT, Final/SO)
            status = parse_game_status(game)

            games.append({
                'game_id': str(game_id),
                'away_team': {
                    'abbr': away_team.get('abbrev', 'UNK'),
                    'name': away_team.get('name', {}).get('default', 'Unknown'),
                    'score': away_team.get('score', 0)
                },
                'home_team': {
                    'abbr': home_team.get('abbrev', 'UNK'),
                    'name': home_team.get('name', {}).get('default', 'Unknown'),
                    'score': home_team.get('score', 0)
                },
                'status': status,
                'periods': game.get('period', 3),
                'box_score': box_score
            })

    return {
        'date': date_str,
        'games': games
    }

def fetch_box_score(game_id) -> Dict[str, Any]:
    """Fetch detailed box score for a game using new API"""
    url = f"{BASE_URL}/gamecenter/{game_id}/boxscore"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"Failed to fetch box score for game {game_id}: {e}")
        return None

    # Extract period-by-period scoring
    away_line = []
    home_line = []

    # Get period summary if available
    line_score_data = data.get('linescore', {})
    if line_score_data:
        for period_data in line_score_data.get('byPeriod', []):
            away_line.append(period_data.get('away', 0))
            home_line.append(period_data.get('home', 0))

    # Get shots on goal from team objects
    shots_away = data.get('awayTeam', {}).get('sog', 0)
    shots_home = data.get('homeTeam', {}).get('sog', 0)

    # Extract goalie stats
    goalies = []
    for team_key in ['awayTeam', 'homeTeam']:
        # Get team abbreviation from the top-level team data
        team_abbr = data.get(team_key, {}).get('abbrev', 'UNK')
        team_data = data.get('playerByGameStats', {}).get(team_key, {})
        for player in team_data.get('goalies', []):
            if player:
                name = player.get('name', {}).get('default', 'Unknown')
                saves = player.get('saves', 0)
                shots_against = player.get('shotsAgainst', 0)

                goalies.append({
                    'team': team_abbr,
                    'name': name,
                    'saves': saves,
                    'shots': shots_against,
                    'save_pct': round(saves / shots_against, 3) if shots_against > 0 else 0.000
                })

    # Extract top scorers (players with points in the game)
    scorers = []
    for team_key in ['awayTeam', 'homeTeam']:
        team_data = data.get('playerByGameStats', {}).get(team_key, {})
        # Get actual team abbreviation from the top-level team data
        team_abbr = data.get(team_key, {}).get('abbrev', 'UNK')

        for position_key in ['forwards', 'defense']:
            for player in team_data.get(position_key, []):
                goals = player.get('goals', 0)
                assists = player.get('assists', 0)
                points = goals + assists

                if points > 0:  # Only include players who scored
                    name = player.get('name', {}).get('default', 'Unknown')
                    scorers.append({
                        'team': team_abbr,
                        'name': name,
                        'goals': goals,
                        'assists': assists,
                        'points': points
                    })

    # Sort by points descending, then goals
    scorers.sort(key=lambda x: (x['points'], x['goals']), reverse=True)

    return {
        'line_score': {
            'away': away_line,
            'home': home_line
        },
        'shots': {
            'away': shots_away,
            'home': shots_home
        },
        'goalies': goalies,
        'scorers': scorers[:6]  # Top 6 scorers
    }

def fetch_standings() -> Dict[str, List[Dict]]:
    """Fetch current NHL standings by division using new API"""
    url = f"{BASE_URL}/standings/now"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"Failed to fetch standings: {e}")
        return {}

    standings = {}

    # Parse standings by division
    for standing_entry in data.get('standings', []):
        division_name = standing_entry.get('divisionName', 'Unknown Division')

        if division_name not in standings:
            standings[division_name] = []

        team_abbr = standing_entry.get('teamAbbrev', {}).get('default', 'UNK')
        team_name = standing_entry.get('teamName', {}).get('default', 'Unknown Team')

        # Build streak string (e.g., "W3", "L2")
        streak_code = standing_entry.get('streakCode', '')
        streak_count = standing_entry.get('streakCount', 0)
        streak_display = f"{streak_code}{streak_count}" if streak_code and streak_count else streak_code

        standings[division_name].append({
            'rank': standing_entry.get('divisionSequence', 0),
            'team': team_abbr,
            'team_name': team_name,
            'wins': standing_entry.get('wins', 0),
            'losses': standing_entry.get('losses', 0),
            'ot_losses': standing_entry.get('otLosses', 0),
            'points': standing_entry.get('points', 0),
            'games_played': standing_entry.get('gamesPlayed', 0),
            'win_pct': round(standing_entry.get('points', 0) / (standing_entry.get('gamesPlayed', 1) * 2), 3),
            'games_behind': 0,  # Will calculate below
            'streak': streak_display
        })

    # Calculate games behind for each division
    for division_name, teams in standings.items():
        if teams:
            # Sort by rank to ensure leader is first
            teams.sort(key=lambda x: x['rank'])
            leader_points = teams[0]['points']
            for team in teams:
                team['games_behind'] = round((leader_points - team['points']) / 2, 1)

    return standings

def fetch_stat_leaders() -> Dict[str, List[Dict]]:
    """Fetch statistical leaders using new API"""
    try:
        # Get player spotlight (featured players)
        url = f"{BASE_URL}/player-spotlight"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        spotlight_data = response.json()

        # Fetch detailed stats for top players
        leaders = {
            'goals': [],
            'assists': [],
            'points': [],
            'save_percentage': []
        }

        # Get top skaters from spotlight (filter out goalies)
        skater_count = 0
        for player in spotlight_data:
            # Skip goalies
            position = player.get('position', '')
            if position == 'G':
                continue

            player_id = player.get('playerId')
            if not player_id:
                continue

            # Fetch player details
            try:
                player_url = f"{BASE_URL}/player/{player_id}/landing"
                player_response = requests.get(player_url, timeout=5)
                player_response.raise_for_status()
                player_data = player_response.json()

                # Extract current season stats
                featured_stats = player_data.get('featuredStats', {})
                regular_season = featured_stats.get('regularSeason', {})
                sub_season = regular_season.get('subSeason', {})

                if sub_season:
                    skater_count += 1
                    player_name = f"{player_data.get('firstName', {}).get('default', '')} {player_data.get('lastName', {}).get('default', '')}"
                    team_abbr = player.get('teamTriCode', 'UNK')

                    # Add to leaders lists
                    goals = sub_season.get('goals', 0)
                    assists = sub_season.get('assists', 0)
                    points = sub_season.get('points', 0)

                    leaders['goals'].append({
                        'rank': skater_count,
                        'player': player_name,
                        'team': team_abbr,
                        'value': goals
                    })

                    leaders['assists'].append({
                        'rank': skater_count,
                        'player': player_name,
                        'team': team_abbr,
                        'value': assists
                    })

                    leaders['points'].append({
                        'rank': skater_count,
                        'player': player_name,
                        'team': team_abbr,
                        'value': points
                    })

                    # Stop after 10 skaters
                    if skater_count >= 10:
                        break

            except Exception as e:
                logger.warning(f"Failed to fetch player {player_id} details: {e}")
                continue

        # Sort each category
        leaders['goals'].sort(key=lambda x: x['value'], reverse=True)
        leaders['assists'].sort(key=lambda x: x['value'], reverse=True)
        leaders['points'].sort(key=lambda x: x['value'], reverse=True)

        # Re-rank after sorting
        for category in ['goals', 'assists', 'points']:
            for i, player in enumerate(leaders[category], 1):
                player['rank'] = i

        return leaders

    except Exception as e:
        logger.error(f"Failed to fetch stat leaders: {e}")
        return {
            'goals': [],
            'assists': [],
            'points': [],
            'save_percentage': []
        }

def fetch_week_schedule(yesterday_date) -> List[Dict]:
    """Fetch 3-day schedule using new API - today, tomorrow, day after"""
    url = f"{BASE_URL}/scoreboard/now"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"Failed to fetch schedule: {e}")
        return []

    schedule = []
    # Start from today (yesterday + 1 day), not yesterday
    today = yesterday_date + timedelta(days=1)
    end_date = today + timedelta(days=2)  # Only show today, tomorrow, day after (3 days total)

    # Filter games for the next 3 days starting from today
    for game_date_obj in data.get('gamesByDate', []):
        game_date_str = game_date_obj.get('date')
        if not game_date_str:
            continue

        game_date = datetime.strptime(game_date_str, '%Y-%m-%d').date()

        # Only include future games (today onwards, up to 3 days from today)
        if game_date < today or game_date > end_date:
            continue

        games = []
        for game in game_date_obj.get('games', []):
            # Skip games that are already finished
            game_state = game.get('gameState', '')
            if game_state in ['OFF', 'FINAL']:
                continue

            # Parse game time and convert from UTC to ET
            start_time_utc = game.get('startTimeUTC', '')
            if start_time_utc:
                try:
                    game_time_utc = datetime.strptime(start_time_utc, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=UTC_TZ)
                    game_time_et = game_time_utc.astimezone(ET_TZ)
                except:
                    game_time_et = datetime.now(ET_TZ)
            else:
                game_time_et = datetime.now(ET_TZ)

            # Get broadcast info
            broadcasts = game.get('tvBroadcasts', [])
            broadcast = broadcasts[0].get('network', '') if broadcasts else ''

            away_team = game.get('awayTeam', {})
            home_team = game.get('homeTeam', {})

            # Extract team records (wins-losses-OT)
            away_record = away_team.get('record', '')
            home_record = home_team.get('record', '')

            games.append({
                'time': game_time_et.strftime('%H:%M'),
                'time_label': game_time_et.strftime('%I:%M %p ET'),
                'away': away_team.get('abbrev', 'UNK'),
                'away_name': away_team.get('name', {}).get('default', away_team.get('abbrev', 'UNK')),
                'away_record': away_record,
                'home': home_team.get('abbrev', 'UNK'),
                'home_name': home_team.get('name', {}).get('default', home_team.get('abbrev', 'UNK')),
                'home_record': home_record,
                'broadcast': broadcast
            })

        if games:
            schedule.append({
                'date': game_date_str,
                'day_label': game_date.strftime('%a'),
                'games': games
            })

    return schedule

def parse_game_status(game) -> str:
    """Parse game status into readable format from new API"""
    game_state = game.get('gameState', 'OFF')
    period = game.get('period', 3)
    period_descriptor = game.get('periodDescriptor', {})
    period_type = period_descriptor.get('periodType', 'REG')

    if game_state in ['OFF', 'FINAL']:
        if period > 3:
            if period_type == 'OT':
                return 'Final/OT'
            elif period_type == 'SO':
                return 'Final/SO'
        return 'Final'

    return game_state

def get_current_season() -> str:
    """Get current NHL season string (e.g., '20252026')"""
    now = datetime.now()
    if now.month >= 10:  # Season starts in October
        return f"{now.year}{now.year + 1}"
    else:
        return f"{now.year - 1}{now.year}"
