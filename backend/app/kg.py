"""
Knowledge Graph module for CrimeKit.

Provides entity extraction, relationship extraction, timeline extraction,
and Neo4j graph ingestion. Uses ML-based extraction when available,
with regex fallback.
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from neo4j import GraphDatabase
except Exception:
    GraphDatabase = None

from .embeddings import get_provider
from .vector_store import DBVectorStore
from . import database
from . import models
from .entity_extractor import extract_entities as _ml_extract_entities
from .entity_normalizer import normalize_entities
from .entity_resolver import resolve_entities
from .relationship_extractor import extract_relationships as _semantic_extract_relationships

logger = logging.getLogger(__name__)

DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


def extract_entities(
    text: str,
    use_ml: bool = True,
    min_confidence: float = 0.5,
) -> List[Dict[str, Any]]:
    """
    Extract entities from text using ML (GLiNER) + regex fallback.

    Returns entities with: name, type, confidence, source, original_value, normalized_value.
    """
    if not text:
        return []

    # ML + regex extraction
    raw_entities = _ml_extract_entities(text, use_ml=use_ml, min_confidence=min_confidence)

    # Normalize
    normalized = normalize_entities(raw_entities)

    return normalized


def extract_relationships(
    text: str,
    entities: List[Dict[str, Any]],
    evidence_id: Optional[str] = None,
    artifact_id: Optional[str] = None,
    page: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Extract relationships between entities with evidence provenance.

    Uses pattern-based extraction + co-occurrence fallback.
    Every relationship includes evidence provenance.
    """
    if not text or not entities:
        return []

    return _semantic_extract_relationships(
        text, entities,
        evidence_id=evidence_id,
        artifact_id=artifact_id,
        page=page,
    )


def extract_timeline(text: str) -> List[Dict[str, Any]]:
    """Extract timeline events (dates + context) from text."""
    if not text:
        return []
    out = []
    for m in DATE_RE.findall(text):
        idx = text.find(m)
        start = max(0, text.rfind('.', 0, idx))
        end = text.find('.', idx)
        snippet = text[start + 1:end].strip() if end != -1 else text[start + 1:].strip()
        out.append({"date": m, "summary": snippet})
    return out


class KGClient:
    """Neo4j-backed knowledge graph client with evidence provenance."""

    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        if GraphDatabase is None:
            raise RuntimeError('neo4j driver not available')
        uri = uri or os.getenv('NEO4J_URI')
        if not uri:
            raise RuntimeError('NEO4J_URI not set')
        user = user or os.getenv('NEO4J_USER', 'neo4j')
        password = password or os.getenv('NEO4J_PASSWORD')
        if not password:
            raise RuntimeError('NEO4J_PASSWORD not set')
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.emb = get_provider()
        self.vs = DBVectorStore()

    def close(self):
        try:
            self.driver.close()
        except Exception:
            pass

    def ingest(
        self,
        entities: List[Dict[str, Any]],
        relationships: Optional[List[Dict[str, Any]]] = None,
        timeline: Optional[List[Dict[str, Any]]] = None,
        evidence_id: Optional[str] = None,
        case_id: Optional[str] = None,
    ) -> Dict[str, int]:
        """
        Ingest entities, relationships, and timeline events into Neo4j.

        All relationships must include evidence provenance.
        Returns counts of ingested items.
        """
        relationships = relationships or []
        timeline = timeline or []
        counts = {"entities": 0, "relationships": 0, "timeline": 0}

        with self.driver.session() as s:
            # Create or merge evidence and case nodes
            if evidence_id:
                s.run(
                    "MERGE (ev:Evidence {id:$id}) ON CREATE SET ev.created_at = timestamp()",
                    id=evidence_id,
                )
            if case_id:
                s.run(
                    "MERGE (c:Case {id:$id}) ON CREATE SET c.created_at = timestamp()",
                    id=case_id,
                )

            # Ingest entities
            for e in entities:
                name = e.get("name")
                if not name:
                    continue
                etype = e.get("type", "entity")
                props = {
                    "name": name,
                    "type": etype,
                    "confidence": e.get("confidence", 0),
                    "source": e.get("source", "regex"),
                    "normalized_value": e.get("normalized_value", name),
                }
                s.run(
                    "MERGE (n:Entity {name:$name, type:$type}) SET n += $props",
                    name=name, type=etype, props=props,
                )
                # Link to evidence
                if evidence_id:
                    s.run(
                        "MATCH (n:Entity {name:$name}), (ev:Evidence {id:$eid}) "
                        "MERGE (n)-[:MENTIONED_IN]->(ev)",
                        name=name, eid=evidence_id,
                    )
                # Link to case
                if case_id:
                    s.run(
                        "MATCH (n:Entity {name:$name}), (c:Case {id:$cid}) "
                        "MERGE (n)-[:RELATED_TO]->(c)",
                        name=name, cid=case_id,
                    )
                # Store embedding
                try:
                    vec = self.emb.embed(name)
                    doc_id = f"kg:entity:{name}"
                    self.vs.upsert(doc_id, vec)
                except Exception:
                    pass
                counts["entities"] += 1

            # Ingest relationships with evidence provenance
            for r in relationships:
                src = r.get("source_entity", r.get("source"))
                tgt = r.get("target_entity", r.get("target"))
                if not src or not tgt:
                    continue

                rel_type = r.get("relationship", r.get("type", "RELATED"))
                confidence = r.get("confidence", 0)
                r_evidence_id = r.get("evidence_id", evidence_id)
                r_artifact_id = r.get("artifact_id")
                source_ref = r.get("source_reference", {})
                processor = r.get("processor", "unknown")

                s.run(
                    """
                    MATCH (a:Entity {name:$a}), (b:Entity {name:$b})
                    MERGE (a)-[rel:RELATIONSHIP {type:$type, evidence_id:$eid}]->(b)
                    SET rel.confidence = $confidence,
                        rel.artifact_id = $artifact_id,
                        rel.source_page = $page,
                        rel.source_text = $text_span,
                        rel.processor = $processor,
                        rel.created_at = timestamp()
                    """,
                    a=src,
                    b=tgt,
                    type=rel_type,
                    eid=r_evidence_id,
                    confidence=confidence,
                    artifact_id=r_artifact_id,
                    page=source_ref.get("page"),
                    text_span=source_ref.get("text_span"),
                    processor=processor,
                )
                counts["relationships"] += 1

            # Ingest timeline events
            for t in timeline:
                when = t.get("date")
                summary = t.get("summary")
                if not when:
                    continue
                s.run(
                    "MERGE (ev:Event {date:$date, summary:$summary}) RETURN ev",
                    date=when, summary=summary,
                )
                if case_id:
                    s.run(
                        "MATCH (e:Event {date:$date, summary:$summary}), (c:Case {id:$cid}) "
                        "MERGE (e)-[:AFFECTS]->(c)",
                        date=when, summary=summary, cid=case_id,
                    )
                if evidence_id:
                    s.run(
                        "MATCH (e:Event {date:$date, summary:$summary}), (ev:Evidence {id:$eid}) "
                        "MERGE (e)-[:RELATED_TO_EVIDENCE]->(ev)",
                        date=when, summary=summary, eid=evidence_id,
                    )
                counts["timeline"] += 1

        return counts

    def query(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        with self.driver.session() as s:
            res = s.run(cypher, params or {})
            out = []
            for r in res:
                try:
                    out.append({k: v for k, v in r.items()})
                except Exception:
                    out.append(dict(r.items()))
            return out


def get_kg_client() -> KGClient:
    return KGClient()
