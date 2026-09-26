import os
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
from cryptography.fernet import Fernet
from django.conf import settings
from sqlalchemy import create_engine, text

def get_fernet_cipher() -> Fernet:
    key = getattr(settings, "CREDENTIAL_ENCRYPTION_KEY", "wAaX_FkODWHVVFVhjMlTQW2rACiLWPJ_CinXLiF48L0=")
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)

def encrypt_credential(secret: str) -> str:
    if not secret:
        return ""
    cipher = get_fernet_cipher()
    return cipher.encrypt(secret.encode()).decode()

def decrypt_credential(encrypted_secret: str) -> str:
    if not encrypted_secret:
        return ""
    try:
        cipher = get_fernet_cipher()
        return cipher.decrypt(encrypted_secret.encode()).decode()
    except Exception:
        return ""

def resolve_sqlite_path(db_name: str) -> str:
    """Resolves SQLite path relative to backend root, project root, or absolute path."""
    p = Path(db_name)
    if p.is_absolute() and p.exists():
        return str(p)
    
    # Check relative to backend/
    backend_cand = settings.BASE_DIR / db_name
    if backend_cand.exists():
        return str(backend_cand)
        
    # Check relative to project root (parent of backend/)
    parent_cand = settings.BASE_DIR.parent / db_name
    if parent_cand.exists():
        return str(parent_cand)

    # Check database/ folder in project root
    db_folder_cand = settings.BASE_DIR.parent / "database" / db_name
    if db_folder_cand.exists():
        return str(db_folder_cand)

    # Default to resolved parent cand
    return str(parent_cand)

def build_connection_url(
    db_type: str,
    database_name: str,
    host: str = "localhost",
    port: int = 5432,
    username: str = "",
    password: str = "",
    ssl_enabled: bool = False
) -> str:
    db_type = db_type.lower()
    if db_type == "sqlite":
        resolved = resolve_sqlite_path(database_name)
        return f"sqlite:///{resolved}"
    elif db_type == "postgresql":
        base = f"postgresql://{username}:{password}@{host}:{port}/{database_name}"
        if ssl_enabled:
            base += "?sslmode=require"
        return base
    elif db_type == "mysql":
        base = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}"
        if ssl_enabled:
            base += "?ssl_ca=true"
        return base
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def test_connection_params(
    db_type: str,
    database_name: str,
    host: str = "localhost",
    port: int = 5432,
    username: str = "",
    password: str = "",
    ssl_enabled: bool = False
) -> Tuple[bool, str]:
    """Tests connectivity to a target database with a 5s timeout."""
    try:
        url = build_connection_url(
            db_type=db_type,
            database_name=database_name,
            host=host,
            port=port,
            username=username,
            password=password,
            ssl_enabled=ssl_enabled
        )
        engine = create_engine(url, connect_args={"connect_timeout": 5} if db_type == "postgresql" else {})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
        engine.dispose()
        return True, "Connection successful"
    except Exception as exc:
        return False, str(exc)

def get_engine_for_connection(connection_instance):
    """Creates a SQLAlchemy engine for a DatabaseConnection model instance."""
    password = decrypt_credential(connection_instance.encrypted_password)
    url = build_connection_url(
        db_type=connection_instance.db_type,
        database_name=connection_instance.database_name,
        host=connection_instance.host,
        port=connection_instance.port,
        username=connection_instance.username,
        password=password,
        ssl_enabled=connection_instance.ssl_enabled
    )
    return create_engine(url, pool_pre_ping=True)
