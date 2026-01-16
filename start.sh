#!/bin/bash
# The Sports Page - Quick Start Script

cd "$(dirname "$0")"

echo "=========================================="
echo "  THE SPORTS PAGE"
echo "=========================================="
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo "✓ Activating virtual environment..."
    source venv/bin/activate
    echo ""
else
    echo "✗ Virtual environment not found!"
    echo "  Run: python3 -m venv venv"
    exit 1
fi

# Check if EPL API key is set
if [ -z "$FOOTBALL_DATA_API_KEY" ]; then
    if [ -f ".env" ]; then
        echo "Loading .env file..."
        source .env
    else
        echo "ℹ️  EPL API key not set (optional)"
        echo "   Get free key: https://www.football-data.org/client/register"
        echo "   Then: echo 'export FOOTBALL_DATA_API_KEY=\"your_key\"' > .env"
    fi
fi
echo ""

# Show menu
echo "Available commands:"
echo ""
echo "  1) Fetch & Serve (one click!)"
echo "     Fetches data then starts server"
echo ""
echo "  2) Fetch live sports data only"
echo "     python backend/fetch_data.py"
echo ""
echo "  3) Test API connectivity"
echo "     python scripts/test_apis.py"
echo ""
echo "  4) Start web server only (http://localhost:8000)"
echo "     cd frontend && python -m http.server 8000"
echo ""
echo "  5) Exit"
echo ""
echo "=========================================="
echo ""

# Interactive menu
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "Fetching sports data..."
        python backend/fetch_data.py
        echo ""
        echo "Starting web server at http://localhost:8000"
        echo "Press Ctrl+C to stop"
        echo ""
        cd frontend && python -m http.server 8000
        ;;
    2)
        echo ""
        echo "Fetching sports data..."
        python backend/fetch_data.py
        ;;
    3)
        echo ""
        python scripts/test_apis.py
        ;;
    4)
        echo ""
        echo "Starting web server at http://localhost:8000"
        echo "Press Ctrl+C to stop"
        echo ""
        cd frontend && python -m http.server 8000
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        ;;
esac

# Keep shell active with venv
echo ""
echo "Virtual environment is still active."
echo "Type 'deactivate' to exit the venv, or continue working."
exec bash --init-file <(echo ". venv/bin/activate; cd $(pwd)")
