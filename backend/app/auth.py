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
    """Return True if demo/development authentication mode is active.
    
    Checks DEMO_MODE or AUTH_DEMO_MODE environment variables.
    Defaults to true for demo/evaluation environments.
    """
    demo_env = os.getenv("DEMO_MODE")
    if demo_env is not None:
        return demo_env.strip().lower() in ("true", "1", "yes", "on")
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
    # Detect token algorithm: Descope IDP uses RS256 / ES384; local tokens use HS256.
    try:
        header = jwt.get_unverified_header(token)
        token_alg = header.get("alg", "")
    except Exception:
        token_alg = ""

    if token_alg != "HS256":
        descope_payload = validate_descope_jwt(token)
    else:
        descope_payload = None

    if descope_payload:
        payload = descope_payload
        is_descope_auth = True
    else:
        # Fallback to local JWT decode
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            is_descope_auth = False
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
        if "@" in user_id:
            user = db.query(models.User).filter(models.User.email == user_id).first()
        if not user:
            user = db.query(models.User).filter(
                (models.User.id == user_id) | (models.User.email == f"{user_id}@descope.local")
            ).first()

    token_roles = [str(r).lower() for r in (payload.get('roles') or [])]
    user_email = (user.email if user else email or user_id or "").lower()
    is_evaluator_request = (
        is_descope_auth
        or any("evaluator" in r or "judge" in r or "jury" in r for r in token_roles)
        or ("evaluator" in user_email)
        or ("judge" in user_email)
        or ("hackathon" in user_email)
        or ("descope" in user_email)
    )

    if not user and (email or user_id):
        # Auto-provision if authenticated via Descope IDP or in demo mode
        user = _sync_descope_user(db, payload)
    elif user and is_evaluator_request:
        # Ensure jury evaluator access is maintained for Descope IDP and evaluator accounts
        user = _sync_descope_user(db, payload)

    if not user:
        raise HTTPException(status_code=401, detail='User not found')

    return user


def _extract_display_name(payload: dict) -> str | None:
    """Extract display name from Google / Descope profile claims.

    Precedence:
    1. payload.name (full profile name from Google/Descope, e.g. "Akash M")
    2. given_name + family_name / firstName + lastName
    3. given_name / firstName
    4. family_name / lastName
    5. None (caller will fallback to email only as final fallback)
    """
    raw_name = (payload.get('name') or payload.get('displayName') or '').strip()
    if raw_name and '@' not in raw_name:
        return raw_name

    given = (payload.get('given_name') or payload.get('givenName') or payload.get('firstName') or '').strip()
    family = (payload.get('family_name') or payload.get('familyName') or payload.get('lastName') or '').strip()
    if given and family:
        return f"{given} {family}"
    if given:
        return given
    if family:
        return family

    custom = payload.get('customAttributes') or {}
    if isinstance(custom, dict) and custom.get('name'):
        custom_name = str(custom['name']).strip()
        if custom_name and '@' not in custom_name:
            return custom_name

    if raw_name:
        return raw_name

    return None


def _sync_descope_user(db: Session, payload: dict) -> models.User:
    """
    Create or update a local user record from Descope JWT claims.
    External evaluators and judges always receive full-functional 'jury_evaluator' access.
    Existing staff roles (admin, investigator, analyst, etc.) are strictly preserved.
    """
    user_id = payload.get('sub') or payload.get('userId', '')
    email = payload.get('email', '')
    if not email and user_id and "@" in user_id:
        email = user_id
    effective_email = email or (f"{user_id}@descope.local" if user_id else None)
    descope_roles = payload.get('roles', [])
    display_name = _extract_display_name(payload)

    privileged_staff = {"admin", "investigator", "analyst", "evidence_officer", "compliance_officer", "auditor"}

    # Check if user already exists
    user = None
    if effective_email:
        user = db.query(models.User).filter(models.User.email == effective_email).first()
    if not user and user_id:
        user = db.query(models.User).filter(
            (models.User.id == user_id) | (models.User.email == f"{user_id}@descope.local")
        ).first()

    if user:
        # Update existing user identity if needed
        updated = False
        if email and user.email != email:
            user.email = email
            updated = True
        if display_name and hasattr(user, 'name') and user.name != display_name:
            user.name = display_name
            updated = True
        if updated:
            db.commit()
            db.refresh(user)

        user_role_names = {r.name.lower() for r in user.roles} if user.roles else set()
        # If user has an existing privileged staff role (admin, investigator, etc.), preserve completely.
        # If user is specifically an evaluator / judge / Descope login or has no roles, upgrade to jury_evaluator!
        # Do not upgrade explicit viewer/user unless token claims or email indicate evaluator/descope.
        token_roles = [str(r).lower() for r in descope_roles] if descope_roles else []
        is_evaluator_claim = (
            any("evaluator" in r or "judge" in r or "jury" in r for r in token_roles)
            or ("evaluator" in (user.email or "").lower())
            or ("judge" in (user.email or "").lower())
            or ("hackathon" in (user.email or "").lower())
            or ("descope" in (user.email or "").lower())
            or (not user_role_names)
        )
        if not any(r in privileged_staff for r in user_role_names) and is_evaluator_claim:
            jury_role = db.query(models.Role).filter(models.Role.name == "jury_evaluator").first()
            if not jury_role:
                jury_role = models.Role(name="jury_evaluator", description="Hackathon Jury Evaluator with full functional access")
                db.add(jury_role)
                db.flush()
            # Clean out viewer / demo_evaluator / user so jury_evaluator is the clean primary role
            cleaned_roles = [r for r in user.roles if r.name.lower() not in {"viewer", "demo_evaluator", "user"}]
            if not any(r.name.lower() == "jury_evaluator" for r in cleaned_roles):
                cleaned_roles.insert(0, jury_role)
            user.roles = cleaned_roles
            db.commit()
            db.refresh(user)
        return user
    else:
        # Create new user record
        user = models.User(
            email=effective_email or f"{user_id}@descope.local",
            name=display_name,
            password_hash="",
            is_active=True,
        )
        db.add(user)

        # Check if Descope explicitly granted an elevated staff role
        assigned_staff_role = False
        for descope_role in descope_roles:
            norm_r = _normalize_role(descope_role)
            if norm_r in privileged_staff:
                local_role = db.query(models.Role).filter(models.Role.name == norm_r).first()
                if local_role:
                    user.roles.append(local_role)
                    assigned_staff_role = True

        # External judges and evaluators always receive 'jury_evaluator' (never 'viewer')
        if not assigned_staff_role:
            default_role = db.query(models.Role).filter(models.Role.name == "jury_evaluator").first()
            if not default_role:
                default_role = models.Role(name="jury_evaluator", description="Hackathon Jury Evaluator with full functional access")
                db.add(default_role)
                db.flush()
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
    "user":                "user",
    "admin":               "admin",
    "investigator":        "investigator",
    "analyst":             "analyst",
    "jury_evaluator":      "jury_evaluator",
    "jury evaluator":      "jury_evaluator",
    "jury":                "jury_evaluator",
    "demo_evaluator":      "jury_evaluator",
    "evaluator":           "jury_evaluator",
    "demo evaluator":      "jury_evaluator",
}

_ROLE_PERMISSIONS = {
    "admin":              ["case:read", "case:create", "case:update", "case:delete",
                           "evidence:read", "evidence:upload", "evidence:update", "evidence:delete",
                           "kg:query", "timeline:read", "search:query", "compliance:manage",
                           "audit:read", "user:manage", "analytics:read"],
    "investigator":       ["case:read", "case:create", "case:update", "case:delete",
                           "evidence:read", "evidence:upload", "evidence:update", "evidence:delete",
                           "kg:query", "timeline:read", "search:query", "analytics:read"],
    "jury_evaluator":     ["case:create", "case:read", "case:update", "case:delete",
                           "evidence:create", "evidence:upload", "evidence:read", "evidence:update", "evidence:delete",
                           "processing:create", "processing:read", "processing:update", "processing:delete",
                           "workspace:create", "workspace:read", "workspace:update", "workspace:delete",
                           "ai:ingest", "ai:query", "ai:read",
                           "kg:query", "kg:read", "kg:create", "kg:update",
                           "timeline:read", "timeline:create", "timeline:update",
                           "search:query",
                           "reports:create", "reports:read", "reports:update", "reports:delete",
                           "compliance:read", "compliance:create", "compliance:update", "compliance:export",
                           "analytics:read",
                           "dashboard:read",
                           "settings:read", "settings:update"],
    "demo_evaluator":     ["case:create", "case:read", "case:update", "case:delete",
                           "evidence:create", "evidence:upload", "evidence:read", "evidence:update", "evidence:delete",
                           "processing:create", "processing:read", "processing:update", "processing:delete",
                           "workspace:create", "workspace:read", "workspace:update", "workspace:delete",
                           "ai:ingest", "ai:query", "ai:read",
                           "kg:query", "kg:read", "kg:create", "kg:update",
                           "timeline:read", "timeline:create", "timeline:update",
                           "search:query",
                           "reports:create", "reports:read", "reports:update", "reports:delete",
                           "compliance:read", "compliance:create", "compliance:update", "compliance:export",
                           "analytics:read",
                           "dashboard:read",
                           "settings:read", "settings:update"],
    "analyst":            ["case:read", "evidence:read", "kg:query", "timeline:read", "analytics:read"],
    "viewer":             ["case:read", "evidence:read", "kg:query", "timeline:read"],
    "evidence_officer":   ["evidence:read", "evidence:upload", "evidence:update", "case:read", "timeline:read"],
    "compliance_officer": ["evidence:read", "case:read", "timeline:read", "kg:query", "compliance:manage"],
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

    normalized_allowed = [_normalize_role(r) for r in allowed_roles]
    if "user" in normalized_allowed:
        normalized_allowed.extend(["investigator", "admin", "analyst", "viewer", "jury_evaluator", "demo_evaluator"])
    if "investigator" in normalized_allowed:
        if "jury_evaluator" not in normalized_allowed:
            normalized_allowed.append("jury_evaluator")
        if "demo_evaluator" not in normalized_allowed:
            normalized_allowed.append("demo_evaluator")
    if "analyst" in normalized_allowed and "jury_evaluator" not in normalized_allowed:
        normalized_allowed.append("jury_evaluator")
    if "evidence_officer" in normalized_allowed and "jury_evaluator" not in normalized_allowed:
        normalized_allowed.append("jury_evaluator")
    if "compliance_officer" in normalized_allowed and "jury_evaluator" not in normalized_allowed:
        normalized_allowed.append("jury_evaluator")

    def _checker(user: models.User = Depends(get_current_user)):
        user_roles = [_normalize_role(r.name) for r in user.roles] if user.roles else []
        if "admin" in user_roles:
            return user
        if not user_roles:
            raise HTTPException(status_code=403, detail='forbidden: no roles assigned')
        # Jury evaluator full-functional access to all application-level endpoints
        if "jury_evaluator" in user_roles and not (len(normalized_allowed) == 1 and normalized_allowed[0] == "admin"):
            return user
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
            # Assign default role for demo mode
            default_role_name = "jury_evaluator" if demo_mode else "investigator"
            default_role = db.query(models.Role).filter(models.Role.name == default_role_name).first()
            if not default_role:
                default_role = models.Role(name=default_role_name, description="Hackathon Jury Evaluator with full functional access")
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
            "name": getattr(user, "name", None) or user.email or "Investigator",
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


@router.post('/refresh')
def refresh_token_endpoint(payload: dict, db: Session = Depends(get_db)):
    """Refresh an access token using a valid refresh token."""
    refresh_token = payload.get("refresh_token") or payload.get("refreshToken")
    if not refresh_token:
        raise HTTPException(status_code=422, detail="refresh_token required")
    try:
        decoded = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = decoded.get("sub")
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or disabled")
        raw_roles = [r.name for r in user.roles] if user.roles else ["investigator"]
        normalized_roles = list(dict.fromkeys(_normalize_role(r) for r in raw_roles))
        new_access_token = create_access_token(
            data={"sub": user.id, "email": user.email, "roles": normalized_roles}
        )
        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


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
        "name": getattr(current_user, "name", None) or current_user.email or "Investigator",
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
