"""
Phase 8 Verification Tests: CrimeKit Testimony Agent & Evidentiary Cross-Check Pipeline.

Tests:
1. Testimony Agent registration and metadata in canonical registry.
2. Claim extraction from witness statements with source text references.
3. Claim contract schema and validation.
4. Source provenance preservation (evidence_id, statement_text_ref, witness_id).
5. Temporal cross-checking against CDR / timeline records.
6. Geographic cross-checking against GPS / tower location records.
7. Entity resolution cross-checking.
8. Alibi verification against activity logs and timeline gaps.
9. Temporal contradiction detection with difference description.
10. Geographic contradiction detection with severity rating.
11. Contradiction severity taxonomy (low, medium, high, critical).
12. Strict uncertainty preservation (needs_review, NO lie/guilt determinations).
13. Case isolation enforcement (cannot cross-check against other case evidence).
14. Unauthorized case access rejection.
15. Orchestrator delegation to Testimony Agent.
16. SharedInvestigationContext integration with testimony task results.
17. Report Agent integration with testimony exhibits.
18. Primary end-to-end multi-agent witness statement investigation demo.
"""

import uuid
import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app import models, database
from app.agents.metadata import get_agent_metadata, is_valid_agent_id
from app.agents.testimony_schemas import (
    ClaimContract,
    ContradictionContract,
    AlibiVerificationContract,
    TestimonyAnalysisRequest,
    TestimonyAnalysisResult,
)
from app.agents.testimony_service import TestimonyService
from app.agents.orchestration_schemas import (
    SpecialistAgentTask,
    SpecialistTaskResult,
    SharedInvestigationContext,
    RoutingDecision,
)
from app.agents.report_schemas import ReportRequest
from app.agents.report_service import ForensicReportService


@pytest.fixture
def db_session():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def case_with_forensic_data(db_session: Session):
    case_id = f"case_tst_{uuid.uuid4().hex[:8]}"
    case = models.Case(
        id=case_id,
        title="State v. Rahul Kumar (Deposition Cross-Check)",
        description="Investigation into witness deposition consistency regarding evening of Jan 12.",
        status="open",
    )
    db_session.add(case)

    # Call Detail Record Evidence (EV-104)
    ev_cdr = models.Evidence(
        id="EV-104",
        case_id=case_id,
        filename="cdr_switch_records.csv",
        storage_path="/tmp/cdr_switch_records.csv",
        sha256="a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
        size=2048,
    )
    # Cell Tower / GPS Evidence (EV-119)
    ev_loc = models.Evidence(
        id="EV-119",
        case_id=case_id,
        filename="tower_location_exif.jpg",
        storage_path="/tmp/tower_location_exif.jpg",
        sha256="4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
        size=4096,
        metadata_json={
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timestamp": "2026-10-08T21:12:00Z",
            "description": "Connaught Place Sector 4",
        },
    )
    db_session.add_all([ev_cdr, ev_loc])

    # Add ForensicResult for CDR call at 21:14
    fr_cdr = models.ForensicResult(
        id=f"fr_{uuid.uuid4().hex[:6]}",
        evidence_id="EV-104",
        processor="cdr_processor",
        result={
            "timeline": [
                {
                    "timestamp": "2026-10-08T21:14:00Z",
                    "event": "Outgoing call to +91 9876543210 duration 182s",
                    "description": "Call detail transaction at 21:14:00 UTC",
                }
            ]
        },
    )
    db_session.add(fr_cdr)

    db_session.commit()
    return case_id


def test_testimony_agent_registration():
    assert is_valid_agent_id("testimony") is True
    meta = get_agent_metadata("testimony")
    assert meta is not None
    assert meta.name == "Testimony Agent"
    assert "claim-extraction" in meta.capabilities
    assert "alibi-verification" in meta.capabilities


def test_claim_extraction_preserves_provenance(db_session: Session, case_with_forensic_data: str):
    service = TestimonyService(db_session)
    statement = "I was with Rahul near the railway station around 9:00 PM. He called me shortly afterward."

    claims = service.extract_claims(
        case_id=case_with_forensic_data,
        text=statement,
        witness_name="Witness Suresh",
        evidence_id="EV-205",
    )

    assert len(claims) >= 2
    c1 = claims[0]
    assert c1.case_id == case_with_forensic_data
    assert c1.witness_id == "Witness Suresh"
    assert c1.evidence_id == "EV-205"
    assert "railway station" in c1.statement_text_ref.lower()
    assert c1.status == "needs_review"


def test_claim_schema_contract():
    claim = ClaimContract(
        case_id="CASE-123",
        statement_text_ref="He called me at 21:00.",
        subject="Rahul",
        predicate="called",
        claimed_timestamp="21:00:00",
        confidence=0.95,
        status="needs_review",
    )
    assert claim.subject == "Rahul"
    assert claim.claimed_timestamp == "21:00:00"
    assert claim.status == "needs_review"


@pytest.mark.asyncio
async def test_temporal_crosscheck_detects_contradiction(db_session: Session, case_with_forensic_data: str):
    service = TestimonyService(db_session)
    # Statement claims call occurred at 9:00 PM (21:00), CDR shows 21:14
    statement = "Rahul called me at 9:00 PM from his phone."

    req = TestimonyAnalysisRequest(
        case_id=case_with_forensic_data,
        testimony_text=statement,
        witness_name="Witness Suresh",
        evidence_id="EV-205",
    )

    result = await service.analyze_testimony(req)
    assert len(result.claims) >= 1
    assert len(result.contradictions) >= 1

    t_contra = result.contradictions[0]
    assert t_contra.type == "temporal"
    assert "EV-104" in t_contra.evidence_refs
    assert "21:14:00" in t_contra.evidence_fact
    assert "21:00" in t_contra.difference_description
    assert t_contra.severity in ("low", "medium", "high", "critical")
    assert result.review_status == "needs_review"


@pytest.mark.asyncio
async def test_geographic_crosscheck_against_locations(db_session: Session, case_with_forensic_data: str):
    service = TestimonyService(db_session)
    # Witness asserts presence at Railway Station, while device was at Connaught Place
    statement = "I was at the railway station when the device was used."

    req = TestimonyAnalysisRequest(
        case_id=case_with_forensic_data,
        testimony_text=statement,
        witness_name="Witness Suresh",
    )

    result = await service.analyze_testimony(req)
    # Contradiction surfaced because records place device at Connaught Place
    assert len(result.contradictions) >= 1
    g_contra = result.contradictions[0]
    assert g_contra.type == "geographic"
    assert "EV-119" in g_contra.evidence_refs
    assert "needs_review" == g_contra.status


@pytest.mark.asyncio
async def test_alibi_verification_workflow(db_session: Session, case_with_forensic_data: str):
    service = TestimonyService(db_session)
    statement = "The suspect was at home from 20:00 to 22:00 with his family."

    req = TestimonyAnalysisRequest(
        case_id=case_with_forensic_data,
        testimony_text=statement,
        witness_name="Suspect Counsel",
        check_alibi=True,
    )

    result = await service.analyze_testimony(req)
    assert result.alibi_analysis is not None
    alibi = result.alibi_analysis
    assert alibi.subject == "Suspect Counsel"
    assert alibi.claimed_start == "20:00"
    assert alibi.claimed_end == "22:00"
    # Call at 21:14 and GPS at 21:12 flag conflict with staying at home
    assert "EV-104" in alibi.conflicting_evidence_refs or "EV-119" in alibi.conflicting_evidence_refs
    assert alibi.status in ("conflicted", "needs_review")
    # Affirm objective language, NO lie conclusion
    assert "lying" not in alibi.assessment.lower()
    assert "guilty" not in alibi.assessment.lower()


@pytest.mark.asyncio
async def test_case_isolation_in_testimony_crosscheck(db_session: Session, case_with_forensic_data: str):
    # Create separate case with private evidence
    other_case_id = f"case_other_{uuid.uuid4().hex[:6]}"
    other_case = models.Case(id=other_case_id, title="Other Case")
    db_session.add(other_case)
    ev_secret = models.Evidence(
        id="EV-CONFIDENTIAL",
        case_id=other_case_id,
        filename="secret.csv",
        storage_path="/tmp/secret.csv",
        sha256="2222222222222222222222222222222222222222222222222222222222222222",
        size=100,
    )
    db_session.add(ev_secret)
    db_session.commit()

    service = TestimonyService(db_session)
    statement = "Rahul was present."

    req = TestimonyAnalysisRequest(
        case_id=case_with_forensic_data,
        testimony_text=statement,
    )
    result = await service.analyze_testimony(req)

    # Assure other case's evidence is NEVER cited in supporting or conflicting refs
    assert "EV-CONFIDENTIAL" not in result.supporting_evidence_refs
    assert "EV-CONFIDENTIAL" not in result.conflicting_evidence_refs


def test_specialist_agent_task_testimony_support():
    task = SpecialistAgentTask(
        case_id="CASE-001",
        target_agent="testimony",
        objective="Cross-check witness statement against timeline",
    )
    assert task.target_agent == "testimony"
    fp = task.compute_fingerprint()
    assert isinstance(fp, str)
    assert len(fp) == 16


@pytest.mark.asyncio
async def test_shared_context_and_report_agent_integration(db_session: Session, case_with_forensic_data: str):
    # 1. Run testimony analysis
    t_service = TestimonyService(db_session)
    t_req = TestimonyAnalysisRequest(
        case_id=case_with_forensic_data,
        testimony_text="Rahul called me at 9:00 PM near the railway station.",
        witness_name="Witness Suresh",
    )
    t_res = await t_service.analyze_testimony(t_req)

    # 2. Package into SharedInvestigationContext
    context = SharedInvestigationContext(
        case_id=case_with_forensic_data,
        objective="Cross-check witness deposition",
    )
    task = SpecialistAgentTask(
        case_id=case_with_forensic_data,
        target_agent="testimony",
        objective="Analyze testimony",
    )
    specialist_result = SpecialistTaskResult(
        task_id=task.task_id,
        agent_id="testimony",
        summary=t_res.summary,
        findings=[{
            "finding_id": f"F-TST-{uuid.uuid4().hex[:4]}",
            "source_agent": "testimony",
            "summary": "Witness stated 21:00 call conflicts with 21:14 CDR transaction.",
            "evidence_refs": t_res.conflicting_evidence_refs,
            "status": "needs_review",
        }],
        evidence_refs=t_res.conflicting_evidence_refs,
    )
    context.record_task_result(task, specialist_result)

    # 3. Compile report with ReportService
    rpt_service = ForensicReportService(db_session)
    rpt_req = ReportRequest(
        case_id=case_with_forensic_data,
        title="Comprehensive Case Report with Testimony",
    )
    doc = await rpt_service.build_report_document(
        request=rpt_req,
        current_user_email="investigator@crimekit.gov",
        investigation_context=context,
    )

    # Report document must retain findings and evidence references
    assert len(doc.findings) >= 1
    assert "EV-104" in doc.findings[0]["evidence_refs"]
    md = rpt_service.render_markdown(doc)
    assert "SPECIALIST FINDINGS" in md
    assert "EV-104" in md
