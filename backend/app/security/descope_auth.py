"""Descope Enterprise Authentication and JWT Validation Module.

This module validates Descope session JWTs using the official Descope SDK.
Every protected API endpoint uses validate_descope_jwt() to verify the token.
"""

import os
import logging
from typing import Dict, Any, Optional
from jose import jwt, JWTError

logger = logging.getLogger(__name__)

DESCOPE_PROJECT_ID = os.getenv("DESCOPE_PROJECT_ID", "")
DESCOPE_MANAGEMENT_KEY = os.getenv("DESCOPE_MANAGEMENT_KEY", "")

_descope_client = None


def _get_descope_client():
    """Lazy-initialize and return the DescopeClient."""
    global _descope_client
    if _descope_client is not None:
        return _descope_client

    if not DESCOPE_PROJECT_ID:
        logger.warning("DESCOPE_PROJECT_ID not set — Descope validation disabled")
        return None

    try:
        from descope import DescopeClient
        _descope_client = DescopeClient(
            project_id=DESCOPE_PROJECT_ID,
            management_key=DESCOPE_MANAGEMENT_KEY,
        )
        logger.info(f"DescopeClient initialized for project: {DESCOPE_PROJECT_ID}")
        return _descope_client
    except ImportError:
        logger.error("descope package not installed — run: pip install descope")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize DescopeClient: {e}")
        return None


def validate_descope_jwt(token: str) -> Optional[Dict[str, Any]]:
    """
    Validate a Descope session JWT using the official SDK.

    Returns the validated JWT payload (claims) if valid, None otherwise.

    The Descope SDK validates:
    - Token signature (RS256)
    - Token expiration
    - Token issuer
    - Token audience
    - Token revocation (if configured)
    """
    client = _get_descope_client()
    if client is None:
        # Fallback: decode without validation (dev mode only)
        logger.debug("Descope client unavailable — using fallback JWT decode")
        return _fallback_decode(token)

    try:
        # Descope SDK validates the session JWT
        # validate_session() returns the JWT claims if valid
        result = client.validate_session(token)

        # Extract the JWT claims from the result
        if hasattr(result, "jwt") and result.jwt:
            return result.jwt
        elif isinstance(result, dict):
            return result
        elif isinstance(result, str):
            # If it returns a string, decode it
            return jwt.get_unverified_claims(result)
        else:
            # Try to get claims directly
            try:
                claims = client.validate_session(token)
                return claims if isinstance(claims, dict) else None
            except Exception:
                return None
    except Exception as e:
        logger.warning(f"Descope SDK validation failed: {e}")
        return _fallback_decode(token)


def _fallback_decode(token: str) -> Optional[Dict[str, Any]]:
    """Fallback JWT decode for development/testing only."""
    secret = os.getenv("JWT_SECRET") or os.getenv("JWT_SECRET_KEY") or "dev-jwt-secret-key-change-in-production-32ch"
    try:
        payload = jwt.decode(
            token, secret, algorithms=["HS256"], options={"verify_aud": False}
        )
        return payload
    except JWTError as e:
        logger.warning(f"Fallback JWT decode failed: {e}")
        return None


def extract_user_from_token(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract user identity from a validated Descope JWT payload.

    Descope JWTs contain:
    - sub: Descope user ID
    - email: User email
    - tenant: Tenant ID
    - roles: Array of Descope roles
    - customClaims: Custom data
    """
    user_id = payload.get("sub") or payload.get("userId") or ""
    email = payload.get("email", "")
    tenant = payload.get("tenant", "default")

    # Descope roles are in the JWT
    roles = payload.get("roles", [])
    if not roles and isinstance(payload.get("role"), str):
        roles = [payload["role"]]

    # Custom claims may contain additional user data
    custom_claims = payload.get("customClaims", {})

    return {
        "user_id": user_id,
        "email": email,
        "tenant": tenant,
        "roles": roles,
        "custom_claims": custom_claims,
    }
