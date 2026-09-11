
# 05_CORRELATION_AGENT.md

# CrimeKit Enterprise Correlation Agent

> Specialized investigation agent responsible for discovering relationships across evidence, entities, events, devices, locations, communications, and digital artifacts.

---

# 1. Agent Purpose

The Correlation Agent identifies meaningful connections that are not obvious when examining evidence individually. It fuses structured and unstructured evidence into an explainable relationship network that supports investigators without replacing human judgment.

---

# 2. Responsibilities

- Correlate evidence across sources
- Link entities, people, devices, accounts, files and locations
- Discover hidden relationships
- Detect repeated patterns
- Identify anomalies
- Build evidence-backed correlation graphs
- Score relationship confidence
- Produce explainable outputs with citations

---

# 3. Goals

- Maximize useful correlations
- Minimize false positives
- Preserve explainability
- Support downstream agents
- Maintain deterministic outputs

---

# 4. Folder Structure

```text
correlation-agent/
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
- Timeline events
- Evidence metadata
- Entity list
- RAG retrieval results
- Knowledge graph context
- Previous agent outputs

# 6. Outputs

- Correlation graph
- Linked entities
- Relationship scores
- Supporting evidence
- Confidence score
- Investigation recommendations
- Evidence citations

---

# 7. Capabilities

- Entity linking
- Multi-source evidence fusion
- Pattern discovery
- Relationship scoring
- Duplicate detection
- Cross-case correlation
- Graph traversal
- Anomaly detection

---

# 8. Limitations

- No unsupported relationships
- No fabricated links
- No evidence modification
- No legal conclusions

---

# 9. Reasoning Process

1. Validate request
2. Retrieve context
3. Extract entities
4. Build candidate relationships
5. Verify with evidence
6. Score confidence
7. Remove weak links
8. Produce explainable graph

---

# 10. Decision Tree

Receive request
→ Evidence available?
→ Retrieve context
→ Build candidate links
→ Verify citations
→ Confidence above threshold?
→ Publish
→ Otherwise request more evidence or escalate.

---

# 11. LangGraph State

State contains:

- request_id
- investigation_id
- retrieved_context
- entities
- relationships
- graph_updates
- confidence
- citations
- tool_results
- errors

---

# 12. graph.py Design

Nodes:

- start
- validate
- retrieve_context
- extract_entities
- discover_relationships
- verify_relationships
- score_confidence
- prune_low_confidence
- finalize
- audit
- end

Conditional paths:

- retry
- fallback
- supervisor_review

---

# 13. tools.py Design

Shared tools:

- search_vector()
- query_graph()
- entity_resolver()
- similarity_search()
- relationship_ranker()
- fetch_case()
- generate_citations()
- anomaly_detector()

Every tool validates inputs and returns structured responses.

---

# 14. memory.py Design

Working Memory:
- Current reasoning

Session Memory:
- Investigation context

Correlation Memory:
- Accepted links

Vector Memory:
- Retrieved evidence

Knowledge Memory:
- Graph references

Audit Memory:
- Decisions

---

# 15. prompt.md Structure

Include:

- Identity
- Mission
- Scope
- Available tools
- Correlation rules
- Citation policy
- Confidence policy
- Output schema
- Safety constraints

---

# 16. skills.md Usage

Skills:

- Entity Resolution
- Relationship Discovery
- Graph Reasoning
- Pattern Analysis
- Similarity Matching
- Cross-source Correlation
- Recommendation Generation

Each skill documents purpose, inputs, outputs, tools and expected confidence.

---

# 17. instruction.md

Rules:

- Retrieve before reasoning
- Never invent relationships
- Preserve citations
- Explain uncertainty
- Reject unsupported correlations
- Delegate specialized work when required

---

# 18. schemas.py

Models:

- CorrelationRequest
- CorrelationResponse
- Entity
- Relationship
- CorrelationGraph
- EvidenceCitation
- ConfidenceScore
- Recommendation
- ErrorResponse

---

# 19. config.yaml

Configuration:

- llm_model
- embedding_model
- retrieval_top_k
- similarity_threshold
- confidence_threshold
- retry_limit
- timeout
- logging_level
- cache_ttl

---

# 20. RAG Strategy

Hybrid retrieval pipeline:

Intent → Metadata Filter → Vector Search → Graph Expansion → Context Assembly → Correlation Reasoning → Citation Verification.

Only retrieved evidence may support relationship creation.

---

# 21. Knowledge Graph Usage

Use Neo4j to:

- Traverse entity relationships
- Discover indirect links
- Detect communities
- Expand investigation context
- Validate known connections

Never overwrite verified graph facts automatically.

---

# 22. Memory Strategy

Maintain:

- accepted relationships
- rejected relationships
- unresolved links
- retrieved evidence
- confidence history

---

# 23. Retry Logic

Retry only transient failures:

- retrieval
- graph queries
- network issues
- temporary service errors

Use exponential backoff.

---

# 24. Fallback Strategy

If correlation fails:

- Reduce search scope
- Query graph directly
- Use metadata matching
- Request additional evidence
- Escalate to Supervisor

---

# 25. Observability

Capture:

- Retrieval latency
- Graph query latency
- Correlation latency
- Token usage
- Relationship count
- Failure count

---

# 26. Metrics

- Correlation precision
- Correlation recall
- Citation coverage
- Graph expansion success
- Hallucination rate
- Average latency
- Confidence distribution

---

# 27. Logging

Structured logs:

- request_id
- investigation_id
- entities_processed
- relationships_created
- citations
- tool_calls
- latency
- outcome

---

# 28. Security

- JWT validation
- RBAC
- Tool authorization
- Prompt injection protection
- Secret isolation
- Output sanitization

---

# 29. Ethical Constraints

- Preserve evidence integrity
- Respect privacy
- Avoid demographic bias
- Distinguish inference from fact
- Require human review for high-risk findings

---

# 30. Hallucination Prevention

- Retrieval-first workflow
- Mandatory citations
- Relationship verification
- Confidence scoring
- Reject unsupported links
- Explain uncertainty

---

# 31. Testing

Unit Tests:
- Entity resolver
- Relationship scorer
- Graph traversal

Integration Tests:
- RAG
- Neo4j
- Memory synchronization

End-to-End:
- Multi-source investigation
- Supervisor orchestration
- Failure recovery

Regression:
- Prompt stability
- Schema validation

---

# 32. Acceptance Criteria

Production-ready when:

- Every relationship is evidence-backed
- Confidence scores are produced
- Schemas validate
- Security checks pass
- Supervisor integration succeeds
- Automated tests pass

---

# 33. Developer Checklist

- Implement graph nodes
- Define prompts
- Implement tools
- Configure memory
- Create schemas
- Configure retries
- Add observability
- Add security
- Write tests
- Validate production readiness

---

# 34. Guiding Principle

The Correlation Agent is the relationship intelligence engine of CrimeKit. It discovers explainable, evidence-backed connections across investigations by combining retrieval, graph reasoning, structured validation, and deterministic workflows while operating securely under the Supervisor Agent.
