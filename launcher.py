#!/usr/bin/env python3
"""
License Uploader - Universal Cross-Platform Launcher
Works on Windows, Linux, and macOS

Automatically selects GUI or CLI mode based on availability.
"""

import os
import sys
import time
import subprocess
import webbrowser
import argparse
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.platform_utils import (
    get_venv_python,
    find_python_executable,
    get_platform_name
)
from utils.port_utils import (
    find_available_port,
    kill_process_on_port,
    is_port_in_use,
    wait_for_port_available
)

try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init()  # Initialize colorama for Windows color support
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Define dummy color constants
    class Fore:
        GREEN = YELLOW = RED = BLUE = CYAN = ''
    class Style:
        RESET_ALL = BRIGHT = ''


def print_colored(message: str, color: str = ''):
    """Print a colored message if colors are available"""
    if COLORS_AVAILABLE:
        print(f"{color}{message}{Style.RESET_ALL}")
    else:
        print(message)


def print_header():
    """Print a friendly welcome message"""
    print("\n" + "="*60)
    print_colored("   📚 LICENSE UPLOADER - Starting Application", Fore.CYAN + Style.BRIGHT)
    print_colored(f"   Platform: {get_platform_name()}", Fore.BLUE)
    print("="*60 + "\n")


def check_environment() -> bool:
    """
    Check if the environment is properly set up

    Returns:
        True if environment is ready, False otherwise
    """
    venv_python = get_venv_python()

    if not venv_python.exists():
        print_colored("❌ Error: Virtual environment not found!", Fore.RED)
        print("\n   Please run the installation first:")
        if sys.platform == 'win32':
            print("   >> Double-click: INSTALL_WINDOWS.bat")
            print("\n   Or manually:")
            print("   1. Open Command Prompt")
            print("   2. Navigate to this folder")
            print("   3. Run: python -m venv venv")
            print("   4. Run: venv\\Scripts\\activate")
            print("   5. Run: pip install -r requirements.txt")
        else:
            print("   >> Run: ./install.sh")
            print("\n   Or manually:")
            print("   1. Open Terminal")
            print("   2. Navigate to this folder")
            print("   3. Run: python3 -m venv venv")
            print("   4. Run: source venv/bin/activate")
            print("   5. Run: pip install -r requirements.txt")
        return False

    env_file = Path('.env')
    if not env_file.exists():
        print_colored("⚠️  Warning: .env file not found!", Fore.YELLOW)
        print("   The application will use default settings.")
        print("   Copy .env.example to .env and configure your API keys.\n")

    return True


def prepare_port(preferred_port: int = 5000) -> int:
    """
    Prepare a port for the application

    Args:
        preferred_port: Preferred port to use

    Returns:
        Available port number
    """
    print_colored("🔍 Checking for available port...", Fore.BLUE)

    # Check if preferred port is available
    if not is_port_in_use(preferred_port):
        print_colored(f"✅ Port {preferred_port} is available", Fore.GREEN)
        return preferred_port

    # Try to kill process on preferred port
    print_colored(f"ℹ️  Port {preferred_port} is in use, attempting to free it...", Fore.YELLOW)
    if kill_process_on_port(preferred_port):
        print_colored("🔧 Freed up port, waiting for availability...", Fore.BLUE)
        if wait_for_port_available(preferred_port, timeout=3):
            print_colored(f"✅ Port {preferred_port} is now available", Fore.GREEN)
            return preferred_port

    # Find alternative port
    print_colored("🔍 Looking for alternative port...", Fore.BLUE)
    port = find_available_port(preferred_port)
    if port is None:
        print_colored(f"❌ Error: No available ports found (tried {preferred_port}-{preferred_port+9})", Fore.RED)
        print("   Please close some applications and try again.")
        return None

    print_colored(f"✅ Using alternative port {port}", Fore.GREEN)
    return port


def start_flask_app(port: int) -> subprocess.Popen:
    """
    Start the Flask application

    Args:
        port: Port number to use

    Returns:
        subprocess.Popen object for the Flask process
    """
    python_exe = find_python_executable()
    if not python_exe:
        raise RuntimeError("Could not find Python executable")

    # Set environment variables
    env = os.environ.copy()
    env['FLASK_RUN_PORT'] = str(port)

    print_colored(f"✅ Starting License Uploader on port {port}...", Fore.GREEN)

    # Start Flask in a subprocess
    process = subprocess.Popen(
        [str(python_exe), 'app.py'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    return process


def wait_for_server(port: int, timeout: int = 10) -> bool:
    """
    Wait for the Flask server to start

    Args:
        port: Port number where server should start
        timeout: Maximum time to wait in seconds

    Returns:
        True if server started successfully, False otherwise
    """
    print_colored("\n⏳ Starting server (this may take a few seconds)...", Fore.BLUE)

    url = f"http://localhost:{port}"
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            import urllib.request
            urllib.request.urlopen(url, timeout=2)
            return True
        except Exception:
            time.sleep(0.5)

    return False


def launch_cli_mode(port: int):
    """
    Launch in CLI mode

    Args:
        port: Port number where server is running
    """
    url = f"http://localhost:{port}"

    print_colored(f"\n✅ SUCCESS! License Uploader is running!\n", Fore.GREEN + Style.BRIGHT)
    print("="*60)
    print_colored(f"   🌐 Open in browser: {url}", Fore.CYAN)
    print("="*60)
    print("\n📝 Instructions:")
    print("   1. Your browser will open automatically in a moment")
    print("   2. Upload a license document (PDF, DOCX, or TXT)")
    print("   3. Review and edit the extracted terms")
    print("   4. Submit to Alma")
    print_colored("\n⚠️  To stop the server: Press Ctrl+C", Fore.YELLOW)
    print("="*60 + "\n")

    # Open browser
    time.sleep(2)
    print_colored("🌐 Opening browser...", Fore.BLUE)
    try:
        webbrowser.open(url)
    except Exception as e:
        print_colored(f"⚠️  Could not open browser automatically: {e}", Fore.YELLOW)
        print(f"   Please open manually: {url}")


def run_server_loop(process: subprocess.Popen):
    """
    Keep the server running and display output

    Args:
        process: Flask subprocess
    """
    print("\n📋 Server Log (latest messages):")
    print("-"*60)

    try:
        for line in process.stdout:
            print(line.rstrip())
    except KeyboardInterrupt:
        print_colored("\n\n🛑 Shutting down License Uploader...", Fore.YELLOW)
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print_colored("✅ Application stopped successfully.", Fore.GREEN)


def main():
    """Main launcher function"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='License Uploader Launcher')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on (default: 5000)')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    args = parser.parse_args()

    try:
        # Print header
        print_header()

        # Check environment
        if not check_environment():
            input("\nPress Enter to exit...")
            return 1

        # Prepare port
        port = prepare_port(args.port)
        if port is None:
            input("\nPress Enter to exit...")
            return 1

        # Start Flask application
        try:
            process = start_flask_app(port)
        except Exception as e:
            print_colored(f"\n❌ Error starting application: {e}", Fore.RED)
            print("\nTroubleshooting:")
            print("  1. Make sure you've installed all requirements: pip install -r requirements.txt")
            print("  2. Check that your .env file is configured correctly")
            print("  3. Try running: python app.py")
            input("\nPress Enter to exit...")
            return 1

        # Wait for server to start
        if not wait_for_server(port, timeout=10):
            print_colored("\n❌ Error: Could not connect to server", Fore.RED)
            print("   The server may have failed to start. Check for errors above.")
            process.terminate()
            input("\nPress Enter to exit...")
            return 1

        if not args.no_browser:
            launch_cli_mode(port)

        # Run server loop
        run_server_loop(process)

        return 0

    except KeyboardInterrupt:
        print_colored("\n\n👋 Application stopped by user", Fore.YELLOW)
        return 0
    except Exception as e:
        print_colored(f"\n❌ Unexpected error: {e}", Fore.RED)
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        return 1


if __name__ == '__main__':
    sys.exit(main())
