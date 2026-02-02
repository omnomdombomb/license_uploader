#!/usr/bin/env python3
"""
License Uploader - GUI Launcher
Simple graphical interface to start and stop the License Uploader application
"""

import os
import sys
import time
import socket
import signal
import subprocess
import webbrowser
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path
import threading

class LicenseUploaderLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("License Uploader Launcher")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        self.process = None
        self.port = 5000
        self.url = f"http://localhost:{self.port}"

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface"""
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="📚 License Uploader",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=20)

        # Main content
        content_frame = tk.Frame(self.root, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Status label
        self.status_label = tk.Label(
            content_frame,
            text="Ready to start",
            font=("Arial", 12),
            fg="#27ae60"
        )
        self.status_label.pack(pady=10)

        # Buttons frame
        button_frame = tk.Frame(content_frame)
        button_frame.pack(pady=10)

        # Start button
        self.start_button = tk.Button(
            button_frame,
            text="▶ Start Application",
            command=self.start_application,
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Stop button
        self.stop_button = tk.Button(
            button_frame,
            text="⬛ Stop Application",
            command=self.stop_application,
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            padx=20,
            pady=10,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Open browser button
        self.browser_button = tk.Button(
            button_frame,
            text="🌐 Open in Browser",
            command=self.open_browser,
            font=("Arial", 12),
            bg="#3498db",
            fg="white",
            padx=20,
            pady=10,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.browser_button.pack(side=tk.LEFT, padx=5)

        # URL display
        url_frame = tk.Frame(content_frame)
        url_frame.pack(pady=10, fill=tk.X)

        tk.Label(url_frame, text="Application URL:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.url_label = tk.Label(
            url_frame,
            text=self.url,
            font=("Arial", 10, "bold"),
            fg="#3498db",
            cursor="hand2"
        )
        self.url_label.pack(side=tk.LEFT, padx=5)
        self.url_label.bind("<Button-1>", lambda e: self.open_browser())

        # Log area
        log_label = tk.Label(content_frame, text="Server Log:", font=("Arial", 10, "bold"))
        log_label.pack(anchor=tk.W, pady=(10, 5))

        self.log_text = scrolledtext.ScrolledText(
            content_frame,
            height=12,
            font=("Courier", 9),
            bg="#f8f9fa",
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Footer
        footer_label = tk.Label(
            self.root,
            text="Close this window to stop the application",
            font=("Arial", 9),
            fg="#7f8c8d",
            pady=10
        )
        footer_label.pack(side=tk.BOTTOM)

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log(self, message, level="INFO"):
        """Add a message to the log"""
        timestamp = time.strftime("%H:%M:%S")
        colors = {
            "INFO": "#2c3e50",
            "SUCCESS": "#27ae60",
            "WARNING": "#f39c12",
            "ERROR": "#e74c3c"
        }

        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def find_available_port(self, start_port=5000):
        """Find an available port"""
        for port in range(start_port, start_port + 10):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        return None

    def kill_process_on_port(self, port):
        """Kill process using the specified port"""
        try:
            if sys.platform == 'win32':
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
                cmd = f'lsof -ti :{port}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.stdout:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            os.kill(int(pid), signal.SIGKILL)
            return True
        except Exception:
            return False

    def start_application(self):
        """Start the Flask application"""
        self.log("Starting License Uploader...")

        # Check environment
        if not Path('venv').exists():
            messagebox.showerror(
                "Error",
                "Virtual environment not found!\n\n"
                "Please run installation first:\n"
                "python -m venv venv\n"
                "pip install -r requirements.txt"
            )
            return

        # Find available port
        self.port = self.find_available_port(5000)
        if self.port is None:
            messagebox.showerror("Error", "No available ports found (tried 5000-5009)")
            return

        if self.port != 5000:
            self.log(f"Port 5000 in use, cleaning up...")
            if self.kill_process_on_port(5000):
                self.port = 5000
                time.sleep(1)

        self.url = f"http://localhost:{self.port}"
        self.url_label.config(text=self.url)

        # Start Flask
        if sys.platform == 'win32':
            python_exe = Path('venv/Scripts/python.exe')
        else:
            python_exe = Path('venv/bin/python')

        env = os.environ.copy()
        env['FLASK_RUN_PORT'] = str(self.port)

        try:
            self.process = subprocess.Popen(
                [str(python_exe), 'app.py'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Update UI
            self.status_label.config(text="Starting...", fg="#f39c12")
            self.start_button.config(state=tk.DISABLED)

            # Wait for server to start
            def wait_for_server():
                time.sleep(3)
                try:
                    import urllib.request
                    urllib.request.urlopen(self.url, timeout=2)
                    self.root.after(0, self.on_server_started)
                except Exception as e:
                    self.root.after(0, lambda: self.on_server_error(str(e)))

            threading.Thread(target=wait_for_server, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start application:\n{e}")
            self.log(f"ERROR: {e}", "ERROR")

    def on_server_started(self):
        """Called when server successfully starts"""
        self.status_label.config(text="✓ Running", fg="#27ae60")
        self.stop_button.config(state=tk.NORMAL)
        self.browser_button.config(state=tk.NORMAL)
        self.log("Application started successfully!", "SUCCESS")
        self.log(f"Access at: {self.url}", "SUCCESS")

        # Auto-open browser
        webbrowser.open(self.url)

    def on_server_error(self, error):
        """Called when server fails to start"""
        self.status_label.config(text="✗ Failed to start", fg="#e74c3c")
        self.start_button.config(state=tk.NORMAL)
        self.log(f"ERROR: {error}", "ERROR")
        if self.process:
            self.process.terminate()

    def stop_application(self):
        """Stop the Flask application"""
        if self.process:
            self.log("Stopping application...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

        self.status_label.config(text="Stopped", fg="#7f8c8d")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.browser_button.config(state=tk.DISABLED)
        self.log("Application stopped", "INFO")

    def open_browser(self):
        """Open the application in the default browser"""
        webbrowser.open(self.url)
        self.log(f"Opening {self.url} in browser...")

    def on_closing(self):
        """Handle window close"""
        if self.process:
            if messagebox.askokcancel("Quit", "Stop the application and quit?"):
                self.stop_application()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = LicenseUploaderLauncher(root)
    root.mainloop()

if __name__ == '__main__':
    main()
