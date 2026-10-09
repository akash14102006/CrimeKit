"""
Orchestration contracts for CrimeKit Multi-Agent Investigation Architecture.

Defines:
- SpecialistAgentTask: Structured task delegated by Orchestrator to a specialist.
- SpecialistTaskResult: Normalized analytical result returned by specialist to Orchestrator.
- SharedInvestigationContext: Bounded context tracking case objectives, references, and completed tasks.
- RoutingDecision: Structured routing decision produced by Orchestrator (delegate vs finalize).
- ContradictionItem: Explicitly flagged conflict between specialist findings (e.g. timestamp gaps).
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
import uuid
import time
import hashlib


class SpecialistAgentTask(BaseModel):
    task_id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}")
    case_id: str = Field(..., description="Authoritative case identifier")
    source_agent: str = Field(default="case-orchestrator")
    target_agent: Literal["detective", "timeline", "geoscope", "testimony"] = Field(
        ..., description="Designated specialist agent"
    )
    objective: str = Field(..., min_length=3, description="Specific investigative sub-goal")
    context_refs: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "entity_ids": [],
            "evidence_ids": [],
            "event_ids": [],
            "location_ids": [],
        },
        description="Selective ID references passed to specialist without dumping raw data",
    )
    constraints: Dict[str, Any] = Field(
        default_factory=lambda: {
            "max_tool_rounds": 4,
            "max_results": 20,
        }
    )
    created_at: float = Field(default_factory=time.time)

    def compute_fingerprint(self) -> str:
        """Deterministic fingerprint for duplicate task prevention."""
        raw = f"{self.target_agent}:{self.objective.strip().lower()}:{sorted(self.context_refs.get('evidence_ids', []))}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


class SpecialistTaskResult(BaseModel):
    task_id: str
    agent_id: str
    status: Literal["completed", "failed", "duplicate_skipped"] = "completed"
    summary: str
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_refs: List[str] = Field(default_factory=list)
    tool_executions: List[Dict[str, Any]] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)
    duration_ms: float = 0.0
    error_message: Optional[str] = None


class ContradictionItem(BaseModel):
    id: str = Field(default_factory=lambda: f"contra_{uuid.uuid4().hex[:6]}")
    type: Literal["timestamp_gap", "location_discrepancy", "entity_mismatch", "conflicting_claim", "testimony_discrepancy"]
    sources: List[str] = Field(default_factory=list, description="Evidence IDs or finding IDs in conflict")
    description: str
    status: Literal["needs_review", "verified_conflict", "resolved"] = "needs_review"


class SharedInvestigationContext(BaseModel):
    case_id: str
    objective: str
    entities: List[str] = Field(default_factory=list)
    evidence_refs: List[str] = Field(default_factory=list)
    event_ids: List[str] = Field(default_factory=list)
    location_ids: List[str] = Field(default_factory=list)
    completed_task_fingerprints: List[str] = Field(default_factory=list)
    task_results: List[SpecialistTaskResult] = Field(default_factory=list)
    contradictions: List[ContradictionItem] = Field(default_factory=list)

    def is_task_duplicate(self, task: SpecialistAgentTask) -> bool:
        return task.compute_fingerprint() in self.completed_task_fingerprints

    def record_task_result(self, task: SpecialistAgentTask, result: SpecialistTaskResult):
        self.completed_task_fingerprints.append(task.compute_fingerprint())
        self.task_results.append(result)
        for ref in result.evidence_refs:
            if ref and ref not in self.evidence_refs:
                self.evidence_refs.append(ref)


class RoutingDecision(BaseModel):
    action: Literal["delegate", "finalize", "request_more"]
    target_agent: Optional[Literal["detective", "timeline", "geoscope", "testimony"]] = None
    objective: Optional[str] = None
    reason: str
    context_evidence_refs: List[str] = Field(default_factory=list)
    identified_contradiction: Optional[ContradictionItem] = None
