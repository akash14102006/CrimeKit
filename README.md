# CrimeKit — Digital Forensics & Multi-Agent Investigation Platform

> **Nebius × NVIDIA Global AI Hackathon (Best Apps & Agents Track)**  
> Evidence-grounded, multi-agent AI forensic analysis powered by **NVIDIA Nemotron** on **Nebius Token Factory**, equipped with deterministic contradiction detection, human investigator review, and tamper-evident case sealing.

---

## The Problem
Digital investigations are severely fragmented across siloed forensic sources: call detail records (CDR), cellular tower pings, GPS telemetry, witness depositions, and disk images. Forensic analysts spend days manually correlating timestamps across incompatible artifacts. Meanwhile, conventional LLM wrappers hallucinate facts, fail at temporal arithmetic, and risk legal compromise by claiming to "detect lies" or "determine guilt."

## The Solution
**CrimeKit** bridges deep digital forensics and autonomous multi-agent systems:
1. **Case Orchestrator** decomposes complex investigative questions into specialist agent subtasks.
2. **Specialist Agents** ([Detective](file:///Users/buvanrajv/Projects/CrimeKit/backend/app/agents/tools/detective_tool.py), [Timeline](file:///Users/buvanrajv/Projects/CrimeKit/backend/app/agents/tools/timeline_tool.py), [GeoScope](file:///Users/buvanrajv/Projects/CrimeKit/backend/app/agents/tools/geoscope_tool.py), [Testimony](file:///Users/buvanrajv/Projects/CrimeKit/backend/app/agents/testimony_service.py)) execute controlled, bounded tools over verified evidence.
3. **Deterministic Contradiction Engine** computes mathematical temporal deltas, Haversine geospatial distances, and sequence inversions using code—not LLM arithmetic.
4. **Interactive Contradiction Matrix** empowers human investigators to review, confirm, or dismiss conflicts.
5. **Report Agent** generates court-reviewable forensic reports with cryptographic SHA-256 hash ledgers.
6. **Tamper-Evident Case Sealing** computes an 8-dimensional Merkle root hash and exports a zero-dependency offline archive inspectable in any web browser.

---

## Core Forensic & Legal Principles
- **No Lie Detection:** CrimeKit extracts structured claims and cross-checks them against evidence. It identifies whether statements are *supported*, *contradicted*, *partially supported*, or *unresolved*.
- **No Guilt Determinations:** The system establishes evidence correlation, not judicial conclusions.
- **Human Investigator Control:** AI correlates and recommends; the investigator confirms or dismisses.
- **Strict Case Isolation:** Case data, evidence, timeline events, and archives never cross tenant/case boundaries.

---

## Multi-Agent Architecture

```
                    INVESTIGATOR
                         │
                         ▼
                  CRIMEKIT UI
                         │
                         ▼
                CASE ORCHESTRATOR
                         │
        ┌────────┬───────┼───────┬────────┐
        ▼        ▼       ▼       ▼        │
    Detective Timeline GeoScope Testimony │
        │        │       │       │        │
        └────────┴───────┴───────┘        │
                         ▼
                SHARED CONTEXT
                         ▼
               CONTRADICTION MATRIX
                         ▼
                 HUMAN REVIEW
                         ▼
                   REPORT AGENT
                         ▼
                   CASE SEAL
                         ▼
              OFFLINE ARCHIVE
                         │
                         ▼
                INTEGRITY VERIFY


AI MODEL GATEWAY PATH:
CrimeKit Agents ──▶ AI Gateway ──▶ Nebius Token Factory ──▶ NVIDIA Nemotron
```

---

## Specialist Agents & Forensic Tools

| Specialist Agent | Core Capabilities | Controlled Forensic Tools |
| :--- | :--- | :--- |
| **Case Orchestrator** | Multi-agent task planning, heuristic routing, dependency resolution | `orchestrator_planner`, `handoff_router` |
| **Detective Agent** | Evidence retrieval, entity resolution, graph exploration | `evidence_search`, `entity_search`, `knowledge_graph_traversal` |
| **Timeline Agent** | Chronological ordering, temporal clustering, window analysis | `timeline_search`, `temporal_correlation`, `timeline_event_context` |
| **GeoScope Agent** | Spatial telemetry, sector triangulation, co-location | `location_search`, `movement_trace`, `co_location_analysis` |
| **Testimony Agent** | Semantic claim decomposition, alibi verification, discrepancy checks | `extract_claims`, `cross_check_temporal`, `cross_check_geographic` |
| **Report Agent** | Synthesis of formal findings, hash ledgers, chain of custody | `build_report_document`, `render_pdf`, `render_markdown` |

---

## NVIDIA Nemotron on Nebius
CrimeKit utilizes **NVIDIA Nemotron** (`nvidia/nemotron-4-340b-instruct`) served via **Nebius Token Factory**:
- **Why Nemotron?** Advanced instruction-following, structured JSON generation, and multi-turn forensic tool-calling reliability.
- **Centralized Gateway:** Pluggable `BaseModelProvider` and `NebiusNemotronRuntime` with exponential backoff, rate limit handling, and zero credential leakage.

---

## Tamper-Evident Offline Archive
When a case investigation is concluded, Phase 10 seals the state into a portable ZIP archive containing:
1. `manifest.json`: Deterministic canonical snapshot of all evidence, claims, findings, and reviews.
2. `case-seal.json`: Merkle-style root hash computed across 8 sub-dimensions.
3. `reports/report.pdf` & `report.json`: Formatted forensic findings and hash ledger.
4. `archive/verification.html`: **Zero-dependency, standalone browser verifier** that inspects the archive offline without needing an active CrimeKit server or internet connection.

---

## Tech Stack
- **Backend:** FastAPI, Python 3.14, SQLAlchemy, PostgreSQL 16 (pgvector), SQLite (tests), Redis, Neo4j
- **Frontend:** Next.js 16 (App Router), React 19, TypeScript, TailwindCSS, Lucide Icons, Shadcn UI
- **AI & Cloud:** NVIDIA Nemotron on Nebius Token Factory (`api.tokenfactory.nebius.com`)

---

## Environment Configuration (`.env`)

```bash
# Nebius Token Factory & NVIDIA Nemotron Gateway
NEBIUS_API_KEY=your_nebius_api_key_here
NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1
NEBIUS_MODEL=nvidia/nemotron-4-340b-instruct
NEBIUS_TIMEOUT_SECONDS=45.0
NEBIUS_MAX_RETRIES=2
AGENT_RUNTIME_MODE=nebius   # Set to 'mock' for local tests / CI

# Optional External Intelligence
TAVILY_API_KEY=your_tavily_key_optional

# Core Services
DATABASE_URL=postgresql://crimekit_app:password@postgres:5432/crimekit
REDIS_URL=redis://:password@redis:6379/0
NEO4J_URI=bolt://neo4j:7687
```

---

## Live Multi-Agent Dashboard (Phase 12)

The **Live Multi-Agent Investigation Dashboard** brings all forensic specialists, tools, and evidence streams into a unified real-time operations console:

- **Case-Scoped WebSocket Streaming:** Connects to `ws://{host}/ws/case/{case_id}` with strict tenant authorization and 25s ping-pong keepalive.
- **Live Agent Board:** Real-time state indicators (`IDLE`, `PLANNING`, `QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`) driven directly by backend execution events.
- **Tool Execution Feed:** Live updates as forensic tools (`evidence_search`, `timeline_search`, `co_location_analysis`) query evidence databases.
- **Streaming Findings & Evidence Citations:** Real findings pop up immediately as specialists uncover leads with 1-click links to raw evidence (`EV-087`, `EV-104`).
- **Interactive Contradiction Matrix:** Automated discrepancy detection with instant 1-click human investigator review (`CONFIRM`, `DISMISS`, `UNRESOLVED`).
- **Tamper-Evident Case Sealing:** Cryptographic 8-dimensional Merkle root calculation and offline browser-verifiable archive export.

---

## Running Locally

### 1. Backend Setup
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Running Test Suites
```bash
# Execute complete multi-agent test suite (Phases 4 through 12)
AGENT_RUNTIME_MODE=mock TESTING=1 pytest backend/tests/test_phase4_detective_tools.py backend/tests/test_phase5_timeline_geoscope_tools.py backend/tests/test_phase6_case_orchestrator.py backend/tests/test_phase7_report_agent.py backend/tests/test_phase8_testimony_agent.py backend/tests/test_phase9_contradiction_matrix.py backend/tests/test_phase10_case_archive.py backend/tests/test_phase11_smoke_and_hardening.py backend/tests/test_phase12_live_dashboard.py
```

---

## Security & Hackathon Compliance
- **Zero Committed Secrets:** Verified clean git status without credentials.
- **Truthful Status Display:** The AI Workspace explicitly displays `Nebius / Nemotron` and never masks mock execution as live.
- **Case Boundary Defense:** Direct cross-case queries return empty or access-denied results.
