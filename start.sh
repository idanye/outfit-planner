#!/bin/bash
# start.sh

# Change directory to the project root
cd "$(dirname "$0")"

echo "Current directory: $(pwd)"
python backend/run_analytics.py &
echo "Analytics backend script is running."
echo " "

# ## Wait for the server to start
sleep 3

# Run the FastAPI server in the background
echo ""
echo "Current directory: $(pwd)"
python backend/run_backend.py &
echo "Additional backend script is running."
echo " "


## Open the HTML file in the default browser
#python open_html.py
