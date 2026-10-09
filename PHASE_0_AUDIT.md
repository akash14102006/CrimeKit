# CrimeKit Multi-Agent AI System — Phase 0 Architectural Audit Report

**Date:** October 8, 2026  
**Auditor:** Principal Software Architect, Senior Full-Stack Engineer, AI Agent Architect, UI/UX Engineer  
**Status:** PHASE 0 COMPLETE — READ-ONLY SYSTEM AUDIT & INTEGRATION SPECIFICATION  

---

## 1. Executive Summary

CrimeKit is a full-stack, enterprise-grade digital forensics and investigation platform. Prior to this audit, the core infrastructure (PostgreSQL 16, Redis 7, Neo4j 5, Celery/Distributed Workers, FastAPI backend, and Next.js 14 frontend) underwent a complete production recovery and passes 100% of its test suite (338/338 tests passing).

The platform already possesses:
1. **Case-Scoped Relational Data Layer**: Robust PostgreSQL schemas covering Cases, Evidence, Chain of Custody (tamper-evident SHA-256), Forensic Jobs, OCR Documents, Vector Embeddings, and Audit Logs.
2. **Knowledge Graph Layer**: Neo4j instance storing entities (`Person`, `Organization`, `Location`, `Phone`, `Account`, `Document`, `Vehicle`), relationships (`COMMUNICATED_WITH`, `TRANSFERRED_FUNDS_TO`, `ASSOCIATED_WITH`, `MENTIONED_IN`), and timeline events with case isolation.
3. **Investigation Workspace**: An active frontend `/workspace/[caseId]` and backend `/workspace/cases/{caseId}` service providing unified evidence lists, timeline events, AI findings summaries, and risk indicators.
4. **Existing AI Workspace**: A dedicated frontend route `/ai` (Case Selector) and `/ai/[caseId]` with a functional multi-tab investigation console containing `ChatPanel`, `ChatSidebar`, `FindingsPanel`, `AgentStatusPanel`, `SuggestedActionsPanel`, `CorrelationPanel`, `InvestigationSummaryPanel`, and Reference panels (`Evidence`, `KG`, `Timeline`, `Citations`).
5. **Existing Agent Foundation**: A foundational `backend/app/agents/` package defining synchronous and asynchronous Supervisors (`Supervisor`, `AsyncSupervisor`), an `AgentRegistry`, `SharedContext`, and prototype heuristic agents (`DetectiveAgent`, `TimelineAgent`, `CorrelationAgent`, `ReportAgent`).
6. **Realtime WebSocket & Task Streams**: Case-scoped WebSocket server (`/ws/case/{case_id}`) for streaming graph and forensic events, complemented by Redis-backed task streams and distributed worker queues.

**Phase 0 Verdict:** The CrimeKit codebase is in a prime architectural position to receive a production-quality multi-agent AI system. It does **not** require rebuilding the frontend, changing databases, or discarding existing forensic pipelines. The target multi-agent architecture can be integrated into the existing `/ai/[caseId]` workspace and `backend/app/agents/` supervisor framework cleanly.

---

## 2. Current Architecture

```
                                  CRIMEKIT SYSTEM TOPOLOGY
                                  
   +-------------------------------------------------------------------------------+
   |                             NEXT.JS 14 FRONTEND                               |
   |                                                                               |
   |   Routes:                                                                     |
   |   /cases               - Case Management & List                               |
   |   /workspace/[caseId]  - Forensic Investigation Workspace                     |
   |   /evidence            - Chain of Custody & Evidence Library                  |
   |   /graph & /kg         - Interactive Knowledge Graph (Neo4j / Vis Network)    |
   |   /timeline            - Forensic Temporal Chronology                         |
   |   /search              - Hybrid Full-Text & Semantic Search                   |
   |   /ai                  - AI Workspace Case Selector                           |
   |   /ai/[caseId]         - AI Intelligence Workspace & Chat Console             |
   |                                                                               |
   |   State & API:                                                                |
   |   - Zustand: authStore, aiStore, sidebarStore                                 |
   |   - TanStack React Query: useCases, useWorkspace, useAIQuery, useTimeline     |
   |   - Axios API Client: Automatic JWT injection, baseURL config                 |
   +---------------------------------------+---------------------------------------+
                                           | HTTP REST / WebSocket
                                           v
   +-------------------------------------------------------------------------------+
   |                             FASTAPI BACKEND (:8002)                           |
   |                                                                               |
   |   Routers:                                                                    |
   |   /auth                - Descope IdP + Local JWT, RBAC & Permissions          |
   |   /cases               - Case CRUD & Assignment                               |
   |   /evidence            - Evidence Upload, Hash Integrity, Custody Ledger      |
   |   /workspace           - Investigation Workspace Aggregation Service          |
   |   /kg                  - Knowledge Graph Cypher Queries & Entity Extraction   |
   |   /timeline            - Forensic Chronology Events                           |
   |   /api/v1/search       - Semantic, Hybrid, and Cross-Correlation Search       |
   |   /ai                  - Vector Ingestion, Document Fetch, /ai/agent/query    |
   |   /processing          - Forensic Pipeline, OCR, Metadata Extractors          |
   |   /ws/case/{case_id}   - Realtime Case-Scoped WebSockets                      |
   |                                                                               |
   |   Internal Agent Engine:                                                      |
   |   backend/app/agents/  - Supervisor, AsyncSupervisor, Registry, SharedContext |
   +-----------------+---------------------+-------------------+-------------------+
                     |                     |                   |
                     v                     v                   v
   +--------------------+  +--------------------+  +--------------------+
   |   POSTGRESQL 16    |  |      REDIS 7       |  |      NEO4J 5       |
   |   Port: 5433       |  |      Port: 6379    |  |      Port: 7687    |
   |                    |  |                    |  |                    |
   |  - users & roles   |  |  - Task streams    |  |  - Person nodes    |
   |  - cases           |  |  - Queue depths    |  |  - Org/Account     |
   |  - evidence        |  |  - Worker pool     |  |  - Phone/Location  |
   |  - custody         |  |  - Realtime broker |  |  - Relations       |
   |  - documents & OCR |  |  - Metrics         |  |  - Case isolation  |
   |  - embeddings (vec)|  +--------------------+  +--------------------+
   |  - audit_logs      |
   +--------------------+
```

---

## 3. Repository Structure

```
CrimeKit/
├── backend/
│   ├── alembic/                    # Database migrations
│   ├── app/
│   │   ├── main.py                 # FastAPI application root & middleware
│   │   ├── models.py               # SQLAlchemy models (User, Case, Evidence, Document, Embedding, etc.)
│   │   ├── database.py             # PostgreSQL session management & pool
│   │   ├── auth.py                 # Descope JWT validator + local JWT + RBAC
│   │   ├── cases.py                # Case REST endpoints
│   │   ├── evidence.py             # Evidence REST endpoints & custody ledger
│   │   ├── ai_pipeline.py          # /ai/ingest and /ai/agent/query endpoints
│   │   ├── agents/                 # Existing Agent framework
│   │   │   ├── interfaces.py       # Base Agent abstract class
│   │   │   ├── registry.py         # AgentRegistry dictionary
│   │   │   ├── context.py          # SharedContext in-memory store
│   │   │   ├── persistent_context.py # DB-backed persistent context
│   │   │   ├── supervisor.py       # Synchronous Supervisor
│   │   │   ├── async_supervisor.py # Asynchronous Supervisor with retries & audit logging
│   │   │   ├── detective.py        # Prototype Detective Agent
│   │   │   ├── timeline.py         # Prototype Timeline Agent
│   │   │   ├── correlation.py      # Prototype Correlation Agent
│   │   │   └── report.py           # Prototype Report Agent
│   │   ├── embeddings.py           # Deterministic & OpenAI embedding providers
│   │   ├── vector_store.py         # DBVectorStore (SQLAlchemy models.Embedding)
│   │   ├── entity_extractor.py     # Regex & heuristics entity extraction
│   │   ├── entity_normalizer.py    # Name/phone/email sanitization
│   │   ├── entity_resolver.py      # Entity deduplication & merging
│   │   ├── kg.py                   # Neo4j Driver & Cypher ingest/queries
│   │   ├── kg_routes.py            # /kg endpoints
│   │   ├── timeline_routes.py      # /timeline endpoints
│   │   ├── workspace.py            # /workspace REST routes
│   │   ├── workspace_service.py    # Case workspace data aggregator
│   │   ├── workspace_schemas.py    # Pydantic schemas for workspace
│   │   ├── search_routes.py        # /api/v1/search endpoints
│   │   ├── processing.py           # Forensic processing queue & jobs
│   │   ├── websocket_manager.py    # Case-scoped WebSocket connection pool
│   │   └── ws_routes.py            # /ws/case/{case_id} WebSocket route
│   └── tests/                      # 338 automated test cases
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/login/       # Enterprise Login page (Descope / Dev bypass)
│   │   │   ├── (dashboard)/
│   │   │   │   ├── layout.tsx      # Sidebar + Header shell with AuthGuard
│   │   │   │   ├── cases/          # Case list page
│   │   │   │   ├── workspace/[id]/ # Forensic Case workspace
│   │   │   │   ├── ai/
│   │   │   │   │   ├── page.tsx    # Case selector for AI Workspace
│   │   │   │   │   └── [caseId]/
│   │   │   │   │       └── page.tsx# Dynamic route mounting AIWorkspacePage
│   │   │   │   ├── graph/          # Knowledge Graph view
│   │   │   │   ├── timeline/       # Timeline view
│   │   │   │   └── search/         # Search view
│   │   ├── features/
│   │   │   ├── ai/
│   │   │   │   ├── components/     # AIWorkspacePage, ChatPanel, ChatSidebar, ChatMessage, ChatInput, etc.
│   │   │   │   ├── hooks/          # useAIWorkspace, useAIQuery
│   │   │   │   └── store/          # aiStore (Zustand state for conversations, messages, streaming)
│   │   │   ├── cases/              # CaseList, CreateCaseDialog, etc.
│   │   │   └── evidence/           # EvidenceTable, UploadManager, etc.
│   │   ├── components/
│   │   │   ├── shared/             # AuthGuard, Header, Sidebar, RoleGuard
│   │   │   └── ui/                 # Button, Card, Dialog, Tabs, ScrollArea, Badge, etc.
│   │   ├── config/env.ts           # Client environment configuration
│   │   ├── constants/api-endpoints.ts # Canonical API constants
│   │   ├── lib/api-client.ts       # Axios instance with auth interceptors
│   │   ├── store/authStore.ts      # Zustand auth state & session storage
│   │   └── types/                  # TypeScript interfaces for Cases, Evidence, Auth, etc.
```

---

## 4. Frontend Architecture

- **Framework**: Next.js 14 / React 18 (with Next 16 Turbopack dev tooling support).
- **Styling**: Tailwind CSS + CSS modules / Vanilla utility variables, Lucide React icons.
- **State Management**:
  - Zustand (`useAuthStore`, `useAIStore`, `useSidebarStore`).
  - TanStack React Query (`v5`) for asynchronous server-state fetching and cache invalidation.
- **API Client**: `lib/api-client.ts` Axios instance configured with base URL `http://localhost:8002` (in dev) or configured environment variable, with request interceptors injecting Bearer JWT tokens.
- **Design Language**: Dark/light hybrid forensic theme, slate/zinc surfaces, emerald/cyan/indigo badges, monospace metadata callouts, crisp high-density cards and tables.

---

## 5. Backend Architecture

- **Framework**: FastAPI (Python 3.14).
- **Data Access**: SQLAlchemy 2.0 ORM with PostgreSQL 16 driver `psycopg2`.
- **Authentication**: `backend/app/auth.py` supporting both Descope RS256/ES384 tokens and local HS256 tokens (`role_required` dependency).
- **Databases**:
  - PostgreSQL 16 on port 5433 (Relational records, evidence metadata, documents, embeddings, audit logs).
  - Redis 7 on port 6379 (Task queues, stream caching, metrics).
  - Neo4j 5 on bolt port 7687 (Knowledge Graph entities, relations, Cypher queries).
- **Processors**: `backend/app/processors/` and `forensic_engine/` handling EXIF, OCR, PDF parsing, hex analysis, and hash computation.

---

## 6. Current AI Workspace Implementation

### Route & Render Path
```
URL: /ai
  ↓
frontend/src/app/(dashboard)/ai/page.tsx (AISelectCasePage)
  ↓
Renders list of cases from useCases()
  ↓ (User clicks a case)
Navigates to: /ai/[caseId]
  ↓
frontend/src/app/(dashboard)/ai/[caseId]/page.tsx
  ↓
frontend/src/features/ai/components/AIWorkspacePage.tsx
  ↓
Split Layout:
  ├── Left: ChatSidebar.tsx (Conversation list, new chat, pin, delete)
  ├── Center: ChatPanel.tsx (Message history, ChatMessage.tsx, ChatInput.tsx)
  └── Right Tabs (420px):
        ├── FindingsPanel.tsx
        ├── AgentStatusPanel.tsx (Supervisor, Detective, Correlation, Timeline, etc.)
        ├── SuggestedActionsPanel.tsx
        ├── CorrelationPanel.tsx
        ├── InvestigationSummaryPanel.tsx
        ├── EvidenceReferencesPanel.tsx
        ├── GraphReferencesPanel.tsx
        ├── TimelineReferencesPanel.tsx
        └── CitationsPanel.tsx
```

### Current Data Flow & Backend Connectivity
1. When an investigator submits a prompt in `ChatInput.tsx`, `ChatPanel.tsx` calls `aiQuery.mutateAsync()` from `useAIQuery()` in `useAIWorkspace.ts`.
2. `useAIQuery()` invokes `aiService.query()` in `services/aiService.ts`, which sends `POST /ai/agent/query` with `{ query, case_id, top_k }`.
3. In `backend/app/ai_pipeline.py`, `agent_query()` computes a pseudo-embedding for the text using `_text_to_embedding()`, computes cosine similarity against stored document embeddings in `models.Embedding`, and returns matching snippets.
4. `ChatPanel.tsx` parses results into assistant messages, extracts evidence citations, and updates the local conversation in `aiStore.ts`.

---

## 7. Current Case Context

- In the frontend, the active case ID is provided via Next.js route params: `const params = useParams(); const caseId = params.caseId as string;`.
- Case details, evidence counts, entities, and risks are queried via `useWorkspace(caseId)` in `hooks/queries/useWorkspace.ts` calling `GET /workspace/cases/{caseId}`.
- Every API endpoint in `aiService.ts`, `evidenceService.ts`, `kgService.ts`, and `timelineService.ts` accepts `case_id` as a scoped parameter.

---

## 8. Evidence Architecture

- **Database Model**: `models.Evidence` in PostgreSQL.
  - Fields: `id`, `case_id`, `filename`, `storage_path`, `sha256`, `size`, `mime_type`, `metadata_json`, `uploaded_by`, `uploaded_at`.
- **Custody Audit Ledger**: `models.ChainOfCustody` linked via `evidence_id`, recording timestamp, actor, action, and cryptographic SHA-256 integrity verification.
- **Extraction Results**: `models.Document` stores extracted/OCR text associated with `evidence_id`.
- **Query Scoping**: `GET /evidence/case/{case_id}` returns all evidence strictly bounded to the case.
- **Detective Agent Access**: A future Detective Agent can query `GET /evidence/case/{case_id}` or `db.query(models.Evidence).filter(models.Evidence.case_id == case_id)`. Because `case_id` is an indexed foreign key, case isolation is guaranteed.

---

## 9. Knowledge Graph Architecture

- **Graph Database**: Neo4j 5 Community Edition (`bolt://localhost:7687`).
- **Graph Client**: `backend/app/kg.py` managing session pools.
- **Schema & Nodes**:
  - Labels: `Entity`, `Person`, `Organization`, `Location`, `Phone`, `Account`, `Document`, `Vehicle`.
  - Properties: `name`, `type`, `case_id`, `evidence_id`, `confidence`, `created_at`.
- **Relationships**: `COMMUNICATED_WITH`, `TRANSFERRED_FUNDS_TO`, `ASSOCIATED_WITH`, `MENTIONED_IN`, `LOCATED_AT`.
- **Case Isolation**: Every node and edge created by `client.ingest(...)` in `kg.py` attaches `case_id: $case_id`. All Cypher queries in `kg_routes.py` (e.g. `MATCH (n:Entity {case_id: $case_id})-[r]-(m:Entity {case_id: $case_id})`) strictly filter by `case_id`.

---

## 10. Timeline Architecture

- **Storage**:
  - Stored in PostgreSQL `models.ForensicResult` (JSON payload containing timeline events per evidence).
  - Also synchronized into Neo4j as `TimelineEvent` nodes with `timestamp` and `case_id`.
- **Endpoints**: `GET /timeline?case_id={case_id}` in `backend/app/timeline_routes.py` and `GET /workspace/cases/{case_id}/timeline`.
- **Fields**: `id`, `evidence_id`, `case_id`, `timestamp`, `title`, `description`, `source` (exif, ocr, email, etc.), `metadata`.

---

## 11. Existing AI / LLM Infrastructure Audit

| File / Component | Purpose | Model / Engine | Provider | API Route | Status |
|---|---|---|---|---|---|
| `backend/app/ai_pipeline.py` | Vector ingest & search | 32-dim SHA-256 Pseudo-embedding | Local / Deterministic | `POST /ai/ingest`, `POST /ai/agent/query` | Active & Tested |
| `backend/app/embeddings.py` | Pluggable embedding adapters | `text-embedding-3-small` / Deterministic | Deterministic (Default) / OpenAI (Optional) | Internal library | Active & Tested |
| `backend/app/vector_store.py` | DB-backed vector cosine similarity | Vector math in Python | PostgreSQL `models.Embedding` | Internal library | Active & Tested |
| `backend/app/agents/supervisor.py` | Synchronous task routing | Heuristic dispatch | Internal | Python class | Active |
| `backend/app/agents/async_supervisor.py` | Async task routing with retries | Heuristic dispatch + Audit logs | Internal | Python class | Active |
| `backend/app/agents/detective.py` | Entity extractor agent | Regex & heuristic | Internal | Python class | Prototype |
| `backend/app/agents/timeline.py` | Date/event extractor agent | Regex & heuristic | Internal | Python class | Prototype |
| `backend/app/agents/correlation.py` | Cross-entity matcher agent | Set intersections | Internal | Python class | Prototype |
| `backend/app/agents/report.py` | Forensic report compiler agent | Markdown templating | Internal | Python class | Prototype |
| `frontend/src/features/ai/store/aiStore.ts` | AI Chat & Workspace state | Client-side Zustand | Browser memory & local storage | Client-side | Active |

**Key Finding**: The existing backend does **NOT** yet integrate Nebius AI, NVIDIA Nemotron, NeMo Agent Toolkit, or Tavily. It utilizes local deterministic embeddings and prototype regex-based agents. This confirms that Phase 0 is starting from a clean slate for external LLM/Agent gateway integration without legacy model conflicts.

---

## 12. Existing Streaming Capabilities

- **WebSockets**:
  - Active in `backend/app/websocket_manager.py` and `backend/app/ws_routes.py`.
  - Endpoint: `ws://localhost:8002/ws/case/{case_id}?token={jwt}`.
  - Features: Case-isolated channels, rate-limiting, heartbeat keep-alive, client connection registry.
- **Server-Sent Events (SSE)**:
  - Not currently used in backend or frontend.
- **Streaming Recommendation for Multi-Agent Chat**:
  - FastAPI supports `StreamingResponse(iter, media_type="text/event-stream")` for standard HTTP SSE.
  - Next.js and browser `fetch` handles SSE natively via `ReadableStream`.
  - In Phase 3, we recommend adding SSE endpoint `POST /api/ai/chat/stream` for live agent token streaming, while retaining WebSocket for background agent execution status updates.

---

## 13. Authentication & Authorization

- **Mechanisms**: Descope Enterprise IdP (RS256/ES384) + Local Fallback JWT (HS256).
- **Roles**: `admin`, `investigator`, `analyst`, `evidence_officer`, `compliance_officer`, `auditor`, `jury_evaluator`, `viewer`.
- **Enforcement Layer**:
  - FastAPI: `role_required(["admin", "investigator", ...])` and `_check_case_access()` in `workspace.py`.
  - Frontend: `<AuthGuard allowedRoles={[...]}>` and `<RoleGuard>` wrapping views and buttons.
- **Multi-Agent Security Rule**: All future AI agent endpoints must depend on `get_current_user` and enforce `_check_case_access(current_user, case_id)`. An agent must never execute queries on behalf of an investigator on a case that investigator is unauthorized to inspect.

---

## 14. Existing Reusable UI Components

The following components already exist in `frontend/src/components/ui/` and `frontend/src/features/` and should be reused:

| Component Category | Existing Component | Location | Reuse Target for Multi-Agent |
|---|---|---|---|
| Chat Message | `ChatMessage.tsx` | `features/ai/components/` | Individual agent messages, user messages |
| Chat Input | `ChatInput.tsx` | `features/ai/components/` | Prompt input with multiline auto-expand and stop button |
| Chat History Sidebar | `ChatSidebar.tsx` | `features/ai/components/` | Per-agent or per-case conversation selector |
| Agent Status | `AgentStatusPanel.tsx` | `features/ai/components/` | Agent status pills, progress, active tools indicator |
| Findings Display | `FindingsPanel.tsx` | `features/ai/components/` | Structured findings cards with confidence badges |
| Citations Display | `CitationsPanel.tsx` | `features/ai/components/` | Forensic evidence links, hash badges, provenance |
| Tabs & Navigation | `Tabs`, `TabsList`, `TabsTrigger` | `components/ui/tabs.tsx` | Agent selector tab bar (Detective, Timeline, etc.) |
| Badges | `Badge` | `components/ui/badge.tsx` | Confidence percentage, agent roles, verified statuses |
| Dialogs / Modals | `Dialog`, `DialogContent` | `components/ui/dialog.tsx` | Evidence modal view, Agent handoff confirmations |
| Scroll Containers | `ScrollArea` | `components/ui/scroll-area.tsx` | Chat stream area, findings lists |
| Tables | `Table`, `TableRow`, `TableCell` | `components/ui/table.tsx` | Extracted entities and timeline tables |

---

## 15. Agent Integration Readiness Score

| Subsystem | Score | Rationale |
|---|---|---|
| **Frontend Architecture** | **9/10** | Route `/ai/[caseId]` and complete UI layout with chat, input, and sidebars already exist and work smoothly. |
| **Backend Architecture** | **9/10** | FastAPI modular routers, clean dependency injection, and centralized DB sessions are ready. |
| **Case Context** | **10/10** | `case_id` is thoroughly threaded through all frontend views, hooks, and backend services. |
| **Evidence Access** | **9/10** | Evidence is case-scoped, SHA-256 hashed, and OCR/text is already extracted into `models.Document`. |
| **Graph Access** | **9/10** | Neo4j client and Cypher queries are operational and indexed with case isolation. |
| **Timeline Access** | **9/10** | Structured temporal events are queryable via REST and Neo4j. |
| **AI Infrastructure** | **4/10** | Only local pseudo-embeddings and regex agents exist; Nebius/Nemotron/OpenShell must be introduced. |
| **Streaming** | **7/10** | WebSockets are production-ready; HTTP SSE streaming needs to be wired for LLM text chunks. |
| **Security & RBAC** | **10/10** | Strong authentication, RBAC, and case-level ownership checks are fully functional. |
| **Testing** | **10/10** | 338 backend tests passing with zero errors; regression harness is robust. |
| **OVERALL READINESS** | **8.6 / 10** | **Ready for Agent Architecture Integration.** |

---

## 16. Technical Risk Matrix

| Risk ID | Severity | Category | Description | Mitigation Strategy |
|---|---|---|---|---|
| **R-01** | **P1** | AI Gateway | External LLM API latency or downtime (Nebius AI / NVIDIA Nemotron). | Implement graceful fallbacks, timeout budgets, and streaming chunk handlers. |
| **R-02** | **P1** | Context Size | Forensic cases contain hundreds of evidence files and thousands of entities exceeding LLM context windows. | Use RAG retrieval via vector store and Neo4j subgraph extraction rather than stuffing raw documents into prompt context. |
| **R-03** | **P2** | Hallucination | LLM generating plausible but non-existent evidence or false correlations. | Strict grounding: System prompts must forbid assertions without specific `evidence_id` / `source` citations; compute explicit confidence metrics. |
| **R-04** | **P2** | State Persistence | Agent chat sessions currently reside only in frontend Zustand `localStorage`. | Create backend `AgentSession` and `AgentMessage` database tables to persist multi-agent investigation history across devices. |
| **R-05** | **P3** | Streaming UX | Chat UI re-rendering too frequently during fast token streaming. | Use throttled state updates or direct stream buffer refs in `ChatPanel`. |

---

## 17. Recommended Target Multi-Agent Architecture

```
                               INVESTIGATOR UI
                                      |
                         +------------v------------+
                         |  AI Workspace (/ai)     |
                         |  Case: [caseId]         |
                         +------------+------------+
                                      |
                   Agent Selector (Horizontal Tab Bar)
     [Case Orchestrator] [Detective] [Timeline] [GeoScope] [Testimony] [Evidence Review] [Report]
                                      |
                                      v
                             AGENT CHAT SHELL
                   (Conversation, Tool Calls, Citations)
                                      |
                         HTTP SSE / WebSocket Stream
                                      |
                                      v
                         FASTAPI AGENT GATEWAY
                                      |
                              AGENT REGISTRY
                                      |
                         +------------v------------+
                         |   CASE ORCHESTRATOR     |
                         |   (Supervisor Engine)   |
                         +------------+------------+
                                      |
         +------------+---------------+---------------+------------+
         |            |               |               |            |
         v            v               v               v            v
     Detective     Timeline        GeoScope       Testimony     Evidence/Report
      Agent         Agent           Agent           Agent           Agents
         |            |               |               |            |
         +------------+---------------+---------------+------------+
                                      |
                                      v
                             CRIMEKIT TOOL LAYER
                 (Strictly scoped to Investigator Permissions & Case ID)
                 ├── Tool 1: Evidence Vector RAG
                 ├── Tool 2: Knowledge Graph Subgraph (Neo4j)
                 ├── Tool 3: Timeline Chronology
                 ├── Tool 4: Metadata & Chain of Custody
                 └── Tool 5: Tavily OSINT (Optional External Intel)
                                      |
                                      v
                          NEBIUS / NVIDIA NEMOTRON
                             LLM Inference API
```

---

## 18. Future Agent Structure (Specification for Later Phases)

In future phases, the following structure will be established without modifying unrelated modules:

### Backend Structure (`backend/app/agents/`):
```
backend/app/agents/
├── core/
│   ├── base_agent.py          # Abstract Agent base class with prompt, memory, and tools
│   ├── session_manager.py     # Persistent database session manager
│   ├── llm_gateway.py         # Nebius / NVIDIA Nemotron unified client
│   └── handoff.py             # Structured agent-to-agent message passing protocol
├── specialists/
│   ├── orchestrator.py        # Case Orchestrator Agent
│   ├── detective.py           # Detective Agent (Entities & Evidence RAG)
│   ├── timeline_agent.py      # Timeline Agent (Chronology & Temporal clustering)
│   ├── geoscope_agent.py      # GeoScope Agent (EXIF coordinates & location graphs)
│   ├── testimony_agent.py     # Testimony Agent (Interview transcript & witness correlation)
│   ├── evidence_review.py     # Evidence Review Agent (Forensic validity & integrity)
│   └── report_agent.py        # Report Agent (Court-admissible document generator)
└── tools/
    ├── evidence_tools.py      # Case-scoped evidence retrieval tools
    ├── kg_tools.py            # Case-scoped Neo4j query tools
    ├── timeline_tools.py      # Case-scoped event tools
    └── external_tools.py      # Tavily OSINT search tools (sandboxed)
```

### Frontend Structure (`frontend/src/features/ai/`):
```
frontend/src/features/ai/
├── components/
│   ├── AgentSelectorBar.tsx   # Switch between the 7 specialist agents
│   ├── AgentIdentityCard.tsx  # Display active agent persona, capability, and status
│   ├── ToolExecutionFeed.tsx  # Expandable real-time tool calls ([Searching Evidence], etc.)
│   ├── HandoffCard.tsx        # Card allowing transfer of finding to another agent
│   └── ... (Existing panels: Findings, Citations, Graph, Timeline)
└── hooks/
    ├── useAgentChat.ts        # SSE streaming hook for agent responses
    └── useAgentSessions.ts    # Session query and management
```

---

## 19. Proposed API Contract

The following endpoints will be introduced in subsequent phases:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/ai/agents` | List available specialist agents, their capabilities, and tool definitions. |
| `GET` | `/api/ai/cases/{case_id}/sessions` | List investigation chat sessions for a specific case. |
| `POST` | `/api/ai/cases/{case_id}/sessions` | Create a new agent session (specifying primary agent). |
| `GET` | `/api/ai/sessions/{session_id}/messages` | Retrieve message history with citations and tool executions. |
| `POST` | `/api/ai/chat/stream` | Stream chat message to selected agent with real-time SSE token delivery. |
| `POST` | `/api/ai/handoff` | Transfer findings from Agent A to Agent B with structured context. |

---

## 20. Phased Implementation Roadmap

* **PHASE 0: Audit & Architecture Specification (COMPLETED)**
* **PHASE 1: Reusable Agent Chat Workspace UI** (Enhance `/ai/[caseId]` with Agent Selector and Tool Execution view).
* **PHASE 2: Backend Agent Registry & Session Model** (Database models for sessions and persistent messages).
* **PHASE 3: Nebius Token Factory & NVIDIA Nemotron AI Gateway** (API client with SSE streaming).
* **PHASE 4: Detective Agent** (Evidence RAG and Entity graph correlation).
* **PHASE 5: Timeline Agent** (Chronology correlation and temporal anomaly detection).
* **PHASE 6: GeoScope Agent** (Geospatial EXIF clustering and movement mapping).
* **PHASE 7: Testimony Agent** (Witness statement extraction and inconsistency detection).
* **PHASE 8: Evidence Review Agent** (Hash verification and Chain of Custody audit).
* **PHASE 9: Report Agent** (Court-ready executive summary and evidence catalog export).
* **PHASE 10: Case Orchestrator** (Supervisory multi-agent delegation and synthesis).
* **PHASE 11: Security & Guardrails** (NVIDIA NemoClaw / OpenShell prompt injection prevention).
* **PHASE 12: External Intelligence** (Tavily search integration for OSINT domain queries).
* **PHASE 13: Cross-Agent Handoffs** (Structured agent-to-agent findings transfer).
* **PHASE 14: Verification, Evaluation & Golden Test Suite**.
* **PHASE 15: Production Polish & Demonstration Readiness**.

---

## 21. File-Level Integration Map

| Existing File | Purpose | Future Modification | Phase |
|---|---|---|---|
| `frontend/src/features/ai/components/AIWorkspacePage.tsx` | Main workspace console | Mount `AgentSelectorBar` and link active agent state | Phase 1 |
| `frontend/src/features/ai/components/ChatPanel.tsx` | Chat viewport | Integrate SSE streaming and `ToolExecutionFeed` | Phase 1 |
| `frontend/src/features/ai/components/ChatMessage.tsx` | Message renderer | Render agent identity avatar, confidence, and handoff buttons | Phase 1 |
| `frontend/src/features/ai/store/aiStore.ts` | AI Zustand state | Add active agent tracking and session sync | Phase 1 |
| `backend/app/models.py` | Database schema | Add `AgentSession` and `AgentMessage` tables | Phase 2 |
| `backend/app/agents/interfaces.py` | Base agent definition | Extend to support tool schemas and system prompts | Phase 2 |
| `backend/app/agents/registry.py` | Agent storage | Register all 7 specialized agents | Phase 2 |
| `backend/app/ai_pipeline.py` | AI routing | Mount `/api/ai/` routers and streaming handler | Phase 3 |
| `backend/app/kg.py` | Neo4j client | Add agent tool wrapper functions with case filtering | Phase 4 |
| `backend/app/timeline_routes.py` | Timeline events | Add agent tool wrapper functions for temporal filtering | Phase 5 |
| `backend/app/evidence.py` | Evidence service | Add custody and metadata tools for Evidence Review agent | Phase 8 |

---

## 22. Audit Verification & Confirmation

- **Files Deleted**: NONE
- **Files Renamed**: NONE
- **Files Moved**: NONE
- **Database Schema Modified**: NONE
- **API Contracts Altered**: NONE
- **Dependencies Installed**: NONE
- **Runnability**: Backend running on port 8002, Frontend running on port 3000, 100% test pass rate maintained.
