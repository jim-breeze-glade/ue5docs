#!/bin/bash
# Setup script for Arch Linux

echo "Setting up UE5 Documentation Scraper on Arch Linux..."

# Install system dependencies using pacman
echo "Installing system dependencies..."
sudo pacman -S --needed wkhtmltopdf chromium python-virtualenv

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies in virtual environment
echo "Installing Python dependencies in virtual environment..."
pip install -r requirements.txt

echo ""
echo "Setup completed!"
echo ""
echo "To use the scraper:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the scraper: python ue5_docs_scraper.py"
echo "3. When done, deactivate: deactivate"