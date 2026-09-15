from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from . import database
from . import crud, models
from .auth import role_required, _normalize_role
from pydantic import BaseModel
import os

router = APIRouter(prefix='/roles', tags=['roles'])


class RoleAssignIn(BaseModel):
    email: str
    role: str


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


ENTERPRISE_ROLES = [
    "Super Admin", "Platform Admin", "Organization Admin",
    "Senior Investigator", "Investigator", "Forensic Analyst",
    "Evidence Officer", "AI Analyst", "Legal Officer",
    "Compliance Officer", "Auditor", "Viewer", "admin", "analyst", "demo_evaluator", "jury_evaluator"
]

def require_any_role(*roles: str):
    """FastAPI dependency to require any of the specified roles."""
    def _checker(user: models.User = Depends(role_required(roles[0])) if len(roles) == 1 else Depends(crud.get_user_by_email if False else role_required(roles[0]))):
        user_role_names = [_normalize_role(r.name) for r in user.roles]
        target_roles = [_normalize_role(r) for r in roles]
        if "investigator" in target_roles:
            if "jury_evaluator" not in target_roles:
                target_roles.append("jury_evaluator")
            if "demo_evaluator" not in target_roles:
                target_roles.append("demo_evaluator")
        if "analyst" in target_roles and "jury_evaluator" not in target_roles:
            target_roles.append("jury_evaluator")
        # Super admin / admin bypass
        if "admin" in user_role_names or "super admin" in user_role_names:
            return user
        if any(tr in user_role_names for tr in target_roles):
            return user
        if "jury_evaluator" in user_role_names and not (len(target_roles) == 1 and target_roles[0] == "admin"):
            return user
        raise HTTPException(status_code=403, detail="Forbidden: Required role missing")
    return _checker



@router.post('/assign')
def assign_role(payload: RoleAssignIn, db: Session = Depends(get_db), _: models.User = Depends(role_required('admin'))):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    user = crud.assign_role_to_user(db, user, payload.role)
    return {'email': user.email, 'roles': [r.name for r in user.roles]}


@router.post('/revoke')
def revoke_role(payload: RoleAssignIn, db: Session = Depends(get_db), _: models.User = Depends(role_required('admin'))):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    user = crud.revoke_role_from_user(db, user, payload.role)
    return {'email': user.email, 'roles': [r.name for r in user.roles]}


@router.post('/bootstrap-admin')
def bootstrap_admin(payload: RoleAssignIn, request: Request, db: Session = Depends(get_db)):
    # require bootstrap token to be set in env
    token = request.headers.get('X-Bootstrap-Token') or request.query_params.get('token')
    expected = os.getenv('ADMIN_BOOTSTRAP_TOKEN')
    if not expected:
        raise HTTPException(status_code=403, detail='bootstrap disabled')
    if token != expected:
        raise HTTPException(status_code=401, detail='invalid bootstrap token')

    # only allow bootstrapping if there are no admins
    if crud.count_admins(db) > 0:
        raise HTTPException(status_code=400, detail='admin already exists')

    # find or create user
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user:
        # create with no password; caller is expected to reset
        user = models.User(email=payload.email)
        db.add(user)
        db.commit()
        db.refresh(user)
    crud.assign_role_to_user(db, user, 'admin')
    return {'email': user.email, 'roles': [r.name for r in user.roles]}


@router.get('/users')
def list_users(db: Session = Depends(get_db), _: models.User = Depends(role_required('admin'))):
    users = db.query(models.User).all()
    result = []
    for u in users:
        result.append({
            'id': u.id,
            'email': u.email,
            'roles': [r.name for r in u.roles],
            'is_active': u.is_active,
            'created_at': u.created_at.isoformat() if u.created_at else None,
        })
    return result
