#!/bin/bash
# License Uploader - Mac/Linux Launcher
# Double-click this file (or run: ./START_HERE.sh) to start the application

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "========================================"
echo "   📚 License Uploader"
echo "   Starting Application..."
echo "========================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -f "venv/bin/python" ]; then
    echo -e "${RED}ERROR: Virtual environment not found!${NC}"
    echo ""
    echo "Please run installation first:"
    echo "  1. Open Terminal"
    echo "  2. Navigate to this folder: cd \"$SCRIPT_DIR\""
    echo "  3. Run: python3 -m venv venv"
    echo "  4. Run: source venv/bin/activate"
    echo "  5. Run: pip install -r requirements.txt"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if GUI is available (X11/Wayland for Linux, always available on Mac)
if command -v python3 &> /dev/null; then
    if python3 -c "import tkinter" &> /dev/null 2>&1; then
        echo -e "${GREEN}✓ Starting GUI launcher...${NC}"
        venv/bin/python start_license_uploader_gui.py
    else
        echo -e "${YELLOW}⚠  GUI not available, using command-line launcher${NC}"
        venv/bin/python start_license_uploader.py
    fi
else
    echo -e "${RED}ERROR: Python 3 not found!${NC}"
    echo "Please install Python 3 and try again."
    read -p "Press Enter to exit..."
    exit 1
fi
