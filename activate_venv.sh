#!/bin/bash
# Simple script to activate the virtual environment

cd "$(dirname "$0")"

if [ -d "venv" ]; then
    echo "Activating virtual environment for The Sports Page..."
    source venv/bin/activate

    # Load .env if it exists
    if [ -f ".env" ]; then
        source .env
        echo "✓ Loaded environment variables from .env"
    fi

    echo "✓ Virtual environment activated!"
    echo ""
    echo "You can now run:"
    echo "  - python backend/fetch_data.py    # Fetch live data"
    echo "  - python scripts/test_apis.py     # Test API connectivity"
    echo "  - cd frontend && python -m http.server 8000  # Start web server"
    echo ""
    echo "Type 'deactivate' to exit the virtual environment"

    # Start a new shell with venv activated
    exec $SHELL
else
    echo "✗ Virtual environment not found at ./venv"
    echo "Run: python3 -m venv venv"
    exit 1
fi
