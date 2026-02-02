# License Uploader - Developer Guide

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Code Structure](#code-structure)
- [Key Components and Modules](#key-components-and-modules)
- [Development Environment Setup](#development-environment-setup)
- [Adding New License Terms](#adding-new-license-terms)
- [Customizing LLM Prompts](#customizing-llm-prompts)
- [Extending Document Parsers](#extending-document-parsers)
- [Database and Session Management](#database-and-session-management)
- [Testing](#testing)
- [Code Style and Standards](#code-style-and-standards)
- [Contributing Guidelines](#contributing-guidelines)

---

## Architecture Overview

The License Uploader is a Flask-based web application with an AI-powered extraction pipeline and Alma API integration.

### Technology Stack

**Backend:**
- **Python 3.11+**: Application language
- **Flask 3.0.0**: Web framework
- **gunicorn/waitress**: WSGI servers (platform-specific)

**AI/ML:**
- **LiteLLM**: Unified LLM interface (OpenAI, etc.)
- **OpenAI SDK**: LLM client library

**Document Processing:**
- **pypdf**: PDF text extraction
- **python-docx**: DOCX text extraction
- **BeautifulSoup4**: HTML parsing (fallback)

**Security:**
- **Flask-WTF**: CSRF protection
- **flask-talisman**: HTTPS enforcement, security headers
- **flask-limiter**: Rate limiting
- **cryptography**: Secure session encryption

**File Handling:**
- **python-magic/python-magic-bin**: MIME type detection (platform-specific)
- **pathlib**: Cross-platform path handling

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Browser                          │
│                     (User Interface)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Reverse Proxy (nginx)                     │
│              SSL/TLS Termination, Static Files              │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                WSGI Server (gunicorn/waitress)              │
│                    Worker Process Pool                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flask Application                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  app.py - Main application & routing                 │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│  ┌──────────────────┴───────────────────────────────────┐  │
│  │  Session Management (secure cookies, temp files)     │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│  ┌──────────────────┴───────────────────────────────────┐  │
│  │  Security Layer (CSRF, rate limiting, validation)    │  │
│  └──────────────────┬───────────────────────────────────┘  │
└────────────────────┬┴───────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────────┐
        │            │            │                │
        ▼            ▼            ▼                ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐
│ Document     │ │   LLM    │ │  Alma    │ │   Config   │
│ Parser       │ │ Extractor│ │   API    │ │            │
│              │ │          │ │          │ │            │
│ - pypdf      │ │ - OpenAI │ │ - REST   │ │ - .env     │
│ - python-docx│ │ - LiteLLM│ │ - Vendors│ │ - Secrets  │
│ - TXT reader │ │ - Prompts│ │ - License│ │            │
└──────────────┘ └────┬─────┘ └────┬─────┘ └────────────┘
                      │            │
                      ▼            ▼
              ┌───────────────────────────┐
              │  External Services        │
              │  - LLM API (GPT, etc.)    │
              │  - Alma API (Ex Libris)   │
              └───────────────────────────┘
```

### Request Flow

**1. Document Upload:**
```
Browser → Flask → Document Parser → LLM Extractor → Session Storage → Review Page
```

**2. Term Refinement:**
```
Browser → Flask → Session → LLM Extractor → Updated Value → Browser
```

**3. License Submission:**
```
Browser → Flask → Alma API → License Created → Session Clear → Home Page
```

---

## Code Structure

### Project Directory

```
license_uploader/
├── app.py                      # Main Flask application (850 lines)
├── config.py                   # Configuration management (50 lines)
├── document_parser.py          # Document text extraction (82 lines)
├── llm_extractor.py            # LLM-based term extraction (342 lines)
├── alma_api.py                 # Alma API integration (228 lines)
├── license_terms_data.py       # License term definitions (530 lines)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in git)
├── .env.example                # Environment template
├── custom_prompt.txt           # Custom LLM prompt (optional)
├── gunicorn_config.py          # gunicorn configuration (optional)
├── README.md                   # Project overview
├── USER_GUIDE.md               # User documentation
├── INSTALLATION_GUIDE.md       # Installation instructions
├── DEPLOYMENT_GUIDE.md         # Production deployment
├── API_DOCUMENTATION.md        # API reference
├── SECURITY_GUIDE.md           # Security best practices
├── TROUBLESHOOTING_GUIDE.md    # Troubleshooting guide
├── DEVELOPER_GUIDE.md          # This file
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Base template with header/footer
│   ├── index.html              # Upload page
│   └── review.html             # Review/edit terms page
│
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css           # Application styles
│   └── js/
│       ├── main.js             # Upload page logic
│       └── review.js           # Review page logic
│
├── logs/                       # Application logs (created on startup)
│   ├── license_uploader.log    # Main application log
│   ├── gunicorn_access.log     # Access log (production)
│   └── gunicorn_error.log      # Error log (production)
│
└── uploads/                    # Temporary file storage (auto-cleaned)
```

### Key Files Description

| File | Lines | Purpose | Dependencies |
|------|-------|---------|--------------|
| `app.py` | 850 | Main application, routing, error handling | Flask, all modules |
| `config.py` | 50 | Configuration loading, validation | python-dotenv |
| `document_parser.py` | 82 | Extract text from PDF/DOCX/TXT | pypdf, python-docx |
| `llm_extractor.py` | 342 | AI term extraction, prompt management | openai, httpx |
| `alma_api.py` | 228 | Alma API client, vendor/license operations | requests |
| `license_terms_data.py` | 530 | 76 license term definitions | None |

---

## Key Components and Modules

### app.py - Main Application

**Responsibilities:**
- Flask application initialization
- Route handling (upload, review, submit)
- Session management
- Error handling
- Security configuration (CSRF, Talisman, rate limiting)
- Logging setup

**Key routes:**
- `GET /` - Home page
- `POST /upload` - File upload and processing
- `GET /review` - Review extracted terms
- `POST /refine-term` - Refine specific term
- `POST /submit-license` - Submit to Alma
- `GET /api/csrf-token` - Get CSRF token
- `POST/GET /api/config` - API configuration
- `POST/GET/DELETE /api/prompt` - Prompt management

**Security features:**
- CSRF protection (Flask-WTF)
- HTTPS enforcement (Talisman in production)
- Rate limiting (Flask-Limiter)
- Session security (httpOnly, secure, SameSite cookies)
- Input sanitization
- Path traversal protection
- File validation (extension, MIME type, size)

**Example - Upload handler:**
```python
@app.route('/upload', methods=['POST'])
@limiter.limit("10 per hour")
def upload_file():
    # 1. Validate file
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    # 2. Save and validate
    filename = secure_filename(file.filename)
    filepath = Path(Config.UPLOAD_FOLDER) / filename
    file.save(str(filepath))

    is_valid, error_message = validate_file_content(str(filepath))
    if not is_valid:
        filepath.unlink()
        return jsonify({'error': error_message}), 400

    # 3. Parse document
    parser = DocumentParser()
    document_text = parser.parse_file(str(filepath))

    # 4. Extract terms with LLM
    extractor = LLMExtractor()
    extraction_result = extractor.extract_license_terms(document_text)

    # 5. Store in session
    session_id = os.urandom(16).hex()
    data_file = Path(tempfile.gettempdir()) / f'license_upload_{session_id}.json'

    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump({
            'document_text': document_text,
            'filename': filename,
            'extracted_terms': extraction_result['terms']
        }, f, ensure_ascii=False)

    session['data_file'] = str(data_file)
    filepath.unlink()

    return jsonify({
        'success': True,
        'redirect': url_for('review')
    })
```

### config.py - Configuration

**Responsibilities:**
- Load environment variables from .env
- Validate configuration values
- Provide default values
- Initialize application directories

**Key configuration:**
```python
class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Session security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

    # File upload
    UPLOAD_FOLDER = Path('uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

    # Alma API
    ALMA_API_KEY = os.getenv('ALMA_API_KEY')
    ALMA_API_BASE_URL = os.getenv('ALMA_API_BASE_URL')

    # LiteLLM
    LITELLM_API_KEY = os.getenv('LITELLM_API_KEY')
    LITELLM_BASE_URL = os.getenv('LITELLM_BASE_URL')
    LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gpt-4')

    @staticmethod
    def init_app(app):
        """Initialize application directories"""
        Config.UPLOAD_FOLDER.mkdir(exist_ok=True, parents=True)
```

**Security validation:**
- Checks SECRET_KEY strength
- Warns if using default values
- Enforces minimum key length

### document_parser.py - Document Parsing

**Responsibilities:**
- Extract text from PDF files
- Extract text from DOCX files
- Extract text from TXT files with encoding fallback
- Handle parsing errors gracefully

**Key methods:**
```python
class DocumentParser:
    @staticmethod
    def parse_file(filepath):
        """Parse file and extract text based on extension"""
        ext = Path(filepath).suffix.lower()

        if ext == '.pdf':
            return DocumentParser._parse_pdf(filepath)
        elif ext == '.docx':
            return DocumentParser._parse_docx(filepath)
        elif ext == '.txt':
            return DocumentParser._parse_txt(filepath)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    @staticmethod
    def _parse_pdf(filepath):
        """Extract text from PDF using pypdf"""
        reader = PdfReader(filepath)
        text = []
        for page in reader.pages:
            text.append(page.extract_text())
        return '\n'.join(text)

    @staticmethod
    def _parse_txt(filepath):
        """Extract text with encoding fallback"""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        # Fallback with error handling
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
```

### llm_extractor.py - LLM Extraction

**Responsibilities:**
- Create extraction prompts
- Call LLM API for term extraction
- Validate and format extracted terms
- Fuzzy matching for term values
- Refine individual terms
- Manage custom prompts

**Key features:**
- **Document truncation**: Limits to 15,000 characters for LLM
- **Fuzzy matching**: Maps LLM output to valid term values
- **Timeout handling**: 180-second timeout for LLM calls
- **Custom prompts**: User-customizable extraction templates

**Example:**
```python
class LLMExtractor:
    MAX_DOCUMENT_LENGTH = 15000
    CUSTOM_PROMPT_FILE = 'custom_prompt.txt'

    def __init__(self, api_key=None, base_url=None, model=None):
        """Initialize OpenAI client with LiteLLM proxy"""
        http_client = httpx.Client(verify=True, timeout=180.0)

        self.client = openai.OpenAI(
            api_key=api_key or Config.LITELLM_API_KEY,
            base_url=base_url or Config.LITELLM_BASE_URL,
            http_client=http_client
        )
        self.model = model or Config.LITELLM_MODEL

    def extract_license_terms(self, document_text):
        """Extract all license terms from document"""
        # Check for truncation
        was_truncated = len(document_text) > self.MAX_DOCUMENT_LENGTH

        # Create prompt
        prompt = self._create_extraction_prompt(document_text)

        # Call LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at analyzing license agreements..."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        # Parse and validate
        result = json.loads(response.choices[0].message.content)
        formatted_terms = self._validate_and_format_terms(result)

        # Add truncation warning if needed
        if was_truncated:
            return {
                'terms': formatted_terms,
                'truncation_warning': {
                    'message': f'Document truncated from {len(document_text)} to {self.MAX_DOCUMENT_LENGTH} characters.'
                }
            }

        return {'terms': formatted_terms}
```

### alma_api.py - Alma Integration

**Responsibilities:**
- Authenticate with Alma API
- Fetch vendor list
- Create licenses
- Build license payloads
- Handle API errors

**Key methods:**
```python
class AlmaAPI:
    def __init__(self, api_key=None, base_url=None):
        """Initialize Alma API client"""
        self.api_key = api_key or Config.ALMA_API_KEY
        self.base_url = base_url or Config.ALMA_API_BASE_URL
        self.headers = {
            'Authorization': f'apikey {self.api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_vendors(self, limit=100, offset=0):
        """Retrieve list of vendors"""
        url = f"{self.base_url}/almaws/v1/acq/vendors"
        params = {'limit': limit, 'offset': offset, 'status': 'active'}

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        data = response.json()
        return [
            {
                'code': v.get('code'),
                'name': v.get('name'),
                'status': v.get('status', {}).get('value')
            }
            for v in data.get('vendor', [])
        ]

    def create_license(self, license_data):
        """Create new license in Alma"""
        url = f"{self.base_url}/almaws/v1/acq/licenses"

        self._validate_license_data(license_data)

        response = requests.post(url, headers=self.headers, json=license_data)
        response.raise_for_status()

        return response.json()

    def build_license_payload(self, basic_info, extracted_terms):
        """Build Alma-compliant license payload"""
        # Build terms array
        terms = []
        for code, term_data in extracted_terms.items():
            if term_data['value'] is not None:
                terms.append({
                    'code': code,
                    'value': term_data['value']
                })

        # Build license object
        license_obj = {
            'code': basic_info.get('code'),
            'name': basic_info.get('name'),
            'type': {'value': basic_info.get('type', 'LICENSE')},
            'status': {'value': basic_info.get('status', 'ACTIVE')},
            'review_status': {'value': basic_info.get('review_status', 'INREVIEW')}
        }

        if terms:
            license_obj['terms'] = {'term': terms}

        return license_obj
```

### license_terms_data.py - Term Definitions

**Responsibilities:**
- Define 76 DLF/ERMI standard license terms
- Define term types and valid values
- Provide term metadata (name, description)

**Data structure:**
```python
LICENSE_TERMS = [
    {
        "code": "ARCHIVE",
        "name": "Archiving Right",
        "description": "The right to permanently retain an electronic copy...",
        "type": "LicenseTermsPermittedProhibited"
    },
    # ... 75 more terms
]

TERM_TYPE_VALUES = {
    "LicenseTermsPermittedProhibited": [
        "Permitted (Explicit)",
        "Permitted (Interpreted)",
        "Prohibited (Explicit)",
        "Prohibited (Interpreted)",
        "Silent",
        "Uninterpreted",
        "Not Applicable"
    ],
    "LicenseTermsYesNo": ["Yes", "No"],
    "LicenseTermsRenewalType": ["Explicit", "Automatic"],
    "LicenseTermsUOM": ["Week", "Calendar Day", "Month", "Business Day"],
    "FREE-TEXT": None
}
```

---

## Development Environment Setup

### 1. Install Prerequisites

```bash
# Python 3.11+
python3.11 --version

# Git
git --version

# Platform-specific libraries (see INSTALLATION_GUIDE.md)
```

### 2. Clone Repository

```bash
git clone <repository-url>
cd license_uploader
```

### 3. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
```

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment

```bash
cp .env.example .env
nano .env  # Fill in API keys
```

### 6. Run Development Server

```bash
# Set development mode
export FLASK_ENV=development  # or set FLASK_ENV=development on Windows

# Run application
python app.py
```

Access at: http://localhost:5000

### 7. Enable Debug Mode

Debug mode is enabled by default when `FLASK_ENV=development`.

**Features:**
- Auto-reload on code changes
- Detailed error pages
- HTTPS enforcement disabled
- Verbose logging

---

## Adding New License Terms

To add custom license terms beyond the standard 76:

### 1. Edit license_terms_data.py

```python
LICENSE_TERMS.append({
    "code": "CUSTOM_TERM",
    "name": "Custom Term Name",
    "description": "Description of what this term means",
    "type": "LicenseTermsYesNo"  # or other type
})
```

### 2. Choose Term Type

**Existing types:**
- `LicenseTermsYesNo` - Yes/No binary
- `LicenseTermsPermittedProhibited` - Rights-based permissions
- `LicenseTermsRenewalType` - Explicit/Automatic
- `LicenseTermsUOM` - Time units
- `FREE-TEXT` - Open-ended text

**Add new type:**
```python
TERM_TYPE_VALUES["CustomType"] = [
    "Option 1",
    "Option 2",
    "Option 3"
]
```

### 3. Update UI (Optional)

If adding a new term type, update `review.html` template:

```html
{% elif term.type == 'CustomType' %}
  <select name="{{ code }}" class="term-value">
    <option value="">-- Select --</option>
    <option value="Option 1">Option 1</option>
    <option value="Option 2">Option 2</option>
    <option value="Option 3">Option 3</option>
  </select>
{% endif %}
```

### 4. Test Extraction

```bash
# Run app and upload test document
python app.py

# Check logs for extraction results
tail -f logs/license_uploader.log
```

---

## Customizing LLM Prompts

### Default Prompt Structure

```
Analyze the following license agreement and extract all relevant license terms.

LICENSE TERMS TO EXTRACT:
- ARCHIVE: Archiving Right - The right to permanently retain... (Valid values: ...)
- FAIRUSE: Fair Use Clause - A clause that affirms... (Valid values: Yes, No)
...

DOCUMENT TEXT:
{document text here}

OUTPUT FORMAT:
Return a JSON object where each key is a term code and the value is the extracted information or null.
Example: {"ARCHIVE": "Permitted (Explicit)", "FAIRUSE": "Yes"}

Return ONLY valid JSON, no additional text.
```

### Create Custom Prompt

**1. Via API:**
```bash
curl -X POST http://localhost:5000/api/prompt \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -d '{
    "prompt": "Custom prompt template with {terms_description} and {document_text}"
  }'
```

**2. Via File:**
```bash
cat > custom_prompt.txt <<'EOF'
Analyze the following license agreement...

{terms_description}

{document_text}

Return JSON only.
EOF
```

### Required Placeholders

**Must include:**
- `{terms_description}` - Replaced with term definitions
- `{document_text}` - Replaced with uploaded document

**Optional:**
- `{truncation_note}` - Warning if document truncated

### Best Practices

- **Be specific**: Provide clear instructions
- **Give examples**: Show expected output format
- **Focus on accuracy**: Emphasize precision over speed
- **Handle ambiguity**: Tell LLM how to handle unclear cases
- **Keep it concise**: Shorter prompts = faster responses

---

## Extending Document Parsers

### Adding New File Format

**Example: RTF support**

```python
# 1. Install library
# pip install pyth3

# 2. Add to document_parser.py
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.plaintext.writer import PlaintextWriter

class DocumentParser:
    @staticmethod
    def parse_file(filepath):
        ext = Path(filepath).suffix.lower()

        if ext == '.rtf':
            return DocumentParser._parse_rtf(filepath)
        # ... existing code

    @staticmethod
    def _parse_rtf(filepath):
        """Extract text from RTF"""
        try:
            with open(filepath, 'rb') as f:
                doc = Rtf15Reader.read(f)
                return PlaintextWriter.write(doc).getvalue()
        except Exception as e:
            raise Exception(f"Error parsing RTF: {str(e)}")

# 3. Add to config.py
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'rtf'}

# 4. Update MIME types in app.py
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'application/rtf',  # Add RTF
    'application/octet-stream'
}
```

---

## Database and Session Management

### Session Storage

**The application uses two storage mechanisms:**

**1. Flask sessions (cookies):**
- Stores session ID and metadata
- Encrypted with SECRET_KEY
- HttpOnly, Secure, SameSite protected
- Max age: 1 hour

**2. Temporary files:**
- Stores extracted data (document text, terms)
- Location: `/tmp/license_upload_<session-id>.json`
- Auto-cleaned after 24 hours
- Deleted after license submission

### Session Data Structure

```json
{
  "document_text": "Full extracted text from uploaded document...",
  "filename": "license.pdf",
  "extracted_terms": {
    "ARCHIVE": {
      "value": "Permitted (Explicit)",
      "type": "LicenseTermsPermittedProhibited",
      "name": "Archiving Right",
      "description": "..."
    }
  },
  "truncation_warning": {
    "truncated": true,
    "message": "Document was truncated..."
  }
}
```

### Session Cleanup

**Automatic cleanup:**
```python
def cleanup_old_temp_files():
    """Clean up temporary session files older than 24 hours"""
    temp_dir = Path(tempfile.gettempdir())
    current_time = time.time()
    max_age = 24 * 60 * 60

    for filepath in temp_dir.glob('license_upload_*.json'):
        try:
            file_age = current_time - filepath.stat().st_mtime
            if file_age > max_age:
                filepath.unlink()
        except (OSError, PermissionError):
            pass
```

**Runs on:**
- Application startup
- After each license submission

---

## Testing

### Manual Testing

**1. Test upload:**
```bash
# Prepare test file
echo "This is a test license agreement." > test.txt

# Upload via curl
curl -X POST http://localhost:5000/upload \
  -F "file=@test.txt" \
  -H "X-CSRFToken: <token>"
```

**2. Test extraction:**
```python
from llm_extractor import LLMExtractor

extractor = LLMExtractor()
result = extractor.extract_license_terms("License text here...")
print(result)
```

**3. Test Alma API:**
```python
from alma_api import AlmaAPI

alma = AlmaAPI()
vendors = alma.get_vendors()
print(f"Found {len(vendors)} vendors")
```

### Unit Tests (Future)

**Recommended test structure:**
```
tests/
├── test_document_parser.py
├── test_llm_extractor.py
├── test_alma_api.py
├── test_routes.py
└── fixtures/
    ├── sample.pdf
    ├── sample.docx
    └── sample.txt
```

**Example test:**
```python
import pytest
from document_parser import DocumentParser

def test_pdf_parsing():
    text = DocumentParser.parse_file('tests/fixtures/sample.pdf')
    assert len(text) > 0
    assert 'license' in text.lower()

def test_unsupported_format():
    with pytest.raises(ValueError):
        DocumentParser.parse_file('test.invalid')
```

---

## Code Style and Standards

### Python Style

**Follow PEP 8:**
- 4 spaces for indentation
- Max line length: 100 characters
- Use descriptive variable names
- Add docstrings to functions

**Example:**
```python
def extract_license_terms(self, document_text):
    """
    Extract license terms from document text

    Args:
        document_text: Full text of the license document

    Returns:
        Dictionary with 'terms' and optional 'truncation_warning' keys

    Raises:
        Exception: If LLM API call fails
    """
    # Implementation
```

### Imports

**Order:**
1. Standard library
2. Third-party
3. Local modules

```python
import os
import json
from pathlib import Path

from flask import Flask, request
import openai

from config import Config
from document_parser import DocumentParser
```

### Error Handling

**Always handle errors gracefully:**
```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    return jsonify({'error': str(e)}), 500
```

### Logging

**Use structured logging:**
```python
app.logger.info(f'Processing file: {filename}')
app.logger.warning(f'Document truncated: {len(document_text)} chars')
app.logger.error(f'LLM extraction failed: {e}', exc_info=True)
```

---

## Contributing Guidelines

### Before Contributing

1. **Check existing issues** - Avoid duplicates
2. **Discuss major changes** - Open an issue first
3. **Follow code style** - PEP 8, existing patterns
4. **Test your changes** - Manually test all affected features
5. **Update documentation** - Keep docs in sync with code

### Contribution Process

**1. Fork and clone:**
```bash
git clone https://github.com/yourusername/license_uploader.git
cd license_uploader
git remote add upstream <original-repo-url>
```

**2. Create feature branch:**
```bash
git checkout -b feature/your-feature-name
```

**3. Make changes:**
- Write code
- Test thoroughly
- Update documentation
- Follow style guide

**4. Commit changes:**
```bash
git add .
git commit -m "Add feature: Brief description

Detailed explanation of changes and why they were made.

Fixes #123"
```

**5. Push and create PR:**
```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

### Commit Message Format

```
Type: Brief description (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Explain what changed and why, not how.

Fixes #issue-number
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code style (formatting, no logic change)
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

### Pull Request Checklist

- [ ] Code follows PEP 8 style guide
- [ ] All functions have docstrings
- [ ] Changes are tested manually
- [ ] Documentation updated (if applicable)
- [ ] No sensitive data in commits (API keys, etc.)
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains what and why

---

**Last Updated**: 2026-01-30
**Version**: 1.0
**Document Owner**: Technical Writer Agent
