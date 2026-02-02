#!/usr/bin/env python3
"""
License Uploader - Easy Launcher
Automatically handles port conflicts and opens the application in your browser
"""

import os
import sys
import time
import socket
import signal
import subprocess
import webbrowser
from pathlib import Path

def print_header():
    """Print a friendly welcome message"""
    print("\n" + "="*60)
    print("   📚 LICENSE UPLOADER - Starting Application")
    print("="*60 + "\n")

def find_available_port(start_port=5000, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

def kill_process_on_port(port):
    """Kill any process using the specified port"""
    try:
        if sys.platform == 'win32':
            # Windows
            cmd = f'netstat -ano | findstr :{port}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
        else:
            # Linux/Mac
            cmd = f'lsof -ti :{port}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        try:
                            os.kill(int(pid), signal.SIGTERM)
                            time.sleep(0.5)
                            os.kill(int(pid), signal.SIGKILL)
                        except ProcessLookupError:
                            pass
        return True
    except Exception as e:
        return False

def check_environment():
    """Check if the environment is properly set up"""
    venv_path = Path('venv')

    if not venv_path.exists():
        print("❌ Error: Virtual environment not found!")
        print("\n   Please run the installation first:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # Linux/Mac")
        print("   venv\\Scripts\\activate     # Windows")
        print("   pip install -r requirements.txt")
        return False

    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("   The application will use default settings.")
        print("   Copy .env.example to .env and configure your API keys.\n")

    return True

def start_application():
    """Start the License Uploader application"""
    print_header()

    # Check environment
    if not check_environment():
        input("\nPress Enter to exit...")
        return

    # Find available port
    print("🔍 Checking for available port...")
    port = find_available_port(5000)

    if port is None:
        print("❌ Error: No available ports found (tried 5000-5009)")
        print("   Please close some applications and try again.")
        input("\nPress Enter to exit...")
        return

    if port != 5000:
        print(f"ℹ️  Port 5000 was in use, using port {port} instead")
        # Kill the process on 5000 and use 5000
        print("🔧 Cleaning up port 5000...")
        if kill_process_on_port(5000):
            port = 5000
            time.sleep(1)

    print(f"✅ Starting License Uploader on port {port}...")

    # Set environment variables
    env = os.environ.copy()
    env['FLASK_RUN_PORT'] = str(port)

    # Determine Python executable
    if sys.platform == 'win32':
        python_exe = Path('venv/Scripts/python.exe')
    else:
        python_exe = Path('venv/bin/python')

    if not python_exe.exists():
        python_exe = sys.executable

    # Start the Flask application
    try:
        # Start Flask in a subprocess
        process = subprocess.Popen(
            [str(python_exe), 'app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Wait for the server to start
        print("\n⏳ Starting server (this may take a few seconds)...")
        time.sleep(3)

        # Check if the server is running
        url = f"http://localhost:{port}"
        try:
            import urllib.request
            urllib.request.urlopen(url, timeout=2)
            print(f"\n✅ SUCCESS! License Uploader is running!\n")
            print("="*60)
            print(f"   🌐 Open in browser: {url}")
            print("="*60)
            print("\n📝 Instructions:")
            print("   1. Your browser will open automatically in a moment")
            print("   2. Upload a license document (PDF, DOCX, or TXT)")
            print("   3. Review and edit the extracted terms")
            print("   4. Submit to Alma")
            print("\n⚠️  To stop the server: Close this window or press Ctrl+C")
            print("="*60 + "\n")

            # Open browser
            time.sleep(2)
            print("🌐 Opening browser...")
            webbrowser.open(url)

            # Keep the process running and show output
            print("\n📋 Server Log (latest messages):")
            print("-"*60)
            try:
                for line in process.stdout:
                    print(line.rstrip())
            except KeyboardInterrupt:
                print("\n\n🛑 Shutting down License Uploader...")
                process.terminate()
                process.wait(timeout=5)
                print("✅ Application stopped successfully.")

        except Exception as e:
            print(f"\n❌ Error: Could not connect to server")
            print(f"   Details: {e}")
            process.terminate()

    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure you've installed all requirements: pip install -r requirements.txt")
        print("  2. Check that your .env file is configured correctly")
        print("  3. Try running: python app.py")

    input("\nPress Enter to exit...")

if __name__ == '__main__':
    try:
        start_application()
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)
