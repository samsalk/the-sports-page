#!/usr/bin/env python3
"""
Create sample data for testing when APIs are unavailable
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import pytz

TIMEZONE = pytz.timezone('America/New_York')
OUTPUT_DIR = Path(__file__).parent.parent / 'frontend' / 'data'
OUTPUT_FILE = OUTPUT_DIR / 'sports_data.json'

def create_sample_data():
    """Generate sample sports data for testing"""
    now_et = datetime.now(TIMEZONE)
    yesterday = (now_et - timedelta(days=1)).date()

    data = {
        'generated_at': now_et.isoformat(),
        'date_label': now_et.strftime('%A, %B %d, %Y'),
        'leagues': {
            'nhl': {
                'yesterday': {
                    'date': yesterday.strftime('%Y-%m-%d'),
                    'games': [
                        {
                            'game_id': '2024020123',
                            'away_team': {'abbr': 'BOS', 'name': 'Boston Bruins', 'score': 3},
                            'home_team': {'abbr': 'NYR', 'name': 'New York Rangers', 'score': 4},
                            'status': 'Final/OT',
                            'periods': 4,
                            'box_score': {
                                'line_score': {
                                    'away': [1, 1, 1, 0],
                                    'home': [0, 2, 1, 1]
                                },
                                'shots': {'away': 32, 'home': 28},
                                'goalies': [
                                    {'team': 'BOS', 'name': 'J. Swayman', 'saves': 24, 'shots': 28, 'save_pct': 0.857},
                                    {'team': 'NYR', 'name': 'I. Shesterkin', 'saves': 29, 'shots': 32, 'save_pct': 0.906}
                                ]
                            }
                        },
                        {
                            'game_id': '2024020124',
                            'away_team': {'abbr': 'TOR', 'name': 'Toronto Maple Leafs', 'score': 5},
                            'home_team': {'abbr': 'MTL', 'name': 'Montreal Canadiens', 'score': 2},
                            'status': 'Final',
                            'periods': 3,
                            'box_score': {
                                'line_score': {
                                    'away': [2, 2, 1],
                                    'home': [1, 0, 1]
                                },
                                'shots': {'away': 38, 'home': 25},
                                'goalies': [
                                    {'team': 'TOR', 'name': 'I. Samsonov', 'saves': 23, 'shots': 25, 'save_pct': 0.920},
                                    {'team': 'MTL', 'name': 'S. Montembeault', 'saves': 33, 'shots': 38, 'save_pct': 0.868}
                                ]
                            }
                        },
                        {
                            'game_id': '2024020125',
                            'away_team': {'abbr': 'EDM', 'name': 'Edmonton Oilers', 'score': 6},
                            'home_team': {'abbr': 'CGY', 'name': 'Calgary Flames', 'score': 3},
                            'status': 'Final',
                            'periods': 3,
                            'box_score': {
                                'line_score': {
                                    'away': [2, 3, 1],
                                    'home': [1, 1, 1]
                                },
                                'shots': {'away': 35, 'home': 28},
                                'goalies': [
                                    {'team': 'EDM', 'name': 'S. Skinner', 'saves': 25, 'shots': 28, 'save_pct': 0.893},
                                    {'team': 'CGY', 'name': 'D. Vladar', 'saves': 29, 'shots': 35, 'save_pct': 0.829}
                                ]
                            }
                        }
                    ]
                },
                'standings': {
                    'Atlantic Division': [
                        {'rank': 1, 'team': 'BOS', 'team_name': 'Boston Bruins', 'wins': 28, 'losses': 12, 'ot_losses': 3, 'points': 59, 'games_played': 43, 'win_pct': 0.686, 'games_behind': 0.0, 'streak': 'L1'},
                        {'rank': 2, 'team': 'TOR', 'team_name': 'Toronto Maple Leafs', 'wins': 27, 'losses': 13, 'ot_losses': 2, 'points': 56, 'games_played': 42, 'win_pct': 0.667, 'games_behind': 1.5, 'streak': 'W1'},
                        {'rank': 3, 'team': 'FLA', 'team_name': 'Florida Panthers', 'wins': 24, 'losses': 15, 'ot_losses': 3, 'points': 51, 'games_played': 42, 'win_pct': 0.607, 'games_behind': 4.0, 'streak': 'L2'},
                        {'rank': 4, 'team': 'TBL', 'team_name': 'Tampa Bay Lightning', 'wins': 23, 'losses': 16, 'ot_losses': 3, 'points': 49, 'games_played': 42, 'win_pct': 0.583, 'games_behind': 5.0, 'streak': 'W1'},
                        {'rank': 5, 'team': 'MTL', 'team_name': 'Montreal Canadiens', 'wins': 18, 'losses': 20, 'ot_losses': 4, 'points': 40, 'games_played': 42, 'win_pct': 0.476, 'games_behind': 9.5, 'streak': 'L1'}
                    ],
                    'Metropolitan Division': [
                        {'rank': 1, 'team': 'NYR', 'team_name': 'New York Rangers', 'wins': 29, 'losses': 11, 'ot_losses': 2, 'points': 60, 'games_played': 42, 'win_pct': 0.714, 'games_behind': 0.0, 'streak': 'W1'},
                        {'rank': 2, 'team': 'CAR', 'team_name': 'Carolina Hurricanes', 'wins': 27, 'losses': 13, 'ot_losses': 2, 'points': 56, 'games_played': 42, 'win_pct': 0.667, 'games_behind': 2.0, 'streak': 'W2'},
                        {'rank': 3, 'team': 'NJD', 'team_name': 'New Jersey Devils', 'wins': 25, 'losses': 14, 'ot_losses': 3, 'points': 53, 'games_played': 42, 'win_pct': 0.631, 'games_behind': 3.5, 'streak': 'W3'},
                        {'rank': 4, 'team': 'WSH', 'team_name': 'Washington Capitals', 'wins': 22, 'losses': 16, 'ot_losses': 4, 'points': 48, 'games_played': 42, 'win_pct': 0.571, 'games_behind': 6.0, 'streak': 'L1'}
                    ],
                    'Pacific Division': [
                        {'rank': 1, 'team': 'VGK', 'team_name': 'Vegas Golden Knights', 'wins': 30, 'losses': 10, 'ot_losses': 2, 'points': 62, 'games_played': 42, 'win_pct': 0.738, 'games_behind': 0.0, 'streak': 'W4'},
                        {'rank': 2, 'team': 'EDM', 'team_name': 'Edmonton Oilers', 'wins': 28, 'losses': 12, 'ot_losses': 2, 'points': 58, 'games_played': 42, 'win_pct': 0.690, 'games_behind': 2.0, 'streak': 'W1'},
                        {'rank': 3, 'team': 'VAN', 'team_name': 'Vancouver Canucks', 'wins': 24, 'losses': 15, 'ot_losses': 3, 'points': 51, 'games_played': 42, 'win_pct': 0.607, 'games_behind': 5.5, 'streak': 'W2'},
                        {'rank': 4, 'team': 'CGY', 'team_name': 'Calgary Flames', 'wins': 20, 'losses': 18, 'ot_losses': 4, 'points': 44, 'games_played': 42, 'win_pct': 0.524, 'games_behind': 9.0, 'streak': 'L1'}
                    ]
                },
                'leaders': {
                    'goals': [
                        {'rank': 1, 'player': 'Auston Matthews', 'team': 'TOR', 'value': 38},
                        {'rank': 2, 'player': 'David Pastrnak', 'team': 'BOS', 'value': 35},
                        {'rank': 3, 'player': 'Connor McDavid', 'team': 'EDM', 'value': 32},
                        {'rank': 4, 'player': 'Leon Draisaitl', 'team': 'EDM', 'value': 31},
                        {'rank': 5, 'player': 'Artemi Panarin', 'team': 'NYR', 'value': 29}
                    ],
                    'assists': [
                        {'rank': 1, 'player': 'Connor McDavid', 'team': 'EDM', 'value': 52},
                        {'rank': 2, 'player': 'Nathan MacKinnon', 'team': 'COL', 'value': 48},
                        {'rank': 3, 'player': 'Nikita Kucherov', 'team': 'TBL', 'value': 46},
                        {'rank': 4, 'player': 'Cale Makar', 'team': 'COL', 'value': 42},
                        {'rank': 5, 'player': 'Artemi Panarin', 'team': 'NYR', 'value': 41}
                    ],
                    'points': [
                        {'rank': 1, 'player': 'Connor McDavid', 'team': 'EDM', 'value': 84},
                        {'rank': 2, 'player': 'Nathan MacKinnon', 'team': 'COL', 'value': 76},
                        {'rank': 3, 'player': 'Nikita Kucherov', 'team': 'TBL', 'value': 74},
                        {'rank': 4, 'player': 'Artemi Panarin', 'team': 'NYR', 'value': 70},
                        {'rank': 5, 'player': 'Auston Matthews', 'team': 'TOR', 'value': 68}
                    ],
                    'save_percentage': []
                },
                'schedule': [
                    {
                        'date': now_et.strftime('%Y-%m-%d'),
                        'day_label': now_et.strftime('%a'),
                        'games': [
                            {'time': '19:00', 'time_label': '07:00 PM', 'away': 'BOS', 'home': 'TBL', 'broadcast': 'ESPN+'},
                            {'time': '20:00', 'time_label': '08:00 PM', 'away': 'CHI', 'home': 'COL', 'broadcast': 'TNT'},
                            {'time': '22:00', 'time_label': '10:00 PM', 'away': 'LAK', 'home': 'VGK', 'broadcast': 'ESPN+'}
                        ]
                    },
                    {
                        'date': (now_et + timedelta(days=1)).strftime('%Y-%m-%d'),
                        'day_label': (now_et + timedelta(days=1)).strftime('%a'),
                        'games': [
                            {'time': '19:30', 'time_label': '07:30 PM', 'away': 'TOR', 'home': 'BOS', 'broadcast': ''},
                            {'time': '20:00', 'time_label': '08:00 PM', 'away': 'EDM', 'home': 'DAL', 'broadcast': 'TNT'}
                        ]
                    },
                    {
                        'date': (now_et + timedelta(days=2)).strftime('%Y-%m-%d'),
                        'day_label': (now_et + timedelta(days=2)).strftime('%a'),
                        'games': []
                    },
                    {
                        'date': (now_et + timedelta(days=3)).strftime('%Y-%m-%d'),
                        'day_label': (now_et + timedelta(days=3)).strftime('%a'),
                        'games': [
                            {'time': '19:00', 'time_label': '07:00 PM', 'away': 'NYR', 'home': 'WSH', 'broadcast': 'ESPN'},
                            {'time': '19:30', 'time_label': '07:30 PM', 'away': 'MTL', 'home': 'TOR', 'broadcast': ''}
                        ]
                    }
                ]
            },
            'epl': {
                'yesterday': {
                    'date': yesterday.strftime('%Y-%m-%d'),
                    'games': [
                        {
                            'match_id': 12345,
                            'home_team': {'abbr': 'MCI', 'name': 'Manchester City FC', 'score': 2},
                            'away_team': {'abbr': 'LIV', 'name': 'Liverpool FC', 'score': 1},
                            'status': 'FINISHED',
                            'half_time_score': '1-0',
                            'box_score': None
                        },
                        {
                            'match_id': 12346,
                            'home_team': {'abbr': 'ARS', 'name': 'Arsenal FC', 'score': 3},
                            'away_team': {'abbr': 'CHE', 'name': 'Chelsea FC', 'score': 3},
                            'status': 'FINISHED',
                            'half_time_score': '2-1',
                            'box_score': None
                        },
                        {
                            'match_id': 12347,
                            'home_team': {'abbr': 'MUN', 'name': 'Manchester United FC', 'score': 1},
                            'away_team': {'abbr': 'NEW', 'name': 'Newcastle United FC', 'score': 0},
                            'status': 'FINISHED',
                            'half_time_score': '0-0',
                            'box_score': None
                        }
                    ]
                },
                'standings': {
                    'Premier League': [
                        {'rank': 1, 'team': 'LIV', 'team_name': 'Liverpool FC', 'played': 20, 'wins': 15, 'draws': 3, 'losses': 2, 'goals_for': 45, 'goals_against': 19, 'goal_diff': 26, 'points': 48, 'form': 'WWDWL'},
                        {'rank': 2, 'team': 'MCI', 'team_name': 'Manchester City FC', 'played': 20, 'wins': 15, 'draws': 3, 'losses': 2, 'goals_for': 50, 'goals_against': 20, 'goal_diff': 30, 'points': 48, 'form': 'WWDWW'},
                        {'rank': 3, 'team': 'ARS', 'team_name': 'Arsenal FC', 'played': 20, 'wins': 13, 'draws': 6, 'losses': 1, 'goals_for': 45, 'goals_against': 19, 'goal_diff': 26, 'points': 45, 'form': 'WDWDD'},
                        {'rank': 4, 'team': 'CHE', 'team_name': 'Chelsea FC', 'played': 20, 'wins': 11, 'draws': 7, 'losses': 2, 'goals_for': 41, 'goals_against': 22, 'goal_diff': 19, 'points': 40, 'form': 'DWDWD'},
                        {'rank': 5, 'team': 'MUN', 'team_name': 'Manchester United FC', 'played': 20, 'wins': 11, 'draws': 5, 'losses': 4, 'goals_for': 32, 'goals_against': 24, 'goal_diff': 8, 'points': 38, 'form': 'WWLDW'},
                        {'rank': 6, 'team': 'NEW', 'team_name': 'Newcastle United FC', 'played': 20, 'wins': 10, 'draws': 6, 'losses': 4, 'goals_for': 35, 'goals_against': 25, 'goal_diff': 10, 'points': 36, 'form': 'WDWWL'}
                    ]
                },
                'leaders': {
                    'goals': [
                        {'rank': 1, 'player': 'Erling Haaland', 'team': 'MCI', 'value': 19},
                        {'rank': 2, 'player': 'Mohamed Salah', 'team': 'LIV', 'value': 16},
                        {'rank': 3, 'player': 'Bukayo Saka', 'team': 'ARS', 'value': 13},
                        {'rank': 4, 'player': 'Cole Palmer', 'team': 'CHE', 'value': 12},
                        {'rank': 5, 'player': 'Alexander Isak', 'team': 'NEW', 'value': 11}
                    ],
                    'assists': []
                },
                'schedule': [
                    {
                        'date': now_et.strftime('%Y-%m-%d'),
                        'day_label': now_et.strftime('%a'),
                        'games': [
                            {'time': '12:30', 'time_label': '12:30 PM', 'home': 'TOT', 'away': 'AVL', 'broadcast': ''},
                            {'time': '15:00', 'time_label': '03:00 PM', 'home': 'EVE', 'away': 'BHA', 'broadcast': ''}
                        ]
                    },
                    {
                        'date': (now_et + timedelta(days=1)).strftime('%Y-%m-%d'),
                        'day_label': (now_et + timedelta(days=1)).strftime('%a'),
                        'games': []
                    },
                    {
                        'date': (now_et + timedelta(days=2)).strftime('%Y-%m-%d'),
                        'day_label': (now_et + timedelta(days=2)).strftime('%a'),
                        'games': [
                            {'time': '20:00', 'time_label': '08:00 PM', 'home': 'LIV', 'away': 'MCI', 'broadcast': ''}
                        ]
                    }
                ]
            }
        }
    }

    return data

if __name__ == '__main__':
    print("Creating sample data for The Sports Page...")

    data = create_sample_data()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✓ Sample data written to {OUTPUT_FILE}")
    print(f"✓ Generated at: {data['generated_at']}")
    print(f"✓ Date: {data['date_label']}")
    print(f"✓ NHL games yesterday: {len(data['leagues']['nhl']['yesterday']['games'])}")
    print(f"✓ EPL games yesterday: {len(data['leagues']['epl']['yesterday']['games'])}")
