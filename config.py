import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Security validation for SECRET_KEY
    if SECRET_KEY in ['dev-secret-key-change-in-production', 'your_secret_key_for_flask', '']:
        if os.getenv('FLASK_ENV') != 'development':
            raise ValueError(
                "CRITICAL SECURITY ERROR: Weak SECRET_KEY detected. "
                "Generate a strong key with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        print("⚠️  WARNING: Using default SECRET_KEY. Generate a secure key for production!")

    if len(SECRET_KEY) < 32:
        print(f"⚠️  WARNING: SECRET_KEY is short ({len(SECRET_KEY)} chars). Recommended: 64+ chars")

    # Session security
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') != 'development'  # Cookies only sent over HTTPS (disabled in dev)
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour session timeout

    UPLOAD_FOLDER = Path('uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    # Note: .doc (legacy MS Word) is not supported - only .docx (OOXML format)
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

    # Alma API
    ALMA_API_KEY = os.getenv('ALMA_API_KEY')
    ALMA_API_BASE_URL = os.getenv('ALMA_API_BASE_URL', 'https://api-na.hosted.exlibrisgroup.com')

    # LiteLLM
    LITELLM_API_KEY = os.getenv('LITELLM_API_KEY')
    LITELLM_BASE_URL = os.getenv('LITELLM_BASE_URL', 'https://ai-gateway.andrew.cmu.edu')
    LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gpt-5')

    # Rate Limiting
    # Use Redis in production for persistent rate limiting across restarts and multiple workers
    # Use memory storage in development for simplicity
    RATE_LIMIT_STORAGE_URI = os.getenv(
        'RATE_LIMIT_STORAGE_URI',
        'memory://' if os.getenv('FLASK_ENV') == 'development' else 'redis://localhost:6379/0'
    )

    @staticmethod
    def init_app(app):
        """Initialize application directories"""
        Config.UPLOAD_FOLDER.mkdir(exist_ok=True, parents=True)
