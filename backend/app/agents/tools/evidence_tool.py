"""
EvidenceSearchTool for CrimeKit.

Performs case-isolated evidence content and metadata searches using CrimeKit's
existing search platform, database full-text matching, and OCR/document index.
"""

import time
import logging
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session
from .base import BaseInvestigationTool, ToolResult
from ... import database, models

logger = logging.getLogger(__name__)


class EvidenceSearchTool(BaseInvestigationTool):
    """
    Search digital evidence records and extracted text belonging strictly to the active case.
    """

    @property
    def tool_name(self) -> str:
        return "evidence_search"

    @property
    def description(self) -> str:
        return (
            "Search digital forensic evidence files, documents, OCR transcriptions, and metadata "
            "belonging to this case. Use to find files referencing specific keywords, phone numbers, "
            "suspects, dates, or file hashes."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keywords, entity names, phone numbers, or phrases to find in case evidence.",
                },
                "mime_type": {
                    "type": "string",
                    "description": "Optional filter by MIME type (e.g. 'image', 'pdf', 'text').",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of evidence matches to return (1-20, default 8).",
                    "default": 8,
                    "minimum": 1,
                    "maximum": 20,
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
        limit = min(max(int(arguments.get("limit", 8)), 1), 20)
        mime_filter = arguments.get("mime_type")

        start_time = time.time()
        db: Session = (context or {}).get("db") or database.SessionLocal()
        should_close = (context or {}).get("db") is None

        try:
            # 1. Search Evidence table constrained strictly by case_id
            evidence_q = db.query(models.Evidence).filter(models.Evidence.case_id == case_id)
            if mime_filter:
                evidence_q = evidence_q.filter(models.Evidence.mime_type.ilike(f"%{mime_filter}%"))

            term = f"%{query_text}%"
            # Match on filename, sha256, or id
            file_matches = evidence_q.filter(
                (models.Evidence.filename.ilike(term))
                | (models.Evidence.id.ilike(term))
                | (models.Evidence.sha256.ilike(term))
            ).limit(limit).all()

            # 2. Search Document OCR / extracted text records linked to this case's evidence
            doc_matches = (
                db.query(models.Document, models.Evidence)
                .join(models.Evidence, models.Document.evidence_id == models.Evidence.id)
                .filter(models.Evidence.case_id == case_id)
                .filter(models.Document.text.ilike(term))
                .limit(limit)
                .all()
            )

            results = []
            seen_evidence_ids = set()

            for doc, ev in doc_matches:
                seen_evidence_ids.add(ev.id)
                # Extract text snippet around match
                full_text = doc.text or ""
                idx = full_text.lower().find(query_text.lower())
                snippet_start = max(0, idx - 80)
                snippet_end = min(len(full_text), idx + len(query_text) + 80)
                snippet = full_text[snippet_start:snippet_end].strip()
                if snippet_start > 0:
                    snippet = f"...{snippet}"
                if snippet_end < len(full_text):
                    snippet = f"{snippet}..."

                results.append({
                    "evidence_id": ev.id,
                    "filename": ev.filename,
                    "mime_type": ev.mime_type,
                    "sha256": ev.sha256,
                    "snippet": snippet,
                    "source_type": "document_ocr",
                    "score": 0.95,
                })

            for ev in file_matches:
                if ev.id not in seen_evidence_ids:
                    seen_evidence_ids.add(ev.id)
                    results.append({
                        "evidence_id": ev.id,
                        "filename": ev.filename,
                        "mime_type": ev.mime_type,
                        "sha256": ev.sha256,
                        "snippet": f"Filename match: {ev.filename}",
                        "source_type": "metadata",
                        "score": 0.85,
                    })

            duration_ms = (time.time() - start_time) * 1000

            return ToolResult(
                tool_name=self.tool_name,
                execution_id="",
                status="completed",
                result_count=len(results[:limit]),
                results=results[:limit],
                evidence_refs=list(seen_evidence_ids)[:limit],
                duration_ms=round(duration_ms, 2),
                metadata={"case_id": case_id, "query": query_text},
            )

        finally:
            if should_close:
                db.close()
