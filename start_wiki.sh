#!/bin/bash
# Start Field Station Wiki Server in Chrome Browser

echo "🚀 Starting Field Station Wiki Server..."
echo ""

# Check if server is already running
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    echo "📖 Wiki server already running at http://localhost:8080"
    echo "🌐 Opening in browser..."
    
    # Try to open in specific browsers
    if command -v google-chrome &> /dev/null; then
        google-chrome http://localhost:8080 >/dev/null 2>&1 &
    elif command -v chromium-browser &> /dev/null; then
        chromium-browser http://localhost:8080 >/dev/null 2>&1 &
    elif command -v firefox &> /dev/null; then
        firefox http://localhost:8080 >/dev/null 2>&1 &
    else
        echo "💡 Manually open: http://localhost:8080"
    fi
else
    echo "🔥 Starting wiki server..."
    python3 simple_wiki_server.py
fi