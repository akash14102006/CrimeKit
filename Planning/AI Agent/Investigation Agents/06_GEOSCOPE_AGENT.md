
# 06_GEOSCOPE_AGENT.md

# CrimeKit Enterprise GeoScope Agent

> Specialized AI investigation agent responsible for geospatial intelligence, movement reconstruction, location correlation, route analysis, and spatial evidence reasoning.

---

# 1. Agent Purpose

The GeoScope Agent transforms location-related evidence into explainable spatial intelligence.

It reconstructs where events happened, how entities moved, and how locations are related while preserving evidence integrity.

---

# 2. Responsibilities

- Analyze GPS coordinates
- Correlate locations across evidence
- Reconstruct movement routes
- Detect geospatial anomalies
- Perform geofencing analysis
- Associate entities with locations
- Generate evidence-backed maps
- Produce spatial confidence scores

---

# 3. Goals

- Accurate spatial reconstruction
- Explainable location reasoning
- Reliable movement timelines
- Evidence-first conclusions
- Enterprise-grade reproducibility

---

# 4. Folder Structure

```text
geoscope-agent/
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
- GPS coordinates
- EXIF metadata
- Cell tower metadata
- Wi-Fi/Bluetooth observations
- Timeline events
- Knowledge graph entities
- RAG context
- Case metadata

---

# 6. Outputs

- Spatial report
- Route reconstruction
- Location clusters
- Geofence matches
- Heatmap-ready data
- Confidence score
- Evidence citations
- Investigation recommendations

---

# 7. Capabilities

- GPS parsing
- Reverse geocoding
- Route reconstruction
- Spatial clustering
- Distance analysis
- Travel pattern detection
- Geofence evaluation
- Location summarization

---

# 8. Limitations

- No fabricated coordinates
- No unsupported movement inference
- No evidence modification
- No legal conclusions

---

# 9. Reasoning Process

1. Validate request
2. Retrieve spatial evidence
3. Normalize coordinates
4. Correlate entities and locations
5. Build movement paths
6. Detect anomalies
7. Score confidence
8. Generate explainable output

---

# 10. Decision Tree

Receive Request
→ Spatial evidence available?
→ Retrieve context
→ Normalize locations
→ Correlate locations
→ Build route
→ Verify citations
→ Confidence acceptable?
→ Publish
→ Else escalate

---

# 11. LangGraph State

- request_id
- investigation_id
- coordinates
- locations
- routes
- geofences
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
- normalize_coordinates
- correlate_locations
- reconstruct_route
- detect_anomalies
- confidence_score
- finalize
- audit
- end

Conditional paths

- retry
- fallback
- supervisor_review

---

# 13. tools.py Design

Shared tools

- parse_coordinates()
- reverse_geocode()
- calculate_distance()
- search_vector()
- query_graph()
- fetch_case()
- geofence_check()
- cluster_locations()
- build_route()
- create_citations()

All tools expose typed request/response contracts.

---

# 14. memory.py Design

Working Memory
- Current reasoning

Session Memory
- Active investigation

Spatial Memory
- Accepted locations

Vector Memory
- Retrieved evidence

Knowledge Memory
- Graph references

Audit Memory
- Execution history

---

# 15. prompt.md Structure

Include:

- Identity
- Mission
- Spatial reasoning rules
- Available tools
- Evidence requirements
- Citation policy
- Confidence policy
- Output schema
- Safety constraints

---

# 16. skills.md Usage

Skills

- GPS Analysis
- Route Reconstruction
- Geofence Analysis
- Spatial Correlation
- Heatmap Preparation
- Location Clustering
- Movement Pattern Detection

Each skill defines purpose, inputs, outputs, required tools and confidence policy.

---

# 17. instruction.md

Rules

- Retrieve before reasoning
- Never invent locations
- Preserve original coordinates
- Always cite evidence
- Explain uncertainty
- Reject unsupported movement paths

---

# 18. schemas.py

Models

- GeoScopeRequest
- GeoScopeResponse
- Coordinate
- Location
- Route
- GeofenceMatch
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
- default_projection
- timeout
- logging_level
- cache_ttl

---

# 20. RAG Strategy

Pipeline

Intent
→ Metadata Filter
→ Vector Retrieval
→ Spatial Evidence Assembly
→ Knowledge Graph Expansion
→ Location Reasoning
→ Citation Verification

Only retrieved evidence may support spatial conclusions.

---

# 21. Knowledge Graph Usage

Use Neo4j to

- connect locations to entities
- identify recurring places
- expand travel relationships
- validate known associations
- discover indirect spatial links

---

# 22. Memory Strategy

Store

- accepted routes
- rejected routes
- verified coordinates
- geofence matches
- confidence history

Expire temporary reasoning after completion.

---

# 23. Retry Logic

Retry

- retrieval failures
- reverse geocoding failures
- temporary network issues

Use exponential backoff.

---

# 24. Fallback Strategy

If spatial data is incomplete

- use metadata
- use timeline references
- use graph relationships
- request additional evidence
- escalate to Supervisor

---

# 25. Observability

Capture

- retrieval latency
- geospatial processing latency
- graph query latency
- token usage
- route generation time

---

# 26. Metrics

- route accuracy
- citation coverage
- geofence precision
- average latency
- hallucination rate
- confidence distribution

---

# 27. Logging

Structured logs include

- request_id
- investigation_id
- coordinates_processed
- routes_generated
- tool_calls
- citations
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

- Respect privacy
- Preserve chain of custody
- Distinguish evidence from inference
- Avoid unsupported surveillance conclusions
- Escalate uncertain findings

---

# 30. Hallucination Prevention

- Retrieval-first reasoning
- Mandatory citations
- Coordinate validation
- Confidence scoring
- Reject unsupported routes
- Explain uncertainty

---

# 31. Testing

Unit

- coordinate parser
- route builder
- geofence checker

Integration

- RAG
- Neo4j
- mapping utilities

End-to-End

- movement reconstruction
- supervisor integration
- failure recovery

Regression

- schema validation
- prompt stability

---

# 32. Acceptance Criteria

Production ready when

- Every location is evidence-backed
- Routes are reproducible
- Confidence scores exist
- Schemas validate
- Security checks pass
- Tests succeed

---

# 33. Developer Checklist

- Implement graph nodes
- Define prompts
- Implement tools
- Configure memory
- Build schemas
- Configure retries
- Add observability
- Add security
- Write automated tests
- Validate production readiness

---

# 34. Guiding Principle

The GeoScope Agent is the spatial intelligence engine of CrimeKit. It transforms geospatial evidence into explainable, evidence-backed movement intelligence while operating under Supervisor orchestration with deterministic, secure, and production-ready workflows.
