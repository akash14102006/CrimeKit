
# 04_REPORTS_SERVICES.md

# CrimeKit Backend – Reports & Service Layer Architecture
**Modules:** `backend/reports/` + `backend/services/`

---

# 1. Purpose

This document defines the architecture for the Report Generation module and the shared Service Layer.

The Report module transforms investigation data into structured, explainable, court-ready reports.

The Service Layer contains the core business logic of CrimeKit. Every module (Authentication, Cases, Evidence, Uploads, AI, Reports) communicates through services rather than directly interacting with databases or other modules.

---

# 2. Design Philosophy

- Thin API Layer
- Rich Service Layer
- Reusable Business Logic
- Explainable AI Outputs
- Human-in-the-loop Reporting
- Modular Components
- Dependency Injection
- Event-driven Workflows
- Production-ready Architecture

---

# 3. Folder Structure

```text
backend/

reports/
├── api/
├── services/
├── repositories/
├── generators/
├── exporters/
├── templates/
├── ai_summary/
├── models/
├── schemas/
└── utils/

services/
├── auth_service.py
├── case_service.py
├── evidence_service.py
├── upload_service.py
├── forensic_service.py
├── ai_service.py
├── graph_service.py
├── search_service.py
├── report_service.py
├── notification_service.py
└── audit_service.py
```

---

# 4. Responsibilities

## Report Module

Responsible for:

- Investigation summaries
- Evidence summaries
- AI findings
- Timeline summaries
- Knowledge graph summaries
- Court-ready reports
- Executive reports
- PDF generation
- DOCX generation
- JSON export

---

## Service Layer

Responsible for:

- Business rules
- Cross-module orchestration
- Validation
- Transaction management
- Workflow coordination
- Domain logic
- AI orchestration
- Search orchestration

The Service Layer never exposes HTTP endpoints.

---

# 5. Report Types

- Investigation Report
- Evidence Report
- Chain of Custody Report
- AI Findings Report
- Timeline Report
- Entity Relationship Report
- GeoScope Report
- Executive Summary
- Court Submission Package
- Audit Report

---

# 6. Report Pipeline

```text
Case

↓

Evidence

↓

Forensic Artifacts

↓

Knowledge Graph

↓

Timeline

↓

AI Correlation

↓

Human Review

↓

Report Generator

↓

PDF / DOCX / JSON
```

---

# 7. Court Report Structure

Each report includes:

- Cover Page
- Case Details
- Investigator Details
- Evidence Inventory
- Chain of Custody
- Timeline
- AI Findings
- Human Verification Notes
- References
- Digital Signature
- Appendix

---

# 8. Service Layer Architecture

```text
API

↓

Service

↓

Repository

↓

Database / Storage

↓

Response
```

Services communicate with repositories—not directly with SQL.

---

# 9. Cross-Service Communication

Services may collaborate:

- Case Service
- Evidence Service
- Upload Service
- AI Service
- Graph Service
- Report Service
- Audit Service

Avoid circular dependencies.

---

# 10. AI Report Generation

AI contributes:

- Investigation summary
- Entity correlation
- Timeline explanation
- Pattern explanation
- Confidence score
- Recommendation

AI never produces the final legal conclusion.

---

# 11. Export Formats

Supported exports:

- PDF
- DOCX
- HTML
- JSON
- CSV (selected datasets)

---

# 12. Report Security

- Authorized users only
- Watermark support
- Immutable generated reports
- Digital signatures (future)
- Version history
- Audit every download

---

# 13. Error Handling

Handle:

- Missing evidence
- Incomplete investigation
- Export failure
- AI timeout
- Template failure
- Storage failure

Every failure is logged.

---

# 14. Performance Goals

- Asynchronous generation
- Queue long reports
- Background exports
- Cache reusable summaries
- Stream large reports

---

# 15. Acceptance Criteria

Reports:

- Generated successfully
- Human-readable
- Court-ready
- Explainable
- Exportable

Services:

- No duplicated business logic
- Fully reusable
- Independently testable
- Dependency injected

---

# 16. Developer Rules

- APIs never contain business logic.
- Services never contain HTTP code.
- Repositories never contain business rules.
- AI outputs must always be reviewable.
- Every report must reference its originating Case and Evidence.

---

# 17. Guiding Principle

The Service Layer is the business brain of CrimeKit.

The Report Module transforms verified investigative knowledge into professional, explainable, and legally defensible documentation while maintaining complete traceability from evidence to final report.
