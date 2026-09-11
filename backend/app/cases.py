from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from . import database
from . import crud, schemas, models
from .auth import role_required
from typing import Optional

router = APIRouter(prefix='/cases', tags=['cases'])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post('/', response_model=schemas.CaseOut)
def create_case(payload: schemas.CaseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(role_required(['user', 'investigator', 'admin']))):
    c = crud.create_case(db, payload.title, payload.description, current_user.id, payload.priority)
    return c


@router.get('/', response_model=schemas.CaseListResponse)
def list_cases(
    db: Session = Depends(get_db),
    _: models.User = Depends(role_required(['user', 'investigator', 'admin'])),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
):
    items, total = crud.list_cases_paginated(
        db, limit=limit, page=page, search=search,
        status=status, priority=priority, assigned_to=assigned_to,
        sort_by=sort_by, sort_order=sort_order,
    )
    return schemas.CaseListResponse(
        items=items, total=total, limit=limit, offset=(page - 1) * limit, page=page,
    )


@router.get('/{case_id}', response_model=schemas.CaseOut)
def get_case(case_id: str, db: Session = Depends(get_db), _: models.User = Depends(role_required(['user', 'investigator', 'admin']))):
    c = crud.get_case(db, case_id)
    if not c:
        raise HTTPException(status_code=404, detail='case not found')
    return c


@router.put('/{case_id}', response_model=schemas.CaseOut)
def update_case(case_id: str, payload: schemas.CaseUpdate, db: Session = Depends(get_db), _: models.User = Depends(role_required(['investigator', 'admin']))):
    c = crud.update_case(
        db, case_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        assigned_to=payload.assigned_to,
    )
    if not c:
        raise HTTPException(status_code=404, detail='case not found')
    return c


@router.patch('/{case_id}', response_model=schemas.CaseOut)
def patch_case(case_id: str, payload: schemas.CaseUpdate, db: Session = Depends(get_db), _: models.User = Depends(role_required(['user', 'investigator', 'admin']))):
    """Partial update — only sent fields are modified."""
    update_fields = payload.dict(exclude_unset=True, exclude_none=True)
    if not update_fields:
        raise HTTPException(status_code=400, detail='no fields to update')
    c = crud.patch_case(db, case_id, **update_fields)
    if not c:
        raise HTTPException(status_code=404, detail='case not found')
    return c


@router.patch('/{case_id}/assign', response_model=schemas.CaseOut)
def assign_case(case_id: str, payload: schemas.CaseUpdate, db: Session = Depends(get_db), _: models.User = Depends(role_required(['investigator', 'admin']))):
    c = crud.assign_case(db, case_id, payload.assigned_to)
    if not c:
        raise HTTPException(status_code=404, detail='case not found')
    return c


@router.delete('/{case_id}', status_code=204)
def delete_case(case_id: str, db: Session = Depends(get_db), _: models.User = Depends(role_required(['investigator', 'admin']))):
    # Legal hold protection — block deletion of a case under an active legal hold.
    try:
        from .compliance import DataRetentionService
        if DataRetentionService.is_under_legal_hold(db, case_id=case_id):
            raise HTTPException(
                status_code=409,
                detail='Case cannot be deleted: it is under an active legal hold',
            )
    except HTTPException:
        raise
    except Exception:
        pass  # If compliance module unavailable, proceed with deletion
    ok = crud.delete_case(db, case_id)
    if not ok:
        raise HTTPException(status_code=404, detail='case not found')
    return None
