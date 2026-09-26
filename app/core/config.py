"""
Configuration settings for QueryMind.
Supports environment variables and .env configuration.
"""

import os
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_SQLITE_PATH = os.path.join(BASE_DIR, "database", "company.db")

class Settings(BaseSettings):
    APP_NAME: str = "QueryMind: Ambiguity-Aware Text-to-SQL System"
    API_V1_STR: str = "/api/v1"
    
    # LLM Settings
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Database Settings: Defaults to SQLite for instant local execution, switchable to Postgres
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
