#!/bin/bash
# License Uploader - Mac/Linux Launcher
# Double-click this file (or run: ./START_HERE.sh) to start the application
#
# This script is now a simple wrapper around the unified Python launcher

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Try to find Python
if [ -f "venv/bin/python" ]; then
    # Use virtual environment Python
    venv/bin/python launcher.py
elif command -v python3 &> /dev/null; then
    # Use system Python 3
    python3 launcher.py
elif command -v python &> /dev/null; then
    # Use system Python (might be Python 2, but launcher will handle it)
    python launcher.py
else
    echo "ERROR: Could not find Python!"
    echo "Please install Python or run the installer first."
    read -p "Press Enter to exit..."
    exit 1
fi
