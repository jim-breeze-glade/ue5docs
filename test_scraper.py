#!/usr/bin/env python3
"""
Test script to verify the UE5 scraper functionality with a limited run
"""

import sys
import time
from ue5_docs_scraper import UE5DocsScraper

def test_limited_scraping():
    """Test scraping with a few specific URLs"""
    
    # Create a test scraper
    scraper = UE5DocsScraper(output_dir="test_output")
    
    # Test URLs - these are common UE5 documentation pages
    test_urls = [
        "https://docs.unrealengine.com/5.3/en-US/",  # Main page
        "https://docs.unrealengine.com/5.3/en-US/understanding-the-basics-of-unreal-engine/",
    ]
    
    print(f"Testing scraper with {len(test_urls)} URLs...")
    
    success_count = 0
    
    for i, url in enumerate(test_urls, 1):
        print(f"\nTesting {i}/{len(test_urls)}: {url}")
        
        try:
            # Test scraping the page
            html_content, soup = scraper.scrape_page_content(url)
            
            if html_content and soup:
                print("  ✓ Content scraped successfully")
                
                # Test directory creation
                dir_path = scraper.create_directory_structure(url)
                print(f"  ✓ Directory created: {dir_path}")
                
                # Test PDF generation
                title = scraper.get_page_title(soup)
                pdf_path = dir_path / f"{title}.pdf"
                
                if scraper.save_as_pdf(html_content, pdf_path):
                    print(f"  ✓ PDF saved: {pdf_path}")
                    success_count += 1
                else:
                    print("  ✗ PDF generation failed")
            else:
                print("  ✗ Content scraping failed")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        # Small delay between requests
        time.sleep(2)
    
    # Cleanup
    scraper.driver.quit()
    
    print(f"\nTest completed: {success_count}/{len(test_urls)} URLs processed successfully")
    
    if success_count == len(test_urls):
        print("🎉 All test URLs processed successfully!")
        return True
    else:
        print("❌ Some test URLs failed")
        return False

def main():
    """Main test function"""
    print("Testing UE5 Documentation Scraper functionality...\n")
    
    if test_limited_scraping():
        print("\n✅ Scraper test successful! You can now run the full scraper.")
    else:
        print("\n❌ Scraper test failed. Please check the logs.")
        sys.exit(1)

if __name__ == "__main__":
    main()