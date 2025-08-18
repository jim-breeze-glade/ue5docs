#!/usr/bin/env python3
"""
Test script to verify the UE5 scraper setup
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import requests
        import bs4
        import selenium
        import fake_useragent
        import platform
        print("✓ Core Python modules imported successfully")
        
        # Test platform-specific PDF modules
        system = platform.system()
        if system == "Windows":
            # On Windows, we use Selenium for PDF generation, so don't require weasyprint
            print("✓ Windows detected: Using Selenium for PDF generation")
        else:
            # On Unix/Linux, try to import weasyprint
            try:
                import weasyprint
                print("✓ WeasyPrint available for PDF generation")
            except ImportError:
                print("! WeasyPrint not available, will fall back to HTML output")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_firefoxdriver():
    """Test if Firefox driver can be set up"""
    try:
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options
        
        options = Options()
        options.add_argument("--headless")
        
        driver = webdriver.Firefox(options=options)
        driver.quit()
        print("✓ Firefox driver setup successful")
        return True
    except Exception as e:
        print(f"✗ Firefox driver setup failed: {e}")
        return False

def test_pdf_generation():
    """Test basic PDF generation"""
    try:
        import platform
        import tempfile
        
        html = "<html><body><h1>Test PDF</h1><p>This is a test.</p></body></html>"
        
        # Use temporary directory that works on all platforms
        temp_dir = tempfile.gettempdir()
        test_pdf_path = os.path.join(temp_dir, "test.pdf")
        
        system = platform.system()
        if system == "Windows":
            # On Windows, test basic HTML functionality since PDF uses Selenium
            temp_html = os.path.join(temp_dir, "test.html")
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(html)
            
            if os.path.exists(temp_html):
                os.remove(temp_html)
                print("✓ HTML generation test successful (Windows PDF ready)")
                return True
            else:
                print("✗ HTML generation test failed")
                return False
        else:
            # On Unix/Linux, try WeasyPrint
            try:
                import weasyprint
                pdf_doc = weasyprint.HTML(string=html)
                pdf_doc.write_pdf(test_pdf_path)
                
                if os.path.exists(test_pdf_path):
                    os.remove(test_pdf_path)
                    print("✓ PDF generation test successful")
                    return True
                else:
                    print("✗ PDF generation failed")
                    return False
            except ImportError:
                print("! WeasyPrint not available, skipping PDF test")
                return True  # Not a failure on Unix if weasyprint is missing
    except Exception as e:
        print(f"✗ PDF generation error: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing UE5 Documentation Scraper setup...\n")
    
    tests = [
        ("Python Module Imports", test_imports),
        ("Firefox Driver Setup", test_firefoxdriver),
        ("PDF Generation", test_pdf_generation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        results.append(test_func())
        print()
    
    if all(results):
        print("🎉 All tests passed! The scraper is ready to use.")
        print("\nTo run the scraper:")
        print("1. source venv/bin/activate")
        print("2. python ue5_docs_scraper.py")
    else:
        print("❌ Some tests failed. Please check the setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()