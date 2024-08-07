#!/bin/bash
# start.sh

# Change directory to the project root
cd "$(dirname "$0")"

# Run the FastAPI server in the background
python backend/run_backend.py &

# Wait for the server to start
sleep 3

# Open the HTML file in the default browser
python open_html.py
