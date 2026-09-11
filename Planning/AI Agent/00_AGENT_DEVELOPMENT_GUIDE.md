
# 00_AGENT_DEVELOPMENT_GUIDE.md

# CrimeKit Enterprise AI Agent Development Guide

> Master blueprint for designing, implementing, testing, deploying and maintaining every AI agent in the CrimeKit platform.

---

# 1. Vision

The AI Agent platform is designed as an enterprise-grade multi-agent system that assists investigators while remaining explainable, auditable, secure, ethical and scalable.

Goals:

- Production-ready
- Human-in-the-loop
- Explainable AI
- Modular agents
- Enterprise security
- High availability
- Observable
- Easy to extend

---

# 2. Agent Philosophy

Every agent must:

- Solve one primary responsibility.
- Never directly modify unrelated domains.
- Produce structured outputs.
- Explain important decisions.
- Operate through the Supervisor Agent.
- Be independently testable.
- Be replaceable without affecting the system.

---

# 3. Standard Agent Folder Structure

```text
agent-name/
│
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

Purpose of each file:

- **prompt.md** – system prompt and reasoning rules.
- **skills.md** – supported capabilities.
- **instruction.md** – execution policies.
- **graph.py** – LangGraph workflow.
- **tools.py** – tool definitions and wrappers.
- **memory.py** – conversation/context memory.
- **schemas.py** – typed request/response models.
- **config.yaml** – runtime configuration.

---

# 4. Enterprise Multi-Agent Architecture

```text
User
  │
Supervisor
  │
 ├── Detective Agent
 ├── Timeline Agent
 ├── Correlation Agent
 ├── GeoScope Agent
 ├── Evidence QA Agent
 ├── Testimony Agent
 ├── Report Agent
 └── Triage Agent
          │
 Shared Infrastructure
          │
RAG • PostgreSQL • Neo4j • pgvector • Elasticsearch • MinIO
```

---

# 5. Standard Execution Lifecycle

1. Receive task.
2. Validate input.
3. Load permissions.
4. Load shared context.
5. Retrieve relevant evidence.
6. Plan execution.
7. Invoke tools.
8. Update memory.
9. Validate output.
10. Return structured response.
11. Log audit event.

---

# 6. Agent Responsibilities

Every agent document should define:

- Mission
- Inputs
- Outputs
- Internal workflow
- Decision tree
- Tools
- Memory strategy
- Failure handling
- Retry policy
- Observability
- Security controls
- Acceptance criteria

---

# 7. Prompt Engineering Standards

Every prompt should include:

- Role
- Mission
- Constraints
- Available tools
- Response schema
- Safety rules
- Reasoning policy
- Output format

Avoid hidden assumptions and hallucinations.

---

# 8. Memory Standards

Memory layers:

- Working memory
- Session memory
- Investigation memory
- Long-term vector memory
- Knowledge graph memory

Agents should persist only relevant investigation context.

---

# 9. Tool Standards

All tools must:

- Have one responsibility.
- Validate inputs.
- Return structured errors.
- Support retries where safe.
- Log execution time.
- Never expose secrets.

---

# 10. LangGraph Standards

Each graph should include:

- Start node
- Planning node
- Retrieval node
- Tool node
- Validation node
- Final response node
- Error node

Graphs must avoid infinite loops and define explicit termination conditions.

---

# 11. RAG Standards

Use:

- Hybrid search
- Metadata filtering
- Semantic retrieval
- Citation tracking
- Source attribution

Generated outputs should reference retrieved evidence whenever possible.

---

# 12. Security Standards

- RBAC enforcement
- JWT authentication
- Principle of least privilege
- Encrypted secrets
- Audit logging
- Prompt injection protection
- Tool permission checks

---

# 13. Explainability

Each agent should expose:

- Why a conclusion was reached.
- Evidence used.
- Confidence level.
- Missing information.
- Recommended next actions.

---

# 14. Ethical AI Principles

- Preserve evidence integrity.
- Do not fabricate facts.
- Respect privacy.
- Minimize bias.
- Require human review for critical decisions.
- Clearly distinguish inference from evidence.

---

# 15. Testing Strategy

Every agent must include:

- Unit tests
- Tool tests
- Prompt regression tests
- Memory tests
- Integration tests
- End-to-end workflow tests

---

# 16. Observability

Capture:

- Latency
- Token usage
- Tool failures
- Retrieval quality
- Agent routing
- Success rate
- Error rate

---

# 17. Production Readiness Checklist

- Configuration externalized
- Secrets managed securely
- Logging enabled
- Monitoring configured
- Health checks implemented
- Retry logic verified
- Documentation complete
- Tests passing

---

# 18. Development Workflow

1. Design agent.
2. Define schemas.
3. Write prompt.
4. Implement graph.
5. Implement tools.
6. Add memory.
7. Configure runtime.
8. Write tests.
9. Validate with sample investigations.
10. Deploy through CI/CD.

---

# 19. Acceptance Criteria

An AI agent is considered production-ready only if it:

- Produces deterministic structured outputs.
- Handles failures gracefully.
- Uses shared infrastructure correctly.
- Logs all important actions.
- Is independently testable.
- Integrates with the Supervisor Agent.

---

# 20. Guiding Principle

Every CrimeKit AI agent should behave like a trustworthy digital investigator: secure, explainable, evidence-driven, modular, observable, and easy to evolve as the platform grows.
