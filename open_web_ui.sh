#!/bin/bash
# Open the Swiggy Analyzer Web UI in browser

# Check if server is running
if ! lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Web server is not running!"
    echo ""
    echo "Starting server..."
    ./run_web.sh &
    sleep 3
fi

echo "🚀 Opening Swiggy Analyzer Web UI..."
echo ""
echo "URL: http://localhost:5000"
echo ""

# Open in default browser
if command -v open >/dev/null 2>&1; then
    # macOS
    open http://localhost:5000
elif command -v xdg-open >/dev/null 2>&1; then
    # Linux
    xdg-open http://localhost:5000
elif command -v start >/dev/null 2>&1; then
    # Windows
    start http://localhost:5000
else
    echo "Please manually open: http://localhost:5000"
fi

echo "✓ Browser opened!"
echo ""
echo "To stop the server, press Ctrl+C or run:"
echo "  lsof -ti:5000 | xargs kill -9"
