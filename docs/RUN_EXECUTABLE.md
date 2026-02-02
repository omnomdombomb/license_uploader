# Running the License Uploader Executable

This guide is for running the pre-built License Uploader executable.

## Quick Start

### Windows

1. Extract the zip file to a folder
2. Navigate to the `license_uploader` folder
3. Copy `.env.example` to `.env` and edit with your API keys
4. Double-click `license_uploader.exe` or run from Command Prompt:
   ```cmd
   license_uploader.exe
   ```
5. Open your browser to http://127.0.0.1:5000

### Linux/macOS

1. Extract the tar.gz file to a folder
2. Navigate to the `license_uploader` folder
3. Copy `.env.example` to `.env` and edit with your API keys
   ```bash
   cp .env.example .env
   nano .env  # or your preferred editor
   ```
4. Make the executable runnable (if needed):
   ```bash
   chmod +x license_uploader
   ```
5. Run the executable:
   ```bash
   ./license_uploader
   ```
6. Open your browser to http://127.0.0.1:5000

## Configuration

### Required Settings

Edit the `.env` file and set:

```bash
# Generate a secret key with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your_generated_secret_key_here

# Set to 'production' for production use
FLASK_ENV=production

# Your Alma API credentials
ALMA_API_KEY=your_alma_api_key
ALMA_API_BASE_URL=https://api-na.hosted.exlibrisgroup.com

# Your LiteLLM/AI Gateway credentials
LITELLM_API_KEY=your_litellm_api_key
LITELLM_BASE_URL=https://ai-gsateway.andrew.cmu.edu
LITELLM_MODEL=gpt-4
```

### Optional Settings

You can also configure:
- `LITELLM_MODEL` - AI model to use (default: gpt-4)
- Port number (edit in the executable, requires rebuild)

## Stopping the Application

- Press `Ctrl+C` in the terminal/command prompt where it's running
- Or close the terminal window

## Troubleshooting

### Windows

**Antivirus/Windows Defender blocks the executable**
- This is common with PyInstaller executables
- Add an exception in Windows Defender or your antivirus
- The executable is safe - it's just not signed

**"VCRUNTIME140.dll not found"**
- Install Microsoft Visual C++ Redistributable:
  https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads

**Console window shows error and closes immediately**
- Run from Command Prompt to see the error
- Check your `.env` file configuration
- Check that logs, uploads, templates, and static folders exist

### Linux/macOS

**"Permission denied"**
```bash
chmod +x license_uploader
```

**"libmagic.so.1: cannot open shared object file" (Linux)**
```bash
# Ubuntu/Debian
sudo apt-get install libmagic1

# Fedora/RHEL
sudo dnf install file-libs

# Arch
sudo pacman -S file
```

**"Address already in use"**
- Another application is using port 5000
- Find and stop it:
  ```bash
  # Linux/macOS
  lsof -i :5000
  kill <PID>

  # Windows
  netstat -ano | findstr :5000
  taskkill /PID <PID> /F
  ```

**macOS: "license_uploader cannot be opened because the developer cannot be verified"**
- Right-click the executable and select "Open"
- Click "Open" in the security dialog
- Or disable Gatekeeper temporarily:
  ```bash
  sudo spctl --master-disable
  ```

## File Structure

```
license_uploader/
├── license_uploader[.exe]    # Main executable
├── templates/                # HTML templates (required)
├── static/                   # CSS, JS files (required)
├── logs/                     # Application logs
├── uploads/                  # Temporary file uploads
├── .env.example             # Example configuration
├── .env                     # Your configuration (you create this)
└── [other PyInstaller files] # Required runtime files
```

**Important:** Do not delete or move any files except `.env`

## Usage

1. Start the application
2. Open http://127.0.0.1:5000 in your browser
3. Configure API keys in the web interface (or use .env file)
4. Upload a license document (PDF, DOCX, or TXT)
5. Review and edit extracted terms
6. Submit to Alma

## Security Notes

- The application runs locally on your machine
- API keys are stored in the `.env` file - keep this secure
- In production mode, use HTTPS (configure reverse proxy)
- Never share your `.env` file or API keys

## Getting Help

- Check logs in the `logs/` directory
- Review the console output for error messages
- Ensure all configuration in `.env` is correct
- Verify your API keys are valid

## System Requirements

- **Windows:** Windows 10 or later
- **Linux:** Most modern distributions (Ubuntu 20.04+, Fedora 35+, etc.)
- **macOS:** macOS 10.15 (Catalina) or later
- **RAM:** 512MB minimum, 1GB recommended
- **Disk Space:** 500MB for the application + space for logs and uploads
- **Network:** Internet connection required for API calls

## Uninstallation

Simply delete the entire `license_uploader` folder. No registry entries or system files are modified.
