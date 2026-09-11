from datetime import datetime
from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, Field


class WorkspaceCaseSummary(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None


class WorkspaceEvidenceItem(BaseModel):
    id: str
    filename: str
    sha256: str
    size: int
    mime_type: Optional[str] = None
    uploaded_by: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    custody_entries: int = 0
    has_document: bool = False
    ai_score: Optional[float] = None


class WorkspaceCustodyEvent(BaseModel):
    id: str
    evidence_id: str
    action: str
    actor_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    notes: Optional[str] = None


class WorkspaceTimelineEvent(BaseModel):
    source_type: str
    source_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    date: Optional[str] = None
    summary: str


class WorkspaceKGSummary(BaseModel):
    available: bool
    status: str
    source: str = "local"
    entity_count: int = 0
    relationship_count: int = 0
    timeline_event_count: int = 0
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    timeline_events: List[Dict[str, Any]] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class WorkspaceAIFinding(BaseModel):
    document_id: str
    evidence_id: Optional[str] = None
    score: float
    snippet: Optional[str] = None


class WorkspaceRelatedEvidence(BaseModel):
    evidence_id: str
    related_evidence_id: str
    similarity: float
    reason: str


class WorkspaceSimilarCase(BaseModel):
    case_id: str
    title: str
    similarity: float
    reason: str


class WorkspaceProgress(BaseModel):
    evidence_total: int
    evidence_with_custody: int
    evidence_with_documents: int
    forensic_jobs_total: int
    forensic_jobs_completed: int
    forensic_jobs_failed: int
    completion_percent: float


class WorkspaceRiskIndicator(BaseModel):
    code: str
    severity: Literal['low', 'medium', 'high']
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class CourtReportStatus(BaseModel):
    status: Literal['draft', 'review', 'ready', 'blocked']
    completion_percent: float
    blockers: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class InvestigationWorkspaceResponse(BaseModel):
    case: WorkspaceCaseSummary
    evidence: List[WorkspaceEvidenceItem]
    custody: List[WorkspaceCustodyEvent]
    timeline: List[WorkspaceTimelineEvent]
    knowledge_graph: WorkspaceKGSummary
    ai_findings: List[WorkspaceAIFinding]
    related_evidence: List[WorkspaceRelatedEvidence]
    similar_cases: List[WorkspaceSimilarCase]
    progress: WorkspaceProgress
    risk_indicators: List[WorkspaceRiskIndicator]
    court_report: CourtReportStatus
    generated_at: datetime
