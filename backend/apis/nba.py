"""NBA API fetcher using cdn.nba.com and nba_api library"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
from nba_api.stats.endpoints import leaguestandings, leagueleaders, scoreboardv2
from nba_api.live.nba.endpoints import scoreboard

logger = logging.getLogger(__name__)

BASE_URL = "https://cdn.nba.com/static/json/liveData"

# Headers to mimic browser requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Referer': 'https://www.nba.com/'
}

# Current NBA season
CURRENT_SEASON = "2025-26"

def fetch_all_data(yesterday_date) -> Dict[str, Any]:
    """Fetch all NBA data for the sports page"""
    logger.info(f"Fetching NBA data for {yesterday_date}")
    return {
        'yesterday': fetch_yesterday_scores(yesterday_date),
        'standings': fetch_standings(),
        'leaders': fetch_stat_leaders(),
        'schedule': fetch_upcoming_schedule(yesterday_date)
    }

def fetch_yesterday_scores(yesterday_date) -> Dict[str, Any]:
    """Fetch yesterday's game scores using nba_api scoreboardv2"""
    try:
        # Use scoreboardv2 which can fetch historical data
        date_str = yesterday_date.strftime('%Y-%m-%d')
        scoreboard_data = scoreboardv2.ScoreboardV2(game_date=date_str).get_dict()

        games = []
        game_headers = []
        line_score_data = {}

        # Parse result sets
        for result_set in scoreboard_data.get('resultSets', []):
            name = result_set.get('name', '')
            headers = result_set.get('headers', [])
            rows = result_set.get('rowSet', [])

            if name == 'GameHeader':
                game_headers = [(dict(zip(headers, row))) for row in rows]
            elif name == 'LineScore':
                # Build line score lookup by game_id and team_id
                for row in rows:
                    row_dict = dict(zip(headers, row))
                    game_id = row_dict.get('GAME_ID', '')
                    team_id = row_dict.get('TEAM_ID', '')
                    if game_id not in line_score_data:
                        line_score_data[game_id] = {}
                    line_score_data[game_id][team_id] = row_dict

        for game in game_headers:
            game_id = game.get('GAME_ID', '')
            game_status = game.get('GAME_STATUS_ID', 0)

            # Only include finished games (status 3 = Final)
            if game_status != 3:
                continue

            # Get team info from line score data
            home_team_id = game.get('HOME_TEAM_ID', '')
            away_team_id = game.get('VISITOR_TEAM_ID', '')

            game_line_scores = line_score_data.get(game_id, {})
            home_line = game_line_scores.get(home_team_id, {})
            away_line = game_line_scores.get(away_team_id, {})

            # Fetch detailed box score
            box_score = fetch_box_score(game_id)

            games.append({
                'game_id': game_id,
                'away_team': {
                    'abbr': away_line.get('TEAM_ABBREVIATION', 'UNK'),
                    'name': away_line.get('TEAM_CITY_NAME', 'Unknown'),
                    'score': away_line.get('PTS', 0) or 0
                },
                'home_team': {
                    'abbr': home_line.get('TEAM_ABBREVIATION', 'UNK'),
                    'name': home_line.get('TEAM_CITY_NAME', 'Unknown'),
                    'score': home_line.get('PTS', 0) or 0
                },
                'status': 'Final',
                'periods': 4,  # Will be updated from box score if OT
                'box_score': box_score
            })

        logger.info(f"Found {len(games)} NBA games for {yesterday_date}")
        return {
            'date': str(yesterday_date),
            'games': games
        }

    except Exception as e:
        logger.error(f"Failed to fetch NBA scores: {e}")
        return {'date': str(yesterday_date), 'games': []}

def fetch_box_score(game_id) -> Dict[str, Any]:
    """Fetch detailed box score for a game using CDN endpoint"""
    url = f"{BASE_URL}/boxscore/boxscore_{game_id}.json"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        game = data.get('game', {})
        home = game.get('homeTeam', {})
        away = game.get('awayTeam', {})

        # Extract quarter-by-quarter scores
        home_periods = [p.get('score', 0) for p in home.get('periods', [])]
        away_periods = [p.get('score', 0) for p in away.get('periods', [])]

        # Extract player stats from both teams
        all_players = []
        for team_data, team_type in [(home, 'home'), (away, 'away')]:
            team_abbr = team_data.get('teamTricode', 'UNK')
            for player in team_data.get('players', []):
                stats = player.get('statistics', {})
                points = stats.get('points', 0)

                if points and points > 0:
                    all_players.append({
                        'team': team_abbr,
                        'name': player.get('name', 'Unknown'),
                        'points': points,
                        'rebounds': stats.get('reboundsTotal', 0),
                        'assists': stats.get('assists', 0),
                        'minutes': stats.get('minutes', ''),
                        'fgm': stats.get('fieldGoalsMade', 0),
                        'fga': stats.get('fieldGoalsAttempted', 0),
                        'fg3m': stats.get('threePointersMade', 0),
                        'fg3a': stats.get('threePointersAttempted', 0),
                        'ftm': stats.get('freeThrowsMade', 0),
                        'fta': stats.get('freeThrowsAttempted', 0),
                        'steals': stats.get('steals', 0),
                        'blocks': stats.get('blocks', 0),
                        'turnovers': stats.get('turnovers', 0),
                    })

        # Sort by points and take top 6
        all_players.sort(key=lambda x: x['points'], reverse=True)

        return {
            'line_score': {
                'away': away_periods,
                'home': home_periods
            },
            'scorers': all_players[:6]
        }

    except Exception as e:
        logger.debug(f"Failed to fetch NBA box score for game {game_id}: {e}")
        return {
            'line_score': {'away': [], 'home': []},
            'scorers': []
        }

def fetch_standings() -> Dict[str, List[Dict]]:
    """Fetch NBA standings using nba_api"""
    try:
        standings_data = leaguestandings.LeagueStandings(
            league_id='00',
            season=CURRENT_SEASON,
            season_type='Regular Season'
        ).get_dict()

        standings = {'Eastern': [], 'Western': []}

        # Parse the resultSets from the API response
        for result_set in standings_data.get('resultSets', []):
            if result_set.get('name') == 'Standings':
                headers = result_set.get('headers', [])
                rows = result_set.get('rowSet', [])

                for row in rows:
                    # Create a dict mapping headers to row values
                    team_dict = dict(zip(headers, row))

                    # Determine conference - map 'East'/'West' to 'Eastern'/'Western'
                    conf_short = team_dict.get('Conference', '')
                    conf_name = 'Eastern' if conf_short == 'East' else 'Western' if conf_short == 'West' else ''

                    if not conf_name:
                        continue

                    # Extract relevant data
                    team_data = {
                        'rank': team_dict.get('PlayoffRank', 0),
                        'team_name': f"{team_dict.get('TeamCity', '')} {team_dict.get('TeamName', 'Unknown')}",
                        'team_abbr': team_dict.get('TeamCity', 'UNK'),
                        'wins': team_dict.get('WINS', 0),
                        'losses': team_dict.get('LOSSES', 0),
                        'win_pct': round(team_dict.get('WinPCT', 0.0), 3),
                        'games_back': team_dict.get('ConferenceGamesBack', 0.0) or 0,
                        'home_record': team_dict.get('HOME', '0-0'),
                        'away_record': team_dict.get('ROAD', '0-0'),
                        'last_10': team_dict.get('L10', '0-0'),
                        'streak': team_dict.get('strCurrentStreak', '')
                    }
                    standings[conf_name].append(team_data)

        return standings

    except Exception as e:
        logger.error(f"Failed to fetch NBA standings: {e}")
        return {'Eastern': [], 'Western': []}

def fetch_stat_leaders() -> Dict[str, List[Dict]]:
    """Fetch NBA statistical leaders using nba_api"""
    leaders = {
        'points': [],
        'rebounds': [],
        'assists': []
    }

    stat_categories = {
        'points': 'PTS',
        'rebounds': 'REB',
        'assists': 'AST'
    }

    try:
        for category_name, stat_code in stat_categories.items():
            try:
                leaders_data = leagueleaders.LeagueLeaders(
                    league_id='00',
                    per_mode48='PerGame',
                    scope='S',
                    season=CURRENT_SEASON,
                    season_type_all_star='Regular Season',
                    stat_category_abbreviation=stat_code
                ).get_dict()

                # Parse the resultSet (singular) from the API response
                result_set = leaders_data.get('resultSet', {})
                headers = result_set.get('headers', [])
                rows = result_set.get('rowSet', [])

                # Get top 10 players
                for i, row in enumerate(rows[:10]):
                    player_dict = dict(zip(headers, row))

                    leaders[category_name].append({
                        'rank': i + 1,
                        'player': player_dict.get('PLAYER', 'Unknown'),
                        'team': player_dict.get('TEAM', 'UNK'),
                        'value': player_dict.get(stat_code, 0)
                    })

            except Exception as e:
                logger.error(f"Failed to fetch NBA {category_name} leaders: {e}")
                continue

        return leaders

    except Exception as e:
        logger.error(f"Failed to fetch NBA stat leaders: {e}")
        return leaders

def fetch_upcoming_schedule(yesterday_date) -> List[Dict]:
    """Fetch 3-day schedule - today, tomorrow, day after using scoreboardv2"""
    schedule = []
    today = yesterday_date + timedelta(days=1)

    # Fetch 3 days: today, tomorrow, day after
    for day_offset in range(3):
        target_date = today + timedelta(days=day_offset)
        date_str = target_date.strftime('%Y-%m-%d')

        try:
            scoreboard_data = scoreboardv2.ScoreboardV2(game_date=date_str).get_dict()

            # Parse game headers and line scores
            game_headers = []
            line_score_data = {}

            for result_set in scoreboard_data.get('resultSets', []):
                name = result_set.get('name', '')
                headers = result_set.get('headers', [])
                rows = result_set.get('rowSet', [])

                if name == 'GameHeader':
                    game_headers = [dict(zip(headers, row)) for row in rows]
                elif name == 'LineScore':
                    for row in rows:
                        row_dict = dict(zip(headers, row))
                        game_id = row_dict.get('GAME_ID', '')
                        team_id = row_dict.get('TEAM_ID', '')
                        if game_id not in line_score_data:
                            line_score_data[game_id] = {}
                        line_score_data[game_id][team_id] = row_dict

            games = []
            for game in game_headers:
                game_id = game.get('GAME_ID', '')
                game_status = game.get('GAME_STATUS_ID', 0)

                # Skip finished games
                if game_status == 3:
                    continue

                # Get team info from line score
                home_team_id = game.get('HOME_TEAM_ID', '')
                away_team_id = game.get('VISITOR_TEAM_ID', '')

                game_line_scores = line_score_data.get(game_id, {})
                home_line = game_line_scores.get(home_team_id, {})
                away_line = game_line_scores.get(away_team_id, {})

                # Parse game time from status text (e.g., "7:00 pm ET")
                game_time_text = game.get('GAME_STATUS_TEXT', '')

                games.append({
                    'time': game_time_text,
                    'time_label': game_time_text,
                    'away': away_line.get('TEAM_ABBREVIATION', 'UNK'),
                    'away_name': away_line.get('TEAM_CITY_NAME', 'Unknown'),
                    'away_record': away_line.get('TEAM_WINS_LOSSES', ''),
                    'home': home_line.get('TEAM_ABBREVIATION', 'UNK'),
                    'home_name': home_line.get('TEAM_CITY_NAME', 'Unknown'),
                    'home_record': home_line.get('TEAM_WINS_LOSSES', ''),
                    'broadcast': ''
                })

            if games:
                schedule.append({
                    'date': date_str,
                    'day_label': target_date.strftime('%a'),
                    'games': games
                })

        except Exception as e:
            logger.debug(f"Failed to fetch NBA schedule for {date_str}: {e}")
            continue

    return schedule
