# 03_EVIDENCE_UPLOADS.md

# CrimeKit Backend – Evidence Management & Upload Pipeline
**Module:** backend/evidence + backend/uploads

---

# 1. Purpose

This document defines the complete architecture for evidence ingestion, secure storage, validation, chain of custody, metadata extraction, and upload orchestration.

Evidence Management is the core domain of CrimeKit. Every uploaded item becomes trusted digital evidence that can be processed by the forensic engine and AI platform.

The system must preserve integrity, traceability, explainability, and legal defensibility.

---

# 2. Module Responsibilities

## evidence/

Responsible for:

- Evidence registration
- Evidence metadata
- Evidence lifecycle
- Chain of custody
- Relationships
- Hash verification
- Permissions
- Status tracking
- Evidence search

## uploads/

Responsible for:

- Large file uploads
- Chunk uploads
- Upload resume
- Upload validation
- Malware scanning trigger
- MinIO storage
- Workflow trigger

Uploads never perform forensic analysis.

---

# 3. Supported Evidence Types

- Disk Images (E01, DD, IMG)
- Android/iOS Extractions
- Documents (PDF, DOCX, XLSX)
- Images (JPG, PNG)
- Videos (MP4, AVI)
- Audio
- Email (PST, MSG, EML)
- Chat Exports
- Browser History
- PCAP
- ZIP / TAR archives

---

# 4. Folder Structure

```text
backend/
├── evidence/
│   ├── api/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   ├── schemas/
│   ├── custody/
│   ├── metadata/
│   └── search/
│
├── uploads/
│   ├── api/
│   ├── services/
│   ├── validators/
│   ├── storage/
│   ├── scanners/
│   └── workers/
```

---

# 5. Evidence Lifecycle

```text
Uploaded
 ↓
Validated
 ↓
SHA-256 Generated
 ↓
Stored in MinIO
 ↓
Metadata Registered
 ↓
Chain of Custody Created
 ↓
Queued for Forensic Processing
 ↓
Artifacts Extracted
 ↓
Available for Investigation
 ↓
Archived
```

---

# 6. Upload Pipeline

```text
Investigator

↓

Upload API

↓

File Validation

↓

Virus Scan

↓

SHA-256 Hash

↓

Store in MinIO

↓

Save Metadata (PostgreSQL)

↓

Create Chain of Custody

↓

Trigger Temporal Workflow

↓

Forensic Engine
```

---

# 7. Chain of Custody

Every evidence item records:

- Evidence ID
- Case ID
- Uploaded By
- Upload Time
- SHA-256 Hash
- Storage Location
- Access History
- Download History
- Status Changes

No custody record is editable.

---

# 8. Metadata

Store:

- Original filename
- MIME type
- Size
- Extension
- Upload source
- Device information (when available)
- Geographic metadata (if present)
- Extraction status
- Processing status

---

# 9. Storage Strategy

Binary files:

- MinIO Object Storage

Metadata:

- PostgreSQL

Relationships:

- Neo4j

Search:

- Elasticsearch

Semantic retrieval:

- pgvector

---

# 10. Validation Rules

Reject:

- Unsupported extensions
- Corrupted files
- Empty uploads
- Oversized uploads
- Invalid MIME types

Every upload receives a SHA-256 integrity hash.

---

# 11. Security

- Authenticated uploads only
- Case-level authorization
- Size limits
- Audit every access
- Immutable evidence records
- Secure object storage
- Signed download URLs (future)

---

# 12. APIs

Evidence APIs:

- Create
- Get
- Update metadata
- Search
- List by case
- Lock
- Archive

Upload APIs:

- Start upload
- Upload chunk
- Resume upload
- Complete upload
- Cancel upload
- Verify integrity

---

# 13. Integration

Evidence integrates with:

- Cases
- Reports
- Temporal
- MinIO
- PostgreSQL
- Neo4j
- Elasticsearch
- LangGraph
- Forensic Engine

---

# 14. Error Handling

Common failures:

- Upload interrupted
- Hash mismatch
- Storage unavailable
- Invalid file
- Duplicate evidence
- Permission denied

Errors are logged with Request ID and Evidence ID.

---

# 15. Acceptance Criteria

The module is complete when:

- Large files upload reliably
- Hashes are generated
- Evidence stored in MinIO
- Metadata stored in PostgreSQL
- Chain of custody created
- Workflow automatically triggered
- Audit logs recorded

---

# 16. Developer Checklist

- Never modify stored evidence
- Never bypass integrity verification
- Always generate SHA-256
- Always create custody record
- Validate every upload
- Store only metadata in PostgreSQL
- Store binary data in MinIO
- Trigger workflows asynchronously

---

# 17. Guiding Principle

Every uploaded file becomes trusted digital evidence.

The upload pipeline guarantees integrity, traceability, security, and readiness for forensic investigation while keeping the backend scalable and production-ready.
