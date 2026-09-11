"""Advanced Forensics API routes for enterprise-grade forensic analysis."""
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import database, models
from .auth import get_current_user
from .forensic_engine import ProcessingPipeline, ForensicProcessorConfig
from .forensic_engine.integration import run_full_processing

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/advanced-forensics", tags=["advanced-forensics"])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _require_investigator(current_user: models.User):
    roles = [r.name for r in current_user.roles]
    if "admin" not in roles and "investigator" not in roles:
        raise HTTPException(status_code=403, detail="forbidden")


class ProcessRequest(BaseModel):
    enabled_processors: Optional[List[str]] = None
    ocr_language: Optional[str] = None
    run_ocr: Optional[bool] = None
    generate_thumbnails: Optional[bool] = None


class IntegrityRequest(BaseModel):
    verify_sha256: bool = True
    verify_sha1: bool = False
    verify_md5: bool = False
    yara_rules_path: Optional[str] = None
    run_clamav: bool = False


# ── 1. GET /processors ────────────────────────────────────────────────

@router.get("/processors")
def list_advanced_processors(
    current_user: models.User = Depends(get_current_user),
):
    pipeline = ProcessingPipeline()
    all_processors = pipeline.get_available_processors()
    advanced = [p for p in all_processors if p.startswith("advanced_forensics.") or p in (
        "browser_forensics", "windows_forensics", "mobile_forensics",
        "email_forensics", "network_forensics", "disk_forensics",
        "memory_forensics", "integrity_forensics",
    )]
    return {"processors": advanced, "total": len(advanced)}


# ── 2. POST /process/{evidence_id} ────────────────────────────────────

@router.post("/process/{evidence_id}")
def run_advanced_processing(
    evidence_id: str,
    request: Optional[ProcessRequest] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    database.init_db()
    _require_investigator(current_user)

    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="evidence not found")

    config = ForensicProcessorConfig()
    if request:
        if request.enabled_processors is not None:
            config.enabled_processors = request.enabled_processors
        if request.ocr_language is not None:
            config.ocr_language = request.ocr_language
        if request.run_ocr is not None:
            config.run_ocr = request.run_ocr
        if request.generate_thumbnails is not None:
            config.generate_thumbnails = request.generate_thumbnails

    try:
        result = run_full_processing(evidence_id, db, config)
    except Exception as e:
        logger.error("Advanced processing failed for %s: %s", evidence_id, e)
        raise HTTPException(status_code=500, detail=f"advanced processing failed: {e}")

    audit = models.AuditLog(
        actor_id=current_user.id,
        action="advanced_forensics.process",
        target_type="evidence",
        target_id=evidence_id,
        detail={
            "processors_run": result.processors_run,
            "duration_seconds": result.duration_seconds,
            "success": result.success,
            "errors": result.errors,
        },
    )
    db.add(audit)
    db.commit()

    return {
        "evidence_id": evidence_id,
        "success": result.success,
        "processors_run": result.processors_run,
        "duration_seconds": result.duration_seconds,
        "errors": result.errors,
        "tags": result.schema.tags if result.schema else [],
    }


# ── 3. GET /results/{evidence_id} ─────────────────────────────────────

@router.get("/results/{evidence_id}")
def get_forensic_results(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="evidence not found")

    results = (
        db.query(models.ForensicResult)
        .filter(models.ForensicResult.evidence_id == evidence_id)
        .order_by(models.ForensicResult.created_at.desc())
        .all()
    )

    advanced_results = []
    for r in results:
        if r.processor:
            advanced_results.append({
                "id": r.id,
                "processor": r.processor,
                "result": r.result,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            })

    audit = models.AuditLog(
        actor_id=current_user.id,
        action="advanced_forensics.results.view",
        target_type="evidence",
        target_id=evidence_id,
        detail={"result_count": len(advanced_results)},
    )
    db.add(audit)
    db.commit()

    return {"evidence_id": evidence_id, "results": advanced_results, "total": len(advanced_results)}


# ── 4. GET /results/{evidence_id}/timeline ────────────────────────────

@router.get("/results/{evidence_id}/timeline")
def get_evidence_timeline(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="evidence not found")

    results = (
        db.query(models.ForensicResult)
        .filter(models.ForensicResult.evidence_id == evidence_id)
        .all()
    )

    timeline_events: List[Dict[str, Any]] = []
    for r in results:
        if not r.processor:
            continue
        result_data = r.result or {}
        events = result_data.get("timeline_events") or result_data.get("timeline", [])
        if isinstance(events, list):
            for ev_item in events:
                if isinstance(ev_item, dict):
                    ev_item.setdefault("source_processor", r.processor)
                    timeline_events.append(ev_item)

    timeline_events.sort(key=lambda x: x.get("timestamp", x.get("date", "")))

    return {"evidence_id": evidence_id, "timeline": timeline_events, "total": len(timeline_events)}


# ── 5. GET /results/{evidence_id}/entities ─────────────────────────────

@router.get("/results/{evidence_id}/entities")
def get_evidence_entities(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="evidence not found")

    results = (
        db.query(models.ForensicResult)
        .filter(models.ForensicResult.evidence_id == evidence_id)
        .all()
    )

    entities: List[Dict[str, Any]] = []
    seen: set = set()
    for r in results:
        if not r.processor:
            continue
        result_data = r.result or {}
        ent_list = result_data.get("entities", [])
        if isinstance(ent_list, list):
            for ent in ent_list:
                if isinstance(ent, dict):
                    key = (ent.get("name", ""), ent.get("type", ""))
                    if key not in seen:
                        seen.add(key)
                        ent.setdefault("source_processor", r.processor)
                        entities.append(ent)

    return {"evidence_id": evidence_id, "entities": entities, "total": len(entities)}


# ── 6. GET /results/{evidence_id}/iocs ─────────────────────────────────

@router.get("/results/{evidence_id}/iocs")
def get_evidence_iocs(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="evidence not found")

    results = (
        db.query(models.ForensicResult)
        .filter(models.ForensicResult.evidence_id == evidence_id)
        .all()
    )

    iocs: List[Dict[str, Any]] = []
    seen: set = set()
    for r in results:
        if not r.processor:
            continue
        result_data = r.result or {}
        ioc_list = result_data.get("iocs", [])
        if isinstance(ioc_list, list):
            for ioc in ioc_list:
                if isinstance(ioc, dict):
                    key = (ioc.get("ioc_type", ""), ioc.get("value", ""))
                    if key not in seen:
                        seen.add(key)
                        ioc.setdefault("source_processor", r.processor)
                        iocs.append(ioc)

    return {"evidence_id": evidence_id, "iocs": iocs, "total": len(iocs)}


# ── 7. GET /results/{evidence_id}/findings ─────────────────────────────

@router.get("/results/{evidence_id}/findings")
def get_evidence_findings(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="evidence not found")

    results = (
        db.query(models.ForensicResult)
        .filter(models.ForensicResult.evidence_id == evidence_id)
        .all()
    )

    findings: List[Dict[str, Any]] = []
    for r in results:
        if not r.processor:
            continue
        result_data = r.result if isinstance(r.result, dict) else {}
        finding_list = result_data.get("findings", [])
        if isinstance(finding_list, list) and finding_list:
            for f in finding_list:
                if isinstance(f, dict):
                    f.setdefault("source_processor", r.processor)
                    findings.append(f)
        elif r.processor == "ai_findings" and result_data.get("status") == "analyzed":
            findings.append({
                "source_processor": r.processor,
                "title": "AI Text Analysis",
                "description": f"Extracted {result_data.get('word_count', 0)} words, {result_data.get('char_count', 0)} characters",
                "risk_level": "info",
                "text_preview": result_data.get("text_preview", ""),
            })

    findings.sort(key=lambda x: _risk_order(x.get("risk_level", "info")))

    return {"evidence_id": evidence_id, "findings": findings, "total": len(findings)}


def _risk_order(level: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}.get(level, 5)


# ── 8. GET /cases/{case_id}/artifacts ──────────────────────────────────

@router.get("/cases/{case_id}/artifacts")
def get_case_artifacts(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="case not found")

    evidence_items = (
        db.query(models.Evidence)
        .filter(models.Evidence.case_id == case_id)
        .all()
    )
    evidence_ids = [e.id for e in evidence_items]
    if not evidence_ids:
        return {"case_id": case_id, "artifacts": [], "total": 0, "evidence_count": 0}

    results = (
        db.query(models.ForensicResult)
        .filter(models.ForensicResult.evidence_id.in_(evidence_ids))
        .all()
    )

    artifacts: List[Dict[str, Any]] = []
    for r in results:
        if not r.processor or not (r.processor.startswith("advanced_forensics.") or r.processor.startswith("forensic_engine.")):
            continue
        result_data = r.result or {}
        for artifact_key in ("artifacts", "recovered_files", "extracted_data"):
            artifact_list = result_data.get(artifact_key, [])
            if isinstance(artifact_list, list):
                for a in artifact_list:
                    if isinstance(a, dict):
                        a.setdefault("source_processor", r.processor)
                        a.setdefault("evidence_id", r.evidence_id)
                        artifacts.append(a)

    return {
        "case_id": case_id,
        "artifacts": artifacts,
        "total": len(artifacts),
        "evidence_count": len(evidence_ids),
    }


# ── 9. GET /cases/{case_id}/timeline ──────────────────────────────────

@router.get("/cases/{case_id}/timeline")
def get_case_timeline(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="case not found")

    evidence_items = (
        db.query(models.Evidence)
        .filter(models.Evidence.case_id == case_id)
        .all()
    )
    evidence_ids = [e.id for e in evidence_items]

    results = (
        db.query(models.ForensicResult)
        .filter(models.ForensicResult.evidence_id.in_(evidence_ids))
        .all()
    )

    timeline_events: List[Dict[str, Any]] = []
    for r in results:
        if not r.processor or not (r.processor.startswith("advanced_forensics.") or r.processor.startswith("forensic_engine.")):
            continue
        result_data = r.result or {}
        events = result_data.get("timeline_events", [])
        if isinstance(events, list):
            for ev_item in events:
                if isinstance(ev_item, dict):
                    ev_item.setdefault("source_processor", r.processor)
                    ev_item.setdefault("evidence_id", r.evidence_id)
                    timeline_events.append(ev_item)

    timeline_events.sort(key=lambda x: x.get("timestamp", x.get("date", "")))

    return {
        "case_id": case_id,
        "timeline": timeline_events,
        "total": len(timeline_events),
        "evidence_count": len(evidence_ids),
    }


# ── 10. GET /cases/{case_id}/entities ─────────────────────────────────

@router.get("/cases/{case_id}/entities")
def get_case_entities(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="case not found")

    evidence_items = (
        db.query(models.Evidence)
        .filter(models.Evidence.case_id == case_id)
        .all()
    )
    evidence_ids = [e.id for e in evidence_items]

    results = (
        db.query(models.ForensicResult)
        .filter(models.ForensicResult.evidence_id.in_(evidence_ids))
        .all()
    )

    entities: List[Dict[str, Any]] = []
    seen: set = set()
    for r in results:
        if not r.processor or not (r.processor.startswith("advanced_forensics.") or r.processor.startswith("forensic_engine.")):
            continue
        result_data = r.result or {}
        ent_list = result_data.get("entities", [])
        if isinstance(ent_list, list):
            for ent in ent_list:
                if isinstance(ent, dict):
                    key = (ent.get("name", ""), ent.get("type", ""))
                    if key not in seen:
                        seen.add(key)
                        ent.setdefault("source_processor", r.processor)
                        ent.setdefault("evidence_id", r.evidence_id)
                        entities.append(ent)

    return {
        "case_id": case_id,
        "entities": entities,
        "total": len(entities),
        "evidence_count": len(evidence_ids),
    }


# ── 11. POST /integrity/{evidence_id} ─────────────────────────────────

@router.post("/integrity/{evidence_id}")
def run_integrity_verification(
    evidence_id: str,
    request: Optional[IntegrityRequest] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    database.init_db()
    _require_investigator(current_user)

    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="evidence not found")

    integrity_result: Dict[str, Any] = {
        "evidence_id": evidence_id,
        "verified": True,
        "checks": {},
    }

    opts = request or IntegrityRequest()

    if opts.verify_sha256:
        try:
            import hashlib
            sha256 = hashlib.sha256()
            with open(ev.storage_path, "rb") as f:
                while True:
                    chunk = f.read(1024 * 64)
                    if not chunk:
                        break
                    sha256.update(chunk)
            computed = sha256.hexdigest()
            match = computed == ev.sha256
            integrity_result["checks"]["sha256"] = {"match": match, "expected": ev.sha256, "computed": computed}
            if not match:
                integrity_result["verified"] = False
        except Exception as e:
            integrity_result["checks"]["sha256"] = {"match": False, "error": str(e)}
            integrity_result["verified"] = False

    try:
        config = ForensicProcessorConfig(enabled_processors=["integrity_forensics"])
        pipeline = ProcessingPipeline(config)
        from .forensic_engine.schemas import EvidenceSchema
        evidence_schema = EvidenceSchema(
            evidence_id=ev.id,
            case_id=ev.case_id,
            storage_path=ev.storage_path,
            filename=ev.filename,
            sha256=ev.sha256,
            size=ev.size,
            mime_type=ev.mime_type,
        )
        result = pipeline.process(evidence_schema)
        integrity_result["checks"]["forensic_integrity"] = {
            "success": result.success,
            "processors_run": result.processors_run,
            "errors": result.errors,
        }
        if not result.success:
            integrity_result["verified"] = False
    except Exception as e:
        logger.error("Integrity forensics processor failed for %s: %s", evidence_id, e)
        integrity_result["checks"]["forensic_integrity"] = {"success": False, "error": str(e)}

    fr = models.ForensicResult(
        evidence_id=evidence_id,
        processor="advanced_forensics.integrity",
        result=integrity_result,
    )
    db.add(fr)

    audit = models.AuditLog(
        actor_id=current_user.id,
        action="advanced_forensics.integrity",
        target_type="evidence",
        target_id=evidence_id,
        detail={"verified": integrity_result["verified"], "checks": list(integrity_result["checks"].keys())},
    )
    db.add(audit)
    db.commit()

    return integrity_result


# ── 12. GET /stats ────────────────────────────────────────────────────

@router.get("/stats")
def get_processing_statistics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    total_evidence = db.query(models.Evidence).count()
    total_results = db.query(models.ForensicResult).count()
    total_cases = db.query(models.Case).count()

    advanced_processor_names = (
        "advanced_forensics.browser", "advanced_forensics.windows",
        "advanced_forensics.mobile", "advanced_forensics.email",
        "advanced_forensics.network", "advanced_forensics.disk",
        "advanced_forensics.memory", "advanced_forensics.integrity",
    )
    advanced_result_count = (
        db.query(models.ForensicResult)
        .filter(
            models.ForensicResult.processor.like("advanced_forensics.%")
            | models.ForensicResult.processor.like("forensic_engine.%")
        )
        .count()
    )

    jobs_completed = (
        db.query(models.ForensicJob)
        .filter(models.ForensicJob.status == "completed")
        .count()
    )
    jobs_failed = (
        db.query(models.ForensicJob)
        .filter(models.ForensicJob.status == "failed")
        .count()
    )
    jobs_queued = (
        db.query(models.ForensicJob)
        .filter(models.ForensicJob.status == "queued")
        .count()
    )

    return {
        "total_evidence": total_evidence,
        "total_results": total_results,
        "advanced_results": advanced_result_count,
        "total_cases": total_cases,
        "jobs": {
            "completed": jobs_completed,
            "failed": jobs_failed,
            "queued": jobs_queued,
        },
    }
