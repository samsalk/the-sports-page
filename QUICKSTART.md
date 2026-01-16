# Quick Start Guide - The Sports Page

## Getting Started in 5 Minutes

### 1. Navigate to the Project

```bash
cd /Users/samsalkin/Documents/projects/sports-page
```

### 2. Install Python Dependencies

The virtual environment is already created. Activate it and verify dependencies:

```bash
source venv/bin/activate
pip list | grep requests  # Should show installed packages
```

### 3. (Optional) Set Up EPL API Key

If you want live EPL data:

1. Get a free API key from https://www.football-data.org/client/register
2. Create a `.env` file:
   ```bash
   echo 'export FOOTBALL_DATA_API_KEY="your_key_here"' > .env
   source .env
   ```

### 4. Fetch Live Data (Optional)

To fetch real data from the APIs:

```bash
python backend/fetch_data.py
```

**Note**: This requires internet connectivity. If it fails, the application will use the sample data that's already included.

### 5. View the Sports Page

Start the web server:

```bash
cd frontend
python -m http.server 8000
```

Open your browser to: **http://localhost:8000**

## Features to Try

### Toggle Leagues
- Uncheck/check NHL and EPL to show/hide leagues
- Your preferences are saved automatically

### Show Box Scores
- Check "Show Box Scores" to see detailed game statistics
- Period-by-period scoring
- Goalie stats

### Print the Page
- Click the "Print" button or press Cmd+P (Mac) / Ctrl+P (Windows)
- The page is optimized for standard letter paper
- All box scores are automatically included in print view

## File Locations

- **Frontend**: `/Users/samsalkin/Documents/projects/sports-page/frontend/`
- **Data File**: `/Users/samsalkin/Documents/projects/sports-page/frontend/data/sports_data.json`
- **Python Backend**: `/Users/samsalkin/Documents/projects/sports-page/backend/`
- **Logs**: `/Users/samsalkin/Documents/projects/sports-page/logs/`

## Daily Updates

To set up automatic daily updates at 3:00 AM:

```bash
./scripts/setup_cron.sh
```

This will add a cron job that runs the data fetcher every day.

## Troubleshooting

### Web server already running?

If port 8000 is in use:

```bash
# Find and kill the process
lsof -ti:8000 | xargs kill

# Or use a different port
python -m http.server 8080
```

### No data showing?

1. Check that `frontend/data/sports_data.json` exists
2. Open browser console (F12) to see any JavaScript errors
3. Try refreshing the page (Cmd+R / Ctrl+R)

### API errors when fetching data?

- NHL API requires no key, but needs internet connection
- EPL API requires a free API key (100 requests/day limit)
- Both can be tested with: `python scripts/test_apis.py`

## Next Steps

1. **Customize the Design**: Edit CSS files in `frontend/css/`
2. **Add More Leagues**: Extend `backend/apis/` with NBA, MLB, or NFL modules
3. **Modify Layout**: Edit `frontend/index.html` and `frontend/js/renderer.js`

## Current Server Status

A web server is currently running at **http://localhost:8000**

You can view your Sports Page right now!
