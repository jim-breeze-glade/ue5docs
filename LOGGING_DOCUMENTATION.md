# Enhanced Cross-Platform Logging Documentation

## Overview

The UE5 Documentation Scraper now includes a comprehensive cross-platform logging system that provides detailed error tracking, performance monitoring, and system information logging. The enhanced logging writes to `log.txt` by default and works seamlessly across Windows, macOS, and Linux.

## Key Features

### 🚀 Cross-Platform Compatibility
- **Windows**: Fully tested and optimized for Windows environments
- **macOS**: Native support for Apple systems  
- **Linux**: Optimized for various Linux distributions

### 📊 Comprehensive System Information
- Platform details (OS, version, architecture)
- Memory usage and availability
- CPU information and utilization
- Disk space monitoring
- Python environment details

### 🎯 Intelligent Error Categorization
Errors are automatically categorized into types:
- **Network**: Connection issues, timeouts, DNS problems
- **Selenium**: WebDriver and browser-related errors
- **Filesystem**: Permission, disk space, and file access issues
- **PDF**: WeasyPrint and PDF generation problems
- **Parsing**: HTML/XML parsing errors
- **Memory**: Memory allocation and usage issues
- **Platform**: OS-specific compatibility issues

### 📈 Performance Monitoring
- Operation duration tracking
- Memory usage monitoring
- CPU utilization tracking
- Performance metrics for all major operations

### 🔄 Advanced File Management
- Automatic log file rotation (default: 10MB max, 5 backups)
- Atomic file operations to prevent corruption
- UTF-8 encoding for international character support

## File Structure

The enhanced logging system consists of two main files:

### `/home/jim/development/ue5docs/enhanced_logger.py`
The core logging module providing:
- `CrossPlatformLogger` class with full logging capabilities
- `JsonFormatter` for structured JSON logging
- `error_handler` decorator for automatic error wrapping
- `create_logger()` convenience function

### `/home/jim/development/ue5docs/ue5_docs_scraper.py` (Updated)
The main scraper with integrated enhanced logging:
- Startup configuration logging
- Detailed error handling for all operations
- Performance tracking for URL processing
- Comprehensive completion summaries

## Usage Examples

### Basic Logging
```python
from enhanced_logger import CrossPlatformLogger

logger = CrossPlatformLogger(log_file="log.txt")
logger.log_info("Starting operation")
logger.log_warning("Warning message", url="http://example.com")
logger.log_success("Operation completed", file_path="/path/to/file.pdf", file_size=1024)
```

### Error Logging with Context
```python
try:
    # Some operation that might fail
    risky_operation()
except Exception as e:
    logger.log_error(
        "Operation failed",
        exception=e,
        operation="risky_operation",
        url="http://example.com",
        context={'additional_info': 'value'}
    )
```

### Performance Monitoring
```python
@error_handler(logger)
def my_function():
    # Function automatically gets performance tracking
    return "result"
```

## Log Output Examples

### Standard Text Format
```
2025-08-18 21:34:37 | ERROR    | UE5DocsScraper:245 | Error retrieving sitemap | URL: https://docs.unrealengine.com/sitemap.xml | Operation: get_sitemap_urls | Exception: ConnectionError: Failed to establish connection | Category: network
```

### System Information
```
2025-08-18 21:34:36 | INFO     | UE5DocsScraper:154 | System platform: Linux-6.16.1-arch1-1-x86_64-with-glibc2.42
2025-08-18 21:34:36 | INFO     | UE5DocsScraper:154 | System total_memory_gb: 31.04
2025-08-18 21:34:36 | INFO     | UE5DocsScraper:154 | System cpu_count: 16
```

### Performance Tracking
```
2025-08-18 21:34:37 | INFO     | UE5DocsScraper:322 | PERFORMANCE: sitemap_parsing completed in 2.30s | Context: {'url_count': 1247} | Memory: 18.0MB | CPU: 0.0%
```

## Configuration Options

### Log Levels
- `DEBUG`: Detailed debugging information
- `INFO`: General operational messages (default)
- `WARNING`: Warning messages for non-critical issues
- `ERROR`: Error messages for failures
- `CRITICAL`: Critical errors that may stop execution

### Output Formats
- **Text Format**: Human-readable logs (default)
- **JSON Format**: Structured logging for automated processing

### File Rotation
- **max_bytes**: Maximum log file size before rotation (default: 10MB)
- **backup_count**: Number of backup files to keep (default: 5)

## Integration Benefits

The enhanced logging provides several benefits for the UE5 documentation scraper:

1. **DevOps Troubleshooting**: Rapid incident response with categorized errors
2. **Performance Monitoring**: Track scraping performance and identify bottlenecks
3. **Cross-Platform Compatibility**: Consistent logging across all operating systems
4. **Comprehensive Error Context**: Detailed information for debugging issues
5. **Automated Analysis**: Structured data for monitoring and alerting systems

## Testing

The system includes comprehensive tests in `/home/jim/development/ue5docs/test_enhanced_logging.py`:
- Basic logging functionality
- JSON format logging
- Error decorator testing
- Platform compatibility
- Log rotation verification

Run tests with:
```bash
python test_enhanced_logging.py
```

## Dependencies

The enhanced logging requires the following additional dependency:
- `psutil`: For system monitoring and performance metrics

This has been added to `requirements.txt`.

## File Locations

- **Primary Log File**: `/home/jim/development/ue5docs/log.txt`
- **Backup Files**: `log.txt.1`, `log.txt.2`, etc. (up to 5 backups)
- **Enhanced Logger Module**: `/home/jim/development/ue5docs/enhanced_logger.py`
- **Updated Scraper**: `/home/jim/development/ue5docs/ue5_docs_scraper.py`

The logging system ensures all paths are absolute and cross-platform compatible.