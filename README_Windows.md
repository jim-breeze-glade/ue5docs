# UE5 Documentation Scraper - Windows 11 Setup

```
  ██╗   ██╗███████╗███████╗    ██████╗  ██████╗  ██████╗███████╗
  ██║   ██║██╔════╝██╔════╝    ██╔══██╗██╔═══██╗██╔════╝██╔════╝
  ██║   ██║█████╗  ███████╗    ██║  ██║██║   ██║██║     ███████╗
  ██║   ██║██╔══╝  ╚════██║    ██║  ██║██║   ██║██║     ╚════██║
  ╚██████╔╝███████╗███████║    ██████╔╝╚██████╔╝╚██████╗███████║
   ╚═════╝ ╚══════╝╚══════╝    ╚═════╝  ╚═════╝  ╚═════╝╚══════╝

                         DOCUMENTATION SCRAPER
```

A comprehensive tool to scrape all Unreal Engine 5 documentation and save it as PDFs with a directory structure mirroring the official website.

## 🚀 Quick Start (Automated Setup)

1. **Download** all files to a folder (e.g., `C:\UE5DocsScraper\`)
2. **Right-click** on `setup_windows.bat` → **"Run as administrator"**
3. **Wait** for setup to complete
4. **Double-click** `run_scraper.bat` to start scraping

## 📋 Prerequisites

### Required Software
- **Windows 11** (or Windows 10)
- **Python 3.8+** ([Download here](https://www.python.org/downloads/)) - Python 3.13+ recommended
- **Mozilla Firefox** ([Download here](https://www.mozilla.org/firefox/)) - Primary browser
- **Chrome/Edge** (Optional) - Alternative browser support
- **Internet connection**
- **2-4GB free disk space** for documentation storage

### Important Notes
- ⚠️ **Install Python with "Add Python to PATH" checked**
- ⚠️ **Firefox is recommended** - Chrome/Edge also supported with automatic driver setup
- ⚠️ **Administrator privileges** required for setup scripts
- ⚠️ **Enhanced logging** provides detailed operation monitoring
- ⚠️ **Automated scripts** handle most setup and execution tasks

## 🛠️ Manual Setup Instructions

If the automated `.bat` file doesn't work, follow these detailed steps:

### Step 1: Install Python
1. Go to [python.org](https://www.python.org/downloads/)
2. Download Python 3.8 or newer
3. **IMPORTANT**: During installation, check ✅ **"Add Python to PATH"**
4. Complete the installation

### Step 2: Install Firefox
1. Go to [mozilla.org/firefox](https://www.mozilla.org/firefox/)
2. Download and install Firefox
3. No special configuration needed

### Step 3: Verify Installations
Open **Command Prompt** (`cmd`) and run:
```cmd
python --version
```
You should see something like `Python 3.11.x`

### Step 4: Set Up the Project
1. **Download/extract** all scraper files to a folder
2. **Open Command Prompt** in that folder:
   - Hold `Shift` + Right-click in the folder
   - Select "Open PowerShell window here" or "Open command window here"

3. **Create virtual environment**:
   ```cmd
   python -m venv venv
   ```

4. **Activate virtual environment**:
   ```cmd
   venv\Scripts\activate.bat
   ```
   
   You should see `(venv)` appear at the start of your prompt

5. **Upgrade pip**:
   ```cmd
   python -m pip install --upgrade pip
   ```

6. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

### Step 5: Test the Installation
**Automated Testing**:
```cmd
test_windows.bat
```

**Manual Testing**:
```cmd
python test_enhanced_logging.py
python demo_logging.py
```

You should see:
- ✓ All Python modules imported successfully
- ✓ Enhanced logging system initialized
- ✓ Browser drivers setup successful (Firefox/Chrome)
- ✓ PDF generation test successful
- ✓ Cross-platform compatibility verified
- 🎉 All tests passed!

## 🎯 Running the Scraper

### Method 1: Batch File (Easiest)
Double-click `run_scraper.bat`

### Method 2: Command Line
1. Open Command Prompt in the project folder
2. Activate virtual environment:
   ```cmd
   venv\Scripts\activate.bat
   ```
3. Run the scraper:
   ```cmd
   python ue5_docs_scraper.py
   ```

## 📁 Output Structure

The scraper creates this structure:
```
project_root/
├── ue5_docs/                    # Generated documentation
│   └── 5.3/
│       └── en-US/
│           ├── getting-started/
│           │   ├── Installation_Guide.pdf
│           │   └── Quick_Start.pdf
│           ├── programming/
│           │   ├── Blueprints/
│           │   └── C++/
│           └── ...
├── log.txt                      # Enhanced logging output
├── scraper.log                  # Legacy log file
├── setup.log                    # Setup operation logs
├── test_results.log             # Test execution logs
├── SCRIPTS_README.md            # Script documentation
├── LOGGING_DOCUMENTATION.md     # Logging system docs
└── enhanced_logger.py           # Logging system core
```

## ⚙️ Configuration

Edit `ue5_docs_scraper.py` to customize:

```python
# Change output directory
scraper = UE5DocsScraper(output_dir="my_custom_folder")

# Change base URL (for different UE versions)
scraper = UE5DocsScraper(base_url="https://docs.unrealengine.com/5.4/en-US/")
```

## 🔧 Troubleshooting

### "Python is not recognized"
- Reinstall Python with "Add Python to PATH" checked
- Or manually add Python to your PATH environment variable

### "Browser driver setup failed"
- **Firefox**: Install from [mozilla.org/firefox](https://www.mozilla.org/firefox/)
- **Chrome**: Install from [google.com/chrome](https://www.google.com/chrome/)
- **Edge**: Usually pre-installed on Windows
- Restart Command Prompt after installation
- Check `setup.log` for detailed driver setup information

### "Permission denied" errors
- Run Command Prompt as Administrator
- Check antivirus isn't blocking the scraper

### "No module named X" errors
- Make sure virtual environment is activated: `venv\Scripts\activate.bat`
- Reinstall dependencies: `pip install -r requirements.txt`

### PDF generation fails
- Check `log.txt` for comprehensive error details and categorization
- Review `scraper.log` for legacy error information
- Ensure you have write permissions to the output directory
- Monitor system resources (memory, disk space) in enhanced logs
- Run diagnostic tests: `python test_enhanced_logging.py`

### Scraper gets blocked/403 errors
- The scraper includes enhanced anti-bot measures with intelligent delays
- **Enhanced logging** tracks network errors and categorizes blocking attempts
- Try running at different times or increase delays in configuration
- Check `log.txt` for detailed network error analysis
- Review system resource usage - high CPU/memory may trigger detection
- Check Epic Games' terms of service for scraping policies

## 📊 Performance Tips

- **Disk Space**: UE5 docs are large - ensure you have 2-4GB free (monitored in logs)
- **Time**: Complete scraping may take several hours (duration tracked in logs)
- **Memory**: Enhanced logging monitors RAM usage - close other applications if warned
- **CPU**: System monitors CPU utilization and adjusts operation accordingly
- **Network**: Stable internet connection recommended (network errors categorized in logs)
- **Monitoring**: Check `log.txt` for real-time performance metrics during operation

## 🚨 Important Warnings

- **Respect Rate Limits**: The scraper includes delays to be respectful
- **Terms of Service**: Ensure your use complies with Epic Games' ToS
- **Personal Use**: This tool is intended for personal documentation purposes
- **Network Usage**: Will consume significant bandwidth

## 📞 Support

If you encounter issues:

1. **Check enhanced logs**: Review `log.txt` for comprehensive error analysis and categorization
2. **Test setup**: Run `test_windows.bat` for complete system validation
3. **Review legacy logs**: Check `scraper.log` for historical error information
4. **Update dependencies**: Try `pip install --upgrade -r requirements.txt`
5. **System diagnostics**: Run `python test_enhanced_logging.py` for logging system tests
6. **Script documentation**: Consult `SCRIPTS_README.md` for detailed troubleshooting
7. **Performance monitoring**: Monitor system resources in real-time via enhanced logs
8. **Restart**: Sometimes a simple restart fixes driver and system issues

## 📜 Legal Notice

This tool is for educational and personal use only. Please respect Epic Games' documentation terms of service and use responsibly. The authors are not responsible for any misuse of this tool.

---

**Happy Scraping! 🎉**

For the latest updates and issues, check the project repository.