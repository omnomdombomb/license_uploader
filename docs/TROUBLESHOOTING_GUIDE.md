# License Uploader - Troubleshooting Guide

## Table of Contents

- [Common Errors and Solutions](#common-errors-and-solutions)
  - [Upload Errors](#upload-errors)
  - [Extraction Errors](#extraction-errors)
  - [Submission Errors](#submission-errors)
  - [Session Errors](#session-errors)
  - [API Errors](#api-errors)
- [Platform-Specific Issues](#platform-specific-issues)
  - [Windows Issues](#windows-issues)
  - [macOS Issues](#macos-issues)
  - [Linux Issues](#linux-issues)
- [Debugging Steps](#debugging-steps)
- [Log File Locations](#log-file-locations)
- [Support Resources](#support-resources)

---

## Common Errors and Solutions

---

## Upload Errors

### Error: "No file uploaded"

**Symptom:**
```json
{"error": "No file uploaded"}
```

**Causes:**
- File input is empty
- Form submission without file
- JavaScript error preventing upload

**Solutions:**
1. Ensure file is selected before clicking "Process Document"
2. Check browser console for JavaScript errors (F12)
3. Try refreshing the page and uploading again
4. Disable browser extensions that might interfere

---

### Error: "No file selected"

**Symptom:**
```json
{"error": "No file selected"}
```

**Causes:**
- Empty filename in upload form
- File picker canceled

**Solutions:**
1. Select a file before submitting
2. Ensure file exists and is accessible
3. Try drag-and-drop instead of file picker

---

### Error: "Invalid file type"

**Symptom:**
```json
{"error": "Invalid file type"}
```

**Causes:**
- File extension not in allowed list (.pdf, .docx, .txt)
- Incorrect file extension

**Solutions:**
1. Convert file to supported format:
   - .doc → .docx (use Microsoft Word or LibreOffice)
   - .rtf → .pdf or .docx
   - Other formats → .pdf or .txt
2. Verify file extension is lowercase (.PDF → .pdf)
3. Check file isn't corrupted

---

### Error: "File too large. Maximum size is 16MB."

**Symptom:**
```json
{"error": "File too large. Maximum size is 16MB."}
```

**Causes:**
- File exceeds 16 MB limit
- High-resolution images in PDF
- Embedded fonts/graphics

**Solutions:**
1. **Compress PDF**:
   ```bash
   # Adobe Acrobat: Save As > Reduced Size PDF
   # Online: https://smallpdf.com/compress-pdf
   # Command line (Ghostscript):
   gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
      -dNOPAUSE -dQUIET -dBATCH -sOutputFile=output.pdf input.pdf
   ```

2. **Extract text only**:
   - Copy text from PDF to .txt file
   - Paste into new document and save

3. **Split document**:
   - Extract just the license sections
   - Upload main license only (not exhibits/schedules)

---

### Error: "Uploaded file is empty. Please upload a file with content."

**Symptom:**
```json
{"error": "Uploaded file is empty. Please upload a file with content."}
```

**Causes:**
- Zero-byte file
- File creation failed
- Corrupted file

**Solutions:**
1. Check file size (should be > 0 bytes)
2. Re-download or re-save the file
3. Try opening file in PDF reader to verify content
4. Create new file by copy/paste from original

---

### Error: "No text content could be extracted from the file."

**Symptom:**
```json
{"error": "No text content could be extracted from the file. Please check the file format."}
```

**Causes:**
- PDF is scanned image (not text-based)
- PDF is password-protected
- File is corrupted
- DOCX file is damaged

**Solutions:**

**For scanned PDFs:**
1. **Use OCR software**:
   - Adobe Acrobat: Tools > Enhance Scans > Recognize Text > In This File
   - Online OCR: https://www.adobe.com/acrobat/online/ocr-pdf.html
   - Free tool: https://ocr.space/

2. **Check if PDF has text**:
   - Try selecting text in PDF reader
   - If you can't select text → it's a scanned image
   - If you can select text → try re-saving PDF

**For password-protected PDFs:**
1. Remove password in PDF reader
2. Save unprotected version
3. Upload unprotected file

**For corrupted files:**
1. Re-download from original source
2. Try opening in different PDF reader
3. Export to new PDF
4. Save as text file if possible

---

### Error: "Invalid file type detected: {mime}. Only PDF, DOCX, and TXT files are allowed."

**Symptom:**
```json
{"error": "Invalid file type detected: image/jpeg. Only PDF, DOCX, and TXT files are allowed."}
```

**Causes:**
- File extension doesn't match content (e.g., renamed JPEG to .pdf)
- File is corrupted
- MIME type detection error

**Solutions:**
1. **Verify file is actually PDF/DOCX/TXT**:
   - Open in appropriate application
   - If it doesn't open, file is corrupted or wrong type

2. **Convert to correct format**:
   - Images → Use OCR to create searchable PDF
   - HTML → Save as PDF from browser
   - Other → Export or convert to PDF

3. **Re-create file**:
   - Don't just rename extension
   - Use proper "Save As" or "Export to PDF"

---

## Extraction Errors

### Error: "Error extracting terms with LLM: {error}"

**Symptom:**
```json
{"error": "Error extracting terms with LLM: Connection timeout"}
```

**Common errors:**
- "Connection timeout"
- "Invalid API key"
- "Model not found"
- "Rate limit exceeded"

**Solutions:**

**Connection timeout:**
1. Check internet connection
2. Try again in a few minutes (service may be overloaded)
3. Contact administrator to check LiteLLM service status

**Invalid API key:**
1. Verify LITELLM_API_KEY in .env file
2. Check API key hasn't expired
3. Test API key with curl:
   ```bash
   curl -X POST https://api.openai.com/v1/chat/completions \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-4","messages":[{"role":"user","content":"test"}]}'
   ```

**Model not found:**
1. Check LITELLM_MODEL in .env
2. Verify model name is correct (e.g., "gpt-4", "gpt-5")
3. Check model is available in your LiteLLM configuration

**Rate limit exceeded:**
1. Wait before trying again (rate limits reset hourly)
2. Contact administrator to increase quota
3. Use different API key if available

---

### Error: "AI service took too long to respond (timeout after 180 seconds)."

**Symptom:**
```json
{"error": "AI service took too long to respond (timeout after 180 seconds)."}
```

**Causes:**
- LLM service is overloaded
- Very large document (near 15,000 char limit)
- Network latency

**Solutions:**
1. **Wait and retry**: Service may be temporarily overloaded
2. **Use shorter document**: Extract just license sections
3. **Check service status**: Contact administrator
4. **Try different time**: Off-peak hours may be faster

---

### Warning: "Document was truncated from {length} to 15000 characters."

**Symptom:**
Yellow banner: "Document was truncated from 25000 to 15000 characters. Some terms in later sections may have been missed."

**Impact:**
- First 15,000 characters analyzed
- Terms in later sections may be missed
- Main license typically in first sections (usually OK)

**Solutions:**
1. **Review extracted terms carefully**
2. **Manually check original document** for terms in later sections
3. **Use Refine button** for specific terms
4. **Manually fill in** any missing terms
5. **Extract license sections only** before uploading (remove exhibits, schedules)

---

## Submission Errors

### Error: "License code is required"

**Symptom:**
```json
{"error": "License code is required"}
```

**Solution:**
Fill in the License Code field (required)

---

### Error: "License name is required"

**Symptom:**
```json
{"error": "License name is required"}
```

**Solution:**
Fill in the License Name field (required)

---

### Error: "End date must be after start date"

**Symptom:**
```json
{"error": "End date must be after start date"}
```

**Causes:**
- End date is same as or before start date
- Date order reversed

**Solutions:**
1. Check date order (start should be before end)
2. Verify dates are in YYYY-MM-DD format
3. Clear and re-enter dates using date picker

---

### Error: "Invalid date format. Please use YYYY-MM-DD format."

**Symptom:**
```json
{"error": "Invalid date format. Please use YYYY-MM-DD format."}
```

**Causes:**
- Date in wrong format (MM/DD/YYYY, DD/MM/YYYY, etc.)
- Invalid date (e.g., Feb 30)

**Solutions:**
1. Use date picker instead of typing
2. Format as YYYY-MM-DD (e.g., 2026-01-15)
3. Ensure month is 01-12, day is valid for month

---

### Error: "Error creating license: {error}"

**Symptom:**
```json
{"error": "Error creating license: License code already exists"}
{"error": "Error creating license: Unauthorized"}
{"error": "Error creating license: Network error"}
```

**License code already exists:**
1. Check Alma for existing license with same code
2. Use different license code
3. Delete or rename existing license in Alma

**Unauthorized:**
1. Check ALMA_API_KEY in .env
2. Verify API key has Acquisitions read/write permissions
3. Test Alma connection: `GET /test-connection`

**Network error:**
1. Check internet connection
2. Verify Alma API base URL is correct
3. Check firewall isn't blocking Alma API
4. Test with curl:
   ```bash
   curl -H "Authorization: apikey YOUR_KEY" \
     https://api-na.hosted.exlibrisgroup.com/almaws/v1/acq/vendors?limit=1
   ```

---

## Session Errors

### Error: "No document in session"

**Symptom:**
```json
{"error": "No document in session"}
```

**Causes:**
- Session expired (1 hour timeout)
- Browser cookies disabled
- Server restart cleared sessions

**Solutions:**
1. Upload document again (session data lost)
2. Enable browser cookies
3. Complete workflow within 1 hour
4. Save extracted data (copy/paste) for long sessions

---

### Error: "Session expired or invalid. Please upload your document again."

**Symptom:**
Redirect to home page with error message

**Causes:**
- Session timeout (no activity for 1 hour)
- Session file deleted
- Path traversal attempt detected (security)
- Server restart

**Solutions:**
1. Upload document again
2. Work faster (complete within 1 hour)
3. Save extracted data before leaving page
4. Check browser isn't clearing cookies automatically

---

### Error: "Session file not found"

**Symptom:**
```json
{"error": "Session file not found"}
```

**Causes:**
- Temporary file was deleted
- Disk space full
- File permissions issue

**Solutions:**
1. Upload document again
2. Check server disk space:
   ```bash
   df -h
   ```
3. Check temp directory permissions:
   ```bash
   ls -la /tmp
   ```

---

## API Errors

### Alma API Connection Errors

**Symptom:**
- "Error fetching vendors from Alma"
- "Error creating license"
- Test connection fails

**Debugging steps:**

1. **Test API key:**
   ```bash
   curl -H "Authorization: apikey YOUR_ALMA_API_KEY" \
     https://api-na.hosted.exlibrisgroup.com/almaws/v1/acq/vendors?limit=1
   ```

2. **Check response:**
   - 200 OK → API key works
   - 401 Unauthorized → Invalid API key
   - 403 Forbidden → Insufficient permissions
   - 404 Not Found → Wrong base URL
   - 500/503 → Alma service issue

3. **Verify base URL:**
   - North America: `https://api-na.hosted.exlibrisgroup.com`
   - Europe: `https://api-eu.hosted.exlibrisgroup.com`
   - Asia Pacific: `https://api-ap.hosted.exlibrisgroup.com`

4. **Check permissions:**
   - Required: Acquisitions (Read/Write)
   - Required: Vendors (Read)
   - Verify in Ex Libris Developer Network

---

### LiteLLM API Connection Errors

**Symptom:**
- "Error extracting terms with LLM"
- Timeout errors
- Invalid model errors

**Debugging steps:**

1. **Test API connectivity:**
   ```bash
   curl -X POST YOUR_LITELLM_BASE_URL/chat/completions \
     -H "Authorization: Bearer YOUR_LITELLM_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-4",
       "messages": [{"role": "user", "content": "test"}]
     }'
   ```

2. **Check configuration:**
   ```bash
   # View current config
   cat .env | grep LITELLM
   ```

3. **Verify model availability:**
   - Check LITELLM_MODEL matches available models
   - Common models: gpt-4, gpt-5

4. **Check quotas:**
   - Verify API usage hasn't exceeded quota
   - Check billing/payment status with provider

---

## Platform-Specific Issues

---

## Windows Issues

### Issue: "python: command not found"

**Causes:**
- Python not in PATH
- Using `python` instead of `py`

**Solutions:**
1. Use `py` command instead:
   ```powershell
   py --version
   py -m venv venv
   ```

2. Or add Python to PATH:
   - Reinstall Python with "Add to PATH" checked
   - Or manually add: System Properties > Environment Variables > Path

---

### Issue: python-magic-bin not found

**Symptom:**
```
ImportError: No module named 'magic'
```

**Solution:**
```powershell
pip uninstall python-magic python-magic-bin
pip install python-magic-bin
```

---

### Issue: waitress not starting

**Symptom:**
```
ModuleNotFoundError: No module named 'waitress'
```

**Solution:**
```powershell
pip install waitress
```

**Run application:**
```powershell
# Development
python app.py

# Production
waitress-serve --host=127.0.0.1 --port=5000 app:app
```

---

### Issue: Permission denied accessing temp files

**Causes:**
- Windows Defender blocking access
- Insufficient permissions
- Antivirus software

**Solutions:**
1. Run as Administrator (temporary test)
2. Add exclusion in Windows Defender:
   - Settings > Update & Security > Windows Security
   - Virus & threat protection > Exclusions
   - Add folder: project directory
3. Check TEMP environment variable:
   ```powershell
   echo $env:TEMP
   ```

---

### Issue: Slow file operations

**Causes:**
- Windows file I/O is slower than Linux/macOS
- Windows Defender scanning files

**Solutions:**
1. Add antivirus exclusion (see above)
2. Use SSD instead of HDD
3. Consider RAM disk for temp files (advanced):
   - Install ImDisk: http://www.ltr-data.se/opencode.html/#ImDisk
   - Create RAM disk for uploads/temp

---

## macOS Issues

### Issue: libmagic not found

**Symptom:**
```
ImportError: failed to find libmagic
```

**Solution:**
```bash
# Install libmagic
brew install libmagic

# Reinstall python-magic
pip uninstall python-magic
pip install python-magic
```

---

### Issue: SSL certificate verification failed

**Symptom:**
```
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

**Solutions:**
1. **Install certificates**:
   ```bash
   /Applications/Python\ 3.11/Install\ Certificates.command
   ```

2. **Or update certificates**:
   ```bash
   pip install --upgrade certifi
   ```

---

### Issue: Permission denied (port 5000)

**Symptom:**
```
OSError: [Errno 48] Address already in use
```

**Causes:**
- Port 5000 already in use (AirPlay Receiver on macOS 12+)

**Solutions:**
1. **Disable AirPlay Receiver**:
   - System Preferences > Sharing
   - Uncheck "AirPlay Receiver"

2. **Or use different port**:
   ```python
   # app.py
   app.run(debug=True, host='127.0.0.1', port=5001)
   ```

---

### Issue: "Operation not permitted" errors

**Causes:**
- macOS security restrictions
- Full Disk Access not granted

**Solutions:**
1. Grant Full Disk Access to Terminal:
   - System Preferences > Security & Privacy > Privacy
   - Full Disk Access > Add Terminal.app

2. Or grant access to Python:
   - Add Python.app to Full Disk Access list

---

## Linux Issues

### Issue: libmagic1 not found

**Symptom:**
```
ImportError: failed to find libmagic
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install libmagic1

# Fedora/CentOS
sudo dnf install file-libs

# Reinstall python-magic
pip install --force-reinstall python-magic
```

---

### Issue: Permission denied errors

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: '/tmp/license_upload_xyz.json'
```

**Causes:**
- Running as wrong user
- SELinux restrictions
- AppArmor restrictions

**Solutions:**

1. **Check file permissions:**
   ```bash
   ls -la /tmp/license_upload*
   ```

2. **Fix ownership:**
   ```bash
   sudo chown -R $USER:$USER /path/to/license_uploader
   ```

3. **SELinux (Fedora/CentOS):**
   ```bash
   # Check SELinux status
   getenforce

   # Set permissive (temporary)
   sudo setenforce 0

   # Or configure properly
   sudo setsebool -P httpd_can_network_connect 1
   ```

4. **AppArmor (Ubuntu):**
   ```bash
   # Check AppArmor status
   sudo aa-status

   # Disable for Python (temporary)
   sudo aa-complain /usr/bin/python3.11
   ```

---

### Issue: gunicorn not found

**Symptom:**
```
bash: gunicorn: command not found
```

**Solutions:**
1. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Install gunicorn:
   ```bash
   pip install gunicorn
   ```

3. Use full path:
   ```bash
   /path/to/venv/bin/gunicorn app:app
   ```

---

### Issue: Port 5000 access denied

**Symptom:**
```
PermissionError: [Errno 13] Permission denied
```

**Causes:**
- Ports below 1024 require root
- Firewall blocking port

**Solutions:**
1. Use port above 1024 (development):
   ```python
   app.run(debug=True, host='127.0.0.1', port=8000)
   ```

2. Use reverse proxy (production):
   - nginx on port 80/443
   - Proxies to app on port 5000

3. Allow port through firewall:
   ```bash
   sudo ufw allow 5000/tcp
   ```

---

## Debugging Steps

### 1. Check Application Logs

```bash
# View logs in real-time
tail -f logs/license_uploader.log

# Search for errors
grep ERROR logs/license_uploader.log

# View last 100 lines
tail -n 100 logs/license_uploader.log
```

### 2. Check Browser Console

1. Press F12 (or Cmd+Option+I on Mac)
2. Go to Console tab
3. Look for JavaScript errors (red text)
4. Check Network tab for failed requests

### 3. Test Individual Components

**Test document parser:**
```python
from document_parser import DocumentParser

text = DocumentParser.parse_file('/path/to/test.pdf')
print(f"Extracted {len(text)} characters")
print(text[:500])  # First 500 chars
```

**Test LLM extractor:**
```python
from llm_extractor import LLMExtractor

extractor = LLMExtractor()
result = extractor.extract_license_terms("Test license text...")
print(result)
```

**Test Alma API:**
```python
from alma_api import AlmaAPI

alma = AlmaAPI()
print(alma.test_connection())  # Should return True
vendors = alma.get_vendors()
print(f"Found {len(vendors)} vendors")
```

### 4. Verify Configuration

```bash
# Check environment variables
cat .env

# Test configuration loading
python -c "from config import Config; print(f'SECRET_KEY: {len(Config.SECRET_KEY)} chars'); print(f'ALMA_API_KEY: {Config.ALMA_API_KEY[:10]}...')"
```

### 5. Check Dependencies

```bash
# List installed packages
pip list

# Check for outdated packages
pip list --outdated

# Verify specific package
pip show python-magic
```

### 6. Test Network Connectivity

```bash
# Test Alma API
curl -H "Authorization: apikey YOUR_KEY" \
  https://api-na.hosted.exlibrisgroup.com/almaws/v1/acq/vendors?limit=1

# Test LiteLLM API
curl -X POST YOUR_LITELLM_URL/chat/completions \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4","messages":[{"role":"user","content":"test"}]}'
```

---

## Log File Locations

### Development

- **Application log**: `logs/license_uploader.log`
- **Console output**: Terminal/PowerShell window

### Production (Linux)

- **Application log**: `/home/licenseapp/license_uploader/logs/license_uploader.log`
- **gunicorn access**: `/home/licenseapp/license_uploader/logs/gunicorn_access.log`
- **gunicorn error**: `/home/licenseapp/license_uploader/logs/gunicorn_error.log`
- **nginx access**: `/var/log/nginx/license-uploader-access.log`
- **nginx error**: `/var/log/nginx/license-uploader-error.log`
- **System log**: `sudo journalctl -u license-uploader`

### Production (Windows)

- **Application log**: `C:\inetpub\license_uploader\logs\license_uploader.log`
- **Service log**: `C:\inetpub\license_uploader\logs\service.out.log`
- **IIS log**: `C:\inetpub\logs\LogFiles\`

---

## Support Resources

### Documentation

- **USER_GUIDE.md**: Usage instructions
- **INSTALLATION_GUIDE.md**: Installation help
- **DEPLOYMENT_GUIDE.md**: Production deployment
- **API_DOCUMENTATION.md**: API reference
- **DEVELOPER_GUIDE.md**: Development guide
- **SECURITY_GUIDE.md**: Security configuration
- **TROUBLESHOOTING_GUIDE.md**: This file

### External Resources

**Ex Libris Alma API:**
- Documentation: https://developers.exlibrisgroup.com/alma/apis/
- Developer Network: https://developers.exlibrisgroup.com/
- Support: Contact Ex Libris support

**LiteLLM:**
- Documentation: https://docs.litellm.ai/
- GitHub: https://github.com/BerriAI/litellm

**Flask:**
- Documentation: https://flask.palletsprojects.com/
- Security: https://flask.palletsprojects.com/en/3.0.x/security/

### Getting Help

**When reporting issues, include:**
1. What you were trying to do
2. What happened instead (exact error message)
3. Steps to reproduce
4. Platform (Windows/macOS/Linux)
5. Python version: `python --version`
6. Relevant log excerpts (last 20-50 lines)
7. Browser and version (if web UI issue)

**Contact:**
- System administrator (for deployment/configuration issues)
- Alma administrator (for Alma API issues)
- Developer (for bugs or feature requests)

---

**Last Updated**: 2026-01-30
**Version**: 1.0
**Document Owner**: Technical Writer Agent
