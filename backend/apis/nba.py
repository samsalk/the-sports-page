"""NBA API fetcher using cdn.nba.com and nba_api library"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
from nba_api.stats.endpoints import leaguestandings, leagueleaders
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
    """Fetch yesterday's game scores"""
    url = f"{BASE_URL}/scoreboard/todaysScoreboard_00.json"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"Failed to fetch NBA scores: {e}")
        return {'date': str(yesterday_date), 'games': []}

    scoreboard = data.get('scoreboard', {})
    game_date = scoreboard.get('gameDate', '')

    # Only return games from yesterday
    if game_date != yesterday_date.strftime('%Y-%m-%d'):
        logger.info(f"No games found for {yesterday_date}")
        return {'date': str(yesterday_date), 'games': []}

    games = []
    for game in scoreboard.get('games', []):
        # Only include finished games
        game_status = game.get('gameStatus', 0)
        if game_status != 3:  # 3 = Final
            continue

        away_team = game.get('awayTeam', {})
        home_team = game.get('homeTeam', {})

        # Get period data
        periods = game.get('periods', [])
        num_periods = game.get('period', 4)  # Default 4 quarters

        # Fetch detailed box score
        box_score = fetch_box_score(game.get('gameId', ''))

        games.append({
            'game_id': game.get('gameId', ''),
            'away_team': {
                'abbr': away_team.get('teamTricode', 'UNK'),
                'name': away_team.get('teamName', 'Unknown'),
                'score': away_team.get('score', 0)
            },
            'home_team': {
                'abbr': home_team.get('teamTricode', 'UNK'),
                'name': home_team.get('teamName', 'Unknown'),
                'score': home_team.get('score', 0)
            },
            'status': 'Final',
            'periods': num_periods,
            'box_score': box_score
        })

    return {
        'date': str(yesterday_date),
        'games': games
    }

def fetch_box_score(game_id) -> Dict[str, Any]:
    """Fetch detailed box score for a game using nba_api"""
    from nba_api.stats.endpoints import boxscoretraditionalv2, boxscoresummaryv2

    try:
        # Get line score (quarter-by-quarter)
        line_score_away = []
        line_score_home = []

        try:
            summary = boxscoresummaryv2.BoxScoreSummaryV2(game_id=game_id)
            summary_result = summary.get_dict()

            for result_set in summary_result.get('resultSets', []):
                if result_set.get('name') == 'LineScore':
                    headers = result_set.get('headers', [])
                    rows = result_set.get('rowSet', [])

                    for i, row in enumerate(rows):
                        team_dict = dict(zip(headers, row))

                        # Extract quarter scores (PTS_QTR1 through PTS_QTR4, plus OT if applicable)
                        quarters = []
                        for q in range(1, 11):  # Check up to 10 periods (4 quarters + 6 OT)
                            qtr_key = f'PTS_QTR{q}' if q <= 4 else f'PTS_OT{q-4}'
                            qtr_pts = team_dict.get(qtr_key)
                            if qtr_pts is not None:
                                quarters.append(qtr_pts)
                            elif q <= 4:
                                break  # Stop if regular quarter is missing

                        # First team is away, second is home
                        if i == 0:
                            line_score_away = quarters
                        elif i == 1:
                            line_score_home = quarters
        except Exception as e:
            logger.debug(f"Could not fetch line score for game {game_id}: {e}")

        # Extract top scorers (top 6 by points)
        scorers = []
        try:
            box = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
            result = box.get_dict()

            for result_set in result.get('resultSets', []):
                if result_set.get('name') == 'PlayerStats':
                    headers = result_set.get('headers', [])
                    rows = result_set.get('rowSet', [])

                    for row in rows:
                        player_dict = dict(zip(headers, row))
                        points = player_dict.get('PTS', 0)

                        if points and points > 0:  # Only include players who scored
                            scorers.append({
                                'team': player_dict.get('TEAM_ABBREVIATION', 'UNK'),
                                'name': player_dict.get('PLAYER_NAME', 'Unknown'),
                                'points': points,
                                'rebounds': player_dict.get('REB', 0),
                                'assists': player_dict.get('AST', 0)
                            })

            # Sort by points and take top 6
            scorers.sort(key=lambda x: x['points'], reverse=True)
        except Exception as e:
            logger.debug(f"Could not fetch player stats for game {game_id}: {e}")

        return {
            'line_score': {
                'away': line_score_away,
                'home': line_score_home
            },
            'scorers': scorers[:6]
        }

    except Exception as e:
        logger.error(f"Failed to fetch NBA box score for game {game_id}: {e}")
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
    """Fetch 3-day schedule - today, tomorrow, day after"""
    url = f"{BASE_URL}/scoreboard/todaysScoreboard_00.json"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"Failed to fetch NBA schedule: {e}")
        return []

    schedule = []
    today = yesterday_date + timedelta(days=1)

    scoreboard = data.get('scoreboard', {})

    # For now, this will only show today's games
    # We'd need to fetch multiple days or use the schedule endpoint
    games = []
    for game in scoreboard.get('games', []):
        # Skip finished games
        game_status = game.get('gameStatus', 0)
        if game_status == 3:  # 3 = Final
            continue

        away_team = game.get('awayTeam', {})
        home_team = game.get('homeTeam', {})

        # Parse game time
        game_time_utc = game.get('gameTimeUTC', '')
        if game_time_utc:
            try:
                game_time = datetime.strptime(game_time_utc, '%Y-%m-%dT%H:%M:%SZ')
            except:
                game_time = datetime.now()
        else:
            game_time = datetime.now()

        games.append({
            'time': game_time.strftime('%H:%M'),
            'time_label': game_time.strftime('%I:%M %p'),
            'away': away_team.get('teamTricode', 'UNK'),
            'away_name': away_team.get('teamName', 'Unknown'),
            'away_record': f"{away_team.get('wins', 0)}-{away_team.get('losses', 0)}",
            'home': home_team.get('teamTricode', 'UNK'),
            'home_name': home_team.get('teamName', 'Unknown'),
            'home_record': f"{home_team.get('wins', 0)}-{home_team.get('losses', 0)}",
            'broadcast': ''
        })

    if games:
        schedule.append({
            'date': scoreboard.get('gameDate', ''),
            'day_label': today.strftime('%a'),
            'games': games
        })

    return schedule
