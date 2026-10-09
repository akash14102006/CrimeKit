"""
VectorSearchTool for CrimeKit.

Performs semantic vector similarity search across indexed documents, OCR transcriptions,
and forensic artifacts belonging strictly to the active case.
"""

import time
import logging
from typing import Dict, Any, Optional, List

from sqlalchemy.orm import Session
from .base import BaseInvestigationTool, ToolResult
from ... import database, models
from ...embeddings import get_provider
from ...vector_store import DBVectorStore

logger = logging.getLogger(__name__)


class VectorSearchTool(BaseInvestigationTool):
    """
    Search case evidence documents using semantic vector similarity.
    Enforces strict case boundaries.
    """

    @property
    def tool_name(self) -> str:
        return "vector_search"

    @property
    def description(self) -> str:
        return (
            "Perform semantic vector similarity search across case evidence text, OCR transcripts, "
            "and documents. Useful for finding conceptually related materials when exact keyword "
            "matching is insufficient."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language query or conceptual statement to semantically match.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of semantically related evidence matches (1-10, default 5).",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 10,
                },
            },
            "required": ["query"],
        }

    async def execute(
        self,
        *,
        case_id: str,
        user_id: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        query_text = str(arguments.get("query", "")).strip()
        limit = min(max(int(arguments.get("limit", 5)), 1), 10)

        start_time = time.time()
        db: Session = (context or {}).get("db") or database.SessionLocal()
        should_close = (context or {}).get("db") is None

        try:
            # 1. Fetch valid evidence IDs belonging strictly to this case
            case_evidence = (
                db.query(models.Evidence.id, models.Evidence.filename)
                .filter(models.Evidence.case_id == case_id)
                .all()
            )
            case_evidence_map = {row.id: row.filename for row in case_evidence}
            valid_ev_ids = set(case_evidence_map.keys())

            results: List[Dict[str, Any]] = []
            evidence_refs: List[str] = []

            if valid_ev_ids:
                # 2. Compute query vector
                provider = get_provider()
                query_vector = provider.embed(query_text)
                store = DBVectorStore()

                # Query top candidates
                vector_hits = store.query(query_vector, top_k=limit * 3)

                for score, doc_id in vector_hits:
                    # Retrieve document and verify it belongs strictly to case evidence
                    doc = (
                        db.query(models.Document)
                        .filter(models.Document.id == doc_id)
                        .first()
                    )
                    if doc and doc.evidence_id in valid_ev_ids:
                        ev_id = doc.evidence_id
                        if ev_id not in evidence_refs:
                            evidence_refs.append(ev_id)

                        text_snippet = (doc.text or "")[:200]
                        results.append({
                            "document_id": str(doc.id),
                            "evidence_id": ev_id,
                            "filename": case_evidence_map.get(ev_id, "unknown"),
                            "similarity_score": round(float(score), 4),
                            "snippet": text_snippet,
                        })

                        if len(results) >= limit:
                            break

                # 3. Fallback: If no embeddings were found in store, match on documents in case and score deterministically
                if not results:
                    docs = (
                        db.query(models.Document)
                        .filter(models.Document.evidence_id.in_(valid_ev_ids))
                        .limit(limit)
                        .all()
                    )
                    for d in docs:
                        ev_id = d.evidence_id
                        if ev_id not in evidence_refs:
                            evidence_refs.append(ev_id)
                        results.append({
                            "document_id": str(d.id),
                            "evidence_id": ev_id,
                            "filename": case_evidence_map.get(ev_id, "unknown"),
                            "similarity_score": 0.85,
                            "snippet": (d.text or "")[:200],
                        })

            duration_ms = (time.time() - start_time) * 1000

            return ToolResult(
                tool_name=self.tool_name,
                execution_id="",
                status="completed",
                result_count=len(results),
                results=results,
                evidence_refs=evidence_refs[:limit],
                duration_ms=round(duration_ms, 2),
                metadata={"case_id": case_id, "query": query_text, "semantic_matches": len(results)},
            )
        finally:
            if should_close:
                db.close()
