import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the MysteryMart application
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if it exists
load_dotenv(BASE_DIR / '.env')


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mysterymart-dev-secret-key-change-in-prod-2026')
    
    # SQL Database Configuration
    raw_db_url = os.environ.get('DATABASE_URL')
    if raw_db_url and raw_db_url.startswith('postgres://'):
        # Fix Render / Heroku legacy postgres:// schema for SQLAlchemy 1.4+ / 2.0+
        SQLALCHEMY_DATABASE_URI = raw_db_url.replace('postgres://', 'postgresql://', 1)
    elif raw_db_url:
        SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        # Default local SQLite database
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'mysterymart.db'}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
    }

    # NoSQL MongoDB Configuration (for chat logs and customer feedback)
    MONGODB_URI = os.environ.get('MONGODB_URI')
    MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME', 'mysterymart_nosql')

    # AI Provider Configuration
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'fallback')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

    # Third-Party Weather API
    WEATHER_API_URL = os.environ.get('WEATHER_API_URL', 'https://api.open-meteo.com/v1/forecast')
    WEATHER_API_TIMEOUT = int(os.environ.get('WEATHER_API_TIMEOUT', 4))

    # Session & Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days

    # Business Logic Defaults
    FREE_DELIVERY_THRESHOLD = 999.00
    STANDARD_DELIVERY_FEE = 99.00
    RATE_LIMIT_LOGIN_MAX = 5  # attempts per minute
    RATE_LIMIT_CHAT_MAX = 30   # requests per minute

    # Live Stream / Tunnel Direct Access Redirection
    REDIRECT_URL = os.environ.get('REDIRECT_URL', 'https://two-toes-shave.loca.lt/shop')
    ENABLE_RENDER_REDIRECT = os.environ.get('ENABLE_RENDER_REDIRECT', 'true').lower() in ('true', '1')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    WEATHER_API_TIMEOUT = 1
    # Use fallback mode for assistant in tests
    AI_PROVIDER = 'fallback'


class ProductionConfig(Config):
    """Production configuration for Render."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
