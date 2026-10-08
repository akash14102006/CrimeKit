# CrimeKit Multi-Agent Investigation Architecture — Phase 6 Documentation

## Overview
Phase 6 implements the **Case Orchestrator** multi-agent coordination architecture in CrimeKit, completing the autonomous cross-specialist investigative loop for the Nebius x NVIDIA AI Hackathon.

The Case Orchestrator receives high-level investigator questions, analyzes the required domains, creates bounded subtasks, delegates them to registered specialist agents (`detective`, `timeline`, `geoscope`), aggregates their findings, identifies contradictions, and synthesizes an evidence-grounded summary.

---

## Target Workflow Architecture

```
                 INVESTIGATOR QUESTION
                           │
                           ▼
                  CASE ORCHESTRATOR
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
     DETECTIVE AGENT  TIMELINE AGENT  GEOSCOPE AGENT
            │              │              │
            ▼              ▼              ▼
     evidence_search  timeline_search location_search
     entity_search    temporal_corr   movement_trace
     knowledge_graph  event_context   co_location
            │              │              │
            └──────────────┼──────────────┘
                           ▼
                  SPECIALIST FINDINGS
                           │
                           ▼
              SHARED INVESTIGATION CONTEXT
              (Fingerprints & Provenance)
                           │
                           ▼
                  CASE ORCHESTRATOR
               (Contradiction Analysis)
                           │
                           ▼
           EVIDENCE-GROUNDED SUMMARY & EXHIBITS
                           │
                           ▼
                 INVESTIGATOR REVIEW
```

---

## Core Components & Contracts

### 1. Orchestration Contracts (`backend/app/agents/orchestration_schemas.py`)
- **`SpecialistAgentTask`**: Structured subtask containing:
  - `task_id`: Unique identifier.
  - `case_id`: Authenticated session case scope.
  - `target_agent`: `detective` | `timeline` | `geoscope`.
  - `objective`: Focused sub-inquiry.
  - `context_refs`: Selective evidence IDs, entities, and locations.
  - `compute_fingerprint()`: Deterministic SHA-256 hash preventing duplicate execution.
- **`SpecialistTaskResult`**: Normalized specialist report with cited evidence refs, findings, tool run logs, and duration.
- **`SharedInvestigationContext`**: State manager tracking entities, evidence IDs, completed task fingerprints, and surfaced contradictions.
- **`RoutingDecision`**: Structured orchestrator decision (`delegate`, `finalize`, `request_more`).
- **`ContradictionItem`**: Explicitly detected conflict across specialists (e.g. `timestamp_gap`).

### 2. Orchestration Service (`backend/app/agents/orchestration_service.py`)
- **`CaseOrchestratorService`**:
  - Implements the bounded coordination loop (`MAX_ORCHESTRATOR_ROUNDS = 4`, `MAX_SPECIALIST_TASKS = 6`, `MAX_TASKS_PER_AGENT = 2`).
  - Emits real-time WebSocket domain events:
    - `orchestration.started`
    - `orchestration.delegated`
    - `orchestration.finding.received`
    - `orchestration.contradiction.detected`
    - `orchestration.completed`
  - Bounded duplicate prevention: Skips repeated tasks matching identical fingerprints.
  - Contradiction detection: Cross-references timeline timestamps against geospatial fixes to flag temporal gaps.

### 3. Prompt Engineering (`backend/app/agents/orchestrator_prompt.py`)
- Instructs NVIDIA Nemotron to operate in strategic, objective orchestrator mode.
- Enforces strict rules:
  1. *"AI coordinates, AI correlates, AI explains, AI cites, AI shows uncertainty. Investigator decides."*
  2. Never claim guilt or reach judicial conclusions.
  3. Never fabricate evidence or specialist outputs.
  4. Preserve device vs. person distinctions.
  5. Select the minimum sufficient set of specialists.

---

## Security & Case Isolation
- **Case Scoping**: Delegated tasks strictly inherit the authenticated session `case_id`. Any attempt by the model or parameters to override `case_id` is automatically stripped.
- **No Direct Data Access**: The Case Orchestrator never directly queries Postgres, Neo4j, or filesystems; it only delegates to authorized specialist runtimes.
- **Recursion Prevention**: The Case Orchestrator cannot delegate to itself, and specialists cannot autonomously delegate to other specialists.

---

## Verification & Test Results
- **Phase 6 Suite**: 8/8 passed (`backend/tests/test_phase6_case_orchestrator.py`)
  - `test_task_fingerprint_and_duplicate_prevention`
  - `test_routing_decision_validation`
  - `test_contradiction_detection`
  - `test_single_specialist_selective_routing`
  - `test_primary_three_agent_orchestration_flow`
  - `test_dual_specialist_timeline_and_geoscope`
  - `test_duplicate_task_prevention`
  - `test_orchestrator_case_isolation`
- **Phase 5 Suite**: 16/16 passed (`backend/tests/test_phase5_timeline_geoscope_tools.py`)
- **Phase 4 Suite**: 9/9 passed (`backend/tests/test_phase4_detective_tools.py`)
- **Nebius Gateway Suite**: 10/10 passed (`backend/tests/test_nebius_nemotron_gateway.py`)
- **Full Backend Regression Suite**: 387/387 passed (`pytest backend/tests -q`)
- **Frontend TypeScript Check**: 0 errors (`npx tsc --noEmit`)

---

## What is NOT Implemented (Out of Scope)
- Tavily web search
- NemoClaw / OpenShell sandboxing
- NeMo Agent Toolkit
- Autonomous infinite delegation loops
- Court-admissible PDF export (Phase 7)
