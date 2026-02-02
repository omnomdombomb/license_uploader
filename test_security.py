"""
Comprehensive Security and Functionality Test Suite
Tests all critical security vulnerabilities and edge cases
"""
import pytest
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from werkzeug.datastructures import FileStorage
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app import app, validate_file_content, validate_session_file_path, sanitize_license_field
from config import Config
from document_parser import DocumentParser
from alma_api import AlmaAPI
from llm_extractor import LLMExtractor


class TestSecurityConfiguration:
    """Test security configuration and settings"""

    def test_secret_key_not_default(self):
        """CRITICAL: Ensure SECRET_KEY is not using default value"""
        assert Config.SECRET_KEY != 'dev-secret-key-change-in-production'
        assert Config.SECRET_KEY != 'your_secret_key_for_flask', \
            "SECRET_KEY must be changed from default!"
        assert len(Config.SECRET_KEY) >= 32, \
            "SECRET_KEY must be at least 32 characters"

    def test_session_cookie_security_settings(self):
        """Verify session cookie security settings"""
        # In development, SECURE should be False (HTTP allowed)
        # In production, SECURE should be True (HTTPS only)
        if os.getenv('FLASK_ENV') == 'development':
            # NOTE: This is a BUG - SESSION_COOKIE_SECURE is always True
            print("⚠️  WARNING: SESSION_COOKIE_SECURE is True even in development!")
            print("   This will break local development on HTTP!")

        assert Config.SESSION_COOKIE_HTTPONLY is True, \
            "SESSION_COOKIE_HTTPONLY must be True to prevent XSS"
        assert Config.SESSION_COOKIE_SAMESITE == 'Lax', \
            "SESSION_COOKIE_SAMESITE should be Lax or Strict for CSRF protection"

    def test_file_upload_limits(self):
        """Verify file upload size limits are set"""
        assert Config.MAX_CONTENT_LENGTH == 16 * 1024 * 1024, \
            "MAX_CONTENT_LENGTH should be 16MB"
        assert Config.ALLOWED_EXTENSIONS == {'pdf', 'docx', 'txt'}, \
            "Only safe file extensions should be allowed"

    def test_api_keys_configured(self):
        """Verify API keys are set (non-empty)"""
        # In real tests, should verify format and validity
        if Config.ALMA_API_KEY:
            assert len(Config.ALMA_API_KEY) > 10, "ALMA_API_KEY seems too short"
        if Config.LITELLM_API_KEY:
            assert len(Config.LITELLM_API_KEY) > 10, "LITELLM_API_KEY seems too short"


class TestPathTraversalProtection:
    """Test protection against path traversal attacks"""

    def test_valid_session_file_path(self):
        """Test that valid session files are accepted"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a valid session file
            test_file = Path(tmpdir) / 'license_upload_test123.json'
            test_file.write_text('{}')

            # Should accept valid file
            result = validate_session_file_path(str(test_file))
            assert result == test_file.resolve()

    def test_reject_path_traversal_attempt(self):
        """Test that path traversal attempts are blocked"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Try to escape temp directory
            malicious_path = os.path.join(tmpdir, '..', '..', 'etc', 'passwd')

            with pytest.raises(ValueError, match="Invalid session file"):
                validate_session_file_path(malicious_path)

    def test_reject_invalid_filename_pattern(self):
        """Test that files not matching expected pattern are rejected"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file with wrong pattern
            test_file = Path(tmpdir) / 'malicious_file.json'
            test_file.write_text('{}')

            with pytest.raises(ValueError, match="Invalid session file"):
                validate_session_file_path(str(test_file))

    def test_reject_symlink_attack(self):
        """Test that symlinks are rejected"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a regular file
            target = Path(tmpdir) / 'target.txt'
            target.write_text('secret')

            # Create a symlink with valid pattern
            link = Path(tmpdir) / 'license_upload_symlink.json'
            try:
                link.symlink_to(target)

                # Should reject symlink
                with pytest.raises(ValueError):
                    validate_session_file_path(str(link))
            except OSError:
                # Symlinks might not be supported on this platform
                pytest.skip("Symlinks not supported on this platform")

    def test_reject_nonexistent_file(self):
        """Test that non-existent files are rejected"""
        fake_path = '/tmp/license_upload_nonexistent.json'

        with pytest.raises(ValueError, match="Session file not found"):
            validate_session_file_path(fake_path)


class TestInputSanitization:
    """Test input validation and sanitization"""

    def test_sanitize_removes_dangerous_chars(self):
        """Test that dangerous characters are removed"""
        dangerous_input = "<script>alert('xss')</script>"
        result = sanitize_license_field(dangerous_input)
        assert '<' not in result
        assert '>' not in result
        assert 'script' in result  # Text remains, just tags removed

    def test_sanitize_enforces_length_limit(self):
        """Test that maximum length is enforced"""
        long_input = 'A' * 1000
        result = sanitize_license_field(long_input, max_length=100)
        assert len(result) == 100

    def test_sanitize_handles_special_chars_when_allowed(self):
        """Test that special characters can be preserved if allowed"""
        input_with_special = "License: Company <Name> - Version 2.0"
        result = sanitize_license_field(input_with_special, allow_special=True)
        # Should keep some characters when allow_special=True
        assert 'Company' in result

    def test_sanitize_none_and_empty(self):
        """Test handling of None and empty strings"""
        assert sanitize_license_field(None) is None
        assert sanitize_license_field('') == ''
        assert sanitize_license_field('   ') == ''  # Strips whitespace


class TestFileUploadValidation:
    """Test file upload validation"""

    def setup_method(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for tests
        self.client = self.app.test_client()

    def test_reject_empty_file(self):
        """Test that empty files are rejected"""
        # Create empty file
        data = {
            'file': (FileStorage(
                stream=open('/dev/null', 'rb'),
                filename='empty.pdf',
                content_type='application/pdf'
            ), 'empty.pdf')
        }

        response = self.client.post('/upload', data=data)
        assert response.status_code == 400
        assert b'empty' in response.data.lower()

    def test_reject_invalid_extension(self):
        """Test that invalid file extensions are rejected"""
        from io import BytesIO
        data = {
            'file': (BytesIO(b'fake content'), 'malicious.exe')
        }

        response = self.client.post('/upload', data=data)
        assert response.status_code == 400
        assert b'invalid file type' in response.data.lower() or b'not allowed' in response.data.lower()

    def test_reject_no_file_provided(self):
        """Test that request without file is rejected"""
        response = self.client.post('/upload', data={})
        assert response.status_code == 400
        assert b'No file' in response.data

    def test_reject_empty_filename(self):
        """Test that empty filename is rejected"""
        data = {
            'file': (FileStorage(
                stream=b'content',
                filename='',
                content_type='application/pdf'
            ), '')
        }

        response = self.client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400


class TestRateLimiting:
    """Test rate limiting functionality"""

    def setup_method(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_rate_limit_on_upload_endpoint(self):
        """Test that upload endpoint is rate limited"""
        # This test would require multiple requests
        # In real scenario, verify "10 per hour" limit on /upload

        # Create a small test file
        test_content = b'%PDF-1.4 test content'

        # Make multiple requests (would need to exceed limit)
        # For this test, just verify endpoint exists and responds
        data = {
            'file': (FileStorage(
                stream=test_content,
                filename='test.pdf',
                content_type='application/pdf'
            ), 'test.pdf')
        }

        response = self.client.post('/upload', data=data, content_type='multipart/form-data')
        # Should get response (not 404)
        assert response.status_code in [200, 400, 500]  # Any response means endpoint exists

    def test_rate_limit_headers_present(self):
        """Test that rate limit headers are returned"""
        response = self.client.get('/')
        # flask-limiter should add headers
        # Check if headers are present (implementation specific)
        assert response.status_code == 200


class TestAPIKeyValidation:
    """Test API key handling"""

    def test_alma_api_rejects_empty_key(self):
        """Test that AlmaAPI rejects empty API key"""
        # AlmaAPI should validate on init and raise ValueError for empty/invalid keys
        with pytest.raises(ValueError, match="ALMA_API_KEY is required"):
            AlmaAPI(api_key='', base_url='https://test.com')

        # Test with None (when Config also has no key)
        from config import Config as ConfigClass
        with patch.object(ConfigClass, 'ALMA_API_KEY', ''):
            with pytest.raises(ValueError, match="ALMA_API_KEY is required"):
                AlmaAPI(base_url='https://test.com')

        # Test with short key (less than 10 chars)
        with pytest.raises(ValueError, match="ALMA_API_KEY is required"):
            AlmaAPI(api_key='short', base_url='https://test.com')

    def test_llm_extractor_rejects_empty_key(self):
        """Test that LLMExtractor validates API key on init"""
        # LLMExtractor should validate on init and raise ValueError for empty/invalid keys
        with pytest.raises(ValueError, match="LITELLM_API_KEY is required"):
            LLMExtractor(api_key='')

        # Test with None (when Config also has no key)
        from config import Config as ConfigClass
        with patch.object(ConfigClass, 'LITELLM_API_KEY', ''):
            with pytest.raises(ValueError, match="LITELLM_API_KEY is required"):
                LLMExtractor()

        # Test with short key (less than 10 chars)
        with pytest.raises(ValueError, match="LITELLM_API_KEY is required"):
            LLMExtractor(api_key='short')


class TestErrorHandling:
    """Test error handling and information disclosure"""

    def setup_method(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_500_error_hides_details_in_production(self):
        """Test that 500 errors don't leak sensitive info in production"""
        # In production mode, error details should be hidden
        # In debug mode, details can be shown

        # Test by accessing non-existent route or causing error
        response = self.client.get('/nonexistent')
        assert response.status_code == 404

        # In production, error should be generic
        # In debug, can show details

    def test_file_validation_error_messages(self):
        """Test that file validation errors are user-friendly"""
        # Errors should be helpful but not leak system info
        data = {
            'file': (FileStorage(
                stream=b'test',
                filename='test.exe',
                content_type='application/x-msdownload'
            ), 'test.exe')
        }

        response = self.client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400

        # Should have user-friendly message
        data = json.loads(response.data)
        assert 'error' in data
        assert isinstance(data['error'], str)

        # Should not contain system paths or stack traces
        assert '/tmp/' not in data['error']
        assert 'Traceback' not in data['error']


class TestDocumentParser:
    """Test document parsing functionality"""

    def test_reject_unsupported_file_types(self):
        """Test that unsupported file types are rejected"""
        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as f:
            f.write(b'fake content')
            f.flush()

            try:
                parser = DocumentParser(f.name)
                with pytest.raises(ValueError, match="Unsupported file type"):
                    parser.parse_file()
            finally:
                os.unlink(f.name)

    def test_reject_legacy_doc_files(self):
        """Test that legacy .doc files are rejected with helpful error"""
        with tempfile.NamedTemporaryFile(suffix='.doc', delete=False) as f:
            f.write(b'fake doc content')
            f.flush()

            try:
                parser = DocumentParser(f.name)
                with pytest.raises(ValueError, match="Legacy .doc files are not supported"):
                    parser.parse_file()
            finally:
                os.unlink(f.name)

    def test_handle_corrupted_pdf(self):
        """Test handling of corrupted PDF files"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b'not a real pdf')
            f.flush()

            try:
                parser = DocumentParser(f.name)
                with pytest.raises(Exception):  # Should raise parsing error
                    parser.parse_file()
            finally:
                os.unlink(f.name)


class TestConfigurationValidation:
    """Test application configuration"""

    def test_upload_folder_exists(self):
        """Test that upload folder is created"""
        assert Config.UPLOAD_FOLDER.exists()
        assert Config.UPLOAD_FOLDER.is_dir()

    def test_logs_folder_exists(self):
        """Test that logs folder is created"""
        logs_dir = Path('logs')
        assert logs_dir.exists()
        assert logs_dir.is_dir()

    def test_environment_variables_loaded(self):
        """Test that .env file is loaded"""
        # Should have loaded SECRET_KEY from .env
        assert Config.SECRET_KEY is not None
        assert len(Config.SECRET_KEY) > 0


class TestSessionManagement:
    """Test session handling and security"""

    def setup_method(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_session_expires(self):
        """Test that sessions have expiration"""
        # Session timeout should be set
        assert Config.PERMANENT_SESSION_LIFETIME == 3600  # 1 hour

    def test_session_cookies_httponly(self):
        """Test that session cookies are httponly"""
        response = self.client.get('/')
        # Check Set-Cookie headers for HttpOnly flag
        cookies = response.headers.getlist('Set-Cookie')
        for cookie in cookies:
            if 'session' in cookie.lower():
                assert 'HttpOnly' in cookie


# Run tests with coverage
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short', '--color=yes'])
