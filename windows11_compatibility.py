#!/usr/bin/env python3
"""
Windows 11 Compatibility Checker for UE5 Documentation Scraper

This module provides comprehensive Windows 11 compatibility checks including:
- Firefox installation detection
- WebDriver compatibility
- System requirements validation
- Permission checks
- Dependency verification
"""

import os
import sys
import platform
import subprocess
import winreg
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

class Windows11CompatibilityChecker:
    """Comprehensive Windows 11 compatibility checker"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.suggestions = []
        self.system_info = {}
        
        # Setup basic logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def check_all(self) -> Dict:
        """Run all compatibility checks and return results"""
        self.logger.info("Starting Windows 11 compatibility check...")
        
        # Gather system information
        self._gather_system_info()
        
        # Run all checks
        self._check_windows_version()
        self._check_python_installation()
        self._check_firefox_installation()
        self._check_webdriver_compatibility()
        self._check_permissions()
        self._check_dependencies()
        self._check_firewall_antivirus()
        self._check_path_environment()
        
        return {
            'system_info': self.system_info,
            'issues': self.issues,
            'warnings': self.warnings,
            'suggestions': self.suggestions,
            'status': 'ready' if not self.issues else 'needs_attention'
        }
    
    def _gather_system_info(self):
        """Gather comprehensive system information"""
        try:
            self.system_info = {
                'platform': platform.platform(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'python_implementation': platform.python_implementation(),
                'is_64bit': platform.machine().endswith('64'),
                'admin_privileges': self._check_admin_privileges()
            }
            
            # Windows-specific version information
            if platform.system() == "Windows":
                try:
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                      r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                        self.system_info['windows_build'] = winreg.QueryValueEx(key, "CurrentBuild")[0]
                        self.system_info['windows_display_version'] = winreg.QueryValueEx(key, "DisplayVersion")[0]
                        self.system_info['windows_product_name'] = winreg.QueryValueEx(key, "ProductName")[0]
                except Exception as e:
                    self.logger.warning(f"Could not get detailed Windows version: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error gathering system info: {e}")
    
    def _check_admin_privileges(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    
    def _check_windows_version(self):
        """Check Windows version compatibility"""
        try:
            if platform.system() != "Windows":
                self.issues.append("This checker is designed for Windows systems")
                return
            
            # Check for Windows 11
            windows_build = self.system_info.get('windows_build')
            if windows_build:
                build_num = int(windows_build)
                if build_num >= 22000:  # Windows 11 builds start at 22000
                    self.logger.info(f"Windows 11 detected (build {build_num})")
                    
                    # Check for known problematic builds
                    if build_num < 22621:  # Builds before 22H2
                        self.warnings.append(
                            f"Windows 11 build {build_num} detected. "
                            "Consider updating to build 22621 or later for better compatibility."
                        )
                        self.suggestions.append("Update to Windows 11 22H2 or later")
                else:
                    self.warnings.append(
                        f"Windows 10 build {build_num} detected. "
                        "The scraper supports Windows 10, but Windows 11 is recommended."
                    )
            
        except Exception as e:
            self.warnings.append(f"Could not determine Windows version: {e}")
    
    def _check_python_installation(self):
        """Check Python installation and version"""
        try:
            python_version = sys.version_info
            
            if python_version < (3, 8):
                self.issues.append(
                    f"Python {python_version.major}.{python_version.minor} is too old. "
                    "Python 3.8 or later is required."
                )
                self.suggestions.append("Upgrade to Python 3.8 or later from python.org")
            elif python_version < (3, 9):
                self.warnings.append(
                    f"Python {python_version.major}.{python_version.minor} works but "
                    "Python 3.9 or later is recommended."
                )
            
            # Check if Python is in PATH
            python_in_path = any(
                os.path.exists(os.path.join(path, "python.exe"))
                for path in os.environ.get("PATH", "").split(os.pathsep)
            )
            
            if not python_in_path:
                self.warnings.append("Python may not be properly added to PATH")
                self.suggestions.append(
                    "Reinstall Python with 'Add Python to PATH' option checked"
                )
            
            # Check for pip
            try:
                import pip
                self.logger.info("pip is available")
            except ImportError:
                self.issues.append("pip is not available")
                self.suggestions.append("Reinstall Python or install pip manually")
                
        except Exception as e:
            self.issues.append(f"Python installation check failed: {e}")
    
    def _check_firefox_installation(self):
        """Check Firefox installation and compatibility"""
        firefox_found = False
        firefox_paths = []
        
        # Standard Firefox installation paths
        potential_paths = [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            os.path.expanduser(r"~\AppData\Local\Mozilla Firefox\firefox.exe"),
        ]
        
        # Check registry for Firefox installation
        try:
            import winreg
            registry_paths = self._get_firefox_from_registry()
            potential_paths.extend(registry_paths)
        except Exception as e:
            self.logger.warning(f"Could not check registry for Firefox: {e}")
        
        # Check each potential path
        for path in potential_paths:
            if os.path.exists(path):
                firefox_found = True
                firefox_paths.append(path)
                
                # Get Firefox version
                try:
                    version = self._get_firefox_version(path)
                    if version:
                        self.system_info['firefox_version'] = version
                        self.logger.info(f"Firefox {version} found at {path}")
                        
                        # Check version compatibility
                        major_version = int(version.split('.')[0])
                        if major_version < 60:
                            self.warnings.append(
                                f"Firefox {version} is quite old. "
                                "Consider updating to a newer version."
                            )
                except Exception as e:
                    self.logger.warning(f"Could not get Firefox version: {e}")
        
        if not firefox_found:
            self.issues.append("Firefox not found in standard locations")
            self.suggestions.extend([
                "Install Firefox from https://firefox.com",
                "Ensure Firefox is installed in a standard location",
                "Alternative: Install Google Chrome as a backup browser"
            ])
        else:
            self.system_info['firefox_paths'] = firefox_paths
        
        # Check for geckodriver
        self._check_geckodriver()
    
    def _get_firefox_from_registry(self) -> List[str]:
        """Get Firefox installation paths from Windows registry"""
        paths = []
        
        registry_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Mozilla\Mozilla Firefox"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Mozilla\Mozilla Firefox"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Mozilla\Mozilla Firefox"),
        ]
        
        for hkey, key_path in registry_keys:
            try:
                with winreg.OpenKey(hkey, key_path) as key:
                    subkey_count = winreg.QueryInfoKey(key)[0]
                    for i in range(subkey_count):
                        subkey_name = winreg.EnumKey(key, i)
                        try:
                            with winreg.OpenKey(key, f"{subkey_name}\\Main") as main_key:
                                install_dir = winreg.QueryValueEx(main_key, "Install Directory")[0]
                                firefox_exe = os.path.join(install_dir, "firefox.exe")
                                if os.path.exists(firefox_exe):
                                    paths.append(firefox_exe)
                        except Exception:
                            continue
            except Exception:
                continue
        
        return paths
    
    def _get_firefox_version(self, firefox_path: str) -> Optional[str]:
        """Get Firefox version from executable"""
        try:
            result = subprocess.run(
                [firefox_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Parse version from output like "Mozilla Firefox 91.0"
                output = result.stdout.strip()
                if "Firefox" in output:
                    parts = output.split()
                    for part in parts:
                        if part.replace('.', '').isdigit():
                            return part
        except Exception as e:
            self.logger.warning(f"Could not get Firefox version: {e}")
        
        return None
    
    def _check_geckodriver(self):
        """Check for geckodriver availability"""
        geckodriver_found = False
        
        # Check if geckodriver is in PATH
        try:
            result = subprocess.run(
                ["geckodriver", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                geckodriver_found = True
                # Parse version from output
                version_line = result.stdout.split('\n')[0]
                if "geckodriver" in version_line:
                    self.system_info['geckodriver_version'] = version_line
                    self.logger.info(f"Geckodriver found: {version_line}")
        except Exception:
            pass
        
        if not geckodriver_found:
            self.warnings.append("Geckodriver not found in PATH")
            self.suggestions.extend([
                "Download geckodriver from https://github.com/mozilla/geckodriver/releases",
                "Add geckodriver to your PATH environment variable",
                "Alternative: Place geckodriver.exe in the same directory as your script"
            ])
    
    def _check_webdriver_compatibility(self):
        """Check WebDriver compatibility"""
        try:
            from selenium import webdriver
            from selenium.webdriver.firefox.options import Options
            
            # Test basic WebDriver functionality
            options = Options()
            options.add_argument("--headless")
            
            try:
                driver = webdriver.Firefox(options=options)
                
                # Test basic navigation
                driver.get("data:text/html,<html><body>Test</body></html>")
                
                # Test page interaction
                title = driver.title
                page_source = driver.page_source
                
                driver.quit()
                
                if "Test" in page_source:
                    self.logger.info("WebDriver compatibility test passed")
                    self.system_info['webdriver_compatible'] = True
                else:
                    self.warnings.append("WebDriver test completed but content may not be correct")
                    
            except Exception as driver_e:
                self.issues.append(f"WebDriver test failed: {driver_e}")
                self.suggestions.extend([
                    "Check Firefox installation",
                    "Verify geckodriver is available",
                    "Try running as Administrator",
                    "Check Windows Defender/antivirus settings"
                ])
                
        except ImportError:
            self.issues.append("Selenium not installed")
            self.suggestions.append("Install selenium: pip install selenium")
    
    def _check_permissions(self):
        """Check file system permissions"""
        test_locations = [
            os.path.expanduser("~"),  # User home directory
            os.path.join(os.path.expanduser("~"), "Documents"),
            ".",  # Current directory
        ]
        
        for location in test_locations:
            try:
                test_file = os.path.join(location, "test_write_permissions.tmp")
                
                # Test write permission
                with open(test_file, 'w') as f:
                    f.write("test")
                
                # Test read permission
                with open(test_file, 'r') as f:
                    content = f.read()
                
                # Clean up
                os.remove(test_file)
                
                if content == "test":
                    self.logger.info(f"Write permissions confirmed for {location}")
                    break
                    
            except Exception as e:
                self.logger.warning(f"Permission test failed for {location}: {e}")
                continue
        else:
            # If all locations failed
            self.issues.append("Cannot write to any test locations")
            self.suggestions.extend([
                "Try running as Administrator",
                "Check folder permissions",
                "Choose a different output directory"
            ])
    
    def _check_dependencies(self):
        """Check Python dependencies"""
        required_modules = [
            'requests', 'beautifulsoup4', 'selenium', 'fake_useragent',
            'lxml', 'aiohttp', 'psutil'
        ]
        
        missing_modules = []
        
        for module in required_modules:
            try:
                if module == 'beautifulsoup4':
                    import bs4  # beautifulsoup4 imports as bs4
                elif module == 'fake_useragent':
                    import fake_useragent
                else:
                    __import__(module)
                    
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            self.issues.append(f"Missing required modules: {', '.join(missing_modules)}")
            self.suggestions.append(
                f"Install missing modules: pip install {' '.join(missing_modules)}"
            )
        else:
            self.logger.info("All required Python modules are available")
    
    def _check_firewall_antivirus(self):
        """Check for potential firewall/antivirus interference"""
        # Check Windows Defender status
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-MpPreference | Select-Object -Property DisableRealtimeMonitoring"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if "False" in result.stdout:
                self.warnings.append(
                    "Windows Defender real-time protection is enabled. "
                    "This may interfere with browser automation."
                )
                self.suggestions.append(
                    "Consider adding the scraper directory to Windows Defender exclusions"
                )
                
        except Exception as e:
            self.logger.warning(f"Could not check Windows Defender status: {e}")
        
        # General antivirus warning
        self.suggestions.append(
            "If you experience issues, try temporarily disabling antivirus real-time protection"
        )
    
    def _check_path_environment(self):
        """Check PATH environment variable"""
        path_env = os.environ.get("PATH", "")
        path_dirs = path_env.split(os.pathsep)
        
        # Check for Python in PATH
        python_in_path = any(
            os.path.exists(os.path.join(path_dir, "python.exe"))
            for path_dir in path_dirs
            if path_dir
        )
        
        if not python_in_path:
            self.warnings.append("Python not found in PATH environment variable")
        
        # Check PATH length (Windows has limitations)
        if len(path_env) > 2047:
            self.warnings.append(
                "PATH environment variable is very long. "
                "This may cause issues on some Windows versions."
            )
    
    def generate_report(self) -> str:
        """Generate a comprehensive compatibility report"""
        report = []
        report.append("=" * 80)
        report.append("UE5 Documentation Scraper - Windows 11 Compatibility Report")
        report.append("=" * 80)
        report.append("")
        
        # System Information
        report.append("SYSTEM INFORMATION:")
        for key, value in self.system_info.items():
            report.append(f"  {key}: {value}")
        report.append("")
        
        # Issues
        if self.issues:
            report.append("CRITICAL ISSUES (must be resolved):")
            for i, issue in enumerate(self.issues, 1):
                report.append(f"  {i}. {issue}")
            report.append("")
        
        # Warnings
        if self.warnings:
            report.append("WARNINGS (recommended to address):")
            for i, warning in enumerate(self.warnings, 1):
                report.append(f"  {i}. {warning}")
            report.append("")
        
        # Suggestions
        if self.suggestions:
            report.append("SUGGESTIONS:")
            for i, suggestion in enumerate(self.suggestions, 1):
                report.append(f"  {i}. {suggestion}")
            report.append("")
        
        # Status
        if not self.issues:
            report.append("STATUS: READY TO RUN")
            report.append("Your system appears to be compatible with the UE5 Documentation Scraper.")
        else:
            report.append("STATUS: NEEDS ATTENTION")
            report.append("Please resolve the critical issues listed above before running the scraper.")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Main function to run compatibility check"""
    if platform.system() != "Windows":
        print("This compatibility checker is designed for Windows systems.")
        sys.exit(1)
    
    checker = Windows11CompatibilityChecker()
    results = checker.check_all()
    
    # Generate and display report
    report = checker.generate_report()
    print(report)
    
    # Save report to file
    try:
        with open("windows11_compatibility_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\nDetailed report saved to: windows11_compatibility_report.txt")
    except Exception as e:
        print(f"\nCould not save report to file: {e}")
    
    # Exit with appropriate code
    if results['status'] == 'ready':
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()