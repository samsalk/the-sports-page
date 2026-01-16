# The Sports Page

A daily-generated, newspaper-styled web application that displays sports scores, standings, statistics, and schedules. Designed to recreate the traditional sports page reading experience.

## Features

- **Daily Updates**: Automatically fetches fresh data at 3:00 AM ET
- **NHL Coverage**: Scores, standings, and schedules from the NHL Stats API
- **EPL Coverage**: Premier League scores, table, and fixtures from football-data.org
- **Newspaper Design**: Vintage newspaper aesthetic with print optimization
- **Customizable**: Toggle leagues and box score details
- **Print-Friendly**: Optimized for printing on standard letter paper

## Quick Start

### 1. Install Dependencies

```bash
cd sports-page
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 2. Set Up API Keys

Create a `.env` file in the project root:

```bash
# Get your free API key from https://www.football-data.org/
export FOOTBALL_DATA_API_KEY="your_api_key_here"
```

Source the environment file:

```bash
source .env  # On Windows: set commands from .env manually
```

### 3. Fetch Data

Run the data fetcher manually to test:

```bash
python backend/fetch_data.py
```

This will create `frontend/data/sports_data.json` with the latest data.

### 4. View the Page

Start a local web server:

```bash
cd frontend
python -m http.server 8000
```

Open your browser to: http://localhost:8000

## Setting Up Daily Updates

### Linux/Mac (cron)

Edit your crontab:

```bash
crontab -e
```

Add this line (adjust paths to match your installation):

```
0 3 * * * /path/to/sports-page/venv/bin/python /path/to/sports-page/backend/fetch_data.py >> /path/to/sports-page/logs/cron.log 2>&1
```

Or use the provided script:

```bash
chmod +x scripts/setup_cron.sh
./scripts/setup_cron.sh
```

### Windows (Task Scheduler)

Run PowerShell as Administrator:

```powershell
$action = New-ScheduledTaskAction -Execute "C:\path\to\venv\Scripts\python.exe" -Argument "C:\path\to\sports-page\backend\fetch_data.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 3:00AM
Register-ScheduledTask -TaskName "SportsPageUpdate" -Action $action -Trigger $trigger
```

## Project Structure

```
sports-page/
├── backend/              # Python data fetcher
│   ├── apis/            # League-specific API integrations
│   │   ├── nhl.py       # NHL Stats API
│   │   └── epl.py       # Football-data.org API
│   ├── fetch_data.py    # Main cron job script
│   ├── config.py        # Configuration
│   └── utils.py         # Utilities
├── frontend/            # Static web application
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript modules
│   ├── data/           # Generated JSON data
│   └── index.html      # Main page
├── logs/               # Log files
└── scripts/            # Setup utilities
```

## Data Sources

- **NHL**: [NHL Stats API](https://gitlab.com/dword4/nhlapi) (free, no key required)
- **EPL**: [football-data.org](https://www.football-data.org/) (free tier, API key required)

## Customization

### Toggle Leagues

Use the checkboxes at the top of the page to show/hide different leagues. Your preferences are saved in localStorage.

### Box Scores

Check "Show Box Scores" to see detailed period-by-period scoring and statistics.

### Print

Click the "Print" button or use your browser's print function (Cmd/Ctrl+P). The page is optimized for standard letter paper (8.5" x 11").

## Troubleshooting

### No data appearing

1. Check that `frontend/data/sports_data.json` exists
2. Run `python backend/fetch_data.py` manually to see any errors
3. Check `logs/fetch_data.log` for error messages

### EPL data not loading

1. Verify your API key is set: `echo $FOOTBALL_DATA_API_KEY`
2. Check your API quota at https://www.football-data.org/
3. Free tier allows 10 requests/minute, 100/day

### NHL data not loading

- The NHL Stats API is free and requires no key
- Check your internet connection
- Verify the API is accessible: `curl https://statsapi.web.nhl.com/api/v1/standings`

## Future Enhancements

- Add NBA, MLB, NFL support
- Player headshots and team logos
- Historical archive (last 30 days)
- Favorite teams highlighting
- Mobile app (PWA)

## License

This project is for personal use. Not affiliated with NHL, EPL, or any sports league.

## Credits

Built with data from:
- NHL Stats API
- football-data.org

Inspired by the traditional newspaper sports section.
