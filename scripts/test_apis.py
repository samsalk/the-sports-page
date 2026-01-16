#!/usr/bin/env python3
"""
Test script to verify API connectivity and credentials
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

import requests
from apis.nhl import BASE_URL as NHL_URL
from apis.epl import BASE_URL as EPL_URL, API_KEY as EPL_KEY, get_headers

def test_nhl_api():
    """Test NHL Stats API connectivity"""
    print("Testing NHL Stats API...")
    try:
        response = requests.get(f"{NHL_URL}/standings", timeout=5)
        response.raise_for_status()
        data = response.json()

        if 'records' in data and len(data['records']) > 0:
            print("✓ NHL API is working!")
            print(f"  Found {len(data['records'])} divisions")
            return True
        else:
            print("✗ NHL API returned unexpected data")
            return False
    except Exception as e:
        print(f"✗ NHL API failed: {e}")
        return False

def test_epl_api():
    """Test Football Data API connectivity"""
    print("\nTesting Football Data API (EPL)...")

    if not EPL_KEY:
        print("✗ FOOTBALL_DATA_API_KEY environment variable not set")
        print("  Get your free API key from: https://www.football-data.org/client/register")
        print("  Then set it: export FOOTBALL_DATA_API_KEY='your_key'")
        return False

    try:
        response = requests.get(
            f"{EPL_URL}/competitions/2021/standings",
            headers=get_headers(),
            timeout=5
        )
        response.raise_for_status()
        data = response.json()

        if 'standings' in data and len(data['standings']) > 0:
            print("✓ Football Data API is working!")
            table = data['standings'][0]['table']
            print(f"  Found {len(table)} teams in Premier League")
            if table:
                print(f"  Leader: {table[0]['team']['name']} ({table[0]['points']} pts)")
            return True
        else:
            print("✗ Football Data API returned unexpected data")
            return False
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print("✗ API key is invalid or unauthorized")
            print("  Check your key at: https://www.football-data.org/client/register")
        elif e.response.status_code == 429:
            print("✗ Rate limit exceeded (10 req/min, 100/day on free tier)")
        else:
            print(f"✗ HTTP Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Football Data API failed: {e}")
        return False

def main():
    print("=" * 50)
    print("Sports Page API Connectivity Test")
    print("=" * 50)

    nhl_ok = test_nhl_api()
    epl_ok = test_epl_api()

    print("\n" + "=" * 50)
    if nhl_ok and epl_ok:
        print("✓ All APIs are working!")
        print("You're ready to run: python backend/fetch_data.py")
        return 0
    else:
        print("✗ Some APIs failed - see errors above")
        return 1

if __name__ == '__main__':
    sys.exit(main())
