# Build Instructions - License Uploader

This guide explains how to build a standalone executable for the License Uploader application on different operating systems.

## Overview

The build process uses [PyInstaller](https://pyinstaller.org/) to package the Flask application and all its dependencies into a single executable that can run without requiring Python to be installed.

## Prerequisites

- **Python 3.8+** installed on your system
- **Git** (optional, for cloning the repository)
- **Internet connection** (for downloading dependencies)

## Building on Windows

### Steps:

1. Open Command Prompt or PowerShell
2. Navigate to the project directory:
   ```cmd
   cd path\to\license_uploader
   ```

3. Run the build script:
   ```cmd
   build_windows.bat
   ```

4. Wait for the build to complete (may take 5-10 minutes)

5. The executable will be in `dist\license_uploader\license_uploader.exe`

### What the script does:
- Creates a Python virtual environment
- Installs all dependencies
- Installs PyInstaller
- Builds the executable using the spec file
- Creates necessary directories (logs, uploads)
- Copies configuration templates

## Building on Linux/macOS

### Steps:

1. Open Terminal
2. Navigate to the project directory:
   ```bash
   cd /path/to/license_uploader
   ```

3. Make the build script executable:
   ```bash
   chmod +x build_unix.sh
   ```

4. Run the build script:
   ```bash
   ./build_unix.sh
   ```

5. Wait for the build to complete (may take 5-10 minutes)

6. The executable will be in `dist/license_uploader/license_uploader`

### What the script does:
- Creates a Python virtual environment
- Installs all dependencies
- Installs PyInstaller
- Builds the executable using the spec file
- Creates necessary directories (logs, uploads)
- Copies configuration templates
- Makes the executable runnable

## After Building

### 1. Configure the Application

Navigate to the `dist/license_uploader/` directory and set up your configuration:

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your favorite text editor
nano .env  # or vim, notepad, etc.
```

### 2. Set Required Environment Variables

Edit the `.env` file and configure:

```bash
# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=production

# Alma API Configuration
ALMA_API_KEY=your_alma_api_key
ALMA_API_BASE_URL=https://api-na.hosted.exlibrisgroup.com

# LiteLLM Configuration
LITELLM_API_KEY=your_litellm_api_key
LITELLM_BASE_URL=https://ai-gsateway.andrew.cmu.edu
LITELLM_MODEL=gpt-4
```

**Generate a secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Run the Application

**Windows:**
```cmd
cd dist\license_uploader
license_uploader.exe
```

**Linux/macOS:**
```bash
cd dist/license_uploader
./license_uploader
```

The application will start and be available at:
- **Local:** http://127.0.0.1:5000
- **Network:** http://0.0.0.0:5000 (if in production mode)

## Distribution

### Creating a Portable Package

Once built, you can zip the entire `dist/license_uploader/` directory and distribute it:

**Windows:**
```cmd
cd dist
tar -a -c -f license_uploader_windows.zip license_uploader
```

**Linux/macOS:**
```bash
cd dist
tar -czf license_uploader_unix.tar.gz license_uploader
```

### What to Include in Distribution

The `dist/license_uploader/` directory contains:
- `license_uploader` or `license_uploader.exe` - The main executable
- `templates/` - HTML templates
- `static/` - CSS, JavaScript, and other static files
- `logs/` - Directory for application logs
- `uploads/` - Temporary directory for file uploads
- `.env.example` - Example configuration file
- All required dependencies (bundled by PyInstaller)

### Instructions for End Users

1. Extract the zip/tar.gz file
2. Copy `.env.example` to `.env`
3. Edit `.env` with their API keys and configuration
4. Run the executable
5. Open a web browser to http://127.0.0.1:5000

## Troubleshooting

### Build Errors

**"Python is not installed"**
- Install Python 3.8+ from https://www.python.org/
- Make sure Python is added to your PATH

**"Module not found" errors during build**
- Delete the `venv` directory and run the build script again
- Check that `requirements.txt` is present

**Build is very slow**
- This is normal - first build can take 10+ minutes
- Subsequent builds will be faster

### Runtime Errors

**"Failed to execute script" on Windows**
- Make sure all files in `dist/license_uploader/` are present
- Check that `.env` file is configured correctly
- Run from Command Prompt to see error messages

**Permission denied on Linux/macOS**
- Make sure the executable has execute permissions:
  ```bash
  chmod +x license_uploader
  ```

**"Address already in use"**
- Another application is using port 5000
- Change the port in `app.py` before building, or kill the other process

**Template/Static files not found**
- Make sure `templates/` and `static/` directories are in the same folder as the executable
- Don't move files around after building

## Advanced Options

### Building a Single-File Executable

To create a single .exe/.bin file instead of a directory, edit `license_uploader.spec`:

```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,      # Add this
    a.zipfiles,      # Add this
    a.datas,         # Add this
    [],
    exclude_binaries=False,  # Change to False
    name='license_uploader',
    # ... rest of config
)

# Remove or comment out the COLLECT section
```

**Note:** Single-file executables are slower to start and larger in size.

### Custom Icon

To add a custom icon, create an `.ico` file (Windows) or `.icns` file (macOS) and update the spec file:

```python
exe = EXE(
    # ... other parameters
    icon='icon.ico',  # Windows
    # or
    icon='icon.icns',  # macOS
)
```

### Reducing Executable Size

1. Exclude unnecessary modules in the spec file
2. Disable UPX compression (if causing issues):
   ```python
   upx=False
   ```

3. Use `--exclude-module` for large unused packages

## Platform-Specific Notes

### Windows
- The executable requires Visual C++ Redistributable
- Windows Defender may flag the .exe - add an exception if needed
- Console window can be hidden by setting `console=False` in the spec file

### Linux
- The executable is built for the specific Linux distribution
- May need to install system libraries: `libmagic1`
- Consider building on the oldest supported Linux version

### macOS
- May need to sign the app for distribution (codesign)
- Users may need to allow the app in System Preferences > Security
- Built executable is architecture-specific (Intel vs ARM/M1)

## Cross-Platform Builds

PyInstaller creates executables for the platform it runs on. To build for multiple platforms:

1. **Use separate build machines** - Build on each target OS
2. **Use virtual machines** - Use VMs to build for different platforms
3. **Use CI/CD** - GitHub Actions, GitLab CI, etc. can build for multiple platforms

## Support

For issues related to:
- **PyInstaller**: https://pyinstaller.org/en/stable/
- **Application bugs**: Check the project's issue tracker
- **Build process**: Review this document and check the build script output

## License

This build process and scripts are part of the License Uploader project.
