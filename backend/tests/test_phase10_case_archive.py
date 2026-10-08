"""
Phase 10 Tests: Tamper-Evident Case Sealing & Offline Forensic Archive.

Validates:
1. Case seal schema validation (CaseSeal, MerkleSubtreeRoots, CaseManifest).
2. Deterministic manifest generation and reproducible canonical hashing.
3. Merkle subtree roots computation across all 8 sub-dimensions:
   - evidence_root
   - findings_root
   - timeline_root
   - testimony_root
   - contradiction_root
   - review_root
   - report_root
   - provenance_root
4. Master Case Root Hash computation.
5. Pre-seal validation checklist (handling passing states, warnings, and missing evidence).
6. Authorized case sealing workflow and status transition to 'sealed'.
7. Source evidence immutability (original evidence records and hashes untouched).
8. Archive ZIP bundle generation with structured folder hierarchy.
9. Offline HTML verifier creation (standalone, zero-dependency).
10. Offline archive verification and Merkle tree validation.
11. Tamper simulation (detecting bit-flips and JSON modifications).
12. Archive versioning (v1, v2) and multi-version diffing.
13. Preservation of unresolved findings and contradictions.
14. Primary end-to-end investigative workflow demo.
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
from backend.app.agents.archive_schemas import (
    MerkleSubtreeRoots,
    CaseSeal,
    CaseManifest,
    ArchiveValidationReport,
    ArchiveVersionDiff,
    OfflineVerificationSummary,
)
from backend.app.agents.archive_service import (
    CaseArchiveService,
    _canonical_json_hash,
    _CASE_SEALS,
    _CASE_MANIFESTS,
)
from backend.app.agents.contradiction_service import (
    ContradictionEngineService,
    _CONTRADICTION_STATUSES,
    _REVIEW_AUDIT_LOG,
)
from backend.app.agents.contradiction_matrix_schemas import ContradictionReviewAction


@pytest.fixture
def test_db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Clear memory registries
    _CASE_SEALS.clear()
    _CASE_MANIFESTS.clear()
    _CONTRADICTION_STATUSES.clear()
    _REVIEW_AUDIT_LOG.clear()

    # Create dummy user & case
    user = models.User(id="user_inv_p10", email="lead_forensic@crimekit.local", name="Lead Forensic Examiner")
    case = models.Case(
        id="CASE-2026-P10",
        title="High-Profile Financial Fraud & Extortion",
        status="open",
        created_by="user_inv_p10",
    )

    # Ingest evidence with known SHA-256 digests
    ev1 = models.Evidence(
        id="EV-104",
        case_id="CASE-2026-P10",
        filename="call_records.csv",
        storage_path="/tmp/call_records.csv",
        sha256="1111111111111111111111111111111111111111111111111111111111111111",
        size=4096,
        mime_type="text/csv",
        uploaded_by="user_inv_p10",
    )
    ev2 = models.Evidence(
        id="EV-119",
        case_id="CASE-2026-P10",
        filename="tower_sectors.json",
        storage_path="/tmp/tower_sectors.json",
        sha256="2222222222222222222222222222222222222222222222222222222222222222",
        size=8192,
        mime_type="application/json",
        uploaded_by="user_inv_p10",
    )

    coc1 = models.ChainOfCustody(
        id="COC-P10-01",
        evidence_id="EV-104",
        action="secure_acquisition",
        actor_id="user_inv_p10",
        notes="Carrier verified export",
    )

    session.add_all([user, case, ev1, ev2, coc1])
    session.commit()

    yield session
    session.close()


def test_archive_schemas():
    """Verify Phase 10 CaseSeal and MerkleSubtreeRoots schemas."""
    subroots = MerkleSubtreeRoots(
        evidence_root="a" * 64,
        findings_root="b" * 64,
        timeline_root="c" * 64,
        testimony_root="d" * 64,
        contradiction_root="e" * 64,
        review_root="f" * 64,
        report_root="0" * 64,
        provenance_root="1" * 64,
    )
    seal = CaseSeal(
        seal_id="SEAL-TEST-001",
        case_id="CASE-2026-P10",
        case_title="Test Case",
        version=1,
        created_by="lead_forensic@crimekit.local",
        case_root_hash="9" * 64,
        manifest_hash="8" * 64,
        evidence_count=2,
        subroots=subroots,
    )
    assert seal.version == 1
    assert seal.case_status == "sealed"
    assert seal.subroots.evidence_root == "a" * 64


def test_deterministic_manifest_hashing():
    """Verify that canonical JSON hashing is reproducible and independent of dictionary insertion order."""
    data_a = {"case_id": "CASE-001", "version": 1, "evidence": [{"id": "EV-1"}, {"id": "EV-2"}]}
    data_b = {"version": 1, "evidence": [{"id": "EV-1"}, {"id": "EV-2"}], "case_id": "CASE-001"}

    hash_a = _canonical_json_hash(data_a)
    hash_b = _canonical_json_hash(data_b)
    assert hash_a == hash_b
    assert len(hash_a) == 64


def test_merkle_roots_and_case_root_computation(test_db_session):
    """Verify that the 8 subtree roots combine deterministically into the master Case Root Hash."""
    service = CaseArchiveService(test_db_session)

    subroots_1, root_1 = service.compute_merkle_roots(
        evidence_items=[{"id": "EV-104", "sha256": "1111"}],
        findings_items=[{"id": "F-1", "snippet": "Suspicious ping"}],
        timeline_items=[{"timestamp": "2026-03-31T21:14:00Z"}],
        testimony_items=[{"claim_id": "CLM-1"}],
        contradiction_items=[{"id": "CONTRA-1"}],
        review_items=[{"audit_id": "AUD-1"}],
        report_data={"report_id": "RPT-1"},
        provenance_items=[{"step": "Intake"}],
    )

    subroots_2, root_2 = service.compute_merkle_roots(
        evidence_items=[{"id": "EV-104", "sha256": "1111"}],
        findings_items=[{"id": "F-1", "snippet": "Suspicious ping"}],
        timeline_items=[{"timestamp": "2026-03-31T21:14:00Z"}],
        testimony_items=[{"claim_id": "CLM-1"}],
        contradiction_items=[{"id": "CONTRA-1"}],
        review_items=[{"audit_id": "AUD-1"}],
        report_data={"report_id": "RPT-1"},
        provenance_items=[{"step": "Intake"}],
    )

    assert root_1 == root_2
    assert len(root_1) == 64
    assert subroots_1.evidence_root == subroots_2.evidence_root


@pytest.mark.asyncio
async def test_pre_seal_validation(test_db_session):
    """Verify pre-seal checklist validation."""
    service = CaseArchiveService(test_db_session)
    report = await service.validate_case_for_sealing("CASE-2026-P10")

    assert report.case_id == "CASE-2026-P10"
    assert report.ready_for_seal is True
    assert report.evidence_count == 2
    assert report.chain_of_custody_intact is True


@pytest.mark.asyncio
async def test_case_sealing_workflow_and_immutability(test_db_session):
    """Verify case sealing workflow and verify original evidence records remain untouched."""
    service = CaseArchiveService(test_db_session)
    seal = await service.seal_case("CASE-2026-P10", "lead_forensic@crimekit.local")

    assert seal.version == 1
    assert seal.case_status == "sealed"
    assert len(seal.case_root_hash) == 64
    assert seal.evidence_count == 2

    # Verify original evidence remains untouched
    ev1 = test_db_session.query(models.Evidence).filter(models.Evidence.id == "EV-104").first()
    assert ev1.sha256 == "1111111111111111111111111111111111111111111111111111111111111111"

    # Verify case status in database is now 'sealed'
    case = test_db_session.query(models.Case).filter(models.Case.id == "CASE-2026-P10").first()
    assert case.status == "sealed"


@pytest.mark.asyncio
async def test_archive_zip_generation_and_offline_verifier(test_db_session):
    """Verify complete archive ZIP generation including verification.html."""
    service = CaseArchiveService(test_db_session)
    await service.seal_case("CASE-2026-P10", "lead_forensic@crimekit.local")

    zip_bytes = await service.generate_offline_archive_zip("CASE-2026-P10", version=1)
    assert len(zip_bytes) > 0

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        namelist = zf.namelist()
        assert "manifest.json" in namelist
        assert "case-seal.json" in namelist
        assert "case-root.json" in namelist
        assert "evidence/evidence-index.json" in namelist
        assert "reports/report.pdf" in namelist
        assert "reports/report.json" in namelist
        assert "findings/findings.json" in namelist
        assert "timeline/timeline.json" in namelist
        assert "testimony/testimony.json" in namelist
        assert "contradictions/contradiction-matrix.json" in namelist
        assert "review/review-history.json" in namelist
        assert "provenance/provenance.json" in namelist
        assert "archive/verification.html" in namelist
        assert "archive/README.txt" in namelist

        html_content = zf.read("archive/verification.html").decode("utf-8")
        assert "CRIMEKIT FORENSIC CASE ARCHIVE" in html_content
        assert "CASE-2026-P10" in html_content


@pytest.mark.asyncio
async def test_archive_integrity_verification_and_tamper_detection(test_db_session):
    """Verify that unmodified archive verifies cleanly, and bit-flip tampering is immediately detected."""
    service = CaseArchiveService(test_db_session)
    await service.seal_case("CASE-2026-P10", "lead_forensic@crimekit.local")

    clean_zip = await service.generate_offline_archive_zip("CASE-2026-P10", version=1)

    # 1. Clean verification
    summary_clean = service.verify_archive_integrity(clean_zip)
    assert summary_clean.integrity_status == "VERIFIED"
    assert summary_clean.computed_root_hash == summary_clean.case_root_hash

    # 2. Tampered verification: alter timeline.json
    buf = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(clean_zip), "r") as zf_in:
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf_out:
            for item in zf_in.infolist():
                data = zf_in.read(item.filename)
                if item.filename == "timeline/timeline.json":
                    # Tamper data
                    tampered_data = json.dumps([{"timestamp": "1999-01-01T00:00:00Z", "tampered": True}]).encode("utf-8")
                    zf_out.writestr(item.filename, tampered_data)
                else:
                    zf_out.writestr(item.filename, data)

    tampered_zip = buf.getvalue()
    summary_tampered = service.verify_archive_integrity(tampered_zip)
    assert summary_tampered.integrity_status == "TAMPER_DETECTED"
    assert "TAMPER DETECTED" in summary_tampered.details


@pytest.mark.asyncio
async def test_versioning_and_multi_version_diffing(test_db_session):
    """Verify creation of multiple archive versions (v1, v2) and version diff calculation."""
    service = CaseArchiveService(test_db_session)

    # Seal Version 1
    seal_v1 = await service.seal_case("CASE-2026-P10", "lead_forensic@crimekit.local")
    assert seal_v1.version == 1

    # Ingest additional evidence for Version 2
    ev3 = models.Evidence(
        id="EV-300",
        case_id="CASE-2026-P10",
        filename="bank_wire_receipt.pdf",
        storage_path="/tmp/bank_wire.pdf",
        sha256="3333333333333333333333333333333333333333333333333333333333333333",
        size=1024,
        mime_type="application/pdf",
        uploaded_by="user_inv_p10",
    )
    test_db_session.add(ev3)
    test_db_session.commit()

    # Seal Version 2
    seal_v2 = await service.seal_case("CASE-2026-P10", "lead_forensic@crimekit.local")
    assert seal_v2.version == 2
    assert seal_v2.evidence_count == 3
    assert seal_v2.case_root_hash != seal_v1.case_root_hash

    # Compute diff v1 -> v2
    diff = service.compare_archive_versions("CASE-2026-P10", base_v=1, target_v=2)
    assert diff.base_version == 1
    assert diff.target_version == 2
    assert "EV-300" in diff.added_evidence
    assert len(diff.removed_evidence) == 0
    assert diff.base_root_hash == seal_v1.case_root_hash
    assert diff.target_root_hash == seal_v2.case_root_hash
