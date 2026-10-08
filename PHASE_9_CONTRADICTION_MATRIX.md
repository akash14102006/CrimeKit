# PHASE 9 — Interactive Contradiction Matrix & Evidence Verification Workspace

## Executive Overview
Phase 9 delivers the **Interactive Contradiction Matrix** and **Evidence Verification Workspace** for CrimeKit. It provides investigators with an interactive forensic audit environment where claims extracted from witness depositions and interrogation transcripts are cross-checked against immutable digital evidence records (Call Detail Records, tower sector registrations, GPS breadcrumbs, and subscriber registries).

### Critical Legal & Ethical Principle
> **AI correlates evidence and computes deterministic discrepancies; the investigator makes the investigative decisions.**
> CrimeKit does NOT evaluate witness mendacity or declare guilt. It calculates temporal, spatial, sequence, and identity deltas and flags them for human review.

---

## Architectural Workflow

```
                        INVESTIGATOR
                             │
                             ▼
                    CASE ORCHESTRATOR
                             │
       ┌───────────┬─────────┴─────────┬───────────┐
       ▼           ▼                   ▼           ▼
   Detective    Timeline            GeoScope   Testimony
       │           │                   │           │
       └───────────┼───────────────────┼───────────┘
                   │                   │
                   ▼                   ▼
                     CONTRADICTION ENGINE
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
       CONTRADICTION MATRIX          EVIDENCE VERIFICATION
                 │                           │
                 └─────────────┬─────────────┘
                               ▼
                      INVESTIGATOR REVIEW
                    [Confirm / Dismiss / Unresolved]
                               │
                               ▼
                     APPEND-ONLY AUDIT TRAIL
                               │
                               ▼
                   EVIDENCE VERIFICATION PACKAGE
                  (report.pdf, matrix.json, manifest.json)
```

---

## Core Components

### 1. Deterministic Contradiction Engine (`backend/app/agents/contradiction_service.py`)
Rather than relying on non-deterministic LLM calculations, contradictions are computed deterministically with dedicated Python logic:
- **Temporal Contradiction:** Computes exact deltas in seconds and minutes between statement assertions and CDR / transaction timestamps. Severity scales based on delta magnitude (`medium`, `high`, `critical`).
- **Geographic Contradiction:** Computes spatial displacement using the Haversine formula between claimed landmarks and recorded cell tower / GPS coordinates. Enforces: *device location does not equal person location*.
- **Sequence Contradiction:** Detects chronological inversions where a claimed sequence ($A \to B$) is disproven by verified event timestamps ($B$ prior to $A$).
- **Identity Contradiction:** Cross-checks attributed ownership against subscriber registries.

### 2. Contradiction Matrix & Review Workflow
- **Matrix Representation (`ContradictionMatrixRow`):** Rows represent claims; columns track evidence links, conflict descriptions, severity, confidence, and current review status.
- **Review Actions:**
  - `confirmed`: The investigator independently validated the discrepancy.
  - `dismissed`: The discrepancy was reviewed and determined to be non-actionable or explained.
  - `unresolved`: Insufficient evidence exists to resolve the conflict.
- **Append-Only Audit Trail (`ReviewAuditTrailItem`):** Preserves immutable history with timestamps, reviewer ID, prior status, new status, and investigator notes.
- **WebSocket Events:** Dispatches `contradiction.detected`, `contradiction.review.updated`, and `review.package.generated`.

### 3. Evidence Verification Panel & Provenance Chain
- **Cryptographic SHA-256 Verification:** Verifies storage hashes against live filesystem hashes; surfaces `VERIFIED`, `MISMATCH`, or `UNAVAILABLE` without silently modifying source records.
- **Provenance Lineage:** Traces each record through:
  $$\text{Evidence Intake} \to \text{Chain of Custody} \to \text{Forensic Extraction} \to \text{Specialist Analysis} \to \text{Contradiction Flagged} \to \text{Report Exhibit}$$

### 4. Evidence Verification Package
Exports a complete `crimekit-evidence-review-{caseId}.zip` bundle:
```
crimekit-evidence-review/
├── manifest.json            # Real SHA-256 digests of all package files
├── report.pdf               # Comprehensive forensic report
├── report.json              # Structured report document
├── contradiction-matrix.json # Complete contradiction matrix
├── review-history.json      # Append-only investigator review audit log
├── evidence-index.json      # Cryptographic evidence index
├── hash-ledger.json         # SHA-256 verification ledger
└── exhibits/
    ├── timeline.json        # Timeline exhibits
    ├── testimony.json       # Witness claims and cross-checks
    └── contradictions.json  # Preserved contradiction items
```

---

## Frontend Integration (`ContradictionMatrixPanel.tsx`)
- Integrated directly into the **AI Investigation Workspace** as a dedicated `Matrix` side-tab.
- Features:
  - KPI summary badges: Needs Review, Confirmed, Dismissed, Unresolved.
  - Type filters (`temporal`, `geographic`, `identity`, `sequence`) and status filters.
  - Split-screen comparison: Left panel shows verbatim witness statement; Right panel shows digital evidence records.
  - 1-click investigator review actions with rationales.
  - Interactive evidence verification drawer with SHA-256 status and provenance chain.
  - One-click export of the complete Evidence Verification Package.

---

## Verification & Test Results
- **Phase 9 Test Suite:** 9/9 passed (`backend/tests/test_phase9_contradiction_matrix.py`)
- **Multi-Agent Regression (Phases 4–9):** 59/59 passed
- **Next.js Production Build:** 0 errors (TypeScript check passed)
