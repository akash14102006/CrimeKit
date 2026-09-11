
# 01_SHARED_AGENT_INFRASTRUCTURE.md

# CrimeKit Shared AI Agent Infrastructure

> Enterprise blueprint for all reusable infrastructure used by every AI agent.

---

# 1. Purpose

The shared infrastructure provides common capabilities so individual agents only implement domain reasoning. Every agent must depend on these shared components instead of creating duplicate implementations.

---

# 2. Design Principles

- Single source of truth
- Reusable components
- Strong typing
- Security first
- Explainable AI
- Stateless execution with managed memory
- Production scalability
- Vendor-neutral architecture

---

# 3. Shared Directory

```text
ai-agents/
└── shared/
    ├── prompts/
    ├── tools/
    ├── memory/
    ├── rag/
    ├── graph/
    ├── schemas/
    ├── config/
    ├── logging/
    ├── telemetry/
    ├── auth/
    ├── policies/
    ├── events/
    ├── cache/
    ├── utilities/
    ├── retry/
    ├── validation/
    └── exceptions/
```

---

# 4. Shared Prompt Framework

All prompts inherit common sections:

- Role
- Mission
- Scope
- Available tools
- Available memory
- Safety rules
- Ethical constraints
- Output schema
- Citation requirements
- Confidence policy
- Hallucination prevention

Prompt inheritance ensures consistent reasoning across all agents.

---

# 5. Shared Tool Framework

Every tool must expose:

- Name
- Description
- Input schema
- Output schema
- Permission requirements
- Timeout
- Retry policy
- Audit metadata
- Error model

Categories:

- Database
- Evidence
- Search
- Knowledge Graph
- OCR
- Vision
- Audio
- Timeline
- Geospatial
- Reporting
- Notification
- External APIs

---

# 6. Shared Memory Architecture

Memory layers:

1. Request Memory
2. Agent Working Memory
3. Investigation Memory
4. Vector Memory
5. Knowledge Graph Memory
6. Audit Memory

Rules:

- Never store secrets.
- Preserve evidence references.
- Expire temporary memory.
- Encrypt persistent state.

---

# 7. Shared RAG Infrastructure

Pipeline:

```text
User Query
    ↓
Intent Analysis
    ↓
Hybrid Retrieval
    ↓
Metadata Filtering
    ↓
Vector Ranking
    ↓
Knowledge Graph Expansion
    ↓
Context Assembly
    ↓
Agent Reasoning
```

Sources:

- PostgreSQL
- pgvector
- Elasticsearch
- Neo4j
- MinIO metadata
- Reports
- Evidence

---

# 8. Shared LangGraph State

Global state contains:

- Request ID
- Investigation ID
- User Context
- Agent Context
- Retrieved Evidence
- Tool Results
- Memory Snapshot
- Confidence Scores
- Errors
- Final Response

---

# 9. Shared Configuration

Central configuration includes:

- Model selection
- Embedding provider
- Vector dimensions
- API endpoints
- Retry limits
- Token limits
- Cache TTL
- Logging levels
- Feature flags

Environment values must never be hardcoded.

---

# 10. Shared Schemas

Reusable schemas:

- AgentRequest
- AgentResponse
- ToolRequest
- ToolResponse
- EvidenceReference
- TimelineEvent
- EntityNode
- RelationshipEdge
- ConfidenceScore
- Citation
- ErrorResponse

---

# 11. Shared Logging

Every execution records:

- Request ID
- Agent Name
- User
- Investigation
- Tool Calls
- Duration
- Token Usage
- Errors
- Final Status

Use structured JSON logging.

---

# 12. Observability

Collect metrics:

- Agent latency
- Retrieval latency
- LLM latency
- Tool latency
- Cache hit ratio
- Success rate
- Failure rate
- Hallucination detection events

Integrations:

- Prometheus
- Grafana
- OpenTelemetry

---

# 13. Shared Cache

Recommended layers:

- Redis
- In-memory cache
- Embedding cache
- Prompt cache
- Tool cache

Cache only deterministic results.

---

# 14. Event Bus

Publish events:

- AgentStarted
- RetrievalCompleted
- ToolExecuted
- MemoryUpdated
- AgentCompleted
- AgentFailed
- ReportGenerated

Consumers should remain loosely coupled.

---

# 15. Retry Strategy

Retry only transient failures.

Policies:

- Exponential backoff
- Circuit breaker
- Timeout protection
- Maximum retry count
- Dead-letter handling

Never retry destructive operations automatically.

---

# 16. Validation Layer

Validate:

- Input schemas
- Tool permissions
- File types
- UUIDs
- Investigation ownership
- Evidence existence

Reject invalid requests before reasoning begins.

---

# 17. Security Infrastructure

Common services:

- JWT validation
- RBAC
- Secret manager
- Encryption utilities
- Prompt injection detection
- Output sanitization
- Data masking

---

# 18. Human-in-the-Loop

Require approval for:

- Evidence deletion
- Report publication
- High-risk conclusions
- Legal recommendations

Record reviewer identity and timestamp.

---

# 19. Testing Infrastructure

Shared fixtures:

- Mock evidence
- Mock graph
- Mock vector store
- Mock users
- Prompt regression datasets
- Benchmark scenarios

Support:

- Unit tests
- Integration tests
- End-to-end tests
- Performance tests

---

# 20. Deployment Standards

Infrastructure should support:

- Docker
- Kubernetes
- Horizontal scaling
- Blue/Green deployment
- Rolling updates
- CI/CD
- Secrets management
- Health checks

---

# 21. Acceptance Criteria

The shared infrastructure is complete when:

- Every agent uses shared prompts.
- Every agent shares schemas.
- Memory is centralized.
- Tool contracts are standardized.
- Logging is consistent.
- Observability is enabled.
- Security is enforced centrally.
- Components are independently testable.

---

# 22. Developer Checklist

- Reuse before creating new modules.
- Keep interfaces stable.
- Version shared schemas.
- Document every tool.
- Add automated tests.
- Monitor performance.
- Avoid agent-specific logic in shared code.

---

# 23. Guiding Principle

The shared infrastructure is the enterprise foundation of the CrimeKit AI ecosystem. Individual agents should focus only on reasoning and investigation logic while all common capabilities—memory, retrieval, security, tooling, observability, validation, and configuration—are implemented once, tested once, and reused everywhere.
