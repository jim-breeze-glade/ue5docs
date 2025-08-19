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
import platform
import datetime
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

# Import enhanced logging
from enhanced_logger import CrossPlatformLogger, error_handler


class UE5DocsScraper:
    def __init__(self, base_url="https://docs.unrealengine.com", output_dir="ue5_docs"):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.scraped_urls = set()
        self.failed_urls = set()
        self.start_time = datetime.datetime.now()
        
        # Setup enhanced cross-platform logging
        self.logger = CrossPlatformLogger(
            log_file="log.txt",
            log_level=logging.INFO,
            enable_console=True,
            enable_json=False
        )
        
        # Log startup configuration
        startup_config = {
            'base_url': base_url,
            'output_dir': str(output_dir),
            'platform': platform.system(),
            'python_version': platform.python_version(),
            'working_directory': str(Path.cwd())
        }
        self.logger.log_startup_summary(startup_config)
        
        # Setup selenium driver
        self.setup_driver()

    def setup_driver(self):
        """Setup Selenium Firefox driver with options to avoid bot detection"""
        try:
            self.logger.log_info("Setting up Selenium Firefox driver")
            
            firefox_options = Options()
            firefox_options.add_argument("--headless")
            firefox_options.add_argument("--no-sandbox")
            
            # Set user agent
            try:
                ua = UserAgent()
                user_agent = ua.random
                firefox_options.set_preference("general.useragent.override", user_agent)
                self.logger.log_info(f"Set user agent: {user_agent[:50]}...")
            except Exception as e:
                self.logger.log_warning("Could not set random user agent, using default", context={'error': str(e)})
            
            # Disable automation indicators
            firefox_options.set_preference("dom.webdriver.enabled", False)
            firefox_options.set_preference("useAutomationExtension", False)
            
            # Additional stability options for cross-platform compatibility
            firefox_options.add_argument("--disable-dev-shm-usage")
            firefox_options.add_argument("--disable-gpu")
            firefox_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Firefox(options=firefox_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.log_success("Selenium Firefox driver setup completed successfully")
            
        except Exception as e:
            self.logger.log_error(
                "Failed to setup Selenium Firefox driver",
                exception=e,
                operation="setup_driver",
                context={
                    'platform': platform.system(),
                    'firefox_available': 'firefox' in str(e).lower()
                }
            )
            raise

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
        sitemap_url = f"{self.base_url}/sitemap.xml"
        
        # Try to get sitemap.xml first
        try:
            self.logger.log_info(f"Attempting to retrieve sitemap from: {sitemap_url}")
            
            start_time = datetime.datetime.now()
            self.driver.get(sitemap_url)
            time.sleep(2)
            
            page_source = self.driver.page_source
            
            # Check for error pages
            if "403" in page_source:
                self.logger.log_warning("Access forbidden (403) when accessing sitemap", url=sitemap_url)
                return self.discover_urls_through_navigation()
            elif "404" in page_source:
                self.logger.log_warning("Sitemap not found (404)", url=sitemap_url)
                return self.discover_urls_through_navigation()
            
            # Parse XML
            try:
                root = ET.fromstring(page_source)
                for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                    loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc_elem is not None:
                        sitemap_urls.append(loc_elem.text)
                        
                if sitemap_urls:
                    duration = (datetime.datetime.now() - start_time).total_seconds()
                    self.logger.log_success(
                        f"Successfully parsed sitemap with {len(sitemap_urls)} URLs",
                        url=sitemap_url
                    )
                    self.logger.log_performance("sitemap_parsing", duration, {'url_count': len(sitemap_urls)})
                    return sitemap_urls
                else:
                    self.logger.log_warning("Sitemap found but no URLs extracted", url=sitemap_url)
                    
            except ET.ParseError as e:
                self.logger.log_error(
                    "XML parsing error in sitemap",
                    exception=e,
                    operation="sitemap_xml_parsing",
                    url=sitemap_url,
                    context={'page_source_length': len(page_source)}
                )
                
        except Exception as e:
            self.logger.log_error(
                "Error retrieving or parsing sitemap",
                exception=e,
                operation="get_sitemap_urls",
                url=sitemap_url
            )

        # Fallback: discover URLs through navigation
        self.logger.log_info("Falling back to URL discovery through navigation")
        return self.discover_urls_through_navigation()

    def discover_urls_through_navigation(self):
        """Discover documentation URLs by crawling the navigation structure"""
        discovered_urls = set()
        main_docs_url = f"{self.base_url}/5.3/en-US/"
        
        try:
            self.logger.log_info(f"Starting URL discovery through navigation from: {main_docs_url}")
            start_time = datetime.datetime.now()
            
            # Start from the main docs page
            self.driver.get(main_docs_url)
            time.sleep(3)
            
            # Look for navigation elements and links
            nav_selectors = [
                "nav a[href*='/5.3/en-US/']",
                ".navigation a[href*='/5.3/en-US/']", 
                ".sidebar a[href*='/5.3/en-US/']",
                ".toc a[href*='/5.3/en-US/']",
                "a[href*='/5.3/en-US/']"
            ]
            
            total_links_found = 0
            
            for i, selector in enumerate(nav_selectors):
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    links_found_for_selector = 0
                    
                    for link in links:
                        try:
                            href = link.get_attribute('href')
                            if href and '/5.3/en-US/' in href:
                                discovered_urls.add(href)
                                links_found_for_selector += 1
                                total_links_found += 1
                        except Exception as link_e:
                            # Log individual link extraction errors only at debug level
                            continue
                    
                    if links_found_for_selector > 0:
                        self.logger.log_info(f"Selector '{selector}' found {links_found_for_selector} valid links")
                        
                except Exception as e:
                    self.logger.log_warning(
                        f"Error processing navigation selector: {selector}",
                        context={'error': str(e), 'selector_index': i}
                    )
                    continue
            
            duration = (datetime.datetime.now() - start_time).total_seconds()
            
            if discovered_urls:
                self.logger.log_success(
                    f"URL discovery completed successfully",
                    context={
                        'discovered_count': len(discovered_urls),
                        'total_links_processed': total_links_found,
                        'selectors_used': len(nav_selectors)
                    }
                )
                self.logger.log_performance("url_discovery", duration, {'url_count': len(discovered_urls)})
            else:
                self.logger.log_warning("No URLs discovered through navigation", url=main_docs_url)
                
            return list(discovered_urls)
            
        except Exception as e:
            self.logger.log_error(
                "Critical error during URL discovery",
                exception=e,
                operation="discover_urls_through_navigation",
                url=main_docs_url
            )
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
            created_parts = []
            
            for part in path_parts:
                # URL decode the part
                try:
                    decoded_part = unquote(part)
                except Exception as decode_e:
                    self.logger.log_warning(f"URL decode error for part: {part}", context={'error': str(decode_e)})
                    decoded_part = part  # Use original if decode fails
                
                # Clean the directory name
                clean_part = self.clean_directory_name(decoded_part)
                
                # Prevent path traversal
                if '..' in clean_part or clean_part.startswith('.'):
                    original_part = clean_part
                    clean_part = clean_part.replace('..', '_').lstrip('.')
                    self.logger.log_warning(
                        f"Path traversal attempt detected and sanitized",
                        context={'original': original_part, 'sanitized': clean_part, 'url': url}
                    )
                
                # Build path safely
                current_path = current_path / clean_part
                created_parts.append(clean_part)
                
                # Check for extremely long paths (Windows has 260 char limit)
                if len(str(current_path)) > 200:  # Leave some buffer
                    # Truncate the last part and break
                    truncated = clean_part[:50]
                    current_path = current_path.parent / truncated
                    created_parts[-1] = truncated
                    
                    self.logger.log_warning(
                        f"Path length exceeded, truncated directory name",
                        context={
                            'original_length': len(str(current_path.parent / clean_part)),
                            'truncated_length': len(str(current_path)),
                            'url': url
                        }
                    )
                    break
            
            # Create the directory structure
            current_path.mkdir(parents=True, exist_ok=True)
            
            # Log successful directory creation
            if created_parts:
                self.logger.log_success(
                    f"Directory structure created",
                    context={
                        'path': str(current_path),
                        'depth': len(created_parts),
                        'parts': created_parts
                    }
                )
            
            return current_path
            
        except PermissionError as e:
            self.logger.log_error(
                f"Permission denied when creating directory structure",
                exception=e,
                operation="create_directory_structure",
                url=url,
                context={'platform': platform.system()}
            )
            # Fallback to a safe default
            safe_path = self.output_dir / "permission_denied_fallback"
            safe_path.mkdir(parents=True, exist_ok=True)
            return safe_path
            
        except OSError as e:
            self.logger.log_error(
                f"OS error when creating directory structure",
                exception=e,
                operation="create_directory_structure",
                url=url,
                context={'platform': platform.system(), 'output_dir': str(self.output_dir)}
            )
            # Fallback to a safe default
            safe_path = self.output_dir / "os_error_fallback"
            safe_path.mkdir(parents=True, exist_ok=True)
            return safe_path
            
        except Exception as e:
            self.logger.log_error(
                f"Unexpected error creating directory structure",
                exception=e,
                operation="create_directory_structure",
                url=url
            )
            # Fallback to a safe default
            safe_path = self.output_dir / "unknown_error_fallback"
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
        start_time = datetime.datetime.now()
        
        try:
            self.logger.log_info(f"Starting to scrape page content", context={'url': url})
            
            # Navigate to the page
            self.driver.get(url)
            time.sleep(2)
            
            # Wait for content to load with timeout handling
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as timeout_e:
                self.logger.log_error(
                    "Timeout waiting for page body to load",
                    exception=timeout_e,
                    operation="scrape_page_content",
                    url=url
                )
                return None, None
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            
            if not page_source or len(page_source) < 100:
                self.logger.log_warning(
                    "Page source is empty or too short",
                    url=url,
                    context={'page_source_length': len(page_source) if page_source else 0}
                )
                return None, None
            
            try:
                soup = BeautifulSoup(page_source, 'html.parser')
            except Exception as parse_e:
                self.logger.log_error(
                    "BeautifulSoup parsing error",
                    exception=parse_e,
                    operation="scrape_page_content",
                    url=url,
                    context={'page_source_length': len(page_source)}
                )
                return None, None
            
            # Remove navigation and unnecessary elements
            elements_removed = 0
            removal_selectors = ['nav', 'header', 'footer', '.navigation', '.sidebar']
            
            for selector in removal_selectors:
                elements = soup.find_all(selector)
                for element in elements:
                    element.decompose()
                    elements_removed += 1
                
            # Extract main content
            main_content = soup.find('main') or soup.find('.content') or soup.find('body')
            
            if not main_content:
                self.logger.log_warning(
                    "No main content found",
                    url=url,
                    context={
                        'elements_removed': elements_removed,
                        'available_tags': [tag.name for tag in soup.find_all()[:10]]  # First 10 tags
                    }
                )
                return None, None
            
            content_length = len(str(main_content))
            duration = (datetime.datetime.now() - start_time).total_seconds()
            
            self.logger.log_success(
                "Page content scraped successfully",
                url=url,
                context={
                    'content_length': content_length,
                    'elements_removed': elements_removed,
                    'duration_seconds': duration
                }
            )
            
            return str(main_content), soup
            
        except Exception as e:
            duration = (datetime.datetime.now() - start_time).total_seconds()
            self.logger.log_error(
                "Unexpected error during page scraping",
                exception=e,
                operation="scrape_page_content",
                url=url,
                context={'duration_seconds': duration}
            )
            return None, None

    def save_as_pdf(self, html_content, output_path):
        """Convert HTML content to PDF with cross-platform support"""
        current_platform = platform.system()
        
        try:
            self.logger.log_info(
                f"Starting PDF generation for {output_path.name}",
                context={
                    'platform': current_platform,
                    'output_path': str(output_path),
                    'content_length': len(html_content)
                }
            )
            
            # Try platform-specific method
            if current_platform == "Windows":
                return self._save_as_pdf_windows(html_content, output_path)
            else:
                return self._save_as_pdf_unix(html_content, output_path)
                
        except Exception as e:
            self.logger.log_error(
                "Critical error in PDF generation dispatcher",
                exception=e,
                operation="save_as_pdf",
                context={
                    'platform': current_platform,
                    'output_path': str(output_path)
                }
            )
            return self._save_as_html_fallback(html_content, output_path)
    
    def _save_as_pdf_windows(self, html_content, output_path):
        """Windows-compatible PDF generation using Selenium and browser printing"""
        start_time = datetime.datetime.now()
        
        try:
            import shutil
            
            self.logger.log_info(f"Starting Windows PDF generation for {output_path.name}")
            
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check available disk space (rough estimate)
            try:
                disk_usage = shutil.disk_usage(output_path.parent)
                free_space_mb = disk_usage.free / (1024 * 1024)
                
                if disk_usage.free < 50 * 1024 * 1024:  # Less than 50MB
                    self.logger.log_error(
                        "Insufficient disk space for PDF generation",
                        operation="_save_as_pdf_windows",
                        context={
                            'free_space_mb': free_space_mb,
                            'required_mb': 50,
                            'output_path': str(output_path)
                        }
                    )
                    raise OSError("Insufficient disk space")
                else:
                    self.logger.log_info(f"Disk space check passed: {free_space_mb:.1f}MB available")
                    
            except OSError as disk_e:
                self.logger.log_error(
                    "Disk space check failed",
                    exception=disk_e,
                    operation="_save_as_pdf_windows",
                    context={'output_path': str(output_path)}
                )
                raise
            except Exception as e:
                # If we can't check disk space, log warning and continue
                self.logger.log_warning(
                    "Could not check disk space, continuing anyway",
                    context={'error': str(e)}
                )
            
            # Create a full HTML document
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                    img {{ max-width: 100%; height: auto; }}
                    pre {{ background: #f5f5f5; padding: 10px; border-radius: 5px; overflow: auto; }}
                    code {{ background: #f5f5f5; padding: 2px 4px; border-radius: 3px; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    h1, h2, h3 {{ color: #333; }}
                    @media print {{
                        body {{ margin: 0; }}
                        * {{ -webkit-print-color-adjust: exact; }}
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # Write HTML to temporary file
            temp_html = output_path.with_suffix('.html')
            temp_path = output_path.with_suffix(output_path.suffix + '.tmp')
            
            try:
                # Write HTML file
                with open(temp_html, 'w', encoding='utf-8') as f:
                    f.write(full_html)
                
                # Use Selenium to print to PDF (works with Firefox on Windows)
                from selenium.webdriver.common.print_page_options import PrintOptions
                
                # Configure print options
                print_options = PrintOptions()
                print_options.page_ranges = ['1-']
                print_options.page_width = 8.27
                print_options.page_height = 11.69
                print_options.margin_top = 0.39
                print_options.margin_bottom = 0.39
                print_options.margin_left = 0.39
                print_options.margin_right = 0.39
                
                # Navigate to the HTML file and print to PDF
                self.driver.get(f"file:///{temp_html.absolute().as_posix()}")
                
                # Wait for page to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Print to PDF
                pdf_data = self.driver.print_page(print_options)
                
                # Save PDF data to file
                import base64
                with open(temp_path, 'wb') as f:
                    f.write(base64.b64decode(pdf_data))
                
                # If successful, rename to final filename
                temp_path.rename(output_path)
                
                # Clean up temp HTML file
                temp_html.unlink()
                
                duration = (datetime.datetime.now() - start_time).total_seconds()
                file_size = output_path.stat().st_size
                
                self.logger.log_success(
                    "Windows PDF generation completed successfully",
                    file_path=str(output_path),
                    file_size=file_size,
                    context={
                        'duration_seconds': duration,
                        'method': 'selenium_print'
                    }
                )
                
                return True
                
            except Exception as e:
                # Clean up temp files if they exist
                if temp_path.exists():
                    temp_path.unlink()
                if temp_html.exists():
                    temp_html.unlink()
                    
                self.logger.log_error(
                    "Error in Windows PDF generation process",
                    exception=e,
                    operation="_save_as_pdf_windows",
                    context={
                        'temp_html_path': str(temp_html),
                        'temp_pdf_path': str(temp_path),
                        'output_path': str(output_path)
                    }
                )
                raise e
            
        except Exception as e:
            duration = (datetime.datetime.now() - start_time).total_seconds()
            self.logger.log_error(
                "Critical error in Windows PDF generation",
                exception=e,
                operation="_save_as_pdf_windows",
                context={
                    'output_path': str(output_path),
                    'duration_seconds': duration,
                    'platform': 'Windows'
                }
            )
            # Fall back to saving as HTML
            self.logger.log_info("Attempting HTML fallback after Windows PDF failure")
            return self._save_as_html_fallback(html_content, output_path)
    
    def _save_as_pdf_unix(self, html_content, output_path):
        """Unix/Linux PDF generation using WeasyPrint"""
        start_time = datetime.datetime.now()
        
        try:
            self.logger.log_info(f"Starting Unix/Linux PDF generation for {output_path.name}")
            
            try:
                import weasyprint
            except ImportError as import_e:
                self.logger.log_error(
                    "WeasyPrint not available for Unix PDF generation",
                    exception=import_e,
                    operation="_save_as_pdf_unix",
                    context={'platform': platform.system()}
                )
                return self._save_as_html_fallback(html_content, output_path)
            
            import shutil
            
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check available disk space (rough estimate)
            try:
                disk_usage = shutil.disk_usage(output_path.parent)
                free_space_mb = disk_usage.free / (1024 * 1024)
                
                if disk_usage.free < 50 * 1024 * 1024:  # Less than 50MB
                    self.logger.log_error(
                        "Insufficient disk space for Unix PDF generation",
                        operation="_save_as_pdf_unix",
                        context={
                            'free_space_mb': free_space_mb,
                            'required_mb': 50,
                            'output_path': str(output_path)
                        }
                    )
                    raise OSError("Insufficient disk space")
                else:
                    self.logger.log_info(f"Disk space check passed: {free_space_mb:.1f}MB available")
                    
            except OSError as disk_e:
                self.logger.log_error(
                    "Disk space check failed",
                    exception=disk_e,
                    operation="_save_as_pdf_unix",
                    context={'output_path': str(output_path)}
                )
                raise
            except Exception as e:
                # If we can't check disk space, log warning and continue
                self.logger.log_warning(
                    "Could not check disk space, continuing anyway",
                    context={'error': str(e)}
                )
            
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
                self.logger.log_info("Creating PDF with WeasyPrint")
                html_doc = weasyprint.HTML(string=full_html)
                html_doc.write_pdf(str(temp_path))
                
                # If successful, rename to final filename
                temp_path.rename(output_path)
                
                duration = (datetime.datetime.now() - start_time).total_seconds()
                file_size = output_path.stat().st_size
                
                self.logger.log_success(
                    "Unix PDF generation completed successfully",
                    file_path=str(output_path),
                    file_size=file_size,
                    context={
                        'duration_seconds': duration,
                        'method': 'weasyprint'
                    }
                )
                
                return True
                
            except Exception as e:
                # Clean up temp file if it exists
                if temp_path.exists():
                    temp_path.unlink()
                    
                self.logger.log_error(
                    "Error in Unix PDF generation process",
                    exception=e,
                    operation="_save_as_pdf_unix",
                    context={
                        'temp_pdf_path': str(temp_path),
                        'output_path': str(output_path),
                        'weasyprint_available': True
                    }
                )
                raise e
            
        except Exception as e:
            duration = (datetime.datetime.now() - start_time).total_seconds()
            self.logger.log_error(
                "Critical error in Unix PDF generation",
                exception=e,
                operation="_save_as_pdf_unix",
                context={
                    'output_path': str(output_path),
                    'duration_seconds': duration,
                    'platform': platform.system()
                }
            )
            # Fall back to saving as HTML
            self.logger.log_info("Attempting HTML fallback after Unix PDF failure")
            return self._save_as_html_fallback(html_content, output_path)
    
    def _save_as_html_fallback(self, html_content, output_path):
        """Fallback method to save as HTML if PDF generation fails"""
        start_time = datetime.datetime.now()
        
        try:
            html_path = output_path.with_suffix('.html')
            
            self.logger.log_info(
                f"Starting HTML fallback generation for {html_path.name}",
                context={'original_pdf_path': str(output_path)}
            )
            
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>UE5 Documentation</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                    img {{ max-width: 100%; height: auto; }}
                    pre {{ background: #f5f5f5; padding: 10px; border-radius: 5px; overflow: auto; }}
                    code {{ background: #f5f5f5; padding: 2px 4px; border-radius: 3px; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    h1, h2, h3 {{ color: #333; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # Write HTML to temporary file first, then rename (atomic operation)
            temp_path = html_path.with_suffix(html_path.suffix + '.tmp')
            
            try:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(full_html)
                
                # If successful, rename to final filename
                temp_path.rename(html_path)
                
                duration = (datetime.datetime.now() - start_time).total_seconds()
                file_size = html_path.stat().st_size
                
                self.logger.log_success(
                    "HTML fallback generation completed successfully",
                    file_path=str(html_path),
                    file_size=file_size,
                    context={
                        'duration_seconds': duration,
                        'content_length': len(html_content),
                        'fallback_reason': 'PDF generation failed'
                    }
                )
                
                return True
                
            except Exception as write_e:
                # Clean up temp file if it exists
                if temp_path.exists():
                    temp_path.unlink()
                raise write_e
            
        except Exception as e:
            duration = (datetime.datetime.now() - start_time).total_seconds()
            self.logger.log_error(
                "Critical error in HTML fallback generation",
                exception=e,
                operation="_save_as_html_fallback",
                context={
                    'output_path': str(output_path),
                    'duration_seconds': duration
                }
            )
            return False

    def scrape_all_docs(self):
        """Main method to scrape all documentation"""
        scraping_start_time = datetime.datetime.now()
        
        self.logger.log_info("Starting UE5 documentation scraping session")
        
        try:
            # Get all URLs to scrape
            urls = self.get_sitemap_urls()
            
            if not urls:
                self.logger.log_error(
                    "No URLs found to scrape - stopping execution",
                    operation="scrape_all_docs",
                    context={'base_url': self.base_url}
                )
                return
                
            total_urls = len(urls)
            self.logger.log_info(f"Starting to process {total_urls} URLs")
            
            # Process each URL
            for i, url in enumerate(urls, 1):
                if url in self.scraped_urls:
                    self.logger.log_info(f"Skipping already processed URL ({i}/{total_urls}): {url}")
                    continue
                    
                url_start_time = datetime.datetime.now()
                self.logger.log_info(f"Processing URL {i}/{total_urls}: {url}")
                
                try:
                    # Scrape the page
                    html_content, soup = self.scrape_page_content(url)
                    
                    if not html_content:
                        self.logger.log_warning(f"No content retrieved for URL", url=url)
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
                        
                        if counter > 10:  # Prevent infinite loop
                            self.logger.log_warning(
                                f"Too many duplicate filenames, using timestamp",
                                context={'original_filename': original_filename, 'url': url}
                            )
                            timestamp = int(datetime.datetime.now().timestamp())
                            filename = f"{name_part}_{timestamp}.pdf"
                            break
                    
                    output_path = dir_path / filename
                    
                    # Save as PDF
                    if self.save_as_pdf(html_content, output_path):
                        url_duration = (datetime.datetime.now() - url_start_time).total_seconds()
                        self.scraped_urls.add(url)
                        
                        self.logger.log_success(
                            f"Successfully processed URL {i}/{total_urls}",
                            url=url,
                            file_path=str(output_path),
                            context={
                                'processing_time_seconds': url_duration,
                                'title': title,
                                'directory': str(dir_path)
                            }
                        )
                    else:
                        self.logger.log_error(
                            f"Failed to save content for URL {i}/{total_urls}",
                            operation="scrape_all_docs",
                            url=url,
                            context={'title': title, 'output_path': str(output_path)}
                        )
                        self.failed_urls.add(url)
                        
                    # Small delay to be respectful
                    time.sleep(1)
                    
                except KeyboardInterrupt:
                    self.logger.log_warning("Scraping interrupted by user")
                    raise
                    
                except Exception as e:
                    url_duration = (datetime.datetime.now() - url_start_time).total_seconds()
                    self.logger.log_error(
                        f"Unexpected error processing URL {i}/{total_urls}",
                        exception=e,
                        operation="scrape_all_docs",
                        url=url,
                        context={'processing_time_seconds': url_duration}
                    )
                    self.failed_urls.add(url)
            
            # Log completion summary
            total_duration = (datetime.datetime.now() - scraping_start_time).total_seconds()
            self.logger.log_completion_summary(
                total_processed=total_urls,
                successful=len(self.scraped_urls),
                failed=len(self.failed_urls),
                duration=total_duration
            )
            
        except Exception as e:
            total_duration = (datetime.datetime.now() - scraping_start_time).total_seconds()
            self.logger.log_error(
                "Critical error in main scraping process",
                exception=e,
                operation="scrape_all_docs",
                context={
                    'total_duration_seconds': total_duration,
                    'urls_processed': len(self.scraped_urls),
                    'urls_failed': len(self.failed_urls)
                }
            )
            raise

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
                if hasattr(self, 'logger'):
                    self.logger.log_info("Selenium driver cleaned up successfully")
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.log_warning(f"Error during driver cleanup: {e}")


def main():
    """Main entry point"""
    try:
        scraper = UE5DocsScraper()
        
        try:
            scraper.scrape_all_docs()
        except KeyboardInterrupt:
            scraper.logger.log_warning("Scraping interrupted by user (Ctrl+C)")
            print("\nScraping interrupted by user")
        except Exception as e:
            scraper.logger.log_error(
                "Critical error in main execution",
                exception=e,
                operation="main"
            )
            print(f"Error: {e}")
        finally:
            try:
                scraper.driver.quit()
                scraper.logger.log_info("Application shutdown completed")
            except Exception as cleanup_e:
                scraper.logger.log_warning(f"Error during cleanup: {cleanup_e}")
                
    except Exception as init_e:
        print(f"Failed to initialize scraper: {init_e}")
        # If we can't initialize the scraper, we can't use its logger
        # So we'll use basic logging for this case
        import logging
        logging.basicConfig(level=logging.ERROR)
        logging.error(f"Scraper initialization failed: {init_e}", exc_info=True)


if __name__ == "__main__":
    main()