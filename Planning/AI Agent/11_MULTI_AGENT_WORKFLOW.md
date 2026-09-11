
# 11_MULTI_AGENT_WORKFLOW.md

# CrimeKit Enterprise Multi-Agent Workflow

## Purpose

This document defines how every CrimeKit AI agent collaborates under the Supervisor Agent to perform an end-to-end investigation while maintaining explainability, security, traceability, and evidence integrity.

---

# 1. Workflow Overview

```
Evidence Intake
      │
      ▼
Triage Agent
      │
      ▼
Supervisor Agent
      │
 ┌────┼──────────────────────────────────────┐
 ▼    ▼          ▼           ▼              ▼
Detective   Timeline   Correlation   GeoScope   Testimony
      └──────────────┬───────────────┘
                     ▼
             Evidence QA Agent
                     ▼
               Report Agent
                     ▼
          Human Review & Approval
                     ▼
             Court-ready Report
```

---

# 2. Agent Responsibilities

| Agent | Primary Responsibility |
|--------|------------------------|
| Supervisor | Orchestrates workflow and routing |
| Triage | Intake, validation, prioritization |
| Detective | Evidence analysis and hypotheses |
| Timeline | Chronological reconstruction |
| Correlation | Relationship discovery |
| GeoScope | Geospatial intelligence |
| Testimony | Witness/interview analysis |
| Evidence QA | Evidence-backed question answering |
| Report | Court-ready report generation |

---

# 3. End-to-End Investigation Lifecycle

1. Evidence ingestion
2. Metadata validation
3. Chain of custody verification
4. Case initialization
5. Triage classification
6. Supervisor routing
7. Parallel specialist agent execution
8. Knowledge graph enrichment
9. RAG retrieval
10. Cross-agent validation
11. Evidence QA
12. Report generation
13. Human review
14. Final export

---

# 4. Shared LangGraph State

Shared state includes:

- request_id
- investigation_id
- case_id
- evidence_inventory
- retrieved_context
- entities
- timeline
- relationships
- locations
- testimony
- findings
- citations
- confidence
- audit_log
- errors

---

# 5. Agent Communication

Agents exchange only structured schemas.

No agent modifies another agent's outputs directly.

Supervisor manages all orchestration and state transitions.

---

# 6. RAG Workflow

Request
→ Hybrid Retrieval
→ Metadata Filtering
→ Vector Search
→ Knowledge Graph Expansion
→ Context Assembly
→ Agent Reasoning
→ Citation Verification

---

# 7. Knowledge Graph Workflow

Neo4j stores:

- entities
- locations
- devices
- evidence
- events
- relationships

Agents query but do not overwrite validated graph facts automatically.

---

# 8. Memory Strategy

- Working Memory
- Session Memory
- Investigation Memory
- Vector Memory
- Knowledge Memory
- Audit Memory

---

# 9. Retry & Recovery

Retry:

- retrieval failures
- transient API failures
- graph failures

Fallback:

- broaden retrieval
- metadata search
- supervisor escalation
- human review

---

# 10. Observability

Capture:

- latency
- token usage
- tool usage
- retries
- confidence
- citations
- workflow duration

---

# 11. Logging

Structured logs:

- request_id
- investigation_id
- active_agent
- workflow_step
- tool_calls
- outcome
- timestamps

---

# 12. Security

- JWT authentication
- RBAC authorization
- Prompt injection protection
- Secret management
- Audit logging
- Output sanitization

---

# 13. Hallucination Prevention

- Retrieval-first reasoning
- Mandatory citations
- Cross-agent validation
- Confidence scoring
- Human review for high-risk outputs

---

# 14. Testing

Unit:
- Individual agents

Integration:
- Agent communication
- RAG
- Neo4j
- Memory

End-to-End:
- Complete investigation pipeline
- Report generation
- Failure recovery

---

# 15. Acceptance Criteria

The workflow is production-ready when:

- All agents communicate through schemas
- Every conclusion references evidence
- Workflow is reproducible
- Security controls pass
- Automated tests succeed
- Human review is supported

---

# 16. Developer Checklist

- Define workflow graph
- Implement state management
- Configure agent routing
- Validate schemas
- Integrate RAG
- Integrate Neo4j
- Add observability
- Add security
- Write tests
- Validate production readiness

---

# Guiding Principle

CrimeKit operates as a coordinated multi-agent investigation platform where specialized agents collaborate through the Supervisor Agent using shared state, verified evidence, RAG, and knowledge graphs to deliver transparent, explainable, and court-ready investigative outcomes.
