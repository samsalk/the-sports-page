"""NBA API fetcher using ESPN API (more reliable from cloud environments)"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
CDN_BASE = "https://cdn.nba.com/static/json/liveData"

# Headers for CDN requests (for box scores)
CDN_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Referer': 'https://www.nba.com/'
}


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
    """Fetch yesterday's game scores using ESPN API"""
    date_str = yesterday_date.strftime('%Y%m%d')

    try:
        url = f"{ESPN_BASE}/scoreboard?dates={date_str}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        games = []
        for event in data.get('events', []):
            # Check if game is finished
            status = event.get('status', {}).get('type', {})
            if not status.get('completed', False):
                continue

            competition = event.get('competitions', [{}])[0]
            competitors = competition.get('competitors', [])

            if len(competitors) < 2:
                continue

            # ESPN returns home team first, then away
            home_team = None
            away_team = None
            for team in competitors:
                if team.get('homeAway') == 'home':
                    home_team = team
                else:
                    away_team = team

            if not home_team or not away_team:
                continue

            # Get game ID for box score (ESPN format)
            game_id = event.get('id', '')

            # Fetch box score from ESPN
            box_score = fetch_box_score_espn(game_id)

            games.append({
                'game_id': game_id,
                'away_team': {
                    'abbr': away_team.get('team', {}).get('abbreviation', 'UNK'),
                    'name': away_team.get('team', {}).get('displayName', 'Unknown'),
                    'score': int(away_team.get('score', 0))
                },
                'home_team': {
                    'abbr': home_team.get('team', {}).get('abbreviation', 'UNK'),
                    'name': home_team.get('team', {}).get('displayName', 'Unknown'),
                    'score': int(home_team.get('score', 0))
                },
                'status': 'Final',
                'periods': 4,
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


def fetch_box_score_espn(game_id) -> Dict[str, Any]:
    """Fetch box score from ESPN API"""
    try:
        url = f"{ESPN_BASE}/summary?event={game_id}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Get line score (quarter-by-quarter)
        boxscore = data.get('boxscore', {})
        line_scores = {'away': [], 'home': []}

        # Get linescores from header
        for comp in data.get('header', {}).get('competitions', []):
            for competitor in comp.get('competitors', []):
                linescores = competitor.get('linescores', [])
                # ESPN uses 'displayValue' for quarter scores
                quarters = [int(ls.get('displayValue', ls.get('value', 0))) for ls in linescores]
                if competitor.get('homeAway') == 'home':
                    line_scores['home'] = quarters
                else:
                    line_scores['away'] = quarters

        # Get top players from box score
        all_players = []
        for team_data in boxscore.get('players', []):
            team = team_data.get('team', {})
            team_abbr = team.get('abbreviation', 'UNK')

            for stat_group in team_data.get('statistics', []):
                # ESPN may have name=None for the main stats group, so don't filter

                labels = stat_group.get('labels', [])
                for athlete in stat_group.get('athletes', []):
                    stats = athlete.get('stats', [])
                    if not stats:
                        continue

                    stat_dict = dict(zip(labels, stats))

                    # Parse points
                    try:
                        points = int(stat_dict.get('PTS', 0))
                    except:
                        points = 0

                    if points > 0:
                        # Parse rebounds and assists
                        try:
                            rebounds = int(stat_dict.get('REB', 0))
                        except:
                            rebounds = 0
                        try:
                            assists = int(stat_dict.get('AST', 0))
                        except:
                            assists = 0

                        # Parse field goals (format: "10-18")
                        fg = stat_dict.get('FG', '0-0')
                        fg_parts = fg.split('-')
                        fgm = int(fg_parts[0]) if fg_parts[0].isdigit() else 0
                        fga = int(fg_parts[1]) if len(fg_parts) > 1 and fg_parts[1].isdigit() else 0

                        # Parse 3-pointers
                        fg3 = stat_dict.get('3PT', '0-0')
                        fg3_parts = fg3.split('-')
                        fg3m = int(fg3_parts[0]) if fg3_parts[0].isdigit() else 0
                        fg3a = int(fg3_parts[1]) if len(fg3_parts) > 1 and fg3_parts[1].isdigit() else 0

                        all_players.append({
                            'team': team_abbr,
                            'name': athlete.get('athlete', {}).get('displayName', 'Unknown'),
                            'points': points,
                            'rebounds': rebounds,
                            'assists': assists,
                            'fgm': fgm,
                            'fga': fga,
                            'fg3m': fg3m,
                            'fg3a': fg3a
                        })

        # Sort by points and take top 6
        all_players.sort(key=lambda x: x['points'], reverse=True)

        return {
            'line_score': line_scores,
            'scorers': all_players[:6]
        }

    except Exception as e:
        logger.debug(f"Failed to fetch ESPN box score for game {game_id}: {e}")
        return {
            'line_score': {'away': [], 'home': []},
            'scorers': []
        }


def fetch_standings() -> Dict[str, List[Dict]]:
    """Fetch NBA standings using ESPN API v2"""
    try:
        # Use v2 endpoint which has full standings data
        url = "https://site.api.espn.com/apis/v2/sports/basketball/nba/standings"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        standings = {'Eastern': [], 'Western': []}

        for group in data.get('children', []):
            conf_name = group.get('name', '')
            if 'Eastern' in conf_name:
                conf_key = 'Eastern'
            elif 'Western' in conf_name:
                conf_key = 'Western'
            else:
                continue

            entries = group.get('standings', {}).get('entries', [])
            for i, entry in enumerate(entries):
                team = entry.get('team', {})

                # Get stats - v2 uses 'name' key for stat names
                stats = {}
                display_stats = {}
                for stat in entry.get('stats', []):
                    name = stat.get('name', '')
                    stats[name] = stat.get('value', stat.get('displayValue', 0))
                    display_stats[name] = stat.get('displayValue', str(stat.get('value', '')))

                wins = int(stats.get('wins', 0))
                losses = int(stats.get('losses', 0))
                pct = float(stats.get('winPercent', 0.0))
                gb = stats.get('gamesBehind', 0)

                standings[conf_key].append({
                    'rank': i + 1,
                    'team_name': team.get('displayName', 'Unknown'),
                    'team_abbr': team.get('abbreviation', 'UNK'),
                    'wins': wins,
                    'losses': losses,
                    'win_pct': round(pct, 3),
                    'games_back': gb if gb != 0 else '-',
                    'streak': display_stats.get('streak', '-')
                })

        # Sort by win percentage descending and re-rank
        for conf_key in standings:
            standings[conf_key].sort(key=lambda x: x['win_pct'], reverse=True)
            for i, team in enumerate(standings[conf_key]):
                team['rank'] = i + 1

        return standings

    except Exception as e:
        logger.error(f"Failed to fetch NBA standings: {e}")
        return {'Eastern': [], 'Western': []}


def fetch_stat_leaders() -> Dict[str, List[Dict]]:
    """Fetch NBA statistical leaders using ESPN core API"""
    leaders = {
        'points': [],
        'rebounds': [],
        'assists': []
    }

    # Map ESPN category names to our keys
    category_map = {
        'pointsPerGame': 'points',
        'reboundsPerGame': 'rebounds',
        'assistsPerGame': 'assists'
    }

    try:
        url = "https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba/seasons/2026/types/2/leaders"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        for cat in data.get('categories', []):
            cat_name = cat.get('name', '')
            if cat_name not in category_map:
                continue

            key = category_map[cat_name]
            for i, leader in enumerate(cat.get('leaders', [])[:10]):
                # Resolve athlete name from $ref
                athlete_ref = leader.get('athlete', {}).get('$ref', '')
                team_ref = leader.get('team', {}).get('$ref', '')

                player_name = 'Unknown'
                team_abbr = 'UNK'

                if athlete_ref:
                    try:
                        resp = requests.get(athlete_ref, timeout=5)
                        if resp.ok:
                            player_name = resp.json().get('displayName', 'Unknown')
                    except:
                        pass

                if team_ref:
                    try:
                        resp = requests.get(team_ref, timeout=5)
                        if resp.ok:
                            team_abbr = resp.json().get('abbreviation', 'UNK')
                    except:
                        pass

                leaders[key].append({
                    'rank': i + 1,
                    'player': player_name,
                    'team': team_abbr,
                    'value': round(leader.get('value', 0), 1)
                })

        return leaders

    except Exception as e:
        logger.error(f"Failed to fetch NBA stat leaders: {e}")
        return leaders


def fetch_upcoming_schedule(yesterday_date) -> List[Dict]:
    """Fetch 3-day schedule using ESPN API"""
    schedule = []
    today = yesterday_date + timedelta(days=1)

    for day_offset in range(3):
        target_date = today + timedelta(days=day_offset)
        date_str = target_date.strftime('%Y%m%d')

        try:
            url = f"{ESPN_BASE}/scoreboard?dates={date_str}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()

            games = []
            for event in data.get('events', []):
                # Skip finished games
                status = event.get('status', {}).get('type', {})
                if status.get('completed', False):
                    continue

                competition = event.get('competitions', [{}])[0]
                competitors = competition.get('competitors', [])

                home_team = None
                away_team = None
                for team in competitors:
                    if team.get('homeAway') == 'home':
                        home_team = team
                    else:
                        away_team = team

                if not home_team or not away_team:
                    continue

                # Get game time
                game_time = status.get('type', {}).get('shortDetail', '')
                if not game_time:
                    game_time = event.get('date', '')
                    if game_time:
                        try:
                            dt = datetime.strptime(game_time, '%Y-%m-%dT%H:%MZ')
                            game_time = dt.strftime('%I:%M %p')
                        except:
                            game_time = 'TBD'

                games.append({
                    'time': game_time,
                    'time_label': game_time,
                    'away': away_team.get('team', {}).get('abbreviation', 'UNK'),
                    'away_name': away_team.get('team', {}).get('displayName', 'Unknown'),
                    'home': home_team.get('team', {}).get('abbreviation', 'UNK'),
                    'home_name': home_team.get('team', {}).get('displayName', 'Unknown'),
                })

            if games:
                schedule.append({
                    'date': target_date.strftime('%Y-%m-%d'),
                    'day_label': target_date.strftime('%a'),
                    'games': games
                })

        except Exception as e:
            logger.debug(f"Failed to fetch NBA schedule for {date_str}: {e}")
            continue

    return schedule
