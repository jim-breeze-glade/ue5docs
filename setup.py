#!/usr/bin/env python3
"""
Setup script for UE5 Documentation Scraper
"""

import subprocess
import sys
import os

def install_system_dependencies():
    """Install system dependencies for PDF generation"""
    print("Installing system dependencies...")
    
    # For wkhtmltopdf (required by pdfkit)
    dependencies = [
        "sudo apt-get update",
        "sudo apt-get install -y wkhtmltopdf",
        "sudo apt-get install -y xvfb",  # For headless PDF generation
    ]
    
    for cmd in dependencies:
        try:
            subprocess.run(cmd.split(), check=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install {cmd}: {e}")

def install_python_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Python dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing Python dependencies: {e}")
        return False
    return True

def create_directories():
    """Create necessary directories"""
    directories = ["ue5_docs", "logs"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def main():
    """Main setup function"""
    print("Setting up UE5 Documentation Scraper...")
    
    # Check if running on Linux (for apt-get commands)
    if sys.platform.startswith('linux'):
        install_system_dependencies()
    else:
        print("Note: Please install wkhtmltopdf manually on your system")
        print("Visit: https://wkhtmltopdf.org/downloads.html")
    
    # Install Python dependencies
    if not install_python_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    print("\nSetup completed!")
    print("You can now run the scraper with: python ue5_docs_scraper.py")

if __name__ == "__main__":
    main()