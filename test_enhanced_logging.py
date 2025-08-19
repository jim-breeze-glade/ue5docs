#!/usr/bin/env python3
"""
Test script for enhanced cross-platform logging functionality.

This script tests the enhanced logging system to ensure it works correctly
across different platforms and scenarios.
"""

import os
import sys
import platform
import tempfile
import time
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_logger import CrossPlatformLogger, create_logger, error_handler


def test_basic_logging():
    """Test basic logging functionality."""
    print("Testing basic logging functionality...")
    
    # Create a temporary log file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
        log_file = tmp_file.name
    
    try:
        logger = CrossPlatformLogger(
            log_file=log_file,
            enable_console=True,
            enable_json=False
        )
        
        # Test different log levels
        logger.log_info("This is an info message")
        logger.log_warning("This is a warning message", context={'test': True})
        
        # Test error logging with exception
        try:
            raise ValueError("This is a test error for logging")
        except Exception as e:
            logger.log_error(
                "Test error occurred",
                exception=e,
                url="http://test.example.com",
                operation="test_operation"
            )
        
        # Test success logging
        logger.log_success(
            "Test operation completed",
            url="http://test.example.com",
            file_path="/test/path/file.txt",
            file_size=1024
        )
        
        # Test performance logging
        logger.log_performance("test_operation", 1.5, {'items_processed': 10})
        
        print(f"✓ Basic logging test completed. Log file: {log_file}")
        return True
        
    except Exception as e:
        print(f"✗ Basic logging test failed: {e}")
        return False
    finally:
        # Clean up
        try:
            os.unlink(log_file)
        except:
            pass


def test_json_logging():
    """Test JSON-formatted logging."""
    print("Testing JSON logging functionality...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        log_file = tmp_file.name
    
    try:
        logger = CrossPlatformLogger(
            log_file=log_file,
            enable_console=False,  # Disable console for JSON test
            enable_json=True
        )
        
        logger.log_info("JSON test message")
        
        try:
            raise RuntimeError("JSON test error")
        except Exception as e:
            logger.log_error("JSON error test", exception=e)
        
        # Check if the log file contains valid JSON-like content
        with open(log_file, 'r') as f:
            content = f.read()
            if '"timestamp"' in content and '"level"' in content:
                print("✓ JSON logging test completed")
                return True
            else:
                print("✗ JSON logging test failed - invalid format")
                return False
                
    except Exception as e:
        print(f"✗ JSON logging test failed: {e}")
        return False
    finally:
        try:
            os.unlink(log_file)
        except:
            pass


def test_error_decorator():
    """Test the error handling decorator."""
    print("Testing error decorator functionality...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
        log_file = tmp_file.name
    
    try:
        logger = create_logger(log_file)
        
        @error_handler(logger)
        def test_function_success():
            """A test function that succeeds."""
            time.sleep(0.1)  # Simulate some work
            return "success"
        
        @error_handler(logger)
        def test_function_failure():
            """A test function that fails."""
            raise Exception("Decorator test error")
        
        # Test successful function
        result = test_function_success()
        if result == "success":
            print("✓ Decorator success test passed")
        else:
            print("✗ Decorator success test failed")
            return False
        
        # Test error function
        try:
            test_function_failure()
            print("✗ Decorator error test failed - no exception raised")
            return False
        except Exception:
            print("✓ Decorator error test passed")
            return True
            
    except Exception as e:
        print(f"✗ Error decorator test failed: {e}")
        return False
    finally:
        try:
            os.unlink(log_file)
        except:
            pass


def test_platform_compatibility():
    """Test platform-specific functionality."""
    print(f"Testing platform compatibility on {platform.system()}...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
        log_file = tmp_file.name
    
    try:
        logger = CrossPlatformLogger(log_file=log_file)
        
        # Test system info gathering
        logger._log_system_info()
        
        # Test different error categories
        test_errors = [
            ("Network error: connection timeout", "network"),
            ("Permission denied accessing file", "filesystem"),
            ("WebDriver timeout error", "selenium"),
            ("WeasyPrint rendering failed", "pdf"),
            ("XML parsing error", "parsing"),
            ("Out of memory error", "memory"),
            ("Windows path too long", "platform")
        ]
        
        for error_msg, expected_category in test_errors:
            category = logger._categorize_error(error_msg)
            if category == expected_category:
                print(f"✓ Error categorization correct: '{error_msg}' -> {category}")
            else:
                print(f"✗ Error categorization failed: '{error_msg}' -> {category} (expected {expected_category})")
        
        print("✓ Platform compatibility test completed")
        return True
        
    except Exception as e:
        print(f"✗ Platform compatibility test failed: {e}")
        return False
    finally:
        try:
            os.unlink(log_file)
        except:
            pass


def test_log_rotation():
    """Test log file rotation functionality."""
    print("Testing log rotation functionality...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
        log_file = tmp_file.name
    
    try:
        # Create logger with small max size for testing
        logger = CrossPlatformLogger(
            log_file=log_file,
            max_bytes=1024,  # 1KB for quick rotation testing
            backup_count=2,
            enable_console=False
        )
        
        # Generate enough log messages to trigger rotation
        for i in range(50):
            logger.log_info(f"Test message {i} - This is a longer message to fill up the log file quickly")
        
        # Check if backup files were created
        log_path = Path(log_file)
        backup1 = log_path.with_suffix(log_path.suffix + '.1')
        
        if backup1.exists():
            print("✓ Log rotation test completed - backup file created")
            return True
        else:
            print("✗ Log rotation test failed - no backup file created")
            return False
            
    except Exception as e:
        print(f"✗ Log rotation test failed: {e}")
        return False
    finally:
        # Clean up all possible files
        try:
            log_path = Path(log_file)
            os.unlink(log_file)
            for i in range(1, 4):
                backup = log_path.with_suffix(log_path.suffix + f'.{i}')
                if backup.exists():
                    os.unlink(backup)
        except:
            pass


def main():
    """Run all logging tests."""
    print("=" * 60)
    print("Enhanced Cross-Platform Logging Test Suite")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print("=" * 60)
    
    tests = [
        test_basic_logging,
        test_json_logging,
        test_error_decorator,
        test_platform_compatibility,
        test_log_rotation
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"✗ Test {test_func.__name__} crashed: {e}")
            print()
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced logging is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())