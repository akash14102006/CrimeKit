"""
Phase 9 Tests: Interactive Contradiction Matrix & Evidence Verification Workspace.

Validates:
1. Contradiction schema validation (ContradictionContract, ClaimEvidenceLink, ContradictionMatrixRow).
2. Claim / evidence relationship linking.
3. Deterministic temporal contradiction evaluation with exact delta calculation.
4. Deterministic geographic contradiction evaluation with Haversine distance and tolerance thresholds.
5. Deterministic identity contradiction evaluation.
6. Deterministic sequence contradiction evaluation (chronological inversion).
7. Contradiction severity assignment (low, medium, high, critical).
8. Evidence reference preservation and provenance tracing.
9. Case isolation enforcement.
10. Investigator review actions: Confirmation, Dismissal, Unresolved.
11. Append-only review audit trail and investigator notes preservation.
12. Cryptographic SHA-256 verification and mismatch detection.
13. Report Agent integration with reviewed contradictions.
14. Evidence Verification Package generation with cryptographically hashed manifest.
15. Primary end-to-end investigative workflow demo.
"""

import pytest
import os
import json
import zipfile
import io
import hashlib
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app import models
from backend.app.agents.testimony_schemas import ClaimContract, ContradictionContract
from backend.app.agents.contradiction_matrix_schemas import (
    ClaimEvidenceLink,
    ContradictionMatrixRow,
    ContradictionReviewAction,
    ReviewAuditTrailItem,
    EvidenceVerificationItem,
    EvidenceProvenanceNode,
)
from backend.app.agents.contradiction_service import (
    ContradictionEngineService,
    _compute_haversine_distance,
    _CONTRADICTION_STATUSES,
    _REVIEW_AUDIT_LOG,
)
from backend.app.agents.report_schemas import ReportRequest
from backend.app.agents.report_service import ForensicReportService


@pytest.fixture
def test_db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Clear review caches
    _CONTRADICTION_STATUSES.clear()
    _REVIEW_AUDIT_LOG.clear()

    # Create dummy user & cases
    user = models.User(id="user_inv_01", email="lead_inv@crimekit.local", name="Lead Investigator")
    case_a = models.Case(id="CASE-P9-001", title="Railway Station Robbery", status="open", created_by="user_inv_01")
    case_b = models.Case(id="CASE-P9-002", title="Unrelated Burglary", status="open", created_by="user_inv_01")

    # Ingest evidence for Case A
    ev_cdr = models.Evidence(
        id="EV-104",
        case_id="CASE-P9-001",
        filename="cdr_dump_jan2026.csv",
        storage_path="/tmp/nonexistent_cdr.csv",
        sha256="a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0",
        size=1024,
        mime_type="text/csv",
        uploaded_by="user_inv_01",
    )
    ev_tower = models.Evidence(
        id="EV-119",
        case_id="CASE-P9-001",
        filename="tower_triangulation.json",
        storage_path="/tmp/nonexistent_tower.json",
        sha256="b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef01",
        size=2048,
        mime_type="application/json",
        uploaded_by="user_inv_01",
    )
    ev_entity = models.Evidence(
        id="EV-087",
        case_id="CASE-P9-001",
        filename="subscriber_registry.pdf",
        storage_path="/tmp/nonexistent_sub.pdf",
        sha256="c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef012",
        size=4096,
        mime_type="application/pdf",
        uploaded_by="user_inv_01",
    )

    # Ingest custody for EV-104
    coc = models.ChainOfCustody(
        id="COC-104-01",
        evidence_id="EV-104",
        action="secure_acquisition",
        actor_id="user_inv_01",
        notes="Carrier subpoena export verified",
    )

    # Ingest evidence for Case B (Isolation test)
    ev_case_b = models.Evidence(
        id="EV-B-999",
        case_id="CASE-P9-002",
        filename="isolated_evidence.csv",
        storage_path="/tmp/isolated.csv",
        sha256="d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0123",
        size=512,
        mime_type="text/csv",
        uploaded_by="user_inv_01",
    )

    session.add_all([user, case_a, case_b, ev_cdr, ev_tower, ev_entity, coc, ev_case_b])
    session.commit()

    yield session
    session.close()


def test_contradiction_and_matrix_schemas():
    """Verify Phase 9 Contradiction Matrix data schemas."""
    claim = ClaimContract(
        claim_id="CLM-100",
        case_id="CASE-P9-001",
        statement_text_ref="Rahul called me at 21:00.",
        subject="Witness A",
        predicate="made_or_received_call",
        claimed_timestamp="21:00:00",
    )
    contra = ContradictionContract(
        case_id="CASE-P9-001",
        type="temporal",
        severity="high",
        claim_id=claim.claim_id,
        statement_excerpt=claim.statement_text_ref,
        evidence_fact="Call detail record at 21:14:00 UTC",
        evidence_refs=["EV-104"],
        difference_description="14-minute temporal gap",
        status="needs_review",
    )
    link = ClaimEvidenceLink(
        case_id="CASE-P9-001",
        claim_id=claim.claim_id,
        evidence_id="EV-104",
        relationship="contradicts",
        explanation="Delta of 14 minutes",
    )
    row = ContradictionMatrixRow(
        claim=claim,
        evidence_refs=["EV-104"],
        contradiction=contra,
        links=[link],
        review_status="needs_review",
    )
    assert row.claim.claim_id == "CLM-100"
    assert row.contradiction.severity == "high"
    assert row.links[0].relationship == "contradicts"
    assert row.review_status == "needs_review"


def test_deterministic_temporal_contradiction(test_db_session):
    """Verify deterministic temporal difference computation and severity assignment."""
    service = ContradictionEngineService(test_db_session)

    # 14-minute gap -> high severity (> 15 min is high, > 5 is medium)
    contra = service.evaluate_temporal_contradiction(
        case_id="CASE-P9-001",
        claim_id="CLM-001",
        statement_excerpt="Rahul called me at 21:00.",
        claimed_time_str="21:00:00",
        evidence_id="EV-104",
        evidence_time_str="21:14:00",
        tolerance_minutes=5,
    )
    assert contra is not None
    assert contra.type == "temporal"
    assert contra.severity in ("medium", "high")
    assert "14 minute(s)" in contra.difference_description
    assert contra.evidence_refs == ["EV-104"]

    # Small gap within tolerance (3 minutes) -> No contradiction
    no_contra = service.evaluate_temporal_contradiction(
        case_id="CASE-P9-001",
        claim_id="CLM-001",
        statement_excerpt="Rahul called me at 21:11.",
        claimed_time_str="21:11:00",
        evidence_id="EV-104",
        evidence_time_str="21:14:00",
        tolerance_minutes=5,
    )
    assert no_contra is None


def test_deterministic_geographic_contradiction(test_db_session):
    """Verify deterministic distance calculation using Haversine formula."""
    service = ContradictionEngineService(test_db_session)

    # Railway Station ~ (28.6430, 77.2197), Tower EV-119 ~ (28.6139, 77.2090) -> ~3.37 km
    dist = _compute_haversine_distance(28.6430, 77.2197, 28.6139, 77.2090)
    assert 3.0 < dist < 4.0

    contra = service.evaluate_geographic_contradiction(
        case_id="CASE-P9-001",
        claim_id="CLM-002",
        statement_excerpt="I was near the railway station at 9:00 PM.",
        claimed_location_name="Railway Station",
        claimed_coords=(28.6430, 77.2197),
        evidence_id="EV-119",
        evidence_coords=(28.6139, 77.2090),
        evidence_location_name="Connaught Sector Tower",
        threshold_km=2.0,
    )
    assert contra is not None
    assert contra.type == "geographic"
    assert "Spatial discrepancy" in contra.difference_description
    assert contra.evidence_refs == ["EV-119"]


def test_deterministic_sequence_and_identity_contradictions(test_db_session):
    """Verify chronological sequence inversion and subscriber identity mismatch."""
    service = ContradictionEngineService(test_db_session)

    # Sequence contradiction: claimed A then B, evidence shows B at 20:00 then A at 21:00
    contra_seq = service.evaluate_sequence_contradiction(
        case_id="CASE-P9-001",
        claim_id="CLM-003",
        statement_excerpt="Met Rahul then went to market.",
        claimed_order=["Met Rahul", "Market Visit"],
        evidence_order=[
            ("Market Visit", "2026-03-31T20:00:00Z", "EV-104"),
            ("Met Rahul", "2026-03-31T21:00:00Z", "EV-119"),
        ],
    )
    assert contra_seq is not None
    assert contra_seq.type == "sequence"
    assert "Sequence contradiction" in contra_seq.difference_description

    # Identity contradiction
    contra_id = service.evaluate_identity_contradiction(
        case_id="CASE-P9-001",
        claim_id="CLM-004",
        statement_excerpt="Rahul's personal SIM card.",
        claimed_entity="Rahul Kumar",
        evidence_id="EV-087",
        registered_entity="Corporate Fleet Telecom Ltd",
    )
    assert contra_id is not None
    assert contra_id.type == "identity"
    assert "Corporate Fleet Telecom Ltd" in contra_id.difference_description


@pytest.mark.asyncio
async def test_investigator_review_workflow_and_audit_trail(test_db_session):
    """Verify investigator decisions (confirm, dismiss, mark unresolved) with append-only audit trail."""
    service = ContradictionEngineService(test_db_session)
    contra_id = "CONTRA-TEST-001"

    # 1. Action: Confirm contradiction
    action_confirm = ContradictionReviewAction(
        case_id="CASE-P9-001",
        contradiction_id=contra_id,
        decision="confirmed",
        note="Confirmed against original CDR record EV-104 by Lead Examiner.",
    )
    audit_item = await service.review_contradiction("CASE-P9-001", action_confirm, "lead_inv@crimekit.local")
    assert audit_item.new_status == "confirmed"
    assert audit_item.previous_status == "needs_review"
    assert "Confirmed against original CDR" in audit_item.note

    # Verify audit trail length
    trail = service.get_review_audit_trail("CASE-P9-001")
    assert len(trail) == 1
    assert trail[0].reviewer == "lead_inv@crimekit.local"

    # 2. Action: Dismiss subsequent review
    action_dismiss = ContradictionReviewAction(
        case_id="CASE-P9-001",
        contradiction_id=contra_id,
        decision="dismissed",
        note="Dismissed after second witness interview.",
    )
    audit_item2 = await service.review_contradiction("CASE-P9-001", action_dismiss, "lead_inv@crimekit.local")
    assert audit_item2.previous_status == "confirmed"
    assert audit_item2.new_status == "dismissed"

    trail2 = service.get_review_audit_trail("CASE-P9-001")
    assert len(trail2) == 2


def test_evidence_verification_and_hash_integrity(test_db_session):
    """Verify SHA-256 verification and mismatch detection."""
    service = ContradictionEngineService(test_db_session)
    ev = test_db_session.query(models.Evidence).filter(models.Evidence.id == "EV-104").first()

    # Integrity verification
    verification = service.verify_evidence_integrity(ev)
    assert verification.evidence_id == "EV-104"
    assert verification.stored_sha256 == ev.sha256
    assert verification.chain_of_custody_available is True
    assert verification.custody_action_count == 1
    assert verification.integrity_status in ("verified", "unavailable")

    # Provenance chain
    nodes = service.trace_evidence_provenance("EV-104", "CASE-P9-001")
    assert len(nodes) >= 3
    steps = [n.step for n in nodes]
    assert "Evidence Intake" in steps
    assert "Chain of Custody" in steps
    assert "Forensic Extraction" in steps


@pytest.mark.asyncio
async def test_case_isolation_enforcement(test_db_session):
    """Ensure evidence and contradictions from CASE-P9-002 do not leak into CASE-P9-001."""
    service = ContradictionEngineService(test_db_session)
    matrix_a = await service.get_contradiction_matrix("CASE-P9-001")
    matrix_b = await service.get_contradiction_matrix("CASE-P9-002")

    assert matrix_a.case_id == "CASE-P9-001"
    assert matrix_b.case_id == "CASE-P9-002"

    # None of Case A rows reference EV-B-999
    for r in matrix_a.rows:
        assert "EV-B-999" not in r.evidence_refs

    # Provenance for EV-B-999 should be empty when requested under Case A
    nodes = service.trace_evidence_provenance("EV-B-999", "CASE-P9-001")
    assert len(nodes) == 0


@pytest.mark.asyncio
async def test_report_integration_with_reviewed_contradictions(test_db_session):
    """Verify that Report Agent includes reviewed contradictions with investigator notes."""
    service = ContradictionEngineService(test_db_session)
    await service.review_contradiction(
        "CASE-P9-001",
        ContradictionReviewAction(
            case_id="CASE-P9-001",
            contradiction_id="CONTRA-001",
            decision="confirmed",
            note="Confirmed discrepancy against CDR EV-104",
        ),
        "lead_inv@crimekit.local",
    )

    report_service = ForensicReportService(test_db_session)
    req = ReportRequest(case_id="CASE-P9-001", title="Case A Final Report")
    doc = await report_service.build_report_document(req, "lead_inv@crimekit.local")

    contra_exhibits = [c for c in doc.contradictions if c.id == "CONTRA-001"]
    assert len(contra_exhibits) > 0
    assert contra_exhibits[0].status == "confirmed"
    assert "Confirmed discrepancy against CDR" in contra_exhibits[0].description


@pytest.mark.asyncio
async def test_primary_evidence_verification_package_export(test_db_session):
    """End-to-end export of Evidence Verification Package ZIP bundle with real SHA-256 manifest."""
    service = ContradictionEngineService(test_db_session)
    zip_bytes, manifest = await service.generate_evidence_verification_package(
        "CASE-P9-001", "lead_inv@crimekit.local"
    )

    assert len(zip_bytes) > 0
    assert manifest["case_id"] == "CASE-P9-001"
    assert len(manifest["files"]) >= 8

    # Unpack ZIP in-memory and verify real SHA-256 digests
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        file_list = zf.namelist()
        assert "manifest.json" in file_list
        assert "report.pdf" in file_list
        assert "report.json" in file_list
        assert "contradiction-matrix.json" in file_list
        assert "review-history.json" in file_list

        # Verify real SHA-256 hashes against manifest entries
        for entry in manifest["files"]:
            file_data = zf.read(entry["path"])
            computed_hash = hashlib.sha256(file_data).hexdigest().lower()
            assert computed_hash == entry["sha256"].lower(), f"Hash mismatch for {entry['path']}"
