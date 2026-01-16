#!/bin/bash
# One-click: Fetch data and start server

cd "$(dirname "$0")"

# Kill any existing server on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

echo "Fetching sports data..."
python3 backend/fetch_data.py

echo ""
echo "Starting server at http://localhost:8000"
echo "Press Ctrl+C to stop"
python3 -m http.server 8000
