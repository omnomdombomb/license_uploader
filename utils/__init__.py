"""
Cross-platform utility modules for License Uploader
"""

from .platform_utils import (
    get_venv_python,
    is_windows,
    is_linux,
    is_macos,
    get_platform_name
)

from .port_utils import (
    find_available_port,
    kill_process_on_port,
    is_port_in_use
)

__all__ = [
    'get_venv_python',
    'is_windows',
    'is_linux',
    'is_macos',
    'get_platform_name',
    'find_available_port',
    'kill_process_on_port',
    'is_port_in_use',
]
