#!/bin/bash
# Run the Swiggy Analyzer Web UI

echo "Starting Swiggy Analyzer Web UI..."
echo ""
echo "The web interface will be available at:"
echo "http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Activate virtual environment and run Flask app
.venv/bin/python -m swiggy_analyzer.web.app
