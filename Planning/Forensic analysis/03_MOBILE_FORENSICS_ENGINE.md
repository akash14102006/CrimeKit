
# 03_MOBILE_FORENSICS_ENGINE.md

# CrimeKit Enterprise Mobile Forensics Engine

> Enterprise architecture specification for secure acquisition processing, artifact extraction, normalization, and intelligence generation from Android and iOS evidence.

---

# 1. Vision

Provide a scalable, forensically sound mobile analysis engine that transforms mobile evidence into normalized, explainable artifacts for investigators and AI agents while preserving evidence integrity.

---

# 2. Objectives

- Read-only forensic processing
- Platform-independent architecture
- Structured artifact extraction
- Timeline reconstruction
- Cross-app correlation
- AI-ready outputs
- Court-ready audit trail

---

# 3. Supported Sources

## Android
- Full filesystem extraction
- Logical extraction
- Backup extraction
- ADB exports
- ALEAPP outputs

## iOS
- iTunes backups
- Filesystem extraction
- Logical extraction
- Future full support for encrypted backups

---

# 4. Folder Structure

```text
mobile/
├── acquisition/
├── android/
├── ios/
├── sqlite/
├── apps/
├── media/
├── location/
├── timeline/
├── artifacts/
├── reports/
├── services/
├── schemas/
└── tests/
```

---

# 5. Architecture

Evidence Intake
→ Validation
→ Device Detection
→ Platform Detection
→ SQLite Parsing
→ App Parsers
→ Media Extraction
→ Timeline Builder
→ Artifact Normalization
→ Knowledge Graph
→ AI Platform

---

# 6. Core Modules

- Device Analyzer
- SQLite Parser
- App Parser Manager
- Media Analyzer
- Location Analyzer
- Contact Analyzer
- Timeline Builder
- Artifact Normalizer
- Report Generator

---

# 7. Tool Integrations

- ALEAPP
- SQLite
- libplist
- ExifTool
- FFmpeg
- OCR
- Whisper
- YARA (optional)

---

# 8. Supported Applications

- WhatsApp
- Telegram
- Signal
- SMS
- Contacts
- Call Logs
- Chrome
- Photos
- Camera
- Calendar
- Notes
- Files

---

# 9. Extracted Artifacts

- Device information
- Installed apps
- Accounts
- Contacts
- SMS
- MMS
- Call history
- Chats
- Attachments
- Photos
- Videos
- Audio
- GPS locations
- Wi-Fi history
- Bluetooth devices
- Browser history
- Downloads
- Notifications
- Calendar events

---

# 10. Unified Artifact Schema

Fields:
- artifact_id
- evidence_id
- device_id
- app_name
- category
- timestamp
- source_database
- extracted_data
- confidence
- provenance
- hash

---

# 11. Processing Workflow

1. Validate extraction
2. Identify platform
3. Parse filesystem
4. Parse SQLite databases
5. Extract application data
6. Recover media metadata
7. Build unified timeline
8. Normalize artifacts
9. Persist data
10. Notify Supervisor

---

# 12. Storage Strategy

PostgreSQL:
- device metadata
- parsed artifacts
- processing status

Neo4j:
- people
- devices
- conversations
- locations

pgvector:
- semantic embeddings

Object Storage:
- original extraction
- recovered media
- exported reports

---

# 13. Security

- Immutable evidence
- Read-only processing
- JWT & RBAC
- Audit logging
- Encryption
- Secure temporary workspace cleanup

---

# 14. Chain of Custody

Track:
- acquisition
- upload
- parsing
- artifact extraction
- export
- archive

---

# 15. Performance

- Parallel app parsers
- Queue-based workers
- Incremental parsing
- Large database streaming

---

# 16. Error Handling

Recoverable:
- parser failure
- unsupported app version
- temporary I/O failure

Non-recoverable:
- corrupted extraction
- invalid backup

Dead-letter queue for failed jobs.

---

# 17. Observability

Metrics:
- apps parsed
- SQLite parse time
- artifact count
- worker latency
- failure rate

Structured Logs:
- request_id
- evidence_id
- device_id
- parser
- duration
- outcome

---

# 18. Testing

- SQLite parser tests
- App parser validation
- Timeline consistency
- Large extraction benchmarks
- Regression tests

---

# 19. Acceptance Criteria

- Evidence remains unchanged
- Mobile artifacts normalized
- Timeline generated
- Chain of custody complete
- AI-ready structured outputs available

---

# 20. Developer Checklist

- Integrate ALEAPP
- Build SQLite framework
- Implement app parsers
- Normalize artifacts
- Persist metadata
- Configure queues
- Add monitoring
- Write automated tests

---

# 21. Future Enhancements

- Full iOS encrypted backup support
- Cloud backup parsing
- Wearable device artifacts
- Mobile malware detection
- Cross-device correlation

---

# Guiding Principle

The Mobile Forensics Engine transforms complex mobile evidence into trusted, standardized, and explainable investigative artifacts while preserving forensic integrity and enabling scalable AI-assisted investigations.
