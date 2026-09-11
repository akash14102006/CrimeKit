
# 07_TESTIMONY_AGENT.md

# CrimeKit Enterprise Testimony Agent

> Specialized AI agent responsible for analyzing witness statements, interview transcripts, victim narratives, suspect interviews, and officer notes to produce evidence-backed, explainable testimony intelligence.

---

# 1. Agent Purpose

The Testimony Agent transforms natural-language statements into structured investigative knowledge.

It compares testimonies with available evidence, identifies agreements and contradictions, extracts factual claims, and prepares testimony summaries for investigators and court reporting.

The agent does **not** determine guilt, innocence, or witness credibility as a legal fact.

---

# 2. Responsibilities

- Analyze witness statements
- Parse interview transcripts
- Extract factual claims
- Compare multiple testimonies
- Detect contradictions
- Detect corroborating statements
- Align testimony with evidence
- Generate structured summaries
- Produce evidence-backed citations

---

# 3. Goals

- Preserve original meaning
- Avoid introducing unsupported facts
- Maximize explainability
- Support investigators and report generation
- Produce deterministic structured outputs

---

# 4. Folder Structure

```text
testimony-agent/
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
- Witness statements
- Interview transcripts
- Audio transcript text
- Timeline events
- Correlation results
- Evidence metadata
- RAG context
- Knowledge graph context

---

# 6. Outputs

- Structured testimony summary
- Extracted factual claims
- Contradictions
- Corroborating evidence
- Confidence score
- Evidence citations
- Recommendations for investigators

---

# 7. Capabilities

- Statement summarization
- Claim extraction
- Contradiction detection
- Similarity comparison
- Speaker separation
- Entity extraction
- Sentiment/context awareness
- Evidence alignment

---

# 8. Limitations

- No legal conclusions
- No fabricated statements
- No credibility determination without evidence
- No modification of original testimony

---

# 9. Reasoning Process

1. Validate request
2. Retrieve supporting evidence
3. Parse testimony
4. Extract claims
5. Compare with evidence
6. Compare with other testimonies
7. Identify contradictions
8. Compute confidence
9. Produce structured response

---

# 10. Decision Tree

Request
→ Testimony available?
→ Parse transcript
→ Extract claims
→ Compare evidence
→ Contradiction?
→ Flag with citations
→ Confidence acceptable?
→ Publish
→ Otherwise escalate to Supervisor

---

# 11. LangGraph State

- request_id
- investigation_id
- testimony_segments
- extracted_claims
- corroborations
- contradictions
- confidence
- citations
- tool_results
- errors

---

# 12. graph.py Design

Nodes

- start
- validate
- retrieve_context
- parse_testimony
- extract_claims
- compare_evidence
- detect_contradictions
- score_confidence
- finalize
- audit
- end

Conditional branches

- retry
- fallback
- supervisor_review

---

# 13. tools.py Design

Shared tools

- retrieve_rag()
- search_vector()
- query_graph()
- compare_similarity()
- extract_entities()
- summarize_text()
- create_citations()
- fetch_case()

All tools use typed request/response schemas.

---

# 14. memory.py Design

Working Memory
- Active reasoning

Session Memory
- Investigation context

Testimony Memory
- Accepted claims

Vector Memory
- Retrieved evidence

Knowledge Memory
- Linked entities

Audit Memory
- Decisions and timestamps

---

# 15. prompt.md Structure

Sections

- Identity
- Mission
- Scope
- Available tools
- Testimony analysis rules
- Citation policy
- Confidence policy
- Output schema
- Safety constraints
- Hallucination prevention

---

# 16. skills.md Usage

Skills

- Claim Extraction
- Contradiction Detection
- Testimony Comparison
- Entity Recognition
- Evidence Alignment
- Summary Generation

Each skill defines purpose, inputs, outputs, required tools and confidence policy.

---

# 17. instruction.md

Rules

- Retrieve before reasoning
- Preserve original wording where possible
- Never invent testimony
- Distinguish fact from inference
- Attach evidence citations
- Explain uncertainty

---

# 18. schemas.py

Models

- TestimonyRequest
- TestimonyResponse
- TestimonySegment
- Claim
- Contradiction
- Corroboration
- EvidenceCitation
- ConfidenceScore
- Recommendation
- ErrorResponse

---

# 19. config.yaml

Configuration

- llm_model
- embedding_model
- retrieval_top_k
- confidence_threshold
- retry_limit
- timeout
- logging_level
- cache_ttl

---

# 20. RAG Strategy

Request
→ Hybrid Retrieval
→ Metadata Filter
→ Vector Search
→ Evidence Assembly
→ Testimony Analysis
→ Citation Verification

Only retrieved evidence may support conclusions.

---

# 21. Knowledge Graph Usage

Use Neo4j to

- link witnesses
- associate entities
- connect statements with events
- identify repeated testimony
- expand investigation context

---

# 22. Memory Strategy

Maintain

- accepted claims
- rejected claims
- contradiction history
- evidence references
- confidence history

---

# 23. Retry Logic

Retry only

- retrieval failures
- temporary service failures
- timeout events

Use exponential backoff.

---

# 24. Fallback Strategy

If evidence is insufficient

- reduce search scope
- query graph
- request additional evidence
- escalate to Supervisor
- recommend human review

---

# 25. Observability

Monitor

- parsing latency
- retrieval latency
- contradiction detection latency
- token usage
- confidence distribution

---

# 26. Metrics

- claim extraction accuracy
- contradiction precision
- citation coverage
- response latency
- hallucination rate
- evidence utilization

---

# 27. Logging

Structured logs

- request_id
- investigation_id
- claims_extracted
- contradictions_found
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
- Output sanitization
- Secret isolation

---

# 29. Ethical Constraints

- Respect privacy
- Preserve testimony integrity
- Distinguish evidence from inference
- Avoid biased language
- Require human oversight for high-risk conclusions

---

# 30. Hallucination Prevention

- Retrieval-first reasoning
- Mandatory citations
- Claim verification
- Confidence scoring
- Reject unsupported statements
- Explain uncertainty

---

# 31. Testing

Unit
- claim extraction
- contradiction detection
- summarization

Integration
- RAG
- Knowledge graph
- memory synchronization

End-to-End
- multi-witness analysis
- supervisor orchestration
- failure recovery

Regression
- schema validation
- prompt stability

---

# 32. Acceptance Criteria

Production ready when

- Every claim is evidence-backed
- Contradictions are explainable
- Output follows schemas
- Confidence is computed
- Security checks pass
- Tests succeed

---

# 33. Developer Checklist

- Implement graph nodes
- Create prompts
- Implement tools
- Configure memory
- Define schemas
- Add retries
- Enable observability
- Add security
- Write automated tests
- Validate production readiness

---

# 34. Guiding Principle

The Testimony Agent is the narrative intelligence engine of CrimeKit. It converts human statements into structured, evidence-backed investigative knowledge while preserving testimony integrity, supporting explainable reasoning, and operating under Supervisor orchestration for secure, auditable, production-ready investigations.
