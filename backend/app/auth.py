from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import models
from . import database
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
import os
import re
import bcrypt
from .security.descope_auth import validate_descope_jwt
from .security.token_blacklist import get_token_blocklist

router = APIRouter(prefix="/auth", tags=["auth"])

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def is_auth_demo_mode() -> bool:
    """Return True if demo/development authentication mode is active."""
    val = os.getenv("AUTH_DEMO_MODE", "true").strip().lower()
    return val in ("true", "1", "yes", "on")


def is_valid_email(email: str) -> bool:
    """Validate basic email format."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

SECRET_KEY = os.getenv('JWT_SECRET') or os.getenv('JWT_SECRET_KEY') or "dev-jwt-secret-key-change-in-production-32ch"
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '15'))


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── Descope JWT Validation ─────────────────────────────────────────────────

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Validate the incoming JWT and return the local user record.

    Strategy:
    1. Try Descope SDK validation (primary).
    2. Fallback to local HS256 JWT decode (for dev/test).
    3. Extract user identity from the validated payload.
    4. Auto-provision Descope users in the local DB on first login.
    """
    payload = validate_descope_jwt(token)

    if not payload:
        # Try local JWT decode as final fallback
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=401, detail='Invalid or expired token')

    # Extract user identity from JWT
    user_id = payload.get('sub') or payload.get('userId', '')
    email = payload.get('email', '')

    if not user_id and not email:
        raise HTTPException(status_code=401, detail='Invalid token payload — no user identity')

    # Check token blocklist
    token_id = payload.get('jti', token[:16])
    if get_token_blocklist().is_blocked(token_id):
        raise HTTPException(status_code=401, detail='Token has been revoked')

    # Find or create local user
    user = None
    if email:
        user = db.query(models.User).filter(models.User.email == email).first()
    if not user and user_id:
        user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user and email:
        if is_auth_demo_mode():
            # Auto-provision Descope / OAuth authenticated user in demo mode
            user = _sync_descope_user(db, payload)
        else:
            raise HTTPException(status_code=401, detail='User not found')

    if not user:
        raise HTTPException(status_code=401, detail='User not found')

    return user


def _sync_descope_user(db: Session, payload: dict) -> models.User:
    """
    Create or update a local user record from Descope JWT claims.
    This is the user synchronization layer (Phase 4).
    """
    email = payload.get('email', '')
    user_id = payload.get('sub') or payload.get('userId', '')
    descope_roles = payload.get('roles', [])

    # Check if user already exists
    user = None
    if email:
        user = db.query(models.User).filter(models.User.email == email).first()
    if not user and user_id:
        user = db.query(models.User).filter(models.User.id == user_id).first()

    if user:
        # Update existing user
        user.email = email or user.email
        db.commit()
        db.refresh(user)
    else:
        # Create new user directly (without crud.create_user's default investigator role)
        user = models.User(
            email=email or f"{user_id}@descope.local",
            password_hash="",
        )
        db.add(user)

        # Map Descope roles to local roles
        role_map = {
            "admin": "admin",
            "investigator": "investigator",
            "viewer": "viewer",
        }
        assigned_role = False
        for descope_role in descope_roles:
            local_role_name = role_map.get(descope_role.lower(), descope_role.lower())
            local_role = db.query(models.Role).filter(
                models.Role.name == local_role_name
            ).first()
            if local_role:
                user.roles.append(local_role)
                assigned_role = True

        # Ensure at least investigator role if no Descope roles mapped
        if not assigned_role:
            default_role = db.query(models.Role).filter(
                models.Role.name == "investigator"
            ).first()
            if default_role:
                user.roles.append(default_role)

        db.commit()
        db.refresh(user)

    return user


# ─── Canonical Role/Permission Mapping ───────────────────────────────────────

_ROLE_CANONICAL_MAP = {
    "super admin":         "admin",
    "platform admin":      "admin",
    "organization admin":  "admin",
    "senior investigator": "investigator",
    "forensic analyst":    "analyst",
    "ai analyst":          "analyst",
    "evidence officer":    "evidence_officer",
    "legal officer":       "compliance_officer",
    "compliance officer":  "compliance_officer",
    "auditor":             "auditor",
    "viewer":              "viewer",
    "user":                "investigator",
    "admin":               "admin",
    "investigator":        "investigator",
    "analyst":             "analyst",
}

_ROLE_PERMISSIONS = {
    "admin":              ["case:read", "case:create", "case:update", "case:delete",
                           "evidence:read", "evidence:upload", "evidence:update", "evidence:delete",
                           "kg:query", "timeline:read", "search:query", "compliance:manage",
                           "audit:read", "user:manage", "analytics:read"],
    "investigator":       ["case:read", "case:create", "case:update",
                           "evidence:read", "evidence:upload", "evidence:update", "evidence:delete",
                           "kg:query", "timeline:read", "search:query", "analytics:read"],
    "analyst":            ["evidence:read", "kg:query", "timeline:read", "analytics:read"],
    "viewer":             ["evidence:read", "kg:query", "timeline:read"],
    "evidence_officer":   ["evidence:read", "evidence:upload", "evidence:update", "case:read", "timeline:read"],
    "compliance_officer": ["evidence:read", "case:read", "timeline:read", "kg:query"],
    "auditor":            ["evidence:read", "case:read", "audit:read"],
}


def _normalize_role(raw: str) -> str:
    return _ROLE_CANONICAL_MAP.get(raw.lower(), raw.lower())


# ─── Role Dependency ─────────────────────────────────────────────────────────

def role_required(allowed: str | list[str]):
    """Role verification dependency. Admin bypass included."""
    if isinstance(allowed, str):
        allowed_roles = [allowed]
    else:
        allowed_roles = allowed

    normalized_allowed = [r.lower() for r in allowed_roles]
    if "user" in normalized_allowed:
        normalized_allowed.extend(["investigator", "admin", "analyst", "viewer"])

    def _checker(user: models.User = Depends(get_current_user)):
        user_roles = [r.name.lower() for r in user.roles] if user.roles else []
        if "admin" in user_roles:
            return user
        if not user_roles:
            raise HTTPException(status_code=403, detail='forbidden: no roles assigned')
        if any(r in normalized_allowed for r in user_roles):
            return user
        raise HTTPException(status_code=403, detail='forbidden: insufficient permissions')
    return _checker


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post('/login')
def login(payload: dict, db: Session = Depends(get_db)):
    """Authenticate user with email/password. In demo mode, allows any valid email and auto-provisions missing users."""
    email = (payload.get("email") or "").strip()
    password = payload.get("password", "")

    if not email or not is_valid_email(email):
        raise HTTPException(status_code=422, detail="Enter a valid email address.")

    demo_mode = is_auth_demo_mode()
    user = db.query(models.User).filter(models.User.email == email).first()

    if demo_mode:
        # Development / Demo Mode: Allow any valid email.
        # Auto-provision user if they do not exist.
        if not user:
            user = models.User(
                email=email,
                password_hash="",
                is_active=True,
            )
            # Assign default investigator role
            default_role = db.query(models.Role).filter(models.Role.name == "investigator").first()
            if not default_role:
                default_role = models.Role(name="investigator", description="Default investigator role")
                db.add(default_role)
                db.flush()
            user.roles.append(default_role)
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            if not user.is_active:
                raise HTTPException(status_code=403, detail="Account disabled")
    else:
        # Production Mode: strict password verification & existing user check
        if not password:
            raise HTTPException(status_code=422, detail="email and password required")
        if not user or not user.password_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account disabled")

    raw_roles = [r.name for r in user.roles] if user.roles else ["investigator"]
    normalized_roles = list(dict.fromkeys(_normalize_role(r) for r in raw_roles))
    primary_role = normalized_roles[0] if normalized_roles else "investigator"

    all_permissions: list[str] = []
    for role in normalized_roles:
        all_permissions.extend(_ROLE_PERMISSIONS.get(role, []))
    permissions = list(dict.fromkeys(all_permissions))

    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "roles": normalized_roles}
    )
    refresh_token = create_access_token(
        data={"sub": user.id, "type": "refresh"},
        expires_delta=timedelta(days=7),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.email.split("@")[0] if user.email else "Investigator",
            "role": primary_role,
            "roles": normalized_roles,
            "permissions": permissions,
            "is_active": user.is_active,
            "organization": "CrimeKit Enterprise",
            "tenant": "default",
        },
    }


@router.post('/register')
def register(payload: dict, db: Session = Depends(get_db)):
    """Register a new user with email/password."""
    email = payload.get("email", "")
    password = payload.get("password", "")
    if not email or not password:
        raise HTTPException(status_code=422, detail="email and password required")

    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = models.User(
        email=email,
        password_hash=bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
    )
    db.add(user)
    db.flush()

    # Assign default investigator role
    default_role = db.query(models.Role).filter(models.Role.name == "investigator").first()
    if default_role:
        user.roles.append(default_role)

    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "roles": ["investigator"]}
    )
    refresh_token = create_access_token(
        data={"sub": user.id, "type": "refresh"},
        expires_delta=timedelta(days=7),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get('/me')
def get_me(current_user: models.User = Depends(get_current_user)):
    """Get the current user profile with normalized Descope-synced roles and permissions."""
    raw_roles = [r.name for r in current_user.roles] if current_user.roles else []
    normalized_roles = list(dict.fromkeys(_normalize_role(r) for r in raw_roles))
    primary_role = normalized_roles[0] if normalized_roles else "viewer"

    all_permissions: list[str] = []
    for role in normalized_roles:
        all_permissions.extend(_ROLE_PERMISSIONS.get(role, []))
    permissions = list(dict.fromkeys(all_permissions))

    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.email.split('@')[0] if current_user.email else "Investigator",
        "role": primary_role,
        "roles": normalized_roles,
        "permissions": permissions,
        "is_active": current_user.is_active,
        "organization": "CrimeKit Enterprise",
        "tenant": "default",
    }


# ─── Test Helpers ────────────────────────────────────────────────────────────
# NOTE: create_access_token is retained for test compatibility only.
# In production, Descope handles all token minting and refresh.


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": int(expire.timestamp())})
    encoded = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Tries Descope validation first, then local HS256 fallback.
    Returns the payload dict on success.
    Raises JWTError or HTTPException on failure.
    """
    payload = validate_descope_jwt(token)
    if payload:
        return payload

    # Fallback to local HS256 decode
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
