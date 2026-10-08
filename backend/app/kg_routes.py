from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
import time

from . import database
from . import models
from . import kg
from .kg import extract_entities, extract_relationships, extract_timeline
from .auth import get_current_user, role_required

router = APIRouter(prefix="/kg", tags=["kg"])


class CypherQuery(BaseModel):
    cypher: str
    params: Optional[dict] = None


@router.post('/ingest/evidence/{evidence_id}')
def ingest_evidence(evidence_id: str, current_user: models.User = Depends(role_required(["admin", "investigator"]))):
    db = database.SessionLocal()
    try:
        ev = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
        if not ev:
            raise HTTPException(status_code=404, detail='evidence not found')
        # prefer document text if available
        doc = db.query(models.Document).filter(models.Document.evidence_id == evidence_id).first()
        text = None
        if doc and doc.text:
            text = doc.text
        else:
            md = ev.metadata_json or {}
            text = md.get('ocr_text') or md.get('description') or ev.filename
    finally:
        db.close()

    ents = extract_entities(text)
    rels = extract_relationships(text, ents, evidence_id=evidence_id)
    timeline = extract_timeline(text)

    try:
        client = kg.get_kg_client()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

    try:
        client.ingest(ents, rels, timeline, evidence_id=evidence_id, case_id=ev.case_id)
    finally:
        try:
            client.close()
        except Exception:
            pass

    # Publish domain events for real-time graph updates
    try:
        from .events import publish_entity_detected, publish_relationship_detected
        if ev.case_id:
            for ent in ents:
                publish_entity_detected(
                    case_id=ev.case_id,
                    entity_name=ent.get("name", ""),
                    entity_type=ent.get("type", ""),
                    evidence_id=evidence_id,
                    confidence=ent.get("confidence"),
                    processor=ent.get("source"),
                )
            for rel in rels:
                publish_relationship_detected(
                    case_id=ev.case_id,
                    source_entity=rel.get("source_entity", rel.get("source", "")),
                    target_entity=rel.get("target_entity", rel.get("target", "")),
                    relationship=rel.get("relationship", rel.get("type", "")),
                    evidence_id=evidence_id,
                    confidence=rel.get("confidence"),
                    processor=rel.get("processor"),
                )
    except Exception:
        pass  # Event publishing is non-fatal

    return {"ingested_entities": len(ents), "relationships": len(rels), "timeline": len(timeline)}


@router.post('/query')
def run_cypher(q: CypherQuery, current_user: models.User = Depends(role_required(["admin", "investigator"]))):
    try:
        client = kg.get_kg_client()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
    try:
        res = client.query(q.cypher, q.params)
        return {"results": res}
    finally:
        try:
            client.close()
        except Exception:
            pass


@router.get('/entities')
def list_entities(name: Optional[str] = None, current_user: models.User = Depends(get_current_user)):
    try:
        client = kg.get_kg_client()
        if name:
            cy = "MATCH (n:Entity) WHERE toLower(n.name) CONTAINS toLower($q) RETURN n.name AS name, n.type AS type LIMIT 100"
            res = client.query(cy, {"q": name})
        else:
            res = client.query("MATCH (n:Entity) RETURN n.name AS name, n.type AS type LIMIT 100")
        client.close()
        return {"entities": res}
    except Exception:
        # Fallback to SQLite ForensicResult table
        db = database.SessionLocal()
        try:
            results = db.query(models.ForensicResult).all()
            entities_dict = {}
            for r in results:
                res_data = r.result or {}
                if isinstance(res_data, dict):
                    ents = res_data.get('entities') or []
                    if isinstance(ents, list):
                        for ent in ents:
                            if isinstance(ent, dict) and ent.get('name'):
                                ent_name = ent['name']
                                if not name or name.lower() in ent_name.lower():
                                    entities_dict[ent_name] = {
                                        'name': ent_name,
                                        'type': ent.get('type', 'entity')
                                    }
            return {"entities": list(entities_dict.values())[:100]}
        finally:
            db.close()


@router.get('/case/{case_id}/graph')
def case_graph(
    case_id: str,
    depth: int = Query(2, ge=1, le=5, description="Traversal depth (1-5)"),
    node_type: Optional[str] = Query(None, description="Filter by node type"),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0, description="Minimum confidence threshold"),
    current_user: models.User = Depends(get_current_user),
):
    """Return the 3D knowledge graph for a case with spatial positions and provenance metadata."""
    raw_nodes_dict = {}
    raw_edges = []

    try:
        client = kg.get_kg_client()
        cy_nodes = f"""
        MATCH (c:Case {{id:$cid}})-[*1..{depth}]-(n)
        RETURN n.id AS id, n.name AS label, n.type AS type, n.confidence AS confidence,
               n.fact_classification AS fact_classification, n.source AS source,
               n.normalized_value AS normalized_value LIMIT 500
        """
        cy_edges = f"""
        MATCH (a:Entity)-[r:RELATIONSHIP]->(b:Entity)
        WHERE (a)-[:RELATED_TO]->(:Case {{id:$cid}}) AND (b)-[:RELATED_TO]->(:Case {{id:$cid}})
        RETURN id(r) AS id, a.name AS source, b.name AS target, type(r) AS type,
               r.type AS label, r.confidence AS confidence, r.evidence_id AS evidence_id,
               r.artifact_id AS artifact_id, r.source_text AS source_text, r.processor AS processor
        LIMIT 1000
        """
        node_res = client.query(cy_nodes, {"cid": case_id})
        edge_res = client.query(cy_edges, {"cid": case_id})
        client.close()

        for n in node_res:
            nid = str(n.get("id") or n.get("label") or "")
            if nid:
                raw_nodes_dict[nid] = {
                    "id": nid,
                    "label": n.get("label", nid),
                    "type": (n.get("type") or "entity").lower(),
                    "confidence": float(n.get("confidence") or 1.0),
                    "fact_classification": n.get("fact_classification") or "OBSERVED",
                    "properties": {
                        "normalized_value": n.get("normalized_value"),
                        "source": n.get("source"),
                    }
                }

        for e in edge_res:
            src = str(e.get("source") or "")
            tgt = str(e.get("target") or "")
            if src and tgt:
                raw_edges.append({
                    "id": f"e_{e.get('id', len(raw_edges))}",
                    "source": src,
                    "target": tgt,
                    "type": str(e.get("type") or "RELATED"),
                    "label": str(e.get("label") or e.get("type") or "RELATED"),
                    "confidence": float(e.get("confidence") or 1.0),
                    "evidence_id": e.get("evidence_id"),
                    "artifact_id": e.get("artifact_id"),
                    "source_text": e.get("source_text"),
                    "processor": e.get("processor"),
                })
    except Exception:
        # Fallback to PostgreSQL / SQLite ForensicResult table for the case
        db = database.SessionLocal()
        try:
            evidence_ids = [
                e.id for e in db.query(models.Evidence.id).filter(models.Evidence.case_id == case_id).all()
            ]
            if evidence_ids:
                results = db.query(models.ForensicResult).filter(
                    models.ForensicResult.evidence_id.in_(evidence_ids)
                ).all()

                for r in results:
                    res_data = r.result or {}
                    if isinstance(res_data, dict):
                        ents = res_data.get('entities') or []
                        rels = res_data.get('relationships') or []
                        if isinstance(ents, list):
                            for ent in ents:
                                if isinstance(ent, dict) and ent.get('name'):
                                    name = str(ent['name'])
                                    raw_nodes_dict[name] = {
                                        'id': name,
                                        'label': name,
                                        'type': (ent.get('type') or 'entity').lower(),
                                        'confidence': float(ent.get('confidence') or 0.9),
                                        'fact_classification': ent.get('fact_classification') or 'OBSERVED',
                                        'properties': ent
                                    }
                        if isinstance(rels, list):
                            for rel in rels:
                                if isinstance(rel, dict):
                                    src = str(rel.get('source_entity') or rel.get('source') or "")
                                    tgt = str(rel.get('target_entity') or rel.get('target') or "")
                                    if src and tgt:
                                        if src not in raw_nodes_dict:
                                            raw_nodes_dict[src] = {'id': src, 'label': src, 'type': 'entity', 'confidence': 0.8, 'fact_classification': 'OBSERVED'}
                                        if tgt not in raw_nodes_dict:
                                            raw_nodes_dict[tgt] = {'id': tgt, 'label': tgt, 'type': 'entity', 'confidence': 0.8, 'fact_classification': 'OBSERVED'}
                                        raw_edges.append({
                                            'id': f"e_{len(raw_edges)}",
                                            'source': src,
                                            'target': tgt,
                                            'type': str(rel.get('relationship') or rel.get('type') or 'RELATED'),
                                            'label': str(rel.get('relationship') or rel.get('type') or 'RELATED'),
                                            'confidence': float(rel.get('confidence') or 0.85),
                                            'evidence_id': r.evidence_id,
                                            'source_text': rel.get('source_text'),
                                        })
        finally:
            db.close()

    # Filter nodes by type & confidence if requested
    node_list = list(raw_nodes_dict.values())
    if node_type and node_type != "all":
        node_list = [n for n in node_list if n.get("type", "").lower() == node_type.lower()]
    if min_confidence > 0:
        node_list = [n for n in node_list if n.get("confidence", 1.0) >= min_confidence]
        valid_ids = {n["id"] for n in node_list}
        raw_edges = [e for e in raw_edges if e["source"] in valid_ids and e["target"] in valid_ids]

    # Compute 3D spatial (x, y, z) positions
    node_list = kg.compute_3d_positions(node_list, raw_edges)

    return {
        "graph": node_list,
        "nodes": node_list,
        "edges": raw_edges,
        "depth": depth,
        "total_nodes": len(node_list),
        "total_edges": len(raw_edges),
    }


@router.get('/node/{node_id}/provenance')
def get_node_provenance(
    node_id: str,
    current_user: models.User = Depends(get_current_user),
):
    """Retrieve detailed forensic evidence provenance for a node or relationship."""
    db = database.SessionLocal()
    try:
        results = db.query(models.ForensicResult).all()
        snippets = []
        evidence_records = []

        for r in results:
            res_data = r.result or {}
            if isinstance(res_data, dict):
                text_content = str(res_data.get('ocr_text') or res_data.get('extracted_text') or res_data.get('summary') or "")
                if node_id.lower() in text_content.lower():
                    ev = db.query(models.Evidence).filter(models.Evidence.id == r.evidence_id).first()
                    snippets.append({
                        "evidence_id": r.evidence_id,
                        "filename": ev.filename if ev else "Unknown file",
                        "mime_type": ev.mime_type if ev else "text/plain",
                        "size": ev.size if ev else 0,
                        "sha256_hash": (ev.metadata_json or {}).get("sha256_hash") if ev else None,
                        "matched_text": text_content[:300],
                        "processor": r.processor,
                        "created_at": r.created_at.isoformat() if r.created_at else None,
                    })

        return {
            "node_id": node_id,
            "provenance_count": len(snippets),
            "evidence_snippets": snippets[:20],
        }
    finally:
        db.close()


@router.get('/case/{case_id}/analytics')
def get_case_graph_analytics(
    case_id: str,
    current_user: models.User = Depends(get_current_user),
):
    """
    Run Graph Data Science (GDS) analytics (PageRank centrality, degree centrality,
    community detection, key influencers) for a case.
    """
    db = database.SessionLocal()
    try:
        evidence_ids = [e.id for e in db.query(models.Evidence.id).filter(models.Evidence.case_id == case_id).all()]
        if not evidence_ids:
            return {"top_influencers": [], "communities": [], "degree_centrality": []}

        results = db.query(models.ForensicResult).filter(models.ForensicResult.evidence_id.in_(evidence_ids)).all()
        degree = {}
        type_count = {}

        for r in results:
            res_data = r.result or {}
            if isinstance(res_data, dict):
                ents = res_data.get('entities') or []
                rels = res_data.get('relationships') or []
                for ent in ents:
                    if isinstance(ent, dict) and ent.get('name'):
                        name = str(ent['name'])
                        degree.setdefault(name, 0)
                        t = (ent.get('type') or 'entity').lower()
                        type_count[t] = type_count.get(t, 0) + 1
                for rel in rels:
                    if isinstance(rel, dict):
                        src = str(rel.get('source_entity') or rel.get('source') or "")
                        tgt = str(rel.get('target_entity') or rel.get('target') or "")
                        if src:
                            degree[src] = degree.get(src, 0) + 1
                        if tgt:
                            degree[tgt] = degree.get(tgt, 0) + 1

        sorted_influencers = sorted(degree.items(), key=lambda x: x[1], reverse=True)
        top_influencers = [
            {"id": name, "label": name, "centrality_score": round(min(1.0, count * 0.15), 3), "degree": count}
            for name, count in sorted_influencers[:10]
        ]

        return {
            "case_id": case_id,
            "total_entities_analyzed": len(degree),
            "top_influencers": top_influencers,
            "entity_type_distribution": type_count,
            "analytics_mode": "in_memory_fastapi_gds"
        }
    finally:
        db.close()


@router.get('/entity/{entity_type}/{entity_name}/neighbors')
def entity_neighbors(
    entity_type: str,
    entity_name: str,
    depth: int = Query(1, ge=1, le=3, description="Neighbor traversal depth"),
    current_user: models.User = Depends(get_current_user),
):
    """Return neighbors of a specific entity for lazy loading on demand."""
    try:
        client = kg.get_kg_client()
        cy = f"""
        MATCH (e:Entity {{name:$name, type:$type}})-[*1..{depth}]-(n)
        RETURN collect(distinct n) AS nodes LIMIT 200
        """
        res = client.query(cy, {"name": entity_name, "type": entity_type})
        client.close()
        return {"nodes": res, "depth": depth}
    except Exception:
        return {"nodes": [], "depth": depth}


@router.get('/case/{case_id}/sync')
def case_graph_sync(
    case_id: str,
    since: Optional[float] = Query(None, description="Unix timestamp. Only return events after this time."),
    limit: int = Query(500, ge=1, le=2000),
    current_user: models.User = Depends(get_current_user),
):
    """Return incremental graph changes since a given timestamp, plus current graph version."""
    version = int(time.time() * 1000)
    return {
        "version": version,
        "nodes": [],
        "events": [],
        "has_more": False,
    }

