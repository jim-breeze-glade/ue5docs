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
- **Python 3.8+** ([Download here](https://www.python.org/downloads/))
- **Mozilla Firefox** ([Download here](https://www.mozilla.org/firefox/))
- **Internet connection**

### Important Notes
- ⚠️ **Install Python with "Add Python to PATH" checked**
- ⚠️ **Firefox is required** - Chrome/Edge won't work
- ⚠️ **Administrator privileges** may be needed for setup

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
```cmd
python test_setup.py
```

You should see:
- ✓ All Python modules imported successfully
- ✓ Firefox driver setup successful  
- ✓ PDF generation test successful
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
ue5_docs/
├── 5.3/
│   └── en-US/
│       ├── getting-started/
│       │   ├── Installation_Guide.pdf
│       │   └── Quick_Start.pdf
│       ├── programming/
│       │   ├── Blueprints/
│       │   └── C++/
│       └── ...
└── scraper.log
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

### "Firefox driver setup failed"
- Install Firefox from [mozilla.org/firefox](https://www.mozilla.org/firefox/)
- Restart Command Prompt after installation

### "Permission denied" errors
- Run Command Prompt as Administrator
- Check antivirus isn't blocking the scraper

### "No module named X" errors
- Make sure virtual environment is activated: `venv\Scripts\activate.bat`
- Reinstall dependencies: `pip install -r requirements.txt`

### PDF generation fails
- Check `scraper.log` for detailed error messages
- Ensure you have write permissions to the output directory

### Scraper gets blocked/403 errors
- The scraper includes anti-bot measures, but some pages may still block requests
- Try running at different times or with longer delays
- Check Epic Games' terms of service for scraping policies

## 📊 Performance Tips

- **Disk Space**: UE5 docs are large - ensure you have several GB free
- **Time**: Complete scraping may take several hours
- **Memory**: Close other applications if you experience slowdowns
- **Network**: Stable internet connection recommended

## 🚨 Important Warnings

- **Respect Rate Limits**: The scraper includes delays to be respectful
- **Terms of Service**: Ensure your use complies with Epic Games' ToS
- **Personal Use**: This tool is intended for personal documentation purposes
- **Network Usage**: Will consume significant bandwidth

## 📞 Support

If you encounter issues:

1. **Check the logs**: Look at `scraper.log` for detailed error messages
2. **Test setup**: Run `python test_setup.py` to verify installation
3. **Update dependencies**: Try `pip install --upgrade -r requirements.txt`
4. **Restart**: Sometimes a simple restart fixes driver issues

## 📜 Legal Notice

This tool is for educational and personal use only. Please respect Epic Games' documentation terms of service and use responsibly. The authors are not responsible for any misuse of this tool.

---

**Happy Scraping! 🎉**

For the latest updates and issues, check the project repository.