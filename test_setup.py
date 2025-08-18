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
        import weasyprint
        import pdfkit
        import fake_useragent
        print("✓ All Python modules imported successfully")
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
        import weasyprint
        
        html = "<html><body><h1>Test PDF</h1><p>This is a test.</p></body></html>"
        pdf_doc = weasyprint.HTML(string=html)
        pdf_doc.write_pdf("/tmp/test.pdf")
        
        if os.path.exists("/tmp/test.pdf"):
            os.remove("/tmp/test.pdf")
            print("✓ PDF generation test successful")
            return True
        else:
            print("✗ PDF generation failed")
            return False
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