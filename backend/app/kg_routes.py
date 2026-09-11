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
    current_user: models.User = Depends(get_current_user),
):
    """Return the knowledge graph for a case with progressive depth loading."""
    try:
        client = kg.get_kg_client()
        # Depth-limited traversal: get nodes within `depth` hops of the case
        cy = f"""
        MATCH (c:Case {{id:$cid}})-[*1..{depth}]-(n)
        RETURN collect(distinct n) AS nodes LIMIT 500
        """
        res = client.query(cy, {"cid": case_id})
        client.close()
        return {"graph": res, "depth": depth}
    except Exception:
        # Fallback to SQLite ForensicResult table for the case
        db = database.SessionLocal()
        try:
            evidence_ids = [
                e.id for e in db.query(models.Evidence.id).filter(models.Evidence.case_id == case_id).all()
            ]
            if not evidence_ids:
                return {"graph": [], "nodes": [], "edges": []}
            
            results = db.query(models.ForensicResult).filter(
                models.ForensicResult.evidence_id.in_(evidence_ids)
            ).all()

            nodes = {}
            edges = []
            for r in results:
                res_data = r.result or {}
                if isinstance(res_data, dict):
                    ents = res_data.get('entities') or []
                    rels = res_data.get('relationships') or []
                    if isinstance(ents, list):
                        for ent in ents:
                            if isinstance(ent, dict) and ent.get('name'):
                                nodes[ent['name']] = {
                                    'id': ent['name'],
                                    'label': ent['name'],
                                    'type': ent.get('type', 'entity')
                                }
                    if isinstance(rels, list):
                        for rel in rels:
                            src = rel.get('source_entity') or rel.get('source')
                            tgt = rel.get('target_entity') or rel.get('target')
                            if isinstance(rel, dict) and src and tgt:
                                edges.append({
                                    'source': src,
                                    'target': tgt,
                                    'type': rel.get('relationship') or rel.get('type', 'cooccurs'),
                                    'confidence': rel.get('confidence', 0),
                                    'evidence_id': rel.get('evidence_id'),
                                })

            return {
                "graph": list(nodes.values()),
                "nodes": list(nodes.values()),
                "edges": edges
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

    if since:
        try:
            client = kg.get_kg_client()
            cy = """
            MATCH (e:Entity)-[r]->(t:Entity)
            WHERE r.detected_at > $since
            RETURN e.name AS source_name, e.type AS source_type,
                   t.name AS target_name, t.type AS target_type,
                   type(r) AS rel_type, r.confidence AS confidence,
                   r.evidence_id AS evidence_id, r.detected_at AS detected_at
            LIMIT $limit
            """
            res = client.query(cy, {"since": since, "limit": limit})
            client.close()
            return {
                "version": version,
                "events": res,
                "has_more": len(res) >= limit,
            }
        except Exception:
            pass

    # Fallback: return full graph for the case
    try:
        client = kg.get_kg_client()
        cy = """
        MATCH (c:Case {id:$cid})-[*1..2]-(n)
        RETURN collect(distinct n) AS nodes LIMIT 1
        """
        res = client.query(cy, {"cid": case_id})
        client.close()
        return {
            "version": version,
            "nodes": res,
            "events": [],
            "has_more": False,
        }
    except Exception:
        return {
            "version": version,
            "nodes": [],
            "events": [],
            "has_more": False,
        }
