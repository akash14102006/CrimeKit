"""End-to-end forensic pipeline test - Direct injection (no MinIO needed)."""
import sys, os, json, time, requests

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("TESTING", "0")

from passlib.hash import pbkdf2_sha256
from app import database, models
from app.auth import create_access_token

BASE = "http://127.0.0.1:8002"

def get_token():
    db = database.SessionLocal()
    for rname in ("admin", "user", "investigator"):
        if not db.query(models.Role).filter(models.Role.name == rname).first():
            db.add(models.Role(name=rname, description=f"{rname} role"))
    db.commit()
    user = db.query(models.User).filter(models.User.email == "pipeline_test@test.com").first()
    if not user:
        user = models.User(email="pipeline_test@test.com", password_hash=pbkdf2_sha256.hash("TestPass123!"), is_active=True)
        db.add(user); db.commit(); db.refresh(user)
        print(f"[+] Created user: {user.id}")
    admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
    if admin_role and admin_role not in user.roles:
        user.roles.append(admin_role); db.commit()
        print("[+] Assigned admin role")
    token = create_access_token({"sub": user.id})
    db.close()
    return token

def test_e2e():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(f"{BASE}/auth/me", headers=headers)
    print(f"\n[1] Auth check: {r.status_code} - {r.json().get('email', 'FAIL')}")
    assert r.status_code == 200

    r = requests.post(f"{BASE}/cases/", json={
        "title": "Pipeline E2E Test Case",
        "description": "Testing full forensic pipeline",
        "status": "open",
    }, headers=headers)
    print(f"[2] Create case: {r.status_code}")
    case = r.json()
    case_id = case["id"]
    print(f"    Case ID: {case_id}")

    pdf_path = os.path.join(os.path.dirname(__file__), "test_pipeline.pdf")
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    import hashlib
    sha256 = hashlib.sha256(pdf_data).hexdigest()
    print(f"\n[3] Test PDF: {len(pdf_data)} bytes, sha256={sha256[:16]}...")

    # Direct injection: create Evidence + ForensicJob in DB (bypass MinIO)
    storage_dir = os.path.join(os.path.dirname(__file__), "storage", "evidence")
    os.makedirs(storage_dir, exist_ok=True)
    storage_path = os.path.join(storage_dir, sha256)
    with open(storage_path, "wb") as f:
        f.write(pdf_data)
    print(f"[4] Stored file: {storage_path}")

    db = database.SessionLocal()
    evidence = models.Evidence(
        filename="investigation_report.pdf",
        case_id=case_id,
        storage_path=storage_path,
        sha256=sha256,
        size=len(pdf_data),
        mime_type="application/pdf",
        metadata_json={},
        bucket="crimekit-evidence",
        object_key=f"cases/{case_id}/investigation_report.pdf",
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    evidence_id = evidence.id
    print(f"[5] Created Evidence: {evidence_id[:8]}")

    job = models.ForensicJob(
        evidence_id=evidence_id,
        processors=["hashes", "mime", "metadata", "ocr", "pdf_text"],
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    job_id = job.id
    print(f"[6] Created ForensicJob: {job_id[:8]} (status=queued)")
    db.close()

    # Start worker in-process (bypass start_worker() which needs server thread)
    print(f"\n[7] Processing job {job_id[:8]} directly via _process_job()...")
    from app.processing import _process_job
    _process_job(job_id)
    print(f"    _process_job() returned")

    # Wait briefly for any async operations
    time.sleep(1)

    # Check results
    db = database.SessionLocal()

    print("\n" + "="*60)
    print("PIPELINE RESULTS VERIFICATION")
    print("="*60)

    # 1. Check ForensicJob
    job = db.query(models.ForensicJob).filter(models.ForensicJob.id == job_id).first()
    print(f"\n[8] ForensicJob: status={job.status}")
    if job.result:
        rdata = json.loads(job.result) if isinstance(job.result, str) else job.result
        print(f"    result_keys: {list(rdata.keys())}")
        for k, v in rdata.items():
            if isinstance(v, dict):
                print(f"    {k}: {list(v.keys())[:5]}")
    if job.error:
        print(f"    ERROR: {job.error}")

    # 2. Check Evidence metadata_json
    evidence = db.query(models.Evidence).filter(models.Evidence.id == evidence_id).first()
    meta = evidence.metadata_json or {}
    print(f"\n[9] Evidence metadata_json keys: {list(meta.keys())}")
    ocr_text = meta.get("ocr_text", "")
    print(f"    OCR text length: {len(ocr_text)}")
    if ocr_text:
        print(f"    OCR preview: {ocr_text[:300]}...")
    fe_meta = meta.get("forensic_engine", {})
    if fe_meta:
        print(f"    forensic_engine keys: {list(fe_meta.keys())[:10]}")

    # 3. Check ForensicResults
    results = db.query(models.ForensicResult).filter(
        models.ForensicResult.evidence_id == evidence_id
    ).all()
    print(f"\n[10] ForensicResult rows: {len(results)}")
    for fr in results:
        rdata = fr.result or {}
        if isinstance(rdata, str):
            rdata = json.loads(rdata)
        keys = list(rdata.keys())[:5]
        print(f"    - processor='{fr.processor}', keys={keys}")

    # Check specific processors
    processors_found = {fr.processor for fr in results}
    expected = {
        "entity_extraction", "relationship_extraction",
        "timeline_extraction", "knowledge_graph", "ai_findings",
    }
    missing = expected - processors_found
    if missing:
        print(f"\n    *** MISSING processors: {missing}")
    else:
        print(f"\n    ALL expected processors present!")

    # 4. Check Documents
    docs = db.query(models.Document).filter(
        models.Document.evidence_id == evidence_id
    ).all()
    print(f"\n[11] Document rows: {len(docs)}")
    for d in docs:
        print(f"    - doc_id={d.id[:8]}, text_length={len(d.text) if d.text else 0}")

    # 5. Check API endpoints
    print("\n[12] API Endpoint Checks:")

    r = requests.get(f"{BASE}/evidence/{evidence_id}/ocr", headers=headers)
    print(f"    OCR endpoint: {r.status_code}")
    if r.status_code == 200:
        ocr = r.json()
        print(f"      source={ocr.get('source')}, text_len={len(ocr.get('text','') or '')}")

    r = requests.get(f"{BASE}/advanced-forensics/results/{evidence_id}", headers=headers)
    print(f"    Forensics results: {r.status_code}")
    if r.status_code == 200:
        print(f"      total={r.json().get('total', 0)}")

    r = requests.get(f"{BASE}/advanced-forensics/results/{evidence_id}/timeline", headers=headers)
    print(f"    Timeline: {r.status_code}")
    if r.status_code == 200:
        print(f"      events={r.json().get('total', 0)}")

    r = requests.get(f"{BASE}/advanced-forensics/results/{evidence_id}/entities", headers=headers)
    print(f"    Entities: {r.status_code}")
    if r.status_code == 200:
        print(f"      entities={r.json().get('total', 0)}")

    r = requests.get(f"{BASE}/advanced-forensics/results/{evidence_id}/findings", headers=headers)
    print(f"    Findings: {r.status_code}")
    if r.status_code == 200:
        print(f"      findings={r.json().get('total', 0)}")

    r = requests.get(f"{BASE}/workspace/cases/{case_id}", headers=headers)
    print(f"    Workspace: {r.status_code}")
    if r.status_code == 200:
        ws = r.json()
        print(f"      evidence_count={ws.get('evidence_count')}")
        kg = ws.get("knowledge_graph", {})
        print(f"      kg.available={kg.get('available')}, entities={kg.get('entity_count')}")

    r = requests.get(f"{BASE}/kg/case/{case_id}/graph", headers=headers)
    print(f"    KG graph: {r.status_code}")
    if r.status_code == 200:
        g = r.json()
        print(f"      nodes={len(g.get('graph', []))}")

    db.close()

    print("\n" + "="*60)
    print("PIPELINE E2E TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_e2e()
