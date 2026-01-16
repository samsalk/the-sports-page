#!/bin/bash
# Setup cron job for daily data updates

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
FETCH_SCRIPT="$PROJECT_DIR/backend/fetch_data.py"
LOG_DIR="$PROJECT_DIR/logs"

# Create log directory
mkdir -p "$LOG_DIR"

# Check if virtual environment exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "Error: Virtual environment not found at $PYTHON_PATH"
    echo "Please run: python3 -m venv venv"
    exit 1
fi

# Check if fetch script exists
if [ ! -f "$FETCH_SCRIPT" ]; then
    echo "Error: Fetch script not found at $FETCH_SCRIPT"
    exit 1
fi

# Cron job line
CRON_JOB="0 3 * * * $PYTHON_PATH $FETCH_SCRIPT >> $LOG_DIR/cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$FETCH_SCRIPT"; then
    echo "Cron job already exists for this script."
    echo "Current crontab:"
    crontab -l | grep "$FETCH_SCRIPT"
    exit 0
fi

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✓ Cron job installed successfully!"
echo "The sports page will update daily at 3:00 AM ET"
echo "Logs will be written to: $LOG_DIR/cron.log"
echo ""
echo "To view your crontab: crontab -l"
echo "To remove this cron job: crontab -e (then delete the line)"
