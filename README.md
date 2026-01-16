# The Sports Page

A newspaper-styled web application that displays sports scores, standings, statistics, and schedules. Designed to recreate the traditional sports page reading experience.

## Features

- **NHL Coverage**: Scores, standings, leaders, schedule, and box scores from the NHL API
- **NBA Coverage**: Scores, standings, leaders, and schedule via nba_api
- **EPL Coverage**: Premier League scores, table, and fixtures (requires API key)
- **Box Scores**: Traditional box scores with period-by-period scoring and top scorers
- **Newspaper Design**: Vintage typography with consistent design scale
- **Print-Friendly**: Optimized for printing on standard letter paper
- **Toggleable Leagues**: Show/hide leagues with persistent preferences

## Quick Start

### One-Click Start

```bash
./run.sh
```

This fetches fresh data and starts the server at http://localhost:8000

### Manual Setup

1. **Install Dependencies**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

2. **Fetch Data**

```bash
python backend/fetch_data.py
```

3. **Start Server**

```bash
cd frontend && python -m http.server 8000
```

4. Open http://localhost:8000

### Interactive Menu

```bash
./start.sh
```

Provides options to fetch data, test APIs, or start the server.

## Optional: EPL API Key

EPL data requires a free API key from [football-data.org](https://www.football-data.org/):

```bash
echo 'export FOOTBALL_DATA_API_KEY="your_key"' > .env
source .env
```

NHL and NBA work without any API keys.

## Project Structure

```
sports-page/
├── backend/
│   ├── apis/
│   │   ├── nhl.py          # NHL API (api-web.nhle.com)
│   │   ├── nba.py          # NBA API (nba_api library)
│   │   └── epl.py          # EPL API (football-data.org)
│   ├── fetch_data.py       # Main data fetcher
│   └── requirements.txt
├── frontend/
│   ├── css/
│   │   ├── base.css        # Variables and reset
│   │   ├── newspaper.css   # Layout and typography
│   │   ├── components.css  # UI components
│   │   └── print.css       # Print styles
│   ├── js/
│   │   ├── app.js          # Main application
│   │   ├── renderer.js     # DOM rendering
│   │   ├── storage.js      # Preferences
│   │   └── utils.js        # Utilities
│   ├── data/               # Generated JSON (gitignored)
│   └── index.html
├── docs/
│   └── design-spec.md      # Typography and design system
├── run.sh                  # One-click start
└── start.sh                # Interactive menu
```

## Design System

See [docs/design-spec.md](docs/design-spec.md) for the typography scale and component hierarchy.

| Level | Size | Use |
|-------|------|-----|
| 1 | 3rem | Masthead |
| 2 | 1.75rem | League headers (NHL, NBA) |
| 3 | 1.125rem | Section headers |
| 4 | 1rem | Conference/Category |
| 5 | 0.9rem | Scores, division headers |
| 6 | 0.85rem | Body text |
| 7 | 0.75rem | Secondary info |
| 8 | 0.7rem | Tertiary info |

## Data Sources

- **NHL**: [NHL API](https://api-web.nhle.com) (free, no key required)
- **NBA**: [nba_api](https://github.com/swar/nba_api) (free, no key required)
- **EPL**: [football-data.org](https://www.football-data.org/) (free tier, API key required)

## Usage

### Toggle Leagues
Use the checkboxes to show/hide leagues. Preferences are saved in localStorage.

### Box Scores
Check "Show Box Scores" to see period-by-period scoring, shots on goal, goalies, and top scorers.

### Print
Click "Print" or use Cmd/Ctrl+P. Optimized for letter paper (8.5" x 11").

## License

This project is for personal use. Not affiliated with NHL, NBA, EPL, or any sports league.

---

Built with Claude Code.
