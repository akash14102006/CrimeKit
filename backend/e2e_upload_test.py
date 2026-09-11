"""
Enterprise E2E Upload Pipeline Test
Tests: Case Creation → Upload Start → Chunk → Complete → OCR → Entities → Timeline → AI → KG → Workspace
"""
import hashlib
import json
import os
import sys
import time
import uuid

import requests

# Add backend to path for auth imports
sys.path.insert(0, os.path.dirname(__file__))
from app.auth import create_access_token

BASE = os.getenv("API_BASE", "http://127.0.0.1:8002")

# Create auth token for testing
test_user_id = "test-user-e2e"
token = create_access_token({"sub": test_user_id, "email": "test@crimekit.dev", "roles": ["admin"]})
HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

PASS_COUNT = 0
FAIL_COUNT = 0

def test(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  [PASS] {name}: {detail}")
    else:
        FAIL_COUNT += 1
        print(f"  [FAIL] {name}: {detail}")


# ── 1. Backend Health ───────────────────────────────────────────
print("\n" + "=" * 60)
print("  STAGE 1: BACKEND HEALTH")
print("=" * 60)
r = requests.get(f"{BASE}/health", timeout=5)
test("GET /health", r.status_code == 200, f"status={r.status_code}")

# ── 2. Create Case ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STAGE 2: CREATE CASE")
print("=" * 60)
case_id = str(uuid.uuid4())
r = requests.post(f"{BASE}/cases/", json={
    "title": "E2E Upload Pipeline Test - Full Pipeline",
    "description": "Automated E2E test for forensic upload pipeline",
    "status": "open",
    "priority": "high"
}, headers=HEADERS, timeout=10)
test("POST /cases/", r.status_code == 200, f"status={r.status_code}")
case_data = r.json() if r.status_code == 200 else {}
case_id = case_data.get("id", case_id)
print(f"     Case ID: {case_id}")

# ── 3. Upload Start ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STAGE 3: UPLOAD START")
print("=" * 60)
test_pdf = os.path.join(os.path.dirname(__file__), "test_evidence", "investigation_report.pdf")
if not os.path.exists(test_pdf):
    # Create a minimal test PDF
    os.makedirs(os.path.dirname(test_pdf), exist_ok=True)
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 185 >>
stream
BT
/F1 24 Tf
100 700 Td
(CrimeKit Investigation Report) Tj
0 -30 Td
/F1 14 Tf
(Case: Pipeline Test) Tj
0 -20 Td
(Date: 2026-08-06) Tj
0 -20 Td
(Status: Under Investigation) Tj
0 -20 Td
(Email: s.mitchell@austin.gov) Tj
0 -20 Td
(Phone: (512) 555-0147) Tj
0 -20 Td
(IP: 192.168.1.45) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000503 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
580
%%EOF"""
    with open(test_pdf, "wb") as f:
        f.write(pdf_content)

file_size = os.path.getsize(test_pdf)
file_hash = hashlib.sha256(open(test_pdf, "rb").read()).hexdigest()
print(f"     PDF: {test_pdf} ({file_size} bytes)")

r = requests.post(f"{BASE}/uploads/start", json={
    "filename": os.path.basename(test_pdf),
    "file_size": file_size,
    "case_id": case_id,
    "mime_type": "application/pdf"
}, headers=HEADERS, timeout=10)
test("POST /uploads/start", r.status_code == 200, f"status={r.status_code}")
upload_data = r.json() if r.status_code == 200 else {}
session_id = upload_data.get("session_id", "")
object_key = upload_data.get("object_key", "")
print(f"     Session: {session_id}")
print(f"     Object Key: {object_key}")

# ── 4. Upload Chunk ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STAGE 4: UPLOAD CHUNK")
print("=" * 60)
with open(test_pdf, "rb") as f:
    chunk_data = f.read()

files = {"chunk": (os.path.basename(test_pdf), chunk_data, "application/pdf")}
data = {"session_id": session_id, "chunk_number": "1", "chunk_sha256": file_hash}
r = requests.post(f"{BASE}/uploads/chunk", files=files, data=data, headers={"Authorization": f"Bearer {token}"}, timeout=30)
test("POST /uploads/chunk", r.status_code == 200, f"status={r.status_code}, size={len(chunk_data)}")
chunk_resp = r.json() if r.status_code == 200 else {}
chunk_etag = chunk_resp.get("etag", "missing")
print(f"     ETag: {chunk_etag}")

# ── 5. Upload Complete ──────────────────────────────────────────
print("\n" + "=" * 60)
print("  STAGE 5: UPLOAD COMPLETE")
print("=" * 60)
r = requests.post(f"{BASE}/uploads/complete?session_id={session_id}", json={
    "parts": [{"PartNumber": 1, "ETag": chunk_etag}]
}, headers=HEADERS, timeout=30)
test("POST /uploads/complete", r.status_code == 200, f"status={r.status_code}")
complete_data = r.json() if r.status_code == 200 else {}
evidence_id = complete_data.get("evidence_id", "")
print(f"     Evidence ID: {evidence_id}")

# ── 6. Verify PostgreSQL ────────────────────────────────────────
print("\n" + "=" * 60)
print("  STAGE 6: VERIFY POSTGRESQL")
print("=" * 60)
r = requests.get(f"{BASE}/evidence/{evidence_id}", headers=HEADERS, timeout=10)
test("GET /evidence/{id}", r.status_code == 200, f"status={r.status_code}")
ev_data = r.json() if r.status_code == 200 else {}
test("Filename matches", ev_data.get("filename") == os.path.basename(test_pdf))
test("Size matches", ev_data.get("size") == file_size)
test("SHA-256 matches", ev_data.get("sha256", "").startswith(file_hash[:16]))

# ── 7. Verify MinIO ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STAGE 7: VERIFY MINIO")
print("=" * 60)
import boto3
from botocore.config import Config
minio = boto3.client("s3",
    endpoint_url=os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
    aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "crimekit_dev_minio"),
    aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "crimekit_dev_minio_secret"),
    config=Config(signature_version="s3v4"),
    region_name="us-east-1"
)
try:
    head = minio.head_object(Bucket="crimekit-evidence", Key=object_key)
    test("Object in MinIO", True, f"size={head['ContentLength']}, type={head['ContentType']}")
except Exception as e:
    test("Object in MinIO", False, str(e))

# ── 8. Wait for Forensic Processing ─────────────────────────────
print("\n" + "=" * 60)
print("  STAGE 8: WAIT FOR FORENSIC PROCESSING")
print("=" * 60)
max_wait = 30
for i in range(max_wait):
    r = requests.get(f"{BASE}/evidence/{evidence_id}/forensic-jobs", headers=HEADERS, timeout=10)
    if r.status_code == 200:
        jobs = r.json()
        completed = sum(1 for j in jobs if j.get("status") == "completed")
        if completed > 0:
            test("Worker processing completed", True, f"completed={completed}")
            break
    time.sleep(1)
else:
    test("Worker processing completed", False, f"timed out after {max_wait}s")

# ── 9. Verify OCR ───────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STAGE 9: VERIFY OCR")
print("=" * 60)
r = requests.get(f"{BASE}/evidence/{evidence_id}/ocr", headers=HEADERS, timeout=10)
test("GET /evidence/{id}/ocr", r.status_code == 200, f"status={r.status_code}")
ocr_data = r.json() if r.status_code == 200 else {}
text = ocr_data.get("text", "")
test("OCR extracted text", len(text) > 0, f"length={len(text)}")

# ── 10. Verify Entities ─────────────────────────────────────────
print("\n" + "=" * 60)
print("  STAGE 10: VERIFY ENTITIES")
print("=" * 60)
r = requests.get(f"{BASE}/entities?case_id={case_id}", headers=HEADERS, timeout=10)
test("GET /entities", r.status_code == 200, f"status={r.status_code}")
ent_data = r.json() if r.status_code == 200 else {}
entities = ent_data.get("entities", [])
test("Entities found", len(entities) > 0, f"count={len(entities)}")
for e in entities[:5]:
    print(f"       - [{e.get('type')}] {e.get('name')}")

# ── 11. Verify Timeline ─────────────────────────────────────────
print("\n" + "=" * 60)
print("  STAGE 11: VERIFY TIMELINE")
print("=" * 60)
r = requests.get(f"{BASE}/timeline?case_id={case_id}", headers=HEADERS, timeout=10)
test("GET /timeline", r.status_code == 200, f"status={r.status_code}")
tl_data = r.json() if r.status_code == 200 else {}
if isinstance(tl_data, list):
    events = tl_data
else:
    events = tl_data.get("timeline", tl_data.get("events", []))
test("Timeline events found", len(events) > 0, f"count={len(events)}")

# ── 12. Verify AI Findings ──────────────────────────────────────
print("\n" + "=" * 60)
print("  STAGE 12: VERIFY AI FINDINGS")
print("=" * 60)
r = requests.get(f"{BASE}/findings?case_id={case_id}", headers=HEADERS, timeout=10)
test("GET /findings", r.status_code == 200, f"status={r.status_code}")
find_data = r.json() if r.status_code == 200 else {}
findings = find_data.get("findings", [])
test("AI findings present", len(findings) > 0, f"count={len(findings)}")

# ── 13. Verify Knowledge Graph ──────────────────────────────────
print("\n" + "=" * 60)
print("  STAGE 13: VERIFY KNOWLEDGE GRAPH")
print("=" * 60)
r = requests.get(f"{BASE}/kg/case/{case_id}/graph", headers=HEADERS, timeout=10)
test("GET /kg/case/{id}/graph", r.status_code == 200, f"status={r.status_code}")
kg_data = r.json() if r.status_code == 200 else {}
nodes = kg_data.get("nodes", [])
edges = kg_data.get("edges", [])
test("KG nodes found", len(nodes) > 0, f"nodes={len(nodes)}")

# ── 14. Verify Workspace ────────────────────────────────────────
print("\n" + "=" * 60)
print("  STAGE 14: VERIFY WORKSPACE")
print("=" * 60)
r = requests.get(f"{BASE}/workspace/cases/{case_id}", headers=HEADERS, timeout=10)
test("GET /workspace/cases/{id}", r.status_code == 200, f"status={r.status_code}")
ws_data = r.json() if r.status_code == 200 else {}
test("Workspace has case", ws_data.get("case", {}).get("id") == case_id)
test("Workspace has evidence", len(ws_data.get("evidence", [])) > 0)
test("Workspace has KG", ws_data.get("knowledge_graph", {}).get("available", False))

# ── 15. Verify Cases List ───────────────────────────────────────
print("\n" + "=" * 60)
print("  STAGE 15: VERIFY CASES LIST")
print("=" * 60)
r = requests.get(f"{BASE}/cases/", headers=HEADERS, timeout=10)
test("GET /cases/", r.status_code == 200, f"status={r.status_code}")
cases_data = r.json() if r.status_code == 200 else {}
items = cases_data.get("items", [])
test("Cases list has items", len(items) > 0, f"count={len(items)}")

# ── Summary ─────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  E2E SUMMARY")
print("=" * 60)
print(f"  Passed: {PASS_COUNT}")
print(f"  Failed: {FAIL_COUNT}")
print(f"  Total:  {PASS_COUNT + FAIL_COUNT}")
print()
if FAIL_COUNT == 0:
    print("  ALL TESTS PASSED")
else:
    print("  SOME TESTS FAILED")
print()
print(f"  Case ID:     {case_id}")
print(f"  Evidence ID: {evidence_id}")
print(f"  Session ID:  {session_id}")
print(f"  MinIO Key:   {object_key}")
print()
sys.exit(0 if FAIL_COUNT == 0 else 1)
