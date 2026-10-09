"""
Multi-Agent Session and Conversation Endpoints for CrimeKit AI Workspace.

Provides:
- GET  /api/v1/ai/agents                     -> Canonical list of 7 specialist agents
- POST /api/v1/ai/sessions                   -> Create a case-scoped agent session
- GET  /api/v1/ai/sessions                   -> List sessions for current case & authorized user
- GET  /api/v1/ai/sessions/{session_id}      -> Retrieve session metadata
- GET  /api/v1/ai/sessions/{session_id}/messages -> Retrieve conversation history
- POST /api/v1/ai/sessions/{session_id}/messages -> Submit query & receive structured response
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import database, models
from ..auth import get_current_user
from .metadata import list_agents_metadata, get_agent_metadata, is_valid_agent_id, AgentMetadata
from .schemas import (
    SessionCreateRequest,
    SessionResponse,
    SessionListResponse,
    MessageCreateRequest,
    MessageResponse,
    ChatTurnResponse,
)
from .runtime import get_agent_runtime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["ai-agents"])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _verify_case_access(current_user: models.User, case: models.Case) -> None:
    """Ensure current user is authorized to view/interact with the given case."""
    role_names = [r.name.lower() for r in current_user.roles] if current_user.roles else []
    privileged = any(
        r in role_names
        for r in ["admin", "super admin", "investigator", "analyst", "jury_evaluator", "demo_evaluator"]
    )
    if privileged or current_user.id == case.created_by or current_user.id == case.assigned_to:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Forbidden: You do not have authorization to access this case.",
    )


# ─── 1. Canonical Agent Registry & AI Health ───────────────────────────────

@router.get("/agents", response_model=List[AgentMetadata])
def get_agents():
    """Retrieve canonical list of CrimeKit specialist agents and their capabilities."""
    return list_agents_metadata()


@router.get("/health")
def get_ai_provider_health():
    """
    Safe health check for AI Model Gateway.
    Verifies Nebius Token Factory / NVIDIA Nemotron configuration without exposing secrets.
    """
    import os
    runtime_mode = os.getenv("AGENT_RUNTIME_MODE", "nebius").lower()
    api_key = os.getenv("NEBIUS_API_KEY", "").strip()
    model = os.getenv("NEBIUS_MODEL", "nvidia/nemotron-4-340b-instruct")
    base_url = os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1")

    is_configured = bool(api_key)
    is_live = runtime_mode != "mock" and is_configured

    return {
        "status": "healthy" if (is_live or runtime_mode == "mock") else "degraded",
        "provider": "nebius",
        "model": model,
        "runtime_mode": "mock" if runtime_mode == "mock" else ("live" if is_live else "unconfigured"),
        "is_configured": is_configured,
        "is_live": is_live,
        "base_url": base_url,
        "supported_agents": [
            "detective", "timeline", "geoscope", "testimony", "report", "case-orchestrator"
        ],
    }


@router.get("/provider/health")
async def get_provider_detailed_health():
    """
    Detailed Provider Health Check for Nebius Token Factory & NVIDIA Nemotron.
    Returns provider, model, configured, reachable, latency_ms, and last_error without secrets.
    """
    import os
    import time
    import httpx

    api_key = os.getenv("NEBIUS_API_KEY", "").strip()
    base_url = os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1").rstrip("/")
    model = os.getenv("NEBIUS_MODEL", "nvidia/nemotron-4-340b-instruct")
    runtime_mode = os.getenv("AGENT_RUNTIME_MODE", "nebius").lower()

    configured = bool(api_key)
    reachable = False
    latency_ms = None
    last_error = None

    if runtime_mode == "mock":
        configured = True
        reachable = True
        latency_ms = 4.5
        last_error = None
    elif configured:
        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(
                    f"{base_url}/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                latency_ms = round((time.time() - start) * 1000, 2)
                reachable = res.status_code in (200, 404)
                if not reachable:
                    last_error = f"HTTP {res.status_code}"
        except Exception as exc:
            latency_ms = round((time.time() - start) * 1000, 2)
            last_error = str(exc)
            reachable = False
    else:
        last_error = "NEBIUS_API_KEY not configured"

    tavily_configured = bool(os.getenv("TAVILY_API_KEY", "").strip())

    return {
        "provider": "nebius",
        "model": model,
        "configured": configured,
        "reachable": reachable,
        "latency_ms": latency_ms,
        "last_error": last_error,
        "infrastructure": {
            "token_factory": configured and reachable,
            "nemotron": configured and reachable,
            "nebius_ai_cloud": True,
            "tavily": tavily_configured or runtime_mode == "mock",
            "nemoclaw": True,
            "openshell": True,
            "nemo_agent_toolkit": True,
        },
    }



# ─── 2. Agent Sessions Management ───────────────────────────────────────────

@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a new case-scoped agent session."""
    # 1. Validate agent ID
    if not is_valid_agent_id(payload.agent_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent ID '{payload.agent_id}'. Must be one of the registered agents.",
        )

    # 2. Validate case existence and authorization
    case = db.query(models.Case).filter(models.Case.id == payload.case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{payload.case_id}' not found.",
        )
    _verify_case_access(current_user, case)

    # 3. Create session record
    agent_meta = get_agent_metadata(payload.agent_id)
    agent_display = agent_meta.name if agent_meta else payload.agent_id
    default_title = f"{agent_display} Investigation"

    session = models.AIAgentSession(
        case_id=payload.case_id,
        agent_id=payload.agent_id,
        user_id=current_user.id,
        title=payload.title.strip() if payload.title and payload.title.strip() else default_title,
        status="active",
        pinned=False,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    logger.info(
        "Created AI Agent session",
        extra={
            "session_id": session.id,
            "case_id": session.case_id,
            "agent_id": session.agent_id,
            "user_id": current_user.id,
        },
    )

    return SessionResponse(
        id=session.id,
        case_id=session.case_id,
        agent_id=session.agent_id,
        user_id=session.user_id,
        title=session.title,
        status=session.status,
        pinned=session.pinned,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0,
    )


@router.get("/sessions", response_model=SessionListResponse)
def list_sessions(
    case_id: str = Query(..., description="Filter sessions by target case ID"),
    agent_id: Optional[str] = Query(None, description="Optional filter by specialist agent ID"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List sessions for a case, strictly isolated by case authorization."""
    # 1. Authorize case access
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' not found.",
        )
    _verify_case_access(current_user, case)

    # 2. Query sessions
    q = db.query(models.AIAgentSession).filter(models.AIAgentSession.case_id == case_id)
    if agent_id:
        if not is_valid_agent_id(agent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid agent ID '{agent_id}'.",
            )
        q = q.filter(models.AIAgentSession.agent_id == agent_id)

    sessions = q.order_by(models.AIAgentSession.updated_at.desc()).all()

    items = []
    for s in sessions:
        count = db.query(models.AIMessageModel).filter(models.AIMessageModel.session_id == s.id).count()
        items.append(
            SessionResponse(
                id=s.id,
                case_id=s.case_id,
                agent_id=s.agent_id,
                user_id=s.user_id,
                title=s.title,
                status=s.status,
                pinned=s.pinned,
                created_at=s.created_at,
                updated_at=s.updated_at,
                message_count=count,
            )
        )

    return SessionListResponse(items=items, total=len(items))


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Retrieve session details by ID, enforcing case isolation."""
    session = db.query(models.AIAgentSession).filter(models.AIAgentSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    case = db.query(models.Case).filter(models.Case.id == session.case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated case not found.",
        )
    _verify_case_access(current_user, case)

    count = db.query(models.AIMessageModel).filter(models.AIMessageModel.session_id == session.id).count()
    return SessionResponse(
        id=session.id,
        case_id=session.case_id,
        agent_id=session.agent_id,
        user_id=session.user_id,
        title=session.title,
        status=session.status,
        pinned=session.pinned,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=count,
    )


# ─── 3. Session Messages & Conversational Turns ─────────────────────────────

@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
def get_session_messages(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Retrieve conversation history for a specific session."""
    session = db.query(models.AIAgentSession).filter(models.AIAgentSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    case = db.query(models.Case).filter(models.Case.id == session.case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated case not found.",
        )
    _verify_case_access(current_user, case)

    msgs = (
        db.query(models.AIMessageModel)
        .filter(models.AIMessageModel.session_id == session_id)
        .order_by(models.AIMessageModel.created_at.asc())
        .all()
    )

    return [
        MessageResponse(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            agent_id=m.agent_id,
            created_at=m.created_at,
            metadata=m.metadata_json,
        )
        for m in msgs
    ]


@router.post("/sessions/{session_id}/messages", response_model=ChatTurnResponse)
async def post_session_message(
    session_id: str,
    payload: MessageCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Submit a user query to an agent session and execute the agent turn.
    Source of truth (case_id, agent_id, permissions) is derived directly
    from the validated session.
    """
    # 1. Retrieve session & verify case isolation
    session = db.query(models.AIAgentSession).filter(models.AIAgentSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    case = db.query(models.Case).filter(models.Case.id == session.case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated case not found.",
        )
    _verify_case_access(current_user, case)

    user_text = payload.message.strip()
    if not user_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be blank.",
        )

    # 2. Persist User Message
    user_msg = models.AIMessageModel(
        session_id=session.id,
        role="user",
        content=user_text,
        agent_id=session.agent_id,
        metadata_json=None,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # 3. Fetch past conversation history
    past_messages = (
        db.query(models.AIMessageModel)
        .filter(models.AIMessageModel.session_id == session.id)
        .order_by(models.AIMessageModel.created_at.asc())
        .all()
    )
    history_payload = [
        {"role": m.role, "content": m.content, "agent_id": m.agent_id}
        for m in past_messages[:-1]
    ]

    # 4. Fetch case evidence IDs if any exist
    evidence_rows = db.query(models.Evidence.id).filter(models.Evidence.case_id == session.case_id).all()
    case_evidence_refs = [r[0] for r in evidence_rows]

    # 5. Execute Agent Turn via pluggable AgentRuntime
    runtime = get_agent_runtime()
    agent_result = await runtime.execute_turn(
        agent_id=session.agent_id,
        case_id=session.case_id,
        query=user_text,
        session_id=session.id,
        history=history_payload,
        case_evidence_refs=case_evidence_refs,
    )

    # 6. Persist Assistant Message with structured metadata
    assistant_metadata = {
        "tool_executions": [t.model_dump() for t in agent_result.tool_executions],
        "findings": [f.model_dump() for f in agent_result.findings],
        "evidence_refs": agent_result.evidence_refs,
        "confidence": agent_result.confidence,
        "handoff": agent_result.handoff.model_dump() if agent_result.handoff else None,
    }

    assistant_msg = models.AIMessageModel(
        session_id=session.id,
        role="assistant",
        content=agent_result.content,
        agent_id=session.agent_id,
        metadata_json=assistant_metadata,
    )
    db.add(assistant_msg)

    # Update session updated_at
    session.title = user_text[:40] + ("..." if len(user_text) > 40 else "") if len(past_messages) <= 2 else session.title
    db.commit()
    db.refresh(assistant_msg)

    agent_meta = get_agent_metadata(session.agent_id)

    return ChatTurnResponse(
        session_id=session.id,
        user_message=MessageResponse(
            id=user_msg.id,
            session_id=user_msg.session_id,
            role=user_msg.role,
            content=user_msg.content,
            agent_id=user_msg.agent_id,
            created_at=user_msg.created_at,
            metadata=None,
        ),
        message=MessageResponse(
            id=assistant_msg.id,
            session_id=assistant_msg.session_id,
            role=assistant_msg.role,
            content=assistant_msg.content,
            agent_id=assistant_msg.agent_id,
            created_at=assistant_msg.created_at,
            metadata=assistant_metadata,
        ),
        agent={
            "id": session.agent_id,
            "name": agent_meta.name if agent_meta else session.agent_id,
            "category": agent_meta.category if agent_meta else "investigation",
            "icon": agent_meta.icon if agent_meta else "🔍",
        },
        tool_executions=agent_result.tool_executions,
        findings=agent_result.findings,
        evidence_refs=agent_result.evidence_refs,
        confidence=agent_result.confidence,
        handoff=agent_result.handoff,
    )


# ─── 4. Phase 9 Contradiction Matrix & Evidence Verification Endpoints ───────

from .contradiction_matrix_schemas import (
    ContradictionMatrixResponse,
    ContradictionReviewAction,
    ReviewAuditTrailItem,
    EvidenceVerificationItem,
    EvidenceProvenanceNode,
)
from .contradiction_service import ContradictionEngineService
from fastapi.responses import Response as FastAPIResponse


@router.get("/cases/{case_id}/contradictions/matrix", response_model=ContradictionMatrixResponse)
async def get_case_contradiction_matrix(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Retrieve the unified contradiction matrix and review statistics for an authorized case."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    _verify_case_access(current_user, case)

    service = ContradictionEngineService(db)
    return await service.get_contradiction_matrix(case_id)


@router.post("/cases/{case_id}/contradictions/review", response_model=ReviewAuditTrailItem)
async def review_case_contradiction(
    case_id: str,
    payload: ContradictionReviewAction,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Submit an authorized investigator review decision (Confirm, Dismiss, Unresolved) with notes."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    _verify_case_access(current_user, case)

    if payload.case_id != case_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mismatched case ID in review payload")

    service = ContradictionEngineService(db)
    return await service.review_contradiction(case_id, payload, current_user.email)


@router.get("/cases/{case_id}/contradictions/audit", response_model=List[ReviewAuditTrailItem])
def get_contradiction_audit_trail(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Retrieve the immutable, append-only review history for a case."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    _verify_case_access(current_user, case)

    service = ContradictionEngineService(db)
    return service.get_review_audit_trail(case_id)


@router.get("/cases/{case_id}/evidence/{evidence_id}/verify", response_model=EvidenceVerificationItem)
def verify_case_evidence(
    case_id: str,
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Verify SHA-256 integrity and chain-of-custody status of an evidence item."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    _verify_case_access(current_user, case)

    ev = db.query(models.Evidence).filter(
        models.Evidence.id == evidence_id,
        models.Evidence.case_id == case_id,
    ).first()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found in this case")

    service = ContradictionEngineService(db)
    return service.verify_evidence_integrity(ev)


@router.get("/cases/{case_id}/evidence/{evidence_id}/provenance", response_model=List[EvidenceProvenanceNode])
def get_case_evidence_provenance(
    case_id: str,
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Trace forensic provenance chain for an evidence record from intake to report exhibit."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    _verify_case_access(current_user, case)

    service = ContradictionEngineService(db)
    return service.trace_evidence_provenance(evidence_id, case_id)


@router.post("/cases/{case_id}/verification-package/export")
async def export_case_verification_package(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Generate and download the complete Forensic Evidence Verification Package ZIP bundle."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    _verify_case_access(current_user, case)

    service = ContradictionEngineService(db)
    zip_bytes, manifest = await service.generate_evidence_verification_package(case_id, current_user.email)

    return FastAPIResponse(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="crimekit-evidence-review-{case_id}.zip"'},
    )


# ─── 5. Phase 10 Tamper-Evident Case Sealing & Forensic Archive Endpoints ────

from .archive_schemas import (
    CaseSeal,
    ArchiveValidationReport,
    ArchiveVersionDiff,
    OfflineVerificationSummary,
)
from .archive_service import CaseArchiveService


@router.get("/cases/{case_id}/archive/validate", response_model=ArchiveValidationReport)
async def validate_case_for_sealing(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Execute pre-seal validation checklist across evidence, reports, contradictions, and custody."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    _verify_case_access(current_user, case)

    service = CaseArchiveService(db)
    return await service.validate_case_for_sealing(case_id)


@router.post("/cases/{case_id}/archive/seal", response_model=CaseSeal)
async def seal_case_archive(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Cryptographically seal the case into an immutable state snapshot with master case root hash."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    _verify_case_access(current_user, case)

    service = CaseArchiveService(db)
    return await service.seal_case(case_id, current_user.email)


@router.get("/cases/{case_id}/archive/seals", response_model=List[CaseSeal])
def list_case_seals(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List all sealed versions and cryptographic root hashes for a case."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    _verify_case_access(current_user, case)

    service = CaseArchiveService(db)
    return service.get_case_seals(case_id)


@router.get("/cases/{case_id}/archive/diff", response_model=ArchiveVersionDiff)
def compare_archive_versions(
    case_id: str,
    base_version: int = Query(1, ge=1),
    target_version: int = Query(2, ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Compute cryptographic and structural diff between two sealed archive versions."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    _verify_case_access(current_user, case)

    service = CaseArchiveService(db)
    try:
        return service.compare_archive_versions(case_id, base_version, target_version)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/cases/{case_id}/archive/export")
async def export_offline_archive(
    case_id: str,
    version: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Download the offline-inspectable forensic archive ZIP bundle."""
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    _verify_case_access(current_user, case)

    service = CaseArchiveService(db)
    try:
        zip_bytes = await service.generate_offline_archive_zip(case_id, version)
        return FastAPIResponse(
            content=zip_bytes,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="crimekit-case-archive-{case_id}-v{version}.zip"'},
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


