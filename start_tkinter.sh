#!/bin/bash

# AI Security System - Tkinter Frontend Launcher

echo "🚀 Starting AI Security System (Tkinter)"
echo "=========================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if we're on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Start backend in new terminal
    osascript <<EOF
tell application "Terminal"
    do script "cd '$SCRIPT_DIR' && echo '🔌 Starting Backend Server...' && python3 backend.py"
    activate
end tell
EOF
    
    # Wait for backend to start
    echo "⏳ Waiting for backend server to start..."
    sleep 3
    
    # Start frontend
    echo "🎨 Starting Tkinter Frontend..."
    python3 frontend.py
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Try gnome-terminal
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "cd '$SCRIPT_DIR' && echo '🔌 Starting Backend Server...' && python3 backend.py; exec bash"
        sleep 3
        python3 frontend.py
    else
        echo "❌ Please run components manually:"
        echo "Terminal 1: python3 backend.py"
        echo "Terminal 2: python3 frontend.py"
        exit 1
    fi
else
    echo "❌ Unsupported OS. Please run manually:"
    echo "Terminal 1: python3 backend.py"
    echo "Terminal 2: python3 frontend.py"
    exit 1
fi

