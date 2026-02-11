#!/usr/bin/env python3
"""
License Uploader - Windows Diagnostic Tool
Comprehensive system checker to identify and fix Windows deployment issues
"""

import os
import sys
import subprocess
import platform
import socket
import json
from pathlib import Path
from typing import Tuple, List, Dict, Optional

# Color codes for terminal output (works in Windows 10+)
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

    @classmethod
    def supports_color(cls):
        """Check if terminal supports colors"""
        if sys.platform != 'win32':
            return True
        # Windows 10+ supports ANSI colors
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except:
            return False

# Disable colors if not supported
if not Colors.supports_color():
    for attr in dir(Colors):
        if not attr.startswith('_') and attr != 'supports_color':
            setattr(Colors, attr, '')

class DiagnosticCheck:
    """Represents a single diagnostic check"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = "PENDING"
        self.message = ""
        self.details = []
        self.fix_available = False
        self.fix_function = None

    def pass_check(self, message: str = "", details: List[str] = None):
        self.status = "PASS"
        self.message = message
        self.details = details or []

    def warn_check(self, message: str, details: List[str] = None, fix_function=None):
        self.status = "WARN"
        self.message = message
        self.details = details or []
        if fix_function:
            self.fix_available = True
            self.fix_function = fix_function

    def fail_check(self, message: str, details: List[str] = None, fix_function=None):
        self.status = "FAIL"
        self.message = message
        self.details = details or []
        if fix_function:
            self.fix_available = True
            self.fix_function = fix_function

    def print_result(self):
        """Print the check result"""
        if self.status == "PASS":
            icon = f"{Colors.GREEN}✓{Colors.END}"
            status_text = f"{Colors.GREEN}PASS{Colors.END}"
        elif self.status == "WARN":
            icon = f"{Colors.YELLOW}⚠{Colors.END}"
            status_text = f"{Colors.YELLOW}WARN{Colors.END}"
        elif self.status == "FAIL":
            icon = f"{Colors.RED}✗{Colors.END}"
            status_text = f"{Colors.RED}FAIL{Colors.END}"
        else:
            icon = "○"
            status_text = "PENDING"

        print(f"\n{icon} [{status_text}] {Colors.BOLD}{self.name}{Colors.END}")
        print(f"  {self.description}")

        if self.message:
            print(f"  → {self.message}")

        for detail in self.details:
            print(f"    • {detail}")

        if self.fix_available:
            print(f"  {Colors.BLUE}[FIX AVAILABLE]{Colors.END}")

class WindowsDiagnostics:
    """Windows deployment diagnostics"""

    def __init__(self):
        self.checks: List[DiagnosticCheck] = []
        self.summary = {"pass": 0, "warn": 0, "fail": 0}

    def add_check(self, check: DiagnosticCheck):
        """Add a check to the list"""
        self.checks.append(check)

    def print_header(self):
        """Print diagnostic header"""
        print("\n" + "="*70)
        print(f"{Colors.BOLD}License Uploader - Windows Diagnostic Tool{Colors.END}")
        print("="*70)
        print(f"\nAnalyzing Windows deployment configuration...")
        print(f"Platform: {platform.system()} {platform.release()} ({platform.version()})")
        print(f"Architecture: {platform.machine()}")
        print(f"Python: {sys.version}")

    def print_summary(self):
        """Print diagnostic summary"""
        print("\n" + "="*70)
        print(f"{Colors.BOLD}DIAGNOSTIC SUMMARY{Colors.END}")
        print("="*70)

        total = sum(self.summary.values())
        print(f"\nTotal Checks: {total}")
        print(f"{Colors.GREEN}✓ Passed:{Colors.END} {self.summary['pass']}")
        print(f"{Colors.YELLOW}⚠ Warnings:{Colors.END} {self.summary['warn']}")
        print(f"{Colors.RED}✗ Failed:{Colors.END} {self.summary['fail']}")

        # Overall status
        if self.summary['fail'] == 0 and self.summary['warn'] == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED!{Colors.END}")
            print("Your system is ready to run License Uploader.")
        elif self.summary['fail'] == 0:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ WARNINGS DETECTED{Colors.END}")
            print("System should work but may have issues. Review warnings above.")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ CRITICAL ISSUES DETECTED{Colors.END}")
            print("System is not ready. Please fix the failed checks above.")

        # Available fixes
        fixable = [c for c in self.checks if c.fix_available]
        if fixable:
            print(f"\n{Colors.BLUE}💡 {len(fixable)} issue(s) can be fixed automatically.{Colors.END}")
            print("Run this tool with the --fix flag to attempt repairs.")

    def run_diagnostics(self):
        """Run all diagnostic checks"""
        self.print_header()

        # Run checks
        self.check_platform()
        self.check_python_installation()
        self.check_python_version()
        self.check_python_path()
        self.check_pip()
        self.check_venv_module()
        self.check_virtual_environment()
        self.check_dependencies()
        self.check_env_file()
        self.check_env_configuration()
        self.check_port_availability()
        self.check_file_permissions()
        self.check_tkinter()
        self.check_antivirus_interference()

        # Count results
        for check in self.checks:
            self.summary[check.status.lower()] += 1

        # Print all results
        for check in self.checks:
            check.print_result()

        # Print summary
        self.print_summary()

        # Save report
        self.save_report()

    def check_platform(self):
        """Check if running on Windows"""
        check = DiagnosticCheck("Platform Check", "Verify running on Windows")

        if sys.platform == 'win32':
            version = platform.version()
            release = platform.release()
            check.pass_check(
                f"Running on Windows {release}",
                [f"Version: {version}"]
            )
        else:
            check.fail_check(
                f"Not running on Windows (detected: {sys.platform})",
                ["This diagnostic tool is designed for Windows systems only"]
            )

        self.add_check(check)

    def check_python_installation(self):
        """Check Python installation"""
        check = DiagnosticCheck("Python Installation", "Check if Python is properly installed")

        python_exe = sys.executable
        check.pass_check(
            f"Python found at: {python_exe}",
            [
                f"Version: {sys.version.split()[0]}",
                f"Executable: {python_exe}"
            ]
        )

        self.add_check(check)

    def check_python_version(self):
        """Check Python version"""
        check = DiagnosticCheck("Python Version", "Verify Python 3.11 or higher")

        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"

        if version.major == 3 and version.minor >= 11:
            check.pass_check(
                f"Python {version_str} meets requirements",
                ["Minimum required: Python 3.11"]
            )
        elif version.major == 3 and version.minor >= 8:
            check.warn_check(
                f"Python {version_str} may work but 3.11+ recommended",
                [
                    "Some features may not work correctly",
                    "Recommendation: Upgrade to Python 3.11 or higher"
                ]
            )
        else:
            check.fail_check(
                f"Python {version_str} is too old",
                [
                    "Minimum required: Python 3.11",
                    f"Current version: {version_str}",
                    "Please upgrade Python from https://www.python.org/downloads/"
                ]
            )

        self.add_check(check)

    def check_python_path(self):
        """Check if Python is in PATH"""
        check = DiagnosticCheck("Python PATH", "Check if Python is accessible from command line")

        # Try different commands
        commands_to_try = ['python', 'py', 'python3']
        found_commands = []

        for cmd in commands_to_try:
            try:
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    found_commands.append(f"{cmd}: {result.stdout.strip()}")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        if found_commands:
            check.pass_check(
                "Python is accessible from command line",
                found_commands
            )
        else:
            check.warn_check(
                "Python not found in PATH",
                [
                    "Python is installed but not in PATH",
                    "Recommendation: Add Python to PATH or use 'py' launcher",
                    "The application may still work using sys.executable"
                ]
            )

        self.add_check(check)

    def check_pip(self):
        """Check pip installation"""
        check = DiagnosticCheck("pip Package Manager", "Verify pip is installed and working")

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                pip_version = result.stdout.strip()
                check.pass_check(
                    "pip is installed and working",
                    [pip_version]
                )
            else:
                check.fail_check(
                    "pip check failed",
                    [result.stderr.strip()]
                )
        except Exception as e:
            check.fail_check(
                "pip not found or not working",
                [
                    str(e),
                    "Try: python -m ensurepip --upgrade"
                ]
            )

        self.add_check(check)

    def check_venv_module(self):
        """Check if venv module is available"""
        check = DiagnosticCheck("venv Module", "Check if virtual environment module is available")

        try:
            import venv
            check.pass_check("venv module is available")
        except ImportError:
            check.fail_check(
                "venv module not found",
                [
                    "The venv module is required to create virtual environments",
                    "This should be included with Python 3.3+",
                    "You may need to reinstall Python"
                ]
            )

        self.add_check(check)

    def check_virtual_environment(self):
        """Check virtual environment status"""
        check = DiagnosticCheck("Virtual Environment", "Check if virtual environment exists and is activated")

        venv_path = Path('venv')

        if not venv_path.exists():
            check.fail_check(
                "Virtual environment not found",
                [
                    "Expected location: ./venv",
                    "Create with: python -m venv venv",
                    "Then activate with: .\\venv\\Scripts\\activate"
                ],
                fix_function=self.fix_create_venv
            )
        else:
            # Check if venv is valid
            python_exe = venv_path / 'Scripts' / 'python.exe'
            if python_exe.exists():
                # Check if currently activated
                if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
                    check.pass_check(
                        "Virtual environment exists and is activated",
                        [f"Location: {venv_path.absolute()}"]
                    )
                else:
                    check.warn_check(
                        "Virtual environment exists but not activated",
                        [
                            f"Location: {venv_path.absolute()}",
                            "Activate with: .\\venv\\Scripts\\activate",
                            "Note: This diagnostic can still run without activation"
                        ]
                    )
            else:
                check.fail_check(
                    "Virtual environment directory exists but appears corrupted",
                    [
                        f"Expected python.exe at: {python_exe}",
                        "Try deleting ./venv and recreating it"
                    ]
                )

        self.add_check(check)

    def check_dependencies(self):
        """Check if required dependencies are installed"""
        check = DiagnosticCheck("Dependencies", "Verify required Python packages are installed")

        required_packages = [
            'flask',
            'flask_wtf',
            'openai',
            'pypdf',
            'docx',
            'requests',
            'dotenv',
            'cryptography',
        ]

        # Windows-specific
        if sys.platform == 'win32':
            required_packages.extend(['magic', 'waitress'])

        missing = []
        installed = []

        for package in required_packages:
            try:
                __import__(package)
                installed.append(package)
            except ImportError:
                missing.append(package)

        if not missing:
            check.pass_check(
                "All required packages are installed",
                [f"Installed: {len(installed)} packages"]
            )
        elif len(missing) == len(required_packages):
            check.fail_check(
                "No packages installed - dependencies not installed",
                [
                    "Install with: pip install -r requirements.txt",
                    "Make sure virtual environment is activated"
                ],
                fix_function=self.fix_install_dependencies
            )
        else:
            check.fail_check(
                f"Missing {len(missing)} required package(s)",
                [f"Missing: {', '.join(missing)}"] +
                [f"Installed: {', '.join(installed)}"] +
                ["Run: pip install -r requirements.txt"],
                fix_function=self.fix_install_dependencies
            )

        self.add_check(check)

    def check_env_file(self):
        """Check if .env file exists"""
        check = DiagnosticCheck(".env File", "Check if configuration file exists")

        env_file = Path('.env')
        env_example = Path('.env.example')

        if env_file.exists():
            size = env_file.stat().st_size
            if size > 0:
                check.pass_check(
                    ".env file exists",
                    [f"Size: {size} bytes"]
                )
            else:
                check.warn_check(
                    ".env file exists but is empty",
                    [
                        "Copy from .env.example and fill in API keys",
                        f"Template available: {env_example}"
                    ]
                )
        else:
            if env_example.exists():
                check.warn_check(
                    ".env file not found",
                    [
                        "Create from template: copy .env.example .env",
                        "Then edit .env with your API keys"
                    ],
                    fix_function=self.fix_create_env
                )
            else:
                check.fail_check(
                    ".env file and .env.example both missing",
                    ["Project may be corrupted or incomplete"]
                )

        self.add_check(check)

    def check_env_configuration(self):
        """Check .env configuration"""
        check = DiagnosticCheck("Configuration", "Validate .env file settings")

        env_file = Path('.env')
        if not env_file.exists():
            check.fail_check(".env file does not exist - skipping validation")
            self.add_check(check)
            return

        try:
            # Parse .env file
            env_vars = {}
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()

            required_vars = ['ALMA_API_KEY', 'LITELLM_API_KEY', 'SECRET_KEY']
            missing = [var for var in required_vars if var not in env_vars or not env_vars[var]]

            warnings = []

            # Check for placeholder values
            for var in required_vars:
                if var in env_vars:
                    value = env_vars[var]
                    if 'your_' in value.lower() or 'example' in value.lower() or 'changeme' in value.lower():
                        warnings.append(f"{var} appears to be a placeholder value")

            if not missing and not warnings:
                check.pass_check(
                    "All required configuration variables are set",
                    [f"Configured: {', '.join(required_vars)}"]
                )
            elif missing:
                check.fail_check(
                    f"Missing required configuration: {', '.join(missing)}",
                    [
                        "Edit .env file and set these variables",
                        "See .env.example for template"
                    ]
                )
            else:
                check.warn_check(
                    "Configuration contains placeholder values",
                    warnings + ["Replace with actual API keys before running"]
                )

        except Exception as e:
            check.fail_check(
                f"Error reading .env file: {e}",
                ["Check file encoding (should be UTF-8)"]
            )

        self.add_check(check)

    def check_port_availability(self):
        """Check if default port is available"""
        check = DiagnosticCheck("Port Availability", "Check if port 5000 is available")

        port = 5000
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                check.pass_check(f"Port {port} is available")
        except OSError:
            # Check what's using it
            check.warn_check(
                f"Port {port} is already in use",
                [
                    "Another application is using port 5000",
                    "License Uploader will automatically use an alternative port",
                    "This is not critical but may cause confusion"
                ]
            )

        self.add_check(check)

    def check_file_permissions(self):
        """Check file system permissions"""
        check = DiagnosticCheck("File Permissions", "Check read/write permissions in project directory")

        test_file = Path('_permission_test.tmp')

        try:
            # Test write
            test_file.write_text("test", encoding='utf-8')
            # Test read
            content = test_file.read_text(encoding='utf-8')
            # Test delete
            test_file.unlink()

            if content == "test":
                check.pass_check("File system permissions are correct")
            else:
                check.fail_check("File read/write verification failed")
        except PermissionError as e:
            check.fail_check(
                "Permission denied in project directory",
                [
                    str(e),
                    "Try running as Administrator",
                    "Or move project to user directory (e.g., Documents)"
                ]
            )
        except Exception as e:
            check.fail_check(f"File permission test failed: {e}")
        finally:
            # Cleanup
            if test_file.exists():
                try:
                    test_file.unlink()
                except:
                    pass

        self.add_check(check)

    def check_tkinter(self):
        """Check if Tkinter is available"""
        check = DiagnosticCheck("Tkinter (GUI)", "Check if GUI components are available")

        try:
            import tkinter
            check.pass_check(
                "Tkinter is available",
                ["GUI launcher will work"]
            )
        except ImportError:
            check.warn_check(
                "Tkinter not available",
                [
                    "GUI launcher (start_license_uploader_gui.py) won't work",
                    "Use command-line launcher instead: python start_license_uploader.py",
                    "Tkinter usually comes with Python but may be missing in some distributions"
                ]
            )

        self.add_check(check)

    def check_antivirus_interference(self):
        """Check for potential antivirus interference"""
        check = DiagnosticCheck("Antivirus", "Check for Windows Defender or antivirus interference")

        # Check if Windows Defender is running
        try:
            result = subprocess.run(
                ['powershell', '-Command', 'Get-MpPreference | Select-Object -ExpandProperty DisableRealtimeMonitoring'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if 'True' in result.stdout:
                check.pass_check("Windows Defender real-time protection is disabled")
            elif 'False' in result.stdout:
                check.warn_check(
                    "Windows Defender real-time protection is enabled",
                    [
                        "This may slow down file operations",
                        "Consider adding project directory to exclusions",
                        "Run: Add-MpPreference -ExclusionPath 'C:\\path\\to\\license_uploader'",
                        "This is optional and not critical"
                    ]
                )
            else:
                check.warn_check(
                    "Could not determine Windows Defender status",
                    ["This is not critical"]
                )
        except Exception:
            check.warn_check(
                "Could not check Windows Defender status",
                ["This is not critical but antivirus may slow operations"]
            )

        self.add_check(check)

    # Fix functions

    def fix_create_venv(self):
        """Fix: Create virtual environment"""
        print(f"\n{Colors.BLUE}Creating virtual environment...{Colors.END}")
        try:
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
            print(f"{Colors.GREEN}✓ Virtual environment created successfully{Colors.END}")
            return True
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to create virtual environment: {e}{Colors.END}")
            return False

    def fix_install_dependencies(self):
        """Fix: Install dependencies"""
        print(f"\n{Colors.BLUE}Installing dependencies...{Colors.END}")
        print("This may take several minutes...")

        # Use venv python if available
        venv_python = Path('venv/Scripts/python.exe')
        python_exe = str(venv_python) if venv_python.exists() else sys.executable

        try:
            # Upgrade pip first
            print("Upgrading pip...")
            subprocess.run(
                [python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'],
                check=True
            )

            # Install requirements
            print("Installing requirements...")
            subprocess.run(
                [python_exe, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                check=True
            )

            print(f"{Colors.GREEN}✓ Dependencies installed successfully{Colors.END}")
            return True
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to install dependencies: {e}{Colors.END}")
            return False

    def fix_create_env(self):
        """Fix: Create .env file from template"""
        print(f"\n{Colors.BLUE}Creating .env file from template...{Colors.END}")
        try:
            import shutil
            shutil.copy('.env.example', '.env')
            print(f"{Colors.GREEN}✓ .env file created{Colors.END}")
            print(f"{Colors.YELLOW}⚠ Remember to edit .env and add your API keys{Colors.END}")
            return True
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to create .env file: {e}{Colors.END}")
            return False

    def save_report(self):
        """Save diagnostic report to file"""
        report_file = Path('diagnostic_report.txt')

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("="*70 + "\n")
                f.write("License Uploader - Windows Diagnostic Report\n")
                f.write("="*70 + "\n\n")
                f.write(f"Platform: {platform.system()} {platform.release()} ({platform.version()})\n")
                f.write(f"Architecture: {platform.machine()}\n")
                f.write(f"Python: {sys.version}\n")
                f.write(f"\nTotal Checks: {sum(self.summary.values())}\n")
                f.write(f"Passed: {self.summary['pass']}\n")
                f.write(f"Warnings: {self.summary['warn']}\n")
                f.write(f"Failed: {self.summary['fail']}\n")
                f.write("\n" + "="*70 + "\n\n")

                for check in self.checks:
                    f.write(f"[{check.status}] {check.name}\n")
                    f.write(f"  {check.description}\n")
                    if check.message:
                        f.write(f"  → {check.message}\n")
                    for detail in check.details:
                        f.write(f"    • {detail}\n")
                    f.write("\n")

            print(f"\n{Colors.BLUE}ℹ Diagnostic report saved to: {report_file.absolute()}{Colors.END}")

        except Exception as e:
            print(f"\n{Colors.YELLOW}⚠ Could not save diagnostic report: {e}{Colors.END}")

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='License Uploader Windows Diagnostic Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python diagnose_windows.py              Run diagnostics
  python diagnose_windows.py --fix        Run diagnostics and attempt automatic fixes
  python diagnose_windows.py --help       Show this help message
        """
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to automatically fix detected issues'
    )

    args = parser.parse_args()

    # Run diagnostics
    diagnostics = WindowsDiagnostics()
    diagnostics.run_diagnostics()

    # Apply fixes if requested
    if args.fix:
        print("\n" + "="*70)
        print(f"{Colors.BOLD}AUTOMATIC FIXES{Colors.END}")
        print("="*70)

        fixable = [c for c in diagnostics.checks if c.fix_available and c.status in ['FAIL', 'WARN']]

        if not fixable:
            print(f"\n{Colors.GREEN}No fixes needed!{Colors.END}")
        else:
            print(f"\nAttempting to fix {len(fixable)} issue(s)...\n")

            for check in fixable:
                print(f"Fixing: {check.name}")
                if check.fix_function:
                    success = check.fix_function()
                    if not success:
                        print(f"  {Colors.YELLOW}Manual intervention may be required{Colors.END}")

            print(f"\n{Colors.BLUE}ℹ Run diagnostics again to verify fixes{Colors.END}")

    # Exit code based on results
    if diagnostics.summary['fail'] > 0:
        return 1
    elif diagnostics.summary['warn'] > 0:
        return 0
    else:
        return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Diagnostic cancelled by user{Colors.END}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
