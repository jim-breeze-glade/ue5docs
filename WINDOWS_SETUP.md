# UE5 Documentation Scraper - Windows Setup Guide

## Prerequisites
1. **Python 3.8+** - Download from [python.org](https://python.org)
   - ⚠️ **IMPORTANT**: During installation, check "Add Python to PATH"
2. **Firefox Browser** - Download from [firefox.com](https://firefox.com)

## Quick Setup (Recommended)
1. Download/clone this repository
2. Open Command Prompt in the project directory
3. Run: `setup_windows.bat`
4. The script will automatically:
   - Check Python and Firefox
   - Create virtual environment
   - Install Windows-compatible dependencies
   - Run tests

## Manual Setup
If the batch file doesn't work:

```cmd
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate.bat

# Install Windows dependencies
pip install -r requirements-windows.txt

# Test the installation
python test_setup.py
```

## Running the Scraper

### Using Batch File (Easy)
- Double-click: `run_scraper.bat`

### Manual Command
```cmd
# Activate environment
venv\Scripts\activate.bat

# Run scraper
python ue5_docs_scraper.py
```

## Windows-Specific Features
- **PDF Generation**: Uses Selenium browser printing (no WeasyPrint dependencies)
- **Fallback Mode**: Saves as HTML files if PDF generation fails
- **Cross-platform**: Same scraper works on Windows, Linux, and macOS

## Troubleshooting

### "WeasyPrint import error"
✅ **Fixed!** The scraper now detects Windows and uses browser-based PDF generation instead.

### "Firefox not found"
- Install Firefox from [firefox.com](https://firefox.com)
- Make sure it's in a standard location:
  - `C:\Program Files\Mozilla Firefox\firefox.exe`
  - `C:\Program Files (x86)\Mozilla Firefox\firefox.exe`

### "Python not recognized"
- Reinstall Python with "Add to PATH" option checked
- Or manually add Python to your PATH environment variable

### Antivirus Interference
Some antivirus software may interfere with:
- Virtual environment creation
- Firefox automation
- PDF file generation

**Solution**: Add the project folder to your antivirus exclusions.

## Support
If you encounter issues:
1. Check the `scraper.log` file for detailed error messages
2. Try running `test_windows.bat` to diagnose problems
3. Make sure both Python and Firefox are properly installed