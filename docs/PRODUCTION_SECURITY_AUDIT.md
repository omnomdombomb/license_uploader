# PRODUCTION SECURITY AUDIT - License Uploader Application
**Date:** 2026-01-31
**Auditor:** Production Readiness Review
**Severity Levels:** 🔴 CRITICAL | 🟡 HIGH | 🟠 MEDIUM | 🟢 LOW

---

## EXECUTIVE SUMMARY
This Flask application handles sensitive document uploads and API key management. The following audit identifies security vulnerabilities, configuration issues, bugs, and missing safeguards that must be addressed before production deployment.

---

## 🔴 CRITICAL SECURITY ISSUES

### 1. SESSION_COOKIE_SECURE Set to True in Development
**File:** [config.py:27](config.py#L27)
**Issue:** `SESSION_COOKIE_SECURE = True` will break the application in development (HTTP).
**Impact:** Application won't work locally without HTTPS, making development impossible.
**Fix Required:**
```python
SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') != 'development'
```

### 2. Production Server Binding to 0.0.0.0
**File:** [app.py:853](app.py#L853)
**Issue:** Application binds to all network interfaces (0.0.0.0) when not in debug mode.
**Impact:** Exposes application to entire network, security risk if not behind proper firewall/proxy.
**Fix Required:** Should bind to 127.0.0.1 and use reverse proxy (nginx/apache), or explicitly document requirement.

### 3. In-Memory Rate Limiting
**File:** [app.py:72](app.py#L72)
**Issue:** `storage_uri="memory://"` - Rate limiting uses in-memory storage.
**Impact:** Rate limits reset on application restart. In multi-process deployment, each worker has separate limits.
**Fix Required:** Use Redis for production: `storage_uri="redis://localhost:6379"`
**Code Comment:** Line 72 even has a comment: "# Use Redis in production"

### 4. Weak SECRET_KEY Detection Not Enforced
**File:** [config.py:12-21](config.py#L12-L21)
**Issue:** Default SECRET_KEY is weak, validation only warns but doesn't block in production.
**Current:** Raises ValueError only if FLASK_ENV != 'development'
**Problem:** If FLASK_ENV is not explicitly set, weak key could be used.
**Fix Required:** Should check `app.debug` flag or production environment more strictly.

### 5. Exception Information Disclosure
**File:** [app.py:794-797](app.py#L794-L797)
**Issue:** In debug mode, raw exception messages are returned to users.
**Impact:** Could expose internal paths, stack traces, or sensitive information.
**Status:** Partially mitigated by debug check, but should log more details server-side.

---

## 🟡 HIGH PRIORITY ISSUES

### 6. Missing API Key Validation
**File:** [alma_api.py:20](alma_api.py#L20), [llm_extractor.py:37](llm_extractor.py#L37)
**Issue:** No validation if API keys are None or empty strings before making requests.
**Impact:** Cryptic errors when API keys are missing. Better to fail fast with clear message.
**Fix Required:**
```python
if not self.api_key:
    raise ValueError("ALMA_API_KEY is required")
```

### 7. Broad Exception Catching
**File:** [alma_api.py:226](alma_api.py#L226)
**Issue:** Bare `except:` catches ALL exceptions, including KeyboardInterrupt and SystemExit.
**Impact:** Makes debugging harder, could hide critical errors.
**Fix Required:** `except Exception:` or specific exception types.

### 8. File Upload Directory Creation
**File:** [config.py:49](config.py#L49)
**Issue:** `UPLOAD_FOLDER` created at module import time, not at app runtime.
**Impact:** If directory creation fails, exception occurs during import, hard to debug.
**Fix Required:** Create directory in app startup, handle permission errors gracefully.

### 9. No Maximum Session File Count
**File:** [app.py:140-155](app.py#L140-L155)
**Issue:** Cleanup only removes files older than 24 hours, no limit on total count.
**Impact:** If someone abuses the upload endpoint, temp directory could fill with files.
**Fix Required:** Add max file count check and cleanup.

### 10. Gunicorn Default Configuration
**File:** [app.py:844-853](app.py#L844-L853)
**Issue:** Using Flask's built-in server for production (`app.run()`).
**Impact:** Flask's dev server is not production-ready (single-threaded, not secure).
**Fix Required:** Should use gunicorn/waitress with proper config file.
**Note:** requirements.txt includes gunicorn, but no config provided.

---

## 🟠 MEDIUM PRIORITY ISSUES

### 11. Hardcoded Timeout Values
**File:** [llm_extractor.py:33](llm_extractor.py#L33)
**Issue:** httpx timeout hardcoded to 180 seconds.
**Impact:** Cannot be adjusted without code change. Large documents might timeout.
**Fix Required:** Make configurable via environment variable.

### 12. Document Truncation Warning
**File:** [llm_extractor.py:15](llm_extractor.py#L15)
**Issue:** Documents limited to 15,000 characters with warning.
**Impact:** Users might not notice important terms were truncated.
**Fix Required:** Make MAX_DOCUMENT_LENGTH configurable, consider chunking strategy.

### 13. CSRF Token Endpoint Not Rate Limited
**File:** [app.py:270-275](app.py#L270-L275)
**Issue:** `/api/csrf-token` endpoint has no rate limiting.
**Impact:** Could be abused to enumerate valid tokens (though Flask-WTF generates unique tokens).
**Fix Required:** Add rate limiting: `@limiter.limit("100 per hour")`.

### 14. Session Data in Temp Directory
**File:** [app.py:364-368](app.py#L364-L368)
**Issue:** Session data stored in system temp directory with predictable names.
**Impact:** On shared hosting, other users might read temp files.
**Fix Required:** Use app-specific temp directory with proper permissions (0700).

### 15. No Input Sanitization on Vendor Code
**File:** [app.py:591](app.py#L591)
**Issue:** `vendor_code` sanitized but not validated against actual vendor list.
**Impact:** Could submit invalid vendor codes to Alma API.
**Fix Required:** Validate vendor code exists before submission.

### 16. Missing HTTPS Redirect Configuration
**File:** [app.py:40-62](app.py#L40-L62)
**Issue:** Talisman enforces HTTPS but no explicit redirect configuration shown.
**Impact:** Users accessing via HTTP might get blocked instead of redirected.
**Status:** Talisman should handle this, but verify in deployment.

### 17. Logging May Not Work in Production
**File:** [app.py:78-130](app.py#L78-L130)
**Issue:** Logs directory created at startup, but no check if writable.
**Impact:** If logs directory isn't writable, application might crash or silently fail.
**Fix Required:** Add permission check and graceful degradation.

### 18. No Health Check Endpoint
**Issue:** No `/health` or `/status` endpoint for monitoring.
**Impact:** Load balancers and monitoring tools can't verify app health.
**Fix Required:** Add simple health check endpoint.

---

## 🟢 LOW PRIORITY / BEST PRACTICES

### 19. Default Model Hardcoded
**File:** [config.py:44](config.py#L44)
**Issue:** Default LLM model is 'gpt-4' which may not exist on all LiteLLM proxies.
**Impact:** Might fail if proxy doesn't have that model.
**Fix Required:** Document model requirements or use safer default.

### 20. No Request ID in All Logs
**File:** [app.py:86](app.py#L86)
**Issue:** Request ID added to format but some logs might not include it.
**Impact:** Harder to trace requests across log entries.
**Fix Required:** Ensure all log entries have request context.

### 21. Magic Library Optional
**File:** [app.py:23-29](app.py#L23-L29)
**Issue:** python-magic is optional with fallback disabled.
**Impact:** File type validation bypassed if library not installed.
**Security:** Attacker could upload malicious files disguised as PDFs.
**Fix Required:** Make python-magic mandatory or implement alternative validation.

### 22. No Password/API Key Strength Validation
**Issue:** API keys stored in session without validation.
**Impact:** Users might enter weak or malformed keys.
**Fix Required:** Validate API key format before storing.

### 23. Session Cleanup Race Condition
**File:** [app.py:632-644](app.py#L632-L644)
**Issue:** Session file deleted while it might still be in use by other requests.
**Impact:** Race condition if user makes concurrent requests.
**Fix Required:** Use proper locking or mark for deletion instead of immediate delete.

### 24. No Content-Length Validation Before File Processing
**File:** [app.py:342-346](app.py#L342-L346)
**Issue:** File size checked AFTER upload completes.
**Impact:** Server processes large files before rejecting them.
**Fix Required:** Flask's MAX_CONTENT_LENGTH should handle this at HTTP level.

### 25. Error Messages Too Verbose
**File:** [alma_api.py:112-115](alma_api.py#L112-L115)
**Issue:** Full response text included in error messages.
**Impact:** Might leak sensitive API responses to user.
**Fix Required:** Sanitize error messages, log full details server-side only.

---

## MISSING COMPONENTS

### 26. No Test Suite
**Issue:** No unit tests, integration tests, or security tests found.
**Impact:** No automated validation of functionality or security.
**Fix Required:** Add pytest-based test suite covering:
- File upload validation
- Path traversal attacks
- CSRF protection
- Rate limiting
- API integration
- Error handling

### 27. No .env.example File
**Issue:** No template for required environment variables.
**Impact:** Developers don't know what variables are needed.
**Fix Required:** Create `.env.example` with all required variables.

### 28. No Database/State Management
**Issue:** All state in temp files and sessions.
**Impact:** Can't track users, audit logs, or persist data across restarts.
**Recommendation:** Consider adding database for audit trails.

### 29. No Rate Limiting on Static Resources
**Issue:** No rate limiting on serving HTML templates.
**Impact:** Could be used for DoS by requesting pages repeatedly.
**Fix Required:** Add global rate limits or use CDN.

### 30. No API Request/Response Logging
**Issue:** No logging of Alma API or LiteLLM requests/responses.
**Impact:** Hard to debug API integration issues.
**Fix Required:** Add structured logging for all external API calls.

---

## DEPLOYMENT CONFIGURATION ISSUES

### 31. No gunicorn.conf.py
**Issue:** requirements.txt includes gunicorn but no configuration file.
**Impact:** Will run with defaults (4 workers, sync workers).
**Fix Required:** Add gunicorn config with:
```python
workers = 4
worker_class = 'sync'
timeout = 300
bind = '127.0.0.1:8000'
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
```

### 32. No systemd Service File
**Issue:** No service configuration for production deployment.
**Impact:** Manual process management required.
**Fix Required:** Add systemd service file or Docker configuration.

### 33. No nginx/Apache Configuration
**Issue:** No reverse proxy configuration provided.
**Impact:** Application exposed directly to internet.
**Fix Required:** Add nginx config sample.

### 34. No Environment Variable Validation on Startup
**Issue:** Missing env vars only discovered when functionality is used.
**Impact:** Application starts but fails during use.
**Fix Required:** Validate all required env vars on startup.

---

## DEPENDENCY SECURITY

### 35. Outdated Dependencies (Need Verification)
**Issue:** Need to verify all dependencies for known vulnerabilities.
**Fix Required:** Run `pip-audit` or `safety check`.

### 36. No Dependency Pinning Hashes
**Issue:** requirements.txt has versions but no hashes.
**Impact:** Supply chain attack possible via compromised PyPI packages.
**Fix Required:** Use `pip-compile` with hashes or Poetry.

---

## RECOMMENDATIONS FOR PRODUCTION

1. **Use Environment-Based Configuration**
   - Create separate configs for dev/staging/prod
   - Never hardcode secrets

2. **Implement Structured Logging**
   - JSON logs for production
   - Include request IDs, user context, timing

3. **Add Monitoring & Alerting**
   - Application metrics (request count, latency, errors)
   - Health checks
   - Error tracking (Sentry, Rollbar)

4. **Implement Backup Strategy**
   - Session data backup
   - Log rotation and archival
   - Configuration backup

5. **Security Headers Audit**
   - Verify Talisman configuration
   - Add HSTS preload
   - Consider adding CSP report-uri

6. **API Integration Resilience**
   - Add retry logic with exponential backoff
   - Circuit breaker for external APIs
   - Graceful degradation

7. **User Input Validation**
   - Whitelist validation for all inputs
   - Sanitize before logging
   - Validate file contents deeply

---

## IMMEDIATE ACTION ITEMS (Before Production)

✅ **MUST FIX:**
1. Fix SESSION_COOKIE_SECURE conditional logic
2. Configure Redis for rate limiting
3. Create gunicorn configuration
4. Add nginx reverse proxy config
5. Set up proper logging with rotation
6. Create comprehensive test suite
7. Fix weak SECRET_KEY enforcement
8. Validate all API keys on initialization
9. Add .env.example file
10. Document deployment procedure

⚠️ **SHOULD FIX:**
1. Add health check endpoint
2. Implement proper error logging
3. Add API request/response logging
4. Create systemd service file
5. Add dependency hash pinning
6. Improve error messages
7. Add max session file count limit

💡 **NICE TO HAVE:**
1. Add monitoring integration
2. Implement audit logging
3. Add user activity tracking
4. Create admin dashboard
5. Add metrics endpoint

---

**END OF AUDIT REPORT**
