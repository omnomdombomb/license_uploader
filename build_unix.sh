#!/bin/bash
# Build script for Linux/macOS - Creates standalone executable

set -e  # Exit on error

echo "===================================="
echo "License Uploader - Unix Build"
echo "===================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3 from your package manager or https://www.python.org/"
    exit 1
fi

echo "Python version: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Install PyInstaller
echo ""
echo "Installing PyInstaller..."
pip install pyinstaller

# Clean previous builds
echo ""
echo "Cleaning previous builds..."
rm -rf build dist

# Build executable
echo ""
echo "Building executable..."
echo "This may take several minutes..."
pyinstaller license_uploader.spec

# Copy .env.example if .env doesn't exist in dist
if [ ! -f "dist/license_uploader/.env" ]; then
    if [ -f ".env.example" ]; then
        echo ""
        echo "Copying .env.example to dist folder..."
        cp .env.example dist/license_uploader/.env.example
    fi
fi

# Create necessary directories in dist
echo ""
echo "Creating required directories..."
mkdir -p dist/license_uploader/logs
mkdir -p dist/license_uploader/uploads

# Make the executable... executable
chmod +x dist/license_uploader/license_uploader

echo ""
echo "===================================="
echo "Build completed successfully!"
echo "===================================="
echo ""
echo "The executable is located in: dist/license_uploader/"
echo ""
echo "Before running:"
echo "1. Copy .env.example to .env in the dist/license_uploader/ folder"
echo "2. Edit .env with your API keys and configuration"
echo "3. Run ./license_uploader"
echo ""
