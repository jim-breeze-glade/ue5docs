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
- **Anti-Bot Handling**: Uses Selenium with Chrome to handle JavaScript and bot protection
- **Progress Tracking**: Detailed logging and progress reporting
- **Error Handling**: Robust error handling with retry mechanisms

## Installation

### Windows 11 Users
For Windows 11, use the dedicated setup files:
1. **Easy setup**: Double-click `setup_windows.bat`
2. **Detailed guide**: See `README_Windows.md`

### Linux/Mac Users
1. Run the setup script:
   ```bash
   # For Arch Linux
   ./setup_arch.sh
   
   # For other Linux distributions
   python setup.py
   ```

2. Or install manually:
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate
   
   # Install Python dependencies
   pip install -r requirements.txt
   ```

## Usage

### Windows 11
Double-click `run_scraper.bat` or:
```cmd
venv\Scripts\activate.bat
python ue5_docs_scraper.py
```

### Linux/Mac
```bash
source venv/bin/activate
python ue5_docs_scraper.py
```

The scraper will:
1. Discover all documentation URLs from the UE5 website
2. Create a mirrored directory structure in `ue5_docs/`
3. Save each page as a PDF with a descriptive filename
4. Log progress to both console and `scraper.log`

## Output Structure

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

## Configuration

You can modify the scraper behavior by editing `ue5_docs_scraper.py`:

- `base_url`: Change the base documentation URL
- `output_dir`: Change the output directory name
- `pdf_options`: Customize PDF generation settings

## Troubleshooting

- **403 Errors**: The site has bot protection. The scraper uses various techniques to avoid detection
- **Missing PDFs**: Check `scraper.log` for specific errors
- **Chrome Driver Issues**: The script automatically downloads the correct ChromeDriver version

## Legal Notice

This tool is for educational and personal use only. Please respect the Unreal Engine documentation's terms of service and use responsibly. Consider the server load and implement appropriate delays between requests.