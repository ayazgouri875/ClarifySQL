"""
Configuration settings for QueryMind Multi-Tenant SaaS.
Supports environment variables and .env configuration.
"""

import os
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_SQLITE_PATH = os.path.join(BASE_DIR, "database", "company.db")
DEFAULT_APP_DB_PATH = os.path.join(BASE_DIR, "database", "app.db")

class Settings(BaseSettings):
    APP_NAME: str = "QueryMind: Ambiguity-Aware Text-to-SQL SaaS"
    API_V1_STR: str = "/api/v1"
    
    # Application Multi-Tenant Database
    APP_DATABASE_URL: str = os.environ.get("APP_DATABASE_URL", f"sqlite:///{DEFAULT_APP_DB_PATH}")
    
    # JWT Authentication Secrets
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "querymind_enterprise_jwt_secret_key_2026_very_secure_string")
    JWT_REFRESH_SECRET_KEY: str = os.environ.get("JWT_REFRESH_SECRET_KEY", "querymind_refresh_jwt_secret_key_2026_very_secure_string")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database Credentials Encryption (AES-256-GCM Key, 32 bytes hex or url-safe string)
    DB_ENCRYPTION_KEY: str = os.environ.get("DB_ENCRYPTION_KEY", "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
    
    # SSRF & Network Security
    ALLOW_LOCAL_CONNECTIONS: bool = True  # Allows localhost/127.0.0.1 for local dev and testing
    BLOCKED_HOSTS: list[str] = [
        "169.254.169.254",   # AWS/Azure/GCP metadata endpoint
        "metadata.google.internal",
        "100.100.100.200"    # Alibaba metadata
    ]
    
    # LLM Settings
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Legacy / Default Demo Database Settings (Preserved for backwards compatibility)
    DATABASE_TYPE: str = "sqlite"  # 'sqlite' or 'postgres'
    DATABASE_URL: str = f"sqlite:///{DEFAULT_SQLITE_PATH}"
    POSTGRES_READONLY_URL: str = "postgresql://text2sql_readonly:Readonly_SafePass2026!@localhost:5432/company_db"
    
    # Security and Execution Limits
    MAX_RESULT_ROWS: int = 1000
    QUERY_TIMEOUT_SECONDS: int = 15
    DEFAULT_QUERY_LIMIT: int = 20
    
    # Reference Date for relative queries (Simulated Production Environment: Sept 2026)
    CURRENT_DATE: str = "2026-09-26"

settings = Settings()
