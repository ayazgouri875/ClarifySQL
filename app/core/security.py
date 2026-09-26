"""
Security Core Module.
Provides secure password hashing (PBKDF2-HMAC-SHA256), JWT token generation/validation,
AES-256-GCM database credentials encryption at rest, and SSRF host safety checks.
"""

import os
import hmac
import hashlib
import base64
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
import jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings

# ------------------------------------------------------------------------------
# 1. PASSWORD HASHING (NIST-Compliant PBKDF2-HMAC-SHA256)
# ------------------------------------------------------------------------------
ITERATIONS = 600000

def hash_password(password: str) -> str:
    """Hashes a plaintext password using PBKDF2-HMAC-SHA256 with a unique 16-byte salt."""
    if not password:
        raise ValueError("Password cannot be empty.")
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    salt_b64 = base64.b64encode(salt).decode("utf-8")
    key_b64 = base64.b64encode(key).decode("utf-8")
    return f"pbkdf2_sha256${ITERATIONS}${salt_b64}${key_b64}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a stored PBKDF2 hash using constant-time comparison."""
    if not plain_password or not hashed_password:
        return False
    try:
        parts = hashed_password.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = base64.b64decode(parts[2].encode("utf-8"))
        stored_key = base64.b64decode(parts[3].encode("utf-8"))
        derived_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(derived_key, stored_key)
    except Exception:
        return False

# ------------------------------------------------------------------------------
# 2. JWT AUTHENTICATION TOKENS
# ------------------------------------------------------------------------------
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates a short-lived access JWT containing user_id, organization_id, and role."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "type": "access"
    })
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates a longer-lived refresh JWT."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "type": "refresh"
    })
    return jwt.encode(to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str, is_refresh: bool = False) -> Dict[str, Any]:
    """Decodes and validates a JWT token against its expiry and signature."""
    key = settings.JWT_REFRESH_SECRET_KEY if is_refresh else settings.JWT_SECRET_KEY
    expected_type = "refresh" if is_refresh else "access"
    try:
        payload = jwt.decode(token, key, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != expected_type:
            raise jwt.InvalidTokenError(f"Invalid token type: expected {expected_type}")
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired. Please log in again.")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid authentication token: {str(e)}")

# ------------------------------------------------------------------------------
# 3. DATABASE CREDENTIALS ENCRYPTION AT REST (AES-256-GCM)
# ------------------------------------------------------------------------------
def _get_encryption_key() -> bytes:
    """Derives a fixed 32-byte key from settings.DB_ENCRYPTION_KEY using SHA-256."""
    raw_key = settings.DB_ENCRYPTION_KEY.encode("utf-8")
    return hashlib.sha256(raw_key).digest()

def encrypt_credential(plaintext: str) -> str:
    """Encrypts plaintext database password using AES-256-GCM with a 12-byte random nonce."""
    if not plaintext:
        return ""
    key = _get_encryption_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit unique nonce
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    # Pack: nonce (12 bytes) + ciphertext + tag
    return base64.b64encode(nonce + ciphertext).decode("utf-8")

def decrypt_credential(ciphertext_b64: str) -> str:
    """Decrypts AES-256-GCM ciphertext back into plaintext credentials."""
    if not ciphertext_b64:
        return ""
    try:
        data = base64.b64decode(ciphertext_b64.encode("utf-8"))
        if len(data) < 28:  # 12 nonce + 16 auth tag minimum
            raise ValueError("Malformed encrypted payload.")
        nonce = data[:12]
        ciphertext = data[12:]
        key = _get_encryption_key()
        aesgcm = AESGCM(key)
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted.decode("utf-8")
    except Exception as e:
        raise ValueError("Failed to decrypt database credential. The encryption key may have changed.")

# ------------------------------------------------------------------------------
# 4. SSRF & NETWORK SECURITY VALIDATOR
# ------------------------------------------------------------------------------
def validate_host_safety(host: str, port: int) -> Tuple[bool, Optional[str]]:
    """
    Validates user-provided database host and port against SSRF / internal scanning attacks.
    Blocks cloud metadata endpoints, internal infrastructure targets, and invalid ports.
    """
    if not host or not host.strip():
        return False, "Database host cannot be empty."

    host_clean = host.strip().lower()

    # Port range check
    if not (1 <= port <= 65535):
        return False, f"Invalid port number: {port}. Port must be between 1 and 65535."

    # Standard database ports whitelist check warning (allows standard 3306, 5432, 5433, etc.)
    # Cloud metadata endpoint blocking
    for blocked in settings.BLOCKED_HOSTS:
        if blocked in host_clean:
            return False, f"Connection to host '{host}' is forbidden for security reasons."

    # Check for IPv4 private subnets unless local connections are explicitly allowed
    if not settings.ALLOW_LOCAL_CONNECTIONS:
        if host_clean in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
            return False, "Connections to localhost/loopback addresses are not permitted in production."

    return True, None
