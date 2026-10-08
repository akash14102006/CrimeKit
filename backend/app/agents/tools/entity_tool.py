"""
EntitySearchTool for CrimeKit.

Searches structured entities (persons, phone numbers, organizations, accounts,
locations) extracted from evidence belonging strictly to the active case.
Integrates with CrimeKit's ForensicResult and metadata index.
"""

import time
import logging
from typing import Dict, Any, Optional, List

from sqlalchemy.orm import Session
from .base import BaseInvestigationTool, ToolResult
from ... import database, models

logger = logging.getLogger(__name__)


class EntitySearchTool(BaseInvestigationTool):
    """
    Search extracted entities (persons, telecom identifiers, emails, vehicles)
    originating strictly from the active case evidence.
    """

    @property
    def tool_name(self) -> str:
        return "entity_search"

    @property
    def description(self) -> str:
        return (
            "Search for extracted entities (suspects, witnesses, phone numbers, IMEI, accounts, "
            "locations, or organizations) found in evidence for this case. Returns entity type, "
            "canonical name/value, confidence, and supporting evidence references."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Entity name, phone number, handle, or identifier to search.",
                },
                "entity_type": {
                    "type": "string",
                    "description": "Optional entity category: 'person', 'phone', 'organization', 'location', 'email'.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of entities to return (1-20, default 10).",
                    "default": 10,
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
        query_text = str(arguments.get("query", "")).strip().lower()
        limit = min(max(int(arguments.get("limit", 10)), 1), 20)
        type_filter = arguments.get("entity_type")

        start_time = time.time()
        db: Session = (context or {}).get("db") or database.SessionLocal()
        should_close = (context or {}).get("db") is None

        try:
            # 1. Fetch all evidence IDs associated with this case
            case_evidence_rows = (
                db.query(models.Evidence.id, models.Evidence.filename)
                .filter(models.Evidence.case_id == case_id)
                .all()
            )
            evidence_map = {row.id: row.filename for row in case_evidence_rows}
            evidence_ids = list(evidence_map.keys())

            results: List[Dict[str, Any]] = []
            matched_evidence_refs = set()

            if evidence_ids:
                # 2. Query ForensicResults for this case's evidence
                forensic_rows = (
                    db.query(models.ForensicResult)
                    .filter(models.ForensicResult.evidence_id.in_(evidence_ids))
                    .all()
                )

                for r in forensic_rows:
                    res_data = r.result or {}
                    entities = res_data.get("entities") or []
                    for ent in entities:
                        if not isinstance(ent, dict):
                            continue
                        name = str(ent.get("name", "")).strip()
                        ent_type = str(ent.get("type", "entity")).strip().lower()
                        norm_val = str(ent.get("normalized_value") or name).strip()

                        # Check query match on name or normalized value
                        if query_text in name.lower() or query_text in norm_val.lower():
                            if type_filter and type_filter.lower() not in ent_type:
                                continue

                            ev_id = r.evidence_id
                            matched_evidence_refs.add(ev_id)
                            results.append({
                                "entity_id": ent.get("id") or f"ent_{abs(hash(name)) % 100000}",
                                "name": name,
                                "entity_type": ent_type,
                                "normalized_value": norm_val,
                                "confidence": ent.get("confidence", 0.90),
                                "evidence_id": ev_id,
                                "source_file": evidence_map.get(ev_id, "unknown"),
                            })

            # 3. Fallback check: If no ForensicResults yet, check Evidence metadata_json
            if not results:
                for ev_id, fn in evidence_map.items():
                    ev_item = db.query(models.Evidence).filter(models.Evidence.id == ev_id).first()
                    meta = (ev_item.metadata_json or {}) if ev_item else {}
                    meta_entities = meta.get("entities") or []
                    for ent in meta_entities:
                        if isinstance(ent, dict):
                            name = str(ent.get("name", "")).strip()
                            if query_text in name.lower():
                                matched_evidence_refs.add(ev_id)
                                results.append({
                                    "entity_id": f"ent_{abs(hash(name)) % 100000}",
                                    "name": name,
                                    "entity_type": ent.get("type", "entity"),
                                    "normalized_value": name,
                                    "confidence": ent.get("confidence", 0.85),
                                    "evidence_id": ev_id,
                                    "source_file": fn,
                                })

            # Deduplicate entities by (name, entity_type)
            deduped = {}
            for res in results:
                key = (res["name"].lower(), res["entity_type"])
                if key not in deduped or res["confidence"] > deduped[key]["confidence"]:
                    deduped[key] = res

            final_list = list(deduped.values())[:limit]
            duration_ms = (time.time() - start_time) * 1000

            return ToolResult(
                tool_name=self.tool_name,
                execution_id="",
                status="completed",
                result_count=len(final_list),
                results=final_list,
                evidence_refs=list(matched_evidence_refs)[:limit],
                duration_ms=round(duration_ms, 2),
                metadata={"case_id": case_id, "query": query_text},
            )

        finally:
            if should_close:
                db.close()
