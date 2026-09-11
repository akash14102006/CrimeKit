
# 00_FORENSIC_ENGINE_ARCHITECTURE.md

# CrimeKit Enterprise Forensic Engine Architecture

> Master architecture specification for the CrimeKit Forensic Engine. This document defines the overall design, responsibilities, processing pipeline, data flow, scalability strategy, security model, and implementation standards for all forensic subsystems.

---

# 1. Vision

Build a production-grade forensic processing platform capable of ingesting heterogeneous digital evidence, extracting normalized forensic artifacts, preserving chain of custody, enriching investigation intelligence, and supplying validated evidence to the AI investigation platform.

---

# 2. Objectives

- Enterprise scalability
- Explainable forensic processing
- Modular processing engines
- Immutable evidence handling
- Tool-agnostic architecture
- AI-ready structured artifacts
- Court-ready auditability

---

# 3. High-Level Architecture

```text
Investigator
    │
Evidence Intake
    │
Validation → Hash → Malware Scan
    │
Classification Engine
    │
┌──────────────────────────────────────────┐
│ Documents │ Disk │ Mobile │ Images │     │
│ Videos │ Audio │ Email │ Chats │ Metadata│
└──────────────────────────────────────────┘
    │
Artifact Normalization
    │
Entity Extraction
    │
Timeline Reconstruction
    │
Knowledge Graph + Search + Vectors
    │
LangGraph Supervisor
    │
AI Investigation Agents
    │
Court-ready Outputs
```

---

# 4. Folder Structure

```text
forensic-engine/
├── disk/
├── mobile/
├── documents/
├── images/
├── videos/
├── audio/
├── email/
├── chats/
├── metadata/
├── timeline/
└── workers/
```

---

# 5. Core Components

## Evidence Intake
Receives uploads, validates integrity, records chain of custody and dispatches background jobs.

## Processing Engines
Dedicated forensic modules for each evidence category.

## Artifact Normalization
Converts outputs from different forensic tools into a unified schema.

## Intelligence Layer
Entity extraction, timeline building, semantic indexing and graph enrichment.

## AI Integration
Provides structured evidence to LangGraph agents through typed APIs.

---

# 6. Supported Evidence

- E01 / DD / RAW images
- Android extractions
- PDF, DOCX, XLSX, CSV
- PST, MSG, EML
- JPG, PNG, TIFF
- MP4, AVI
- MP3, WAV
- WhatsApp exports
- Telegram exports
- Browser history
- PCAP
- ZIP archives

---

# 7. Processing Pipeline

1. Upload
2. SHA-256 verification
3. Malware scan
4. Metadata extraction
5. Evidence classification
6. Queue creation
7. Worker execution
8. Artifact normalization
9. Entity extraction
10. Timeline reconstruction
11. Knowledge graph enrichment
12. Search indexing
13. Vector embedding
14. AI consumption

---

# 8. Tool Integrations

Disk:
- The Sleuth Kit
- libewf
- Bulk Extractor
- PhotoRec

Mobile:
- ALEAPP

Documents:
- Apache Tika
- OCR

Media:
- FFmpeg
- Whisper
- ExifTool

Timeline:
- Plaso
- Timesketch

---

# 9. Data Layer

PostgreSQL
- cases
- evidence
- artifacts
- audit logs

Neo4j
- entities
- relationships
- events

pgvector
- semantic embeddings

Search
- Elasticsearch/OpenSearch

Object Storage
- immutable original evidence

---

# 10. Worker Architecture

Dedicated asynchronous workers:

- Disk Worker
- Mobile Worker
- Document Worker
- Image Worker
- Video Worker
- Audio Worker
- Email Worker
- Chat Worker
- Metadata Worker
- Timeline Worker

Workers communicate through Redis-backed queues and return standardized artifact packages.

---

# 11. Unified Artifact Schema

Every module emits:

- artifact_id
- case_id
- evidence_id
- source_tool
- timestamps
- extracted_entities
- metadata
- confidence
- provenance
- hash
- citations

---

# 12. Security

- RBAC
- JWT authentication
- Immutable evidence
- Encryption at rest
- Encryption in transit
- Audit logging
- Prompt injection protection for AI interfaces

---

# 13. Chain of Custody

Every evidence item records:

- acquisition
- upload
- processing
- access
- export

Each event is timestamped and auditable.

---

# 14. RAG & Knowledge Graph

Normalized artifacts feed:

- Neo4j
- Vector database
- Search index

This enables explainable AI responses with evidence references.

---

# 15. Observability

Metrics:
- processing latency
- queue depth
- worker success rate
- extraction coverage
- tool failures

Logs:
- request_id
- case_id
- worker
- tool
- execution time
- outcome

---

# 16. Scalability

- Stateless processing workers
- Horizontal autoscaling
- Independent module deployment
- Queue-based orchestration
- GPU-enabled AI services

---

# 17. Testing Strategy

- Unit tests per engine
- Integration tests for tool wrappers
- End-to-end evidence workflows
- Performance benchmarks
- Regression tests

---

# 18. Acceptance Criteria

The forensic engine is production-ready when:

- All supported evidence types process successfully.
- Outputs conform to the unified artifact schema.
- Chain of custody is preserved.
- AI agents receive normalized artifacts.
- Security and audit requirements pass.
- Monitoring and logging are operational.

---

# 19. Developer Checklist

- Define module interfaces
- Implement tool adapters
- Normalize artifacts
- Configure queues
- Persist artifacts
- Integrate Neo4j
- Integrate vector search
- Add monitoring
- Add automated tests
- Validate enterprise deployment

---

# 20. Roadmap

01_EVIDENCE_INTAKE_ENGINE.md

02_DISK_FORENSICS_ENGINE.md

03_MOBILE_FORENSICS_ENGINE.md

04_DOCUMENT_INTELLIGENCE_ENGINE.md

05_IMAGE_FORENSICS_ENGINE.md

06_VIDEO_FORENSICS_ENGINE.md

07_AUDIO_FORENSICS_ENGINE.md

08_EMAIL_FORENSICS_ENGINE.md

09_CHAT_FORENSICS_ENGINE.md

10_METADATA_INTELLIGENCE_ENGINE.md

11_TIMELINE_RECONSTRUCTION_ENGINE.md

12_FORENSIC_WORKER_ORCHESTRATION.md

13_FORENSIC_DEPLOYMENT.md

---

# Guiding Principle

The Forensic Engine is the trusted evidence processing foundation of CrimeKit. Every module must preserve forensic integrity, produce explainable structured artifacts, scale independently, and provide reliable inputs for investigator workflows and AI-assisted analysis.
