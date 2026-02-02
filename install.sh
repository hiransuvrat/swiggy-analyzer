#!/bin/bash
# Installation script for Swiggy Analyzer

set -e

echo "=========================================="
echo "Swiggy Analyzer Installation"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Install package
echo ""
echo "Installing swiggy-analyzer..."
pip install -e .

# Create directories
echo ""
echo "Creating directories..."
mkdir -p data logs

# Create default config
echo ""
echo "Creating default configuration..."
if [ ! -f config.yaml ]; then
    cp config.yaml config.yaml
    echo "✓ Configuration created at config.yaml"
else
    echo "Configuration already exists at config.yaml"
fi

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source .venv/bin/activate"
echo ""
echo "2. Authenticate with Swiggy:"
echo "   swiggy-analyzer auth login"
echo ""
echo "3. Sync your order history:"
echo "   swiggy-analyzer sync now"
echo ""
echo "4. Run analysis:"
echo "   swiggy-analyzer analyze run"
echo ""
echo "For more information, see README.md"
