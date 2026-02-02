# License Uploader - Deployment Guide

## Table of Contents

- [Production Deployment Checklist](#production-deployment-checklist)
- [Platform-Specific Deployment](#platform-specific-deployment)
  - [Linux Deployment with gunicorn](#linux-deployment-with-gunicorn)
  - [macOS Deployment with gunicorn](#macos-deployment-with-gunicorn)
  - [Windows Deployment with waitress](#windows-deployment-with-waitress)
- [WSGI Server Configuration](#wsgi-server-configuration)
- [SSL/TLS Certificate Setup](#ssltls-certificate-setup)
- [Environment Variable Configuration](#environment-variable-configuration)
- [Security Hardening Checklist](#security-hardening-checklist)
- [Monitoring and Logging Setup](#monitoring-and-logging-setup)
- [Performance Tuning](#performance-tuning)
- [Backup and Recovery](#backup-and-recovery)

---

## Production Deployment Checklist

Before deploying to production, ensure you have completed all items:

### Pre-Deployment

- [ ] **Python 3.11+ installed** on production server
- [ ] **All dependencies installed** from requirements.txt
- [ ] **Environment variables configured** (.env file with production values)
- [ ] **Strong SECRET_KEY generated** (64+ characters, random)
- [ ] **Valid SSL/TLS certificates** obtained (Let's Encrypt, commercial CA)
- [ ] **Alma API key** configured with correct permissions
- [ ] **LiteLLM API key** configured and tested
- [ ] **Firewall rules** configured (ports 80, 443)
- [ ] **Reverse proxy** set up (nginx, Apache, or Caddy)
- [ ] **Log directory** created with proper permissions
- [ ] **Upload directory** created with proper permissions
- [ ] **Backup strategy** planned and tested

### Security

- [ ] **FLASK_ENV=production** (not development)
- [ ] **Debug mode disabled** (debug=False)
- [ ] **HTTPS enforcement enabled** (Talisman in production)
- [ ] **Rate limiting configured** (Redis recommended for production)
- [ ] **CSRF protection enabled** (Flask-WTF)
- [ ] **Secure session cookies** (SESSION_COOKIE_SECURE=True)
- [ ] **Security headers configured** (CSP, HSTS, X-Frame-Options)
- [ ] **File upload validation** enabled
- [ ] **Input sanitization** verified
- [ ] **.env file protected** (chmod 600, not in git)

### Monitoring

- [ ] **Application logging** configured to files
- [ ] **Log rotation** enabled (RotatingFileHandler)
- [ ] **Error monitoring** set up (Sentry, Rollbar, etc. - optional)
- [ ] **Uptime monitoring** configured (Pingdom, UptimeRobot, etc.)
- [ ] **Disk space monitoring** for uploads and logs
- [ ] **Resource monitoring** (CPU, RAM, network)

### Testing

- [ ] **Upload workflow tested** with sample documents
- [ ] **Alma API integration tested** (create test license)
- [ ] **Vendor search tested** (verify API connection)
- [ ] **Error handling tested** (invalid files, API failures)
- [ ] **Session management tested** (timeouts, CSRF)
- [ ] **SSL/TLS verified** (A+ rating on SSL Labs)
- [ ] **Load testing completed** (optional but recommended)

---

## Platform-Specific Deployment

---

## Linux Deployment with gunicorn

### Recommended for: Production servers, best performance

### Prerequisites

- Ubuntu 20.04+ LTS or equivalent
- Python 3.11+
- sudo privileges
- Domain name with DNS pointing to server

### Step 1: Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    libmagic1 \
    nginx \
    supervisor \
    git

# Create application user (recommended - don't run as root)
sudo useradd -m -s /bin/bash licenseapp
sudo su - licenseapp
```

### Step 2: Application Setup

```bash
# Clone or upload application
cd /home/licenseapp
git clone <repository-url> license_uploader
cd license_uploader

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy and edit .env
cp .env.example .env
nano .env
```

**Critical production settings:**
```env
FLASK_ENV=production
SECRET_KEY=<64-character-random-string>
ALMA_API_KEY=<your-production-key>
LITELLM_API_KEY=<your-production-key>
```

```bash
# Protect .env file
chmod 600 .env
```

### Step 4: Create gunicorn Configuration

Create `/home/licenseapp/license_uploader/gunicorn_config.py`:

```python
"""Gunicorn configuration for License Uploader"""
from pathlib import Path

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = 4  # 2-4 x CPU cores
worker_class = "sync"
worker_connections = 1000
timeout = 180  # Increased for LLM processing
keepalive = 2

# Logging
accesslog = "/home/licenseapp/license_uploader/logs/gunicorn_access.log"
errorlog = "/home/licenseapp/license_uploader/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "license_uploader"

# Server mechanics
daemon = False  # Supervisor will manage
pidfile = "/home/licenseapp/license_uploader/gunicorn.pid"
user = "licenseapp"
group = "licenseapp"
umask = 0o007
tmp_upload_dir = None

# SSL (if terminating SSL at gunicorn)
# keyfile = "/path/to/privkey.pem"
# certfile = "/path/to/fullchain.pem"
```

**Worker calculation:**
```
workers = (2 x CPU cores) + 1
```

For 2 CPU cores: 5 workers
For 4 CPU cores: 9 workers

### Step 5: Create systemd Service

Create `/etc/systemd/system/license-uploader.service`:

```ini
[Unit]
Description=License Uploader Web Application
After=network.target

[Service]
Type=simple
User=licenseapp
Group=licenseapp
WorkingDirectory=/home/licenseapp/license_uploader
Environment="PATH=/home/licenseapp/license_uploader/venv/bin"
ExecStart=/home/licenseapp/license_uploader/venv/bin/gunicorn \
    --config /home/licenseapp/license_uploader/gunicorn_config.py \
    app:app

# Restart policy
Restart=always
RestartSec=10

# Security settings
PrivateTmp=true
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/licenseapp/license_uploader/logs
ReadWritePaths=/home/licenseapp/license_uploader/uploads

# Resource limits
LimitNOFILE=65535
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
```

### Step 6: Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable license-uploader

# Start service
sudo systemctl start license-uploader

# Check status
sudo systemctl status license-uploader

# View logs
sudo journalctl -u license-uploader -f
```

### Step 7: Configure nginx Reverse Proxy

Create `/etc/nginx/sites-available/license-uploader`:

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name license-uploader.example.edu;

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name license-uploader.example.edu;

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/license-uploader.example.edu/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/license-uploader.example.edu/privkey.pem;

    # SSL configuration (Mozilla Intermediate)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/license-uploader.example.edu/chain.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Logging
    access_log /var/log/nginx/license-uploader-access.log;
    error_log /var/log/nginx/license-uploader-error.log;

    # Max upload size (match Flask config)
    client_max_body_size 16M;

    # Proxy to gunicorn
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts (increased for LLM processing)
        proxy_connect_timeout 180s;
        proxy_send_timeout 180s;
        proxy_read_timeout 180s;

        # Buffer settings
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # Static files (if serving directly from nginx)
    location /static {
        alias /home/licenseapp/license_uploader/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/license-uploader /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### Step 8: Verify Deployment

```bash
# Check service status
sudo systemctl status license-uploader

# Check nginx status
sudo systemctl status nginx

# Test HTTPS
curl -I https://license-uploader.example.edu

# View application logs
tail -f /home/licenseapp/license_uploader/logs/license_uploader.log

# View gunicorn logs
tail -f /home/licenseapp/license_uploader/logs/gunicorn_error.log
```

---

## macOS Deployment with gunicorn

### Recommended for: Development servers, staging environments

### Step 1: Application Setup

Same as Linux steps 1-4, but install to user directory:

```bash
cd ~/Applications
git clone <repository-url> license_uploader
cd license_uploader
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Create gunicorn Configuration

Create `~/Applications/license_uploader/gunicorn_config.py` (same as Linux example above)

### Step 3: Create launchd Service

Create `~/Library/LaunchAgents/com.license-uploader.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.license-uploader</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/yourusername/Applications/license_uploader/venv/bin/gunicorn</string>
        <string>--config</string>
        <string>/Users/yourusername/Applications/license_uploader/gunicorn_config.py</string>
        <string>app:app</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/Users/yourusername/Applications/license_uploader</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/Users/yourusername/Applications/license_uploader/logs/launchd.out.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/yourusername/Applications/license_uploader/logs/launchd.err.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/Users/yourusername/Applications/license_uploader/venv/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
```

### Step 4: Load Service

```bash
# Load service
launchctl load ~/Library/LaunchAgents/com.license-uploader.plist

# Check status
launchctl list | grep license-uploader

# View logs
tail -f ~/Applications/license_uploader/logs/launchd.out.log
```

### Step 5: Configure Reverse Proxy (Optional)

Use nginx (install via Homebrew) with same configuration as Linux.

---

## Windows Deployment with waitress

### Recommended for: Windows-only environments

### Step 1: Application Setup

```powershell
# Navigate to desired location
cd C:\inetpub

# Clone or copy application
git clone <repository-url> license_uploader
cd license_uploader

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Create waitress Runner Script

Create `C:\inetpub\license_uploader\run_waitress.py`:

```python
"""
Waitress WSGI server runner for Windows
"""
from waitress import serve
from app import app
import os

if __name__ == '__main__':
    # Production settings
    os.environ['FLASK_ENV'] = 'production'

    # Serve with waitress
    serve(
        app,
        host='127.0.0.1',
        port=5000,
        threads=12,  # Adjust based on CPU cores
        url_scheme='https',  # If behind reverse proxy with HTTPS
        channel_timeout=180,  # Increased for LLM processing
        asyncore_use_poll=True,
        backlog=2048
    )
```

### Step 3: Create Windows Service

**Using NSSM (Non-Sucking Service Manager):**

```powershell
# Download NSSM
# https://nssm.cc/download

# Install as service
nssm install LicenseUploader "C:\inetpub\license_uploader\venv\Scripts\python.exe" "C:\inetpub\license_uploader\run_waitress.py"

# Configure service
nssm set LicenseUploader AppDirectory "C:\inetpub\license_uploader"
nssm set LicenseUploader DisplayName "License Uploader Web Application"
nssm set LicenseUploader Description "AI-powered license term extraction and upload to Alma"
nssm set LicenseUploader Start SERVICE_AUTO_START

# Set output logging
nssm set LicenseUploader AppStdout "C:\inetpub\license_uploader\logs\service.out.log"
nssm set LicenseUploader AppStderr "C:\inetpub\license_uploader\logs\service.err.log"

# Start service
nssm start LicenseUploader

# Check status
nssm status LicenseUploader
```

**Using Windows Service Manager (Alternative):**

Create `C:\inetpub\license_uploader\service.py`:

```python
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
from pathlib import Path

# Add project directory to path
sys.path.insert(0, str(Path(__file__).parent))

class LicenseUploaderService(win32serviceutil.ServiceFramework):
    _svc_name_ = "LicenseUploader"
    _svc_display_name_ = "License Uploader Web Application"
    _svc_description_ = "AI-powered license term extraction and upload to Alma"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        from waitress import serve
        from app import app

        os.environ['FLASK_ENV'] = 'production'

        serve(
            app,
            host='127.0.0.1',
            port=5000,
            threads=12,
            channel_timeout=180
        )

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(LicenseUploaderService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(LicenseUploaderService)
```

Install:
```powershell
python service.py install
python service.py start
```

### Step 4: Configure IIS Reverse Proxy (Recommended)

1. **Install IIS with URL Rewrite and ARR**:
   - Enable IIS in Windows Features
   - Install URL Rewrite module
   - Install Application Request Routing (ARR)

2. **Configure ARR Proxy**:
   - IIS Manager > Server > Application Request Routing Cache
   - Server Proxy Settings > Enable Proxy

3. **Create IIS Site**:
   - Add new website
   - Bindings: HTTPS (443) with SSL certificate
   - Create web.config:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="ReverseProxyToWaitress" stopProcessing="true">
                    <match url="(.*)" />
                    <action type="Rewrite" url="http://127.0.0.1:5000/{R:1}" />
                </rule>
            </rules>
        </rewrite>
        <security>
            <requestFiltering>
                <requestLimits maxAllowedContentLength="16777216" />
            </requestFiltering>
        </security>
    </system.webServer>
</configuration>
```

### Step 5: Verify Deployment

```powershell
# Check service status
sc query LicenseUploader

# View logs
Get-Content C:\inetpub\license_uploader\logs\service.out.log -Tail 50 -Wait

# Test endpoint
Invoke-WebRequest -Uri http://localhost:5000
```

---

## WSGI Server Configuration

### gunicorn (Linux/macOS)

**Basic configuration:**
```bash
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

**Production configuration:**
```python
# gunicorn_config.py
workers = 4
worker_class = "sync"
bind = "127.0.0.1:5000"
timeout = 180
keepalive = 2
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
```

**Run:**
```bash
gunicorn --config gunicorn_config.py app:app
```

### waitress (Windows)

**Basic configuration:**
```python
from waitress import serve
from app import app

serve(app, host='127.0.0.1', port=5000)
```

**Production configuration:**
```python
serve(
    app,
    host='127.0.0.1',
    port=5000,
    threads=12,
    channel_timeout=180,
    asyncore_use_poll=True,
    backlog=2048
)
```

### Performance Tuning

**Worker calculation:**
- **gunicorn sync workers**: `(2 x CPU cores) + 1`
- **waitress threads**: `4 x CPU cores` (Windows)

**Timeout settings:**
- Standard: 30 seconds
- **License Uploader**: 180 seconds (for LLM processing)

---

## SSL/TLS Certificate Setup

### Let's Encrypt (Free, Automated)

**Install Certbot:**
```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# Fedora/CentOS
sudo dnf install certbot python3-certbot-nginx
```

**Obtain certificate:**
```bash
# Automatic nginx configuration
sudo certbot --nginx -d license-uploader.example.edu

# Manual (certificate only)
sudo certbot certonly --webroot -w /var/www/html -d license-uploader.example.edu
```

**Auto-renewal:**
```bash
# Test renewal
sudo certbot renew --dry-run

# Renewal is automatic via cron/systemd timer
sudo systemctl status certbot.timer
```

### Commercial Certificate

1. **Generate CSR:**
```bash
openssl req -new -newkey rsa:2048 -nodes \
    -keyout privkey.pem \
    -out csr.pem
```

2. **Submit CSR to CA** (DigiCert, GlobalSign, etc.)

3. **Install certificate:**
```bash
# Copy files to /etc/ssl/
sudo cp fullchain.pem /etc/ssl/certs/
sudo cp privkey.pem /etc/ssl/private/
sudo chmod 644 /etc/ssl/certs/fullchain.pem
sudo chmod 600 /etc/ssl/private/privkey.pem
```

4. **Update nginx config** with certificate paths

---

## Environment Variable Configuration

### Production .env Settings

```env
# CRITICAL: Set to production
FLASK_ENV=production

# Generate strong random key (64+ characters)
SECRET_KEY=<output-of-python-secrets-token_hex-32>

# Production API keys
ALMA_API_KEY=<production-alma-key>
LITELLM_API_KEY=<production-litellm-key>

# Production URLs
ALMA_API_BASE_URL=https://api-na.hosted.exlibrisgroup.com
LITELLM_BASE_URL=https://ai-gateway.production.edu
LITELLM_MODEL=gpt-5
```

### Security for .env File

```bash
# Set restrictive permissions
chmod 600 .env
chown licenseapp:licenseapp .env

# Verify not in git
cat .gitignore | grep ".env"
```

---

## Security Hardening Checklist

### Application Security

- [ ] FLASK_ENV=production
- [ ] Debug mode disabled
- [ ] Strong SECRET_KEY (64+ chars)
- [ ] HTTPS enforcement enabled (Talisman)
- [ ] SESSION_COOKIE_SECURE=True
- [ ] SESSION_COOKIE_HTTPONLY=True
- [ ] SESSION_COOKIE_SAMESITE='Lax'
- [ ] CSRF protection enabled (Flask-WTF)
- [ ] Rate limiting enabled
- [ ] File upload validation
- [ ] Input sanitization

### Server Security

- [ ] Firewall configured (UFW, iptables)
- [ ] SSH key-based authentication
- [ ] Disable root SSH login
- [ ] Keep system updated
- [ ] Fail2ban installed
- [ ] Minimal services running
- [ ] SELinux/AppArmor enabled

### Network Security

- [ ] HTTPS only (redirect HTTP)
- [ ] TLS 1.2+ only
- [ ] Strong cipher suites
- [ ] HSTS enabled
- [ ] OCSP stapling
- [ ] DDoS protection (Cloudflare, etc.)

---

## Monitoring and Logging Setup

### Application Logs

Location: `/home/licenseapp/license_uploader/logs/`

- `license_uploader.log` - Application logs
- `gunicorn_access.log` - Access logs
- `gunicorn_error.log` - Error logs

### Log Rotation

Automatic via `RotatingFileHandler` in app.py:
- Max size: 10 MB
- Backups: 5 files
- Format: Timestamp, level, request ID, message

### System Monitoring

**Uptime monitoring:**
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Check system resources
htop
```

**Disk space monitoring:**
```bash
# Check disk usage
df -h

# Monitor uploads directory
du -sh /home/licenseapp/license_uploader/uploads

# Set up cron for cleanup
crontab -e
# Add: 0 2 * * * find /home/licenseapp/license_uploader/uploads -mtime +1 -delete
```

---

## Performance Tuning

### gunicorn Workers

```python
# Optimal workers
import multiprocessing
workers = multiprocessing.cpu_count() * 2 + 1
```

### Redis for Rate Limiting (Recommended)

```bash
# Install Redis
sudo apt install redis-server

# Update app.py
limiter = Limiter(
    app=app,
    storage_uri="redis://localhost:6379"
)
```

### nginx Caching (Optional)

```nginx
# Cache static assets
location /static {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

See DEPLOYMENT_GUIDE.md for detailed performance optimizations.

---

## Backup and Recovery

### What to Backup

- [ ] `.env` file (encrypted)
- [ ] Custom prompt files
- [ ] Application logs (optional)
- [ ] nginx/systemd configurations

### Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/license_uploader"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup .env (encrypted)
gpg -c /home/licenseapp/license_uploader/.env > $BACKUP_DIR/env_$DATE.gpg

# Backup custom prompts
cp /home/licenseapp/license_uploader/custom_prompt.txt $BACKUP_DIR/ 2>/dev/null

# Backup configs
cp /etc/nginx/sites-available/license-uploader $BACKUP_DIR/nginx_$DATE.conf
cp /etc/systemd/system/license-uploader.service $BACKUP_DIR/systemd_$DATE.service

# Delete old backups (keep 30 days)
find $BACKUP_DIR -mtime +30 -delete
```

Run daily via cron:
```bash
crontab -e
# Add: 0 3 * * * /home/licenseapp/backup.sh
```

---

**Last Updated**: 2026-01-30
**Version**: 1.0
**Document Owner**: Technical Writer Agent
