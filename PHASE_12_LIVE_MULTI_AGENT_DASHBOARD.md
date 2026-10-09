# PHASE 12: Real Live Multi-Agent Investigation Dashboard

## Architecture Overview

Phase 12 unifies CrimeKit's entire multi-agent forensic ecosystem into **ONE continuous, real-time investigator dashboard**. When an investigator enters an inquiry, the entire chain executes live and emits case-scoped domain events over WebSocket directly into the interface:

```
[INVESTIGATOR QUESTION]
         ↓
[CASE ORCHESTRATOR] (NVIDIA Nemotron 4-340B via Nebius Token Factory)
         ↓
┌────────┼────────┐
▼        ▼        ▼
[DETECTIVE] [TIMELINE] [GEOSCOPE] (Specialists)
         ↓
[REAL FORENSIC TOOLS] (Evidence Search, Timeline Correlation, Co-Location)
         ↓
[REAL FINDINGS & CONTRADICTIONS]
         ↓
[WEBSOCKET STREAM] (`/ws/case/{case_id}`)
         ↓
[LIVE INVESTIGATION DASHBOARD]
```

---

## 1. WebSocket Event Protocol & Lifecycle

### Connection Endpoint
```
ws://{host}/ws/case/{case_id}?token={JWT_TOKEN}
```
* Authenticates caller via JWT and enforces strict case-level authorization (`_verify_case_access`).
* Subscribes socket to case-isolated room. Clients on `CASE-A` **never** receive events from `CASE-B`.
* Heartbeat: 25s ping-pong keepalive with auto-reconnection and exponential backoff.

### Event Schema
All events follow a strictly typed schema:
```json
{
  "event_type": "tool.completed",
  "case_id": "CASE-2026-001",
  "timestamp": "2026-10-08T13:42:15.000Z",
  "event_id": "evt-uuid-v4",
  "metadata": {
    "tool_name": "evidence_search",
    "agent_id": "detective",
    "result_count": 3,
    "duration_ms": 142.8
  }
}
```

### Event Lifecycle Stages
1. `orchestration.started`: Orchestrator parses user objective and begins multi-agent decomposition.
2. `orchestration.delegated`: Orchestrator dispatches subtasks to specialist agents.
3. `agent.task.started`: Target specialist transitions to `● RUNNING`.
4. `tool.started`: Forensics tool begins executing on case data.
5. `tool.completed` / `tool.failed`: Tool finishes and logs output snippet and duration.
6. `finding.created`: Grounded forensic finding emitted with evidence references (`EV-087`, `EV-104`).
7. `agent.task.completed`: Specialist aggregates output and hands back context.
8. `contradiction.detected`: Automated discrepancy engine flags temporal/spatial conflicts.
9. `contradiction.review.updated`: Human investigator marks review (`confirmed`, `dismissed`, `unresolved`).
10. `report.generated`: Report Agent compiles provenance-grounded PDF/JSON report.
11. `case.archive.sealed`: Offline Merkle tree calculated, generating tamper-evident root hash.

---

## 2. Frontend State Machine & Dashboard Components

### `useLiveInvestigationStore` (`frontend/src/features/ai/store/liveInvestigationStore.ts`)
* Centralized reactive Zustand store tracking:
  * Connection health (`CONNECTED`, `CONNECTING`, `RECONNECTING`, `DISCONNECTED`).
  * Real-time agent state machine (`IDLE`, `PLANNING`, `QUEUED`, `RUNNING`, `WAITING`, `COMPLETED`, `FAILED`).
  * Deduplicated event stream via `processedEventIds`.
  * Tool executions with status badges and elapsed execution time.
  * Live findings stream with clickable evidence references.
  * Contradiction Matrix with 1-click human verification actions.

### `LiveInvestigationDashboard` (`frontend/src/features/ai/components/LiveInvestigationDashboard.tsx`)
* **Live Investigation Header**: Displays case identifier, live connection badge, active AI provider badge (`Nebius / NVIDIA Nemotron`), active run ID, and live elapsed timer.
* **Live Agents Board**: Visual cards for Orchestrator, Detective, Timeline, GeoScope, Testimony, and Report agents with live indicators and deep inspector.
* **Investigation Workflow Graph**: Reactive visual node-link progress flow.
* **Tool Activity Feed**: Real-time tool execution cards displaying tool name, agent, status, and duration without leaking sensitive parameters.
* **Live Activity Event Feed**: Chronological timestamped event log.
* **Live Findings with Evidence Citations**: Displays findings immediately as they arrive; citations link directly to evidence inspector.
* **Contradiction Matrix with Human Review**: One-click `CONFIRM`, `DISMISS`, and `UNRESOLVED` buttons dispatching real backend audit logs.

---

## 3. End-to-End Live Demo Procedure

1. **Open AI Workspace**: Navigate to `/ai/{caseId}`.
2. **Observe Connection**: Header displays `● WS CONNECTED` and `● LIVE: Nebius / NVIDIA Nemotron`.
3. **Submit Inquiry**:
   > "Determine whether Rahul Kumar was associated with the phone number, what happened around the relevant call, whether the device was near the incident location, and whether witness testimony is consistent with the digital evidence."
4. **Watch Live Execution**:
   * Orchestrator activates (`PLANNING`).
   * Detective runs `evidence_search` and `entity_search`.
   * Timeline correlates timestamps and flags the 21:14 call.
   * GeoScope runs co-location analysis and detects 20:52 location fix.
   * Contradiction Matrix displays 22-minute temporal discrepancy alert.
5. **Investigator Review**: Click `CONFIRM` on the contradiction card.
6. **Generate Report & Seal Case**:
   * Switch to `Seal/Archive` tab.
   * Click `Confirm & Seal`.
   * Master SHA-256 Merkle root hash is generated and verified offline.

---

## 4. Verification & Testing

* **Backend Test Suite**: 82 passed unit & integration tests covering Phase 4 to Phase 12.
* **Frontend TypeScript**: `npm run build` completed with zero type errors and clean production build.
