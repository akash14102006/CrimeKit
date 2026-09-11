
# 03_DETECTIVE_AGENT.md

# CrimeKit Enterprise Detective Agent

> Primary investigation reasoning agent responsible for evidence-driven analysis, hypothesis generation, entity extraction, relationship discovery and investigation recommendations.

---

# 1. Agent Purpose

The Detective Agent acts as the lead digital investigator.

It never edits evidence.
It never produces legal conclusions.
It transforms raw evidence into structured investigative intelligence.

---

# 2. Responsibilities

- Analyze evidence
- Generate investigation hypotheses
- Discover entities
- Identify suspicious activities
- Recommend additional evidence
- Correlate findings
- Produce explainable reasoning
- Pass structured outputs to downstream agents

---

# 3. Goals

- Maximize evidence understanding
- Minimize hallucinations
- Preserve chain of custody
- Explain every conclusion
- Produce deterministic structured outputs

---

# 4. Folder Structure

```text
detective-agent/
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
- Evidence metadata
- Retrieved RAG context
- Knowledge graph context
- Previous agent outputs
- User permissions

# 6. Outputs

- Investigation summary
- Extracted entities
- Suspicious findings
- Confidence score
- Supporting evidence
- Citations
- Recommended next actions

---

# 7. Capabilities

- OCR reasoning
- Document analysis
- Image observation
- Metadata inspection
- Timeline clue detection
- Entity extraction
- Relationship discovery
- Evidence summarization
- Retrieval augmented reasoning

---

# 8. Limitations

- No evidence modification
- No legal verdicts
- No unsupported claims
- No fabricated citations
- No bypass of supervisor

---

# 9. Reasoning Process

1. Understand objective
2. Load context
3. Retrieve evidence
4. Validate permissions
5. Extract entities
6. Build hypotheses
7. Verify against retrieved evidence
8. Score confidence
9. Produce explainable output

---

# 10. Decision Tree

Request
→ Is evidence available?
→ If no: request retrieval.
→ If yes: analyze.
→ Confidence ≥ threshold?
→ Yes: publish findings.
→ No: recommend more evidence or human review.

---

# 11. LangGraph State

Global state fields:

- request_id
- investigation_id
- evidence_refs
- retrieved_chunks
- entities
- hypotheses
- confidence
- tool_results
- errors
- final_response

---

# 12. graph.py Design

Nodes:

- start
- validate_input
- retrieve_context
- inspect_evidence
- extract_entities
- build_hypotheses
- verify_claims
- score_confidence
- finalize
- audit
- end

Conditional edges:

- retry
- fallback
- human_review

---

# 13. tools.py Design

Shared tool interfaces:

- search_evidence()
- query_vector()
- query_graph()
- fetch_case()
- inspect_metadata()
- ocr_reader()
- image_reasoning()
- summarize_document()
- create_citation()

Every tool returns typed responses and structured errors.

---

# 14. memory.py Design

Working Memory:
- Current reasoning

Session Memory:
- Active investigation

Case Memory:
- Prior findings

Vector Memory:
- Semantic retrieval

Knowledge Memory:
- Entity graph references

Audit Memory:
- Decisions and timestamps

---

# 15. prompt.md Structure

Sections:

- Identity
- Mission
- Scope
- Constraints
- Available tools
- Memory usage
- Evidence rules
- Citation policy
- Reasoning steps
- Output JSON schema
- Safety
- Ethical rules
- Hallucination prevention

---

# 16. skills.md Usage

Declared capabilities:

- Entity Extraction
- Evidence Analysis
- Metadata Analysis
- OCR Interpretation
- Image Understanding
- Investigation Planning
- Evidence Correlation
- Recommendation Generation

Each skill declares:
- purpose
- input
- output
- required tools
- confidence policy

---

# 17. instruction.md

Execution rules:

- Retrieve before reasoning
- Always cite evidence
- Never invent entities
- Use structured outputs
- Preserve evidence integrity
- Escalate uncertainty
- Delegate specialist tasks to Supervisor when required

---

# 18. schemas.py

Models:

- DetectiveRequest
- DetectiveResponse
- Entity
- Finding
- Hypothesis
- EvidenceCitation
- Recommendation
- ConfidenceScore
- ErrorResponse

---

# 19. config.yaml

Configuration:

- model
- embedding_model
- max_tokens
- temperature
- retrieval_top_k
- confidence_threshold
- retry_limit
- timeout
- logging_level
- cache_ttl

---

# 20. RAG Strategy

Pipeline:

Intent
→ Hybrid Retrieval
→ Metadata Filter
→ Vector Ranking
→ Knowledge Graph Expansion
→ Context Assembly
→ Reasoning
→ Citation Verification

Retrieve only investigation-relevant content.

---

# 21. Knowledge Graph Usage

Use Neo4j to:

- resolve identities
- detect relationships
- connect evidence
- identify repeated entities
- discover investigation paths

Never overwrite graph facts directly.

---

# 22. Memory Strategy

Maintain:

- current task
- retrieved evidence
- validated findings
- unresolved questions
- hypotheses
- rejected hypotheses

Expire temporary reasoning after completion.

---

# 23. Retry Logic

Retry only:

- retrieval failures
- transient API failures
- timeout events

Maximum configurable retries with exponential backoff.

---

# 24. Fallback Strategy

If retrieval fails:

- search metadata
- reduce search scope
- query graph
- ask Supervisor for assistance
- request human review

---

# 25. Observability

Record:

- request latency
- retrieval latency
- reasoning latency
- token usage
- confidence
- tool usage

---

# 26. Metrics

KPIs:

- Precision
- Recall
- Citation coverage
- Hallucination rate
- Retry frequency
- Average response time
- Evidence utilization

---

# 27. Logging

Structured JSON logs:

- investigation_id
- request_id
- agent
- tool_calls
- evidence_refs
- latency
- outcome

---

# 28. Security

- RBAC
- JWT validation
- Prompt injection detection
- Secret isolation
- Tool authorization
- Output sanitization

---

# 29. Ethical Constraints

- Respect privacy
- Preserve chain of custody
- Distinguish evidence from inference
- Avoid demographic bias
- Require human oversight for high-risk findings

---

# 30. Hallucination Prevention

- Retrieval-first reasoning
- Mandatory citations
- Confidence scoring
- Evidence verification
- Reject unsupported claims
- Explain uncertainty

---

# 31. Testing

Unit:
- entity extraction
- hypothesis generation
- tool wrappers

Integration:
- RAG
- knowledge graph
- memory

End-to-End:
- complete investigation workflow
- failure handling
- supervisor integration

Regression:
- prompt stability
- deterministic schema outputs

---

# 32. Acceptance Criteria

Production ready when:

- Outputs are schema compliant
- Every finding references evidence
- Confidence is computed
- Supervisor integration passes
- Security checks pass
- Tests succeed

---

# 33. Developer Checklist

- Define prompts
- Implement graph nodes
- Implement tools
- Configure memory
- Define schemas
- Add retries
- Add observability
- Add security
- Write tests
- Validate production readiness

---

# 34. Guiding Principle

The Detective Agent behaves as an evidence-first digital investigator. Every conclusion must be transparent, reproducible, attributable to retrieved evidence, and orchestrated through the Supervisor Agent so that investigations remain secure, explainable, ethical, scalable, and enterprise-ready.
