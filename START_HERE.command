#!/bin/bash
# License Uploader - macOS Launcher
#
# IMPORTANT: This file uses the .command extension instead of .sh because
# macOS Finder only executes .command files on double-click. Double-clicking
# a .sh file opens it in a text editor (Xcode / TextEdit / Script Editor),
# which is the wrong behavior for end users.
#
# First time running on macOS:
#   - If Gatekeeper blocks the file, right-click -> Open -> Open (once).
#   - On stricter macOS versions you may need to remove the quarantine flag:
#       xattr -d com.apple.quarantine START_HERE.command

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [ -f "venv/bin/python" ]; then
    venv/bin/python launcher.py
elif command -v python3 &> /dev/null; then
    python3 launcher.py
elif command -v python &> /dev/null; then
    python launcher.py
else
    echo "ERROR: Could not find Python!"
    echo "Please install Python 3.11+ from https://www.python.org/ and run ./install.command first."
    read -p "Press Enter to exit..."
    exit 1
fi
