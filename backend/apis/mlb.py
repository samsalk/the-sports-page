"""MLB API fetcher using statsapi.mlb.com (free, no authentication required)"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://statsapi.mlb.com/api/v1"

# Team abbreviation mapping
TEAM_ABBR = {
    'Arizona Diamondbacks': 'ARI', 'Atlanta Braves': 'ATL', 'Baltimore Orioles': 'BAL',
    'Boston Red Sox': 'BOS', 'Chicago Cubs': 'CHC', 'Chicago White Sox': 'CWS',
    'Cincinnati Reds': 'CIN', 'Cleveland Guardians': 'CLE', 'Colorado Rockies': 'COL',
    'Detroit Tigers': 'DET', 'Houston Astros': 'HOU', 'Kansas City Royals': 'KC',
    'Los Angeles Angels': 'LAA', 'Los Angeles Dodgers': 'LAD', 'Miami Marlins': 'MIA',
    'Milwaukee Brewers': 'MIL', 'Minnesota Twins': 'MIN', 'New York Mets': 'NYM',
    'New York Yankees': 'NYY', 'Athletics': 'OAK', 'Philadelphia Phillies': 'PHI',
    'Pittsburgh Pirates': 'PIT', 'San Diego Padres': 'SD', 'San Francisco Giants': 'SF',
    'Seattle Mariners': 'SEA', 'St. Louis Cardinals': 'STL', 'Tampa Bay Rays': 'TB',
    'Texas Rangers': 'TEX', 'Toronto Blue Jays': 'TOR', 'Washington Nationals': 'WSH'
}

def get_team_abbr(team_name: str) -> str:
    """Get team abbreviation from full name"""
    return TEAM_ABBR.get(team_name, team_name[:3].upper())


def fetch_all_data(yesterday_date) -> Dict[str, Any]:
    """Fetch all MLB data for the sports page"""
    logger.info(f"Fetching MLB data for {yesterday_date}")

    # Get current season year
    season = yesterday_date.year

    return {
        'yesterday': fetch_yesterday_scores(yesterday_date),
        'standings': fetch_standings(season),
        'leaders': fetch_stat_leaders(season),
        'schedule': fetch_upcoming_schedule(yesterday_date)
    }


def fetch_yesterday_scores(yesterday_date) -> Dict[str, Any]:
    """Fetch yesterday's game scores with full box score data"""
    date_str = yesterday_date.strftime('%Y-%m-%d')
    url = f"{BASE_URL}/schedule?sportId=1&date={date_str}&hydrate=linescore"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"Failed to fetch MLB schedule: {e}")
        return {'date': date_str, 'games': []}

    games = []
    for date_obj in data.get('dates', []):
        for game in date_obj.get('games', []):
            # Only include finished games
            if game['status']['detailedState'] != 'Final':
                continue

            game_id = game['gamePk']
            away_team = game['teams']['away']
            home_team = game['teams']['home']

            # Get detailed box score
            box_score = fetch_box_score(game_id)

            games.append({
                'game_id': game_id,
                'away_team': {
                    'abbr': get_team_abbr(away_team['team']['name']),
                    'name': away_team['team']['name'],
                    'score': away_team.get('score', 0)
                },
                'home_team': {
                    'abbr': get_team_abbr(home_team['team']['name']),
                    'name': home_team['team']['name'],
                    'score': home_team.get('score', 0)
                },
                'status': 'Final',
                'box_score': box_score
            })

    logger.info(f"Found {len(games)} MLB games for {yesterday_date}")
    return {
        'date': date_str,
        'games': games
    }


def fetch_box_score(game_id: int) -> Dict[str, Any]:
    """Fetch detailed box score for a game - newspaper style"""
    try:
        # Fetch box score data
        box_url = f"{BASE_URL}/game/{game_id}/boxscore"
        box_resp = requests.get(box_url, timeout=10)
        box_resp.raise_for_status()
        box_data = box_resp.json()

        # Fetch line score (inning-by-inning)
        line_url = f"{BASE_URL}/game/{game_id}/linescore"
        line_resp = requests.get(line_url, timeout=10)
        line_resp.raise_for_status()
        line_data = line_resp.json()

        # Build line score
        innings = line_data.get('innings', [])
        away_innings = [inn.get('away', {}).get('runs', 0) for inn in innings]
        home_innings = [inn.get('home', {}).get('runs', 0) for inn in innings]

        away_totals = line_data['teams']['away']
        home_totals = line_data['teams']['home']

        line_score = {
            'away': {
                'innings': away_innings,
                'runs': away_totals.get('runs', 0),
                'hits': away_totals.get('hits', 0),
                'errors': away_totals.get('errors', 0)
            },
            'home': {
                'innings': home_innings,
                'runs': home_totals.get('runs', 0),
                'hits': home_totals.get('hits', 0),
                'errors': home_totals.get('errors', 0)
            }
        }

        # Build batting stats for each team
        away_batting = extract_batting_stats(box_data['teams']['away'])
        home_batting = extract_batting_stats(box_data['teams']['home'])

        # Build pitching stats for each team
        away_pitching = extract_pitching_stats(box_data['teams']['away'])
        home_pitching = extract_pitching_stats(box_data['teams']['home'])

        # Get game notes (HRs, 2B, 3B, SB, etc.)
        game_notes = fetch_game_notes(game_id)

        return {
            'line_score': line_score,
            'away_batting': away_batting,
            'home_batting': home_batting,
            'away_pitching': away_pitching,
            'home_pitching': home_pitching,
            'game_notes': game_notes
        }

    except Exception as e:
        logger.debug(f"Failed to fetch MLB box score for game {game_id}: {e}")
        return {
            'line_score': {'away': {}, 'home': {}},
            'away_batting': [],
            'home_batting': [],
            'away_pitching': [],
            'home_pitching': [],
            'game_notes': {}
        }


def extract_batting_stats(team_data: Dict) -> List[Dict]:
    """Extract batting statistics in batting order"""
    batters = []
    players = team_data.get('players', {})

    # Sort by batting order
    batting_order = []
    for player_id, player in players.items():
        order = player.get('battingOrder')
        if order:
            batting_order.append((int(order), player_id, player))

    batting_order.sort(key=lambda x: x[0])

    for order, player_id, player in batting_order:
        stats = player.get('stats', {}).get('batting', {})
        if not stats:
            continue

        # Position - handle substitutes
        pos = player.get('position', {}).get('abbreviation', '')

        batters.append({
            'name': player['person']['fullName'],
            'position': pos,
            'ab': stats.get('atBats', 0),
            'r': stats.get('runs', 0),
            'h': stats.get('hits', 0),
            'rbi': stats.get('rbi', 0),
            'bb': stats.get('baseOnBalls', 0),
            'so': stats.get('strikeOuts', 0),
            'avg': stats.get('avg', '.000')
        })

    return batters


def extract_pitching_stats(team_data: Dict) -> List[Dict]:
    """Extract pitching statistics"""
    pitchers = []
    players = team_data.get('players', {})

    # Get pitchers who appeared in game
    for player_id, player in players.items():
        stats = player.get('stats', {}).get('pitching', {})
        if not stats.get('inningsPitched'):
            continue

        # Determine W/L/S/H
        game_status = player.get('gameStatus', {})
        result = ''
        if game_status.get('isWinner'):
            result = 'W'
        elif game_status.get('isLoser'):
            result = 'L'
        elif stats.get('saves', 0) > 0:
            result = 'S'
        elif stats.get('holds', 0) > 0:
            result = 'H'

        # Season record for W/L pitchers
        season_stats = player.get('seasonStats', {}).get('pitching', {})
        record = ''
        if result in ['W', 'L']:
            wins = season_stats.get('wins', 0)
            losses = season_stats.get('losses', 0)
            record = f"{wins}-{losses}"

        pitchers.append({
            'name': player['person']['fullName'],
            'result': result,
            'record': record,
            'ip': stats.get('inningsPitched', '0.0'),
            'h': stats.get('hits', 0),
            'r': stats.get('runs', 0),
            'er': stats.get('earnedRuns', 0),
            'bb': stats.get('baseOnBalls', 0),
            'so': stats.get('strikeOuts', 0),
            'np': stats.get('numberOfPitches', 0),
            'era': season_stats.get('era', '0.00')
        })

    return pitchers


def fetch_game_notes(game_id: int) -> Dict[str, List[str]]:
    """Extract game notes from play-by-play (HRs, 2B, 3B, SB, etc.)"""
    try:
        url = f"{BASE_URL}/game/{game_id}/playByPlay"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        home_runs = []
        doubles = []
        triples = []
        stolen_bases = []
        double_plays = 0

        for play in data.get('allPlays', []):
            result = play.get('result', {})
            event = result.get('event', '')
            desc = result.get('description', '')
            batter = play.get('matchup', {}).get('batter', {}).get('fullName', '')

            if 'Home Run' in event:
                # Extract HR details
                rbi = play.get('result', {}).get('rbi', 1)
                hr_desc = f"{batter} ({rbi})"
                home_runs.append(hr_desc)
            elif event == 'Double':
                doubles.append(batter)
            elif event == 'Triple':
                triples.append(batter)
            elif 'Stolen Base' in event:
                runners = play.get('runners', [])
                for runner in runners:
                    if runner.get('movement', {}).get('isOut') == False:
                        runner_name = runner.get('details', {}).get('runner', {}).get('fullName', '')
                        if runner_name and runner_name not in stolen_bases:
                            stolen_bases.append(runner_name)
            elif 'Double Play' in event or 'DP' in event:
                double_plays += 1

        return {
            'hr': home_runs,
            '2b': doubles,
            '3b': triples,
            'sb': stolen_bases,
            'dp': double_plays
        }

    except Exception as e:
        logger.debug(f"Failed to fetch game notes for {game_id}: {e}")
        return {'hr': [], '2b': [], '3b': [], 'sb': [], 'dp': 0}


def fetch_standings(season: int) -> Dict[str, List[Dict]]:
    """Fetch MLB standings by division"""
    url = f"{BASE_URL}/standings?leagueId=103,104&season={season}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"Failed to fetch MLB standings: {e}")
        return {}

    standings = {}

    for record in data.get('records', []):
        division = record.get('division', {}).get('name', 'Unknown')
        # Simplify division name
        div_short = division.replace('American League ', 'AL ').replace('National League ', 'NL ')

        teams = []
        for team_record in record.get('teamRecords', []):
            teams.append({
                'rank': len(teams) + 1,
                'team': get_team_abbr(team_record['team']['name']),
                'team_name': team_record['team']['name'],
                'wins': team_record['wins'],
                'losses': team_record['losses'],
                'pct': team_record['winningPercentage'],
                'gb': team_record.get('gamesBack', '-'),
                'home': team_record.get('records', {}).get('splitRecords', [{}])[0].get('wins', 0),
                'away': team_record.get('records', {}).get('splitRecords', [{}])[1].get('wins', 0),
                'streak': team_record.get('streak', {}).get('streakCode', '-')
            })

        standings[div_short] = teams

    return standings


def fetch_stat_leaders(season: int) -> Dict[str, List[Dict]]:
    """Fetch MLB statistical leaders"""
    leaders = {
        'batting_avg': [],
        'home_runs': [],
        'rbi': [],
        'wins': [],
        'era': [],
        'strikeouts': []
    }

    # Batting leaders
    batting_categories = {
        'batting_avg': 'battingAverage',
        'home_runs': 'homeRuns',
        'rbi': 'runsBattedIn'
    }

    try:
        for key, cat in batting_categories.items():
            url = f"{BASE_URL}/stats/leaders?leaderCategories={cat}&season={season}&limit=10&playerPool=qualified"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            for category in data.get('leagueLeaders', []):
                if category.get('leaderCategory') == cat:
                    for leader in category.get('leaders', [])[:10]:
                        leaders[key].append({
                            'rank': leader.get('rank', 0),
                            'player': leader.get('person', {}).get('fullName', ''),
                            'team': get_team_abbr(leader.get('team', {}).get('name', '')),
                            'value': leader.get('value', '')
                        })
                    break
    except Exception as e:
        logger.error(f"Failed to fetch batting leaders: {e}")

    # Pitching leaders
    pitching_categories = {
        'wins': 'wins',
        'era': 'earnedRunAverage',
        'strikeouts': 'strikeouts'
    }

    try:
        for key, cat in pitching_categories.items():
            url = f"{BASE_URL}/stats/leaders?leaderCategories={cat}&season={season}&limit=10&playerPool=qualified"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            for category in data.get('leagueLeaders', []):
                if category.get('leaderCategory') == cat:
                    for leader in category.get('leaders', [])[:10]:
                        leaders[key].append({
                            'rank': leader.get('rank', 0),
                            'player': leader.get('person', {}).get('fullName', ''),
                            'team': get_team_abbr(leader.get('team', {}).get('name', '')),
                            'value': leader.get('value', '')
                        })
                    break
    except Exception as e:
        logger.error(f"Failed to fetch pitching leaders: {e}")

    return leaders


def fetch_upcoming_schedule(yesterday_date) -> List[Dict]:
    """Fetch 3-day schedule"""
    schedule = []
    today = yesterday_date + timedelta(days=1)

    for day_offset in range(3):
        target_date = today + timedelta(days=day_offset)
        date_str = target_date.strftime('%Y-%m-%d')

        try:
            url = f"{BASE_URL}/schedule?sportId=1&date={date_str}"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            games = []
            for date_obj in data.get('dates', []):
                for game in date_obj.get('games', []):
                    # Skip finished games
                    if game['status']['detailedState'] == 'Final':
                        continue

                    # Parse game time
                    game_time = game.get('gameDate', '')
                    time_label = ''
                    if game_time:
                        try:
                            dt = datetime.strptime(game_time, '%Y-%m-%dT%H:%M:%SZ')
                            time_label = dt.strftime('%I:%M %p')
                        except:
                            time_label = game['status'].get('abstractGameState', '')

                    away = game['teams']['away']
                    home = game['teams']['home']

                    games.append({
                        'time': game_time,
                        'time_label': time_label,
                        'away': get_team_abbr(away['team']['name']),
                        'away_name': away['team']['name'],
                        'home': get_team_abbr(home['team']['name']),
                        'home_name': home['team']['name']
                    })

            if games:
                schedule.append({
                    'date': date_str,
                    'day_label': target_date.strftime('%a'),
                    'games': games
                })

        except Exception as e:
            logger.debug(f"Failed to fetch MLB schedule for {date_str}: {e}")
            continue

    return schedule
