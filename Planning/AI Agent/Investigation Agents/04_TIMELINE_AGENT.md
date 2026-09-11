
# 04_TIMELINE_AGENT.md

# CrimeKit Enterprise Timeline Agent

> Specialized AI agent responsible for reconstructing accurate chronological timelines from digital evidence, documents, media, logs, metadata, and investigator observations.

---

# 1. Agent Purpose

The Timeline Agent converts scattered evidence into a coherent, explainable sequence of events.

Its objective is to answer:

- What happened?
- When did it happen?
- In what order?
- Which evidence supports each event?
- Which events are missing or contradictory?

The Timeline Agent never creates events without supporting evidence.

---

# 2. Responsibilities

- Extract timestamps
- Normalize dates and time zones
- Build chronological timelines
- Merge events from multiple evidence sources
- Detect conflicting timestamps
- Identify missing temporal gaps
- Estimate confidence
- Produce evidence-backed event chains
- Provide structured output to downstream agents

---

# 3. Goals

- Accurate chronology
- Evidence-backed sequencing
- Explainable event ordering
- Deterministic output
- Support courtroom-quality reporting

---

# 4. Folder Structure

```text
timeline-agent/
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
- File timestamps
- EXIF data
- Email headers
- Chat logs
- OCR output
- Retrieved RAG context
- Knowledge graph entities
- Previous agent findings

---

# 6. Outputs

- Ordered timeline
- TimelineEvent objects
- Time conflicts
- Missing intervals
- Event confidence
- Evidence citations
- Recommendations

---

# 7. Capabilities

- Timestamp extraction
- Date normalization
- Timezone conversion
- Event sequencing
- Metadata correlation
- Duplicate event detection
- Timeline summarization
- Gap detection

---

# 8. Limitations

- No unsupported timestamps
- No fabricated chronology
- No evidence modification
- No legal interpretation

---

# 9. Reasoning Process

1. Validate request
2. Retrieve evidence
3. Extract temporal data
4. Normalize timestamps
5. Correlate related events
6. Order chronologically
7. Detect conflicts
8. Compute confidence
9. Produce explainable timeline

---

# 10. Decision Tree

Request
→ Evidence Available?
→ Extract Dates
→ Normalize
→ Merge Events
→ Conflict?
→ Resolve Using Evidence
→ Confidence Acceptable?
→ Publish
→ Otherwise Escalate

---

# 11. LangGraph State

Shared state contains:

- request_id
- investigation_id
- retrieved_context
- timestamps
- timeline_events
- conflicts
- citations
- confidence
- errors

---

# 12. graph.py Design

Nodes

- start
- validate
- retrieve_context
- extract_timestamps
- normalize_times
- correlate_events
- detect_conflicts
- build_timeline
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

Shared tools

- parse_datetime()
- extract_exif()
- inspect_metadata()
- search_vector()
- query_graph()
- fetch_case()
- normalize_timezone()
- generate_citations()

All tools expose typed contracts.

---

# 14. memory.py Design

Working Memory
- Active reasoning

Session Memory
- Current investigation

Timeline Memory
- Generated events

Vector Memory
- Retrieved evidence

Audit Memory
- Execution history

---

# 15. prompt.md Structure

Include:

- Identity
- Mission
- Allowed evidence
- Time reasoning rules
- Citation requirements
- Output schema
- Safety constraints
- Hallucination policy

---

# 16. skills.md Usage

Skills

- Timestamp Extraction
- Metadata Parsing
- Timeline Reconstruction
- Event Correlation
- Conflict Detection
- Chronology Summarization

Each skill defines inputs, outputs, required tools and confidence policy.

---

# 17. instruction.md

Rules

- Evidence before inference
- Normalize all timestamps
- Preserve original timestamp values
- Always attach citations
- Explain uncertainty
- Never reorder events without evidence

---

# 18. schemas.py

Models

- TimelineRequest
- TimelineResponse
- TimelineEvent
- TimeConflict
- Citation
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
- timezone_default
- timeout
- logging_level

---

# 20. RAG Strategy

Hybrid Retrieval

Evidence
→ Metadata Filter
→ Semantic Search
→ Vector Ranking
→ Timeline Context Assembly
→ Chronological Reasoning

Only retrieved evidence is used for event creation.

---

# 21. Knowledge Graph Usage

Use Neo4j to:

- Connect entities with events
- Trace repeated actors
- Link locations and timestamps
- Expand investigation context

---

# 22. Memory Strategy

Persist:

- Accepted events
- Rejected events
- Time conflicts
- Retrieval context
- Confidence history

Expire temporary reasoning after completion.

---

# 23. Retry Logic

Retry

- Retrieval failures
- Metadata parsing failures
- Temporary service outages

Use exponential backoff with configurable limits.

---

# 24. Fallback Strategy

If timestamps are unavailable:

- Use metadata
- Use related evidence
- Use graph relationships
- Request additional evidence
- Escalate to Supervisor

---

# 25. Observability

Monitor

- Extraction latency
- Timeline generation latency
- Retrieval latency
- Token usage
- Conflict count

---

# 26. Metrics

KPIs

- Timeline completeness
- Conflict resolution rate
- Citation coverage
- Average latency
- Confidence distribution
- Hallucination rate

---

# 27. Logging

Structured logs include:

- investigation_id
- request_id
- events_created
- conflicts
- tool_calls
- latency
- outcome

---

# 28. Security

- RBAC
- JWT validation
- Prompt injection protection
- Tool authorization
- Encrypted communication
- Output sanitization

---

# 29. Ethical Constraints

- Never alter evidence
- Preserve chain of custody
- Clearly distinguish inference from evidence
- Respect privacy
- Escalate uncertain conclusions

---

# 30. Hallucination Prevention

- Retrieval-first workflow
- Mandatory citations
- Metadata verification
- Confidence scoring
- Reject unsupported events

---

# 31. Testing

Unit Tests
- Timestamp parser
- Conflict detector
- Event sorter

Integration Tests
- RAG
- Knowledge graph
- Metadata extraction

End-to-End
- Multi-source timeline generation
- Supervisor integration
- Failure recovery

Regression
- Stable schemas
- Deterministic outputs

---

# 32. Acceptance Criteria

Production-ready when:

- Every event references evidence
- Events are chronologically ordered
- Time conflicts are reported
- Outputs follow schema
- Security checks pass
- Tests succeed

---

# 33. Developer Checklist

- Implement graph nodes
- Define prompt
- Implement tools
- Configure memory
- Build schemas
- Add retries
- Add observability
- Write automated tests
- Validate production readiness

---

# 34. Guiding Principle

The Timeline Agent serves as the trusted chronological reconstruction engine for CrimeKit. It transforms evidence into an auditable timeline by relying on retrieved facts, verified timestamps, metadata, and explainable reasoning while integrating seamlessly with the Supervisor Agent and the broader multi-agent investigation platform.
