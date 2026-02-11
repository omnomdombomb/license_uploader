#!/bin/bash
# License Uploader - Unix/macOS Installation Script

echo "======================================"
echo "License Uploader Installation"
echo "======================================"
echo ""

# Find Python
echo "Step 1/6: Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ ERROR: Python not found"
    echo "Please install Python 3.11+ from https://www.python.org/"
    exit 1
fi

VERSION=$($PYTHON --version 2>&1)
echo "✓ Found: $VERSION"

# Check Python version
MAJOR=$($PYTHON -c 'import sys; print(sys.version_info.major)')
MINOR=$($PYTHON -c 'import sys; print(sys.version_info.minor)')

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 11 ]); then
    echo "❌ ERROR: Python 3.11+ required, found $VERSION"
    echo "Please upgrade Python from https://www.python.org/"
    exit 1
fi
echo "✓ Python version is compatible"
echo ""

# Create virtual environment
echo "Step 2/6: Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠  Virtual environment already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        $PYTHON -m venv venv
        echo "✓ Virtual environment recreated"
    else
        echo "✓ Using existing virtual environment"
    fi
else
    $PYTHON -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Step 3/6: Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Step 4/6: Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

# Install requirements
echo "Step 5/6: Installing dependencies..."
echo "(This may take a few minutes...)"
if pip install -r requirements.txt --quiet; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ ERROR: Failed to install dependencies"
    echo "Please check requirements.txt and try again"
    exit 1
fi
echo ""

# Create .env file
echo "Step 6/6: Setting up configuration..."
if [ -f .env ]; then
    echo "⚠  .env file already exists - skipping creation"
else
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✓ Created .env from template"
    else
        echo "⚠  .env.example not found, creating basic .env"
        cat > .env << 'ENVEOF'
# License Uploader Configuration
FLASK_SECRET_KEY=change-me-to-random-string
LITELLM_API_KEY=your-litellm-api-key-here
ALMA_API_KEY=your-alma-api-key-here
ALMA_API_BASE_URL=https://api-na.hosted.exlibrisgroup.com
FLASK_ENV=development
ENVEOF
        echo "✓ Created basic .env file"
    fi
fi
echo ""

# Create logs directory
mkdir -p logs

# Make START_HERE.sh executable
if [ -f START_HERE.sh ]; then
    chmod +x START_HERE.sh
    echo "✓ Made START_HERE.sh executable"
fi

echo ""
echo "======================================"
echo "Installation Complete! ✓"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys:"
echo "   nano .env  (or use your preferred editor)"
echo ""
echo "2. Run the application:"
echo "   ./START_HERE.sh"
echo ""
echo "For troubleshooting, see: docs/TROUBLESHOOTING_GUIDE.md"
echo ""
