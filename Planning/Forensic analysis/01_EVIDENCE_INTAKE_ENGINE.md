
# 01_EVIDENCE_INTAKE_ENGINE.md

# CrimeKit Enterprise Evidence Intake Engine

> Master specification for secure evidence ingestion, validation, chain of custody, classification, storage, and orchestration.

---

# 1. Vision

The Evidence Intake Engine is the trusted gateway into the CrimeKit platform. Every evidence item enters through this engine, is validated, hashed, classified, securely stored, and scheduled for forensic processing while preserving complete chain of custody.

---

# 2. Objectives

- Secure evidence ingestion
- Immutable evidence preservation
- Automated validation
- Intelligent classification
- Explainable routing
- Horizontal scalability
- Court-ready auditability

---

# 3. Responsibilities

- Receive uploads
- Authenticate investigator
- Verify permissions
- Generate evidence identifiers
- Compute SHA-256 hash
- Perform malware scan
- Detect MIME/file type
- Validate metadata
- Detect duplicates
- Preserve originals
- Create chain-of-custody records
- Schedule forensic workers
- Publish intake events

---

# 4. High-Level Workflow

```text
Upload
 ↓
Authentication
 ↓
Authorization
 ↓
Virus Scan
 ↓
Hash Verification
 ↓
Metadata Extraction
 ↓
Classification
 ↓
Duplicate Detection
 ↓
Immutable Storage
 ↓
Chain of Custody
 ↓
Worker Queue
 ↓
Forensic Engines
```

---

# 5. Supported Inputs

- Disk images (E01, RAW, DD)
- Mobile extractions
- Documents
- Images
- Videos
- Audio
- Emails
- Chat exports
- Archives
- Network captures

---

# 6. Folder Structure

```text
evidence-intake/
├── api/
├── services/
├── validators/
├── hash/
├── malware/
├── metadata/
├── classifier/
├── storage/
├── custody/
├── queue/
├── schemas/
└── tests/
```

---

# 7. Processing Stages

1. Request validation
2. User authentication (JWT/RBAC)
3. Upload streaming
4. Size & quota validation
5. SHA-256 hashing
6. Malware scanning
7. MIME detection
8. Metadata extraction
9. Duplicate detection
10. Evidence classification
11. Immutable object storage
12. Database persistence
13. Chain-of-custody event
14. Queue dispatch
15. Investigator notification

---

# 8. Metadata Model

Store:

- evidence_id
- case_id
- investigator_id
- filename
- original_hash
- mime_type
- file_size
- timestamps
- acquisition_source
- upload_device
- processing_status

---

# 9. Duplicate Detection

Compare:

- SHA-256 hash
- File size
- Metadata
- Acquisition identifiers

Duplicates are linked, never overwritten.

---

# 10. Storage Strategy

Original evidence:
- Read-only object storage

Derived artifacts:
- Separate artifact storage

Metadata:
- PostgreSQL

Relationships:
- Neo4j

Embeddings:
- pgvector

---

# 11. Queue Architecture

Redis/Celery queues:

- disk_queue
- mobile_queue
- document_queue
- image_queue
- video_queue
- audio_queue
- email_queue
- chat_queue
- metadata_queue
- timeline_queue

---

# 12. Chain of Custody

Every event records:

- actor
- action
- timestamp
- location
- hash
- previous state
- next state

Events are append-only.

---

# 13. API Contracts

POST /evidence/upload

GET /evidence/{id}

GET /evidence/{id}/status

POST /evidence/{id}/verify

GET /evidence/{id}/custody

---

# 14. Security

- JWT
- RBAC
- TLS
- Encryption at rest
- Immutable originals
- Audit logs
- Rate limiting
- Input validation

---

# 15. Error Handling

Recoverable:
- Temporary storage failures
- Queue outages

Non-recoverable:
- Invalid evidence
- Corrupted uploads
- Authentication failures

---

# 16. Retry Strategy

- Exponential backoff
- Idempotent uploads
- Dead-letter queue
- Supervisor alerts

---

# 17. Observability

Metrics:

- upload latency
- validation time
- queue depth
- duplicate rate
- failed uploads

Logs:

- request_id
- evidence_id
- investigator_id
- status
- duration

---

# 18. Testing

- Upload validation
- Malware scan integration
- Hash verification
- Queue dispatch
- Chain-of-custody integrity
- Large file stress tests
- Security testing

---

# 19. Acceptance Criteria

- All uploads validated
- Original evidence immutable
- Hashes verified
- Chain of custody complete
- Correct worker routing
- Full audit trail
- Production monitoring enabled

---

# 20. Developer Checklist

- Implement streaming upload
- Add hash service
- Integrate malware scanner
- Build classifier
- Configure object storage
- Configure PostgreSQL
- Configure Redis queues
- Persist custody events
- Add APIs
- Write automated tests

---

# Guiding Principle

The Evidence Intake Engine is the foundation of the forensic platform. Every evidence item must enter the system securely, preserve forensic integrity, produce a complete audit trail, and be routed reliably for downstream forensic analysis without altering the original evidence.
