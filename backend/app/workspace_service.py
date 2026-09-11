from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from typing import List, Dict, Any

from . import models, workspace_schemas
from .kg import get_kg_client, extract_timeline
from .ai_pipeline import _text_to_embedding, _cosine

class WorkspaceService:
    def __init__(self, db: Session):
        self.db = db

    async def get_workspace(self, case_id: str) -> workspace_schemas.InvestigationWorkspaceResponse:
        case = self.db.query(models.Case).filter(models.Case.id == case_id).first()
        if not case:
            raise ValueError("Case not found")

        # 1. Case Summary
        case_summary = workspace_schemas.WorkspaceCaseSummary(
            id=case.id,
            title=case.title,
            description=case.description,
            status=case.status,
            created_by=case.created_by,
            created_at=case.created_at
        )

        # 2. Evidence & Progress Stats
        evidence_items = self.db.query(models.Evidence).filter(models.Evidence.case_id == case_id).all()
        workspace_evidence = []
        evidence_ids = [e.id for e in evidence_items]
        
        # Prefetch counts and existence
        custody_counts = {
            row.evidence_id: row.count 
            for row in self.db.query(
                models.ChainOfCustody.evidence_id, 
                func.count(models.ChainOfCustody.id).label('count')
            ).filter(models.ChainOfCustody.evidence_id.in_(evidence_ids)).group_by(models.ChainOfCustody.evidence_id).all()
        } if evidence_ids else {}

        docs = {
            d.evidence_id: d 
            for d in self.db.query(models.Document).filter(models.Document.evidence_id.in_(evidence_ids)).all()
        } if evidence_ids else {}

        for e in evidence_items:
            workspace_evidence.append(workspace_schemas.WorkspaceEvidenceItem(
                id=e.id,
                filename=e.filename,
                sha256=e.sha256,
                size=e.size,
                mime_type=e.mime_type,
                uploaded_by=e.uploaded_by,
                uploaded_at=e.uploaded_at,
                custody_entries=custody_counts.get(e.id, 0),
                has_document=e.id in docs
            ))

        # 3. Chain of Custody
        custody_events = self.db.query(models.ChainOfCustody).filter(
            models.ChainOfCustody.evidence_id.in_(evidence_ids)
        ).order_by(models.ChainOfCustody.timestamp.desc()).limit(50).all() if evidence_ids else []
        
        workspace_custody = [
            workspace_schemas.WorkspaceCustodyEvent(
                id=c.id,
                evidence_id=c.evidence_id,
                action=c.action,
                actor_id=c.actor_id,
                timestamp=c.timestamp,
                notes=c.notes
            ) for c in custody_events
        ]

        # 4. Timeline (Aggregated from KG and Evidence)
        workspace_timeline = []
        for doc in docs.values():
            if doc.text:
                extracted = extract_timeline(doc.text)
                for item in extracted:
                    workspace_timeline.append(workspace_schemas.WorkspaceTimelineEvent(
                        source_type="evidence",
                        source_id=doc.evidence_id,
                        date=item.get('date'),
                        summary=item.get('summary')
                    ))
        
        workspace_timeline.sort(key=lambda x: x.date or "", reverse=True)

        # 5. Knowledge Graph Summary
        kg_summary = self._get_kg_summary(case_id)

        # 6. AI Findings (Top documents by "importance" or recent queries)
        ai_findings = []
        # In a real scenario, this might be powered by a specific analysis job
        # Here we'll just take documents with non-empty text
        for doc_id, doc in list(docs.items())[:5]:
            ai_findings.append(workspace_schemas.WorkspaceAIFinding(
                document_id=doc.id,
                evidence_id=doc.evidence_id,
                score=0.9, # Placeholder
                snippet=doc.text[:200] if doc.text else None
            ))

        # 7. Progress
        forensic_jobs = self.db.query(models.ForensicJob).filter(
            models.ForensicJob.evidence_id.in_(evidence_ids)
        ).all() if evidence_ids else []
        
        jobs_total = len(forensic_jobs)
        jobs_completed = len([j for j in forensic_jobs if j.status == 'completed'])
        jobs_failed = len([j for j in forensic_jobs if j.status == 'failed'])
        
        progress = workspace_schemas.WorkspaceProgress(
            evidence_total=len(evidence_items),
            evidence_with_custody=len([e for e in workspace_evidence if e.custody_entries > 0]),
            evidence_with_documents=len(docs),
            forensic_jobs_total=jobs_total,
            forensic_jobs_completed=jobs_completed,
            forensic_jobs_failed=jobs_failed,
            completion_percent=(jobs_completed / jobs_total * 100) if jobs_total > 0 else 0
        )

        # 8. Risk Indicators (Simple heuristics)
        risks = []
        for e in workspace_evidence:
            if e.custody_entries == 0:
                risks.append(workspace_schemas.WorkspaceRiskIndicator(
                    code="MISSING_CUSTODY",
                    severity="high",
                    message=f"Evidence {e.filename} has no chain of custody entries.",
                    details={"evidence_id": e.id}
                ))
        
        if jobs_failed > 0:
            risks.append(workspace_schemas.WorkspaceRiskIndicator(
                code="PROCESSING_FAILURE",
                severity="medium",
                message=f"{jobs_failed} forensic jobs failed.",
                details={"failed_count": jobs_failed}
            ))

        return workspace_schemas.InvestigationWorkspaceResponse(
            case=case_summary,
            evidence=workspace_evidence,
            custody=workspace_custody,
            timeline=workspace_timeline[:100],
            knowledge_graph=kg_summary,
            ai_findings=ai_findings,
            related_evidence=[], # Placeholder for cross-evidence similarity
            similar_cases=[], # Placeholder for cross-case similarity
            progress=progress,
            risk_indicators=risks,
            court_report=workspace_schemas.CourtReportStatus(
                status="draft",
                completion_percent=progress.completion_percent * 0.8, # Simple heuristic
                blockers=["Missing expert review"] if risks else []
            ),
            generated_at=datetime.now(timezone.utc)
        )

    def _get_kg_summary(self, case_id: str) -> workspace_schemas.WorkspaceKGSummary:
        try:
            client = get_kg_client()
            res_nodes = client.query("MATCH (n)-[:RELATED_TO|MENTIONED_IN|AFFECTS]-(c:Case {id:$cid}) RETURN count(n) as count", {"cid": case_id})
            res_ents = client.query("MATCH (n:Entity)-[:RELATED_TO|MENTIONED_IN]-(c:Case {id:$cid}) RETURN n.name as name, n.type as type LIMIT 10", {"cid": case_id})
            
            return workspace_schemas.WorkspaceKGSummary(
                available=True,
                status="online",
                source="neo4j",
                entity_count=res_nodes[0]['count'] if res_nodes else 0,
                entities=res_ents
            )
        except Exception:
            # Fallback: Query SQLite ForensicResult records for this case's evidence
            try:
                evidence_ids = [
                    e.id for e in self.db.query(models.Evidence.id).filter(models.Evidence.case_id == case_id).all()
                ]
                if not evidence_ids:
                    return workspace_schemas.WorkspaceKGSummary(
                        available=True,
                        status="online_sqlite",
                        source="sqlite",
                        entity_count=0,
                        entities=[]
                    )
                
                results = self.db.query(models.ForensicResult).filter(
                    models.ForensicResult.evidence_id.in_(evidence_ids)
                ).all()

                entities_dict = {}
                for r in results:
                    res_data = r.result or {}
                    if isinstance(res_data, dict):
                        ents = res_data.get('entities') or []
                        if isinstance(ents, list):
                            for ent in ents:
                                if isinstance(ent, dict) and ent.get('name'):
                                    entities_dict[ent['name']] = {
                                        'name': ent['name'],
                                        'type': ent.get('type', 'entity')
                                    }
                
                unique_entities = list(entities_dict.values())
                return workspace_schemas.WorkspaceKGSummary(
                    available=True,
                    status="online_sqlite",
                    source="sqlite",
                    entity_count=len(unique_entities),
                    entities=unique_entities[:20]
                )
            except Exception as fallback_err:
                return workspace_schemas.WorkspaceKGSummary(
                    available=False,
                    status="offline",
                    notes=[str(fallback_err)]
                )
