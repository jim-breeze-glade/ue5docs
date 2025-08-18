#!/usr/bin/env python3
"""
Unreal Engine 5 Documentation Scraper

This script scrapes all documentation from the UE5 website and saves individual pages
as PDFs in a directory structure mirroring the sitemap.
"""

import os
import sys
import asyncio
import aiohttp
import time
import logging
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import xml.etree.ElementTree as ET
import re
import html
import unicodedata


class UE5DocsScraper:
    def __init__(self, base_url="https://docs.unrealengine.com", output_dir="ue5_docs"):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.scraped_urls = set()
        self.failed_urls = set()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup selenium driver
        self.setup_driver()

    def setup_driver(self):
        """Setup Selenium Firefox driver with options to avoid bot detection"""
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--no-sandbox")
        
        # Set user agent
        ua = UserAgent()
        firefox_options.set_preference("general.useragent.override", ua.random)
        
        # Disable automation indicators
        firefox_options.set_preference("dom.webdriver.enabled", False)
        firefox_options.set_preference("useAutomationExtension", False)
        
        self.driver = webdriver.Firefox(options=firefox_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def clean_filename(self, name, max_length=50):
        """Clean a string to be safe for use as a filename"""
        if not name or not name.strip():
            return "unnamed"
        
        # Normalize unicode and decode HTML entities
        name = unicodedata.normalize('NFKD', name)
        name = html.unescape(name)
        
        # Replace problematic characters
        forbidden_chars = '<>:"|?*\\/\r\n\t'
        for char in forbidden_chars:
            name = name.replace(char, '_')
        
        # Remove control characters (ASCII 0-31)
        name = ''.join(char for char in name if ord(char) >= 32)
        
        # Collapse multiple spaces/underscores
        name = re.sub(r'[_\s]+', '_', name)
        
        # Remove leading/trailing dots, spaces, underscores
        name = name.strip('._\t\n\r ')
        name = name.strip('._')
        
        # Handle Windows reserved names
        windows_reserved = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        
        if name.upper() in windows_reserved:
            name = f"_{name}"
        
        # Limit length
        if len(name) > max_length:
            name = name[:max_length]
        
        # Ensure we don't end with a dot (Windows issue)
        name = name.rstrip('.')
        
        # Final fallback
        return name if name else "unnamed"

    def clean_directory_name(self, name):
        """Clean a string to be safe for use as a directory name"""
        if not name or not name.strip():
            return "unnamed_dir"
        
        # Apply same cleaning as filename but allow longer names
        clean_name = self.clean_filename(name, max_length=100)
        
        # Remove trailing dots (Windows doesn't allow directories ending with dots)
        clean_name = clean_name.rstrip('.')
        
        return clean_name or "unnamed_dir"

    def get_sitemap_urls(self):
        """Extract URLs from sitemap or discover through navigation"""
        sitemap_urls = []
        
        # Try to get sitemap.xml first
        try:
            self.driver.get(f"{self.base_url}/sitemap.xml")
            time.sleep(2)
            
            page_source = self.driver.page_source
            if "403" not in page_source and "404" not in page_source:
                root = ET.fromstring(page_source)
                for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                    loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc_elem is not None:
                        sitemap_urls.append(loc_elem.text)
                        
            if sitemap_urls:
                self.logger.info(f"Found {len(sitemap_urls)} URLs in sitemap")
                return sitemap_urls
                
        except Exception as e:
            self.logger.warning(f"Could not parse sitemap: {e}")

        # Fallback: discover URLs through navigation
        return self.discover_urls_through_navigation()

    def discover_urls_through_navigation(self):
        """Discover documentation URLs by crawling the navigation structure"""
        discovered_urls = set()
        
        try:
            # Start from the main docs page
            self.driver.get(f"{self.base_url}/5.3/en-US/")
            time.sleep(3)
            
            # Look for navigation elements and links
            nav_selectors = [
                "nav a[href*='/5.3/en-US/']",
                ".navigation a[href*='/5.3/en-US/']", 
                ".sidebar a[href*='/5.3/en-US/']",
                ".toc a[href*='/5.3/en-US/']",
                "a[href*='/5.3/en-US/']"
            ]
            
            for selector in nav_selectors:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for link in links:
                        href = link.get_attribute('href')
                        if href and '/5.3/en-US/' in href:
                            discovered_urls.add(href)
                except Exception as e:
                    continue
                    
            self.logger.info(f"Discovered {len(discovered_urls)} URLs through navigation")
            return list(discovered_urls)
            
        except Exception as e:
            self.logger.error(f"Error discovering URLs: {e}")
            return []

    def create_directory_structure(self, url):
        """Create directory structure based on URL path with enhanced safety"""
        try:
            parsed_url = urlparse(url)
            path_parts = [part for part in parsed_url.path.split('/') if part]
            
            # Remove filename if it exists (has extension)
            if path_parts and '.' in path_parts[-1]:
                path_parts = path_parts[:-1]
            
            # Start from base directory
            current_path = self.output_dir
            
            for part in path_parts:
                # URL decode the part
                decoded_part = unquote(part)
                
                # Clean the directory name
                clean_part = self.clean_directory_name(decoded_part)
                
                # Prevent path traversal
                if '..' in clean_part or clean_part.startswith('.'):
                    clean_part = clean_part.replace('..', '_').lstrip('.')
                
                # Build path safely
                current_path = current_path / clean_part
                
                # Check for extremely long paths (Windows has 260 char limit)
                if len(str(current_path)) > 200:  # Leave some buffer
                    # Truncate the last part and break
                    truncated = clean_part[:50]
                    current_path = current_path.parent / truncated
                    break
            
            # Create the directory structure
            current_path.mkdir(parents=True, exist_ok=True)
            return current_path
            
        except Exception as e:
            self.logger.warning(f"Error creating directory for {url}: {e}")
            # Fallback to a safe default
            safe_path = self.output_dir / "unknown_structure"
            safe_path.mkdir(parents=True, exist_ok=True)
            return safe_path

    def get_page_title(self, soup, url=None):
        """Extract page title for filename with enhanced safety"""
        filename = "page"  # Default fallback
        
        try:
            # Try to extract title from various sources
            title_elem = (
                soup.find('title') or 
                soup.find('h1') or 
                soup.find('h2') or
                soup.find('meta', {'property': 'og:title'})
            )
            
            if title_elem:
                if title_elem.name == 'meta':
                    title = title_elem.get('content', '')
                else:
                    title = title_elem.get_text()
                
                if title and title.strip():
                    filename = self.clean_filename(title.strip(), max_length=50)
        
        except Exception:
            # If anything fails, use URL-based name
            if url:
                try:
                    parsed_url = urlparse(url)
                    path_parts = [part for part in parsed_url.path.split('/') if part]
                    if path_parts:
                        filename = self.clean_filename(path_parts[-1], max_length=50)
                except Exception:
                    pass
        
        return filename

    def scrape_page_content(self, url):
        """Scrape content from a single page"""
        try:
            self.driver.get(url)
            time.sleep(2)
            
            # Wait for content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Remove navigation and unnecessary elements
            for element in soup.find_all(['nav', 'header', 'footer', '.navigation', '.sidebar']):
                element.decompose()
                
            # Extract main content
            main_content = soup.find('main') or soup.find('.content') or soup.find('body')
            
            if not main_content:
                self.logger.warning(f"No main content found for {url}")
                return None
                
            return str(main_content), soup
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return None, None

    def save_as_pdf(self, html_content, output_path):
        """Convert HTML content to PDF using WeasyPrint with enhanced safety"""
        try:
            import weasyprint
            import shutil
            
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check available disk space (rough estimate)
            try:
                free_space = shutil.disk_usage(output_path.parent).free
                if free_space < 50 * 1024 * 1024:  # Less than 50MB
                    raise OSError("Insufficient disk space")
            except Exception:
                # If we can't check disk space, continue anyway
                pass
            
            # Create a full HTML document
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                    img {{ max-width: 100%; height: auto; }}
                    pre {{ background: #f5f5f5; padding: 10px; border-radius: 5px; }}
                    code {{ background: #f5f5f5; padding: 2px 4px; border-radius: 3px; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    @page {{ margin: 1in; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # Write to temporary file first, then rename (atomic operation)
            temp_path = output_path.with_suffix(output_path.suffix + '.tmp')
            
            try:
                # Use WeasyPrint to create PDF
                html_doc = weasyprint.HTML(string=full_html)
                html_doc.write_pdf(str(temp_path))
                
                # If successful, rename to final filename
                temp_path.rename(output_path)
                return True
                
            except Exception as e:
                # Clean up temp file if it exists
                if temp_path.exists():
                    temp_path.unlink()
                raise e
            
        except Exception as e:
            self.logger.error(f"Error creating PDF {output_path}: {e}")
            return False

    def scrape_all_docs(self):
        """Main method to scrape all documentation"""
        self.logger.info("Starting UE5 documentation scraping...")
        
        # Get all URLs to scrape
        urls = self.get_sitemap_urls()
        
        if not urls:
            self.logger.error("No URLs found to scrape")
            return
            
        total_urls = len(urls)
        self.logger.info(f"Found {total_urls} URLs to process")
        
        for i, url in enumerate(urls, 1):
            if url in self.scraped_urls:
                continue
                
            self.logger.info(f"Processing {i}/{total_urls}: {url}")
            
            try:
                # Scrape the page
                html_content, soup = self.scrape_page_content(url)
                
                if not html_content:
                    self.failed_urls.add(url)
                    continue
                
                # Create directory structure
                dir_path = self.create_directory_structure(url)
                
                # Generate filename
                title = self.get_page_title(soup, url)
                filename = f"{title}.pdf"
                
                # Handle duplicate filenames
                counter = 1
                original_filename = filename
                while (dir_path / filename).exists():
                    name_part = original_filename[:-4]  # Remove .pdf
                    filename = f"{name_part}_{counter}.pdf"
                    counter += 1
                
                output_path = dir_path / filename
                
                # Save as PDF
                if self.save_as_pdf(html_content, output_path):
                    self.logger.info(f"Saved: {output_path}")
                    self.scraped_urls.add(url)
                else:
                    self.failed_urls.add(url)
                    
                # Small delay to be respectful
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error processing {url}: {e}")
                self.failed_urls.add(url)
                
        self.logger.info(f"Scraping completed. Successfully scraped: {len(self.scraped_urls)}, Failed: {len(self.failed_urls)}")

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'driver'):
            self.driver.quit()


def main():
    """Main entry point"""
    scraper = UE5DocsScraper()
    
    try:
        scraper.scrape_all_docs()
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.driver.quit()


if __name__ == "__main__":
    main()