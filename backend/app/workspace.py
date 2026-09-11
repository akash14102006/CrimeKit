from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import database, models
from .auth import get_current_user
from .workspace_service import WorkspaceService
from .workspace_schemas import (
    InvestigationWorkspaceResponse,
    WorkspaceEvidenceItem,
    WorkspaceCustodyEvent,
    WorkspaceTimelineEvent,
    WorkspaceKGSummary,
    WorkspaceAIFinding,
    WorkspaceProgress,
    WorkspaceRiskIndicator,
    CourtReportStatus,
)

router = APIRouter(prefix='/workspace', tags=['workspace'])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/cases/{case_id}', response_model=InvestigationWorkspaceResponse)
async def get_workspace(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get the complete investigation workspace for a case."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')

    roles = [r.name for r in current_user.roles]
    if 'admin' not in roles and 'investigator' not in roles and current_user.id != case.created_by:
        raise HTTPException(status_code=403, detail='Forbidden')

    service = WorkspaceService(db)
    return await service.get_workspace(case_id)


@router.get('/cases/{case_id}/evidence', response_model=List[WorkspaceEvidenceItem])
async def get_workspace_evidence(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get evidence for a case workspace."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')

    roles = [r.name for r in current_user.roles]
    if 'admin' not in roles and 'investigator' not in roles and current_user.id != case.created_by:
        raise HTTPException(status_code=403, detail='Forbidden')

    service = WorkspaceService(db)
    ws = await service.get_workspace(case_id)
    return ws.evidence


@router.get('/cases/{case_id}/custody', response_model=List[WorkspaceCustodyEvent])
async def get_workspace_custody(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get chain of custody for a case workspace."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')

    roles = [r.name for r in current_user.roles]
    if 'admin' not in roles and 'investigator' not in roles and current_user.id != case.created_by:
        raise HTTPException(status_code=403, detail='Forbidden')

    service = WorkspaceService(db)
    ws = await service.get_workspace(case_id)
    return ws.custody


@router.get('/cases/{case_id}/timeline', response_model=List[WorkspaceTimelineEvent])
async def get_workspace_timeline(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get timeline events for a case workspace."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')

    roles = [r.name for r in current_user.roles]
    if 'admin' not in roles and 'investigator' not in roles and current_user.id != case.created_by:
        raise HTTPException(status_code=403, detail='Forbidden')

    service = WorkspaceService(db)
    ws = await service.get_workspace(case_id)
    return ws.timeline


@router.get('/cases/{case_id}/progress', response_model=WorkspaceProgress)
async def get_workspace_progress(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get investigation progress for a case workspace."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')

    roles = [r.name for r in current_user.roles]
    if 'admin' not in roles and 'investigator' not in roles and current_user.id != case.created_by:
        raise HTTPException(status_code=403, detail='Forbidden')

    service = WorkspaceService(db)
    ws = await service.get_workspace(case_id)
    return ws.progress


@router.get('/cases/{case_id}/risks', response_model=List[WorkspaceRiskIndicator])
async def get_workspace_risks(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get risk indicators for a case workspace."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')

    roles = [r.name for r in current_user.roles]
    if 'admin' not in roles and 'investigator' not in roles and current_user.id != case.created_by:
        raise HTTPException(status_code=403, detail='Forbidden')

    service = WorkspaceService(db)
    ws = await service.get_workspace(case_id)
    return ws.risk_indicators


@router.get('/cases/{case_id}/kg-summary', response_model=WorkspaceKGSummary)
async def get_workspace_kg_summary(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get knowledge graph summary for a case workspace."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')

    roles = [r.name for r in current_user.roles]
    if 'admin' not in roles and 'investigator' not in roles and current_user.id != case.created_by:
        raise HTTPException(status_code=403, detail='Forbidden')

    service = WorkspaceService(db)
    ws = await service.get_workspace(case_id)
    return ws.knowledge_graph


@router.get('/cases/{case_id}/ai-findings', response_model=List[WorkspaceAIFinding])
async def get_workspace_ai_findings(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get AI findings for a case workspace."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')

    roles = [r.name for r in current_user.roles]
    if 'admin' not in roles and 'investigator' not in roles and current_user.id != case.created_by:
        raise HTTPException(status_code=403, detail='Forbidden')

    service = WorkspaceService(db)
    ws = await service.get_workspace(case_id)
    return ws.ai_findings


@router.get('/cases/{case_id}/court-report', response_model=CourtReportStatus)
async def get_workspace_court_report(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get court report status for a case workspace."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail='Case not found')

    roles = [r.name for r in current_user.roles]
    if 'admin' not in roles and 'investigator' not in roles and current_user.id != case.created_by:
        raise HTTPException(status_code=403, detail='Forbidden')

    service = WorkspaceService(db)
    ws = await service.get_workspace(case_id)
    return ws.court_report