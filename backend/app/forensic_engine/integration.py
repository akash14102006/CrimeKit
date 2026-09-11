"""Integration layer between forensic engine and CrimeKit subsystems."""
import logging
from typing import Optional

from sqlalchemy.orm import Session

from .. import models
from .schemas import EvidenceSchema, ProcessingResult

logger = logging.getLogger(__name__)


def integrate_with_ai_pipeline(
    evidence: EvidenceSchema, result: ProcessingResult, db: Session
) -> None:
    """Feed extracted text and OCR results into the AI pipeline for embedding.
    
    Always creates a Document record when text is available, even if embedding fails.
    """
    from ..ai_pipeline import _text_to_embedding
    text = evidence.extracted_text or evidence.ocr_text
    if not text or len(text.strip()) < 10:
        logger.debug("AI pipeline: skipping evidence %s — text too short", evidence.evidence_id)
        return
    try:
        existing_doc = (
            db.query(models.Document)
            .filter(models.Document.evidence_id == evidence.evidence_id)
            .first()
        )
        if existing_doc:
            existing_doc.text = text
            existing_doc.metadata_json = {
                "processor": "forensic_engine",
                "category": evidence.category.value,
                "updated": True,
            }
            db.commit()
            logger.info("AI pipeline: updated document %s for evidence %s",
                        existing_doc.id, evidence.evidence_id)
        else:
            doc = models.Document(
                evidence_id=evidence.evidence_id,
                text=text,
                metadata_json={
                    "processor": "forensic_engine",
                    "category": evidence.category.value,
                },
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
            logger.info("AI pipeline: created document %s for evidence %s",
                        doc.id, evidence.evidence_id)
            # Attempt embedding — non-fatal if it fails
            try:
                vec = _text_to_embedding(text)
                emb = models.Embedding(document_id=doc.id, vector=vec)
                db.add(emb)
                db.commit()
                logger.info("AI pipeline: created embedding for document %s", doc.id)
            except Exception as emb_err:
                logger.warning("AI pipeline: embedding failed for document %s: %s",
                               doc.id, emb_err)
    except Exception as e:
        logger.error("AI pipeline integration failed: %s", e)


def integrate_with_kg(
    evidence: EvidenceSchema, result: ProcessingResult, db: Session
) -> None:
    """Feed entities, relationships, and timeline events into the Knowledge Graph.
    
    Falls back to storing KG data in ForensicResult when Neo4j is unavailable.
    """
    if not evidence.entities and not evidence.relationships and not evidence.timeline_events:
        return

    # Always store KG data in ForensicResult (SQLite fallback)
    try:
        kg_data = {
            'entities': evidence.entities,
            'relationships': evidence.relationships,
            'timeline': evidence.timeline_events,
            'entity_count': len(evidence.entities),
            'relationship_count': len(evidence.relationships),
            'event_count': len(evidence.timeline_events),
            'source': 'forensic_engine',
        }
        fr = models.ForensicResult(
            evidence_id=evidence.evidence_id,
            processor='forensic_engine.kg',
            result=kg_data,
        )
        db.add(fr)
        db.commit()
        logger.info(
            "KG fallback: stored %d entities, %d relationships, %d events in DB for evidence %s",
            len(evidence.entities), len(evidence.relationships),
            len(evidence.timeline_events), evidence.evidence_id,
        )
    except Exception as e:
        logger.error("KG fallback storage failed: %s", e)

    # Try Neo4j if available
    try:
        from ..kg import get_kg_client
        client = get_kg_client()
        client.ingest(
            entities=evidence.entities,
            relationships=evidence.relationships,
            timeline=evidence.timeline_events,
            evidence_id=evidence.evidence_id,
            case_id=evidence.case_id,
        )
        client.close()
        logger.info(
            "KG Neo4j: ingested %d entities, %d relationships, %d events for evidence %s",
            len(evidence.entities), len(evidence.relationships),
            len(evidence.timeline_events), evidence.evidence_id,
        )
    except Exception as e:
        logger.debug("KG Neo4j unavailable (using SQLite fallback): %s", e)


def store_forensic_results(
    evidence: EvidenceSchema, result: ProcessingResult, db: Session
) -> None:
    """Persist forensic processing results to the database."""
    try:
        ev = (
            db.query(models.Evidence)
            .filter(models.Evidence.id == evidence.evidence_id)
            .first()
        )
        if not ev:
            return
        existing_meta = ev.metadata_json or {}
        existing_meta["forensic_engine"] = evidence.to_dict()
        ev.metadata_json = existing_meta
        if evidence.extracted_text:
            ev.metadata_json["ocr_text"] = evidence.extracted_text
        db.commit()
        for proc_name, proc_result in evidence.processor_results.items():
            fr_bare = models.ForensicResult(
                evidence_id=evidence.evidence_id,
                processor=proc_name,
                result=proc_result,
            )
            fr_ns = models.ForensicResult(
                evidence_id=evidence.evidence_id,
                processor=f"forensic_engine.{proc_name}",
                result=proc_result,
            )
            db.add(fr_bare)
            db.add(fr_ns)

            # Sub-processor aliases for backward compatibility
            if proc_name == 'integrity_forensics' and isinstance(proc_result, dict):
                if 'hashes' in proc_result:
                    db.add(models.ForensicResult(evidence_id=evidence.evidence_id, processor='hashes', result=proc_result['hashes']))
                db.add(models.ForensicResult(evidence_id=evidence.evidence_id, processor='mime', result=proc_result))
        db.commit()
        audit = models.AuditLog(
            actor_id=None,
            action="forensic_engine.completed",
            target_type="evidence",
            target_id=evidence.evidence_id,
            detail={
                "processors_run": result.processors_run,
                "duration_seconds": result.duration_seconds,
                "errors": result.errors,
                "tags": evidence.tags,
            },
        )
        db.add(audit)
        db.commit()
        logger.info("Stored forensic results for evidence %s", evidence.evidence_id)
    except Exception as e:
        logger.error("Failed to store forensic results: %s", e)


def run_full_processing(
    evidence_id: str, db: Session, config=None
) -> ProcessingResult:
    """End-to-end forensic processing with all integrations."""
    from .pipeline import ProcessingPipeline
    from .. import database

    ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    if not ev:
        raise ValueError(f"Evidence {evidence_id} not found")

    pipeline = ProcessingPipeline(config)
    evidence = EvidenceSchema(
        evidence_id=ev.id,
        case_id=ev.case_id,
        storage_path=ev.storage_path,
        filename=ev.filename,
        sha256=ev.sha256,
        size=ev.size,
        mime_type=ev.mime_type,
    )
    result = pipeline.process(evidence)
    store_forensic_results(evidence, result, db)
    integrate_with_ai_pipeline(evidence, result, db)
    integrate_with_kg(evidence, result, db)
    return result
