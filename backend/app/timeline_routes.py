from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging

from . import models, database, auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/timeline", tags=["timeline"])


class TimelineEvent(BaseModel):
    id: str
    evidence_id: Optional[str] = None
    case_id: Optional[str] = None
    timestamp: str
    title: str
    description: str
    source: str  # e.g., 'exif', 'ocr', 'email', 'system'
    metadata: Optional[Dict[str, Any]] = None


@router.get("", response_model=List[TimelineEvent])
@router.get("/", response_model=List[TimelineEvent])
def get_timeline_events(
    case_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(database.get_db_session),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Retrieve chronological timeline events across cases or for a specific case."""
    events = []
    
    # Query forensic results where timeline data was extracted
    query = db.query(models.ForensicResult)
    if case_id:
        # Get evidence IDs associated with case_id
        evidence_ids = [e.id for e in db.query(models.Evidence).filter(models.Evidence.case_id == case_id).all()]
        query = query.filter(models.ForensicResult.evidence_id.in_(evidence_ids))

    results = query.limit(limit).all()

    for res in results:
        res_data = res.result or {}
        if isinstance(res_data, dict) and "timeline" in res_data:
            t_data = res_data["timeline"]
            if isinstance(t_data, list):
                for item in t_data:
                    events.append(
                        TimelineEvent(
                            id=f"{res.id}-{len(events)}",
                            evidence_id=res.evidence_id,
                            case_id=case_id,
                            timestamp=str(item.get("timestamp", res.created_at)),
                            title=item.get("event", "Forensic Artifact Detected"),
                            description=item.get("description", f"Extracted via {res.processor}"),
                            source=res.processor or "forensic_engine",
                            metadata=item.get("metadata"),
                        )
                    )

    # If few or no events found, extract timeline events directly from Document text
    if len(events) < 5:
        from .kg import extract_timeline
        doc_query = db.query(models.Document)
        if case_id:
            evidence_ids = [e.id for e in db.query(models.Evidence).filter(models.Evidence.case_id == case_id).all()]
            doc_query = doc_query.filter(models.Document.evidence_id.in_(evidence_ids))
        docs = doc_query.limit(50).all()

        for doc in docs:
            if doc.text:
                extracted = extract_timeline(doc.text)
                for item in extracted:
                    events.append(
                        TimelineEvent(
                            id=f"doc-{doc.id}-{len(events)}",
                            evidence_id=doc.evidence_id,
                            case_id=case_id,
                            timestamp=str(item.get("date", doc.created_at)),
                            title=f"Event Extracted from Text",
                            description=item.get("summary", ""),
                            source="text_extraction",
                            metadata={"document_id": doc.id},
                        )
                    )

    # Sort events chronologically
    events.sort(key=lambda x: str(x.timestamp), reverse=True)
    return events
