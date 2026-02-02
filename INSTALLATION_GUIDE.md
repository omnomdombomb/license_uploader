# License Uploader - Installation Guide

## Table of Contents

- [Prerequisites](#prerequisites)
- [Platform-Specific Installation](#platform-specific-installation)
  - [Windows 10/11 Installation](#windows-1011-installation)
  - [macOS 12+ Installation](#macos-12-installation)
  - [Linux (Ubuntu 20.04+) Installation](#linux-ubuntu-2004-installation)
- [Virtual Environment Setup](#virtual-environment-setup)
- [Dependency Installation](#dependency-installation)
- [Configuration Setup](#configuration-setup)
- [Verification Steps](#verification-steps)
- [Common Installation Issues](#common-installation-issues)
- [Next Steps](#next-steps)

---

## Prerequisites

### Required Software

All platforms require:

- **Python 3.11 or higher**
  - Python 3.11, 3.12, or 3.13 recommended
  - Check version: `python --version` or `python3 --version`
  - Download: https://www.python.org/downloads/

- **pip** (Python package manager)
  - Usually included with Python
  - Check version: `pip --version` or `pip3 --version`

- **Git** (optional, for cloning repository)
  - Download: https://git-scm.com/downloads
  - Or download ZIP from repository

### System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **RAM** | 2 GB | 4 GB+ |
| **Disk Space** | 500 MB | 1 GB+ |
| **CPU** | Dual-core | Quad-core+ |
| **Network** | Broadband internet (for AI and Alma APIs) | |

### Platform-Specific Requirements

**Windows:**
- Windows 10 or Windows 11 (64-bit)
- PowerShell or Command Prompt
- Administrator rights (for some installations)

**macOS:**
- macOS 12 (Monterey) or higher
- Homebrew package manager (recommended)
- Xcode Command Line Tools

**Linux:**
- Ubuntu 20.04 LTS or higher (or equivalent Debian-based)
- Other distributions: Fedora, CentOS, Arch (adapt commands accordingly)
- sudo privileges

---

## Platform-Specific Installation

Choose your operating system and follow the corresponding instructions.

---

## Windows 10/11 Installation

### Step 1: Install Python

1. **Download Python 3.11+**
   - Visit: https://www.python.org/downloads/windows/
   - Download: "Windows installer (64-bit)"

2. **Run the installer**
   - ✅ **IMPORTANT**: Check "Add Python to PATH"
   - Click "Install Now"
   - Wait for installation to complete
   - Click "Close"

3. **Verify installation**
   ```powershell
   python --version
   ```
   Expected output: `Python 3.11.x` or higher

### Step 2: Install Git (Optional)

1. **Download Git for Windows**
   - Visit: https://git-scm.com/download/win
   - Download and run installer
   - Use default options

2. **Verify installation**
   ```powershell
   git --version
   ```

### Step 3: Get the Application Code

**Option A: Clone with Git**
```powershell
cd C:\Users\YourUsername\Documents
git clone <repository-url> license_uploader
cd license_uploader
```

**Option B: Download ZIP**
1. Download ZIP from repository
2. Extract to desired location (e.g., `C:\Users\YourUsername\Documents\license_uploader`)
3. Open PowerShell in that directory

### Step 4: Create Virtual Environment

```powershell
# Navigate to project directory
cd C:\Users\YourUsername\Documents\license_uploader

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# You should see (venv) in your prompt
```

### Step 5: Install Dependencies

```powershell
# Upgrade pip first (recommended)
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

**This will install:**
- Flask web framework
- python-magic-bin (Windows-specific file type detection)
- waitress (Windows WSGI server)
- pypdf, python-docx (document parsing)
- openai, httpx (AI integration)
- All other dependencies

**Installation time**: 2-5 minutes depending on internet speed

### Step 6: Configure Environment Variables

1. **Copy example .env file**
   ```powershell
   copy .env.example .env
   ```

2. **Edit .env file**
   ```powershell
   notepad .env
   ```

3. **Fill in your API keys** (see [Configuration Setup](#configuration-setup) section)

4. **Save and close**

### Step 7: Verify Installation

```powershell
# Run the application
python app.py
```

Expected output:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Open browser to: http://localhost:5000

### Windows-Specific Notes

**PowerShell Execution Policy:**
If you get an error activating the virtual environment:
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows Defender:**
- Windows Defender may slow down file operations
- Consider adding exclusion for project directory (optional)
- Settings > Update & Security > Windows Security > Virus & threat protection > Exclusions

**Performance:**
- Windows has slower file I/O than Linux/macOS
- See DEPLOYMENT_GUIDE.md for Windows performance optimizations (RAM disk, etc.)

---

## macOS 12+ Installation

### Step 1: Install Xcode Command Line Tools

```bash
xcode-select --install
```

Click "Install" in the popup dialog.

### Step 2: Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the on-screen instructions.

### Step 3: Install Python 3.11+

```bash
# Install Python
brew install python@3.11

# Verify installation
python3 --version
```

Expected output: `Python 3.11.x` or higher

### Step 4: Install libmagic (Required)

```bash
brew install libmagic
```

**Why**: macOS needs the native `libmagic` library for file type detection.

### Step 5: Install Git (if not already installed)

```bash
brew install git
```

### Step 6: Get the Application Code

**Option A: Clone with Git**
```bash
cd ~/Documents
git clone <repository-url> license_uploader
cd license_uploader
```

**Option B: Download ZIP**
1. Download ZIP from repository
2. Extract to desired location (e.g., `~/Documents/license_uploader`)
3. Open Terminal in that directory

### Step 7: Create Virtual Environment

```bash
# Navigate to project directory
cd ~/Documents/license_uploader

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt
```

### Step 8: Install Dependencies

```bash
# Upgrade pip first (recommended)
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

**This will install:**
- Flask web framework
- python-magic (macOS-specific, uses libmagic)
- gunicorn (Unix WSGI server)
- pypdf, python-docx (document parsing)
- openai, httpx (AI integration)
- All other dependencies

**Installation time**: 2-5 minutes

### Step 9: Configure Environment Variables

```bash
# Copy example .env file
cp .env.example .env

# Edit .env file
nano .env
# Or use your preferred editor: vim, TextEdit, VS Code, etc.
```

Fill in your API keys (see [Configuration Setup](#configuration-setup) section)

Save: Ctrl+O, Enter, Ctrl+X (in nano)

### Step 10: Verify Installation

```bash
# Run the application
python app.py
```

Expected output:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Open browser to: http://localhost:5000

### macOS-Specific Notes

**Apple Silicon (M1/M2/M3):**
- All dependencies support ARM architecture
- Installation may take slightly longer due to compilation
- Performance is excellent on Apple Silicon

**Rosetta 2:**
- Not required for Python 3.11+
- All dependencies have native ARM builds

**Firewall:**
- macOS may prompt to allow Python to accept incoming connections
- Click "Allow" for local development

---

## Linux (Ubuntu 20.04+) Installation

### Step 1: Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Install Python 3.11+

**Ubuntu 22.04+ (Python 3.11 available):**
```bash
sudo apt install -y python3.11 python3.11-venv python3.11-dev
```

**Ubuntu 20.04 (requires PPA):**
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev
```

**Verify installation:**
```bash
python3.11 --version
```

### Step 3: Install Required System Libraries

```bash
sudo apt install -y \
    libmagic1 \
    libmagic-dev \
    git \
    build-essential \
    libssl-dev \
    libffi-dev
```

**Package purposes:**
- `libmagic1`: File type detection library
- `libmagic-dev`: Development headers
- `git`: Version control
- `build-essential`: Compilers for Python packages
- `libssl-dev`, `libffi-dev`: Cryptography dependencies

### Step 4: Get the Application Code

**Option A: Clone with Git**
```bash
cd ~
git clone <repository-url> license_uploader
cd license_uploader
```

**Option B: Download ZIP**
```bash
cd ~
wget <repository-zip-url> -O license_uploader.zip
unzip license_uploader.zip
cd license_uploader
```

### Step 5: Create Virtual Environment

```bash
# Navigate to project directory
cd ~/license_uploader

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt
```

### Step 6: Install Dependencies

```bash
# Upgrade pip first (recommended)
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

**This will install:**
- Flask web framework
- python-magic (Linux-specific, uses libmagic1)
- gunicorn (Unix WSGI server)
- pypdf, python-docx (document parsing)
- openai, httpx (AI integration)
- All other dependencies

**Installation time**: 2-5 minutes

### Step 7: Configure Environment Variables

```bash
# Copy example .env file
cp .env.example .env

# Edit .env file
nano .env
# Or use your preferred editor: vim, gedit, etc.
```

Fill in your API keys (see [Configuration Setup](#configuration-setup) section)

Save: Ctrl+O, Enter, Ctrl+X (in nano)

### Step 8: Verify Installation

```bash
# Run the application
python app.py
```

Expected output:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Open browser to: http://localhost:5000

### Linux-Specific Notes

**SELinux (Fedora/CentOS):**
If using SELinux, you may need to set proper contexts:
```bash
sudo semanage fcontext -a -t httpd_sys_content_t "/path/to/license_uploader(/.*)?"
sudo restorecon -Rv /path/to/license_uploader
```

**Firewall:**
If running on a server, allow port 5000 (development) or 80/443 (production):
```bash
sudo ufw allow 5000/tcp
```

**Other Distributions:**
- **Fedora/CentOS**: Use `dnf` instead of `apt`, install `python3-devel`, `file-devel`
- **Arch**: Use `pacman`, install `python`, `file`, `gcc`

---

## Virtual Environment Setup

### Why Use a Virtual Environment?

- **Isolation**: Keeps project dependencies separate from system Python
- **Version control**: Pin specific package versions
- **Portability**: Easy to recreate environment on other machines
- **No conflicts**: Avoid package version conflicts with other projects

### Creating Virtual Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Activating Virtual Environment

**Always activate before working on the project:**

**Windows:**
```powershell
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Confirmation**: You should see `(venv)` prefix in your terminal prompt.

### Deactivating Virtual Environment

When you're done:
```bash
deactivate
```

### Deleting and Recreating Virtual Environment

If you encounter issues:

**Windows:**
```powershell
deactivate
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Dependency Installation

### Requirements File

The `requirements.txt` file contains all Python dependencies with version pins:

```
# Core Flask dependencies (cross-platform)
flask==3.0.0
Flask-WTF==1.2.1
flask-talisman==1.1.0
flask-limiter==3.8.0

# AI/ML dependencies (cross-platform)
openai==1.12.0
httpx==0.27.0

# Document processing (cross-platform)
pypdf==5.1.0
python-docx==1.1.2
beautifulsoup4==4.12.3
lxml==5.3.0

# File type detection (platform-specific)
python-magic==0.4.27; sys_platform != 'win32'
python-magic-bin==0.4.14; sys_platform == 'win32'

# HTTP client (cross-platform)
requests==2.32.3

# Configuration (cross-platform)
python-dotenv==1.0.1

# Security (cross-platform)
cryptography==44.0.0

# WSGI servers (platform-specific)
gunicorn==23.0.0; sys_platform != 'win32'
waitress==3.0.0; sys_platform == 'win32'
```

### Platform-Specific Dependencies

**Windows automatically gets:**
- `python-magic-bin` (Windows-compatible file detection)
- `waitress` (Windows WSGI server)

**macOS/Linux automatically gets:**
- `python-magic` (requires libmagic system library)
- `gunicorn` (Unix WSGI server)

### Installing Dependencies

```bash
# Make sure virtual environment is activated
pip install -r requirements.txt
```

### Upgrading Dependencies

```bash
# Upgrade all packages to latest compatible versions
pip install --upgrade -r requirements.txt
```

### Troubleshooting Dependency Issues

**Issue: "Could not find a version that satisfies the requirement"**

Solution:
```bash
# Upgrade pip first
pip install --upgrade pip

# Try installing again
pip install -r requirements.txt
```

**Issue: "Failed building wheel for cryptography"**

Solution (Linux):
```bash
sudo apt install build-essential libssl-dev libffi-dev python3-dev
pip install -r requirements.txt
```

Solution (macOS):
```bash
brew install openssl
pip install -r requirements.txt
```

**Issue: "python-magic import error"**

**Windows:**
```powershell
pip uninstall python-magic python-magic-bin
pip install python-magic-bin
```

**macOS:**
```bash
brew install libmagic
pip install python-magic
```

**Linux:**
```bash
sudo apt install libmagic1
pip install python-magic
```

---

## Configuration Setup

### Environment Variables (.env file)

The application requires a `.env` file with the following configuration:

### Step 1: Copy Template

```bash
cp .env.example .env
```

### Step 2: Edit Configuration

Open `.env` in a text editor and fill in the following:

#### Required Configuration

**1. Alma API Configuration**

```env
# Get your API key from: https://developers.exlibrisgroup.com/
ALMA_API_KEY=your_alma_api_key_here

# Choose region (North America, Europe, or Asia Pacific)
ALMA_API_BASE_URL=https://api-na.hosted.exlibrisgroup.com
```

**API Key Regions:**
- North America: `https://api-na.hosted.exlibrisgroup.com`
- Europe: `https://api-eu.hosted.exlibrisgroup.com`
- Asia Pacific: `https://api-ap.hosted.exlibrisgroup.com`

**Getting Alma API Key:**
1. Log in to Ex Libris Developer Network
2. Navigate to API Keys
3. Create new API key with permissions:
   - Acquisitions: Read/Write
   - Vendors: Read
4. Copy the API key

**2. LiteLLM Configuration**

```env
# Your LiteLLM proxy URL (provided by administrator)
LITELLM_BASE_URL=https://ai-gateway.example.edu

# Your LiteLLM API key
LITELLM_API_KEY=your_litellm_api_key_here

# Model to use (gpt-4, gpt-5, etc.)
LITELLM_MODEL=gpt-5
```

**3. Application Secret Key**

```env
# Generate a secure random key
SECRET_KEY=your_secret_key_for_flask_sessions_here
```

**Generate secure secret key:**

**Windows PowerShell:**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

**macOS/Linux:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste into `.env` file.

**Example output:**
```
a7f3e9c2b8d4f1a6e0c7b3d9f2a5c8e1b4d7f0a3c6e9b2d5f8a1c4e7b0d3f6a9
```

**⚠️ CRITICAL**: Never use default/example secret keys in production!

**4. Flask Environment**

```env
# Set to 'development' for local testing, 'production' for deployment
FLASK_ENV=development
```

### Step 3: Verify Configuration

After editing, your `.env` file should look like:

```env
# Alma API Configuration
ALMA_API_KEY=l7xxabcdef1234567890abcdef1234567890
ALMA_API_BASE_URL=https://api-na.hosted.exlibrisgroup.com

# LiteLLM Configuration
LITELLM_API_KEY=sk-1234567890abcdef
LITELLM_BASE_URL=https://ai-gateway.andrew.cmu.edu
LITELLM_MODEL=gpt-5

# Application Configuration
SECRET_KEY=a7f3e9c2b8d4f1a6e0c7b3d9f2a5c8e1b4d7f0a3c6e9b2d5f8a1c4e7b0d3f6a9

# Flask Environment
FLASK_ENV=development
```

### Step 4: Protect .env File

**Important**: Never commit `.env` to version control!

Verify `.env` is in `.gitignore`:
```bash
cat .gitignore | grep ".env"
```

Should show: `.env`

### Configuration Security

**Best practices:**
1. ✅ Use strong, randomly generated SECRET_KEY
2. ✅ Keep .env out of version control
3. ✅ Use different keys for development and production
4. ✅ Rotate API keys periodically
5. ✅ Restrict API key permissions to minimum required
6. ❌ Never share .env file via email or chat
7. ❌ Never hardcode secrets in application code

---

## Verification Steps

### 1. Verify Python Installation

```bash
python --version  # or python3 --version
```

Expected: `Python 3.11.x` or higher

### 2. Verify Virtual Environment

```bash
which python  # Linux/macOS
where python  # Windows
```

Path should point to `venv/bin/python` or `venv\Scripts\python.exe`

### 3. Verify Dependencies

```bash
pip list
```

Should show all packages from `requirements.txt`

Key packages to verify:
- flask (3.0.0)
- openai (1.12.0)
- pypdf (5.1.0)
- python-docx (1.1.2)
- python-magic or python-magic-bin
- gunicorn or waitress

### 4. Verify Configuration

```bash
# Test that .env file is loaded
python -c "from config import Config; print('Config OK' if Config.SECRET_KEY else 'Missing SECRET_KEY')"
```

Expected: `Config OK`

### 5. Test Application Startup

```bash
python app.py
```

Expected output:
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING in app: Running in development mode - HTTPS enforcement disabled
INFO in app: Rate limiting enabled
INFO in app: License Uploader application starting
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### 6. Test Web Interface

Open browser: http://localhost:5000

You should see the License Uploader home page with:
- Upload area
- "Choose File" button
- Drag-and-drop zone

### 7. Test Alma API Connection (Optional)

If you have configured Alma API key:

```bash
python -c "from alma_api import AlmaAPI; alma = AlmaAPI(); print('Connection successful' if alma.test_connection() else 'Connection failed')"
```

### 8. Test File Upload (Optional)

1. Prepare a small test PDF or TXT file
2. Go to http://localhost:5000
3. Upload the file
4. Verify it processes without errors

---

## Common Installation Issues

### Issue: "python: command not found"

**Cause**: Python not installed or not in PATH

**Solution:**
- Windows: Reinstall Python with "Add to PATH" checked
- macOS: Use `python3` instead of `python`
- Linux: Install Python 3.11+ using package manager

---

### Issue: "pip: command not found"

**Cause**: pip not installed

**Solution:**
```bash
# Download get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

# Install pip
python get-pip.py

# Verify
pip --version
```

---

### Issue: "venv creation failed" or "ensurepip not available"

**Cause**: Python venv module not installed

**Solution (Ubuntu/Debian):**
```bash
sudo apt install python3.11-venv
```

**Solution (Fedora/CentOS):**
```bash
sudo dnf install python3-venv
```

---

### Issue: "Failed building wheel for cryptography"

**Cause**: Missing system libraries for compilation

**Solution (Ubuntu/Debian):**
```bash
sudo apt install build-essential libssl-dev libffi-dev python3-dev
pip install -r requirements.txt
```

**Solution (macOS):**
```bash
brew install openssl
pip install -r requirements.txt
```

**Solution (Windows):**
- Install Visual Studio Build Tools
- Or use pre-compiled wheel: `pip install --only-binary :all: cryptography`

---

### Issue: "ImportError: No module named magic"

**Cause**: python-magic not installed correctly

**Solution (Windows):**
```powershell
pip uninstall python-magic python-magic-bin
pip install python-magic-bin
```

**Solution (macOS):**
```bash
brew install libmagic
pip install python-magic
```

**Solution (Linux):**
```bash
sudo apt install libmagic1
pip install python-magic
```

---

### Issue: "OSError: cannot load library 'libmagic'"

**Cause**: libmagic system library not installed

**Solution (macOS):**
```bash
brew install libmagic
```

**Solution (Linux):**
```bash
sudo apt install libmagic1
```

**Solution (Windows):**
```powershell
pip uninstall python-magic
pip install python-magic-bin
```

---

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Cause**: Dependencies not installed or wrong Python environment

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

---

### Issue: "Permission denied" errors (Linux/macOS)

**Cause**: Insufficient permissions

**Solution:**
```bash
# Don't use sudo with pip in virtual environment
# If you accidentally used sudo, recreate venv:
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### Issue: "Address already in use" when starting app

**Cause**: Port 5000 is already in use

**Solution:**

**Find and kill process:**
```bash
# macOS/Linux
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Or use different port:**
Edit `app.py` and change port:
```python
app.run(debug=True, host='127.0.0.1', port=5001)
```

---

### Issue: "CSRF token missing or invalid"

**Cause**: Flask-WTF not configured correctly

**Solution:**
- Ensure SECRET_KEY is set in .env
- Clear browser cookies and cache
- Restart application

---

### Issue: "Can't find config.py" or import errors

**Cause**: Running from wrong directory

**Solution:**
```bash
# Make sure you're in project root directory
cd /path/to/license_uploader

# Verify files exist
ls -la  # macOS/Linux
dir     # Windows

# Should see: app.py, config.py, requirements.txt, etc.
```

---

## Next Steps

After successful installation:

1. **Read User Guide**
   - See `USER_GUIDE.md` for usage instructions
   - Learn how to upload and process documents

2. **Configure for Production** (if deploying)
   - See `DEPLOYMENT_GUIDE.md` for production setup
   - Configure WSGI server (gunicorn/waitress)
   - Set up reverse proxy (nginx/Apache)
   - Enable HTTPS with SSL certificates

3. **Review Security Settings**
   - See `SECURITY_GUIDE.md` for security best practices
   - Configure rate limiting
   - Set up proper authentication

4. **Test the Application**
   - Upload a sample license document
   - Review extracted terms
   - Test Alma API integration
   - Verify vendor search works

5. **Customize (Optional)**
   - See `DEVELOPER_GUIDE.md` for customization options
   - Add custom license terms
   - Modify extraction prompts
   - Adjust UI styling

---

## Getting Help

If you encounter issues not covered here:

1. Check `TROUBLESHOOTING_GUIDE.md` for detailed solutions
2. Review application logs in `logs/license_uploader.log`
3. Check GitHub Issues (if applicable)
4. Contact system administrator
5. Refer to `DEVELOPER_GUIDE.md` for technical details

---

**Last Updated**: 2026-01-30
**Version**: 1.0
**Document Owner**: Technical Writer Agent
