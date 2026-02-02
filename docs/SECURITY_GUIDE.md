# License Uploader - Security Guide

## Table of Contents

- [Security Overview](#security-overview)
- [Authentication and Authorization](#authentication-and-authorization)
- [API Key Management](#api-key-management)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Rate Limiting](#rate-limiting)
- [Security Headers](#security-headers)
- [CSRF Protection](#csrf-protection)
- [File Upload Security](#file-upload-security)
- [Session Security](#session-security)
- [Input Validation and Sanitization](#input-validation-and-sanitization)
- [Security Monitoring](#security-monitoring)
- [Security Checklist](#security-checklist)

---

## Security Overview

The License Uploader implements multiple layers of security to protect against common web vulnerabilities and ensure safe handling of sensitive data.

### Security Features

**Layer 1: Network Security**
- HTTPS enforcement (TLS 1.2+)
- Strong cipher suites
- HSTS (HTTP Strict Transport Security)
- Firewall rules

**Layer 2: Application Security**
- Session-based authentication
- CSRF protection
- Rate limiting
- Input validation
- Path traversal prevention
- MIME type validation

**Layer 3: Data Security**
- Encrypted sessions
- Secure API key storage
- Temporary file cleanup
- No persistent storage of sensitive data

**Layer 4: Infrastructure Security**
- Minimal attack surface
- Least privilege principle
- Security headers
- Error handling without information disclosure

---

## Authentication and Authorization

### Session-Based Authentication

The application uses **server-side sessions** with secure cookies.

**Session Configuration:**
```python
# config.py
SESSION_COOKIE_SECURE = True       # HTTPS only
SESSION_COOKIE_HTTPONLY = True     # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'    # CSRF protection
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour timeout
```

**Security properties:**
- ✅ Session data stored server-side (not in browser)
- ✅ Session ID encrypted with SECRET_KEY
- ✅ HttpOnly flag prevents XSS attacks
- ✅ Secure flag requires HTTPS
- ✅ SameSite prevents CSRF attacks
- ✅ 1-hour timeout limits exposure window

### No User Authentication

The application **does not require user login**. This simplifies deployment but means:

**Security implications:**
- Anyone with access to the URL can upload documents
- No user-level access control
- Session-based isolation only

**Recommended mitigations:**
1. **Deploy behind institutional authentication**:
   - Shibboleth
   - SAML
   - OAuth/OIDC
   - IP restriction

2. **Use reverse proxy authentication**:
   - nginx basic auth
   - Apache mod_auth

3. **Network restrictions**:
   - VPN access only
   - IP whitelist
   - Firewall rules

**Example nginx basic auth:**
```nginx
location / {
    auth_basic "License Uploader";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://127.0.0.1:5000;
}
```

---

## API Key Management

### Environment Variable Storage

**All API keys stored in .env file:**
```env
# .env (NEVER commit to git)
SECRET_KEY=<64-character-random-hex>
ALMA_API_KEY=<alma-api-key>
LITELLM_API_KEY=<litellm-api-key>
```

### SECRET_KEY Security

**Critical importance:**
- Encrypts session data
- Signs CSRF tokens
- Must be cryptographically random
- Must be unique per environment

**Generate secure key:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Output example:**
```
a7f3e9c2b8d4f1a6e0c7b3d9f2a5c8e1b4d7f0a3c6e9b2d5f8a1c4e7b0d3f6a9
```

**Security validation in config.py:**
```python
# Reject weak SECRET_KEY in production
if SECRET_KEY in ['dev-secret-key-change-in-production', 'your_secret_key_for_flask', '']:
    if os.getenv('FLASK_ENV') != 'development':
        raise ValueError("CRITICAL SECURITY ERROR: Weak SECRET_KEY detected.")

# Warn if short
if len(SECRET_KEY) < 32:
    print(f"WARNING: SECRET_KEY is short ({len(SECRET_KEY)} chars). Recommended: 64+ chars")
```

### API Key Permissions

**Alma API Key:**
- **Required permissions**: Acquisitions (Read/Write), Vendors (Read)
- **Recommended**: Create dedicated key for License Uploader
- **Rotate**: Every 90 days
- **Revoke**: Immediately if compromised

**LiteLLM API Key:**
- **Required permissions**: Model access (GPT-4, GPT-5, etc.)
- **Recommended**: Set usage limits/quotas
- **Monitor**: Track API usage for anomalies

### .env File Protection

**File permissions:**
```bash
# Restrict to owner read/write only
chmod 600 .env
chown licenseapp:licenseapp .env
```

**Git ignore:**
```bash
# Verify .env is ignored
cat .gitignore | grep ".env"
# Should show: .env
```

**Never:**
- ❌ Commit .env to version control
- ❌ Share .env via email/chat
- ❌ Store .env in shared drives
- ❌ Hardcode keys in application code
- ❌ Log API keys

### Session-Based API Configuration

**Users can override API keys per-session:**
```javascript
// POST /api/config
{
  "alma_api_key": "user-specific-key",
  "litellm_api_key": "user-specific-key"
}
```

**Security:**
- ✅ Stored server-side in session
- ✅ Never sent to browser
- ✅ Cleared after 1 hour
- ✅ Not logged

---

## SSL/TLS Configuration

### HTTPS Enforcement

**Production mode enables Talisman:**
```python
# app.py
if not app.debug and os.getenv('FLASK_ENV') != 'development':
    talisman = Talisman(
        app,
        force_https=True,
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,  # 1 year
        strict_transport_security_include_subdomains=True,
        content_security_policy={...},
        feature_policy={...}
    )
```

**Features:**
- All HTTP requests redirected to HTTPS
- HSTS header prevents downgrade attacks
- CSP prevents XSS and injection attacks

### Certificate Configuration

**Recommended: Let's Encrypt (Free)**
```bash
sudo certbot --nginx -d license-uploader.example.edu
```

**Certificate requirements:**
- ✅ TLS 1.2 minimum (TLS 1.3 preferred)
- ✅ Strong cipher suites only
- ✅ Valid certificate chain
- ✅ OCSP stapling enabled
- ✅ Auto-renewal configured

**nginx SSL configuration:**
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
ssl_prefer_server_ciphers off;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
```

**Test SSL configuration:**
- https://www.ssllabs.com/ssltest/
- Target: A+ rating

---

## Rate Limiting

### Implementation

**Flask-Limiter with configurable storage:**
```python
# app.py
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",  # Development
    # storage_uri="redis://localhost:6379",  # Production (recommended)
    headers_enabled=True
)
```

### Endpoint Limits

| Endpoint | Limit | Reason |
|----------|-------|--------|
| Global | 200/day, 50/hour | Prevent abuse |
| `POST /upload` | 10/hour | Heavy processing (file + LLM) |
| `POST /refine-term` | 30/hour | LLM API call |
| `POST /submit-license` | 20/hour | Alma API write |
| `POST /api/prompt` | 10/hour | Administrative operation |

**Example:**
```python
@app.route('/upload', methods=['POST'])
@limiter.limit("10 per hour")
def upload_file():
    # Process upload
```

### Rate Limit Bypass (Internal)

**For trusted internal users, whitelist IPs:**
```python
# app.py
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379",
    headers_enabled=True,
    # Whitelist internal IPs
    exempt_when=lambda: request.remote_addr in ['10.0.0.0/8', '192.168.0.0/16']
)
```

### Production Rate Limiting

**Use Redis for distributed rate limiting:**
```bash
# Install Redis
sudo apt install redis-server

# Start Redis
sudo systemctl start redis
```

**Update app.py:**
```python
limiter = Limiter(
    app=app,
    storage_uri="redis://localhost:6379"
)
```

**Benefits:**
- Shared limits across multiple workers
- Persistent across app restarts
- Better performance

---

## Security Headers

### Implemented Headers

**Via Talisman (production):**
```python
# Content Security Policy
content_security_policy={
    'default-src': "'self'",
    'script-src': ["'self'", 'cdn.jsdelivr.net'],
    'style-src': ["'self'", 'cdn.jsdelivr.net', "'unsafe-inline'"],
    'img-src': ["'self'", 'data:'],
    'font-src': ["'self'", 'cdn.jsdelivr.net'],
    'connect-src': ["'self'"],
    'frame-ancestors': "'none'"
}
```

**Manually added (all modes):**
```python
# app.py - set_security_headers()
response.headers['X-Content-Type-Options'] = 'nosniff'
response.headers['X-Frame-Options'] = 'DENY'
response.headers['X-XSS-Protection'] = '1; mode=block'
response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
response.headers['Permissions-Policy'] = 'geolocation=(), camera=(), microphone=(), payment=(), usb=()'
```

**Server header removed:**
```python
response.headers.pop('Server', None)
```

### Header Explanations

**Strict-Transport-Security (HSTS):**
- Forces HTTPS for 1 year
- Includes subdomains
- Prevents SSL stripping attacks

**Content-Security-Policy (CSP):**
- Prevents XSS attacks
- Restricts script sources to self + CDN
- Blocks inline scripts (except from CDN)
- Prevents clickjacking (frame-ancestors: none)

**X-Content-Type-Options:**
- Prevents MIME sniffing
- Forces browser to respect Content-Type

**X-Frame-Options:**
- Prevents clickjacking
- Blocks embedding in iframes

**X-XSS-Protection:**
- Enables browser XSS filter
- Blocks page on XSS detection

**Referrer-Policy:**
- Limits referer information leakage
- Sends origin only on cross-origin

**Permissions-Policy:**
- Disables unnecessary browser features
- Geolocation, camera, microphone, payment, USB

---

## CSRF Protection

### Flask-WTF Implementation

**Initialization:**
```python
# app.py
from flask_wtf.csrf import CSRFProtect, generate_csrf

csrf = CSRFProtect(app)
```

**All POST/PUT/DELETE requests protected automatically.**

### Getting CSRF Token

**Endpoint:**
```http
GET /api/csrf-token HTTP/1.1
```

**Response:**
```json
{
  "csrf_token": "ImFjYzQ4NzQ3ZGU5ZjRhNmY4YjI3MmE4ZjE2OTY0NTIwYjNhMGY0YmEi.Z6Y8gw.xGqxTZ8lH5hPzF3VUcR8e8T0Kz4"
}
```

### Using CSRF Token

**In JavaScript:**
```javascript
const csrfToken = document.getElementById('csrf-token').value;

fetch('/upload', {
  method: 'POST',
  headers: {
    'X-CSRFToken': csrfToken
  },
  body: formData
});
```

**In HTML form:**
```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

### CSRF Token Properties

- ✅ Unique per session
- ✅ Time-limited (1 hour)
- ✅ Signed with SECRET_KEY
- ✅ Validated on each request
- ✅ Prevents cross-site request forgery

---

## File Upload Security

### Multi-Layer Validation

**Layer 1: File Extension**
```python
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

**Layer 2: MIME Type Detection**
```python
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'application/octet-stream'
}

def validate_file_content(filepath):
    mime = magic.from_file(filepath, mime=True)
    if mime not in ALLOWED_MIME_TYPES:
        return False, f'Invalid file type detected: {mime}'
    return True, None
```

**Layer 3: File Size**
```python
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

if file_size > Config.MAX_CONTENT_LENGTH:
    return False, 'File too large (16MB limit)'
```

**Layer 4: Content Validation**
```python
if not document_text or document_text.strip() == '':
    return jsonify({'error': 'No text content extracted'}), 400
```

### Secure Filename Handling

**Werkzeug secure_filename:**
```python
from werkzeug.utils import secure_filename

filename = secure_filename(file.filename)
# "../../etc/passwd" → "etc_passwd"
# "script<>.pdf" → "script.pdf"
```

### Path Traversal Prevention

**Validate session file paths:**
```python
def validate_session_file_path(session_file_path):
    """Prevent path traversal attacks"""
    # Convert to absolute path
    file_path = Path(session_file_path).resolve()
    temp_dir = Path(tempfile.gettempdir()).resolve()

    # Ensure path is within temp directory
    if not str(file_path).startswith(str(temp_dir)):
        raise ValueError("Path traversal attempt detected")

    # Check filename pattern
    if not file_path.name.startswith('license_upload_'):
        raise ValueError("Invalid session file format")

    # Verify is regular file
    if not file_path.is_file():
        raise ValueError("Not a regular file")

    return file_path
```

### File Cleanup

**Immediate cleanup:**
```python
# After processing
filepath.unlink()  # Delete uploaded file

# After submission
Path(session['data_file']).unlink(missing_ok=True)
session.clear()
```

**Scheduled cleanup:**
```python
def cleanup_old_temp_files():
    """Delete files older than 24 hours"""
    temp_dir = Path(tempfile.gettempdir())
    max_age = 24 * 60 * 60

    for filepath in temp_dir.glob('license_upload_*.json'):
        file_age = time.time() - filepath.stat().st_mtime
        if file_age > max_age:
            filepath.unlink()
```

---

## Session Security

### Configuration

```python
# config.py
SESSION_COOKIE_SECURE = True       # HTTPS only
SESSION_COOKIE_HTTPONLY = True     # No JS access
SESSION_COOKIE_SAMESITE = 'Lax'    # CSRF protection
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
```

### Session Storage

**Dual storage:**
1. **Cookie**: Session ID (encrypted with SECRET_KEY)
2. **Temp file**: Session data (document text, extracted terms)

**Benefits:**
- Cookie size stays small
- Large data doesn't bloat cookies
- Server-side data security

### Session Cleanup

**On submission:**
```python
# Clean up temp file
if 'data_file' in session:
    Path(session['data_file']).unlink(missing_ok=True)

# Clear session
session.clear()
```

**On startup:**
```python
cleanup_old_temp_files()
```

### Session Timeout

**Inactivity timeout: 1 hour**
- Session expires after 1 hour of no requests
- User must re-upload document

**Security benefit:**
- Limits exposure window
- Prevents session hijacking
- Forces re-authentication periodically

---

## Input Validation and Sanitization

### License Field Sanitization

**Function:**
```python
def sanitize_license_field(value, max_length=255, allow_special=False):
    """Sanitize license field input"""
    if not value:
        return value

    # Strip whitespace
    sanitized = str(value).strip()

    # Enforce max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    # Remove dangerous characters
    if not allow_special:
        dangerous_chars = ['<', '>', '{', '}', '\\', '`']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')

    return sanitized
```

**Usage:**
```python
basic_info['code'] = sanitize_license_field(basic_info.get('code'), max_length=50)
basic_info['name'] = sanitize_license_field(basic_info.get('name'), max_length=255)
```

### Date Validation

```python
# Parse and validate dates
if start_date:
    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    basic_info['start_date'] = start_dt.strftime('%Y-%m-%d')

# Validate date range
if start_date and end_date:
    if end_dt <= start_dt:
        return jsonify({'error': 'End date must be after start date'}), 400
```

### Term Value Validation

**Fuzzy matching with whitelist:**
```python
def _validate_and_format_terms(self, extracted_terms):
    """Validate against allowed values"""
    if term['type'] != 'FREE-TEXT':
        allowed_values = TERM_TYPE_VALUES.get(term['type'], [])
        if extracted_value not in allowed_values:
            # Try fuzzy match
            matched_value = self._fuzzy_match_value(extracted_value, allowed_values)
            if matched_value:
                extracted_value = matched_value
            else:
                extracted_value = None  # Reject invalid value
```

---

## Security Monitoring

### Application Logging

**Rotating file handler:**
```python
file_handler = RotatingFileHandler(
    'logs/license_uploader.log',
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)
```

**Log format:**
```
%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s
```

### Security Events Logged

**Upload events:**
```python
app.logger.info(f'File upload initiated from {request.remote_addr}')
app.logger.warning(f'Invalid file type attempted: {filename}')
```

**Session events:**
```python
app.logger.warning(f"Invalid session file access from {request.remote_addr}")
app.logger.warning(f"Path traversal attempt detected: {session_file_path}")
```

**Rate limiting:**
```python
app.logger.warning(f"Rate limit exceeded for {request.remote_addr}: {request.path}")
```

**API errors:**
```python
app.logger.error(f"Alma API error: {e}", exc_info=True)
```

### Log Monitoring

**Watch for:**
- Multiple failed uploads from same IP
- Path traversal attempts
- Rate limit violations
- API authentication failures
- Unusual file sizes or types

**Example grep:**
```bash
# Watch for security events
tail -f logs/license_uploader.log | grep -i "warning\|error\|attempt\|invalid"

# Count rate limit violations today
grep "Rate limit exceeded" logs/license_uploader.log | grep "$(date +%Y-%m-%d)" | wc -l
```

---

## Security Checklist

### Pre-Deployment

- [ ] **SECRET_KEY**: Strong random 64+ character key
- [ ] **FLASK_ENV**: Set to `production` (not development)
- [ ] **Debug mode**: Disabled (`debug=False`)
- [ ] **.env file**: Protected (chmod 600, not in git)
- [ ] **API keys**: Valid and properly permissioned
- [ ] **SSL/TLS**: Valid certificate configured
- [ ] **HTTPS**: Enforced (Talisman enabled)
- [ ] **Rate limiting**: Enabled with Redis (production)
- [ ] **Firewall**: Ports 80/443 only (22 for admin)
- [ ] **File uploads**: Validation enabled (extension + MIME)

### Application Security

- [ ] **CSRF**: Protection enabled (Flask-WTF)
- [ ] **Session cookies**: Secure, HttpOnly, SameSite
- [ ] **Security headers**: All headers configured
- [ ] **Input validation**: All user inputs sanitized
- [ ] **Path traversal**: Prevention implemented
- [ ] **Error handling**: No sensitive data in errors
- [ ] **Logging**: Security events logged
- [ ] **File cleanup**: Automatic cleanup enabled

### Infrastructure Security

- [ ] **Operating system**: Up to date with security patches
- [ ] **Python**: 3.11+ with latest security updates
- [ ] **Dependencies**: All packages updated (pip list --outdated)
- [ ] **Web server**: nginx/Apache properly configured
- [ ] **WSGI server**: gunicorn/waitress with security options
- [ ] **Firewall**: UFW/iptables configured
- [ ] **SSH**: Key-based auth only, root login disabled
- [ ] **Monitoring**: Log monitoring configured

### Ongoing Security

- [ ] **Log review**: Check logs weekly for security events
- [ ] **API key rotation**: Rotate keys every 90 days
- [ ] **Dependency updates**: Update packages monthly
- [ ] **SSL certificate**: Auto-renewal enabled
- [ ] **Backup**: Configuration backed up
- [ ] **Incident response**: Plan documented
- [ ] **Security testing**: Penetration test annually

---

**Last Updated**: 2026-01-30
**Version**: 1.0
**Document Owner**: Technical Writer Agent
