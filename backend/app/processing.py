from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import database
from . import models
from .auth import get_current_user
from .processors import get_processor, list_processors
from . import processors as proc_module
from .forensic_engine import ProcessingPipeline, ForensicProcessorConfig
from .forensic_engine.integration import run_full_processing
from datetime import datetime, timezone
import os
import time
import threading
import json

router = APIRouter(prefix='/processing', tags=['processing'])

# Worker pool configuration
MAX_WORKERS = int(os.getenv('WORKER_POOL_SIZE', '4'))
_worker_threads: list[threading.Thread] = []
_worker_lock = threading.Lock()
_cancelled_jobs: set[str] = set()
_cancel_lock = threading.Lock()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post('/evidence/{evidence_id}/enqueue')
def enqueue_processing(evidence_id: str, request: dict | None = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # ensure DB tables exist (safeguard for tests/startup ordering)
    database.init_db()
    # RBAC: uploader, admin, investigator can enqueue
    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail='evidence not found')
    roles = [r.name.lower() for r in current_user.roles] if current_user.roles else []
    if 'admin' not in roles and 'investigator' not in roles and 'jury_evaluator' not in roles and 'demo_evaluator' not in roles and current_user.id != ev.uploaded_by:
        raise HTTPException(status_code=403, detail='forbidden')


    processors = request.get('processors') if request else None
    if not processors:
        processors = list_processors()

    job = models.ForensicJob(evidence_id=evidence_id, processors=processors, status='queued')
    db.add(job)
    db.commit()
    db.refresh(job)

    # In test mode, process job synchronously to prevent background thread database races
    if os.environ.get("TESTING") == "1":
        _process_job(job.id)
    else:
        start_worker()

    audit = models.AuditLog(actor_id=current_user.id, action='processing.enqueue', target_type='evidence', target_id=evidence_id, detail={'job_id': job.id, 'processors': processors})
    db.add(audit)
    db.commit()

    return {'job_id': job.id}


@router.get('/jobs/{job_id}')
def get_job(job_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    job = db.query(models.ForensicJob).filter(models.ForensicJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail='job not found')
    return {
        'id': job.id,
        'evidence_id': job.evidence_id,
        'processors': job.processors,
        'status': job.status,
        'queued_at': job.queued_at.isoformat() if job.queued_at else None,
        'started_at': job.started_at.isoformat() if job.started_at else None,
        'finished_at': job.finished_at.isoformat() if job.finished_at else None,
        'result': job.result,
        'error': job.error,
    }


def _process_job(job_id: str):
    """Process a forensic job using the full forensic engine pipeline."""
    import logging
    _logger = logging.getLogger('crimekit.processing')
    db = database.SessionLocal()
    try:
        job = db.query(models.ForensicJob).filter(models.ForensicJob.id == job_id).first()
        if not job:
            return

        # Check if cancelled (supports both 'queued' and 'claiming' status)
        with _cancel_lock:
            if job_id in _cancelled_jobs:
                _cancelled_jobs.discard(job_id)
                job.status = 'cancelled'
                job.finished_at = datetime.now(timezone.utc)
                db.add(job)
                db.commit()
                return

        # Accept job from 'claiming' or 'queued' status
        if job.status not in ('queued', 'claiming'):
            return

        job.status = 'running'
        job.started_at = datetime.now(timezone.utc)
        db.add(job)
        db.commit()

        ev = db.query(models.Evidence).filter(models.Evidence.id == job.evidence_id).first()
        if not ev:
            job.status = 'failed'
            job.error = 'evidence not found'
            job.finished_at = datetime.now(timezone.utc)
            db.add(job)
            db.commit()
            return

        # Check cancellation before heavy processing
        with _cancel_lock:
            if job_id in _cancelled_jobs:
                _cancelled_jobs.discard(job_id)
                job.status = 'cancelled'
                job.finished_at = datetime.now(timezone.utc)
                db.add(job)
                db.commit()
                return

        results = {}
        try:
            # ── Stage 1: Run full forensic engine pipeline ──
            _logger.info("Job %s: Running forensic engine on evidence %s (%s)",
                         job_id[:8], ev.id[:8], ev.filename)
            result = run_full_processing(ev.id, db)
            results['forensic_engine'] = {
                'success': result.success,
                'processors_run': result.processors_run,
                'duration_seconds': result.duration_seconds,
                'errors': result.errors,
            }
            _logger.info("Job %s: Forensic engine completed — processors=%s, success=%s",
                         job_id[:8], result.processors_run, result.success)

            # E01/EWF is never handled as a generic binary. Once the backend
            # classifier has verified TSK capability, use the existing native
            # worker so its real events and artifacts flow through the system.
            forensic_meta = (ev.metadata_json or {}).get("forensic_engine", {}).get("metadata", {}).get("forensic_image", {})
            if forensic_meta.get("evidence_type") == "forensic_disk_image" and forensic_meta.get("capability") == "supported":
                from .tsk_engine.integration import TSKIntegration
                tsk_result = TSKIntegration().process_evidence_sync(
                    evidence_id=ev.id,
                    case_id=ev.case_id or "",
                )
                results["tsk"] = tsk_result
                _logger.info("Job %s: TSK processing completed — %s", job_id[:8], tsk_result)

            # ── Stage 1b: Execute specifically requested registered processors ──
            for p_name in (job.processors or []):
                proc_fn = get_processor(p_name)
                if proc_fn and ev.storage_path and os.path.exists(ev.storage_path):
                    try:
                        p_res = proc_fn(ev.storage_path, filename=ev.filename)
                        results[p_name] = p_res
                        db.add(models.ForensicResult(
                            evidence_id=ev.id,
                            processor=p_name,
                            result=p_res,
                        ))
                        db.commit()
                        _logger.info("Job %s: Executed registered processor '%s'", job_id[:8], p_name)
                    except Exception as p_err:
                        _logger.warning("Job %s: Processor '%s' failed: %s", job_id[:8], p_name, p_err)

            # ── Stage 2: Extract text for downstream processing ──
            extracted_text = None
            # Check Document table (created by integrate_with_ai_pipeline)
            doc = db.query(models.Document).filter(
                models.Document.evidence_id == ev.id
            ).order_by(models.Document.created_at.desc()).first()
            if doc and doc.text:
                extracted_text = doc.text
            # Fallback: check evidence metadata
            if not extracted_text:
                meta = ev.metadata_json or {}
                extracted_text = meta.get('ocr_text') or meta.get('extracted_text')

            _logger.info("Job %s: Extracted text length=%d",
                         job_id[:8], len(extracted_text) if extracted_text else 0)

            # ── Stage 3: Entity extraction ──
            if extracted_text and len(extracted_text.strip()) > 10:
                try:
                    from .kg import extract_entities, extract_relationships, extract_timeline
                    from .entity_resolver import resolve_entities

                    entities = extract_entities(extracted_text)
                    relationships = extract_relationships(
                        extracted_text, entities,
                        evidence_id=ev.id,
                    )
                    timeline_events = extract_timeline(extracted_text)

                    # Resolve entities (merge duplicates)
                    resolved_entities = resolve_entities(entities, evidence_id=ev.id)

                    entity_result = {
                        'entities': resolved_entities,
                        'entity_count': len(resolved_entities),
                        'raw_count': len(entities),
                    }
                    results['entities'] = entity_result
                    db.add(models.ForensicResult(
                        evidence_id=ev.id,
                        processor='entity_extraction',
                        result=entity_result,
                    ))

                    rel_result = {
                        'relationships': relationships,
                        'relationship_count': len(relationships),
                    }
                    results['relationships'] = rel_result
                    db.add(models.ForensicResult(
                        evidence_id=ev.id,
                        processor='relationship_extraction',
                        result=rel_result,
                    ))

                    timeline_result = {
                        'timeline': [
                            {'timestamp': t.get('date', ''), 'event': t.get('summary', ''),
                             'description': t.get('summary', ''), 'metadata': {}}
                            for t in timeline_events
                        ],
                        'event_count': len(timeline_events),
                    }
                    results['timeline'] = timeline_result
                    db.add(models.ForensicResult(
                        evidence_id=ev.id,
                        processor='timeline_extraction',
                        result=timeline_result,
                    ))

                    # Store KG data in ForensicResult for SQLite-based KG fallback
                    kg_result = {
                        'entities': resolved_entities,
                        'relationships': relationships,
                        'timeline': timeline_events,
                        'entity_count': len(resolved_entities),
                        'relationship_count': len(relationships),
                        'event_count': len(timeline_events),
                    }
                    results['knowledge_graph'] = kg_result
                    db.add(models.ForensicResult(
                        evidence_id=ev.id,
                        processor='knowledge_graph',
                        result=kg_result,
                    ))

                    db.commit()
                    _logger.info(
                        "Job %s: Extracted %d entities, %d relationships, %d timeline events",
                        job_id[:8], len(resolved_entities), len(relationships), len(timeline_events),
                    )

                    # ── Persist to Neo4j knowledge graph (auto-ingest) ──
                    # This is the missing link: the processing pipeline computes
                    # entities/relationships but never wrote them to the canonical
                    # graph store. KGClient.ingest MERGEs by (name, type), so this
                    # also provides cross-evidence entity resolution automatically.
                    try:
                        from .kg import get_kg_client
                        _kg = get_kg_client()
                        _kg_counts = _kg.ingest(
                            entities=resolved_entities,
                            relationships=relationships,
                            timeline=timeline_events,
                            evidence_id=ev.id,
                            case_id=ev.case_id,
                        )
                        _logger.info(
                            "Job %s: Neo4j ingest -> %s", job_id[:8], _kg_counts,
                        )
                    except Exception as kg_err:
                        _logger.warning(
                            "Job %s: Neo4j graph ingest failed (non-fatal): %s",
                            job_id[:8], kg_err,
                        )

                    # ── Publish domain events for real-time graph updates ──
                    try:
                        from .events import (
                            publish_entity_detected,
                            publish_relationship_detected,
                            publish_evidence_processed,
                        )
                        _logger.info("Job %s: PUBLISH block entered", job_id[:8])
                        case_id = ev.case_id
                        _logger.info("Job %s: publishing case_id=%r", job_id[:8], case_id)
                        if case_id:
                            for ent in resolved_entities:
                                publish_entity_detected(
                                    case_id=case_id,
                                    entity_name=ent.get("name", ""),
                                    entity_type=ent.get("type", ""),
                                    evidence_id=ev.id,
                                    confidence=ent.get("confidence"),
                                    processor=ent.get("source"),
                                )
                            for rel in relationships:
                                publish_relationship_detected(
                                    case_id=case_id,
                                    source_entity=rel.get("source_entity", rel.get("source", "")),
                                    target_entity=rel.get("target_entity", rel.get("target", "")),
                                    relationship=rel.get("relationship", rel.get("type", "")),
                                    evidence_id=ev.id,
                                    confidence=rel.get("confidence"),
                                    processor=rel.get("processor"),
                                )
                            publish_evidence_processed(
                                case_id=case_id,
                                evidence_id=ev.id,
                                entity_count=len(resolved_entities),
                                relationship_count=len(relationships),
                            )
                    except Exception as ev_err:
                        _logger.warning("Job %s: Event publishing failed: %s", job_id[:8], ev_err)
                except Exception as e:
                    _logger.error("Job %s: Entity/timeline extraction failed: %s", job_id[:8], e)
                    results['entity_extraction_error'] = str(e)

            # ── Stage 4: AI findings summary ──
            if extracted_text and len(extracted_text.strip()) > 50:
                try:
                    # Generate a simple AI findings summary
                    text_preview = extracted_text[:500]
                    word_count = len(extracted_text.split())
                    ai_result = {
                        'text_preview': text_preview,
                        'word_count': word_count,
                        'char_count': len(extracted_text),
                        'status': 'analyzed',
                    }
                    results['ai_findings'] = ai_result
                    db.add(models.ForensicResult(
                        evidence_id=ev.id,
                        processor='ai_findings',
                        result=ai_result,
                    ))
                    db.commit()
                    _logger.info("Job %s: AI findings generated — %d words", job_id[:8], word_count)
                except Exception as e:
                    _logger.error("Job %s: AI findings failed: %s", job_id[:8], e)

        except Exception as e:
            _logger.error("Job %s: Processing failed: %s", job_id[:8], e, exc_info=True)
            results['error'] = str(e)
            job.error = str(e)

        # ── Finalize job status ──
        job.status = 'completed' if not job.error else 'failed'
        job.finished_at = datetime.now(timezone.utc)
        job.result = results
        db.add(job)
        db.commit()

        # Audit completion
        audit = models.AuditLog(
            actor_id=None, action='processing.completed',
            target_type='evidence', target_id=ev.id,
            detail={'job_id': job.id, 'status': job.status},
        )
        db.add(audit)
        db.commit()
        _logger.info("Job %s: Finalized with status=%s", job_id[:8], job.status)
    finally:
        db.close()


_worker_thread = None


def _worker_loop():
    while True:
        db = database.SessionLocal()
        try:
            # Use SELECT FOR UPDATE pattern via ORM to prevent double-poll
            from sqlalchemy import update as sa_update
            job = db.query(models.ForensicJob).filter(
                models.ForensicJob.status == 'queued'
            ).with_for_update(nowait=False).order_by(
                models.ForensicJob.queued_at.asc()
            ).first()

            if job:
                # Atomically claim the job by setting status to 'claiming'
                job.status = 'claiming'
                db.commit()
                _process_job(job.id)
            else:
                time.sleep(0.5)
        except Exception:
            time.sleep(0.5)
        finally:
            db.close()


@router.post('/jobs/{job_id}/cancel')
def cancel_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Cancel a queued or running job."""
    job = db.query(models.ForensicJob).filter(models.ForensicJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail='job not found')

    if job.status in ('completed', 'failed', 'cancelled'):
        raise HTTPException(status_code=400, detail=f'job already {job.status}')

    with _cancel_lock:
        _cancelled_jobs.add(job_id)

    audit = models.AuditLog(
        actor_id=current_user.id,
        action='processing.cancel',
        target_type='forensic_job',
        target_id=job_id,
        detail={'previous_status': job.status},
    )
    db.add(audit)
    db.commit()

    return {'detail': f'job {job_id} cancellation requested', 'job_id': job_id}


@router.get('/jobs/{job_id}/progress')
def get_job_progress(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get detailed job progress."""
    job = db.query(models.ForensicJob).filter(models.ForensicJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail='job not found')

    result = job.result or {}
    progress = result.get('_progress', '0/0')

    return {
        'job_id': job.id,
        'status': job.status,
        'progress': progress,
        'queued_at': job.queued_at.isoformat() if job.queued_at else None,
        'started_at': job.started_at.isoformat() if job.started_at else None,
        'finished_at': job.finished_at.isoformat() if job.finished_at else None,
        'processors': job.processors,
        'completed_processors': [k for k in result if not k.startswith('_')],
        'error': job.error,
    }


@router.get('/queue/stats')
def get_queue_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get processing queue statistics."""
    queued = db.query(models.ForensicJob).filter(models.ForensicJob.status == 'queued').count()
    running = db.query(models.ForensicJob).filter(models.ForensicJob.status == 'running').count()
    completed = db.query(models.ForensicJob).filter(models.ForensicJob.status == 'completed').count()
    failed = db.query(models.ForensicJob).filter(models.ForensicJob.status == 'failed').count()
    cancelled = db.query(models.ForensicJob).filter(models.ForensicJob.status == 'cancelled').count()

    return {
        'queued': queued,
        'running': running,
        'completed': completed,
        'failed': failed,
        'cancelled': cancelled,
        'active_workers': len([t for t in _worker_threads if t.is_alive()]),
        'max_workers': MAX_WORKERS,
    }


@router.post('/forensic/{evidence_id}')
def run_forensic_processing(evidence_id: str, request: dict | None = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    database.init_db()
    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail='evidence not found')
    roles = [r.name for r in current_user.roles]
    if 'admin' not in roles and 'investigator' not in roles and current_user.id != ev.uploaded_by:
        raise HTTPException(status_code=403, detail='forbidden')

    config = ForensicProcessorConfig()
    if request:
        if "enabled_processors" in request:
            config.enabled_processors = request["enabled_processors"]
        if "ocr_language" in request:
            config.ocr_language = request["ocr_language"]
        if "run_ocr" in request:
            config.run_ocr = request["run_ocr"]
        if "generate_thumbnails" in request:
            config.generate_thumbnails = request["generate_thumbnails"]

    try:
        result = run_full_processing(evidence_id, db, config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'forensic processing failed: {e}')

    audit = models.AuditLog(
        actor_id=current_user.id,
        action='processing.forensic',
        target_type='evidence',
        target_id=evidence_id,
        detail={'processors_run': result.processors_run, 'duration': result.duration_seconds},
    )
    db.add(audit)
    db.commit()

    return {
        'evidence_id': evidence_id,
        'success': result.success,
        'processors_run': result.processors_run,
        'duration_seconds': result.duration_seconds,
        'errors': result.errors,
        'tags': result.schema.tags if result.schema else [],
    }


@router.get('/forensic/processors')
def list_forensic_processors():
    pipeline = ProcessingPipeline()
    return {'processors': pipeline.get_available_processors()}


def start_worker():
    if os.getenv("TESTING") == "1":
        return
    global _worker_thread
    with _worker_lock:
        # Start worker pool up to MAX_WORKERS
        active = [t for t in _worker_threads if t.is_alive()]
        while len(active) < MAX_WORKERS:
            t = threading.Thread(target=_worker_loop, daemon=True)
            t.start()
            active.append(t)
        _worker_threads.clear()
        _worker_threads.extend(active)
