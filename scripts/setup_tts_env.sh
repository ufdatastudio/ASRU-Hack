#!/bin/bash
# Setup separate virtual environment for Coqui TTS
# Adapted from Coqui TTS installation instructions for Linux

set -e

echo "=========================================="
echo "Setting up Coqui TTS Virtual Environment"
echo "=========================================="
echo ""

# Set base directory
BASE_DIR="/orange/ufdatastudios/c.okocha/ASRU-Hack"
TTS_DIR="$BASE_DIR/tts-env"
TTS_REPO_DIR="$TTS_DIR/TTS"

cd "$BASE_DIR"

echo "TTS environment will be created at: $TTS_DIR"
echo ""

# Check Python version (need 3.8, not 3.9+)
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "Current Python version: $PYTHON_VERSION"

if [ "$(printf '%s\n' "3.9" "$PYTHON_VERSION" | sort -V | head -n1)" = "3.9" ]; then
    echo "WARNING: Python 3.9+ detected. Coqui TTS requires Python 3.8."
    echo "You may need to install Python 3.8 separately."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create directory for TTS environment
echo ""
echo "Creating TTS environment directory..."
mkdir -p "$TTS_DIR"
cd "$TTS_DIR"

# Clone Coqui TTS repository
if [ ! -d "TTS" ]; then
    echo ""
    echo "Cloning Coqui TTS repository..."
    git clone https://github.com/coqui-ai/TTS.git
else
    echo "TTS repository already exists, skipping clone..."
fi

cd TTS

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "../venv" ]; then
    python3 -m venv ../venv
    echo "Virtual environment created at: $TTS_DIR/venv"
else
    echo "Virtual environment already exists, skipping..."
fi

# Activate virtual environment and install
echo ""
echo "Activating virtual environment and installing TTS..."
source ../venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install TTS in editable mode
echo ""
echo "Installing Coqui TTS in editable mode..."
pip install -e .

echo ""
echo "=========================================="
echo "TTS Environment Setup Complete!"
echo "=========================================="
echo ""
echo "To activate the TTS environment:"
echo "  source $TTS_DIR/venv/bin/activate"
echo ""
echo "To use TTS in your code, you can:"
echo "  1. Activate this environment before running"
echo "  2. Or modify your code to use this environment's Python"
echo ""

