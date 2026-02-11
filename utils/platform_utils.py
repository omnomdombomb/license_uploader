"""
Cross-platform utilities for platform detection and path handling
"""
import sys
from pathlib import Path
from typing import Optional


def is_windows() -> bool:
    """Check if running on Windows"""
    return sys.platform == 'win32'


def is_linux() -> bool:
    """Check if running on Linux"""
    return sys.platform.startswith('linux')


def is_macos() -> bool:
    """Check if running on macOS"""
    return sys.platform == 'darwin'


def get_platform_name() -> str:
    """Get human-readable platform name"""
    if is_windows():
        return "Windows"
    elif is_linux():
        return "Linux"
    elif is_macos():
        return "macOS"
    else:
        return sys.platform


def get_venv_python() -> Path:
    """
    Get the path to the Python executable in the virtual environment

    Returns:
        Path object pointing to the venv Python executable for this platform
    """
    venv_base = Path('venv')

    if is_windows():
        return venv_base / 'Scripts' / 'python.exe'
    else:
        # Linux and macOS
        return venv_base / 'bin' / 'python'


def get_venv_activate_script() -> Path:
    """
    Get the path to the virtual environment activation script

    Returns:
        Path object pointing to the activation script for this platform
    """
    venv_base = Path('venv')

    if is_windows():
        return venv_base / 'Scripts' / 'activate.bat'
    else:
        # Linux and macOS
        return venv_base / 'bin' / 'activate'


def get_current_python() -> Path:
    """
    Get the current Python executable path

    Returns:
        Path object pointing to the current Python executable
    """
    return Path(sys.executable)


def find_python_executable() -> Optional[Path]:
    """
    Find the best Python executable to use

    Priority:
    1. Virtual environment Python (if exists)
    2. Current Python executable

    Returns:
        Path to Python executable, or None if not found
    """
    # Try virtual environment first
    venv_python = get_venv_python()
    if venv_python.exists():
        return venv_python

    # Fall back to current Python
    current = get_current_python()
    if current.exists():
        return current

    return None


def check_tkinter_available() -> bool:
    """
    Check if Tkinter (GUI) is available

    Returns:
        True if Tkinter can be imported, False otherwise
    """
    try:
        import tkinter
        # Try to create a root window to verify it works
        root = tkinter.Tk()
        root.withdraw()
        root.destroy()
        return True
    except (ImportError, Exception):
        return False
