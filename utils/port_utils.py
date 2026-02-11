"""
Cross-platform utilities for port management using psutil
"""
import socket
import time
from typing import Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def is_port_in_use(port: int, host: str = '127.0.0.1') -> bool:
    """
    Check if a port is in use

    Args:
        port: Port number to check
        host: Host address (default: 127.0.0.1)

    Returns:
        True if port is in use, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return False
    except OSError:
        return True


def find_available_port(start_port: int = 5000, max_attempts: int = 10) -> Optional[int]:
    """
    Find an available port starting from start_port

    Args:
        start_port: Port number to start searching from
        max_attempts: Maximum number of ports to try

    Returns:
        Available port number, or None if no port found
    """
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            return port
    return None


def kill_process_on_port(port: int) -> bool:
    """
    Kill any process using the specified port (cross-platform)

    Args:
        port: Port number to free up

    Returns:
        True if a process was killed, False otherwise
    """
    if not PSUTIL_AVAILABLE:
        # If psutil is not available, can't kill processes reliably
        return False

    try:
        # Find all network connections
        for conn in psutil.net_connections(kind='inet'):
            # Check if this connection is using our port and is listening
            if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                try:
                    # Get the process using this port
                    process = psutil.Process(conn.pid)
                    # Terminate it gracefully
                    process.terminate()
                    # Wait a moment for graceful termination
                    time.sleep(0.5)
                    # Force kill if still running
                    if process.is_running():
                        process.kill()
                    return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process already gone or we don't have permission
                    continue
        return False
    except Exception:
        # If anything goes wrong, return False
        return False


def wait_for_port_available(port: int, timeout: float = 5.0) -> bool:
    """
    Wait for a port to become available

    Args:
        port: Port number to wait for
        timeout: Maximum time to wait in seconds

    Returns:
        True if port became available, False if timeout
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not is_port_in_use(port):
            return True
        time.sleep(0.1)
    return False


def get_process_info_on_port(port: int) -> Optional[dict]:
    """
    Get information about the process using a port

    Args:
        port: Port number to check

    Returns:
        Dictionary with process info, or None if no process found
    """
    if not PSUTIL_AVAILABLE:
        return None

    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port:
                try:
                    process = psutil.Process(conn.pid)
                    return {
                        'pid': conn.pid,
                        'name': process.name(),
                        'status': conn.status,
                        'cmdline': ' '.join(process.cmdline()) if process.cmdline() else None
                    }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        return None
    except Exception:
        return None
