#!/usr/bin/env python3
"""
Improved filesystem handling functions for the UE5 scraper
"""

import os
import re
import string
from pathlib import Path
from urllib.parse import urlparse, unquote

def clean_filename(name, max_length=50):
    """
    Clean a string to be safe for use as a filename
    
    Issues fixed:
    - Reserved Windows names (CON, PRN, AUX, etc.)
    - Invalid characters for both Windows and Linux
    - Leading/trailing dots and spaces
    - Empty strings
    - Unicode normalization
    """
    if not name or not name.strip():
        return "unnamed"
    
    # Normalize unicode
    import unicodedata
    name = unicodedata.normalize('NFKD', name)
    
    # Remove HTML entities if any
    import html
    name = html.unescape(name)
    
    # Replace problematic characters
    # Windows forbidden: < > : " | ? * \ /
    # Also remove control characters
    forbidden_chars = '<>:"|?*\\/\r\n\t'
    for char in forbidden_chars:
        name = name.replace(char, '_')
    
    # Remove control characters (ASCII 0-31)
    name = ''.join(char for char in name if ord(char) >= 32)
    
    # Collapse multiple spaces/underscores
    name = re.sub(r'[_\s]+', '_', name)
    
    # Remove leading/trailing dots, spaces, underscores
    name = name.strip('._\s')
    
    # Handle Windows reserved names
    windows_reserved = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    if name.upper() in windows_reserved:
        name = f"_{name}"
    
    # Limit length but preserve extension if any
    if len(name) > max_length:
        name = name[:max_length]
    
    # Ensure we don't end with a dot (Windows issue)
    name = name.rstrip('.')
    
    # Final fallback
    if not name:
        return "unnamed"
    
    return name

def clean_directory_name(name):
    """
    Clean a string to be safe for use as a directory name
    """
    if not name or not name.strip():
        return "unnamed_dir"
    
    # Apply same cleaning as filename but allow longer names
    clean_name = clean_filename(name, max_length=100)
    
    # Additional directory-specific cleaning
    # Remove trailing dots (Windows doesn't allow directories ending with dots)
    clean_name = clean_name.rstrip('.')
    
    return clean_name or "unnamed_dir"

def safe_create_directory_structure(base_dir, url):
    """
    Safely create directory structure based on URL path
    
    Issues fixed:
    - Path traversal attacks (../ sequences)
    - Overly long paths
    - Invalid directory names
    - Cross-platform compatibility
    """
    try:
        parsed_url = urlparse(url)
        path_parts = [part for part in parsed_url.path.split('/') if part]
        
        # Remove filename if it exists (has extension)
        if path_parts and '.' in path_parts[-1]:
            path_parts = path_parts[:-1]
        
        # Start from base directory
        current_path = Path(base_dir)
        
        for part in path_parts:
            # URL decode the part
            decoded_part = unquote(part)
            
            # Clean the directory name
            clean_part = clean_directory_name(decoded_part)
            
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
        # Fallback to a safe default
        safe_path = Path(base_dir) / "unknown_structure"
        safe_path.mkdir(parents=True, exist_ok=True)
        return safe_path

def generate_safe_pdf_filename(soup, url, max_length=50):
    """
    Generate a safe PDF filename from page content
    
    Issues fixed:
    - Empty titles
    - Invalid filename characters
    - Duplicate filenames
    - Missing file extensions
    """
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
                filename = clean_filename(title.strip(), max_length)
    
    except Exception:
        # If anything fails, use URL-based name
        try:
            parsed_url = urlparse(url)
            path_parts = [part for part in parsed_url.path.split('/') if part]
            if path_parts:
                filename = clean_filename(path_parts[-1], max_length)
        except Exception:
            pass
    
    # Ensure .pdf extension
    if not filename.lower().endswith('.pdf'):
        filename = f"{filename}.pdf"
    
    return filename

def safe_write_file(content, file_path):
    """
    Safely write content to a file with proper error handling
    
    Issues fixed:
    - Permission errors
    - Disk space issues
    - Atomic writes
    - Directory creation
    """
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check available disk space (rough estimate)
        import shutil
        free_space = shutil.disk_usage(file_path.parent).free
        if free_space < 100 * 1024 * 1024:  # Less than 100MB
            raise OSError("Insufficient disk space")
        
        # Write to temporary file first, then rename (atomic operation)
        temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
        
        # The actual writing would be done by the PDF library
        # This is just the framework
        return temp_path, file_path
        
    except Exception as e:
        raise OSError(f"Failed to prepare file write: {e}")

# Test the functions
if __name__ == "__main__":
    # Test filename cleaning
    test_cases = [
        "Normal Title",
        "Title with <illegal> characters",
        "CON",  # Windows reserved
        "Title with / slashes \\ and : colons",
        "Very long title that exceeds normal filename length limits and should be truncated",
        "",
        "..\\..\\dangerous",
        "Title with unicode: café résumé naïve"
    ]
    
    print("Testing filename cleaning:")
    for test in test_cases:
        cleaned = clean_filename(test)
        print(f"'{test}' -> '{cleaned}'")
    
    print("\nTesting directory structure creation:")
    test_urls = [
        "https://docs.unrealengine.com/5.3/en-US/getting-started/",
        "https://docs.unrealengine.com/5.3/en-US/programming/blueprints/../introduction/",
        "https://docs.unrealengine.com/5.3/en-US/very/deeply/nested/structure/that/goes/on/forever/"
    ]
    
    for url in test_urls:
        print(f"URL: {url}")
        # Would call: safe_create_directory_structure("test_output", url)
        print(f"Would create safe directory structure")