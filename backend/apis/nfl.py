"""NFL API fetcher using ESPN API"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
import pytz

logger = logging.getLogger(__name__)

ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
UTC_TZ = pytz.UTC
ET_TZ = pytz.timezone('America/New_York')


def current_nfl_season(date) -> int:
    """NFL season year: Sept+ is current year, before Sept is previous year"""
    return date.year if date.month >= 9 else date.year - 1


def fetch_all_data(yesterday_date) -> Dict[str, Any]:
    """Fetch all NFL data for the sports page"""
    logger.info(f"Fetching NFL data for {yesterday_date}")
    season = current_nfl_season(yesterday_date)
    return {
        'yesterday': fetch_yesterday_scores(yesterday_date),
        'standings': fetch_standings(season),
        'leaders': fetch_stat_leaders(season),
        'schedule': fetch_upcoming_schedule(yesterday_date)
    }


def fetch_yesterday_scores(yesterday_date) -> Dict[str, Any]:
    """Fetch completed NFL games for the given date"""
    date_str = yesterday_date.strftime('%Y%m%d')

    try:
        url = f"{ESPN_BASE}/scoreboard?dates={date_str}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        games = []
        for event in data.get('events', []):
            status = event.get('status', {}).get('type', {})
            if not status.get('completed', False):
                continue

            competition = event.get('competitions', [{}])[0]
            competitors = competition.get('competitors', [])
            if len(competitors) < 2:
                continue

            home_team = next((t for t in competitors if t.get('homeAway') == 'home'), None)
            away_team = next((t for t in competitors if t.get('homeAway') == 'away'), None)
            if not home_team or not away_team:
                continue

            game_id = event.get('id', '')
            box_score = fetch_box_score(game_id)

            # Check for OT
            status_detail = status.get('shortDetail', 'Final')
            game_status = 'Final/OT' if 'OT' in status_detail else 'Final'

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
                'status': game_status,
                'box_score': box_score
            })

        logger.info(f"Found {len(games)} NFL games for {yesterday_date}")
        return {'date': str(yesterday_date), 'games': games}

    except Exception as e:
        logger.error(f"Failed to fetch NFL scores: {e}")
        return {'date': str(yesterday_date), 'games': []}


def fetch_box_score(game_id: str) -> Dict[str, Any]:
    """Fetch quarter-by-quarter line score"""
    try:
        url = f"{ESPN_BASE}/summary?event={game_id}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        line_scores = {'away': [], 'home': []}
        for comp in data.get('header', {}).get('competitions', []):
            for competitor in comp.get('competitors', []):
                quarters = [
                    int(ls.get('displayValue', ls.get('value', 0)))
                    for ls in competitor.get('linescores', [])
                ]
                if competitor.get('homeAway') == 'home':
                    line_scores['home'] = quarters
                else:
                    line_scores['away'] = quarters

        # Top performers from box score
        scorers = []
        boxscore = data.get('boxscore', {})
        for team_data in boxscore.get('players', []):
            team_abbr = team_data.get('team', {}).get('abbreviation', 'UNK')
            for stat_group in team_data.get('statistics', []):
                labels = stat_group.get('labels', [])
                stat_name = stat_group.get('name', '')

                # Passing leaders
                if stat_name == 'passing':
                    for athlete in stat_group.get('athletes', [])[:1]:
                        stats = dict(zip(labels, athlete.get('stats', [])))
                        yds = stats.get('YDS', '0')
                        tds = stats.get('TD', '0')
                        ints = stats.get('INT', '0')
                        scorers.append({
                            'team': team_abbr,
                            'name': athlete.get('athlete', {}).get('displayName', ''),
                            'points': int(yds) if str(yds).isdigit() else 0,
                            'stat_line': f"{yds} yds, {tds} TD, {ints} INT",
                            'stat_type': 'passing'
                        })

                # Rushing leaders
                elif stat_name == 'rushing':
                    for athlete in stat_group.get('athletes', [])[:1]:
                        stats = dict(zip(labels, athlete.get('stats', [])))
                        yds = stats.get('YDS', '0')
                        tds = stats.get('TD', '0')
                        car = stats.get('CAR', '0')
                        scorers.append({
                            'team': team_abbr,
                            'name': athlete.get('athlete', {}).get('displayName', ''),
                            'points': int(yds) if str(yds).isdigit() else 0,
                            'stat_line': f"{car} car, {yds} yds, {tds} TD",
                            'stat_type': 'rushing'
                        })

                # Receiving leaders
                elif stat_name == 'receiving':
                    for athlete in stat_group.get('athletes', [])[:1]:
                        stats = dict(zip(labels, athlete.get('stats', [])))
                        yds = stats.get('YDS', '0')
                        tds = stats.get('TD', '0')
                        rec = stats.get('REC', '0')
                        scorers.append({
                            'team': team_abbr,
                            'name': athlete.get('athlete', {}).get('displayName', ''),
                            'points': int(yds) if str(yds).isdigit() else 0,
                            'stat_line': f"{rec} rec, {yds} yds, {tds} TD",
                            'stat_type': 'receiving'
                        })

        return {'line_score': line_scores, 'scorers': scorers}

    except Exception as e:
        logger.debug(f"Failed to fetch NFL box score for game {game_id}: {e}")
        return {'line_score': {'away': [], 'home': []}, 'scorers': []}


def fetch_standings(season: int) -> Dict[str, List[Dict]]:
    """Fetch NFL standings by division"""
    try:
        url = f"https://site.api.espn.com/apis/v2/sports/football/nfl/standings?season={season}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        standings = {}
        for conference in data.get('children', []):
            conf_name = conference.get('name', '')
            for division in conference.get('children', []):
                div_name = division.get('name', '')
                entries = division.get('standings', {}).get('entries', [])

                teams = []
                for i, entry in enumerate(entries):
                    team = entry.get('team', {})
                    stats = {s.get('name'): s for s in entry.get('stats', [])}

                    wins = int(stats.get('wins', {}).get('value', 0))
                    losses = int(stats.get('losses', {}).get('value', 0))
                    ties = int(stats.get('ties', {}).get('value', 0))
                    pct = stats.get('winPercent', {}).get('displayValue', '.000')
                    gb = stats.get('gamesBehind', {}).get('displayValue', '-')
                    streak = stats.get('streak', {}).get('displayValue', '-')

                    record = f"{wins}-{losses}" if ties == 0 else f"{wins}-{losses}-{ties}"
                    teams.append({
                        'rank': i + 1,
                        'team': team.get('abbreviation', 'UNK'),
                        'team_name': team.get('displayName', 'Unknown'),
                        'wins': wins,
                        'losses': losses,
                        'ties': ties,
                        'record': record,
                        'pct': pct,
                        'gb': gb,
                        'streak': streak
                    })

                standings[div_name] = teams

        return standings

    except Exception as e:
        logger.error(f"Failed to fetch NFL standings: {e}")
        return {}


def fetch_stat_leaders(season: int) -> Dict[str, List[Dict]]:
    """Fetch NFL statistical leaders"""
    leaders = {
        'passing_yards': [],
        'rushing_yards': [],
        'receiving_yards': [],
        'touchdowns': [],
        'sacks': [],
        'interceptions': []
    }

    category_map = {
        'passingYards': 'passing_yards',
        'rushingYards': 'rushing_yards',
        'receivingYards': 'receiving_yards',
        'totalTouchdowns': 'touchdowns',
        'sacks': 'sacks',
        'interceptions': 'interceptions'
    }

    try:
        url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/{season}/types/2/leaders"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        for cat in data.get('categories', []):
            cat_name = cat.get('name', '')
            if cat_name not in category_map:
                continue

            key = category_map[cat_name]
            for i, leader in enumerate(cat.get('leaders', [])[:10]):
                athlete_ref = leader.get('athlete', {}).get('$ref', '')
                team_ref = leader.get('team', {}).get('$ref', '')

                player_name = 'Unknown'
                team_abbr = 'UNK'

                if athlete_ref:
                    try:
                        resp = requests.get(athlete_ref, timeout=5)
                        if resp.ok:
                            player_name = resp.json().get('displayName', 'Unknown')
                    except Exception:
                        pass

                if team_ref:
                    try:
                        resp = requests.get(team_ref, timeout=5)
                        if resp.ok:
                            team_abbr = resp.json().get('abbreviation', 'UNK')
                    except Exception:
                        pass

                leaders[key].append({
                    'rank': i + 1,
                    'player': player_name,
                    'team': team_abbr,
                    'value': leader.get('value', 0)
                })

    except Exception as e:
        logger.error(f"Failed to fetch NFL stat leaders: {e}")

    return leaders


def fetch_upcoming_schedule(yesterday_date) -> List[Dict]:
    """Fetch upcoming NFL games (week ahead)"""
    schedule = []
    today = yesterday_date + timedelta(days=1)

    # Check the next 7 days for games
    for day_offset in range(7):
        target_date = today + timedelta(days=day_offset)
        date_str = target_date.strftime('%Y%m%d')

        try:
            url = f"{ESPN_BASE}/scoreboard?dates={date_str}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()

            games = []
            for event in data.get('events', []):
                status = event.get('status', {}).get('type', {})
                if status.get('completed', False):
                    continue

                competition = event.get('competitions', [{}])[0]
                competitors = competition.get('competitors', [])

                home_team = next((t for t in competitors if t.get('homeAway') == 'home'), None)
                away_team = next((t for t in competitors if t.get('homeAway') == 'away'), None)
                if not home_team or not away_team:
                    continue

                game_time_str = event.get('date', '')
                time_label = 'TBD'
                if game_time_str:
                    try:
                        dt_utc = datetime.strptime(game_time_str, '%Y-%m-%dT%H:%MZ').replace(tzinfo=UTC_TZ)
                        dt_et = dt_utc.astimezone(ET_TZ)
                        time_label = dt_et.strftime('%I:%M %p ET')
                    except Exception:
                        time_label = status.get('type', {}).get('shortDetail', 'TBD')

                games.append({
                    'time': game_time_str,
                    'time_label': time_label,
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
            logger.debug(f"Failed to fetch NFL schedule for {date_str}: {e}")
            continue

    return schedule
