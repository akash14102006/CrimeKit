
# 10_TRIAGE_AGENT.md

# CrimeKit Enterprise Triage Agent

> Specialized AI agent responsible for intelligent evidence intake, prioritization, routing, and case readiness assessment before deeper investigation by downstream agents.

---

# 1. Agent Purpose

The Triage Agent is the entry point for investigation workflows. It classifies incoming evidence, assesses urgency, estimates processing priority, detects duplicates, validates completeness, and routes work to the appropriate specialist agents under Supervisor orchestration.

The agent never makes legal conclusions or alters evidence.

---

# 2. Responsibilities

- Intake new evidence
- Validate submission completeness
- Classify evidence type
- Assess investigation priority
- Score case severity
- Detect duplicate evidence
- Route evidence to specialist agents
- Recommend missing artifacts
- Generate intake summary

---

# 3. Goals

- Fast evidence triage
- Consistent prioritization
- Accurate routing
- Reduced investigator workload
- Deterministic and explainable decisions

---

# 4. Folder Structure

```text
triage-agent/
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

# 5. Inputs

- Investigation request
- Case metadata
- Uploaded evidence
- Evidence metadata
- Chain-of-custody information
- User role and permissions
- RAG retrieval context
- Knowledge graph context

---

# 6. Outputs

- Intake summary
- Evidence classification
- Severity score
- Priority level
- Duplicate detection result
- Recommended downstream agents
- Missing evidence checklist
- Confidence score
- Evidence citations

---

# 7. Capabilities

- Evidence classification
- Risk scoring
- Priority assignment
- Duplicate detection
- Metadata validation
- Queue routing
- Checklist generation
- Intake summarization

---

# 8. Limitations

- No evidence modification
- No unsupported classifications
- No legal decisions
- No fabricated metadata

---

# 9. Reasoning Process

1. Validate request
2. Verify permissions
3. Inspect evidence metadata
4. Classify evidence
5. Detect duplicates
6. Assess severity and priority
7. Select downstream agents
8. Score confidence
9. Produce structured intake report

---

# 10. Decision Tree

Request
→ Valid submission?
→ Metadata complete?
→ Duplicate?
→ Classify evidence
→ Severity high?
→ Immediate routing
→ Standard routing
→ Publish intake summary
→ Escalate if uncertainty exceeds threshold

---

# 11. LangGraph State

- request_id
- investigation_id
- evidence_inventory
- classifications
- severity
- priority
- routing_plan
- confidence
- citations
- tool_results
- errors

---

# 12. graph.py Design

Nodes

- start
- validate_request
- validate_permissions
- inspect_metadata
- classify_evidence
- detect_duplicates
- assess_severity
- plan_routing
- confidence_score
- finalize
- audit
- end

Conditional branches

- retry
- fallback
- supervisor_review

---

# 13. tools.py Design

Core tools

- inspect_metadata()
- classify_evidence()
- duplicate_search()
- hybrid_retrieval()
- query_graph()
- fetch_case()
- severity_scorer()
- routing_planner()
- citation_builder()

All tools expose typed request and response contracts.

---

# 14. memory.py Design

Working Memory
- Current intake reasoning

Session Memory
- Active case context

Triage Memory
- Previous intake decisions

Vector Memory
- Retrieved evidence

Knowledge Memory
- Entity relationships

Audit Memory
- Routing history

---

# 15. prompt.md Structure

- Identity
- Mission
- Scope
- Intake workflow
- Classification rules
- Routing rules
- Citation policy
- Confidence policy
- Output schema
- Safety constraints

---

# 16. skills.md Usage

Skills

- Evidence Classification
- Severity Assessment
- Priority Assignment
- Duplicate Detection
- Metadata Validation
- Routing Recommendation
- Intake Summarization

Each skill specifies purpose, inputs, outputs, required tools, validation rules, and confidence expectations.

---

# 17. instruction.md

Rules

- Validate before reasoning
- Preserve evidence integrity
- Never invent metadata
- Route using evidence-backed criteria
- Always explain uncertainty
- Attach supporting citations where applicable

---

# 18. schemas.py

Models

- TriageRequest
- TriageResponse
- EvidenceItem
- Classification
- SeverityScore
- PriorityLevel
- RoutingDecision
- Citation
- ConfidenceScore
- ErrorResponse

---

# 19. config.yaml

Configuration

- llm_model
- embedding_model
- retrieval_top_k
- severity_thresholds
- priority_rules
- confidence_threshold
- retry_limit
- timeout
- logging_level
- cache_ttl

---

# 20. RAG Strategy

Pipeline

Request
→ Metadata Filter
→ Hybrid Retrieval
→ Similar Case Lookup
→ Knowledge Graph Expansion
→ Classification
→ Routing Decision
→ Citation Verification

Only verified retrieved context is used for routing decisions.

---

# 21. Knowledge Graph Usage

Use Neo4j to

- identify related cases
- discover linked entities
- detect repeated evidence
- enrich routing context
- support duplicate detection

---

# 22. Memory Strategy

Maintain

- accepted classifications
- rejected classifications
- routing history
- severity history
- confidence history

Expire temporary reasoning after workflow completion.

---

# 23. Retry Logic

Retry

- retrieval failures
- duplicate search failures
- graph query failures
- temporary service outages

Use exponential backoff with configurable limits.

---

# 24. Fallback Strategy

If classification cannot be completed

- broaden retrieval
- inspect metadata only
- request additional evidence
- route to manual review
- escalate to Supervisor

---

# 25. Observability

Capture

- intake latency
- classification latency
- routing latency
- token usage
- duplicate detection rate

---

# 26. Metrics

- Classification accuracy
- Routing accuracy
- Duplicate detection precision
- Intake completion rate
- Average latency
- Hallucination rate

---

# 27. Logging

Structured logs

- request_id
- investigation_id
- classifications
- severity
- routing_plan
- citations
- tool_calls
- latency
- outcome

---

# 28. Security

- RBAC
- JWT validation
- Tool authorization
- Prompt injection detection
- Secret isolation
- Output sanitization
- Audit logging

---

# 29. Ethical Constraints

- Preserve chain of custody
- Respect privacy
- Avoid unsupported prioritization
- Distinguish evidence from inference
- Require human review for high-impact routing

---

# 30. Hallucination Prevention

- Retrieval-first workflow
- Mandatory validation
- Confidence scoring
- Duplicate verification
- Reject unsupported classifications
- Explain uncertainty

---

# 31. Testing

Unit

- classifier
- severity scorer
- duplicate detector
- routing planner

Integration

- RAG
- Neo4j
- Supervisor
- Memory synchronization

End-to-End

- evidence intake
- routing workflow
- failure recovery

Regression

- schema validation
- prompt stability
- routing consistency

---

# 32. Acceptance Criteria

Production ready when

- Evidence is consistently classified
- Routing is explainable
- Confidence scores are produced
- Duplicate detection functions correctly
- Security checks pass
- Automated tests succeed

---

# 33. Developer Checklist

- Implement graph nodes
- Build prompt package
- Implement tool wrappers
- Configure memory
- Create schemas
- Configure retries
- Add observability
- Add security
- Write automated tests
- Validate production readiness

---

# 34. Guiding Principle

The Triage Agent is the intelligent intake and orchestration gateway for CrimeKit. Every routing decision must be evidence-driven, transparent, reproducible, and auditable so that downstream investigation agents receive complete, prioritized, and trustworthy case context.
