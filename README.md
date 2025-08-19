# UE5 Documentation Scraper

```
  ██╗   ██╗███████╗███████╗    ██████╗  ██████╗  ██████╗███████╗
  ██║   ██║██╔════╝██╔════╝    ██╔══██╗██╔═══██╗██╔════╝██╔════╝
  ██║   ██║█████╗  ███████╗    ██║  ██║██║   ██║██║     ███████╗
  ██║   ██║██╔══╝  ╚════██║    ██║  ██║██║   ██║██║     ╚════██║
  ╚██████╔╝███████╗███████║    ██████╔╝╚██████╔╝╚██████╗███████║
   ╚═════╝ ╚══════╝╚══════╝    ╚═════╝  ╚═════╝  ╚═════╝╚══════╝

                         DOCUMENTATION SCRAPER
```

A Python tool to scrape all documentation from the Unreal Engine 5 website and save individual pages as PDFs in a directory structure mirroring the sitemap.

## Features

- **Comprehensive Scraping**: Extracts all UE5 documentation pages
- **PDF Generation**: Converts each page to a well-formatted PDF
- **Directory Mirroring**: Creates a local directory structure matching the website
- **Anti-Bot Handling**: Uses Selenium with Firefox to handle JavaScript and bot protection
- **Enhanced Logging**: Cross-platform detailed logging with error categorization and system monitoring
- **Progress Tracking**: Real-time progress reporting with performance metrics
- **Error Handling**: Robust error handling with retry mechanisms and intelligent error categorization
- **Cross-Platform Support**: Native support for Windows, macOS, and Linux
- **Automated Scripts**: Optimized batch and shell scripts for setup and execution
- **Performance Monitoring**: System resource tracking and operation duration monitoring

## Installation

### Prerequisites
- **Python 3.8+** (Python 3.13+ recommended)
- **Firefox Browser** (Chrome/Edge also supported)
- **Internet connection**
- **2-4GB free disk space** for documentation

### Windows Users
For Windows, use the automated setup:
1. **Quick setup**: Double-click `setup_windows.bat` (run as administrator)
2. **Run scraper**: Double-click `run_scraper.bat`
3. **Detailed guide**: See `README_Windows.md`

### Linux Users
1. **Automated setup** (Arch Linux):
   ```bash
   chmod +x setup_arch.sh
   ./setup_arch.sh
   ```

2. **Run scraper**:
   ```bash
   chmod +x run_scraper.sh
   ./run_scraper.sh
   ```

3. **Manual installation**:
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

## Usage

### Windows
**Automated** (Recommended):
```cmd
run_scraper.bat
```

**Manual**:
```cmd
venv\Scripts\activate.bat
python ue5_docs_scraper.py
```

### Linux/Mac
**Automated** (Recommended):
```bash
./run_scraper.sh
```

**Manual**:
```bash
source venv/bin/activate
python ue5_docs_scraper.py
```

The scraper will:
1. **Initialize** enhanced logging system with system information
2. **Discover** all documentation URLs from the UE5 website
3. **Create** a mirrored directory structure in `ue5_docs/`
4. **Convert** each page to a well-formatted PDF with descriptive filename
5. **Monitor** system resources and performance during operation
6. **Log** comprehensive progress to console and detailed logs to `log.txt`
7. **Generate** completion summary with statistics and performance metrics

## Output Structure

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
└── SCRIPTS_README.md            # Script documentation
```

## Configuration

You can modify the scraper behavior by editing `ue5_docs_scraper.py`:

- `base_url`: Change the base documentation URL (supports different UE versions)
- `output_dir`: Change the output directory name
- `pdf_options`: Customize PDF generation settings
- **Enhanced Logging**: Configure logging levels and output formats in `enhanced_logger.py`
- **Performance Settings**: Adjust delays, timeouts, and resource monitoring
- **Browser Settings**: Switch between Firefox, Chrome, or other supported browsers

### Logging Configuration
The enhanced logging system supports:
- **Multiple output formats**: Text and JSON structured logging
- **Log rotation**: Automatic log file management
- **Error categorization**: Network, filesystem, PDF, parsing, memory, and platform errors
- **Performance tracking**: Operation duration and system resource monitoring

## Troubleshooting

### Common Issues
- **403 Errors**: The site has bot protection. The scraper uses various techniques to avoid detection
- **Missing PDFs**: Check `log.txt` and `scraper.log` for detailed error information
- **Browser Driver Issues**: Scripts automatically handle driver setup for Firefox and Chrome
- **Permission Errors**: Run setup scripts as administrator on Windows
- **Memory Issues**: Monitor system resources in logs; close other applications if needed

### Logging and Diagnostics
- **Enhanced Logs**: Check `log.txt` for comprehensive error details and system information
- **Error Categories**: Logs automatically categorize errors (network, selenium, filesystem, etc.)
- **Performance Metrics**: Monitor operation duration and resource usage in logs
- **Test Scripts**: Run `test_windows.bat` (Windows) or `test_linux.sh` (Linux) to verify setup

### Script Documentation
For detailed script usage and troubleshooting, see `SCRIPTS_README.md`

## Testing

### Automated Testing
**Windows**:
```cmd
test_windows.bat
```

**Linux**:
```bash
chmod +x test_linux.sh
./test_linux.sh
```

### Manual Testing
```bash
# Test enhanced logging
python test_enhanced_logging.py

# Test basic functionality
python demo_logging.py
```

## Documentation

- **`README.md`**: Main project documentation (this file)
- **`README_Windows.md`**: Detailed Windows setup guide
- **`SCRIPTS_README.md`**: Comprehensive script documentation
- **`LOGGING_DOCUMENTATION.md`**: Enhanced logging system documentation

## Legal Notice

This tool is for educational and personal use only. Please respect Epic Games' Unreal Engine documentation terms of service and use responsibly. Consider server load and implement appropriate delays between requests. The enhanced logging system helps monitor and ensure respectful usage patterns.