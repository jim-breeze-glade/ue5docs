#!/usr/bin/env python3
"""
Enhanced Cross-Platform Logging Module for UE5 Documentation Scraper

This module provides comprehensive error logging with cross-platform support,
detailed error information, and structured logging to log.txt file.
"""

import os
import sys
import logging
import logging.handlers
import platform
import traceback
import json
import datetime
import psutil
import socket
from pathlib import Path
from typing import Optional, Dict, Any
from functools import wraps


class CrossPlatformLogger:
    """
    Enhanced logging class with cross-platform support and detailed error tracking.
    
    Features:
    - Cross-platform compatibility (Windows, macOS, Linux)
    - Structured logging with JSON format option
    - System information logging
    - Performance metrics
    - Detailed stack traces
    - Error categorization
    - Log rotation
    """
    
    def __init__(self, 
                 log_file: str = "log.txt",
                 log_level: int = logging.INFO,
                 max_bytes: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 enable_console: bool = True,
                 enable_json: bool = False):
        """
        Initialize the enhanced logger.
        
        Args:
            log_file: Path to the log file
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
            enable_console: Whether to also log to console
            enable_json: Whether to use JSON format for structured logging
        """
        self.log_file = Path(log_file).resolve()
        self.log_level = log_level
        self.enable_json = enable_json
        self.start_time = datetime.datetime.now()
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize logger
        self.logger = logging.getLogger("UE5DocsScraper")
        self.logger.setLevel(log_level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup formatters
        self._setup_formatters()
        
        # Setup file handler with rotation
        self._setup_file_handler(max_bytes, backup_count)
        
        # Setup console handler if enabled
        if enable_console:
            self._setup_console_handler()
        
        # Log system information at startup
        self._log_system_info()
        
        # Setup error categorization
        self.error_categories = {
            'selenium': ['webdriver', 'browser', 'element not found', 'selenium'],
            'network': ['connection', 'timeout', 'dns', 'ssl', 'certificate', 'proxy'],
            'filesystem': ['permission', 'disk', 'space', 'file not found', 'access denied'],
            'pdf': ['weasyprint', 'wkhtmltopdf', 'print', 'rendering'],
            'parsing': ['beautifulsoup', 'xml', 'html', 'encoding'],
            'memory': ['memory', 'ram', 'out of memory', 'allocation'],
            'platform': ['windows', 'linux', 'macos', 'path', 'separator']
        }
        
    def _setup_formatters(self):
        """Setup logging formatters for different output types."""
        if self.enable_json:
            # JSON formatter for structured logging
            self.json_formatter = JsonFormatter()
            self.file_formatter = self.json_formatter
        else:
            # Standard text formatter
            self.file_formatter = logging.Formatter(
                fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # Console formatter (simpler)
        self.console_formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    
    def _setup_file_handler(self, max_bytes: int, backup_count: int):
        """Setup rotating file handler."""
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                filename=str(self.log_file),
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(self.file_formatter)
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            # Fallback to basic file handler if rotation fails
            fallback_handler = logging.FileHandler(
                str(self.log_file), 
                encoding='utf-8'
            )
            fallback_handler.setLevel(self.log_level)
            fallback_handler.setFormatter(self.file_formatter)
            self.logger.addHandler(fallback_handler)
            print(f"Warning: Could not setup rotating file handler, using basic handler: {e}")
    
    def _setup_console_handler(self):
        """Setup console handler for real-time feedback."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(self.console_formatter)
        self.logger.addHandler(console_handler)
    
    def _log_system_info(self):
        """Log comprehensive system information at startup."""
        system_info = self._gather_system_info()
        
        self.logger.info("=" * 80)
        self.logger.info("UE5 Documentation Scraper - Enhanced Logging Started")
        self.logger.info("=" * 80)
        
        for key, value in system_info.items():
            self.logger.info(f"System {key}: {value}")
        
        self.logger.info("=" * 80)
    
    def _gather_system_info(self) -> Dict[str, Any]:
        """Gather comprehensive system information."""
        info = {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation(),
            'hostname': socket.gethostname(),
        }
        
        # Add memory information if psutil is available
        try:
            memory = psutil.virtual_memory()
            info.update({
                'total_memory_gb': round(memory.total / (1024**3), 2),
                'available_memory_gb': round(memory.available / (1024**3), 2),
                'memory_percent_used': memory.percent
            })
            
            # CPU information
            info.update({
                'cpu_count': psutil.cpu_count(logical=True),
                'cpu_count_physical': psutil.cpu_count(logical=False),
                'cpu_percent': psutil.cpu_percent(interval=1)
            })
            
            # Disk space for log directory
            disk_usage = psutil.disk_usage(str(self.log_file.parent))
            info.update({
                'disk_total_gb': round(disk_usage.total / (1024**3), 2),
                'disk_free_gb': round(disk_usage.free / (1024**3), 2),
                'disk_percent_used': round((disk_usage.used / disk_usage.total) * 100, 2)
            })
            
        except Exception as e:
            info['system_info_error'] = str(e)
        
        return info
    
    def _categorize_error(self, error_msg: str) -> str:
        """Categorize error based on message content."""
        error_msg_lower = error_msg.lower()
        
        for category, keywords in self.error_categories.items():
            if any(keyword in error_msg_lower for keyword in keywords):
                return category
        
        return 'unknown'
    
    def _get_performance_info(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        try:
            current_process = psutil.Process()
            
            return {
                'memory_usage_mb': round(current_process.memory_info().rss / (1024**2), 2),
                'cpu_percent': current_process.cpu_percent(),
                'num_threads': current_process.num_threads(),
                'elapsed_time_seconds': (datetime.datetime.now() - self.start_time).total_seconds()
            }
        except Exception:
            return {'performance_info_error': 'Unable to gather performance metrics'}
    
    def log_error(self, 
                  message: str, 
                  exception: Optional[Exception] = None,
                  context: Optional[Dict[str, Any]] = None,
                  url: Optional[str] = None,
                  operation: Optional[str] = None):
        """
        Log an error with enhanced context and categorization.
        
        Args:
            message: Error message
            exception: Exception object if available
            context: Additional context information
            url: URL being processed when error occurred
            operation: Operation being performed when error occurred
        """
        error_data = {
            'message': message,
            'timestamp': datetime.datetime.now().isoformat(),
            'level': 'ERROR'
        }
        
        if exception:
            error_data.update({
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'traceback': traceback.format_exc(),
                'category': self._categorize_error(str(exception))
            })
        else:
            error_data['category'] = self._categorize_error(message)
        
        if url:
            error_data['url'] = url
            
        if operation:
            error_data['operation'] = operation
            
        if context:
            error_data['context'] = context
        
        # Add performance info
        error_data['performance'] = self._get_performance_info()
        
        # Add platform-specific information
        error_data['platform_info'] = {
            'system': platform.system(),
            'python_version': platform.python_version(),
            'working_directory': str(Path.cwd())
        }
        
        if self.enable_json:
            self.logger.error(json.dumps(error_data, indent=2))
        else:
            # Format for readable text output
            formatted_msg = f"{message}"
            if url:
                formatted_msg += f" | URL: {url}"
            if operation:
                formatted_msg += f" | Operation: {operation}"
            if exception:
                formatted_msg += f" | Exception: {type(exception).__name__}: {exception}"
                formatted_msg += f" | Category: {error_data['category']}"
            
            self.logger.error(formatted_msg)
            
            # Log traceback separately if available
            if exception and traceback.format_exc() != "NoneType: None\n":
                self.logger.error(f"Traceback:\n{traceback.format_exc()}")
    
    def log_warning(self, 
                    message: str, 
                    context: Optional[Dict[str, Any]] = None,
                    url: Optional[str] = None):
        """Log a warning with context."""
        if context or url:
            formatted_msg = message
            if url:
                formatted_msg += f" | URL: {url}"
            if context:
                formatted_msg += f" | Context: {context}"
            self.logger.warning(formatted_msg)
        else:
            self.logger.warning(message)
    
    def log_info(self, 
                 message: str, 
                 context: Optional[Dict[str, Any]] = None):
        """Log an info message with optional context."""
        if context:
            self.logger.info(f"{message} | Context: {context}")
        else:
            self.logger.info(message)
    
    def log_success(self, 
                    message: str, 
                    url: Optional[str] = None,
                    file_path: Optional[str] = None,
                    file_size: Optional[int] = None):
        """Log a successful operation with details."""
        formatted_msg = f"SUCCESS: {message}"
        
        if url:
            formatted_msg += f" | URL: {url}"
        if file_path:
            formatted_msg += f" | File: {file_path}"
        if file_size:
            formatted_msg += f" | Size: {file_size} bytes"
            
        self.logger.info(formatted_msg)
    
    def log_performance(self, 
                       operation: str, 
                       duration: float,
                       context: Optional[Dict[str, Any]] = None):
        """Log performance metrics for operations."""
        perf_info = self._get_performance_info()
        formatted_msg = f"PERFORMANCE: {operation} completed in {duration:.2f}s"
        
        if context:
            formatted_msg += f" | Context: {context}"
            
        formatted_msg += f" | Memory: {perf_info.get('memory_usage_mb', 'N/A')}MB"
        formatted_msg += f" | CPU: {perf_info.get('cpu_percent', 'N/A')}%"
        
        self.logger.info(formatted_msg)
    
    def log_startup_summary(self, config: Dict[str, Any]):
        """Log startup configuration summary."""
        self.logger.info("STARTUP CONFIGURATION:")
        for key, value in config.items():
            self.logger.info(f"  {key}: {value}")
    
    def log_completion_summary(self, 
                              total_processed: int,
                              successful: int,
                              failed: int,
                              duration: float):
        """Log completion summary with statistics."""
        success_rate = (successful / total_processed * 100) if total_processed > 0 else 0
        
        self.logger.info("=" * 80)
        self.logger.info("SCRAPING COMPLETION SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Total URLs processed: {total_processed}")
        self.logger.info(f"Successful: {successful}")
        self.logger.info(f"Failed: {failed}")
        self.logger.info(f"Success rate: {success_rate:.1f}%")
        self.logger.info(f"Total duration: {duration:.2f} seconds")
        self.logger.info(f"Average time per URL: {duration/total_processed:.2f}s" if total_processed > 0 else "N/A")
        
        # Final performance summary
        final_perf = self._get_performance_info()
        self.logger.info(f"Final memory usage: {final_perf.get('memory_usage_mb', 'N/A')}MB")
        self.logger.info("=" * 80)


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage()
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)


def error_handler(logger: CrossPlatformLogger):
    """
    Decorator for automatic error logging and handling.
    
    Usage:
        @error_handler(logger)
        def my_function():
            # Function code here
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                start_time = datetime.datetime.now()
                result = func(*args, **kwargs)
                duration = (datetime.datetime.now() - start_time).total_seconds()
                
                logger.log_performance(
                    operation=func.__name__,
                    duration=duration,
                    context={'args_count': len(args), 'kwargs_count': len(kwargs)}
                )
                
                return result
                
            except Exception as e:
                logger.log_error(
                    message=f"Error in function {func.__name__}",
                    exception=e,
                    operation=func.__name__,
                    context={
                        'args_count': len(args),
                        'kwargs_count': len(kwargs)
                    }
                )
                raise
                
        return wrapper
    return decorator


# Convenience function to create a pre-configured logger
def create_logger(log_file: str = "log.txt", 
                  enable_json: bool = False,
                  log_level: int = logging.INFO) -> CrossPlatformLogger:
    """
    Create a pre-configured CrossPlatformLogger instance.
    
    Args:
        log_file: Path to log file
        enable_json: Whether to use JSON formatting
        log_level: Logging level
        
    Returns:
        Configured CrossPlatformLogger instance
    """
    return CrossPlatformLogger(
        log_file=log_file,
        enable_json=enable_json,
        log_level=log_level,
        enable_console=True
    )


if __name__ == "__main__":
    # Test the logging functionality
    test_logger = create_logger("test_log.txt")
    
    test_logger.log_info("Testing enhanced logging system")
    
    try:
        # Simulate an error
        raise ValueError("This is a test error")
    except Exception as e:
        test_logger.log_error(
            "Test error occurred",
            exception=e,
            url="http://test.example.com",
            operation="test_operation"
        )
    
    test_logger.log_success(
        "Test completed successfully",
        file_path="/test/path/file.txt",
        file_size=1024
    )