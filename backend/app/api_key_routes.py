"""API Key management endpoints for machine-to-machine authentication.

Provides CRUD operations for API keys with secure generation,
hashing, rotation, and revocation.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import database, models
from .auth import get_current_user
from .security.api_keys import generate_api_key, hash_api_key, is_valid_format

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ApiKeyCreateIn(BaseModel):
    name: str
    environment: str = "live"
    expires_in_days: Optional[int] = None
    scopes: Optional[list[str]] = None


class ApiKeyOut(BaseModel):
    id: str
    name: str
    key_prefix: str
    environment: str
    is_active: bool
    created_at: str
    last_used_at: Optional[str]
    expires_at: Optional[str]
    scopes: Optional[list[str]]


class ApiKeyCreatedOut(ApiKeyOut):
    raw_key: str


@router.post("", response_model=ApiKeyCreatedOut, status_code=201)
def create_api_key(
    payload: ApiKeyCreateIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a new API key. The raw key is only shown once."""
    database.init_db()

    raw_key, key_hash = generate_api_key(payload.environment)
    key_prefix = raw_key[:12] + "..."

    expires_at = None
    if payload.expires_in_days:
        expires_at = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + __import__('datetime').timedelta(days=payload.expires_in_days)

    api_key = models.ApiKey(
        user_id=current_user.id,
        name=payload.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        environment=payload.environment,
        expires_at=expires_at,
        scopes=payload.scopes,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    audit = models.AuditLog(
        actor_id=current_user.id,
        action="api_key.create",
        target_type="api_key",
        target_id=api_key.id,
        detail={"name": payload.name, "environment": payload.environment},
    )
    db.add(audit)
    db.commit()

    return ApiKeyCreatedOut(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        environment=api_key.environment,
        is_active=api_key.is_active,
        created_at=api_key.created_at.isoformat() if api_key.created_at else "",
        last_used_at=api_key.last_used_at.isoformat() if api_key.last_used_at else None,
        expires_at=api_key.expires_at.isoformat() if api_key.expires_at else None,
        scopes=api_key.scopes,
        raw_key=raw_key,
    )


@router.get("", response_model=list[ApiKeyOut])
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List all API keys for the current user."""
    keys = (
        db.query(models.ApiKey)
        .filter(models.ApiKey.user_id == current_user.id)
        .order_by(models.ApiKey.created_at.desc())
        .all()
    )
    return [
        ApiKeyOut(
            id=k.id,
            name=k.name,
            key_prefix=k.key_prefix,
            environment=k.environment,
            is_active=k.is_active,
            created_at=k.created_at.isoformat() if k.created_at else "",
            last_used_at=k.last_used_at.isoformat() if k.last_used_at else None,
            expires_at=k.expires_at.isoformat() if k.expires_at else None,
            scopes=k.scopes,
        )
        for k in keys
    ]


@router.delete("/{key_id}")
def revoke_api_key(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Revoke (deactivate) an API key."""
    key = db.query(models.ApiKey).filter(
        models.ApiKey.id == key_id,
        models.ApiKey.user_id == current_user.id,
    ).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")

    key.is_active = False
    db.commit()

    audit = models.AuditLog(
        actor_id=current_user.id,
        action="api_key.revoke",
        target_type="api_key",
        target_id=key_id,
    )
    db.add(audit)
    db.commit()

    return {"detail": "API key revoked"}


@router.post("/{key_id}/rotate", response_model=ApiKeyCreatedOut)
def rotate_api_key(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Rotate an API key: revoke old, generate new."""
    key = db.query(models.ApiKey).filter(
        models.ApiKey.id == key_id,
        models.ApiKey.user_id == current_user.id,
    ).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")

    # Revoke old key
    key.is_active = False

    # Generate new key
    raw_key, key_hash = generate_api_key(key.environment)
    key.key_hash = key_hash
    key.key_prefix = raw_key[:12] + "..."
    key.is_active = True
    key.created_at = datetime.now(timezone.utc)
    key.last_used_at = None
    db.commit()
    db.refresh(key)

    audit = models.AuditLog(
        actor_id=current_user.id,
        action="api_key.rotate",
        target_type="api_key",
        target_id=key_id,
    )
    db.add(audit)
    db.commit()

    return ApiKeyCreatedOut(
        id=key.id,
        name=key.name,
        key_prefix=key.key_prefix,
        environment=key.environment,
        is_active=key.is_active,
        created_at=key.created_at.isoformat() if key.created_at else "",
        last_used_at=key.last_used_at.isoformat() if key.last_used_at else None,
        expires_at=key.expires_at.isoformat() if key.expires_at else None,
        scopes=key.scopes,
        raw_key=raw_key,
    )
