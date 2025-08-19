#!/usr/bin/env python3
"""
Demonstration of enhanced cross-platform logging for UE5 Documentation Scraper.

This script demonstrates the enhanced logging capabilities without running
the full scraper, showing various error scenarios and logging features.
"""

import sys
import time
import platform
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_logger import CrossPlatformLogger


def demonstrate_logging():
    """Demonstrate the enhanced logging capabilities."""
    
    # Initialize the enhanced logger (same as used in the scraper)
    logger = CrossPlatformLogger(
        log_file="log.txt",
        log_level=20,  # INFO level
        enable_console=True,
        enable_json=False
    )
    
    # Log startup configuration like the scraper does
    startup_config = {
        'base_url': 'https://docs.unrealengine.com',
        'output_dir': 'ue5_docs',
        'platform': platform.system(),
        'python_version': platform.python_version(),
        'working_directory': str(Path.cwd())
    }
    logger.log_startup_summary(startup_config)
    
    # Simulate various scraper operations with logging
    print("\nDemonstrating various logging scenarios...\n")
    
    # 1. Successful operation
    logger.log_info("Starting sitemap retrieval from: https://docs.unrealengine.com/sitemap.xml")
    time.sleep(0.5)
    logger.log_success(
        "Successfully parsed sitemap with 1,247 URLs",
        url="https://docs.unrealengine.com/sitemap.xml"
    )
    logger.log_performance("sitemap_parsing", 2.3, {'url_count': 1247})
    
    # 2. Warning scenario
    logger.log_warning(
        "Access forbidden (403) when accessing sitemap",
        url="https://docs.unrealengine.com/sitemap.xml"
    )
    logger.log_info("Falling back to URL discovery through navigation")
    
    # 3. Network error simulation
    try:
        raise ConnectionError("Failed to establish a new connection: [Errno 111] Connection refused")
    except Exception as e:
        logger.log_error(
            "Error retrieving or parsing sitemap",
            exception=e,
            operation="get_sitemap_urls",
            url="https://docs.unrealengine.com/sitemap.xml"
        )
    
    # 4. Selenium/WebDriver error simulation
    try:
        raise Exception("WebDriver timeout: element not found after 10 seconds")
    except Exception as e:
        logger.log_error(
            "Timeout waiting for page body to load",
            exception=e,
            operation="scrape_page_content",
            url="https://docs.unrealengine.com/5.3/en-US/getting-started/"
        )
    
    # 5. Filesystem error simulation
    try:
        raise PermissionError("Permission denied when creating directory")
    except Exception as e:
        logger.log_error(
            "Permission denied when creating directory structure",
            exception=e,
            operation="create_directory_structure",
            url="https://docs.unrealengine.com/5.3/en-US/blueprints/",
            context={'platform': platform.system()}
        )
    
    # 6. PDF generation success
    logger.log_success(
        "Unix PDF generation completed successfully",
        file_path="/home/user/ue5_docs/5.3/en-US/blueprints/Getting_Started.pdf",
        file_size=245760
    )
    logger.log_performance("pdf_generation", 3.2, {'method': 'weasyprint'})
    
    # 7. HTML fallback scenario
    try:
        raise ImportError("No module named 'weasyprint'")
    except Exception as e:
        logger.log_error(
            "WeasyPrint not available for Unix PDF generation",
            exception=e,
            operation="_save_as_pdf_unix",
            context={'platform': platform.system()}
        )
    
    logger.log_info("Attempting HTML fallback after Unix PDF failure")
    logger.log_success(
        "HTML fallback generation completed successfully",
        file_path="/home/user/ue5_docs/5.3/en-US/blueprints/Getting_Started.html",
        file_size=89432
    )
    logger.log_performance("html_fallback", 0.8, {'content_length': 82540, 'fallback_reason': 'PDF generation failed'})
    
    # 8. Progress logging
    for i in range(1, 4):
        logger.log_info(f"Processing URL {i}/3: https://docs.unrealengine.com/5.3/en-US/example-page-{i}/")
        time.sleep(0.3)
        logger.log_success(
            f"Successfully processed URL {i}/3",
            url=f"https://docs.unrealengine.com/5.3/en-US/example-page-{i}/",
            file_path=f"/home/user/ue5_docs/5.3/en-US/example-page-{i}.pdf"
        )
        logger.log_performance(f"url_processing_{i}", 4.1 + i * 0.5, {
            'title': f'Example Page {i}',
            'directory': '/home/user/ue5_docs/5.3/en-US/'
        })
    
    # 9. Final completion summary
    logger.log_completion_summary(
        total_processed=3,
        successful=3,
        failed=0,
        duration=18.7
    )
    
    print(f"\nDemo completed! Check the log.txt file to see the detailed logs.")
    print(f"Log file location: {Path('log.txt').absolute()}")
    
    return logger


if __name__ == "__main__":
    print("Enhanced Cross-Platform Logging Demonstration")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print("=" * 50)
    
    logger = demonstrate_logging()
    
    # Show some stats from the log file
    log_file = Path("log.txt")
    if log_file.exists():
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        print(f"\nLog file statistics:")
        print(f"- Total lines written: {len(lines)}")
        print(f"- File size: {log_file.stat().st_size} bytes")
        print(f"- Location: {log_file.absolute()}")
        
        # Show first few lines and last few lines
        print(f"\nFirst 3 lines of log.txt:")
        for line in lines[:3]:
            print(f"  {line.strip()}")
        
        if len(lines) > 6:
            print(f"\n... ({len(lines) - 6} more lines) ...\n")
            print(f"Last 3 lines of log.txt:")
            for line in lines[-3:]:
                print(f"  {line.strip()}")
    
    print("\nDemo completed successfully!")