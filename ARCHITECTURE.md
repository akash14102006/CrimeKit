# CrimeKit — Enterprise Architecture & System Blueprint

## Overview
CrimeKit is an enterprise-grade, court-admissible digital forensics investigation and AI intelligence platform. It provides end-to-end evidence ingestion, cryptographic integrity verification, multi-layer forensic artifact extraction, case-scoped AI/RAG reasoning, and immutable blockchain-backed chain of custody logs.

---

## 1. System Architecture Diagram

```
+-------------------------------------------------------------------------------------------------+
|                                        CRIMEKIT CLIENT                                          |
|                     Next.js 16 Static Export (Zoho Catalyst Web Client Hosting)                 |
+-------------------------------------------------------------------------------------------------+
                                                 | HTTPS / WSS
                                                 v
+-------------------------------------------------------------------------------------------------+
|                                    APPLICATION GATEWAY / NGINX                                  |
|                             TLS Termination, Rate Limiting, CORS                                |
+-------------------------------------------------------------------------------------------------+
                                                 |
                                                 v
+-------------------------------------------------------------------------------------------------+
|                                     FASTAPI BACKEND SERVICE                                     |
|                                                                                                 |
|   +-----------------------+   +------------------------+   +--------------------------------+   |
|   |   Auth / RBAC / JWT   |   | Case & Evidence Router |   | Multi-Tenancy / Org Isolation  |   |
|   +-----------------------+   +------------------------+   +--------------------------------+   |
|               |                            |                               |                    |
|   +-----------------------+   +------------------------+   +--------------------------------+   |
|   | Forensic Engine / TSK |   | Streaming Upload Engine|   | Realtime Relay (WebSockets)    |   |
|   +-----------------------+   +------------------------+   +--------------------------------+   |
|               |                            |                               |                    |
|   +-----------------------+   +------------------------+   +--------------------------------+   |
|   | AI Pipeline / RAG     |   | Blockchain Audit Engine|   | Observability & Telemetry (OTel)|  |
|   +-----------------------+   +------------------------+   +--------------------------------+   |
+-------------------------------------------------------------------------------------------------+
       |                     |                       |                         |
       v                     v                       v                         v
+--------------+    +------------------+    +-------------------+    +--------------------+
|  PostgreSQL  |    |  Redis Streams   |    |    Neo4j Graph    |    |  Object Storage    |
| 16+pgvector  |    |  & Pub/Sub       |    | Knowledge Graph   |    | (MinIO / AWS S3)   |
+--------------+    +------------------+    +-------------------+    +--------------------+
```

---

## 2. Core Subsystems

### A. Evidence & Ingestion Subsystem
- **Streaming Upload**: Handles multi-gigabyte forensic disk images (`.raw`, `.dd`, `.E01`, `.vmdk`) without loading files fully into RAM.
- **Integrity Validation**: Computes SHA-256 and MD5 cryptographic hashes on the fly during upload chunk streaming.
- **Pluggable Storage**: Seamlessly switches between local filesystem storage, MinIO (local dev), and AWS S3 with Object Lock (production).

### B. Forensic Processing Engine
- **Sleuth Kit (TSK) Engine**: Partition table parsing (MBR, GPT), filesystem extraction (NTFS, FAT32, EXT4), inode inspection, and timeline reconstruction.
- **Deep Extraction Suite**:
  - Memory dumps (processes, DLLs, network sockets, injected shellcode, registry hives).
  - Network captures (PCAP packet decoding, protocol breakdown).
  - Registry hives (SAM, SYSTEM, SOFTWARE parsing).
  - Windows artifacts (EVTX event logs, Prefetch execution traces, LNK shortcuts).
  - Browser history (Chrome, Firefox, Edge, Safari SQLite artifact parsing).
  - File carving and entropy analysis for hidden or truncated payloads.

### C. Case-Scoped AI & RAG Subsystem
- **Evidence Separation**: Strict separation between immutable forensic truth and AI reasoning. The LLM can never alter evidence files or custody records.
- **Case Isolation**: Every document, chunk, and embedding is scoped by `case_id`. Cross-case leakage is strictly barred at the vector retrieval and SQL layers.
- **Deterministic Fallback**: Provides a zero-external-dependency deterministic embedding provider fallback when external LLM endpoints (OpenAI) are offline or unconfigured.

### D. Cryptographic Chain of Custody & Blockchain Ledger
- **Append-Only Event Ledger**: Every evidence access, download, status change, and forensic result is cryptographically signed and chained.
- **Merkle Tree Anchoring**: Batch commitments are anchored into Merkle trees, ensuring that any single-bit tampering of evidence files or metadata is mathematically detectable.
- **Court Admissibility**: Conforms to ISO/IEC 27037 digital evidence handling standards.

### E. Realtime Event Streaming
- **Redis Pub/Sub & WebSockets**: Status changes in background worker queues (`crimekit:tasks:*`) fan out to connected investigator browsers via `/ws/case/{case_id}` in real-time.
