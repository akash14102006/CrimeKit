
# 02_DISK_FORENSICS_ENGINE.md

# CrimeKit Enterprise Disk Forensics Engine

> Production architecture specification for enterprise-grade disk forensic acquisition, parsing, artifact extraction, correlation, and evidence normalization.

---

# 1. Vision

The Disk Forensics Engine processes forensic disk images without modifying the original evidence, extracting structured artifacts suitable for investigators and downstream AI agents.

---

# 2. Objectives

- Forensically sound processing
- Read-only evidence handling
- Modular parser pipeline
- Explainable artifact extraction
- High-performance background execution
- AI-ready normalized outputs
- Court-admissible audit trail

---

# 3. Scope

Supported images:

- E01 / Ex01
- RAW / DD
- AFF4 (future)
- VMDK (read-only)
- VHD / VHDX
- QCOW2 (future)

Supported file systems:

- NTFS
- FAT16/32
- exFAT
- EXT2/3/4
- APFS
- HFS+
- XFS

---

# 4. Folder Structure

```text
disk/
├── acquisition/
├── mount/
├── partitions/
├── filesystem/
├── artifacts/
├── browser/
├── registry/
├── users/
├── recovery/
├── yara/
├── reports/
├── services/
├── schemas/
└── tests/
```

---

# 5. Core Architecture

Upload
→ Verify Hash
→ Mount Read-only
→ Detect Partitions
→ Enumerate File Systems
→ Extract Artifacts
→ Recover Deleted Files
→ Build Timeline
→ Normalize Results
→ Store Artifacts
→ Publish Events

---

# 6. Primary Components

- Image Loader
- Partition Analyzer
- File System Parser
- Registry Analyzer
- Browser Analyzer
- Deleted File Recovery
- Hash Validator
- Timeline Builder
- Artifact Normalizer
- Report Generator

---

# 7. Tool Integrations

Core:

- The Sleuth Kit (TSK)
- libewf
- ewfmount
- mmls
- fls
- icat
- istat

Recovery:

- PhotoRec
- Scalpel
- Foremost

Analysis:

- Bulk Extractor
- YARA

Timeline:

- Plaso
- Timesketch

---

# 8. Extracted Artifacts

- Partition tables
- File listings
- Deleted files
- File hashes
- Registry hives
- User accounts
- Browser history
- Downloads
- Cookies
- USB history
- Shellbags
- Prefetch
- Jump Lists
- Recycle Bin
- LNK files
- Installed programs
- Event logs
- Documents
- Images
- Archives

---

# 9. Unified Artifact Schema

Every artifact includes:

- artifact_id
- evidence_id
- case_id
- source_image
- filesystem
- inode/path
- timestamps
- hash
- parser
- confidence
- provenance

---

# 10. Processing Workflow

1. Validate image
2. Verify checksum
3. Mount read-only
4. Detect partitions
5. Detect filesystem
6. Parse metadata
7. Extract artifacts
8. Recover deleted content
9. Build timeline
10. Normalize
11. Persist
12. Notify supervisor

---

# 11. Database Strategy

PostgreSQL:
- evidence
- artifacts
- timeline
- processing

Neo4j:
- users
- devices
- files
- applications
- events

pgvector:
- semantic embeddings

Object Storage:
- original image
- recovered files
- reports

---

# 12. Security

- Immutable originals
- Read-only mounts
- RBAC
- JWT
- Audit logging
- Encryption
- Secure temp workspace cleanup

---

# 13. Chain of Custody

Record:

- image received
- hash verified
- mounted
- analyzed
- exported
- archived

---

# 14. Performance

- Queue-based execution
- Parallel artifact extractors
- Incremental parsing
- Configurable worker limits

---

# 15. Error Handling

Recoverable:
- parser timeout
- temporary mount failure

Non-recoverable:
- corrupted image
- unsupported filesystem

Dead-letter queue for failed jobs.

---

# 16. Observability

Metrics:

- mount time
- extraction latency
- recovered files
- parser failures
- throughput

Logs:

- request_id
- evidence_id
- worker
- parser
- duration

---

# 17. Testing

- Tool wrapper tests
- Filesystem parser tests
- Recovery validation
- Timeline validation
- Performance benchmarks
- Regression suite

---

# 18. Acceptance Criteria

- Images remain unchanged
- Hashes verified
- Artifacts normalized
- Timeline generated
- Chain of custody complete
- AI-compatible outputs produced

---

# 19. Developer Checklist

- Integrate libewf
- Implement TSK wrappers
- Build registry parser
- Build browser parser
- Configure recovery tools
- Normalize artifacts
- Persist metadata
- Add observability
- Write automated tests

---

# 20. Future Enhancements

- AFF4 support
- BitLocker detection
- APFS snapshots
- Live memory linkage
- Distributed processing
- GPU-assisted file carving

---

# Guiding Principle

The Disk Forensics Engine is the trusted source for storage-device evidence. Every extraction must be deterministic, repeatable, explainable, and forensically sound while producing standardized artifacts for investigators and AI-driven analysis.
