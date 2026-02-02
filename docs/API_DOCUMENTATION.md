# License Uploader - API Documentation

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Common Headers](#common-headers)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [API Endpoints](#api-endpoints)
  - [GET /](#get-)
  - [GET /api/csrf-token](#get-apicsrf-token)
  - [POST /api/config](#post-apiconfig)
  - [GET /api/config](#get-apiconfig)
  - [POST /upload](#post-upload)
  - [GET /review](#get-review)
  - [POST /refine-term](#post-refine-term)
  - [POST /submit-license](#post-submit-license)
  - [GET /test-connection](#get-test-connection)
  - [GET /get-vendors](#get-get-vendors)
  - [GET /api/prompt](#get-apiprompt)
  - [POST /api/prompt](#post-apiprompt)
  - [DELETE /api/prompt](#delete-apiprompt)

---

## Overview

The License Uploader provides a RESTful API for uploading license documents, extracting terms using AI, and submitting to Ex Libris Alma. The API is designed for web browser consumption with session-based authentication and CSRF protection.

**Architecture:**
- **Backend**: Flask Python web framework
- **Authentication**: Session-based with secure cookies
- **Security**: CSRF tokens, rate limiting, HTTPS enforcement
- **Data Format**: JSON (application/json)

---

## Base URL

**Development:**
```
http://localhost:5000
```

**Production:**
```
https://license-uploader.example.edu
```

Replace `license-uploader.example.edu` with your actual deployment domain.

---

## Authentication

The API uses **session-based authentication** with secure HTTP-only cookies.

### Session Management

**Session Cookie Name**: `session`

**Session Properties:**
- `HttpOnly`: Yes (prevents JavaScript access)
- `Secure`: Yes (HTTPS only in production)
- `SameSite`: Lax (CSRF protection)
- `Max-Age`: 3600 seconds (1 hour)

**Session Lifetime:**
- 1 hour of inactivity
- Permanent sessions disabled
- Sessions cleared after license submission

### No API Keys Required

The API does not require API keys for client requests. Backend API keys (Alma, LiteLLM) are configured server-side in the `.env` file.

---

## Common Headers

### Request Headers

All POST/PUT/DELETE requests must include:

```http
Content-Type: application/json
X-CSRFToken: <csrf-token>
```

**CSRF Token:**
- Required for all state-changing operations
- Obtain from `/api/csrf-token` endpoint
- Include in `X-CSRFToken` header or form field

### Response Headers

**Standard response headers:**
```http
Content-Type: application/json
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; ...
```

---

## Error Handling

### Error Response Format

All errors return JSON with the following structure:

```json
{
  "error": "Human-readable error message"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `200` | OK | Request successful |
| `400` | Bad Request | Invalid input, missing required fields |
| `413` | Payload Too Large | File exceeds 16 MB limit |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server-side error |

### Common Error Messages

**Upload Errors:**
- `"No file uploaded"` - File missing from request
- `"No file selected"` - Empty filename
- `"Invalid file type"` - Unsupported file format
- `"File too large. Maximum size is 16MB."` - File exceeds limit
- `"Uploaded file is empty. Please upload a file with content."` - Zero-byte file
- `"No text content could be extracted from the file."` - PDF is scanned image or corrupted
- `"Invalid file type detected: {mime}. Only PDF, DOCX, and TXT files are allowed."` - MIME type validation failure

**Session Errors:**
- `"No document in session"` - Session expired or upload not completed
- `"Session expired or invalid. Please upload your document again."` - Session timeout
- `"Session file not found"` - Temporary file deleted or corrupted

**Validation Errors:**
- `"License code is required"` - Missing required field
- `"License name is required"` - Missing required field
- `"End date must be after start date"` - Invalid date range
- `"Invalid date format. Please use YYYY-MM-DD format."` - Malformed date

**API Errors:**
- `"Error extracting terms with LLM: {error}"` - LLM service failure
- `"AI service took too long to respond (timeout after 180 seconds)."` - LLM timeout
- `"Error creating license: {error}"` - Alma API failure
- `"Error fetching vendors from Alma: {error}"` - Alma API connection failure

---

## Rate Limiting

The API implements rate limiting to prevent abuse and ensure fair usage.

### Global Limits

**Default limits:**
- 200 requests per day per IP
- 50 requests per hour per IP

### Endpoint-Specific Limits

| Endpoint | Limit | Reason |
|----------|-------|--------|
| `POST /upload` | 10 per hour | Heavy processing (file + LLM) |
| `POST /refine-term` | 30 per hour | LLM API call |
| `POST /submit-license` | 20 per hour | Alma API write operation |
| `POST /api/prompt` | 10 per hour | Administrative operation |
| `DELETE /api/prompt` | 10 per hour | Administrative operation |

### Rate Limit Headers

**Response headers when rate limited:**
```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1706745600
Retry-After: 3600
```

### Rate Limit Error Response

**HTTP 429 Too Many Requests:**
```json
{
  "error": "Rate limit exceeded. Please slow down and try again later.",
  "retry_after": "3600 seconds"
}
```

---

## API Endpoints

---

## GET /

### Description
Home page - returns HTML upload interface.

### Request

```http
GET / HTTP/1.1
Host: license-uploader.example.edu
```

### Response

**HTTP 200 OK**
```html
<!DOCTYPE html>
<html>
  <head><title>License Uploader</title></head>
  <body>...</body>
</html>
```

### Use Case
- Load the upload interface in a web browser
- Entry point for users

---

## GET /api/csrf-token

### Description
Get CSRF token for AJAX requests. Required for all POST/PUT/DELETE operations.

### Request

```http
GET /api/csrf-token HTTP/1.1
Host: license-uploader.example.edu
```

### Response

**HTTP 200 OK**
```json
{
  "csrf_token": "ImFjYzQ4NzQ3ZGU5ZjRhNmY4YjI3MmE4ZjE2OTY0NTIwYjNhMGY0YmEi.Z6Y8gw.xGqxTZ8lH5hPzF3VUcR8e8T0Kz4"
}
```

### Example Usage

**JavaScript:**
```javascript
// Get CSRF token
const response = await fetch('/api/csrf-token');
const data = await response.json();
const csrfToken = data.csrf_token;

// Use in subsequent requests
fetch('/upload', {
  method: 'POST',
  headers: {
    'X-CSRFToken': csrfToken
  },
  body: formData
});
```

---

## POST /api/config

### Description
Save API configuration in server-side session. Stores API keys securely without exposing to client.

### Request

```http
POST /api/config HTTP/1.1
Host: license-uploader.example.edu
Content-Type: application/json
X-CSRFToken: <csrf-token>

{
  "litellm_api_key": "sk-1234567890abcdef",
  "alma_api_key": "l7xx1234567890abcdef",
  "llm_model": "gpt-5"
}
```

**Request Body Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `litellm_api_key` | string | No | LiteLLM API key (overrides server default) |
| `alma_api_key` | string | No | Alma API key (overrides server default) |
| `llm_model` | string | No | LLM model to use (e.g., gpt-4, gpt-5) |

### Response

**HTTP 200 OK**
```json
{
  "success": true
}
```

**HTTP 400 Bad Request**
```json
{
  "error": "No configuration provided"
}
```

### Notes
- Configuration is stored in server-side session
- Session expires after 1 hour of inactivity
- Use this for per-user API key overrides
- Not required if using server-configured keys

---

## GET /api/config

### Description
Retrieve API configuration from server-side session.

### Request

```http
GET /api/config HTTP/1.1
Host: license-uploader.example.edu
```

### Response

**HTTP 200 OK**
```json
{
  "litellm_api_key": "sk-1234567890abcdef",
  "alma_api_key": "l7xx1234567890abcdef",
  "llm_model": "gpt-5"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `litellm_api_key` | string | LiteLLM API key (empty string if not set) |
| `alma_api_key` | string | Alma API key (empty string if not set) |
| `llm_model` | string | LLM model name (empty string if not set) |

### Notes
- Returns empty strings for unset values
- Used to restore configuration in UI

---

## POST /upload

### Description
Upload and process a license document. Extracts text and uses AI to extract license terms.

### Rate Limit
**10 requests per hour** (strict limit due to heavy processing)

### Request

```http
POST /upload HTTP/1.1
Host: license-uploader.example.edu
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary
X-CSRFToken: <csrf-token>

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="license.pdf"
Content-Type: application/pdf

<binary-file-data>
------WebKitFormBoundary--
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | file | Yes | License document (PDF, DOCX, or TXT) |

**File Requirements:**
- **Formats**: PDF, DOCX, TXT
- **Max size**: 16 MB
- **Content**: Must contain extractable text (not scanned images)

### Response

**HTTP 200 OK (Success)**
```json
{
  "success": true,
  "message": "Document processed successfully",
  "redirect": "/review"
}
```

**HTTP 200 OK (Success with truncation warning)**
```json
{
  "success": true,
  "message": "Document processed successfully",
  "redirect": "/review",
  "warning": "Document was truncated from 25000 to 15000 characters. Some terms in later sections may have been missed."
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always true for successful processing |
| `message` | string | Success message |
| `redirect` | string | URL to redirect to (review page) |
| `warning` | string | Optional truncation warning message |

**HTTP 400 Bad Request**
```json
{
  "error": "Invalid file type"
}
```

**HTTP 413 Payload Too Large**
```json
{
  "error": "File too large. Maximum size is 16MB."
}
```

**HTTP 500 Internal Server Error**
```json
{
  "error": "Error extracting terms with LLM: Connection timeout"
}
```

### Processing Steps

1. Validate file extension (.pdf, .docx, .txt)
2. Save file securely with sanitized filename
3. Validate file content using MIME type detection
4. Extract text from document
5. Send text to LLM for term extraction
6. Store results in server-side session
7. Clean up uploaded file
8. Return success with redirect URL

### Example Usage

**JavaScript (Fetch API):**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('/upload', {
  method: 'POST',
  headers: {
    'X-CSRFToken': csrfToken
  },
  body: formData
});

const result = await response.json();

if (result.success) {
  if (result.warning) {
    console.warn(result.warning);
  }
  window.location.href = result.redirect;
} else {
  console.error(result.error);
}
```

**cURL:**
```bash
curl -X POST https://license-uploader.example.edu/upload \
  -H "X-CSRFToken: <token>" \
  -F "file=@license.pdf"
```

---

## GET /review

### Description
Review and edit extracted license terms. Returns HTML page with form interface.

### Request

```http
GET /review HTTP/1.1
Host: license-uploader.example.edu
Cookie: session=<session-id>
```

### Response

**HTTP 200 OK**
```html
<!DOCTYPE html>
<html>
  <head><title>Review License Terms</title></head>
  <body>
    <!-- Review form with extracted terms -->
  </body>
</html>
```

**HTTP 302 Redirect (No session)**
```
Location: /
```

### Notes
- Requires active session with uploaded document
- Redirects to home page if no session
- Returns HTML form, not JSON

---

## POST /refine-term

### Description
Refine a specific license term using AI. Re-analyzes the document focusing on one term.

### Rate Limit
**30 requests per hour** (moderate limit due to LLM API call)

### Request

```http
POST /refine-term HTTP/1.1
Host: license-uploader.example.edu
Content-Type: application/json
X-CSRFToken: <csrf-token>
Cookie: session=<session-id>

{
  "term_code": "ARCHIVE",
  "current_value": "Permitted (Explicit)"
}
```

**Request Body Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `term_code` | string | Yes | License term code (e.g., ARCHIVE, FAIRUSE, GOVJUR) |
| `current_value` | string | No | Current extracted value (for context) |

### Response

**HTTP 200 OK**
```json
{
  "success": true,
  "value": "Permitted (Explicit)"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always true for successful refinement |
| `value` | string or null | Refined value or null if not found |

**HTTP 400 Bad Request**
```json
{
  "error": "Term code required"
}
```

**HTTP 400 Bad Request (Session expired)**
```json
{
  "error": "Session invalid. Please upload your document again."
}
```

**HTTP 500 Internal Server Error**
```json
{
  "error": "AI service took too long to respond (timeout after 180 seconds)."
}
```

### Example Usage

**JavaScript:**
```javascript
const response = await fetch('/refine-term', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({
    term_code: 'ARCHIVE',
    current_value: 'Silent'
  })
});

const result = await response.json();
console.log('Refined value:', result.value);
```

### Notes
- Requires active session with uploaded document
- Uses same LLM model as initial extraction
- Focuses analysis on specific term
- May return same value if document is ambiguous

---

## POST /submit-license

### Description
Submit license with all terms to Ex Libris Alma. Creates a new license record.

### Rate Limit
**20 requests per hour** (moderate limit for API write operations)

### Request

```http
POST /submit-license HTTP/1.1
Host: license-uploader.example.edu
Content-Type: application/json
X-CSRFToken: <csrf-token>
Cookie: session=<session-id>

{
  "basic_info": {
    "code": "LIC-2026-SPRINGER-001",
    "name": "SpringerLink Electronic Journals 2026",
    "type": "LICENSE",
    "status": "ACTIVE",
    "review_status": "INREVIEW",
    "vendor_code": "SPRINGER",
    "start_date": "2026-01-01",
    "end_date": "2026-12-31"
  },
  "terms": {
    "ARCHIVE": {
      "value": "Permitted (Explicit)",
      "type": "LicenseTermsPermittedProhibited",
      "name": "Archiving Right",
      "description": "..."
    },
    "FAIRUSE": {
      "value": "Yes",
      "type": "LicenseTermsYesNo",
      "name": "Fair Use Clause",
      "description": "..."
    }
  }
}
```

**Request Body Parameters:**

**basic_info** (object, required):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | Yes | Unique license code (max 50 chars) |
| `name` | string | Yes | License name (max 255 chars) |
| `type` | string | No | LICENSE, AMENDMENT, or ADDENDUM (default: LICENSE) |
| `status` | string | No | ACTIVE, DRAFT, EXPIRED, or RETIRED (default: ACTIVE) |
| `review_status` | string | No | INREVIEW, APPROVED, or PENDING (default: INREVIEW) |
| `vendor_code` | string | No | Vendor code from Alma (max 50 chars) |
| `start_date` | string | No | Start date in YYYY-MM-DD format |
| `end_date` | string | No | End date in YYYY-MM-DD format |

**terms** (object, optional):
- Key: term code (e.g., "ARCHIVE")
- Value: term object with `value`, `type`, `name`, `description`

### Response

**HTTP 200 OK**
```json
{
  "success": true,
  "message": "License created successfully",
  "license_code": "LIC-2026-SPRINGER-001"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always true for successful submission |
| `message` | string | Success message |
| `license_code` | string | Created license code (echoed from request) |

**HTTP 400 Bad Request (Validation error)**
```json
{
  "error": "License code is required"
}
```

**HTTP 400 Bad Request (Invalid dates)**
```json
{
  "error": "End date must be after start date"
}
```

**HTTP 500 Internal Server Error (Alma API error)**
```json
{
  "error": "Error creating license: API key invalid"
}
```

### Example Usage

**JavaScript:**
```javascript
const licenseData = {
  basic_info: {
    code: 'LIC-2026-001',
    name: 'Test License Agreement',
    type: 'LICENSE',
    status: 'ACTIVE',
    start_date: '2026-01-01',
    end_date: '2026-12-31'
  },
  terms: extractedTerms  // From review page
};

const response = await fetch('/submit-license', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify(licenseData)
});

const result = await response.json();
if (result.success) {
  console.log('License created:', result.license_code);
}
```

### Notes
- Requires active session with uploaded document
- Session and temporary files are cleared after submission
- Date validation: end_date must be after start_date
- Input sanitization applied to all text fields
- License code must be unique in Alma

---

## GET /test-connection

### Description
Test connection to Alma API. Verifies API key and network connectivity.

### Request

```http
GET /test-connection HTTP/1.1
Host: license-uploader.example.edu
Cookie: session=<session-id>
```

### Response

**HTTP 200 OK (Connection successful)**
```json
{
  "success": true,
  "message": "Connection successful"
}
```

**HTTP 500 Internal Server Error (Connection failed)**
```json
{
  "success": false,
  "message": "Connection failed"
}
```

### Example Usage

**JavaScript:**
```javascript
const response = await fetch('/test-connection');
const result = await response.json();

if (result.success) {
  console.log('Alma API connection OK');
} else {
  console.error('Alma API connection failed');
}
```

### Notes
- Tests Alma API connectivity by fetching 1 vendor record
- Uses API key from session config or server .env
- Useful for troubleshooting API configuration

---

## GET /get-vendors

### Description
Retrieve list of active vendors from Alma. Used for vendor selection in review form.

### Request

```http
GET /get-vendors HTTP/1.1
Host: license-uploader.example.edu
Cookie: session=<session-id>
```

### Response

**HTTP 200 OK**
```json
{
  "success": true,
  "vendors": [
    {
      "code": "SPRINGER",
      "name": "Springer Nature",
      "status": "active"
    },
    {
      "code": "ELSEVIER",
      "name": "Elsevier B.V.",
      "status": "active"
    }
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always true for successful retrieval |
| `vendors` | array | Array of vendor objects |

**Vendor Object:**

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Vendor code (used for linking) |
| `name` | string | Vendor display name |
| `status` | string | Vendor status (typically "active") |

**HTTP 500 Internal Server Error**
```json
{
  "success": false,
  "error": "Error fetching vendors from Alma: Unauthorized"
}
```

### Example Usage

**JavaScript:**
```javascript
const response = await fetch('/get-vendors');
const result = await response.json();

if (result.success) {
  const vendorSelect = document.getElementById('vendor-select');
  result.vendors.forEach(vendor => {
    const option = document.createElement('option');
    option.value = vendor.code;
    option.textContent = vendor.name;
    vendorSelect.appendChild(option);
  });
}
```

### Notes
- Returns up to 100 active vendors (default limit)
- Sorted alphabetically by name
- Requires valid Alma API key

---

## GET /api/prompt

### Description
Get the current AI extraction prompt template. Shows custom prompt if set, otherwise default.

### Request

```http
GET /api/prompt HTTP/1.1
Host: license-uploader.example.edu
```

### Response

**HTTP 200 OK (Custom prompt)**
```json
{
  "success": true,
  "prompt": "Analyze the following license agreement...",
  "is_custom": true
}
```

**HTTP 200 OK (Default prompt)**
```json
{
  "success": true,
  "prompt": "Analyze the following license agreement...",
  "is_custom": false
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always true for successful retrieval |
| `prompt` | string | Prompt template text |
| `is_custom` | boolean | True if custom prompt is active, false for default |

### Example Usage

**JavaScript:**
```javascript
const response = await fetch('/api/prompt');
const result = await response.json();

document.getElementById('prompt-textarea').value = result.prompt;
document.getElementById('custom-indicator').textContent =
  result.is_custom ? 'Custom' : 'Default';
```

---

## POST /api/prompt

### Description
Update the AI extraction prompt template. Saves custom prompt for all future extractions.

### Rate Limit
**10 requests per hour** (administrative operation)

### Request

```http
POST /api/prompt HTTP/1.1
Host: license-uploader.example.edu
Content-Type: application/json
X-CSRFToken: <csrf-token>

{
  "prompt": "Analyze the following license agreement...\n\n{terms_description}\n\n{document_text}"
}
```

**Request Body Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | New prompt template (must include placeholders) |

**Required placeholders:**
- `{terms_description}` - Replaced with license term definitions
- `{document_text}` - Replaced with uploaded document text

### Response

**HTTP 200 OK**
```json
{
  "success": true,
  "message": "Prompt updated successfully"
}
```

**HTTP 400 Bad Request (Validation error)**
```json
{
  "success": false,
  "error": "Prompt must contain placeholders: {terms_description}, {document_text}"
}
```

### Example Usage

**JavaScript:**
```javascript
const newPrompt = document.getElementById('prompt-textarea').value;

const response = await fetch('/api/prompt', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({ prompt: newPrompt })
});

const result = await response.json();
if (result.success) {
  alert('Prompt saved successfully');
}
```

### Notes
- Custom prompt applies to all users of the instance
- Changes take effect immediately for new uploads
- Prompt is saved to `custom_prompt.txt` file

---

## DELETE /api/prompt

### Description
Reset prompt template to default by deleting custom prompt file.

### Rate Limit
**10 requests per hour** (administrative operation)

### Request

```http
DELETE /api/prompt HTTP/1.1
Host: license-uploader.example.edu
X-CSRFToken: <csrf-token>
```

### Response

**HTTP 200 OK**
```json
{
  "success": true,
  "message": "Prompt reset to default"
}
```

### Example Usage

**JavaScript:**
```javascript
const response = await fetch('/api/prompt', {
  method: 'DELETE',
  headers: {
    'X-CSRFToken': csrfToken
  }
});

const result = await response.json();
if (result.success) {
  alert('Prompt reset to default');
  // Reload prompt
  location.reload();
}
```

### Notes
- Deletes `custom_prompt.txt` file if it exists
- Subsequent extractions use default prompt
- Idempotent operation (safe to call multiple times)

---

## Complete Workflow Example

### End-to-End License Upload

**1. Get CSRF Token**
```javascript
const csrfResponse = await fetch('/api/csrf-token');
const { csrf_token } = await csrfResponse.json();
```

**2. Upload Document**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('/upload', {
  method: 'POST',
  headers: { 'X-CSRFToken': csrf_token },
  body: formData
});

const uploadResult = await uploadResponse.json();
// uploadResult.redirect = "/review"
```

**3. Navigate to Review Page**
```javascript
window.location.href = uploadResult.redirect;
// User reviews and edits terms in browser
```

**4. Refine Specific Term (Optional)**
```javascript
const refineResponse = await fetch('/refine-term', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrf_token
  },
  body: JSON.stringify({
    term_code: 'FAIRUSE',
    current_value: null
  })
});

const { value } = await refineResponse.json();
// Update UI with refined value
```

**5. Submit to Alma**
```javascript
const submitResponse = await fetch('/submit-license', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrf_token
  },
  body: JSON.stringify({
    basic_info: {
      code: 'LIC-2026-001',
      name: 'Test License',
      type: 'LICENSE',
      status: 'ACTIVE'
    },
    terms: extractedTerms
  })
});

const submitResult = await submitResponse.json();
// submitResult.license_code = "LIC-2026-001"
```

---

## Data Models

### License Term Object

```json
{
  "value": "Permitted (Explicit)",
  "type": "LicenseTermsPermittedProhibited",
  "name": "Archiving Right",
  "description": "The right to permanently retain an electronic copy of the licensed materials."
}
```

### Term Types and Valid Values

**LicenseTermsYesNo:**
- `"Yes"`
- `"No"`

**LicenseTermsPermittedProhibited:**
- `"Permitted (Explicit)"`
- `"Permitted (Interpreted)"`
- `"Prohibited (Explicit)"`
- `"Prohibited (Interpreted)"`
- `"Silent"`
- `"Uninterpreted"`
- `"Not Applicable"`

**LicenseTermsRenewalType:**
- `"Explicit"`
- `"Automatic"`

**LicenseTermsUOM:**
- `"Week"`
- `"Calendar Day"`
- `"Month"`
- `"Business Day"`

**FREE-TEXT:**
- Any string (max 255 characters for most fields)

---

## Security Considerations

### CSRF Protection

**All state-changing requests require CSRF token:**
- POST /upload
- POST /refine-term
- POST /submit-license
- POST /api/config
- POST /api/prompt
- DELETE /api/prompt

**Obtain token:**
```javascript
const response = await fetch('/api/csrf-token');
const { csrf_token } = await response.json();
```

**Include in requests:**
```javascript
headers: {
  'X-CSRFToken': csrf_token
}
```

### Session Security

- **HttpOnly cookies**: Prevents JavaScript access
- **Secure flag**: HTTPS only (production)
- **SameSite=Lax**: CSRF protection
- **1 hour timeout**: Sessions expire after inactivity

### Input Validation

All inputs are validated:
- File type and size
- Date formats
- Required fields
- Text length limits
- Dangerous characters removed

### Rate Limiting

Prevents abuse and ensures fair usage:
- Global: 200/day, 50/hour per IP
- Upload: 10/hour
- Refine: 30/hour
- Submit: 20/hour

---

**Last Updated**: 2026-01-30
**Version**: 1.0
**Document Owner**: Technical Writer Agent
