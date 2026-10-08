# PHASE 8 — Testimony Agent & Evidentiary Cross-Check Pipeline

## Executive Overview
Phase 8 introduces the **Testimony Agent** (`testimony`) to CrimeKit's multi-agent digital forensics suite. The agent performs structured factual decomposition and cross-checks of witness statements, interrogation records, and depositions against verified physical and digital evidence (call detail records, cell tower pings, GPS waypoints, and timeline events).

### Non-Negotiable Forensic Principle
> **CrimeKit identifies evidence inconsistencies; it does NOT determine whether a person is lying.**
> The Testimony Agent decomposes witness narratives into structured propositions and cross-checks those propositions against verified timeline events and geospatial telemetry. The investigator remains the sole decision-maker.

---

## Architecture & Integration

```
                           Investigator
                                │
                                ▼
                        Case Orchestrator
                                │
       ┌───────────┬────────────┼────────────┬───────────┐
       ▼           ▼            ▼            ▼           ▼
   Detective    Timeline     GeoScope    Testimony    Report
       │           │            │            │           │
       └───────────┴────────────┴────────────┴───────────┘
                                │
                                ▼
                    SharedInvestigationContext
                                │
                                ▼
                       Verified Findings
                                │
                                ▼
                          Report Agent
```

### Centralized Runtime
- **Runtime:** `NebiusNemotronRuntime` via the centralized model gateway (`NVIDIA Nemotron` on Nebius).
- **Execution Mode:** Bounded multi-turn tool calling with fallback heuristics and deterministic offline cross-checking.
- **Agent ID:** `testimony`.
- **System Prompt:** Configured in `backend/app/agents/testimony_prompt.py` and `backend/app/agents/specialist_prompts.py` (`build_testimony_prompt()`).

---

## Core Capabilities

1. **Claim Extraction (`claim-extraction`):**
   - Decomposes free-text narrative statements into structured semantic triples:
     - `subject`
     - `predicate`
     - `object`
     - `timestamp` / `time_range`
     - `location`
     - `entity_refs`
     - `source_ref` (witness ID, document citation, page/offset)
     - `confidence` (analytical extraction confidence)
     - `status` (`supported`, `contradicted`, `partially_supported`, `unresolved`, `needs_review`)

2. **Temporal Cross-Check (`testimony-timeline-crosscheck`):**
   - Matches claimed times against timeline events (CDR, network logs, security events).
   - Flag discrepancies with exact millisecond/second deltas and associated evidence IDs without asserting fabrication.

3. **Geographic Cross-Check (`testimony-location-crosscheck`):**
   - Correlates claimed locations with GeoScope waypoints and cell sectors.
   - Strictly enforces that **device location does not equal person location** unless independently corroborated.

4. **Entity Resolution (`testimony-entity-resolution`):**
   - Maps referenced persons and aliases against case entity records and phone numbers.

5. **Alibi Verification (`alibi-verification`):**
   - Structured verification over claimed temporal intervals (`claimed_start` to `claimed_end`).
   - Categorizes evidence into `supporting_events`, `conflicting_events`, and coverage `gaps`.

6. **Contradiction Analysis (`contradiction-analysis`):**
   - Taxonomy: `TEMPORAL`, `GEOGRAPHIC`, `IDENTITY`, `EVENT`, `SEQUENCE`.
   - Severity: `low`, `medium`, `high`, `critical`.
   - Severity denotes the evidentiary divergence, not personal mendacity.

---

## Schemas & Contracts

### `ClaimContract` (`backend/app/agents/testimony_schemas.py`)
```json
{
  "claim_id": "CLM-001",
  "case_id": "CASE-2026-001",
  "testimony_id": "TEST-001",
  "witness_id": "WIT-01",
  "statement_text_reference": "I was at the shop near the railway station at 9:15 PM when Rahul called me.",
  "subject": "Witness A",
  "predicate": "was_at_location",
  "object": "Shop near railway station",
  "timestamp": "2026-03-31T21:15:00Z",
  "location": "Railway Station Market",
  "entity_refs": ["Rahul", "Witness A"],
  "source_ref": "EV-205 (Interview Transcript p. 2)",
  "confidence": 0.88,
  "status": "needs_review"
}
```

### `ContradictionContract` (`backend/app/agents/testimony_schemas.py`)
```json
{
  "contradiction_id": "CT-001",
  "case_id": "CASE-2026-001",
  "claim_id": "CLM-002",
  "contradiction_type": "temporal",
  "severity": "high",
  "statement_claim": "Rahul called witness at 21:00",
  "evidence_record": "CDR records incoming call from Rahul at 21:14 (EV-104)",
  "evidence_refs": ["EV-104"],
  "temporal_delta_seconds": 840,
  "status": "needs_review",
  "reasoning": "Statement indicates call at 21:00, but call detail records (EV-104) show call at 21:14:00."
}
```

---

## Orchestrator & Report Integration

1. **Orchestrator Routing:**
   - Case Orchestrator (`backend/app/agents/orchestration_service.py`) routes witness, testimony, interview, alibi, and statement cross-check requests directly to `testimony`.
   - The Orchestrator collects structured testimony findings and incorporates them into `SharedInvestigationContext`.

2. **Report Agent Integration:**
   - `ReportDocument` in `backend/app/agents/report_schemas.py` includes `testimony_exhibits`.
   - `ReportService` formats witness statements, extracted claims, temporal/geographic cross-checks, and alibi coverage tables into court-ready markdown reports.

---

## Security & Case Isolation
- **Tenant & Case Scoping:** All operations strictly require and validate `case_id`. Evidence, timeline events, or entities belonging to other cases cannot be accessed or compared.
- **Controlled Tool Execution:** Only approved investigation tools are accessible. No raw Cypher, raw SQL, shell execution, or unrestricted HTTP access.

---

## Verification Summary
- **Phase 8 Tests:** 9/9 passed (`backend/tests/test_phase8_testimony_agent.py`)
- **Full Phase 3–8 Multi-Agent Test Suite:** 60/60 passed
- **Full Backend Tests (Unit & Integration):** 401/401 passed (excluding mocked KG standalone suite)
- **Frontend Build & TypeScript Validation:** 0 errors (Next.js 16 production build succeeded)
