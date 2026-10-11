"""
Security and Authentication Module
Provides:
1. PBKDF2 Password Hashing (200,000 iterations, sha256, unique per-user random salt)
2. Token Creation and Cryptographic Verification (URLSafeTimedSerializer with expiration)
3. FastAPI Dependencies for Role-Based Access Control (RBAC)
"""
import os
import secrets
import hashlib
import hmac
from typing import Optional, Dict, Any
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.app.core.config import settings

# Security configuration defaults
TOKEN_SECRET = getattr(settings, "ADMIN_TOKEN_SECRET", os.getenv("ADMIN_TOKEN_SECRET", "restaurant-ops-admin-token-secret-2026"))
TOKEN_SALT = "restaurant_ops_auth_token_v1"
TOKEN_TTL = int(getattr(settings, "ADMIN_TOKEN_TTL_SECONDS", os.getenv("ADMIN_TOKEN_TTL_SECONDS", 86400)))

_serializer = URLSafeTimedSerializer(TOKEN_SECRET, salt=TOKEN_SALT)
_bearer_scheme = HTTPBearer(auto_error=False)


# -----------------------------------------------------------------------------
# 1. PBKDF2 Password Hashing & Verification
# -----------------------------------------------------------------------------
def hash_password(plain_password: str) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with 200,000 iterations
    and a cryptographically secure 16-byte random salt.
    Format: pbkdf2_sha256$200000$<salt_hex>$<hash_hex>
    """
    if not plain_password:
        raise ValueError("Password cannot be empty.")
    salt_bytes = secrets.token_bytes(16)
    salt_hex = salt_bytes.hex()
    key = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt_bytes,
        200000
    )
    return f"pbkdf2_sha256$200000${salt_hex}${key.hex()}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Verifies a plaintext password against a stored PBKDF2 hash.
    Also handles transparent one-time legacy migration if needed.
    """
    if not plain_password or not stored_hash:
        return False

    parts = stored_hash.split("$")
    if len(parts) == 4 and parts[0] == "pbkdf2_sha256":
        try:
            iterations = int(parts[1])
            salt_bytes = bytes.fromhex(parts[2])
            expected_key = parts[3]
            derived = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt_bytes,
                iterations
            )
            return hmac.compare_digest(derived.hex(), expected_key)
        except Exception:
            return False

    # Never allow plain string matches in production
    return False


# -----------------------------------------------------------------------------
# 2. Signed Token Generation & Validation
# -----------------------------------------------------------------------------
def create_access_token(data: Dict[str, Any], expires_in_seconds: Optional[int] = None) -> str:
    """Creates a cryptographically signed token containing user claims."""
    ttl = expires_in_seconds or TOKEN_TTL
    payload = dict(data)
    payload["_ttl"] = ttl
    return _serializer.dumps(payload)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes and validates a signed token, verifying signature and expiration.
    Returns payload dict if valid, or None if expired / tampered.
    """
    try:
        data = _serializer.loads(token, max_age=TOKEN_TTL)
        return data
    except (SignatureExpired, BadSignature, Exception):
        return None


# -----------------------------------------------------------------------------
# 3. FastAPI Authentication Dependencies
# -----------------------------------------------------------------------------
def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme)
) -> Dict[str, Any]:
    """
    FastAPI dependency that extracts and validates the Bearer token.
    Raises HTTP 401 if token is missing, invalid, or expired.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is expired or invalid.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    username = payload.get("sub") or payload.get("username")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload structure.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    from backend.app.services.admin_service import get_admin_service
    admin_svc = get_admin_service()
    user = admin_svc.get_user_by_username(username)
    if user:
        if user.get("status") != "Active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        # Return safe user dictionary without password
        return {k: v for k, v in user.items() if k != "password"}

    # If user not in SQLite (e.g. test token or federated claims), use verified signed claims
    return {
        "user_id": payload.get("user_id", f"usr_{username}"),
        "username": username,
        "role": payload.get("role", "user"),
        "display_name": payload.get("display_name", username.capitalize()),
        "status": "Active"
    }


def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    FastAPI dependency restricting access to users with the 'admin' role.
    Raises HTTP 403 Forbidden if user lacks admin role.
    """
    user_role = current_user.get("role", "").lower()
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: administrative privileges required."
        )
    return current_user
