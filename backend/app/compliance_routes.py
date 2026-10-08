"""Enterprise Compliance API routes for GDPR, retention, legal holds, and audit."""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import database, models
from .auth import get_current_user
from .compliance import (
    ComplianceAuditService,
    ComplianceReport,
    ComplianceReportService,
    ComplianceReportType,
    DataClassification,
    DataClassificationService,
    DataDeletionRequest,
    DataRetentionPolicy,
    DataRetentionService,
    EvidenceExportService,
    CaseExportService,
    GDPRService,
    LegalHold,
    LegalHoldService,
    LegalHoldStatus,
    RetentionScheduleRun,
    RetentionScheduler,
)
from .multitenancy import TenantContext, TenantMiddleware

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/compliance", tags=["compliance"])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _require_admin(current_user: models.User):
    roles = [r.name.lower() for r in current_user.roles] if current_user.roles else []
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="forbidden: admin required")

def _require_admin_or_investigator(current_user: models.User):
    roles = [r.name.lower() for r in current_user.roles] if current_user.roles else []
    if "admin" not in roles and "investigator" not in roles and "jury_evaluator" not in roles and "demo_evaluator" not in roles:
        raise HTTPException(status_code=403, detail="forbidden: admin or investigator required")



def _get_org_id() -> Optional[str]:
    return TenantContext.get_org_id()


# ── Pydantic request models ──────────────────────────────────────────


class GDPRDeleteRequest(BaseModel):
    user_id: str
    reason: Optional[str] = None


class RetentionPolicyCreateRequest(BaseModel):
    name: str
    evidence_type: Optional[str] = None
    case_status: Optional[str] = None
    retention_days: int = 365
    classification: str = DataClassification.INTERNAL.value
    action_on_expiry: str = "archive"


class RetentionPolicyUpdateRequest(BaseModel):
    name: Optional[str] = None
    evidence_type: Optional[str] = None
    case_status: Optional[str] = None
    retention_days: Optional[int] = None
    classification: Optional[str] = None
    action_on_expiry: Optional[str] = None
    is_active: Optional[bool] = None


class LegalHoldCreateRequest(BaseModel):
    case_id: Optional[str] = None
    evidence_id: Optional[str] = None
    reason: str
    authority: Optional[str] = None


class ComplianceReportGenerateRequest(BaseModel):
    report_type: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    case_ids: Optional[List[str]] = None


class DataClassificationRequest(BaseModel):
    entity_type: str
    entity_id: str
    classification: str


# ── 1. POST /gdpr/delete ─────────────────────────────────────────────


@router.post("/gdpr/delete")
async def gdpr_request_deletion(
    body: GDPRDeleteRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Initiate a GDPR right-to-deletion request for a user."""
    _require_admin(current_user)
    try:
        org_id = _get_org_id()
        request_obj = GDPRService.create_deletion_request(
            db, user_id=body.user_id, reason=body.reason, org_id=org_id
        )
        return JSONResponse(
            status_code=201,
            content={
                "id": request_obj.id,
                "user_id": request_obj.user_id,
                "status": request_obj.status,
                "reason": request_obj.reason,
                "requested_at": request_obj.requested_at.isoformat() if request_obj.requested_at else None,
            },
        )
    except Exception as e:
        logger.error("GDPR deletion request failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── 2. GET /gdpr/status/{user_id} ────────────────────────────────────


@router.get("/gdpr/status/{user_id}")
async def gdpr_check_status(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Check the status of GDPR deletion requests for a user."""
    _require_admin_or_investigator(current_user)
    from .compliance import DataDeletionRequest as DeletionRequest

    requests = (
        db.query(DeletionRequest)
        .filter(DeletionRequest.user_id == user_id)
        .order_by(DeletionRequest.requested_at.desc())
        .all()
    )
    return JSONResponse(
        content={
            "user_id": user_id,
            "requests": [
                {
                    "id": r.id,
                    "status": r.status,
                    "reason": r.reason,
                    "requested_at": r.requested_at.isoformat() if r.requested_at else None,
                    "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                    "deleted_tables": r.deleted_tables,
                    "denied_reason": r.denied_reason,
                }
                for r in requests
            ],
            "total": len(requests),
        }
    )


# ── 3. POST /retention/policies ──────────────────────────────────────


@router.post("/retention/policies")
async def create_retention_policy(
    body: RetentionPolicyCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a new data retention policy."""
    _require_admin(current_user)
    try:
        policy = DataRetentionService.create_policy(
            db,
            name=body.name,
            retention_days=body.retention_days,
            evidence_type=body.evidence_type,
            case_status=body.case_status,
            classification=body.classification,
            action_on_expiry=body.action_on_expiry,
        )
        return JSONResponse(
            status_code=201,
            content={
                "id": policy.id,
                "name": policy.name,
                "evidence_type": policy.evidence_type,
                "case_status": policy.case_status,
                "retention_days": policy.retention_days,
                "classification": policy.classification,
                "action_on_expiry": policy.action_on_expiry,
                "is_active": policy.is_active,
                "created_at": policy.created_at.isoformat() if policy.created_at else None,
            },
        )
    except Exception as e:
        logger.error("Failed to create retention policy: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── 4. GET /retention/policies ────────────────────────────────────────


@router.get("/retention/policies")
async def list_retention_policies(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List all active data retention policies."""
    _require_admin_or_investigator(current_user)
    policies = db.query(DataRetentionPolicy).filter(DataRetentionPolicy.is_active == True).all()
    return JSONResponse(
        content={
            "policies": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "evidence_type": p.evidence_type,
                    "case_status": p.case_status,
                    "retention_days": p.retention_days,
                    "classification": p.classification,
                    "action_on_expiry": p.action_on_expiry,
                    "legal_hold_override": p.legal_hold_override,
                    "is_active": p.is_active,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                    "updated_at": p.updated_at.isoformat() if p.updated_at else None,
                }
                for p in policies
            ],
            "total": len(policies),
        }
    )


# ── 5. PUT /retention/policies/{policy_id} ────────────────────────────


@router.put("/retention/policies/{policy_id}")
async def update_retention_policy(
    policy_id: str,
    body: RetentionPolicyUpdateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update an existing data retention policy."""
    _require_admin(current_user)
    policy = db.query(DataRetentionPolicy).filter(DataRetentionPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    update_fields = body.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        if value is not None:
            setattr(policy, key, value)
    policy.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(policy)

    return JSONResponse(
        content={
            "id": policy.id,
            "name": policy.name,
            "evidence_type": policy.evidence_type,
            "case_status": policy.case_status,
            "retention_days": policy.retention_days,
            "classification": policy.classification,
            "action_on_expiry": policy.action_on_expiry,
            "is_active": policy.is_active,
            "updated_at": policy.updated_at.isoformat() if policy.updated_at else None,
        }
    )


# ── 6. DELETE /retention/policies/{policy_id} ─────────────────────────


@router.delete("/retention/policies/{policy_id}")
async def delete_retention_policy(
    policy_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Deactivate a data retention policy (soft delete)."""
    _require_admin(current_user)
    policy = db.query(DataRetentionPolicy).filter(DataRetentionPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    policy.is_active = False
    policy.updated_at = datetime.now(timezone.utc)
    db.commit()

    return JSONResponse(content={"detail": "Policy deactivated", "id": policy_id})


# ── 7. POST /retention/execute ────────────────────────────────────────


@router.post("/retention/execute")
async def execute_retention_policies(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Execute retention policies — run cleanup across all evidence."""
    _require_admin(current_user)
    try:
        org_id = _get_org_id()
        run = RetentionScheduler.run_scheduled_cleanup(db, org_id=org_id)
        return JSONResponse(
            content={
                "run_id": run.id,
                "status": run.status,
                "policies_evaluated": run.policies_evaluated,
                "items_expired": run.items_expired,
                "items_archived": run.items_archived,
                "items_deleted": run.items_deleted,
                "items_anonymized": run.items_anonymized,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "finished_at": run.finished_at.isoformat() if run.finished_at else None,
            }
        )
    except Exception as e:
        logger.error("Retention execution failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── 8. POST /legal-hold ──────────────────────────────────────────────


@router.post("/legal-hold")
async def place_legal_hold(
    body: LegalHoldCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Place a legal hold on a case or evidence item."""
    _require_admin(current_user)
    if not body.case_id and not body.evidence_id:
        raise HTTPException(status_code=400, detail="Either case_id or evidence_id is required")

    try:
        hold = LegalHoldService.place_hold(
            db,
            case_id=body.case_id,
            evidence_id=body.evidence_id,
            reason=body.reason,
            legal_reference=body.authority,
            placed_by=current_user.id,
        )
        return JSONResponse(
            status_code=201,
            content={
                "id": hold.id,
                "case_id": hold.case_id,
                "evidence_id": hold.evidence_id,
                "reason": hold.reason,
                "legal_reference": hold.legal_reference,
                "status": hold.status,
                "placed_by": hold.placed_by,
                "placed_at": hold.placed_at.isoformat() if hold.placed_at else None,
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to place legal hold: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── 9. DELETE /legal-hold/{hold_id} ───────────────────────────────────


@router.delete("/legal-hold/{hold_id}")
async def release_legal_hold(
    hold_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Release an active legal hold."""
    _require_admin(current_user)
    try:
        hold = LegalHoldService.release_hold(
            db, hold_id=hold_id, released_by=current_user.id
        )
        return JSONResponse(
            content={
                "id": hold.id,
                "status": hold.status,
                "released_by": hold.released_by,
                "released_at": hold.released_at.isoformat() if hold.released_at else None,
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── 10. GET /legal-hold ──────────────────────────────────────────────


@router.get("/legal-hold")
async def list_legal_holds(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List all active legal holds."""
    _require_admin_or_investigator(current_user)
    holds = LegalHoldService.list_active_holds(db)
    return JSONResponse(
        content={
            "holds": [
                {
                    "id": h.id,
                    "case_id": h.case_id,
                    "evidence_id": h.evidence_id,
                    "reason": h.reason,
                    "legal_reference": h.legal_reference,
                    "status": h.status,
                    "placed_by": h.placed_by,
                    "placed_at": h.placed_at.isoformat() if h.placed_at else None,
                    "notes": h.notes,
                }
                for h in holds
            ],
            "total": len(holds),
        }
    )


# ── 11. GET /legal-hold/check/{entity_type}/{entity_id} ───────────────


@router.get("/legal-hold/check/{entity_type}/{entity_id}")
async def check_legal_hold_status(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Check if a case or evidence item has an active legal hold."""
    _require_admin_or_investigator(current_user)
    if entity_type == "case":
        status = LegalHoldService.check_hold_status(db, case_id=entity_id)
    elif entity_type == "evidence":
        status = LegalHoldService.check_hold_status(db, evidence_id=entity_id)
    else:
        raise HTTPException(status_code=400, detail="entity_type must be 'case' or 'evidence'")

    return JSONResponse(content=status)


# ── 12. POST /reports/generate ────────────────────────────────────────


@router.post("/reports/generate")
async def generate_compliance_report(
    body: ComplianceReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Generate a compliance report (GDPR, ISO27001, SOC2, chain_of_custody, retention)."""
    _require_admin_or_investigator(current_user)
    org_id = _get_org_id()

    try:
        if body.report_type == ComplianceReportType.GDPR.value:
            report = ComplianceReportService.generate_gdpr_report(
                db,
                generated_by=current_user.id,
                period_start=body.start_date,
                period_end=body.end_date,
                org_id=org_id,
            )
        elif body.report_type == ComplianceReportType.ISO27001.value:
            report = ComplianceReportService.generate_iso27001_report(
                db,
                generated_by=current_user.id,
                period_start=body.start_date,
                period_end=body.end_date,
                org_id=org_id,
            )
        elif body.report_type == ComplianceReportType.SOC2.value:
            report = ComplianceReportService.generate_soc2_report(
                db,
                generated_by=current_user.id,
                period_start=body.start_date,
                period_end=body.end_date,
                org_id=org_id,
            )
        elif body.report_type == ComplianceReportType.RETENTION.value:
            report = ComplianceReportService.generate_retention_report(
                db,
                generated_by=current_user.id,
                period_start=body.start_date,
                period_end=body.end_date,
                org_id=org_id,
            )
        elif body.report_type == ComplianceReportType.CHAIN_OF_CUSTODY.value:
            if not body.case_ids or len(body.case_ids) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="case_ids is required for chain_of_custody reports",
                )
            report = ComplianceReportService.generate_chain_of_custody_report(
                db,
                evidence_id=body.case_ids[0],
                generated_by=current_user.id,
                org_id=org_id,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid report_type: {body.report_type}",
            )

        return JSONResponse(
            status_code=201,
            content={
                "id": report.id,
                "report_type": report.report_type,
                "title": report.title,
                "generated_by": report.generated_by,
                "generated_at": report.generated_at.isoformat() if report.generated_at else None,
                "period_start": report.period_start.isoformat() if report.period_start else None,
                "period_end": report.period_end.isoformat() if report.period_end else None,
                "content": report.content,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to generate compliance report: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── 13. GET /reports ─────────────────────────────────────────────────


@router.get("/reports")
async def list_compliance_reports(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List available compliance reports."""
    _require_admin_or_investigator(current_user)
    from .compliance import ComplianceReport as ReportModel

    org_id = _get_org_id()
    query = db.query(ReportModel)
    if org_id:
        query = query.filter(ReportModel.org_id == org_id)

    reports = query.order_by(ReportModel.generated_at.desc()).all()
    return JSONResponse(
        content={
            "reports": [
                {
                    "id": r.id,
                    "report_type": r.report_type,
                    "title": r.title,
                    "generated_by": r.generated_by,
                    "generated_at": r.generated_at.isoformat() if r.generated_at else None,
                    "period_start": r.period_start.isoformat() if r.period_start else None,
                    "period_end": r.period_end.isoformat() if r.period_end else None,
                }
                for r in reports
            ],
            "total": len(reports),
        }
    )


# ── 14. GET /classification/{entity_type}/{entity_id} ─────────────────


@router.get("/classification/{entity_type}/{entity_id}")
async def get_data_classification(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get the data classification for an entity."""
    _require_admin_or_investigator(current_user)
    tag = DataClassificationService.get_classification(db, entity_type, entity_id)
    if not tag:
        return JSONResponse(
            content={
                "target_type": entity_type,
                "target_id": entity_id,
                "classification": None,
                "message": "No classification set",
            }
        )
    return JSONResponse(
        content={
            "id": tag.id,
            "target_type": tag.target_type,
            "target_id": tag.target_id,
            "classification": tag.classification,
            "classified_by": tag.classified_by,
            "classified_at": tag.classified_at.isoformat() if tag.classified_at else None,
            "expires_at": tag.expires_at.isoformat() if tag.expires_at else None,
            "notes": tag.notes,
        }
    )


# ── 15. POST /classification ─────────────────────────────────────────


@router.post("/classification")
async def set_data_classification(
    body: DataClassificationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Set or update the data classification for an entity."""
    _require_admin(current_user)
    try:
        org_id = _get_org_id()
        tag = DataClassificationService.classify(
            db,
            target_type=body.entity_type,
            target_id=body.entity_id,
            classification=body.classification,
            classified_by=current_user.id,
            org_id=org_id,
        )
        return JSONResponse(
            status_code=201,
            content={
                "id": tag.id,
                "target_type": tag.target_type,
                "target_id": tag.target_id,
                "classification": tag.classification,
                "classified_by": tag.classified_by,
                "classified_at": tag.classified_at.isoformat() if tag.classified_at else None,
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to set classification: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── 16. GET /audit/verify-chain ──────────────────────────────────────


@router.get("/audit/verify-chain")
async def verify_audit_chain(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Verify the integrity of the compliance audit trail hash chain."""
    _require_admin_or_investigator(current_user)
    org_id = _get_org_id()
    result = ComplianceAuditService.verify_chain(db, org_id=org_id)
    return JSONResponse(content=result)


# ── 17. POST /export/evidence/{evidence_id} ──────────────────────────


@router.post("/export/evidence/{evidence_id}")
async def export_evidence(
    evidence_id: str,
    format: str = "json",
    purpose: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Export evidence data in CSV, JSON, or PDF-ready format."""
    _require_admin_or_investigator(current_user)
    org_id = _get_org_id()
    try:
        if format == "csv":
            result = EvidenceExportService.export_csv(
                db, evidence_id, exported_by=current_user.id, purpose=purpose, org_id=org_id
            )
        elif format == "pdf_ready":
            result = EvidenceExportService.export_pdf_ready(
                db, evidence_id, exported_by=current_user.id, purpose=purpose, org_id=org_id
            )
        else:
            result = EvidenceExportService.export_json(
                db, evidence_id, exported_by=current_user.id, purpose=purpose, org_id=org_id
            )
        return JSONResponse(content={"export_id": result["export_id"], "format": format})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Evidence export failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── 18. POST /export/case/{case_id} ──────────────────────────────────


@router.post("/export/case/{case_id}")
async def export_case(
    case_id: str,
    format: str = "json",
    includes_evidence: bool = True,
    includes_audit_trail: bool = True,
    includes_chain_of_custody: bool = True,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Export a complete case package with evidence, audit trail, and chain of custody."""
    _require_admin_or_investigator(current_user)
    org_id = _get_org_id()
    try:
        result = CaseExportService.export_case(
            db,
            case_id=case_id,
            exported_by=current_user.id,
            export_format=format,
            includes_evidence=includes_evidence,
            includes_audit_trail=includes_audit_trail,
            includes_chain_of_custody=includes_chain_of_custody,
            org_id=org_id,
        )
        return JSONResponse(content={"export_id": result["export_id"], "format": format})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Case export failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
