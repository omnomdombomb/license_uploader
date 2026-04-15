# 📚 License Uploader

AI-powered license term extraction and upload to Ex Libris Alma.

**Automate license processing:** Upload document → AI extracts terms → Review → Submit → Done!

---

## 🚀 Quick Start

**New Users (Easiest):**
1. Read **[GET_STARTED.md](GET_STARTED.md)**
2. Double-click the launcher for your OS:
   - **Windows** → `START_HERE.bat`
   - **macOS** → `START_HERE.command` (not `.sh` — Finder opens `.sh` in a text editor)
   - **Linux** → `START_HERE.sh`
3. Browser opens automatically - start uploading!

**Need More Help?**
- 📖 Usage instructions: [USER_GUIDE.md](USER_GUIDE.md)
- 🔧 Installation help: [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

**Technical Documentation:** See [docs/](docs/) folder for production deployment, security audits, and build instructions.

---

## ✨ What It Does

The License Uploader automates the manual process of extracting and entering license terms:

- **Upload** any license document (PDF, DOCX, TXT)
- **AI extracts** 76+ DLF-standard license terms automatically
- **Review & edit** extracted terms in clean interface
- **Submit** directly to Alma via API

**Time savings:** Hours → Minutes per license

---

## 📋 System Requirements

- Python 3.11+
- 2 GB RAM (4 GB recommended)
- Internet connection
- Windows 10+, macOS 12+, or Linux (Ubuntu 20.04+)

---

## 📚 Documentation

### For End Users
- **[GET_STARTED.md](GET_STARTED.md)** ⭐ Start here! Simple 3-step setup
- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete usage instructions

### For Administrators
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Installation & configuration
- **[docs/PRODUCTION_READINESS_REPORT.md](docs/PRODUCTION_READINESS_REPORT.md)** - Production deployment
- **[docs/PRODUCTION_SECURITY_AUDIT.md](docs/PRODUCTION_SECURITY_AUDIT.md)** - Security review

### For Developers
- **[docs/BUILD_INSTRUCTIONS.md](docs/BUILD_INSTRUCTIONS.md)** - Build executables
- **[docs/RUN_EXECUTABLE.md](docs/RUN_EXECUTABLE.md)** - Run pre-built executables
- **[docs/](docs/)** - Additional technical documentation

## Features

- **Document Upload**: Support for PDF, DOCX, and TXT files (16 MB max)
- **AI-Powered Extraction**: Automatically extracts 76+ DLF-compliant license terms using LLM technology
- **Interactive Review Interface**:
  - Edit extracted terms with type-safe input fields
  - Search and filter terms
  - AI-powered term refinement
  - Date picker for start/end dates
  - Vendor selection from Alma
- **Alma Integration**: Direct API integration for license creation
- **Security**: CSRF protection, rate limiting, HTTPS enforcement, input validation
- **Cross-Platform**: 100% compatible with Windows 10/11, macOS 12+, Linux (Ubuntu 20.04+)

## Architecture

### Backend Components

- **Flask Application** (`app.py`): Main web server and routing
- **Document Parser** (`document_parser.py`): Extracts text from various file formats
- **LLM Extractor** (`llm_extractor.py`): Uses LiteLLM to extract license terms
- **Alma API** (`alma_api.py`): Handles communication with Ex Libris Alma APIs
- **License Terms Data** (`license_terms_data.py`): Defines 76 license terms conforming to DLF standards

### Frontend Components

- **Templates**: Jinja2 templates with responsive design
- **CSS**: Modern, clean styling with CSS variables
- **JavaScript**: Vanilla JS with modular architecture

## Requirements

**System Requirements:**
- **Python**: 3.11+ (3.12 or 3.13 recommended)
- **RAM**: 2 GB minimum, 4 GB+ recommended
- **Disk**: 500 MB minimum, 1 GB+ recommended
- **Network**: Broadband internet for AI and Alma APIs

**Platform Support:**
- **Windows**: 10/11 (64-bit) with python-magic-bin and waitress
- **macOS**: 12+ (Monterey or later) with libmagic and gunicorn
- **Linux**: Ubuntu 20.04+ LTS with libmagic1 and gunicorn

## Installation

There are **three ways** to use License Uploader:

### Option 1: Pre-Built Executable (Easiest)

Download and run the standalone executable - **no Python installation required!**

**See [RUN_EXECUTABLE.md](RUN_EXECUTABLE.md) for instructions.**

**Windows:**
1. Download `license_uploader_windows.zip`
2. Extract and run `license_uploader.exe`

**Linux/macOS:**
1. Download `license_uploader_unix.tar.gz`
2. Extract and run `./license_uploader`

### Option 2: Build Your Own Executable

Build a standalone executable from source for distribution.

**See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for complete build instructions.**

**Quick build:**
```bash
# Windows
build_windows.bat

# Linux/macOS
chmod +x build_unix.sh
./build_unix.sh
```

### Option 3: Python Installation (Development/Server)

Install from source for development or server deployment.

**See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for detailed platform-specific instructions.**

### Quick Install (Linux/macOS)

```bash
# Clone repository
git clone <repository-url>
cd license_uploader

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies (platform-specific automatically selected)
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Fill in API keys

# Run application
python app.py
```

Access at: http://localhost:5000

### Quick Install (Windows)

```powershell
# Clone repository
git clone <repository-url>
cd license_uploader

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies (python-magic-bin and waitress automatically installed)
pip install -r requirements.txt

# Configure environment
copy .env.example .env
notepad .env  # Fill in API keys

# Run application
python app.py
```

Access at: http://localhost:5000

## Usage

**See [USER_GUIDE.md](USER_GUIDE.md) for complete usage instructions.**

### Basic Workflow

1. **Upload**: Upload PDF, DOCX, or TXT license document (max 16MB)
2. **Review**: AI extracts 76+ license terms automatically
3. **Edit**: Review and edit extracted terms, use AI refinement if needed
4. **Submit**: Fill in basic info (code, name, type, status) and submit to Alma

**Processing time**: 10-30 seconds for extraction, 5-15 seconds for submission

## License Terms

The application extracts **76 license terms** conforming to Digital Library Federation (DLF) Electronic Resource Management Initiative (ERMI) standards, fully compatible with Ex Libris Alma.

**Key term categories:**
- Access rights (Remote, Walk-in, Concurrent Users)
- Usage rights (Print, Digital Copy, Scholarly Sharing)
- ILL rights (Electronic, Print/Fax, Secure Transmission)
- Course rights (Reserves, Packs - Print/Electronic)
- Archival rights (Archiving, Perpetual Access)
- Legal terms (Governing Law, Jurisdiction, Indemnification)
- Administrative (Renewal, Termination, Notice Periods)

**See [USER_GUIDE.md](USER_GUIDE.md) for complete list of terms.**

## API Reference

The application provides a RESTful API with session-based authentication and CSRF protection.

**Key endpoints:**
- `POST /upload` - Upload and extract terms (rate limit: 10/hour)
- `GET /review` - Review extracted terms
- `POST /refine-term` - Refine specific term with AI (rate limit: 30/hour)
- `POST /submit-license` - Submit to Alma (rate limit: 20/hour)
- `GET /api/csrf-token` - Get CSRF token for AJAX requests
- `GET /get-vendors` - Retrieve Alma vendor list
- `POST/GET/DELETE /api/prompt` - Manage custom extraction prompts

**See [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for complete API reference with request/response examples.**

## Configuration

All configuration is managed through the `.env` file. **Never commit `.env` to version control.**

### Required Environment Variables

```env
# Alma API (get key from Ex Libris Developer Network)
ALMA_API_KEY=your_alma_api_key_here
ALMA_API_BASE_URL=https://api-na.hosted.exlibrisgroup.com

# LiteLLM (AI extraction service)
LITELLM_API_KEY=your_litellm_api_key_here
LITELLM_BASE_URL=https://ai-gateway.example.edu
LITELLM_MODEL=gpt-5

# Application Security (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your_64_character_random_hex_string_here

# Environment (development or production)
FLASK_ENV=development
```

**See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for detailed configuration instructions.**

## Production Deployment

**See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for complete production deployment instructions.**

### Platform-Specific Deployment

**Linux (Recommended):**
- WSGI server: gunicorn with 4+ workers
- Reverse proxy: nginx with SSL/TLS
- Service manager: systemd
- Auto-start on boot

**macOS:**
- WSGI server: gunicorn
- Service manager: launchd
- Suitable for development/staging

**Windows:**
- WSGI server: waitress with 12+ threads
- Reverse proxy: IIS with ARR
- Service manager: NSSM or Windows Service

### Security Checklist

- [ ] HTTPS enabled with valid SSL certificate
- [ ] `FLASK_ENV=production` (not development)
- [ ] Strong `SECRET_KEY` (64+ random characters)
- [ ] Rate limiting enabled (Redis recommended)
- [ ] All security headers configured
- [ ] Firewall rules configured
- [ ] Regular security updates applied

**See [docs/SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md) for complete security configuration.**

## Troubleshooting

**See [docs/TROUBLESHOOTING_GUIDE.md](docs/TROUBLESHOOTING_GUIDE.md) for detailed troubleshooting.**

### Quick Troubleshooting

**Upload issues:**
- "Invalid file type" → Use PDF, DOCX, or TXT only
- "File too large" → Compress PDF or extract license sections (16MB limit)
- "No text extracted" → Use OCR for scanned PDFs

**Extraction issues:**
- "LLM timeout" → Wait and retry, service may be overloaded
- "Document truncated" → Review later sections manually (15,000 char limit)
- Incorrect extraction → Use refine button or manually edit

**Submission issues:**
- "License code required" → Fill in required fields
- "Alma API error" → Check API key and permissions
- "Session expired" → Upload document again (1 hour timeout)

**Platform issues:**
- **Windows**: Install python-magic-bin, use waitress WSGI
- **macOS**: Install libmagic via Homebrew, use gunicorn
- **Linux**: Install libmagic1, use gunicorn

### Logs

**Location:** `logs/license_uploader.log`

**View logs:**
```bash
tail -f logs/license_uploader.log
```

## Development

**See [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) for complete development documentation.**

### Development Setup

```bash
# Clone and install
git clone <repository-url>
cd license_uploader
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add API keys

# Run in development mode
export FLASK_ENV=development
python app.py
```

### Contributing

**See [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) for contribution guidelines.**

1. Fork repository
2. Create feature branch
3. Make changes following code style (PEP 8)
4. Test thoroughly
5. Submit pull request with clear description

### Adding Features

**New license terms:** Edit `license_terms_data.py`
**New file formats:** Extend `document_parser.py`
**Custom LLM prompts:** Use `/api/prompt` endpoint or edit `custom_prompt.txt`

## Architecture

**Technology Stack:**
- **Backend**: Python 3.11+, Flask 3.0
- **AI/ML**: LiteLLM (OpenAI, etc.)
- **Document Processing**: pypdf, python-docx
- **Security**: Flask-WTF (CSRF), flask-talisman (HTTPS), flask-limiter (rate limiting)
- **WSGI**: gunicorn (Linux/macOS), waitress (Windows)
- **Deployment**: nginx reverse proxy, systemd/launchd/NSSM service managers

**See [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) for architecture details and diagrams.**

## Standards Compliance

- **Digital Library Federation (DLF)** Electronic Resource Management Initiative (ERMI)
- **Ex Libris Alma API** schemas and specifications
- All 76 license terms conform to DLF/ERMI standards

## Support

**Documentation:**
- User questions: [USER_GUIDE.md](USER_GUIDE.md)
- Installation help: [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- Deployment issues: [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- API questions: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- Development: [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)
- Security: [docs/SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md)
- Troubleshooting: [docs/TROUBLESHOOTING_GUIDE.md](docs/TROUBLESHOOTING_GUIDE.md)

**External Resources:**
- Ex Libris Alma API: https://developers.exlibrisgroup.com/alma/apis/
- LiteLLM Documentation: https://docs.litellm.ai/
- Flask Documentation: https://flask.palletsprojects.com/

## Acknowledgments

- **Ex Libris** for Alma APIs and developer support
- **Digital Library Federation** for license term standards (DLF/ERMI)
- **LiteLLM** for unified LLM interface
- **OpenAI and other LLM providers** for language models
- **Flask** and Python ecosystem contributors

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Version

**Version 1.0** - Production Ready
- Document upload and parsing (PDF, DOCX, TXT)
- AI-powered extraction of 76 DLF-compliant license terms
- Interactive review interface with search, filter, and refinement
- Direct Alma API integration for license creation
- Production-grade security, rate limiting, and error handling
- 100% cross-platform compatibility (Windows/macOS/Linux)

---

**Last Updated**: 2026-02-25
**Status**: Production Ready
**Built with Flask, powered by AI, designed for librarians.**
