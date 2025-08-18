# UE5 Documentation Scraper

A Python tool to scrape all documentation from the Unreal Engine 5 website and save individual pages as PDFs in a directory structure mirroring the sitemap.

## Features

- **Comprehensive Scraping**: Extracts all UE5 documentation pages
- **PDF Generation**: Converts each page to a well-formatted PDF
- **Directory Mirroring**: Creates a local directory structure matching the website
- **Anti-Bot Handling**: Uses Selenium with Chrome to handle JavaScript and bot protection
- **Progress Tracking**: Detailed logging and progress reporting
- **Error Handling**: Robust error handling with retry mechanisms

## Installation

1. Run the setup script:
   ```bash
   python setup.py
   ```

2. Or install manually:
   ```bash
   # Install system dependencies (Linux)
   sudo apt-get update
   sudo apt-get install -y wkhtmltopdf xvfb

   # Install Python dependencies
   pip install -r requirements.txt
   ```

## Usage

Run the scraper:
```bash
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