"""
Phase 7 Verification Tests: CrimeKit Forensic Report Agent & Export Pipeline.

Tests:
1. Report request validation & schema integrity.
2. ReportDocument assembly with real case evidence.
3. Cryptographic hash ledger generation & SHA-256 verification.
4. Hash mismatch detection when physical storage is altered.
5. Deterministic PyMuPDF PDF report rendering & multi-page support.
6. Structured JSON report export with exhibits & contradictions.
7. Report package manifest computation with verified SHA-256 digests.
8. Certificate template is strictly marked DRAFT / HUMAN REVIEW.
9. Case boundary isolation (cannot access other case records).
10. Primary end-to-end multi-agent investigation to forensic report pipeline.
"""

import os
import uuid
import pytest
import hashlib
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app import models, database
from app.agents.report_schemas import (
    ReportRequest,
    ReportDocument,
    CertificateTemplate,
    ReportPackageManifest,
)
from app.agents.report_service import ForensicReportService, compute_sha256_bytes, compute_sha256_file
from app.agents.orchestration_schemas import (
    SharedInvestigationContext,
    SpecialistAgentTask,
    SpecialistTaskResult,
    ContradictionItem,
)


@pytest.fixture
def db_session():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def case_with_forensic_evidence(db_session: Session):
    case_id = f"case_rpt_{uuid.uuid4().hex[:8]}"
    case = models.Case(
        id=case_id,
        title="State v. Rahul Kumar (Telecom Fraud)",
        description="Investigation into unauthorized SIM swap and fraudulent funds transfer.",
        status="open",
    )
    db_session.add(case)

    # Add evidence 1
    ev1 = models.Evidence(
        id="EV-087",
        case_id=case_id,
        filename="sim_registration_form.pdf",
        storage_path="/tmp/fake_sim_registration.pdf",
        sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        size=1024,
        mime_type="application/pdf",
    )
    # Add evidence 2
    ev2 = models.Evidence(
        id="EV-104",
        case_id=case_id,
        filename="cdr_activity_log.csv",
        storage_path="/tmp/fake_cdr_activity.csv",
        sha256="a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
        size=2048,
        mime_type="text/csv",
    )
    # Add evidence 3
    ev3 = models.Evidence(
        id="EV-119",
        case_id=case_id,
        filename="tower_location_exif.jpg",
        storage_path="/tmp/fake_tower_location.jpg",
        sha256="4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
        size=4096,
        mime_type="image/jpeg",
    )
    db_session.add_all([ev1, ev2, ev3])

    # Chain of custody records
    c1 = models.ChainOfCustody(
        id=f"coc_{uuid.uuid4().hex[:6]}",
        evidence_id="EV-087",
        action="ingest",
        actor_id="officer_sharma",
        notes="Seized from telecom store repository",
    )
    c2 = models.ChainOfCustody(
        id=f"coc_{uuid.uuid4().hex[:6]}",
        evidence_id="EV-104",
        action="ingest",
        actor_id="officer_sharma",
        notes="Exported from server switch logs",
    )
    db_session.add_all([c1, c2])

    # Add ForensicResult with timeline record
    fr1 = models.ForensicResult(
        id=f"fr_{uuid.uuid4().hex[:6]}",
        evidence_id="EV-104",
        processor="cdr_processor",
        result={
            "timeline": [
                {
                    "timestamp": "2026-10-08T21:14:00Z",
                    "event": "Outgoing call to +91 9876543210 duration 182s",
                    "description": "Call detail transaction",
                }
            ]
        },
    )
    db_session.add(fr1)

    # Attach GPS metadata to EV-119
    ev3.metadata_json = {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timestamp": "2026-10-08T21:12:00Z",
        "description": "Connaught Place Sector 4",
    }

    db_session.commit()
    return case_id


def test_report_request_and_contract_validation():
    req = ReportRequest(
        case_id="CASE-001",
        title="Forensic Audit",
        include_hash_ledger=True,
    )
    assert req.case_id == "CASE-001"
    assert req.include_hash_ledger is True
    assert req.include_certificate_template is True


@pytest.mark.asyncio
async def test_build_report_document_with_evidence_and_custody(db_session: Session, case_with_forensic_evidence: str):
    service = ForensicReportService(db_session)
    req = ReportRequest(
        case_id=case_with_forensic_evidence,
        title="Executive Forensic Brief",
        objective="Verify device association and timeline integrity",
    )

    doc = await service.build_report_document(req, "investigator@crimekit.gov")
    assert doc.case_id == case_with_forensic_evidence
    assert len(doc.evidence_index) == 3
    assert len(doc.hash_ledger) == 3
    assert len(doc.chain_of_custody) == 2
    assert len(doc.timeline_exhibits) >= 1
    assert len(doc.geospatial_exhibits) >= 1
    assert doc.review_status == "review_required"


def test_pdf_report_rendering_deterministic(db_session: Session, case_with_forensic_evidence: str):
    import asyncio
    service = ForensicReportService(db_session)
    req = ReportRequest(case_id=case_with_forensic_evidence, title="Court Summary Report")
    doc = asyncio.run(service.build_report_document(req, "investigator@crimekit.gov"))

    pdf_bytes = service.render_pdf(doc)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF-")


def test_certificate_template_marked_as_human_review():
    cert = CertificateTemplate(
        case_id="CASE-TEST",
        declaration_text="Evidence preserved intact.",
        hash_affirmation="Hashes verified.",
    )
    assert "REQUIRES AUTHORIZED HUMAN/LEGAL REVIEW" in cert.legal_framework_notice
    assert "Does not constitute automated legal admissibility" in cert.legal_framework_notice
    assert cert.status == "DRAFT"
    assert "_____" in cert.signatory_name


@pytest.mark.asyncio
async def test_hash_mismatch_detection_on_altered_file(tmp_path, db_session: Session):
    # Create real file on disk
    file_path = str(tmp_path / "sample_evidence.bin")
    with open(file_path, "wb") as f:
        f.write(b"ORIGINAL FORENSIC DATA")

    stored_hash = hashlib.sha256(b"ORIGINAL FORENSIC DATA").hexdigest()

    case_id = f"case_mismatch_{uuid.uuid4().hex[:6]}"
    case = models.Case(id=case_id, title="Tamper Test Case")
    db_session.add(case)

    ev = models.Evidence(
        id=f"EV-TAMPER-{uuid.uuid4().hex[:4]}",
        case_id=case_id,
        filename="sample_evidence.bin",
        storage_path=file_path,
        sha256=stored_hash,
        size=22,
    )
    db_session.add(ev)
    db_session.commit()

    service = ForensicReportService(db_session)
    req = ReportRequest(case_id=case_id, title="Integrity Check")

    # 1. Unaltered state -> verified
    doc = await service.build_report_document(req, "examiner@crimekit.gov")
    assert doc.hash_ledger[0].verification_status == "verified"

    # 2. Alter file content on disk
    with open(file_path, "wb") as f:
        f.write(b"TAMPERED FILE CONTENT")

    doc2 = await service.build_report_document(req, "examiner@crimekit.gov")
    assert doc2.hash_ledger[0].verification_status == "mismatch"


def test_package_manifest_and_sha256_verification(db_session: Session, case_with_forensic_evidence: str):
    import asyncio
    service = ForensicReportService(db_session)
    req = ReportRequest(case_id=case_with_forensic_evidence, title="Package Manifest Test")
    doc = asyncio.run(service.build_report_document(req, "examiner@crimekit.gov"))

    pdf_bytes = service.render_pdf(doc)
    json_bytes = doc.model_dump_json().encode("utf-8")

    manifest = service.generate_report_package(doc, pdf_bytes, json_bytes)
    assert manifest.case_id == case_with_forensic_evidence
    assert len(manifest.files) == 2
    assert manifest.files[0].path == "report.pdf"
    assert manifest.files[0].sha256 == compute_sha256_bytes(pdf_bytes)
    assert manifest.files[1].path == "report.json"
    assert manifest.files[1].sha256 == compute_sha256_bytes(json_bytes)
    assert manifest.overall_integrity_status == "verified"


@pytest.mark.asyncio
async def test_case_isolation_in_report_building(db_session: Session, case_with_forensic_evidence: str):
    # Create another case
    other_case_id = f"case_other_{uuid.uuid4().hex[:6]}"
    other_case = models.Case(id=other_case_id, title="Other Department Case")
    db_session.add(other_case)
    ev_other = models.Evidence(
        id="EV-999-SECRET",
        case_id=other_case_id,
        filename="unrelated_confidential.docx",
        storage_path="/tmp/unrelated.docx",
        sha256="1111111111111111111111111111111111111111111111111111111111111111",
        size=500,
    )
    db_session.add(ev_other)
    db_session.commit()

    service = ForensicReportService(db_session)
    req = ReportRequest(case_id=case_with_forensic_evidence, title="Isolation Check")
    doc = await service.build_report_document(req, "investigator@crimekit.gov")

    # Assure other case's evidence does not appear
    evidence_ids = [e.evidence_id for e in doc.evidence_index]
    assert "EV-999-SECRET" not in evidence_ids
    assert len(doc.evidence_index) == 3


@pytest.mark.asyncio
async def test_primary_e2e_multi_agent_findings_to_report(db_session: Session, case_with_forensic_evidence: str):
    # Simulate verified orchestrator context from Phase 6
    context = SharedInvestigationContext(
        case_id=case_with_forensic_evidence,
        objective="Determine whether Rahul Kumar was associated with the phone number, what happened around the relevant call, and whether the device was near the incident location.",
        evidence_refs=["EV-087", "EV-104", "EV-119"],
    )

    t1_res = SpecialistTaskResult(
        task_id="task_det_1",
        agent_id="detective",
        status="completed",
        summary="SIM application links phone number to Rahul Kumar.",
        findings=[{
            "finding_id": "F-001",
            "source_agent": "detective",
            "summary": "SIM registration records affirm association with Rahul Kumar.",
            "evidence_refs": ["EV-087"],
            "status": "supported",
        }],
        evidence_refs=["EV-087"],
    )
    t2_res = SpecialistTaskResult(
        task_id="task_time_1",
        agent_id="timeline",
        status="completed",
        summary="Call activity recorded at 21:14 UTC.",
        findings=[{
            "finding_id": "F-002",
            "source_agent": "timeline",
            "summary": "182-second call transaction occurred at 21:14 UTC.",
            "evidence_refs": ["EV-104"],
            "status": "supported",
        }],
        evidence_refs=["EV-104"],
    )
    t3_res = SpecialistTaskResult(
        task_id="task_geo_1",
        agent_id="geoscope",
        status="completed",
        summary="Device fix located at Connaught Place at 21:12 UTC.",
        findings=[{
            "finding_id": "F-003",
            "source_agent": "geoscope",
            "summary": "Device location fix recorded near incident area at 21:12 UTC.",
            "evidence_refs": ["EV-119"],
            "status": "supported",
        }],
        evidence_refs=["EV-119"],
    )
    contra = ContradictionItem(
        type="timestamp_gap",
        sources=["EV-104", "EV-119"],
        description="Temporal gap between GPS fix (21:12) and subsequent cell activity.",
        status="needs_review",
    )

    context.task_results = [t1_res, t2_res, t3_res]
    context.contradictions = [contra]

    service = ForensicReportService(db_session)
    req = ReportRequest(
        case_id=case_with_forensic_evidence,
        title="Primary E2E Multi-Agent Report",
        objective=context.objective,
    )

    doc = await service.build_report_document(
        request=req,
        current_user_email="lead_investigator@crimekit.gov",
        investigation_context=context,
    )

    # Validate aggregated findings preserve provenance
    assert len(doc.findings) == 3
    finding_agents = [f["source_agent"] for f in doc.findings]
    assert "detective" in finding_agents
    assert "timeline" in finding_agents
    assert "geoscope" in finding_agents

    # Validate contradiction is preserved
    assert len(doc.contradictions) == 1
    assert doc.contradictions[0].type == "timestamp_gap"

    # Validate evidence index references
    assert len(doc.evidence_index) == 3

    # Validate markdown render preserves critical sections
    markdown = service.render_markdown(doc)
    assert "SPECIALIST FINDINGS" in markdown
    assert "EV-087" in markdown
    assert "EV-104" in markdown
    assert "EV-119" in markdown
    assert "ELECTRONIC EVIDENCE CERTIFICATE TEMPLATE" in markdown
    assert "REQUIRES AUTHORIZED HUMAN/LEGAL REVIEW" in markdown
