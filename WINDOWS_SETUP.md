# UE5 Documentation Scraper - Windows 11 Setup Guide

## Prerequisites
1. **Windows 10/11** - Windows 11 build 22000+ recommended
2. **Python 3.8+** - Download from [python.org](https://python.org)
   - ⚠️ **IMPORTANT**: During installation, check "Add Python to PATH"
3. **Firefox Browser** - Download from [firefox.com](https://firefox.com)
   - Alternative: Google Chrome (automatic fallback)

## Windows 11 Compatibility Check (Recommended First Step)
1. Download/clone this repository
2. Open Command Prompt **as Administrator** in the project directory
3. Run: `test_windows11_compatibility.bat`
4. Review the compatibility report and resolve any issues

## Quick Setup (After Compatibility Check)
1. Run: `setup_windows.bat`
2. The script will automatically:
   - Check Python and Firefox
   - Create virtual environment
   - Install Windows-compatible dependencies
   - Run tests
3. If setup fails, review the compatibility report

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

## Windows 11 Specific Features
- **Enhanced Error Handling**: Better detection and recovery from Windows permission issues
- **Smart Directory Creation**: Automatic fallback to Documents folder if permission denied
- **Antivirus Compatibility**: Built-in detection and workarounds for Windows Defender
- **Long Path Support**: Handles Windows path length limitations automatically
- **PDF Generation**: Uses Selenium browser printing (no complex dependencies)

## Troubleshooting

### Critical Issues

**"Firefox WebDriver failed"**
1. Ensure Firefox is installed from [firefox.com](https://firefox.com)
2. Run `test_windows11_compatibility.bat` for detailed diagnosis
3. Try running Command Prompt as Administrator
4. Check Windows Defender settings (add project folder to exclusions)

**"Permission denied when creating directory"**
1. Run Command Prompt as Administrator
2. The scraper will automatically try alternative locations
3. Check folder permissions in the chosen output directory

**"Python not recognized"**
1. Reinstall Python with "Add to PATH" option checked
2. Restart Command Prompt after Python installation
3. Verify installation: `python --version`

### Windows 11 Specific Issues

**"Connection refused" errors**
- Check Windows Firewall settings
- Temporarily disable real-time antivirus protection
- Ensure internet connection is stable

**"Timeout waiting for page body"**
- The scraper now uses longer timeouts on Windows 11
- Check system performance (close other applications)
- Try running during off-peak hours

**"WeasyPrint import error"**
✅ **Automatically handled!** The scraper detects Windows and uses browser-based PDF generation.

### Antivirus Interference
Modern antivirus software may interfere with:
- Virtual environment creation
- Firefox automation (flagged as suspicious)
- PDF file generation
- Network requests

**Solutions**:
1. Add the project folder to antivirus exclusions
2. Temporarily disable real-time protection during setup
3. Use Windows Defender instead of third-party antivirus (better compatibility)

## Advanced Troubleshooting

### Detailed Diagnostics
1. Run: `test_windows11_compatibility.bat` for comprehensive system check
2. Review generated report: `windows11_compatibility_report.txt`
3. Check logs: `scraper.log` and `setup.log`

### Manual Dependency Installation
If automatic setup fails:
```cmd
# Create virtual environment manually
python -m venv venv
venv\Scripts\activate.bat

# Install core dependencies
pip install requests beautifulsoup4 selenium fake-useragent psutil

# Test installation
python test_setup.py
```

### Alternative Browsers
If Firefox issues persist:
1. Install Google Chrome
2. The scraper can automatically fallback to Chrome
3. Update `setup_driver()` method if needed

### Network Issues
For corporate/restricted networks:
1. Configure proxy settings in the scraper
2. Use direct HTTP requests instead of browser automation
3. Run during off-peak hours to avoid rate limiting

## Performance Optimization

### For Windows 11
- **SSD Storage**: Use SSD for better I/O performance
- **Memory**: 8GB+ RAM recommended for large documentation sets
- **Antivirus**: Use Windows Defender (better performance than third-party)
- **Updates**: Keep Windows 11 updated (build 22621+ recommended)

### Resource Management
- Close unnecessary applications during scraping
- Monitor disk space (PDFs can be large)
- Use Task Manager to monitor resource usage

## Support
If you encounter issues:
1. **First**: Run `test_windows11_compatibility.bat`
2. **Second**: Check generated compatibility report
3. **Third**: Review logs: `scraper.log`, `setup.log`
4. **Fourth**: Try running as Administrator
5. **Fifth**: Check Windows Defender/antivirus settings

### Common Solutions
- 90% of Windows issues are resolved by running as Administrator
- 80% of remaining issues are antivirus-related
- Most network issues are firewall/proxy related

### Getting Help
When reporting issues, include:
- Windows version and build number
- Python version
- Firefox version
- Compatibility report output
- Full error messages from logs