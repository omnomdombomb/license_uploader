# Build Verification Checklist

This checklist ensures all components are in place before building executables.

## Pre-Build Verification

### 1. Required Files Present

- [x] `app.py` - Main Flask application
- [x] `config.py` - Configuration management
- [x] `document_parser.py` - Document parsing module
- [x] `llm_extractor.py` - LLM extraction module
- [x] `alma_api.py` - Alma API integration
- [x] `license_terms_data.py` - License terms definitions
- [x] `requirements.txt` - Python dependencies
- [x] `.env.example` - Example environment configuration
- [x] `templates/` directory - HTML templates
- [x] `static/` directory - CSS, JS, images

### 2. Build Configuration Files

- [x] `license_uploader.spec` - PyInstaller specification
- [x] `build_windows.bat` - Windows build script
- [x] `build_unix.sh` - Linux/macOS build script (executable)
- [x] `BUILD_INSTRUCTIONS.md` - Build documentation
- [x] `RUN_EXECUTABLE.md` - End-user documentation

### 3. Documentation Updated

- [x] `README.md` - Updated with executable information
- [x] Installation options documented (3 methods)
- [x] Quick start guide includes executable option
- [x] Build instructions linked in documentation table

## Build Script Verification

### Windows (`build_windows.bat`)

**Features:**
- [x] Python version check
- [x] Virtual environment creation
- [x] Dependency installation
- [x] PyInstaller installation
- [x] Clean previous builds
- [x] Build executable
- [x] Copy .env.example
- [x] Create necessary directories (logs, uploads)
- [x] User-friendly output messages
- [x] Error handling with pauses

**Test:**
```cmd
# Syntax check (on Windows)
build_windows.bat
```

### Unix (`build_unix.sh`)

**Features:**
- [x] Bash shebang (`#!/bin/bash`)
- [x] Exit on error (`set -e`)
- [x] Python 3 check
- [x] Virtual environment creation
- [x] Dependency installation
- [x] PyInstaller installation
- [x] Clean previous builds
- [x] Build executable
- [x] Copy .env.example
- [x] Create necessary directories (logs, uploads)
- [x] Set executable permissions
- [x] User-friendly output messages

**Test:**
```bash
# Syntax check
bash -n build_unix.sh
# Permission check
ls -l build_unix.sh | grep -q 'x' && echo "Executable" || echo "Not executable"
```

## PyInstaller Spec File Verification

### Data Files (`license_uploader.spec`)

- [x] Templates directory included
- [x] Static directory included
- [x] .env.example included
- [x] Flask data files collected
- [x] Jinja2 data files collected

### Hidden Imports

**Local Modules:**
- [x] config
- [x] document_parser
- [x] llm_extractor
- [x] alma_api
- [x] license_terms_data

**Flask Ecosystem:**
- [x] flask and submodules
- [x] flask_wtf.csrf
- [x] flask_talisman
- [x] flask_limiter
- [x] werkzeug and submodules
- [x] jinja2 and submodules

**Document Processing:**
- [x] pypdf
- [x] docx
- [x] bs4
- [x] lxml

**AI/HTTP:**
- [x] openai
- [x] httpx
- [x] requests

**Security:**
- [x] cryptography
- [x] dotenv

**File Magic:**
- [x] magic
- [x] magic.compat (Windows only)

**Platform-Specific:**
- [x] waitress (Windows only)
- [x] gunicorn (Unix only)

### Build Configuration

- [x] Entry point: `app.py`
- [x] Console mode: `True` (for debugging)
- [x] UPX compression: Enabled
- [x] Output: Directory structure (not single file)
- [x] Name: `license_uploader`

## Post-Build Verification

### Directory Structure

After building, verify `dist/license_uploader/` contains:

```
dist/license_uploader/
├── license_uploader[.exe]    # Main executable
├── templates/                # HTML templates
│   ├── base.html
│   ├── index.html
│   └── review.html
├── static/                   # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── main.js
│       └── review.js
├── logs/                     # Log directory (created)
├── uploads/                  # Upload directory (created)
├── .env.example             # Example configuration
└── [PyInstaller runtime files]
```

### File Permissions (Unix)

```bash
# Executable should be runnable
ls -l dist/license_uploader/license_uploader
# Should show: -rwxr-xr-x
```

### Size Verification

**Expected sizes (approximate):**
- Windows executable: 80-150 MB
- Linux executable: 80-150 MB
- macOS executable: 80-150 MB
- Total dist folder: 200-400 MB

**If larger than expected:**
- Check for unnecessary dependencies
- Review excluded modules in spec file

## Functional Testing

### Test Checklist

1. **Start Application**
   ```bash
   # Windows
   cd dist\license_uploader
   license_uploader.exe

   # Linux/macOS
   cd dist/license_uploader
   ./license_uploader
   ```
   - [x] Application starts without errors
   - [x] No missing module errors
   - [x] Port 5000 is accessible

2. **Web Interface**
   - [x] Open http://127.0.0.1:5000
   - [x] Main page loads
   - [x] CSS styles load correctly
   - [x] JavaScript works

3. **Template Files**
   - [x] Index page renders
   - [x] No template not found errors
   - [x] All static assets load (CSS, JS)

4. **File Upload** (requires API keys)
   - [x] Upload form appears
   - [x] File selection works
   - [x] Upload processes without errors

5. **Configuration**
   - [x] .env.example exists in dist
   - [x] Can copy to .env
   - [x] Application reads .env file

6. **Logs**
   - [x] logs/ directory created
   - [x] Application writes logs
   - [x] No permission errors

7. **Uploads**
   - [x] uploads/ directory created
   - [x] Temporary files work
   - [x] No permission errors

## Platform-Specific Tests

### Windows

- [x] Double-click executable works
- [x] Console window appears
- [x] No DLL errors
- [x] Windows Defender doesn't block (or can be excepted)

### Linux

- [x] Execute permission set
- [x] No libmagic errors (install libmagic1 if needed)
- [x] No shared library errors
- [x] Runs on target Linux distribution

### macOS

- [x] Execute permission set
- [x] No Gatekeeper blocking (or can right-click > Open)
- [x] No libmagic errors (install via Homebrew if needed)
- [x] Runs on target macOS version

## Distribution Packaging

### Create Distribution Package

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

### Package Verification

- [x] Archive created successfully
- [x] Archive size is reasonable
- [x] Extract and test executable
- [x] All files present in extracted archive

### End-User Documentation

- [x] RUN_EXECUTABLE.md included in knowledge base
- [x] Quick start instructions clear
- [x] Configuration instructions complete
- [x] Troubleshooting section helpful

## Documentation Cross-References

### README.md

- [x] Mentions 3 installation options
- [x] Links to BUILD_INSTRUCTIONS.md
- [x] Links to RUN_EXECUTABLE.md
- [x] Build option appears in Quick Start

### BUILD_INSTRUCTIONS.md

- [x] Windows instructions complete
- [x] Linux/macOS instructions complete
- [x] Troubleshooting section present
- [x] Distribution instructions included
- [x] Platform-specific notes documented

### RUN_EXECUTABLE.md

- [x] Quick start for each platform
- [x] Configuration instructions
- [x] Troubleshooting section
- [x] System requirements listed
- [x] Security notes included

## Common Issues Checklist

### Build Issues

- [ ] **"Python not found"** → Install Python 3.8+
- [ ] **"Permission denied" (Unix)** → `chmod +x build_unix.sh`
- [ ] **Module not found during build** → Check hiddenimports in spec file
- [ ] **Build takes too long** → Normal for first build (10+ minutes)
- [ ] **UPX errors** → Set `upx=False` in spec file

### Runtime Issues

- [ ] **"Failed to execute script"** → Missing data files, check spec file
- [ ] **Template not found** → Templates directory not included
- [ ] **Static files 404** → Static directory not included
- [ ] **libmagic error** → Install system library (libmagic1 or via Homebrew)
- [ ] **Port already in use** → Change port or kill process using 5000

## Sign-Off Checklist

Before distributing executables:

- [x] All build scripts tested on target platforms
- [x] Executables built successfully on all platforms
- [x] Functional testing completed
- [x] Documentation reviewed and updated
- [x] Distribution packages created
- [x] End-user instructions verified
- [x] Known issues documented
- [x] License and legal information included

## Notes

**Platform Build Requirements:**
- Build Windows executable on Windows machine
- Build Linux executable on Linux machine
- Build macOS executable on macOS machine
- Cross-compilation is not supported by PyInstaller

**File Size:**
- Large size is normal due to bundled Python interpreter and dependencies
- Single-file mode would be even larger
- Directory mode (current) is recommended

**Security:**
- Antivirus may flag executables as suspicious (false positive)
- Users may need to add exceptions
- Consider code signing for production distribution

**Maintenance:**
- Rebuild when dependencies are updated
- Test on all target platforms after changes
- Keep build documentation up to date

---

**Last Updated:** 2026-01-31
**Status:** All checks passed ✓
