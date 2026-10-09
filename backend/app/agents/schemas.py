"""
Pydantic contracts for Multi-Agent AI Sessions, Messages, Tools, and Findings.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ─── Tool Executions ────────────────────────────────────────────────────────

class ToolExecutionContract(BaseModel):
    id: str = Field(..., description="Unique tool execution run ID")
    tool_name: str = Field(..., description="Programmatic tool identifier")
    display_name: str = Field(..., description="Human-readable tool title")
    status: str = Field(..., description="pending | running | completed | failed")
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    output_snippet: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# ─── Findings ───────────────────────────────────────────────────────────────

class FindingContract(BaseModel):
    id: str = Field(..., description="Unique finding ID")
    title: str = Field(..., description="Summary headline")
    description: str = Field(..., description="Analytical description")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    status: str = Field(
        ...,
        description="supported | contradicted | needs_review | insufficient_evidence",
    )
    agent_id: str = Field(..., description="Agent author ID")
    evidence_refs: List[str] = Field(default_factory=list, description="Referenced evidence IDs")
    subgraph_nodes: Optional[List[str]] = None


# ─── Agent Handoff ──────────────────────────────────────────────────────────

class AgentHandoffContract(BaseModel):
    source_agent: str = Field(..., description="Agent initiating handoff")
    target_agent: str = Field(..., description="Recommended specialist agent ID")
    reason: str = Field(..., description="Analytical rationale for delegation")
    context_summary: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


# ─── Sessions ───────────────────────────────────────────────────────────────

class SessionCreateRequest(BaseModel):
    case_id: str = Field(..., description="Target Case ID")
    agent_id: str = Field(..., description="Specialist Agent ID")
    title: Optional[str] = Field(None, description="Optional custom session title")


class SessionResponse(BaseModel):
    id: str
    case_id: str
    agent_id: str
    user_id: Optional[str] = None
    title: str
    status: str
    pinned: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    message_count: int = 0


class SessionListResponse(BaseModel):
    items: List[SessionResponse]
    total: int


# ─── Messages ──────────────────────────────────────────────────────────────

class MessageCreateRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Investigator query content")


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str  # user | assistant | system | tool
    content: str
    agent_id: Optional[str] = None
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatTurnResponse(BaseModel):
    session_id: str
    user_message: MessageResponse
    message: MessageResponse
    agent: Dict[str, Any]
    tool_executions: List[ToolExecutionContract] = Field(default_factory=list)
    findings: List[FindingContract] = Field(default_factory=list)
    evidence_refs: List[str] = Field(default_factory=list)
    confidence: Optional[float] = None
    handoff: Optional[AgentHandoffContract] = None
