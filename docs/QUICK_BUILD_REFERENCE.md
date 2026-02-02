# Quick Build Reference

**One-page reference for building License Uploader executables**

## Build Commands

### Windows
```cmd
build_windows.bat
```

### Linux/macOS
```bash
./build_unix.sh
```

## Output Location

```
dist/license_uploader/
├── license_uploader[.exe]    # Your executable
├── templates/                # Required
├── static/                   # Required
└── .env.example             # Copy to .env and configure
```

## Quick Test

```bash
# Navigate to output
cd dist/license_uploader

# Copy and edit config
cp .env.example .env
nano .env  # Add your API keys

# Run (Windows)
license_uploader.exe

# Run (Linux/macOS)
./license_uploader

# Test in browser
open http://127.0.0.1:5000
```

## Distribution

### Package for Distribution

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

### Give to Users

1. Send them the zip/tar.gz file
2. Include link to [RUN_EXECUTABLE.md](RUN_EXECUTABLE.md)
3. They extract, configure .env, and run
4. No Python installation needed!

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check Python 3.8+ installed |
| "Permission denied" (Unix) | `chmod +x build_unix.sh` |
| Executable won't start | Check logs/ directory for errors |
| Templates not found | Ensure templates/ in same dir as .exe |
| Antivirus blocks (Windows) | Add exception for executable |
| libmagic error (Linux) | `sudo apt-get install libmagic1` |
| Gatekeeper blocks (macOS) | Right-click > Open |

## File Sizes

- Build time: 5-15 minutes (first time)
- Executable: ~150 MB
- Total dist/ folder: 200-400 MB
- This is normal for PyInstaller!

## Documentation

- **Building:** [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)
- **Running:** [RUN_EXECUTABLE.md](RUN_EXECUTABLE.md)
- **Checklist:** [BUILD_CHECKLIST.md](BUILD_CHECKLIST.md)
- **Complete Summary:** [EXECUTABLE_BUILD_SUMMARY.md](EXECUTABLE_BUILD_SUMMARY.md)

## Requirements

### Build Requirements
- Python 3.8+ (automatically creates venv)
- Internet connection (downloads dependencies)
- 500 MB disk space

### End-User Requirements
- None! (Executable is self-contained)
- Just need to configure .env file

## Platform Notes

| Platform | Build On | Executable | Notes |
|----------|----------|-----------|-------|
| Windows 10/11 | Windows | .exe | May need VC++ Redistributable |
| Linux | Linux | Binary | May need libmagic1 |
| macOS 12+ | macOS | Binary | May trigger Gatekeeper |

**Important:** Build on the platform you want to distribute for (no cross-compilation).

---

**Quick Start:** Run build script → Test executable → Package → Distribute
