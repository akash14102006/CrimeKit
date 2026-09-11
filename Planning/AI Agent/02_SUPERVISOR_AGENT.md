
# 02_SUPERVISOR_AGENT.md

# CrimeKit Enterprise Supervisor Agent

> Master orchestration agent responsible for planning, routing, coordinating and validating every investigation workflow.

---

# 1. Mission

The Supervisor Agent is the brain of the multi-agent platform.

It never performs deep domain analysis itself. Instead it:

- Understands the investigation goal
- Plans execution
- Chooses agents
- Coordinates parallel work
- Shares context
- Validates outputs
- Resolves conflicts
- Produces the final investigation package

---

# 2. Responsibilities

- Intent detection
- Investigation planning
- Dynamic routing
- Agent scheduling
- Context management
- Memory coordination
- Tool authorization
- Human approval routing
- Retry decisions
- Final response assembly
- Audit logging

---

# 3. Folder Structure

```text
supervisor/
├── prompt.md
├── skills.md
├── instruction.md
├── graph.py
├── tools.py
├── memory.py
├── schemas.py
├── config.yaml
└── tests/
```

---

# 4. Inputs

- User request
- Investigation ID
- User role
- Available evidence
- Case metadata
- Previous agent outputs
- Shared memory

Outputs

- Execution plan
- Agent routing map
- Final structured response
- Audit record

---

# 5. Decision Engine

Determine:

1. Investigation type
2. Required agents
3. Sequential vs parallel execution
4. Required tools
5. Confidence thresholds
6. Human approval requirements

---

# 6. Routing Matrix

| Request | Primary Agent |
|---------|---------------|
| Evidence review | Detective |
| Timeline | Timeline |
| Relationships | Correlation |
| Maps | GeoScope |
| Q&A | Evidence QA |
| Witness summary | Testimony |
| Court report | Report |
| Prioritization | Triage |

---

# 7. LangGraph Workflow

```text
Start
 ↓
Validate Request
 ↓
Load Memory
 ↓
Retrieve Context
 ↓
Create Plan
 ↓
Route Agents
 ↓
Parallel / Sequential Execution
 ↓
Collect Results
 ↓
Conflict Resolution
 ↓
Confidence Evaluation
 ↓
Human Review (if required)
 ↓
Generate Final Response
 ↓
Audit Log
 ↓
End
```

---

# 8. graph.py Design

Nodes

- start
- validate
- load_memory
- retrieve_context
- planning
- route_agents
- execute_parallel
- execute_sequential
- aggregate
- validate_results
- human_review
- finalize
- audit
- end

Edges should support conditional branching and retry.

---

# 9. prompt.md

Must define:

- Role
- Mission
- Available agents
- Routing rules
- Delegation policy
- Safety policy
- Output schema
- Confidence rules

---

# 10. instruction.md

Execution policies

- Never bypass permissions.
- Never fabricate evidence.
- Prefer retrieval before reasoning.
- Delegate specialized work.
- Preserve citations.
- Record all orchestration decisions.

---

# 11. tools.py

Shared wrappers for:

- RAG
- Knowledge Graph
- Vector Search
- Database
- Evidence Store
- Notifications
- Report Service
- Metrics
- Authentication

Supervisor only invokes approved tools.

---

# 12. memory.py

Maintain:

- Active investigation
- Agent history
- Pending tasks
- Completed tasks
- Shared context
- Human feedback
- Retry history

---

# 13. schemas.py

Core models

- SupervisorRequest
- ExecutionPlan
- AgentTask
- AgentResult
- RoutingDecision
- FinalResponse
- ErrorResponse

---

# 14. config.yaml

Configuration

- Default model
- Temperature
- Token limits
- Parallelism
- Timeout
- Retry count
- Confidence threshold
- Human approval threshold
- Logging level

---

# 15. Parallel Execution

Run simultaneously when independent:

- Timeline
- Correlation
- GeoScope
- Evidence QA

Synchronize before report generation.

---

# 16. Conflict Resolution

If agents disagree:

1. Compare evidence.
2. Check citations.
3. Request re-analysis.
4. Lower confidence.
5. Escalate to reviewer if unresolved.

---

# 17. Human-in-the-Loop

Mandatory for:

- Case closure
- Legal recommendations
- Evidence deletion
- Low-confidence conclusions
- Report publication

---

# 18. Error Recovery

- Retry transient failures
- Skip unavailable optional agents
- Continue partial execution
- Escalate critical failures
- Preserve audit trail

---

# 19. Security

- RBAC
- JWT validation
- Tool authorization
- Prompt injection detection
- Secret isolation
- Output sanitization

---

# 20. Observability

Track

- Request latency
- Agent latency
- Routing accuracy
- Token usage
- Tool failures
- Retry count
- Confidence distribution

---

# 21. Testing

Unit:
- Planner
- Router
- Validator

Integration:
- Multi-agent orchestration
- Memory synchronization

End-to-End:
- Full investigation lifecycle
- Failure recovery
- Human approval flow

---

# 22. Acceptance Criteria

The Supervisor Agent is complete when it:

- Plans every investigation.
- Routes only necessary agents.
- Shares context consistently.
- Coordinates parallel execution.
- Produces deterministic orchestration.
- Maintains complete audit logs.
- Enforces security centrally.

---

# 23. Developer Checklist

- Define graph states.
- Implement routing logic.
- Add structured schemas.
- Validate every tool call.
- Test orchestration paths.
- Measure latency.
- Document workflows.

---

# 24. Guiding Principle

The Supervisor Agent acts as the trusted investigation orchestrator. It coordinates specialized AI agents, preserves context, enforces security and governance, validates evidence-driven outputs, and ensures every investigation remains explainable, auditable, scalable, and production-ready.
