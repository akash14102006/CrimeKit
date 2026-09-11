import requests
import json
import time
import os
from jose import jwt
from datetime import datetime, timedelta, timezone

BASE_URL = "http://localhost:8002"
SECRET_KEY = os.getenv('JWT_SECRET', 'dev-secret-change-me')

# 1. Generate local dev JWT token
now = datetime.now(timezone.utc)
payload = {
    "sub": "test-admin-id",
    "userId": "test-admin-id",
    "email": "admin@crimekit.io",
    "roles": ["admin", "investigator"],
    "exp": int((now + timedelta(hours=1)).timestamp())
}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
headers = {"Authorization": f"Bearer {token}"}

print(f"[1] Minted JWT dev token: {token[:30]}...")

# 2. Get active case
cases_res = requests.get(f"{BASE_URL}/cases/", headers=headers)
print(f"[2] Get cases response: status={cases_res.status_code}")
cases = cases_res.json()
if isinstance(cases, dict):
    cases = cases.get("items", [])
case_id = cases[0]["id"] if cases else None
print(f"    Active case ID: {case_id}")

# 3. Create a valid raw PDF file with structured forensic text
pdf_path = os.path.join(os.getcwd(), "scratch_test_report.pdf")
pdf_bytes = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kinds [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 380 >>
stream
BT
/F1 12 Tf
50 700 Td
(CONFIDENTIAL FORENSIC INVESTIGATION REPORT) Tj
0 -20 Td
(Date: 2026-08-04) Tj
0 -20 Td
(Investigator: Agent John Smith john.smith@cybercrime.gov) Tj
0 -20 Td
(Target Organization: Apex Global Technologies security@apexglobal.com) Tj
0 -20 Td
(Timeline: 2026-06-15 Unauthorized access detected) Tj
0 -20 Td
(Timeline: 2026-07-01 Data exfiltration to external C2 server) Tj
0 -20 Td
(Key Suspect: Robert Davis identified) Tj
0 -20 Td
(Summary: Critical severity cyber intrusion confirmed.) Tj
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
0000000246 00000 n 
0000000677 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
748
%%EOF
"""

with open(pdf_path, "wb") as f:
    f.write(pdf_bytes)
print(f"[3] Created real PDF file ({len(pdf_bytes)} bytes) at {pdf_path}")

# 4. Upload evidence
with open(pdf_path, "rb") as f:
    files = {"file": ("forensic_test_report.pdf", f, "application/pdf")}
    params = {"case_id": case_id} if case_id else {}
    upload_res = requests.post(f"{BASE_URL}/evidence/upload", files=files, params=params, headers=headers)

upload_data = upload_res.json()
evidence_id = upload_data.get("id")
print(f"[4] Upload Evidence Result: status={upload_res.status_code}, evidence_id={evidence_id}")

# 5. Wait for background worker processing
print("[5] Waiting 3 seconds for background worker to process evidence...")
time.sleep(3)

# 6. Check OCR Endpoint
ocr_res = requests.get(f"{BASE_URL}/evidence/{evidence_id}/ocr", headers=headers)
ocr_data = ocr_res.json()
print(f"[6] OCR Endpoint Result: status={ocr_res.status_code}, source={ocr_data.get('source')}, text_len={len(ocr_data.get('text') or '')}")
print(f"    Extracted Text:\n{(ocr_data.get('text') or '')}")

# 7. Check Workspace API
ws_res = requests.get(f"{BASE_URL}/workspace/cases/{case_id}", headers=headers)
ws_data = ws_res.json()
print(f"[7] Workspace API Result: status={ws_res.status_code}")
print(f"    - Evidence Count: {len(ws_data.get('evidence', []))}")
print(f"    - Custody Count: {len(ws_data.get('custody', []))}")
print(f"    - Timeline Count: {len(ws_data.get('timeline', []))}")
print(f"    - KG Summary Status: {ws_data.get('knowledge_graph', {}).get('status')}")
print(f"    - KG Entity Count: {ws_data.get('knowledge_graph', {}).get('entity_count')}")
print(f"    - KG Entities Sample: {ws_data.get('knowledge_graph', {}).get('entities', [])[:5]}")
print(f"    - AI Findings Count: {len(ws_data.get('ai_findings', []))}")
print(f"    - Progress Completion %: {ws_data.get('progress', {}).get('completion_percent')}%")

# 8. Check Timeline API
tl_res = requests.get(f"{BASE_URL}/timeline?case_id={case_id}", headers=headers)
tl_data = tl_res.json()
print(f"[8] Timeline API Result: total_events={len(tl_data)}")

# 9. Check KG Entities API
kg_res = requests.get(f"{BASE_URL}/kg/entities", headers=headers)
kg_data = kg_res.json()
print(f"[9] KG Entities Result: total_entities={len(kg_data.get('entities', []))}")
