from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import Response as FastAPIResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import uuid
import logging
import json
import zipfile
import io
from datetime import datetime, timezone

from . import models, database, auth
from .database import Base
from .agents.report_schemas import ReportRequest, ReportDocument, ReportPackageManifest
from .agents.report_service import ForensicReportService, compute_sha256_bytes

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["reports"])


class ReportCreate(BaseModel):
    case_id: str
    title: str
    report_type: str = "court_ready"  # court_ready, executive_summary, technical_forensic, forensic_package
    notes: Optional[str] = None
    evidence_refs: Optional[List[str]] = None
    finding_refs: Optional[List[str]] = None
    include_exhibits: bool = True
    include_hash_ledger: bool = True
    include_chain_of_custody: bool = True
    include_certificate_template: bool = True


class ReportOut(BaseModel):
    id: str
    case_id: str
    title: str
    report_type: str
    status: str  # generated, pending, failed, review_required
    content_markdown: str
    created_by: str
    created_at: str

    class Config:
        from_attributes = True
        orm_mode = True


# Create reports table if it doesn't exist
def _ensure_reports_table():
    from sqlalchemy import Column, String, Text, DateTime

    if not hasattr(models, 'ReportRecord'):
        class ReportRecord(Base):
            __tablename__ = 'reports'
            id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
            case_id = Column(String, nullable=False, index=True)
            title = Column(String, nullable=False)
            report_type = Column(String, nullable=False, default='court_ready')
            status = Column(String, nullable=False, default='generated')
            content_markdown = Column(Text, nullable=False)
            created_by = Column(String, nullable=False)
            created_at = Column(DateTime, nullable=False)
            updated_at = Column(DateTime, nullable=False)
        models.ReportRecord = ReportRecord
    try:
        engine = database.get_engine()
        models.ReportRecord.__table__.create(bind=engine, checkfirst=True)
    except Exception:
        pass


_ensure_reports_table()


def _verify_case_access(current_user: models.User, case: models.Case) -> None:
    role_names = [r.name.lower() for r in current_user.roles] if current_user.roles else []
    privileged = any(
        r in role_names
        for r in ["admin", "super admin", "investigator", "analyst", "jury_evaluator", "demo_evaluator"]
    )
    if privileged or current_user.id == case.created_by or current_user.id == case.assigned_to:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Forbidden: You do not have authorization to access this case.",
    )


@router.post("", response_model=ReportOut)
@router.post("/", response_model=ReportOut)
async def generate_report(
    payload: ReportCreate,
    db: Session = Depends(database.get_db_session),
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    Generate a comprehensive forensic report using the Phase 7 Report Service pipeline.
    Produces evidence-grounded markdown, hash ledgers, exhibits, and certificate templates.
    """
    case = db.query(models.Case).filter(models.Case.id == payload.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    _verify_case_access(current_user, case)

    report_service = ForensicReportService(db)
    report_req = ReportRequest(
        case_id=payload.case_id,
        title=payload.title,
        objective=payload.notes,
        evidence_refs=payload.evidence_refs or [],
        finding_refs=payload.finding_refs or [],
        include_exhibits=payload.include_exhibits,
        include_hash_ledger=payload.include_hash_ledger,
        include_chain_of_custody=payload.include_chain_of_custody,
        include_certificate_template=payload.include_certificate_template,
        investigator_notes=payload.notes,
    )

    doc: ReportDocument = await report_service.build_report_document(
        request=report_req,
        current_user_email=current_user.email,
    )

    markdown = report_service.render_markdown(doc)
    now = datetime.now(timezone.utc)
    report_id = doc.report_id

    # Persist report to database
    report_record = models.ReportRecord(
        id=report_id,
        case_id=case.id,
        title=payload.title,
        report_type=payload.report_type,
        status="generated",
        content_markdown=markdown,
        created_by=current_user.email,
        created_at=now,
        updated_at=now,
    )
    db.add(report_record)
    db.commit()

    return ReportOut(
        id=report_id,
        case_id=case.id,
        title=payload.title,
        report_type=payload.report_type,
        status="generated",
        content_markdown=markdown,
        created_by=current_user.email,
        created_at=now.isoformat(),
    )


@router.get("/{case_id}", response_model=List[ReportOut])
def get_case_reports(
    case_id: str,
    db: Session = Depends(database.get_db_session),
    current_user: models.User = Depends(auth.get_current_user),
):
    """List reports generated for a given case."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    _verify_case_access(current_user, case)

    if not hasattr(models, 'ReportRecord'):
        return []
    reports = db.query(models.ReportRecord).filter(
        models.ReportRecord.case_id == case_id
    ).order_by(models.ReportRecord.created_at.desc()).all()

    return [
        ReportOut(
            id=r.id,
            case_id=r.case_id,
            title=r.title,
            report_type=r.report_type,
            status=r.status,
            content_markdown=r.content_markdown,
            created_by=r.created_by,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in reports
    ]


@router.get("/detail/{report_id}", response_model=ReportOut)
def get_report_detail(
    report_id: str,
    db: Session = Depends(database.get_db_session),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Retrieve detailed report metadata and content."""
    report = db.query(models.ReportRecord).filter(models.ReportRecord.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    case = db.query(models.Case).filter(models.Case.id == report.case_id).first()
    if case:
        _verify_case_access(current_user, case)

    return ReportOut(
        id=report.id,
        case_id=report.case_id,
        title=report.title,
        report_type=report.report_type,
        status=report.status,
        content_markdown=report.content_markdown,
        created_by=report.created_by,
        created_at=report.created_at.isoformat() if report.created_at else "",
    )


@router.delete("/{report_id}")
def delete_report(
    report_id: str,
    db: Session = Depends(database.get_db_session),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Delete a report record."""
    report = db.query(models.ReportRecord).filter(models.ReportRecord.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    case = db.query(models.Case).filter(models.Case.id == report.case_id).first()
    if case:
        _verify_case_access(current_user, case)

    db.delete(report)
    db.commit()
    return {"detail": "Report deleted successfully"}


@router.get("/{report_id}/export/pdf")
async def export_report_pdf(
    report_id: str,
    db: Session = Depends(database.get_db_session),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Export report as court-reviewable PDF."""
    report = db.query(models.ReportRecord).filter(models.ReportRecord.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    case = db.query(models.Case).filter(models.Case.id == report.case_id).first()
    if case:
        _verify_case_access(current_user, case)

    service = ForensicReportService(db)
    req = ReportRequest(case_id=report.case_id, title=report.title)
    doc = await service.build_report_document(req, current_user.email)
    pdf_bytes = service.render_pdf(doc)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{report.title or "report"}.pdf"'},
    )


@router.get("/{report_id}/export/json")
async def export_report_json(
    report_id: str,
    db: Session = Depends(database.get_db_session),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Export report as structured JSON document with evidence index and hash ledger."""
    report = db.query(models.ReportRecord).filter(models.ReportRecord.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    case = db.query(models.Case).filter(models.Case.id == report.case_id).first()
    if case:
        _verify_case_access(current_user, case)

    service = ForensicReportService(db)
    req = ReportRequest(case_id=report.case_id, title=report.title)
    doc = await service.build_report_document(req, current_user.email)
    json_str = doc.model_dump_json(indent=2)

    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{report.title or "report"}.json"'},
    )


@router.get("/{report_id}/export/docx")
async def export_report_docx(
    report_id: str,
    db: Session = Depends(database.get_db_session),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Export report as plain text / markdown bundle."""
    report = db.query(models.ReportRecord).filter(models.ReportRecord.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    case = db.query(models.Case).filter(models.Case.id == report.case_id).first()
    if case:
        _verify_case_access(current_user, case)

    return Response(
        content=report.content_markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{report.title or "report"}.md"'},
    )


@router.get("/{report_id}/export/zip")
async def export_report_zip(
    report_id: str,
    db: Session = Depends(database.get_db_session),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Export complete forensic report package ZIP with PDF, JSON, and SHA-256 package manifest."""
    report = db.query(models.ReportRecord).filter(models.ReportRecord.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    case = db.query(models.Case).filter(models.Case.id == report.case_id).first()
    if case:
        _verify_case_access(current_user, case)

    service = ForensicReportService(db)
    req = ReportRequest(case_id=report.case_id, title=report.title)
    doc = await service.build_report_document(req, current_user.email)
    pdf_bytes = service.render_pdf(doc)
    json_bytes = doc.model_dump_json(indent=2).encode("utf-8")

    manifest = service.generate_report_package(doc, pdf_bytes, json_bytes)
    manifest_bytes = manifest.model_dump_json(indent=2).encode("utf-8")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("report.pdf", pdf_bytes)
        zf.writestr("report.json", json_bytes)
        zf.writestr("manifest.json", manifest_bytes)
        zf.writestr("report.md", report.content_markdown.encode("utf-8"))

    buf.seek(0)
    zip_bytes = buf.getvalue()

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{report.title or "report"}-package.zip"'},
    )
