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
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from fake_useragent import UserAgent
import xml.etree.ElementTree as ET
import re
import html
import unicodedata
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Import enhanced logging
from enhanced_logger import CrossPlatformLogger, error_handler

# Global variables for dependency management
_weasyprint_module = None
_weasyprint_checked = False

# Enhanced dependency checking
def check_system_dependencies():
    """Check system dependencies before starting scraper"""
    issues = []
    suggestions = []
    
    system = platform.system()
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append(f"Python {sys.version} is too old")
        suggestions.append("Upgrade to Python 3.8 or later")
    
    # Check required modules
    required_modules = ['requests', 'bs4', 'selenium', 'fake_useragent']
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            issues.append(f"Missing required module: {module}")
            suggestions.append(f"Install missing module: pip install {module}")
    
    # Platform-specific checks
    if system == "Windows":
        # Check for Firefox on Windows
        firefox_paths = [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
        ]
        
        firefox_found = any(os.path.exists(path) for path in firefox_paths)
        if not firefox_found:
            issues.append("Firefox not found in standard Windows locations")
            suggestions.append("Install Firefox from https://firefox.com")
    
    return issues, suggestions


class UE5DocsScraper:
    def __init__(self, base_url="https://docs.unrealengine.com", output_dir="ue5_docs"):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        
        # Enhanced output directory creation with Windows support
        try:
            self.output_dir.mkdir(exist_ok=True, parents=True)
        except PermissionError as pe:
            if platform.system() == "Windows":
                # Try alternative location on Windows
                alt_dir = Path.home() / "Documents" / "UE5_Docs_Output"
                print(f"Permission denied for {output_dir}, trying alternative location: {alt_dir}")
                try:
                    alt_dir.mkdir(exist_ok=True, parents=True)
                    self.output_dir = alt_dir
                except Exception:
                    raise PermissionError(
                        f"Cannot create output directory. Try running as Administrator or "
                        f"choose a different location. Original error: {pe}"
                    )
            else:
                raise pe
        
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
        """Setup Selenium Firefox driver with enhanced Windows 11 compatibility"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                self.logger.log_info(f"Setting up Selenium Firefox driver (attempt {attempt + 1}/{max_retries})")
                
                firefox_options = Options()
                firefox_options.add_argument("--headless")
                firefox_options.add_argument("--no-sandbox")
                
                # Windows 11 specific options
                if platform.system() == "Windows":
                    firefox_options.add_argument("--disable-blink-features=AutomationControlled")
                    firefox_options.add_argument("--disable-extensions")
                    firefox_options.add_argument("--disable-plugins")
                    firefox_options.add_argument("--disable-web-security")
                    firefox_options.add_argument("--allow-running-insecure-content")
                    firefox_options.add_argument("--ignore-certificate-errors")
                    
                    # Set Windows-specific paths if needed
                    firefox_options.set_preference("browser.download.folderList", 2)
                    firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
                    firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
                
                # Set user agent with retry mechanism
                try:
                    ua = UserAgent()
                    user_agent = ua.random
                    firefox_options.set_preference("general.useragent.override", user_agent)
                    self.logger.log_info(f"Set user agent: {user_agent[:50]}...")
                except Exception as e:
                    self.logger.log_warning("Could not set random user agent, using default", context={'error': str(e)})
                    # Fallback to a known working user agent
                    fallback_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
                    firefox_options.set_preference("general.useragent.override", fallback_ua)
                
                # Disable automation indicators
                firefox_options.set_preference("dom.webdriver.enabled", False)
                firefox_options.set_preference("useAutomationExtension", False)
                
                # Enhanced stability options for cross-platform compatibility
                firefox_options.add_argument("--disable-dev-shm-usage")
                firefox_options.add_argument("--disable-gpu")
                firefox_options.add_argument("--window-size=1920,1080")
                firefox_options.add_argument("--no-first-run")
                firefox_options.add_argument("--disable-default-apps")
                
                # Set longer timeouts for Windows 11
                firefox_options.set_preference("network.http.connection-timeout", 30)
                firefox_options.set_preference("network.http.response.timeout", 30)
                
                # Try to create the driver
                self.driver = webdriver.Firefox(options=firefox_options)
                
                # Set enhanced timeouts for Windows 11 compatibility
                base_timeout = 30
                if platform.system() == "Windows":
                    base_timeout = 45  # Longer timeouts for Windows
                
                # Set implicit wait for better element detection
                self.driver.implicitly_wait(15)
                
                # Set page load timeout
                self.driver.set_page_load_timeout(base_timeout)
                
                # Set script timeout
                self.driver.set_script_timeout(base_timeout)
                
                # Execute anti-detection script
                try:
                    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                except Exception as js_e:
                    self.logger.log_warning(f"Could not execute anti-detection script: {js_e}")
                
                # Test the driver with a simple navigation
                test_url = "data:text/html,<html><body><h1>Test</h1></body></html>"
                self.driver.get(test_url)
                
                self.logger.log_success("Selenium Firefox driver setup completed successfully")
                return  # Success, exit retry loop
                
            except WebDriverException as e:
                self.logger.log_error(
                    f"WebDriver setup failed on attempt {attempt + 1}",
                    exception=e,
                    operation="setup_driver",
                    context={
                        'platform': platform.system(),
                        'attempt': attempt + 1,
                        'max_retries': max_retries,
                        'error_type': type(e).__name__
                    }
                )
                
                if attempt < max_retries - 1:
                    self.logger.log_info(f"Retrying driver setup in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    # Final attempt failed, provide helpful error message
                    error_msg = "Failed to setup Selenium Firefox driver after all retry attempts"
                    if platform.system() == "Windows":
                        error_msg += "\n\nWindows 11 troubleshooting:\n"
                        error_msg += "1. Ensure Firefox is installed from firefox.com\n"
                        error_msg += "2. Try running as Administrator\n"
                        error_msg += "3. Check Windows Defender/antivirus settings\n"
                        error_msg += "4. Ensure geckodriver is in PATH or same directory"
                    raise Exception(error_msg)
                    
            except Exception as e:
                self.logger.log_error(
                    f"Unexpected error during driver setup on attempt {attempt + 1}",
                    exception=e,
                    operation="setup_driver",
                    context={
                        'platform': platform.system(),
                        'attempt': attempt + 1,
                        'max_retries': max_retries
                    }
                )
                
                if attempt == max_retries - 1:
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
        """Extract URLs from sitemap with enhanced error handling and retry mechanism"""
        sitemap_urls = []
        sitemap_url = f"{self.base_url}/sitemap.xml"
        
        # First, try direct HTTP request with retry mechanism
        try:
            self.logger.log_info(f"Attempting direct HTTP request to sitemap: {sitemap_url}")
            sitemap_urls = self._try_direct_sitemap_request(sitemap_url)
            if sitemap_urls:
                return sitemap_urls
        except Exception as e:
            self.logger.log_warning(f"Direct HTTP request failed: {e}")
        
        # Fallback to Selenium-based retrieval with retry
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                self.logger.log_info(f"Attempting Selenium sitemap retrieval (attempt {attempt + 1}/{max_retries}): {sitemap_url}")
                
                start_time = datetime.datetime.now()
                
                # Use enhanced page loading with timeout handling
                try:
                    self.driver.get(sitemap_url)
                    
                    # Wait for page to load with explicit timeout
                    WebDriverWait(self.driver, 15).until(
                        lambda driver: driver.execute_script("return document.readyState") == "complete"
                    )
                    
                except TimeoutException:
                    self.logger.log_warning(f"Page load timeout on attempt {attempt + 1}, trying to continue...")
                
                # Add delay for content to fully load
                time.sleep(3)
                
                page_source = self.driver.page_source
                
                # Enhanced error detection
                error_indicators = {
                    '403': 'Access forbidden',
                    '404': 'Sitemap not found', 
                    '500': 'Server error',
                    'Access Denied': 'Access denied',
                    'Forbidden': 'Forbidden access',
                    'Not Found': 'Resource not found'
                }
                
                detected_error = None
                for indicator, description in error_indicators.items():
                    if indicator in page_source:
                        detected_error = description
                        break
                
                if detected_error:
                    self.logger.log_warning(f"{detected_error} when accessing sitemap on attempt {attempt + 1}", url=sitemap_url)
                    if attempt == max_retries - 1:  # Last attempt
                        return self.discover_urls_through_navigation()
                    else:
                        # Wait before retry
                        self.logger.log_info(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 1.5  # Increase delay
                        continue
                
                # Try to parse XML content
                try:
                    # Clean the page source for XML parsing
                    xml_content = page_source
                    if '<?xml' not in xml_content:
                        # Try to extract XML from HTML
                        soup = BeautifulSoup(page_source, 'html.parser')
                        pre_tags = soup.find_all('pre')
                        for pre in pre_tags:
                            if '<?xml' in pre.get_text():
                                xml_content = pre.get_text()
                                break
                    
                    root = ET.fromstring(xml_content)
                    
                    # Extract URLs from sitemap
                    for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                        loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                        if loc_elem is not None and loc_elem.text:
                            sitemap_urls.append(loc_elem.text.strip())
                    
                    # Also check for sitemap index files
                    for sitemap_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                        loc_elem = sitemap_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                        if loc_elem is not None and loc_elem.text:
                            # Recursively process sub-sitemaps
                            sub_urls = self._process_sub_sitemap(loc_elem.text.strip())
                            sitemap_urls.extend(sub_urls)
                            
                    if sitemap_urls:
                        duration = (datetime.datetime.now() - start_time).total_seconds()
                        self.logger.log_success(
                            f"Successfully parsed sitemap with {len(sitemap_urls)} URLs",
                            url=sitemap_url
                        )
                        self.logger.log_performance("sitemap_parsing", duration, {'url_count': len(sitemap_urls)})
                        return sitemap_urls
                    else:
                        self.logger.log_warning(f"Sitemap found but no URLs extracted on attempt {attempt + 1}", url=sitemap_url)
                        
                except ET.ParseError as e:
                    self.logger.log_error(
                        f"XML parsing error in sitemap on attempt {attempt + 1}",
                        exception=e,
                        operation="sitemap_xml_parsing",
                        url=sitemap_url,
                        context={
                            'page_source_length': len(page_source),
                            'attempt': attempt + 1,
                            'contains_xml_declaration': '<?xml' in page_source
                        }
                    )
                
                # If we reach here on the last attempt, fall back to navigation
                if attempt == max_retries - 1:
                    break
                    
                # Wait before retry
                self.logger.log_info(f"Retrying sitemap access in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 1.5
                
            except Exception as e:
                self.logger.log_error(
                    f"Error retrieving sitemap on attempt {attempt + 1}",
                    exception=e,
                    operation="get_sitemap_urls",
                    url=sitemap_url,
                    context={'attempt': attempt + 1, 'max_retries': max_retries}
                )
                
                if attempt == max_retries - 1:
                    break
                    
                # Wait before retry
                time.sleep(retry_delay)
                retry_delay *= 1.5

        # Final fallback: discover URLs through navigation
        self.logger.log_info("All sitemap attempts failed, falling back to URL discovery through navigation")
        return self.discover_urls_through_navigation()
    
    def _try_direct_sitemap_request(self, sitemap_url):
        """Try to fetch sitemap directly with HTTP requests and retry logic"""
        sitemap_urls = []
        
        # Create session with retry strategy
        session = requests.Session()
        
        # Define retry strategy with exponential backoff
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'Accept': 'application/xml,text/xml,*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        try:
            response = session.get(sitemap_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse the XML content
            root = ET.fromstring(response.content)
            
            # Extract URLs
            for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None and loc_elem.text:
                    sitemap_urls.append(loc_elem.text.strip())
            
            # Check for sitemap index
            for sitemap_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                loc_elem = sitemap_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None and loc_elem.text:
                    sub_urls = self._process_sub_sitemap(loc_elem.text.strip())
                    sitemap_urls.extend(sub_urls)
            
            if sitemap_urls:
                self.logger.log_success(f"Direct HTTP request successful: {len(sitemap_urls)} URLs found")
                
        except requests.exceptions.RequestException as e:
            self.logger.log_warning(f"Direct HTTP request failed: {e}")
            raise
        except ET.ParseError as e:
            self.logger.log_warning(f"XML parsing failed in direct request: {e}")
            raise
        finally:
            session.close()
            
        return sitemap_urls
    
    def _process_sub_sitemap(self, sub_sitemap_url):
        """Process a sub-sitemap URL and extract its URLs"""
        sub_urls = []
        try:
            self.logger.log_info(f"Processing sub-sitemap: {sub_sitemap_url}")
            
            # Use the same direct request method for sub-sitemaps
            session = requests.Session()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
            }
            
            response = session.get(sub_sitemap_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None and loc_elem.text:
                    sub_urls.append(loc_elem.text.strip())
            
            self.logger.log_info(f"Sub-sitemap processed: {len(sub_urls)} URLs found")
            
        except Exception as e:
            self.logger.log_warning(f"Failed to process sub-sitemap {sub_sitemap_url}: {e}")
            
        return sub_urls

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
        """Create directory structure with enhanced Windows 11 permission handling"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                parsed_url = urlparse(url)
                path_parts = [part for part in parsed_url.path.split('/') if part]
                
                # Remove filename if it exists (has extension)
                if path_parts and '.' in path_parts[-1]:
                    path_parts = path_parts[:-1]
                
                # Start from base directory
                current_path = self.output_dir
                created_parts = []
                
                # Windows-specific path handling
                if platform.system() == "Windows":
                    # Ensure we're not hitting Windows path limitations
                    max_path_length = 200  # Conservative limit for Windows
                    max_part_length = 50   # Conservative limit for directory names
                else:
                    max_path_length = 240
                    max_part_length = 100
                
                for part in path_parts:
                    # URL decode the part
                    try:
                        decoded_part = unquote(part)
                    except Exception as decode_e:
                        self.logger.log_warning(f"URL decode error for part: {part}", context={'error': str(decode_e)})
                        decoded_part = part  # Use original if decode fails
                    
                    # Clean the directory name with platform-specific rules
                    clean_part = self._clean_directory_name_enhanced(decoded_part, max_part_length)
                    
                    # Prevent path traversal
                    if '..' in clean_part or clean_part.startswith('.'):
                        original_part = clean_part
                        clean_part = clean_part.replace('..', '_').lstrip('.')
                        self.logger.log_warning(
                            f"Path traversal attempt detected and sanitized",
                            context={'original': original_part, 'sanitized': clean_part, 'url': url}
                        )
                    
                    # Build path safely
                    proposed_path = current_path / clean_part
                    
                    # Check for path length limits
                    if len(str(proposed_path)) > max_path_length:
                        # Implement intelligent truncation
                        remaining_length = max_path_length - len(str(current_path)) - 1  # -1 for separator
                        if remaining_length > 10:  # Minimum meaningful length
                            truncated = clean_part[:remaining_length]
                            # Ensure truncated name doesn't end with dot (Windows issue)
                            truncated = truncated.rstrip('.')
                            if not truncated:  # If truncation results in empty string
                                truncated = "dir"
                            proposed_path = current_path / truncated
                            created_parts.append(truncated)
                            
                            self.logger.log_warning(
                                f"Path length exceeded, truncated directory name",
                                context={
                                    'original': clean_part,
                                    'truncated': truncated,
                                    'original_length': len(str(current_path / clean_part)),
                                    'truncated_length': len(str(proposed_path)),
                                    'url': url
                                }
                            )
                        else:
                            # Path is too long, stop here
                            self.logger.log_warning(
                                f"Path too long, stopping directory creation at current level",
                                context={'current_path': str(current_path), 'url': url}
                            )
                            break
                    else:
                        created_parts.append(clean_part)
                    
                    current_path = proposed_path
                
                # Create the directory structure with enhanced error handling
                self._create_directory_with_windows_handling(current_path, attempt)
                
                # Log successful directory creation
                if created_parts:
                    self.logger.log_success(
                        f"Directory structure created",
                        context={
                            'path': str(current_path),
                            'depth': len(created_parts),
                            'parts': created_parts,
                            'attempt': attempt + 1 if attempt > 0 else None
                        }
                    )
                
                return current_path
                
            except PermissionError as e:
                self.logger.log_error(
                    f"Permission denied when creating directory structure (attempt {attempt + 1})",
                    exception=e,
                    operation="create_directory_structure",
                    url=url,
                    context={
                        'platform': platform.system(),
                        'attempt': attempt + 1,
                        'current_user': os.getenv('USERNAME' if platform.system() == 'Windows' else 'USER'),
                        'output_dir': str(self.output_dir)
                    }
                )
                
                if attempt < max_retries - 1:
                    # Try Windows-specific permission fixes
                    if platform.system() == "Windows":
                        self._try_windows_permission_fixes()
                    
                    self.logger.log_info(f"Retrying directory creation in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    # Final attempt failed, use alternative strategies
                    return self._create_fallback_directory(url, "permission_denied")
                    
            except OSError as e:
                error_context = {
                    'platform': platform.system(),
                    'output_dir': str(self.output_dir),
                    'attempt': attempt + 1,
                    'error_code': getattr(e, 'errno', None),
                    'error_message': str(e)
                }
                
                # Check for specific Windows errors
                if platform.system() == "Windows":
                    if "The filename, directory name, or volume label syntax is invalid" in str(e):
                        error_context['likely_cause'] = 'Invalid characters in path'
                    elif "The system cannot find the path specified" in str(e):
                        error_context['likely_cause'] = 'Parent directory missing'
                    elif "Access is denied" in str(e):
                        error_context['likely_cause'] = 'Access denied (try running as Administrator)'
                
                self.logger.log_error(
                    f"OS error when creating directory structure (attempt {attempt + 1})",
                    exception=e,
                    operation="create_directory_structure",
                    url=url,
                    context=error_context
                )
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    return self._create_fallback_directory(url, "os_error")
                    
            except Exception as e:
                self.logger.log_error(
                    f"Unexpected error creating directory structure (attempt {attempt + 1})",
                    exception=e,
                    operation="create_directory_structure",
                    url=url,
                    context={'attempt': attempt + 1, 'max_retries': max_retries}
                )
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    return self._create_fallback_directory(url, "unknown_error")
        
        # This should never be reached, but just in case
        return self._create_fallback_directory(url, "max_retries_exceeded")
    
    def _clean_directory_name_enhanced(self, name, max_length):
        """Enhanced directory name cleaning with platform-specific rules"""
        if not name or not name.strip():
            return "unnamed_dir"
        
        # Apply the existing cleaning logic
        clean_name = self.clean_directory_name(name)
        
        # Additional Windows-specific cleaning
        if platform.system() == "Windows":
            # Windows doesn't allow certain characters in paths
            additional_forbidden = ['<', '>', ':', '"', '|', '?', '*']
            for char in additional_forbidden:
                clean_name = clean_name.replace(char, '_')
            
            # Windows doesn't allow paths ending with space or dot
            clean_name = clean_name.rstrip(' .')
            
            # Windows reserved device names (case insensitive)
            windows_reserved = {
                'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5',
                'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4',
                'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
            }
            
            if clean_name.upper() in windows_reserved:
                clean_name = f"_{clean_name}"
        
        # Limit length
        if len(clean_name) > max_length:
            clean_name = clean_name[:max_length].rstrip(' .')
        
        return clean_name or "dir"
    
    def _create_directory_with_windows_handling(self, path, attempt):
        """Create directory with Windows-specific handling"""
        if platform.system() == "Windows" and attempt > 0:
            # On Windows, sometimes we need to ensure parent directories exist first
            parent = path.parent
            if not parent.exists():
                try:
                    parent.mkdir(parents=True, exist_ok=True)
                    # Small delay to let Windows file system catch up
                    time.sleep(0.1)
                except Exception as parent_e:
                    self.logger.log_warning(f"Could not create parent directory: {parent_e}")
        
        # Create the actual directory
        path.mkdir(parents=True, exist_ok=True)
        
        # Verify creation on Windows (sometimes mkdir silently fails)
        if platform.system() == "Windows":
            if not path.exists():
                raise OSError(f"Directory creation appeared to succeed but directory does not exist: {path}")
    
    def _try_windows_permission_fixes(self):
        """Try to fix Windows permission issues"""
        try:
            # Check if output directory is writable
            test_file = self.output_dir / "test_write_permissions.tmp"
            with open(test_file, 'w') as f:
                f.write("test")
            test_file.unlink()  # Clean up
            
            self.logger.log_info("Write permissions confirmed for output directory")
            
        except Exception as e:
            self.logger.log_warning(
                f"Permission test failed. Try running as Administrator or choose a different output directory.",
                context={'error': str(e), 'output_dir': str(self.output_dir)}
            )
    
    def _create_fallback_directory(self, url, error_type):
        """Create a fallback directory when normal creation fails"""
        try:
            # Create a safe fallback path
            import hashlib
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            fallback_name = f"{error_type}_fallback_{url_hash}"
            
            safe_path = self.output_dir / fallback_name
            safe_path.mkdir(parents=True, exist_ok=True)
            
            self.logger.log_warning(
                f"Created fallback directory due to {error_type}",
                context={
                    'fallback_path': str(safe_path),
                    'original_url': url,
                    'error_type': error_type
                }
            )
            
            return safe_path
            
        except Exception as fallback_e:
            # If even the fallback fails, use the base output directory
            self.logger.log_error(
                f"Fallback directory creation failed, using base output directory",
                exception=fallback_e,
                operation="_create_fallback_directory",
                context={'error_type': error_type, 'url': url}
            )
            
            # Ensure base output directory exists
            try:
                self.output_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass  # If this fails, we're in trouble
                
            return self.output_dir

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
        """Scrape content from a single page with enhanced timeout handling"""
        start_time = datetime.datetime.now()
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                self.logger.log_info(
                    f"Starting to scrape page content (attempt {attempt + 1}/{max_retries})", 
                    context={'url': url}
                )
                
                # Navigate to the page with enhanced error handling
                try:
                    self.driver.get(url)
                except TimeoutException as nav_timeout:
                    self.logger.log_warning(
                        f"Navigation timeout on attempt {attempt + 1}",
                        context={'url': url, 'timeout': self.driver.timeouts.page_load}
                    )
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise
                
                # Progressive wait strategy for content loading
                self._wait_for_page_content(url, attempt)
                
                # Additional wait for dynamic content
                time.sleep(2 + attempt)  # Increase wait time with each retry
            
                # Get page source with validation
                page_source = self.driver.page_source
                
                # Enhanced page source validation
                if not self._validate_page_source(page_source, url, attempt):
                    if attempt < max_retries - 1:
                        self.logger.log_info(f"Retrying page scraping in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 1.5
                        continue
                    else:
                        return None, None
            
                # Parse with BeautifulSoup
                try:
                    soup = BeautifulSoup(page_source, 'html.parser')
                except Exception as parse_e:
                    self.logger.log_error(
                        f"BeautifulSoup parsing error on attempt {attempt + 1}",
                        exception=parse_e,
                        operation="scrape_page_content",
                        url=url,
                        context={
                            'page_source_length': len(page_source),
                            'attempt': attempt + 1,
                            'contains_html': '<html' in page_source.lower()
                        }
                    )
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    else:
                        return None, None
            
                # Remove navigation and unnecessary elements
                elements_removed = self._clean_page_content(soup)
                    
                # Extract main content with enhanced detection
                main_content = self._extract_main_content(soup, url)
                
                if not main_content:
                    if attempt < max_retries - 1:
                        self.logger.log_warning(
                            f"No main content found on attempt {attempt + 1}, retrying...",
                            url=url
                        )
                        time.sleep(retry_delay)
                        continue
                    else:
                        self.logger.log_warning(
                            "No main content found after all attempts",
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
                        'duration_seconds': duration,
                        'attempt': attempt + 1 if attempt > 0 else None
                    }
                )
                
                return str(main_content), soup
            
            except Exception as e:
                self.logger.log_error(
                    f"Unexpected error during page scraping (attempt {attempt + 1})",
                    exception=e,
                    operation="scrape_page_content",
                    url=url,
                    context={
                        'attempt': attempt + 1,
                        'max_retries': max_retries,
                        'error_type': type(e).__name__
                    }
                )
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    duration = (datetime.datetime.now() - start_time).total_seconds()
                    self.logger.log_error(
                        "All page scraping attempts failed",
                        operation="scrape_page_content",
                        url=url,
                        context={'duration_seconds': duration, 'total_attempts': max_retries}
                    )
                    return None, None
        
        # Should never reach here
        return None, None
    
    def _wait_for_page_content(self, url, attempt):
        """Enhanced page content waiting with progressive timeouts"""
        base_timeout = 15
        timeout = base_timeout + (attempt * 5)  # Increase timeout with each retry
        
        try:
            # Wait for basic page structure
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait for page to be fully loaded
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Additional checks for content-specific elements
            content_selectors = [
                "main", ".content", ".main-content", "article", 
                ".documentation", ".docs", "#content", ".page-content"
            ]
            
            content_found = False
            for selector in content_selectors:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    content_found = True
                    self.logger.log_info(f"Content found using selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not content_found:
                self.logger.log_warning(
                    f"No specific content selectors found, proceeding with body content",
                    context={'url': url, 'attempt': attempt + 1}
                )
            
        except TimeoutException as timeout_e:
            self.logger.log_error(
                f"Timeout waiting for page content (attempt {attempt + 1})",
                exception=timeout_e,
                operation="_wait_for_page_content",
                url=url,
                context={
                    'timeout_seconds': timeout,
                    'attempt': attempt + 1,
                    'page_title': self.driver.title if hasattr(self.driver, 'title') else 'Unknown'
                }
            )
            raise
        except WebDriverException as web_e:
            self.logger.log_error(
                f"WebDriver error during content wait (attempt {attempt + 1})",
                exception=web_e,
                operation="_wait_for_page_content",
                url=url,
                context={'attempt': attempt + 1}
            )
            raise
    
    def _validate_page_source(self, page_source, url, attempt):
        """Validate page source quality and content"""
        if not page_source:
            self.logger.log_warning(
                f"Page source is empty (attempt {attempt + 1})",
                url=url
            )
            return False
        
        if len(page_source) < 100:
            self.logger.log_warning(
                f"Page source is too short (attempt {attempt + 1})",
                url=url,
                context={'page_source_length': len(page_source)}
            )
            return False
        
        # Check for error pages
        error_indicators = [
            "Access Denied", "403 Forbidden", "404 Not Found", "500 Internal Server Error",
            "Service Unavailable", "Bad Gateway", "Gateway Timeout",
            "This page can't be displayed", "Page not found",
            "<title>Just a moment...</title>"  # Cloudflare protection
        ]
        
        for indicator in error_indicators:
            if indicator in page_source:
                self.logger.log_warning(
                    f"Error page detected: {indicator} (attempt {attempt + 1})",
                    url=url
                )
                return False
        
        # Check for actual content
        content_indicators = [
            "<main", "<article", "class=\"content\"", "class=\"documentation\"",
            "<h1", "<h2", "<p", "<div"
        ]
        
        content_found = any(indicator in page_source for indicator in content_indicators)
        if not content_found:
            self.logger.log_warning(
                f"No content indicators found in page source (attempt {attempt + 1})",
                url=url
            )
            return False
        
        return True
    
    def _clean_page_content(self, soup):
        """Remove navigation and unnecessary elements"""
        elements_removed = 0
        
        # Extended list of elements to remove
        removal_selectors = [
            'nav', 'header', 'footer', '.navigation', '.sidebar', '.nav',
            '.header', '.footer', '.menu', '.breadcrumb', '.breadcrumbs',
            '.social-share', '.comments', '.related-posts', '.ads',
            '.advertisement', '.banner', '.popup', '.modal',
            'script', 'style', 'noscript'
        ]
        
        for selector in removal_selectors:
            elements = soup.find_all(selector)
            for element in elements:
                element.decompose()
                elements_removed += 1
        
        return elements_removed
    
    def _extract_main_content(self, soup, url):
        """Extract main content with enhanced detection"""
        # Try multiple selectors in order of preference
        content_selectors = [
            'main',
            '.main-content',
            '.content',
            '#content',
            '.documentation',
            '.docs',
            '.page-content',
            'article',
            '.entry-content',
            '.post-content',
            '[role="main"]',
            'body'  # Fallback
        ]
        
        for selector in content_selectors:
            try:
                content = soup.select_one(selector)
                if content and len(content.get_text(strip=True)) > 50:
                    self.logger.log_info(
                        f"Main content extracted using selector: {selector}",
                        context={'content_length': len(str(content))}
                    )
                    return content
            except Exception as e:
                self.logger.log_warning(
                    f"Error with selector {selector}: {e}",
                    context={'url': url}
                )
                continue
        
        # If no good content found, log available structure
        self.logger.log_warning(
            "Could not find main content with any selector",
            context={
                'url': url,
                'available_ids': [tag.get('id') for tag in soup.find_all(id=True)][:10],
                'available_classes': [cls for tag in soup.find_all(class_=True) for cls in tag.get('class')][:20]
            }
        )
        
        return None

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
        """Unix/Linux PDF generation using WeasyPrint with enhanced dependency management"""
        start_time = datetime.datetime.now()
        
        try:
            self.logger.log_info(f"Starting Unix/Linux PDF generation for {output_path.name}")
            
            # Try to import WeasyPrint with enhanced error handling
            weasyprint = self._import_weasyprint_with_fallbacks()
            if not weasyprint:
                self.logger.log_warning(
                    "WeasyPrint not available, falling back to HTML generation",
                    context={
                        'platform': platform.system(),
                        'suggestion': 'Install WeasyPrint: pip install weasyprint'
                    }
                )
                return self._save_as_html_fallback(html_content, output_path)
            
            import shutil
            
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check for WeasyPrint dependencies on Unix/Linux
            if not self._check_weasyprint_dependencies():
                self.logger.log_warning(
                    "WeasyPrint dependencies missing, falling back to HTML",
                    context={
                        'platform': platform.system(),
                        'suggestion': 'Install system dependencies for WeasyPrint'
                    }
                )
                return self._save_as_html_fallback(html_content, output_path)
            
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

    def _import_weasyprint_with_fallbacks(self):
        """Import WeasyPrint with enhanced error handling and suggestions"""
        global _weasyprint_module, _weasyprint_checked
        
        if _weasyprint_checked:
            return _weasyprint_module
        
        _weasyprint_checked = True
        
        try:
            import weasyprint
            _weasyprint_module = weasyprint
            
            # Test WeasyPrint functionality
            test_html = "<html><body>Test</body></html>"
            test_doc = weasyprint.HTML(string=test_html)
            
            self.logger.log_success("WeasyPrint imported and tested successfully")
            return weasyprint
            
        except ImportError as e:
            self.logger.log_warning(
                f"WeasyPrint import failed: {e}",
                context={
                    'platform': platform.system(),
                    'suggestions': self._get_weasyprint_install_suggestions()
                }
            )
            _weasyprint_module = None
            return None
            
        except Exception as e:
            self.logger.log_warning(
                f"WeasyPrint test failed: {e}",
                context={
                    'platform': platform.system(),
                    'error_type': type(e).__name__,
                    'suggestions': self._get_weasyprint_troubleshooting_suggestions()
                }
            )
            _weasyprint_module = None
            return None
    
    def _get_weasyprint_install_suggestions(self):
        """Get platform-specific WeasyPrint installation suggestions"""
        system = platform.system()
        
        suggestions = {
            'common': 'pip install weasyprint',
        }
        
        if system == "Linux":
            suggestions.update({
                'ubuntu_debian': 'sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0',
                'fedora_centos': 'sudo dnf install python3-cffi python3-brotli pango harfbuzz',
                'arch': 'sudo pacman -S python-cffi python-brotli pango harfbuzz'
            })
        elif system == "Darwin":  # macOS
            suggestions.update({
                'brew': 'brew install pango harfbuzz',
                'port': 'sudo port install pango +universal harfbuzz +universal'
            })
        elif system == "Windows":
            suggestions.update({
                'note': 'WeasyPrint on Windows requires GTK+ libraries',
                'alternative': 'Use Selenium-based PDF generation (automatic fallback)',
                'manual_install': 'Download GTK+ from https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer'
            })
        
        return suggestions
    
    def _get_weasyprint_troubleshooting_suggestions(self):
        """Get WeasyPrint troubleshooting suggestions"""
        return {
            'missing_fonts': 'Install system fonts: sudo apt-get install fonts-liberation (Linux)',
            'cairo_issues': 'Install cairo development libraries',
            'dll_errors': 'Check GTK+ installation on Windows',
            'permission_errors': 'Try running with administrator privileges'
        }
    
    def _check_weasyprint_dependencies(self):
        """Check if WeasyPrint dependencies are available"""
        try:
            # Test if we can create a simple PDF
            import weasyprint
            test_html = "<html><body><p>Dependency test</p></body></html>"
            doc = weasyprint.HTML(string=test_html)
            
            # Try to render to bytes (this will fail if dependencies are missing)
            pdf_bytes = doc.write_pdf()
            
            if len(pdf_bytes) > 0:
                self.logger.log_info("WeasyPrint dependencies check passed")
                return True
            else:
                self.logger.log_warning("WeasyPrint produced empty PDF")
                return False
                
        except Exception as e:
            self.logger.log_warning(
                f"WeasyPrint dependency check failed: {e}",
                context={
                    'error_type': type(e).__name__,
                    'platform': platform.system()
                }
            )
            return False
    
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
    """Main entry point with Windows 11 compatibility checking"""
    
    # Run Windows 11 compatibility check if on Windows
    if platform.system() == "Windows":
        print("Running Windows 11 compatibility check...")
        try:
            # Import and run the compatibility checker
            issues, suggestions = check_system_dependencies()
            
            if issues:
                print("\n⚠️  COMPATIBILITY ISSUES DETECTED:")
                for i, issue in enumerate(issues, 1):
                    print(f"  {i}. {issue}")
                
                if suggestions:
                    print("\n💡 SUGGESTIONS:")
                    for i, suggestion in enumerate(suggestions, 1):
                        print(f"  {i}. {suggestion}")
                
                print("\nFor detailed compatibility analysis, run: python windows11_compatibility.py")
                
                # Ask user if they want to continue
                try:
                    response = input("\nDo you want to continue despite these issues? (y/N): ")
                    if response.lower() not in ['y', 'yes']:
                        print("Exiting. Please resolve the issues and try again.")
                        sys.exit(1)
                except KeyboardInterrupt:
                    print("\nExiting.")
                    sys.exit(1)
            else:
                print("✅ System compatibility check passed!")
                
        except Exception as check_e:
            print(f"⚠️  Could not run compatibility check: {check_e}")
            print("Continuing with scraper initialization...")
    
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
            
            # Provide Windows-specific troubleshooting hints
            if platform.system() == "Windows":
                print("\nWindows troubleshooting tips:")
                print("1. Try running as Administrator")
                print("2. Check Windows Defender/antivirus settings")
                print("3. Run: python windows11_compatibility.py for detailed analysis")
                print("4. Ensure Firefox is properly installed")
                
        finally:
            try:
                scraper.driver.quit()
                scraper.logger.log_info("Application shutdown completed")
            except Exception as cleanup_e:
                scraper.logger.log_warning(f"Error during cleanup: {cleanup_e}")
                
    except Exception as init_e:
        print(f"Failed to initialize scraper: {init_e}")
        
        # Provide specific guidance for initialization failures
        if platform.system() == "Windows":
            print("\nWindows initialization troubleshooting:")
            print("1. Run: python windows11_compatibility.py")
            print("2. Ensure Firefox is installed and accessible")
            print("3. Try running as Administrator")
            print("4. Check if any antivirus is blocking the application")
        
        # If we can't initialize the scraper, we can't use its logger
        # So we'll use basic logging for this case
        import logging
        logging.basicConfig(level=logging.ERROR)
        logging.error(f"Scraper initialization failed: {init_e}", exc_info=True)


if __name__ == "__main__":
    main()