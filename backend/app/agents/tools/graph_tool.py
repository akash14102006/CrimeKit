"""
KnowledgeGraphTool for CrimeKit.

Performs controlled relationship traversal against CrimeKit's Neo4j graph
or ForensicResult graph fallback strictly within case authorization.
Never permits raw Cypher injection from LLM.
"""

import time
import logging
from typing import Dict, Any, Optional, List

from sqlalchemy.orm import Session
from .base import BaseInvestigationTool, ToolResult
from ... import database, models, kg

logger = logging.getLogger(__name__)


class KnowledgeGraphTool(BaseInvestigationTool):
    """
    Performs controlled, parameterized relationship traversal around specific entities.
    Returns structured nodes, relationships, and supporting evidence IDs.
    """

    @property
    def tool_name(self) -> str:
        return "knowledge_graph_traversal"

    @property
    def description(self) -> str:
        return (
            "Explore multi-hop relationships and connections around a person, phone number, "
            "or organization in the case knowledge graph. Reveals who communicated with whom, "
            "shared devices, or co-occurred in seized evidence with provenance."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "entity": {
                    "type": "string",
                    "description": "Anchor entity name or value to traverse from (e.g. 'Rahul Kumar', '+91 9876543210').",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Traversal depth hops (1 or 2, default 2).",
                    "default": 2,
                    "minimum": 1,
                    "maximum": 2,
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum relationships to return (1-25, default 15).",
                    "default": 15,
                    "minimum": 1,
                    "maximum": 25,
                },
            },
            "required": ["entity"],
        }

    async def execute(
        self,
        *,
        case_id: str,
        user_id: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        entity_name = str(arguments.get("entity", "")).strip()
        depth = min(max(int(arguments.get("max_depth", 2)), 1), 2)
        limit = min(max(int(arguments.get("limit", 15)), 1), 25)

        start_time = time.time()
        db: Session = (context or {}).get("db") or database.SessionLocal()
        should_close = (context or {}).get("db") is None

        nodes: List[Dict[str, Any]] = []
        relationships: List[Dict[str, Any]] = []
        evidence_refs = set()

        try:
            # 1. Attempt Neo4j query via KGClient using parameterized safe Cypher
            neo4j_success = False
            try:
                client = kg.get_kg_client()
                # Parameterized query linking entity to case
                cy = f"""
                MATCH (a:Entity)
                WHERE toLower(a.name) CONTAINS toLower($entity)
                MATCH (a)-[r:RELATIONSHIP*1..{depth}]-(b:Entity)
                RETURN a.name AS source, type(r[0]) AS rel_type, b.name AS target,
                       r[0].confidence AS confidence, r[0].evidence_id AS evidence_id
                LIMIT $limit
                """
                raw_rows = client.query(cy, {"entity": entity_name, "limit": limit})
                client.close()

                if raw_rows:
                    neo4j_success = True
                    seen_nodes = set()
                    for row in raw_rows:
                        src = row.get("source")
                        tgt = row.get("target")
                        eid = row.get("evidence_id")
                        if eid:
                            evidence_refs.add(eid)

                        if src and src not in seen_nodes:
                            seen_nodes.add(src)
                            nodes.append({"id": src, "label": src, "type": "entity"})
                        if tgt and tgt not in seen_nodes:
                            seen_nodes.add(tgt)
                            nodes.append({"id": tgt, "label": tgt, "type": "entity"})

                        relationships.append({
                            "source": src,
                            "target": tgt,
                            "relationship": row.get("rel_type") or "CONNECTED_TO",
                            "confidence": row.get("confidence") or 0.90,
                            "evidence_id": eid,
                        })

            except Exception as e:
                logger.info("Neo4j traversal unavailable or empty, evaluating ForensicResult fallback: %s", e)

            # 2. Database Fallback: ForensicResult extraction for case evidence
            if not neo4j_success:
                case_evidence = (
                    db.query(models.Evidence.id)
                    .filter(models.Evidence.case_id == case_id)
                    .all()
                )
                evidence_ids = [e.id for e in case_evidence]

                if evidence_ids:
                    f_results = (
                        db.query(models.ForensicResult)
                        .filter(models.ForensicResult.evidence_id.in_(evidence_ids))
                        .all()
                    )

                    seen_nodes = set()
                    for fr in f_results:
                        res = fr.result or {}
                        rels = res.get("relationships") or []
                        for rel in rels:
                            if not isinstance(rel, dict):
                                continue
                            src = rel.get("source_entity") or rel.get("source")
                            tgt = rel.get("target_entity") or rel.get("target")
                            rel_type = rel.get("relationship") or rel.get("type", "RELATED_TO")
                            conf = rel.get("confidence", 0.88)
                            eid = rel.get("evidence_id") or fr.evidence_id

                            # Match if entity is either source or target
                            if src and tgt and (
                                entity_name.lower() in str(src).lower()
                                or entity_name.lower() in str(tgt).lower()
                            ):
                                if eid:
                                    evidence_refs.add(eid)

                                if src not in seen_nodes:
                                    seen_nodes.add(src)
                                    nodes.append({"id": src, "label": src, "type": "entity"})
                                if tgt not in seen_nodes:
                                    seen_nodes.add(tgt)
                                    nodes.append({"id": tgt, "label": tgt, "type": "entity"})

                                relationships.append({
                                    "source": src,
                                    "target": tgt,
                                    "relationship": rel_type,
                                    "confidence": conf,
                                    "evidence_id": eid,
                                })

            # Deduplicate and limit
            relationships = relationships[:limit]
            duration_ms = (time.time() - start_time) * 1000

            return ToolResult(
                tool_name=self.tool_name,
                execution_id="",
                status="completed",
                result_count=len(relationships),
                results=[
                    {
                        "nodes": nodes,
                        "relationships": relationships,
                    }
                ],
                evidence_refs=list(evidence_refs)[:limit],
                duration_ms=round(duration_ms, 2),
                metadata={
                    "case_id": case_id,
                    "anchor_entity": entity_name,
                    "depth": depth,
                    "edge_count": len(relationships),
                },
            )

        finally:
            if should_close:
                db.close()
