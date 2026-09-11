"""TSK forensic engine API routes — endpoints for disk image analysis."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..auth import get_current_user
from ..database import SessionLocal
from ..models import Evidence
from .integration import TSKIntegration
from .bindings import TSKBindings

router = APIRouter(prefix="/tsk", tags=["tsk-forensics"])

_integration: Optional[TSKIntegration] = None


def get_integration() -> TSKIntegration:
    global _integration
    if _integration is None:
        _integration = TSKIntegration()
    return _integration


class TSKProcessRequest(BaseModel):
    evidence_id: str
    case_id: str
    sync: bool = True


class TSKEnqueueRequest(BaseModel):
    evidence_id: str
    case_id: str
    priority: str = "high"


def _ensure_tsk_capable(evidence: Evidence) -> None:
    filename = (evidence.filename or "").lower()
    is_ewf = filename.endswith((".e01", ".ex01", ".ewf"))
    if is_ewf and not TSKBindings.ewf_capability()["supported"]:
        raise HTTPException(
            status_code=422,
            detail="E01/EWF analysis unavailable: libewf support is not installed.",
        )
    if not TSKBindings.is_available():
        raise HTTPException(status_code=422, detail="TSK analysis unavailable: pytsk3 is not installed.")


@router.get("/capabilities")
async def get_tsk_capabilities(
    current_user: Any = Depends(get_current_user),
) -> dict:
    return get_integration().get_tsk_capabilities()


@router.post("/process")
async def process_evidence(
    request: TSKProcessRequest,
    current_user: Any = Depends(get_current_user),
) -> dict:
    db = SessionLocal()
    try:
        evidence = db.query(Evidence).filter(Evidence.id == request.evidence_id).first()
        if not evidence:
            raise HTTPException(status_code=404, detail="Evidence not found")
        if evidence.case_id != request.case_id:
            raise HTTPException(status_code=403, detail="Evidence does not belong to this case")
        _ensure_tsk_capable(evidence)
    finally:
        db.close()

    if request.sync:
        return get_integration().process_evidence_sync(
            evidence_id=request.evidence_id,
            case_id=request.case_id,
        )
    else:
        return get_integration().enqueue_tsk_processing(
            evidence_id=request.evidence_id,
            case_id=request.case_id,
        )


@router.post("/enqueue")
async def enqueue_tsk_processing(
    request: TSKEnqueueRequest,
    current_user: Any = Depends(get_current_user),
) -> dict:
    db = SessionLocal()
    try:
        evidence = db.query(Evidence).filter(Evidence.id == request.evidence_id).first()
        if not evidence:
            raise HTTPException(status_code=404, detail="Evidence not found")
        if evidence.case_id != request.case_id:
            raise HTTPException(status_code=403, detail="Evidence does not belong to this case")
        _ensure_tsk_capable(evidence)
    finally:
        db.close()
    return get_integration().enqueue_tsk_processing(
        evidence_id=request.evidence_id,
        case_id=request.case_id,
        priority=request.priority,
    )


@router.get("/status/{job_id}")
async def get_processing_status(
    job_id: str,
    current_user: Any = Depends(get_current_user),
) -> dict:
    return get_integration().get_processing_status(job_id)
