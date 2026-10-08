# CrimeKit Phase 7: Forensic Report Agent & Export Architecture

## Executive Overview
Phase 7 introduces the **Report Agent** to CrimeKit, completing the full lifecycle from multi-specialist investigation and cross-domain correlation to evidence-grounded report compilation, cryptographic hash ledger verification, and deterministic PDF/JSON packaging.

---

## Central Forensic Principle
```
SPECIALISTS INVESTIGATE (Detective, Timeline, GeoScope)
           │
           ▼
CASE ORCHESTRATOR CORRELATES
           │
           ▼
INVESTIGATOR REVIEWS
           │
           ▼
REPORT AGENT PACKAGES
           │
           ▼
FORENSIC REPORT PACKAGE (PDF + JSON + Manifest)
```

> [!IMPORTANT]
> **Legal Admissibility Boundary:** CrimeKit does NOT automatically determine legal admissibility or guilt. Generated certificate sections are explicitly marked:
> `TEMPLATE — REQUIRES AUTHORIZED HUMAN/LEGAL REVIEW`.
> No fake signatures, seals, or jurisdictional compliance claims are fabricated.

---

## Core Components Implemented

### 1. Report Contracts (`backend/app/agents/report_schemas.py`)
- `ReportRequest`: Strictly enforces case-scoping from the authenticated user context.
- `ReportDocument`: Normalized schema holding:
  - Objective & Methodology
  - Findings with preserved provenance (`evidence_refs`, `source_agent`, `status`)
  - `EvidenceIndexItem`: Artifact identifier, size, mime type, exhibit label (`EX-01`).
  - `HashLedgerItem`: Stored intake hash vs recomputed physical file hash (`verified`, `mismatch`, `unavailable`).
  - `TimelineExhibitItem` & `GeospatialExhibitItem`: Preserved timestamps and GPS coordinates.
  - `ContradictionExhibitItem`: Explicitly surfaced investigation discrepancies.
  - `CertificateTemplate`: Human-review declaration template.
  - `ReportPackageManifest`: SHA-256 digests for all generated export bundle files.

### 2. Forensic Report Service (`backend/app/agents/report_service.py`)
- **Hash Ledger & Verification:** Recomputes SHA-256 for physical files; detects tampering if file on disk differs from intake hash.
- **Deterministic PDF Generation:** Utilizes PyMuPDF (`pymupdf`) to produce clean, multi-page vector PDFs with headers, footers, tables, and notices.
- **Manifest Builder:** Computes SHA-256 digests of `report.pdf` and `report.json` to guarantee bundle integrity.

### 3. Report Agent Runtime Integration (`backend/app/agents/runtime.py`)
- `NebiusNemotronRuntime` supports `report` agent natively using centralized model gateway.
- `build_report_prompt` injects verified case context and forensic boundaries.

### 4. Report Routes & Exports (`backend/app/reports_routes.py`)
- `POST /reports`: Compiles report document and persists markdown.
- `GET /reports/{case_id}`: Lists case reports with strict RBAC access checks.
- `GET /reports/{id}/export/pdf`: Downloads generated PyMuPDF PDF.
- `GET /reports/{id}/export/json`: Downloads structured JSON document.
- `GET /reports/{id}/export/zip`: Downloads ZIP package containing PDF, JSON, markdown, and `manifest.json`.

---

## Verification Summary
- **Phase 7 Targeted Tests:** 8/8 passed (`backend/tests/test_phase7_report_agent.py`)
- **Multi-Agent Regression Suite (Phases 2-7):** 57/57 passed
- **Full Backend Suite:** 395/395 passed
- **Frontend TypeScript & Next.js Production Build:** Passed (0 errors)
