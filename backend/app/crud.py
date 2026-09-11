from sqlalchemy.orm import Session
from . import models
from passlib.hash import pbkdf2_sha256
from datetime import datetime


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, email: str, password: str):
    pwd = pbkdf2_sha256.hash(password)
    user = models.User(email=email, password_hash=pwd)
    # assign default role 'investigator' — matches frontend page guards
    role = db.query(models.Role).filter(models.Role.name == 'investigator').first()
    if not role:
        role = create_role(db, 'investigator', 'default investigator role')
    user.roles.append(role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def store_refresh_token(db: Session, user_id: str, token: str, expires_at: datetime):
    rt = models.RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(rt)
    db.commit()
    return rt


def get_refresh_token(db: Session, token: str):
    return db.query(models.RefreshToken).filter(models.RefreshToken.token == token).first()


def revoke_refresh_token(db: Session, rt: models.RefreshToken):
    rt.revoked = True
    db.add(rt)
    db.commit()
    return rt


# Case CRUD
def create_case(db: Session, title: str, description: str | None, created_by: str | None, priority: str | None = "medium"):
    c = models.Case(title=title, description=description, created_by=created_by, priority=priority)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def get_case(db: Session, case_id: str):
    return db.query(models.Case).filter(models.Case.id == case_id).first()


def list_cases(db: Session, limit: int = 100, offset: int = 0):
    return db.query(models.Case).order_by(models.Case.created_at.desc()).offset(offset).limit(limit).all()


def list_cases_paginated(
    db: Session,
    limit: int = 20,
    page: int = 1,
    search: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    assigned_to: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    q = db.query(models.Case)

    if search:
        term = f"%{search}%"
        q = q.filter(
            (models.Case.title.ilike(term))
            | (models.Case.description.ilike(term))
        )
    if status:
        q = q.filter(models.Case.status == status)
    if priority:
        q = q.filter(models.Case.priority == priority)
    if assigned_to:
        q = q.filter(models.Case.assigned_to == assigned_to)

    total = q.count()

    sort_col = getattr(models.Case, sort_by, models.Case.created_at)
    if sort_order == "asc":
        q = q.order_by(sort_col.asc())
    else:
        q = q.order_by(sort_col.desc())

    offset = (page - 1) * limit
    items = q.offset(offset).limit(limit).all()

    return items, total


def update_case(db: Session, case_id: str, **fields):
    c = get_case(db, case_id)
    if not c:
        return None
    for k, v in fields.items():
        if v is not None and hasattr(c, k):
            setattr(c, k, v)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def patch_case(db: Session, case_id: str, **fields):
    """Partial update — only set provided non-None fields."""
    c = get_case(db, case_id)
    if not c:
        return None
    for k, v in fields.items():
        if v is not None and hasattr(c, k):
            setattr(c, k, v)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def delete_case(db: Session, case_id: str):
    c = get_case(db, case_id)
    if not c:
        return False
    # Detach associated evidence before removing the case. This preserves the
    # forensic evidence records (and their chain of custody / MinIO objects) while
    # avoiding a foreign-key violation. Evidence remains in the library, orphaned
    # from the deleted case.
    db.query(models.Evidence).filter(models.Evidence.case_id == case_id).update(
        {models.Evidence.case_id: None}
    )
    db.delete(c)
    db.commit()
    return True


def assign_case(db: Session, case_id: str, user_id: str | None):
    """Assign or unassign a case. Pass None to unassign."""
    c = get_case(db, case_id)
    if not c:
        return None
    c.assigned_to = user_id
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


# Role management
def get_role_by_name(db: Session, name: str):
    return db.query(models.Role).filter(models.Role.name == name).first()


def create_role(db: Session, name: str, description: str | None = None):
    r = models.Role(name=name, description=description)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def assign_role_to_user(db: Session, user: models.User, role_name: str):
    role = get_role_by_name(db, role_name)
    if not role:
        role = create_role(db, role_name)
    if role not in user.roles:
        user.roles.append(role)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def revoke_role_from_user(db: Session, user: models.User, role_name: str):
    role = get_role_by_name(db, role_name)
    if role and role in user.roles:
        user.roles.remove(role)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def count_admins(db: Session):
    admin = get_role_by_name(db, 'admin')
    if not admin:
        return 0
    return db.query(models.User).join(models.user_roles).filter(models.user_roles.c.role_id == admin.id).count()

