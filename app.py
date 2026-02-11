"""
License Uploader Flask Application
"""
import os
import json
import tempfile
import time
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from config import Config
from document_parser import DocumentParser
from llm_extractor import LLMExtractor
from alma_api import AlmaAPI

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    import logging
    logging.warning("⚠️  WARNING: python-magic not installed. File content validation disabled!")
    logging.info("   Install with: pip install python-magic")


app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Enable CSRF protection
csrf = CSRFProtect(app)

# Enable HTTPS enforcement and security headers (in production only)
if not app.debug and os.getenv('FLASK_ENV') != 'development':
    talisman = Talisman(
        app,
        force_https=True,
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,  # 1 year
        strict_transport_security_include_subdomains=True,
        content_security_policy={
            'default-src': "'self'",
            'script-src': ["'self'", 'cdn.jsdelivr.net'],
            'style-src': ["'self'", 'cdn.jsdelivr.net', "'unsafe-inline'"],
            'img-src': ["'self'", 'data:'],
            'font-src': ["'self'", 'cdn.jsdelivr.net'],
            'connect-src': ["'self'"],
            'frame-ancestors': "'none'"
        },
        content_security_policy_nonce_in=['script-src'],
        feature_policy={
            'geolocation': "'none'",
            'camera': "'none'",
            'microphone': "'none'"
        }
    )
    app.logger.info("HTTPS enforcement enabled (Talisman)")
else:
    app.logger.warning("Running in development mode - HTTPS enforcement disabled")

# Enable rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=Config.RATE_LIMIT_STORAGE_URI,
    headers_enabled=True
)
app.logger.info(f"Rate limiting enabled (storage: {Config.RATE_LIMIT_STORAGE_URI})")

# Configure logging
def setup_logging():
    """Configure application logging with file rotation"""
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True, parents=True)

    # Configure logging format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s'
    )

    # Add filter to provide default request_id for non-request logs
    class RequestIdFilter(logging.Filter):
        def filter(self, record):
            if not hasattr(record, 'request_id'):
                # Try to get request_id from Flask request context
                try:
                    from flask import request
                    if hasattr(request, 'request_id'):
                        record.request_id = request.request_id
                    else:
                        record.request_id = 'system'
                except (RuntimeError, ImportError):
                    # No request context available
                    record.request_id = 'system'
            return True

    request_id_filter = RequestIdFilter()

    # File handler with rotation (10MB max, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_dir / 'license_uploader.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_format)
    file_handler.addFilter(request_id_filter)

    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    console_handler.setFormatter(log_format)
    console_handler.addFilter(request_id_filter)

    # Configure root logger
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    # Log startup
    app.logger.info('License Uploader application starting')

setup_logging()

# Add request ID to logs for tracking
@app.before_request
def before_request():
    """Add request ID to each request for logging"""
    request.request_id = os.urandom(4).hex()


def cleanup_old_temp_files():
    """Clean up temporary session files older than 24 hours"""
    temp_dir = Path(tempfile.gettempdir())
    current_time = time.time()
    max_age = 24 * 60 * 60  # 24 hours in seconds

    # Use pathlib's glob instead of glob.glob
    for filepath in temp_dir.glob('license_upload_*.json'):
        try:
            file_age = current_time - filepath.stat().st_mtime
            if file_age > max_age:
                filepath.unlink()  # pathlib's delete method
        except (OSError, PermissionError) as e:
            # Log but don't fail - cleanup is best-effort
            app.logger.debug(f"Could not clean up temp file {filepath}: {e}")


# Clean up old temp files on startup
cleanup_old_temp_files()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


# Allowed MIME types for file validation
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/msword',  # .doc (legacy)
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
    'text/plain',
    'application/octet-stream'  # Sometimes used for DOCX files
}


def validate_file_content(filepath):
    """
    Validate file content using magic numbers (MIME type detection)

    Args:
        filepath: Path to the file to validate

    Returns:
        tuple: (is_valid, error_message)

    Raises:
        None - returns (False, error) instead
    """
    if not MAGIC_AVAILABLE:
        # If python-magic is not available, skip validation
        return True, None

    try:
        # Detect MIME type from file content
        mime = magic.from_file(filepath, mime=True)

        if mime not in ALLOWED_MIME_TYPES:
            return False, f'Invalid file type detected: {mime}. Only PDF, DOCX, and TXT files are allowed.'

        # Additional check for file size
        file_size = Path(filepath).stat().st_size
        if file_size > Config.MAX_CONTENT_LENGTH:
            return False, f'File too large ({file_size} bytes). Maximum size is 16MB.'

        return True, None

    except Exception as e:
        # If validation fails, log but don't block
        app.logger.warning(f'File content validation error: {e}')
        return True, None  # Allow upload but log warning


def validate_session_file_path(session_file_path):
    """
    Validate session file path to prevent path traversal attacks (VULN-010)

    Args:
        session_file_path: Path from session cookie

    Returns:
        Path: Validated absolute Path object

    Raises:
        ValueError: If path is invalid or outside allowed directory
    """
    if not session_file_path:
        raise ValueError("No session file specified")

    try:
        # Convert to Path object and resolve to absolute path
        file_path = Path(session_file_path).resolve()

        # Get temp directory as Path object
        temp_dir = Path(tempfile.gettempdir()).resolve()

        # Ensure path is within temp directory (prevent path traversal)
        if not str(file_path).startswith(str(temp_dir)):
            app.logger.warning(f"Path traversal attempt detected: {session_file_path}")
            raise ValueError("Invalid session file path")

        # Check filename pattern (additional security layer)
        if not file_path.name.startswith('license_upload_'):
            app.logger.warning(f"Invalid session file pattern: {file_path.name}")
            raise ValueError("Invalid session file format")

        # Check file exists
        if not file_path.exists():
            raise ValueError("Session file not found")

        # Check file is a regular file (not symlink, device, etc.)
        if not file_path.is_file():
            raise ValueError("Session file is not a regular file")

        return file_path

    except (ValueError, OSError) as e:
        # Re-raise ValueError, convert OSError to ValueError
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Invalid session file path: {str(e)}")


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """
    Health check endpoint for monitoring and load balancers
    Returns basic system status and timestamp
    """
    from datetime import datetime
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'service': 'license_uploader'
    })


@app.route('/api/csrf-token', methods=['GET'])
def get_csrf_token():
    """
    Get CSRF token for AJAX requests
    """
    return jsonify({'csrf_token': generate_csrf()})


@app.route('/api/config', methods=['POST'])
def save_api_config():
    """
    Save API configuration in server-side session (not localStorage)
    Security: Keeps sensitive API keys server-side instead of in browser
    """
    data = request.json

    if not data:
        return jsonify({'error': 'No configuration provided'}), 400

    # Store in session (server-side, httpOnly cookies)
    session['api_config'] = {
        'litellm_api_key': data.get('litellm_api_key', ''),
        'alma_api_key': data.get('alma_api_key', ''),
        'llm_model': data.get('llm_model', 'gpt-5')
    }
    session.permanent = False  # Session expires when browser closes

    app.logger.info('API configuration saved to session')
    return jsonify({'success': True})


@app.route('/api/config', methods=['GET'])
def get_api_config():
    """
    Retrieve API configuration from server-side session
    Returns empty strings if not set
    """
    config = session.get('api_config', {})
    return jsonify({
        'litellm_api_key': config.get('litellm_api_key', ''),
        'alma_api_key': config.get('alma_api_key', ''),
        'llm_model': config.get('llm_model', 'gpt-5')
    })


@app.route('/upload', methods=['POST'])
@limiter.limit("10 per hour")  # Strict limit: file processing + LLM API call
def upload_file():
    """Handle file upload and extraction"""
    app.logger.info(f'File upload initiated from {request.remote_addr}')

    if 'file' not in request.files:
        app.logger.warning('Upload request missing file')
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        app.logger.warning('Upload request with empty filename')
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        app.logger.warning(f'Invalid file type attempted: {file.filename}')
        return jsonify({'error': 'Invalid file type'}), 400

    app.logger.info(f'Processing file: {file.filename}')

    try:
        # Save file
        filename = secure_filename(file.filename)
        filepath = Path(Config.UPLOAD_FOLDER) / filename
        file.save(str(filepath))

        # Check if file has content
        if filepath.stat().st_size == 0:
            filepath.unlink()
            return jsonify({'error': 'Uploaded file is empty. Please upload a file with content.'}), 400

        # Validate file content using magic numbers
        is_valid, error_message = validate_file_content(str(filepath))
        if not is_valid:
            filepath.unlink()
            app.logger.warning(f'File content validation failed: {error_message}')
            return jsonify({'error': error_message}), 400

        # Parse document with location tracking
        parser = DocumentParser(str(filepath))
        document_text = parser.parse_file()

        # Check if parsed text has content
        if not document_text or document_text.strip() == '':
            filepath.unlink()
            return jsonify({'error': 'No text content could be extracted from the file. Please check the file format.'}), 400

        # Store data in temporary files instead of session
        temp_dir = Path(tempfile.gettempdir())
        session_id = os.urandom(16).hex()

        data_file = temp_dir / f'license_upload_{session_id}.json'

        # Get API configuration from server session (not headers/localStorage)
        api_config = session.get('api_config', {})
        litellm_api_key = api_config.get('litellm_api_key')
        llm_model = api_config.get('llm_model')

        # Extract terms using LLM (citation validation feature disabled)
        extractor = LLMExtractor(
            api_key=litellm_api_key if litellm_api_key else None,
            model=llm_model if llm_model else None
        )
        # Note: document_parser parameter is no longer used for citation validation
        extraction_result = extractor.extract_license_terms(document_text, document_parser=parser)

        # Handle new format with truncation warning
        extracted_terms = extraction_result.get('terms', extraction_result)
        truncation_warning = extraction_result.get('truncation_warning')

        # Save to file with explicit UTF-8 encoding
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump({
                'document_text': document_text,
                'filename': filename,
                'extracted_terms': extracted_terms,
                'truncation_warning': truncation_warning
            }, f, ensure_ascii=False)

        # Store only the session ID in session
        session['data_file'] = str(data_file)
        session['filename'] = filename

        # Clean up uploaded file
        filepath.unlink()

        response_data = {
            'success': True,
            'message': 'Document processed successfully',
            'redirect': url_for('review')
        }

        # Add truncation warning to response if present
        if truncation_warning:
            response_data['warning'] = truncation_warning['message']

        return jsonify(response_data)

    except Exception as e:
        # Clean up temp file on error
        if 'data_file' in locals():
            try:
                Path(data_file).unlink(missing_ok=True)
            except Exception as cleanup_error:
                app.logger.debug(f"Could not clean up temp file: {cleanup_error}")
        # Clean up uploaded file on error
        if 'filepath' in locals():
            try:
                Path(filepath).unlink(missing_ok=True)
            except Exception as cleanup_error:
                app.logger.debug(f"Could not clean up uploaded file: {cleanup_error}")
        return jsonify({'error': str(e)}), 500


@app.route('/review')
def review():
    """Review and edit extracted terms"""
    if 'data_file' not in session:
        return redirect(url_for('index'))

    # Load data from file with path traversal protection
    try:
        # Validate session file path (prevent path traversal - VULN-010)
        file_path = validate_session_file_path(session['data_file'])

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        extracted_terms = data.get('extracted_terms', {})
        filename = data.get('filename', 'Unknown')
        truncation_warning = data.get('truncation_warning')
    except ValueError as e:
        # Path validation error - potential security issue
        app.logger.warning(f"Invalid session file access attempt from {request.remote_addr}: {e}")
        session.clear()
        return render_template('index.html',
            error='Session expired or invalid. Please upload your document again.')
    except FileNotFoundError:
        # Handle case where file was deleted
        app.logger.warning(f"Session file not found for {request.remote_addr}")
        session.clear()
        return render_template('index.html',
            error='Session expired or data lost. Please upload your document again.')
    except Exception as e:
        app.logger.error(f"Error loading session data: {e}", exc_info=True)
        session.clear()
        return render_template('index.html',
            error='Error loading session data. Please upload your document again.')

    # Get vendors from Alma
    try:
        # Get custom API configuration from headers if available
        api_config = session.get('api_config', {})
        alma_api_key = api_config.get('alma_api_key')

        alma = AlmaAPI(api_key=alma_api_key if alma_api_key else None)
        vendors = alma.get_vendors()
    except Exception as e:
        app.logger.error(f"Error fetching vendors: {e}", exc_info=True)
        vendors = []

    return render_template(
        'review.html',
        extracted_terms=extracted_terms,
        vendors=vendors,
        filename=filename,
        truncation_warning=truncation_warning
    )


@app.route('/refine-term', methods=['POST'])
@limiter.limit("30 per hour")  # Moderate limit: LLM API call
def refine_term():
    """Refine a specific term using LLM"""
    data = request.json
    term_code = data.get('term_code')
    current_value = data.get('current_value')

    if not term_code:
        return jsonify({'error': 'Term code required'}), 400

    if 'data_file' not in session:
        return jsonify({'error': 'No document in session'}), 400

    try:
        # Validate session file path (prevent path traversal - VULN-010)
        file_path = validate_session_file_path(session['data_file'])

        # Load document text from file
        with open(file_path, 'r', encoding='utf-8') as f:
            data_stored = json.load(f)
        document_text = data_stored.get('document_text')

        if not document_text:
            return jsonify({'error': 'No document text found'}), 400

        # Get custom API configuration from server session
        api_config = session.get('api_config', {})
        litellm_api_key = api_config.get('litellm_api_key')
        llm_model = api_config.get('llm_model')

        extractor = LLMExtractor(
            api_key=litellm_api_key if litellm_api_key else None,
            model=llm_model if llm_model else None
        )
        refined_value = extractor.refine_term(document_text, term_code, current_value)

        return jsonify({
            'success': True,
            'value': refined_value
        })

    except ValueError as e:
        # Path validation error
        app.logger.warning(f"Invalid session file access in refine-term from {request.remote_addr}: {e}")
        return jsonify({'error': 'Session invalid. Please upload your document again.'}), 400
    except Exception as e:
        app.logger.error(f"Error refining term: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


def sanitize_license_field(value, max_length=255, allow_special=False):
    """
    Sanitize license field input
    Args:
        value: Input value to sanitize
        max_length: Maximum allowed length
        allow_special: Whether to allow special characters
    Returns:
        Sanitized string
    """
    if not value:
        return value

    # Convert to string and strip whitespace
    sanitized = str(value).strip()

    # Enforce maximum length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    # Remove potentially dangerous characters if not allowing special chars
    if not allow_special:
        # Remove HTML/script tags and other dangerous characters
        dangerous_chars = ['<', '>', '{', '}', '\\', '`']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')

    return sanitized


@app.route('/submit-license', methods=['POST'])
@limiter.limit("20 per hour")  # Moderate limit: Alma API write operation
def submit_license():
    """Submit license to Alma"""
    data = request.json

    try:
        # Get custom API configuration from server session
        api_config = session.get('api_config', {})
        alma_api_key = api_config.get('alma_api_key')

        # Get and sanitize basic info
        basic_info = data.get('basic_info', {})

        # Validate and sanitize required fields
        if 'code' not in basic_info or not basic_info['code']:
            return jsonify({'error': 'License code is required'}), 400

        if 'name' not in basic_info or not basic_info['name']:
            return jsonify({'error': 'License name is required'}), 400

        if 'start_date' not in basic_info or not basic_info['start_date']:
            return jsonify({'error': 'Start date is required'}), 400

        # Sanitize all text fields
        basic_info['code'] = sanitize_license_field(basic_info.get('code'), max_length=50)
        basic_info['name'] = sanitize_license_field(basic_info.get('name'), max_length=255)

        if 'vendor_code' in basic_info:
            basic_info['vendor_code'] = sanitize_license_field(basic_info['vendor_code'], max_length=50)

        # Validate dates
        start_date = basic_info.get('start_date')
        end_date = basic_info.get('end_date')

        try:
            # Parse start date (required)
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            basic_info['start_date'] = start_dt.strftime('%Y-%m-%d')

            # Parse end date if present
            if end_date:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                basic_info['end_date'] = end_dt.strftime('%Y-%m-%d')

                # Validate that end_date is after start_date
                if end_dt <= start_dt:
                    return jsonify({'error': 'End date must be after start date'}), 400

        except (ValueError, AttributeError) as e:
            return jsonify({'error': f'Invalid date format. Please use YYYY-MM-DD format.'}), 400

        # Build license payload
        alma = AlmaAPI(api_key=alma_api_key if alma_api_key else None)
        app.logger.info(f"Submitting license with info: {json.dumps(basic_info, indent=2)}")

        # DEBUG: Log received terms data
        terms_data = data.get('terms')
        app.logger.debug("="*80)
        app.logger.debug("Received terms data from request:")
        app.logger.debug(json.dumps(terms_data, indent=2))
        app.logger.debug("="*80)

        license_payload = alma.build_license_payload(
            basic_info=basic_info,
            extracted_terms=terms_data
        )

        # DEBUG: Log the final Alma API license payload
        app.logger.debug("="*80)
        app.logger.debug("Final Alma API License Payload Being Sent:")
        app.logger.debug(json.dumps(license_payload, indent=2))
        app.logger.debug("="*80)

        app.logger.debug(f"License payload: {json.dumps(license_payload, indent=2)}")

        # Create license in Alma
        app.logger.info(f'Creating license in Alma: {basic_info.get("code")}')
        result = alma.create_license(license_payload)
        app.logger.info(f'License created successfully: {result.get("code")}')

        # Clean up temporary file and clear session
        if 'data_file' in session:
            try:
                # Validate path before deletion (prevent path traversal)
                file_path = validate_session_file_path(session['data_file'])
                file_path.unlink(missing_ok=True)
                app.logger.info('Cleaned up temporary session file')
            except ValueError as e:
                # Path validation error - potential security issue
                app.logger.warning(f'Invalid session file path during cleanup: {e}')
            except Exception as e:
                app.logger.warning(f'Failed to clean up temp file: {e}')
        session.clear()

        return jsonify({
            'success': True,
            'message': 'License created successfully',
            'license_code': result.get('code')
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/test-connection')
def test_connection():
    """Test Alma API connection"""
    try:
        # Get custom API configuration from headers if available
        api_config = session.get('api_config', {})
        alma_api_key = api_config.get('alma_api_key')

        alma = AlmaAPI(api_key=alma_api_key if alma_api_key else None)
        if alma.test_connection():
            return jsonify({'success': True, 'message': 'Connection successful'})
        else:
            return jsonify({'success': False, 'message': 'Connection failed'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/get-vendors')
def get_vendors():
    """Get list of vendors from Alma"""
    try:
        # Get custom API configuration from headers if available
        api_config = session.get('api_config', {})
        alma_api_key = api_config.get('alma_api_key')

        alma = AlmaAPI(api_key=alma_api_key if alma_api_key else None)
        vendors = alma.get_vendors()
        return jsonify({'success': True, 'vendors': vendors})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/prompt', methods=['GET'])
def get_prompt():
    """Get the current extraction prompt template"""
    try:
        # Try to load custom prompt
        custom_prompt = LLMExtractor.load_custom_prompt()

        if custom_prompt:
            return jsonify({
                'success': True,
                'prompt': custom_prompt,
                'is_custom': True
            })
        else:
            # Return default prompt
            return jsonify({
                'success': True,
                'prompt': LLMExtractor.get_default_prompt_template(),
                'is_custom': False
            })
    except Exception as e:
        app.logger.error(f"Error getting prompt: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/prompt', methods=['POST'])
@limiter.limit("10 per hour")  # Limit prompt updates
def update_prompt():
    """Update the extraction prompt template"""
    try:
        data = request.json
        prompt_text = data.get('prompt', '').strip()

        if not prompt_text:
            return jsonify({'success': False, 'error': 'Prompt text is required'}), 400

        # Validate that the prompt contains required placeholders
        required_placeholders = ['{terms_description}', '{document_text}']
        missing_placeholders = [p for p in required_placeholders if p not in prompt_text]

        if missing_placeholders:
            return jsonify({
                'success': False,
                'error': f'Prompt must contain placeholders: {", ".join(missing_placeholders)}'
            }), 400

        # Save the custom prompt
        LLMExtractor.save_custom_prompt(prompt_text)
        app.logger.info('Custom extraction prompt updated')

        return jsonify({
            'success': True,
            'message': 'Prompt updated successfully'
        })

    except Exception as e:
        app.logger.error(f"Error updating prompt: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/prompt', methods=['DELETE'])
@limiter.limit("10 per hour")
def reset_prompt():
    """Reset to default prompt by deleting custom prompt file"""
    try:
        prompt_file = Path(LLMExtractor.CUSTOM_PROMPT_FILE)
        if prompt_file.exists():
            prompt_file.unlink()
            app.logger.info('Custom extraction prompt reset to default')

        return jsonify({
            'success': True,
            'message': 'Prompt reset to default'
        })

    except Exception as e:
        app.logger.error(f"Error resetting prompt: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(413)
def file_too_large(e):
    """Handle file too large error"""
    app.logger.warning(f"File too large uploaded from {request.remote_addr}")
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded error"""
    app.logger.warning(f"Rate limit exceeded for {request.remote_addr}: {request.path}")
    return jsonify({
        'error': 'Rate limit exceeded. Please slow down and try again later.',
        'retry_after': e.description
    }), 429


@app.errorhandler(500)
def internal_server_error(e):
    """Handle internal server errors"""
    app.logger.error(f"Internal server error: {str(e)}", exc_info=True)

    if app.debug:
        return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'An internal error occurred. Please try again.'}), 500


# ============================================================================
# SECURITY HEADERS (for development mode - Talisman handles production)
# ============================================================================

@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""

    # In development mode, manually add security headers (Talisman handles production)
    if app.debug or os.getenv('FLASK_ENV') == 'development':
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' cdn.jsdelivr.net 'unsafe-inline'; "
            "style-src 'self' cdn.jsdelivr.net 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self' cdn.jsdelivr.net; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'

        # XSS Protection (legacy, but still good to include)
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # Remove server header (information disclosure - all modes)
    response.headers.pop('Server', None)

    # Permissions-Policy (formerly Feature-Policy) - all modes
    response.headers['Permissions-Policy'] = (
        'geolocation=(), camera=(), microphone=(), payment=(), usb=()'
    )

    return response


def cleanup_on_shutdown(signum=None, frame=None):
    """Cleanup resources on shutdown"""
    app.logger.info('Shutting down application...')
    # Flask and gunicorn handle port cleanup automatically
    # This function is here for any future cleanup needs
    app.logger.info('Cleanup complete')


if __name__ == '__main__':
    import signal
    import atexit

    # Register cleanup handlers
    signal.signal(signal.SIGTERM, cleanup_on_shutdown)
    signal.signal(signal.SIGINT, cleanup_on_shutdown)
    atexit.register(cleanup_on_shutdown)

    # Enable debug mode only in development environment
    debug_mode = os.getenv('FLASK_ENV') == 'development'

    if debug_mode:
        app.logger.warning("⚠️  DEBUG mode enabled - NOT FOR PRODUCTION!")
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        app.logger.info("Running in production mode")
        app.run(debug=False, host='0.0.0.0', port=5000)
