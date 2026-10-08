# CRIMEKIT — GRAPH API LAYER

## MASTER IMPLEMENTATION PROMPT

### Prompt #6 — Production Graph API • Neo4j Intelligence API • 3D Graph Read Model • Forensic GraphRAG

## 0. MISSION

Act as a world-class Principal Graph/API Architect, Neo4j Architect, FastAPI Staff Engineer, Distributed Systems Engineer, Digital Forensics Architect, 3D Data Contract Architect, Security Architect, AI/GraphRAG Architect and Production QA Lead.

Your mission is to implement the CrimeKit **Graph API Layer** as an enterprise production boundary between the authoritative CrimeKit platform and the Neo4j forensic knowledge graph.

The Graph API is NOT a thin `/graph` endpoint.

It is a controlled translation layer that converts graph knowledge into:
- investigator-safe graph views
- progressive 3D graph data
- evidence/provenance navigation
- timeline context
- graph-diff/replay information
- controlled graph analytics
- AI-readable structured graph context
- realtime graph updates

The implementation must be:
scalable • explainable • ethical • secure • case-scoped • tenant-safe where applicable • observable • testable • resilient • versioned • reproducible • production-ready.

## 1. TARGET ARCHITECTURE

```text
                         CRIMEKIT
                            |
                  Next.js / React / 3D UI
                            |
                            v
                     FASTAPI GRAPH API
                            |
              +-------------+-------------+
              |                           |
       Auth / Case Policy            Graph Service
              |                           |
              +-------------+-------------+
                            |
                     Query Policy
                            |
                     Graph Repository
                            |
                       Neo4j Driver
                            |
                            v
                        NEO4J AURA
                   /         |                        Cypher       GDS      Vector/Search
                            |
                            v
                     Graph Read Model
                            |
               +------------+------------+
               |            |            |
              3D        Inspector      AI Tools
               |            |            |
               +------------+------------+
                            |
                    Evidence / Timeline
                            |
                      Human Review


DEVELOPER / AGENT PLANE

Google Antigravity
        |
        v
Official Neo4j MCP
        |
        v
Neo4j DEV / STAGING
```

## 2. SOURCE-OF-TRUTH CONTRACT

| Layer | Responsibility |
|---|---|
| PostgreSQL | authoritative CrimeKit domain/case records |
| Object Storage | original evidence and binaries |
| Redis/Event Layer | events, jobs, realtime transport |
| Neo4j | relationship intelligence projection |
| GDS | bounded graph analytics |
| pgvector | existing semantic/vector retrieval where already used |
| Graph API | authorization, query policy, semantic DTOs |
| 3D UI | visualization and interaction |
| AI | grounded reasoning/explanation |
| Neo4j MCP | developer/agent graph tooling |

Never silently make Neo4j the forensic source of truth.

## 3. NON-NEGOTIABLE RULES

- Browser MUST NOT connect directly to Neo4j.
- Browser MUST NOT connect directly to MCP.
- Graph API MUST enforce case authorization server-side.
- Graph API MUST enforce tenant scope where multi-tenancy exists.
- Every traversal MUST be bounded.
- Every user-provided Cypher value MUST be parameterized.
- Do not expose arbitrary investigator-facing Cypher.
- Do not expose unrestricted graph dumps.
- Do not hide contradictions.
- Do not convert similarity into identity.
- Do not convert graph centrality into guilt.
- Do not convert anomaly into crime.
- Do not create fake graph nodes/edges for visual density.
- Do not fabricate provenance, confidence or freshness.
- GET operations must not silently mutate canonical graph state.
- MCP is a developer/tooling plane, not the production application API.

## 4. CURRENT NEO4J DRIVER PRINCIPLES

Use the official Neo4j Python driver already compatible with the actual CrimeKit runtime.

Current Neo4j documentation states that the official Python Driver is the supported Python application library; `verify_connectivity()` can validate connectivity; sessions/transactions are the primary database access mechanisms; and transaction functions can retry, so transaction functions should be idempotent. Parameterized Cypher is recommended instead of string-building user values. citeturn425442search9turn425442search0turn425442search8

Implementation implications:
- one shared application driver abstraction
- clean session lifecycle
- managed transactions for logical multi-query units
- retry only transient/retryable failures
- bounded timeouts
- parameterized queries
- clean driver shutdown

## 5. MCP + ANTIGRAVITY BOUNDARY

```text
PRODUCTION APPLICATION:
CrimeKit Frontend → FastAPI Graph API → Neo4j

DEVELOPER / AGENT:
Google Antigravity → Official Neo4j MCP → Neo4j DEV/STAGING
```

Current official Neo4j MCP documentation lists:
`get-schema`
`read-cypher`
`write-cypher`
`list-gds-procedures`

and documents `NEO4J_READ_ONLY=true` to disable write tools. The documentation also cautions about LLM-generated write operations. citeturn425442search1turn425442search2

Use readonly MCP by default for production-adjacent development.

## 6. REPOSITORY-FIRST IMPLEMENTATION

Before touching code:
1. inspect repository structure
2. inspect current FastAPI graph routes
3. inspect Neo4j driver integration
4. inspect services/repositories
5. inspect existing graph DTOs
6. inspect auth/case/RBAC
7. inspect Redis/realtime flow
8. inspect 3D frontend graph consumer
9. inspect graph schema/migrations
10. inspect tests
11. inspect MCP configuration
12. inspect deployment/secrets

Never create duplicate graph abstractions before proving the current ones are insufficient.

## 7. CLASSIFICATION

Classify existing graph/API components as:
- IMPLEMENTED
- PARTIAL
- MOCKED
- DUPLICATED
- DEAD
- DEPRECATED
- PLANNED
- UNKNOWN

## 8. SINGLE GRAPH ACCESS ABSTRACTION

Preferred logical structure:

```text
FastAPI Router
    ↓
Authorization / Scope
    ↓
Graph Service
    ↓
Graph Repository
    ↓
Neo4j Driver
```

Do not put complex Cypher into every router.
Do not allow multiple competing Neo4j clients.

## 9. GRAPH SCOPE

Create a trusted scope concept such as:

```text
GraphScope
  tenant_id
  case_id
  investigation_id
  user_id
  permissions
```

Every graph operation must receive trusted authorization scope.

## 10. AUTHORIZATION PIPELINE

```text
Request
  ↓
Authentication
  ↓
Tenant resolution
  ↓
Case access check
  ↓
Permission check
  ↓
Query scope validation
  ↓
Query budget
  ↓
Neo4j
  ↓
DTO redaction
  ↓
Response
```

Do not query Neo4j first and authorize later.

## 11. PERMISSIONS

Potential permission model:

| Permission | Purpose |
|---|---|
| graph.read | read authorized graph data |
| graph.expand | expand neighborhood |
| graph.path | path analysis |
| graph.provenance | provenance inspection |
| graph.timeline | graph-linked timeline |
| graph.analytics | controlled graph analytics |
| graph.export | graph export |
| graph.review | review candidate/derived relations |
| graph.admin | graph maintenance |

Use the actual CrimeKit RBAC model if it already exists.

## 12. CORE API DESIGN

Do NOT design:

```text
GET /graph?cypher=<arbitrary query>
```

Design task-specific operations:

```text
GET  /cases/{case_id}/graph/overview
GET  /cases/{case_id}/graph/entities/{entity_id}
GET  /cases/{case_id}/graph/entities/{entity_id}/neighbors
GET  /cases/{case_id}/graph/search
POST /cases/{case_id}/graph/path
GET  /cases/{case_id}/graph/timeline
GET  /cases/{case_id}/graph/provenance/{relationship_id}
GET  /cases/{case_id}/graph/contradictions
GET  /cases/{case_id}/graph/checkpoints
POST /cases/{case_id}/graph/diff
GET  /cases/{case_id}/graph/replay
POST /cases/{case_id}/graph/analytics
GET  /cases/{case_id}/graph/status
POST /cases/{case_id}/graph/export
```

Only create endpoints that match actual repository needs.

## 13. STANDARD RESPONSE ENVELOPE

```json
{
  "data": {},
  "meta": {
    "case_id": "CASE-001",
    "scope": "overview",
    "graph_version": "ontology-v1",
    "projection_version": "projection-v1",
    "generated_at": "...",
    "last_projected_at": "...",
    "truncated": false,
    "request_id": "REQ-001"
  }
}
```

## 14. LIGHTWEIGHT 3D NODE DTO

```json
{
  "id": "P-001",
  "type": "Person",
  "label": "Person P-001",
  "status": "REVIEW",
  "degree": 12,
  "evidence_count": 4,
  "provenance_count": 6,
  "expandable": true
}
```

Do not return raw Neo4j node properties by default.

## 15. LIGHTWEIGHT 3D EDGE DTO

```json
{
  "id": "REL-001",
  "source": "P-001",
  "target": "D-001",
  "type": "USES",
  "status": "OBSERVED",
  "directed": true,
  "confidence_available": true,
  "provenance_available": true
}
```

## 16. OVERVIEW API

Purpose:
- initial 3D scene
- bounded case context
- fast first render
- no giant graph dump

Required:
- case scope
- bounded node count
- bounded edge count
- bounded depth
- optional node/edge filters
- timeout
- truncation metadata
- freshness metadata when measured

## 17. NEIGHBOR API

```text
GET /cases/{case_id}/graph/entities/{entity_id}/neighbors
```

Potential parameters:
- depth
- limit
- relationship_types
- node_types
- from
- to

Always clamp client-provided values server-side.

## 18. PATH API

```text
POST /cases/{case_id}/graph/path
```

Request:
```json
{
  "source_id": "P-001",
  "target_id": "P-002",
  "max_hops": 4,
  "limit": 10,
  "relationship_types": ["USES", "CONNECTED_TO"],
  "time_range": {
    "from": "...",
    "to": "..."
  }
}
```

A path expresses graph connectivity. It does not automatically establish causation.

## 19. PROVENANCE API

```text
GET /cases/{case_id}/graph/provenance/{relationship_id}
```

Return a structured chain such as:

```text
Relationship
 ↓
Observation / Assertion
 ↓
Artifact
 ↓
Processing Run
 ↓
Evidence
 ↓
Source reference
```

This is a core CrimeKit differentiator.

## 20. EVIDENCE-TO-GRAPH API

```text
GET /cases/{case_id}/evidence/{evidence_id}/graph-impact
```

Answer:
- which graph entities were affected?
- which relationships were created/updated?
- which timeline records changed?
- which contradictions appeared?
- which processing run caused the change?

All values must come from actual projection lineage.

## 21. GRAPH-TO-EVIDENCE API

```text
GET /cases/{case_id}/graph/relationships/{relationship_id}/evidence
```

Answer:
- supporting evidence references
- observations
- processing lineage
- review status
- source categories

## 22. PROCESSING IMPACT API

```text
GET /cases/{case_id}/processing-runs/{run_id}/graph-impact
```

Expose real graph consequences of a processing run.

## 23. TIMELINE GRAPH API

```text
GET /cases/{case_id}/graph/timeline
```

Support:
- time range
- entity scope
- event type
- bounded result count

Do not replace authoritative Timeline semantics with an accidental graph reconstruction.

## 24. GRAPH DIFF

```text
POST /cases/{case_id}/graph/diff
```

Compare two checkpoints/states and return:
- nodes added
- nodes removed
- edges added
- edges removed
- edges changed
- provenance changes
- status changes

## 25. GRAPH REPLAY

```text
GET /cases/{case_id}/graph/replay
```

Replay actual graph projection events.

Never generate fictional historical graph movement.

## 26. GRAPH STATUS

```text
GET /cases/{case_id}/graph/status
```

Possible states:
- CURRENT
- STALE
- SYNCING
- FAILED
- UNAVAILABLE

`CURRENT` must mean the graph is within the defined freshness policy, not merely that Neo4j is reachable.

## 27. SEARCH API

```text
GET /cases/{case_id}/graph/search?q=...&node_type=...&limit=...
```

Search scores are retrieval signals, not evidentiary certainty.
Use existing CrimeKit search infrastructure where already appropriate.

## 28. TYPED FILTER SYSTEM

Represent advanced filters as typed request objects instead of arbitrary Cypher:

```json
{
  "node_types": ["Person", "Device"],
  "relationship_types": ["USES"],
  "status": ["OBSERVED"],
  "time_range": {
    "from": "...",
    "to": "..."
  }
}
```

Translate typed filters to parameterized Cypher through a controlled query builder.

## 29. CYPHER SAFETY

Never do:

```python
query = f"MATCH (n {{name: '{name}'}}) RETURN n"
```

Use query parameters.

Neo4j documentation explicitly describes parameterized querying as the safer alternative to string-building values. citeturn425442search8

## 30. QUERY BUDGET

Every graph request must have:

```text
max_hops
max_nodes
max_edges
max_paths
max_evidence
timeout
max_payload
```

Example policy:
- entity lookup → low cost
- neighbor expansion → bounded
- short path → bounded
- large path → async
- GDS → async
- replay → bounded/async
- export → async

## 31. SERVER-SIDE CLAMPING

Never trust:
`depth=9999`
`limit=9999999`
`max_hops=1000`

Clamp or reject before Neo4j.

## 32. NO UNBOUNDED TRAVERSAL

Reject or redesign queries containing unbounded patterns such as:

```cypher
MATCH (n)-[*]-(m)
```

unless a controlled internal use case has a strict hard limit elsewhere.

## 33. QUERY TIMEOUTS

Apply application-level and, where supported, transaction-level time budgets.

Current Neo4j Python documentation describes transaction timeout configuration. citeturn425442search0

## 34. RESULT ORDERING

Use deterministic ordering:
- stable ID
- timestamp
- explicit relevance
- explicit score

Never rely on incidental database result order.

## 35. PAGINATION

Use cursor-based pagination for scalable graph lists.

Cursor must be bound to:
- case scope
- tenant scope where applicable
- query/filter context
- graph/projection version where appropriate

Do not put sensitive data directly in cursors.

## 36. GRAPH CACHING

Potentially cache:
- schema metadata
- case overview
- entity summary
- bounded neighbors

Cache keys must include scope and query context.

Never let a cached graph result bypass authorization.

## 37. STALE DATA

If cached/projected graph data is stale but safe to display:
return freshness metadata.

If stale data creates unacceptable investigative risk:
require refresh or show controlled degraded state.

## 38. N+1 PROTECTION

Never:
1. fetch 100 nodes
2. issue 100 provenance queries
3. issue 100 evidence queries

Prefer:
- bounded batch lookup
- consolidated query
- on-demand drill-down

## 39. MULTI-STORE QUERY

When a graph result needs authoritative fields:

```text
Neo4j graph context
      +
PostgreSQL authoritative metadata
      +
Evidence service metadata
      ↓
Normalized Graph API DTO
```

Do not pretend the combined result is an atomic single-store truth if stores have different freshness.

## 40. GRAPH API ERROR MODEL

Use stable error codes:

```text
CASE_NOT_FOUND
FORBIDDEN
GRAPH_INVALID_SCOPE
GRAPH_ENTITY_NOT_FOUND
GRAPH_QUERY_TIMEOUT
GRAPH_QUERY_TOO_LARGE
GRAPH_UNAVAILABLE
GRAPH_SCHEMA_INCOMPATIBLE
GRAPH_PROJECTION_STALE
GRAPH_ANALYTICS_UNAVAILABLE
```

Never return:
- Cypher
- passwords
- tokens
- stack traces
- database topology

## 41. EMPTY RESULT

A valid graph query returning no data should normally return HTTP 200 with:

```json
{
  "nodes": [],
  "edges": [],
  "meta": {
    "truncated": false
  }
}
```

Do not confuse empty data with database failure.

## 42. OUTAGE DEGRADATION

If Neo4j is unavailable:

```text
Neo4j failure
 ↓
bounded retry
 ↓
safe error
 ↓
graph UI degraded state
 ↓
other CrimeKit features continue where possible
```

Do not let a graph outage crash the complete case workspace.

## 43. DRIVER LIFECYCLE

Maintain one shared driver abstraction.
Close sessions.
Close driver at application shutdown.

Current Neo4j docs describe driver pooling and lightweight sessions that should be closed when complete. citeturn425442search11turn425442search0

## 44. CAUSAL CONSISTENCY

Use causal consistency/bookmarks only where there is a real read-after-write requirement across sessions.

Current driver documentation describes bookmark management and notes that waiting for causal consistency can have performance cost. citeturn425442search5turn425442search4

## 45. TRANSACTION IDEMPOTENCY

If a transaction function can be retried, its behavior must be idempotent.

Do not place non-idempotent external side effects inside retried transaction callbacks.

## 46. GRAPH API + REDIS REALTIME

Preferred:

```text
Projection Engine
      ↓
Graph change event
      ↓
Redis/event layer
      ↓
Realtime authorization
      ↓
WebSocket/SSE
      ↓
3D UI
```

Reuse the existing CrimeKit Redis architecture rather than adding a second broker solely for graph API traffic.

## 47. REALTIME EVENT

```json
{
  "event_type": "GRAPH_EDGE_CREATED",
  "case_id": "CASE-001",
  "sequence": 104,
  "projection_version": "v1",
  "edge": {
    "id": "REL-001",
    "source": "P-001",
    "target": "D-001",
    "type": "USES"
  },
  "occurred_at": "..."
}
```

## 48. REALTIME SECURITY

Before a graph WebSocket/SSE subscription:
1. authenticate
2. authorize case
3. authorize graph permission
4. subscribe

On reconnect, detect sequence gaps and request a fresh bounded snapshot or replay.

## 49. GRAPH FRESHNESS

Track where available:
- last source event
- last successful projection
- projection lag

Do not label the graph realtime without measured projection freshness.

## 50. 3D READ MODEL

The 3D frontend should receive normalized semantic DTOs.

Do not expose raw Neo4j driver records.
Do not make Three.js understand Neo4j-specific data structures.

## 51. 3D PROGRESSIVE LOADING

```text
Case overview
   ↓
User selects node
   ↓
Neighbor API
   ↓
Merge node/edge IDs
   ↓
Layout
   ↓
Render
   ↓
Further expansion on demand
```

Persisted graph scale and concurrently rendered graph scale are different capacity problems.

## 52. HIGH-DEGREE NODES

For very connected entities:
- return counts
- apply relationship filters
- aggregate where useful
- allow drill-down
- avoid rendering every edge immediately

## 53. GRAPH AGGREGATION

If returning summary clusters:

```json
{
  "type": "ClusterSummary",
  "count": 47,
  "expandable": true
}
```

The aggregate must remain traceable to underlying graph records.

## 54. GRAPH LENSES

Support future scoped lenses:

```text
Evidence
Timeline
Communication
Device
Identity
Location
Provenance
Contradiction
Investigation
```

A lens changes selection/emphasis, not canonical graph truth.

## 55. NOVELTY #1 — PROVENANCE THREAD

Selecting one edge should allow the UI to request:

```text
Relationship
 ↓
Observation
 ↓
Artifact
 ↓
Processing Run
 ↓
Evidence
 ↓
Source
```

The graph edge becomes an auditable investigative object.

## 56. NOVELTY #2 — EVIDENCE IMPACT

One evidence item can expose:

```text
Evidence
 ↓
Artifacts
 ↓
Observations
 ↓
Entities affected
 ↓
Relationships affected
 ↓
Timeline changes
 ↓
Contradictions
```

This is substantially more useful than a generic 'evidence linked' card.

## 57. NOVELTY #3 — PROCESSING IMPACT

A processing run can expose:

```text
ProcessingRun
 ↓
Artifacts
 ↓
Entities discovered
 ↓
Relations created/proposed
 ↓
Timeline events
```

All metrics must be computed from actual records.

## 58. NOVELTY #4 — GRAPH DIFF

Compare:
- investigation stage A
- investigation stage B

Show only actual graph changes.

## 59. NOVELTY #5 — TEMPORAL GRAPH TIME MACHINE

Support a time selector where the backend can genuinely reconstruct graph state from event history/checkpoints.

Possible architecture:
- event replay
- bitemporal state
- checkpoints
- versioned projections

Do not fake historical state.

## 60. NOVELTY #6 — INVESTIGATION REPLAY

Replay how knowledge emerged:

```text
Evidence arrived
 → Artifact extracted
 → Entity resolved
 → Relationship created
 → Contradiction detected
 → Human review
```

Use actual projection/review events.

## 61. NOVELTY #7 — CONTRADICTION LAYER

Expose:
- supporting observations
- conflicting observations
- disputed relationships
- unknowns

Do not silently choose one side.

## 62. NOVELTY #8 — KNOWLEDGE GAPS

Expose explicit gaps:

```text
KNOWN
UNKNOWN
UNRESOLVED
MISSING SUPPORT
CONFLICTED
```

A knowledge gap is not a guessed relationship.

## 63. NOVELTY #9 — NEXT-BEST-EVIDENCE

A reasoning layer can use graph gaps to suggest:

```text
What evidence would reduce this uncertainty?
```

This is a review/research suggestion, never a conviction recommendation.

## 64. NOVELTY #10 — HYPOTHESIS SANDBOX

Separate:

```text
Canonical Graph
     |
     +----> Hypothesis/Sandbox Graph
```

Hypothesis relationships must never silently enter the canonical forensic graph.

## 65. NOVELTY #11 — EVIDENCE SUPPORT INDEX

Potential transparent navigation metric built from components such as:
- provenance completeness
- source diversity
- independent observations
- review status
- contradiction presence
- recency

Never label it 'truth score', 'guilt score' or 'criminality score'.

## 66. NOVELTY #12 — UNCERTAINTY STACK

Where supported, return separate dimensions:

```text
identity uncertainty
source quality
model confidence
temporal uncertainty
human review state
```

A single scalar hides important distinctions.

## 67. NOVELTY #13 — RELATIONSHIP EVIDENCE STACK

Inspector layout:

```text
TOP
Semantic Relationship

MIDDLE
Evidence / Observation support

BOTTOM
Processing / Provenance / Source
```

The API must support these drill-down levels.

## 68. NOVELTY #14 — SOURCE DIVERSITY

Return supporting source categories such as:
- CCTV
- document
- device log
- communication
- metadata
- human review

Do not interpret more source types as automatic truth.

## 69. NOVELTY #15 — GRAPH EVOLUTION

Make graph evolution a first-class API concept:

```text
what appeared?
what disappeared?
what changed?
what became disputed?
what became reviewed?
```

## 70. FORENSIC ETHICS

Hard restrictions:
- graph centrality is not guilt
- graph connectivity is not causation
- anomaly is not criminality
- face similarity is not identity proof
- IP association is not person identity
- device location is not automatically person location
- absence from graph is not proof of absence
- AI narrative is not evidence

## 71. GRAPH ASSERTION SEMANTICS

Distinguish:
- direct observation
- derived assertion
- candidate identity
- hypothesis
- human-reviewed relationship
- disputed relationship

## 72. CONFIDENCE SEMANTICS

Never overload `confidence`.

If possible, separate:
- model confidence
- identity confidence
- temporal confidence
- source quality
- review state

Document what each means.

## 73. MODEL PROVENANCE

For ML-derived graph results, where relevant:

```text
model_name
model_version
inference_time
threshold_policy
source_frame/artifact
processing_run_id
```

Do not store giant duplicated metadata in every node when an existing registry can be referenced.

## 74. FACE TRACE API SAFETY

Potential flow:

```text
Frame
 ↓
Detection
 ↓
Track
 ↓
Embedding
 ↓
Candidate
 ↓
Human Review
```

A similarity candidate must remain a candidate until policy allows promotion.

## 75. TIMELINE SEMANTICS

Preserve:
- event time
- ingestion time
- projection time

Do not substitute projection time for unknown source time.

## 76. TEMPORAL UNCERTAINTY

Support where needed:
- exact timestamp
- approximate timestamp
- time interval
- unknown time

## 77. GRAPH SCHEMA ENDPOINT

A developer/admin endpoint may expose actual graph schema:

```text
GET /graph/schema
```

It must not be a manually copied ontology file that silently drifts from Neo4j.

## 78. SCHEMA DRIFT

Detect:
- missing label
- unexpected label
- missing relationship
- unexpected relationship
- missing index
- missing constraint
- incompatible property expectation

## 79. VERSION MATRIX

Keep distinct:

| Version | Meaning |
|---|---|
| API version | HTTP contract |
| Ontology version | graph semantics |
| Projection version | source→graph rules |
| Graph state/checkpoint | materialized state |
| Model version | ML provenance |

Do not collapse these.

## 80. GRAPH REPOSITORY METHODS

Prefer semantic methods:

```text
get_case_overview
get_entity
get_neighbors
search_entities
find_paths
get_timeline
get_provenance
get_contradictions
get_graph_diff
get_checkpoint
get_graph_status
```

Do not expose a generic arbitrary-Cypher repository to controllers.

## 81. QUERY REGISTRY

Assign stable IDs:

```text
CASE_OVERVIEW_V1
ENTITY_LOOKUP_V1
ENTITY_NEIGHBORS_V1
PATH_SEARCH_V1
PROVENANCE_THREAD_V1
TIMELINE_GRAPH_V1
GRAPH_DIFF_V1
```

Log query template ID rather than sensitive raw query values where practical.

## 82. QUERY PLAN SAFETY

Use controlled developer/staging performance analysis.

Do not expose arbitrary `PROFILE` or `EXPLAIN` endpoints to public clients.

## 83. GRAPH ANALYTICS API

Potential:
```text
POST /cases/{case_id}/graph/analytics
GET  /cases/{case_id}/graph/analytics/{analysis_id}
```

Whitelist algorithms.

Potential categories:
- degree centrality
- PageRank
- betweenness
- community detection
- shortest paths
- similarity

Use only algorithms supported by the deployment.

## 84. GDS SAFETY

Never represent:
```text
high centrality = suspect
community = criminal group
similarity = identity
anomaly = crime
```

Instead represent the mathematical/graph result and methodology.

## 85. GDS MCP

The official Neo4j MCP documentation provides `list-gds-procedures` for inspecting available GDS procedures. citeturn425442search1

Use MCP for development discovery, not as the investigator application API.

## 86. ANALYTICS JOB MODEL

Heavy analytics should be asynchronous:

```text
request
 ↓
job
 ↓
worker
 ↓
Neo4j/GDS
 ↓
stored result
 ↓
API
```

Capture:
- algorithm
- graph scope
- parameters
- graph version
- timestamp
- status

## 87. GRAPH API + AI TOOLS

Provide narrow tools:

```text
find_entity
get_neighbors
find_path
get_timeline
get_evidence
get_provenance
find_contradictions
get_graph_changes
```

Do not give a normal investigator AI unrestricted arbitrary Cypher by default.

## 88. AI GRAPH TOOL FLOW

```text
Authenticated user
      ↓
Case scope
      ↓
Typed graph tool
      ↓
Graph API
      ↓
Structured context
      ↓
LLM
```

AI receives no broader graph authorization than the authenticated user.

## 89. AI TOKEN/COST CONTROL

Graph API can reduce AI context cost by:
- bounded neighborhoods
- deduplicated entities
- compact edges
- evidence references
- summarized repeated structures
- explicit limits

## 90. AI GROUNDING

AI factual statements should be traceable to:
- graph node IDs
- relationship IDs
- evidence IDs
- timeline IDs
- provenance IDs

When no supporting graph/evidence data exists, the model must say so.

## 91. AI CAUSALITY GUARDRAIL

A graph path:
```text
A → Device → IP → Account → B
```

means connectivity.

It does not automatically mean:
```text
A caused B
A controlled B
A committed an offense
```

## 92. GRAPH API + REPORTING

Reports should use authorized structured graph/evidence data.

Do not scrape the 3D canvas as the source of truth.

Report claims should be traceable to graph/evidence identifiers where applicable.

## 93. GRAPH EXPORT

Exports are sensitive operations.

Require:
- permission
- case scope
- field minimization
- audit
- async processing for large exports
- explicit filters
- graph/projection version

## 94. SAVED GRAPH VIEW

A saved view can store:

```json
{
  "case_id": "CASE-001",
  "checkpoint_id": "CP-01",
  "selected_node_ids": [],
  "selected_edge_ids": [],
  "filters": {},
  "lens": "provenance",
  "layout": "force"
}
```

This is visualization state, not forensic truth.

## 95. GRAPH INSPECTOR DTO

Provide a rich inspector DTO separate from the lightweight 3D DTO:

```text
identity
relationships
timeline
evidence
provenance
uncertainty
contradictions
review
```

## 96. NODE/EDGE FIELD WHITELIST

Do not serialize all Neo4j properties.

Use explicit allowlists for browser DTOs.

The browser should receive only:
- identifiers
- labels
- approved metadata
- counts
- provenance flags
- approved temporal data

## 97. PII / REDACTION

Graph results can still contain sensitive data.

Apply:
- role-based field masking
- case-level authorization
- evidence-level permissions where necessary
- data minimization

## 98. CACHE SECURITY

Cache key must bind to authorization-relevant scope.

Do not let User A's graph response become User B's cached response.

## 99. WEBSOCKET GAP RECOVERY

If sequence:
```text
101
104
```

is observed:

```text
gap detected
 ↓
request fresh bounded snapshot or replay
 ↓
merge using stable IDs
```

## 100. API OBSERVABILITY

Track:
- requests
- errors
- latency
- P50/P95/P99
- nodes returned
- edges returned
- payload size
- timeouts
- projection lag
- realtime gaps

## 101. SAFE LOGGING

Log:
- request ID
- operation ID
- case ID where policy permits
- duration
- result counts

Never log:
- passwords
- tokens
- full evidence
- sensitive raw query parameters

## 102. ERROR TAXONOMY

Differentiate:
- unavailable
- timeout
- invalid request
- forbidden
- not found
- conflict
- schema incompatibility

Do not map every failure to 500.

## 103. RATE LIMITING

Use stricter controls for:
- path queries
- replay
- export
- analytics

Use appropriate general limits for:
- overview
- neighbors
- search

## 104. QUERY FAN-OUT

Avoid one request triggering dozens of independent Neo4j queries.

Prefer:
- consolidated read
- batch query
- lazy drill-down

## 105. GRAPH RESPONSE SIZE

Reject or truncate oversized responses before browser memory becomes a problem.

Always communicate:
```text
truncated = true
```
when data was intentionally bounded.

## 106. 3D GRAPH PERFORMANCE

Server:
- filter
- bound
- paginate
- aggregate

Client:
- LOD
- instancing
- progressive rendering
- frustum culling
- lazy expansion
- cluster collapse

Do not equate database size with renderable viewport size.

## 107. HIGH-VOLUME EVENT GRAPH

Do not necessarily materialize every CCTV frame as a graph node.

Potential hierarchy:
```text
Video
 ↓
Frame
 ↓
Detection
 ↓
Track
 ↓
Observation
```

Project persistent investigative signals, not raw UI noise.

## 108. GRAPH AGGREGATION

When high-frequency relationships become dense, aggregate where semantics allow:

```text
many events
 ↓
bounded observation/sighting summary
 ↓
drill-down to source records
```

Aggregation must remain traceable.

## 109. GRAPH API + POSTGRES

When graph context references entities whose authoritative metadata is in PostgreSQL:

1. retrieve graph IDs
2. batch-fetch authoritative records
3. merge into response
4. preserve freshness/version differences

## 110. GRAPH API + OBJECT STORAGE

Original evidence stays in object storage.

Graph API should provide:
- evidence ID
- metadata
- secure resource references

Do not move raw evidence binaries into Neo4j or Graph API payloads unnecessarily.

## 111. GRAPH API + SEARCH/VECTOR

Potential hybrid:

```text
Text/vector retrieval
      ↓
candidate entity IDs
      ↓
Neo4j graph expansion
      ↓
provenance/evidence
```

Do not automatically duplicate pgvector in Neo4j.

## 112. GRAPH API + ENTITY RESOLUTION

Expose:
- canonical entity
- candidate entity
- resolution status
- evidence basis
- model metadata

Do not silently merge uncertain identities.

## 113. GRAPH API + CONTRADICTIONS

Contradictions may be:
- temporal
- identity
- location
- device association
- document disagreement
- model disagreement

Return the conflict, source references and status.

## 114. GRAPH API + KNOWLEDGE GAPS

Gaps can include:
- missing ownership support
- unresolved identity
- missing timestamp
- insufficient source diversity
- conflicting observations

Do not fabricate missing links.

## 115. GRAPH API + HUMAN REVIEW

For candidate/derived relationships:

```text
Candidate
 ↓
Review
 ↓
Accept / Reject / Dispute
```

Review changes assessment state, not original evidence.

## 116. GRAPH API + HYPOTHESIS

Hypothesis data must be:
- clearly labeled
- separately scoped
- excluded from canonical facts by default
- excluded from evidence conclusions

## 117. GRAPH VIEW VS GRAPH FACT

Keep distinct:
- graph fact
- analytical result
- hypothesis
- investigator annotation
- UI state

## 118. GRAPH VIEW REPRODUCIBILITY

A graph view should be reproducible from:
- case
- query/filter
- graph version
- projection version
- checkpoint/time state

## 119. GRAPH CHECKPOINT

Potential workflow checkpoints:
- Initial Intake
- Post Processing
- Post Entity Resolution
- Human Review
- Reporting Stage

These are workflow states, not legal certifications.

## 120. GRAPH DIFF VISUAL SUPPORT

The API should enable the 3D layer to render:
- newly created nodes
- newly created edges
- retired edges
- changed statuses

This produces real visual evolution instead of decorative animation.

## 121. GRAPH PULSE

Realtime updates can create an actual graph pulse for:
- new evidence
- new artifact
- new observation
- new relationship
- contradiction
- projection status

The event must originate from real system state.

## 122. GRAPH LENS API CONTRACT

Potential query modes:
```text
overview
evidence
timeline
communication
device
identity
provenance
contradiction
replay
```

Each is a bounded graph selection.

## 123. GRAPH QUERY POLICY ENGINE

Before Neo4j:
1. validate endpoint
2. validate user
3. validate case
4. validate node types
5. validate relationship types
6. validate time range
7. clamp depth
8. clamp result count
9. assign timeout
10. execute

## 124. NO RAW CYPHER ENDPOINT

Do not expose:
```text
POST /graph/cypher
```

to investigators.

A developer-only diagnostic tool may exist behind strict authorization if necessary.

## 125. INTERNAL GRAPH DIAGNOSTICS

Potential internal capabilities:
- schema drift
- counts by label
- counts by relationship
- orphan detection
- provenance coverage
- graph freshness
- query latency
- projection lag

Never expose raw maintenance functions publicly.

## 126. RECONCILIATION

Graph API can surface reconciliation status:

```text
authoritative source
      ↕
Neo4j projection
```

Detect:
- missing node
- extra node
- missing edge
- extra edge
- wrong property
- missing provenance

## 127. REBUILDABILITY

The API should not be the source of rebuild truth.

Rebuild should come from:
```text
authoritative records/events
+
projection rules
```

## 128. PROJECTION FRESHNESS CONTRACT

Expose:
- last projected event
- last projected timestamp
- projection version
- stale flag

Do not infer freshness from the HTTP request time.

## 129. GRAPH STATE METADATA

Useful metadata:
```text
graph_version
projection_version
generated_at
last_projected_at
checkpoint_id
truncated
request_id
```

## 130. API VERSIONING

Follow existing CrimeKit API versioning.

A semantic change to:
- node IDs
- edge meaning
- confidence meaning
- timestamp semantics
- status semantics

is a breaking change even if the JSON shape remains identical.

## 131. OPENAPI

Document:
- endpoint
- request schema
- response schema
- permission
- limits
- error codes
- freshness semantics
- semantic meaning

## 132. API CONTRACT TESTS

Required:
- DTO schema tests
- endpoint schema tests
- auth tests
- case isolation tests
- query limit tests
- provenance tests
- realtime tests

## 133. GRAPH GOLDEN TEST

Create deterministic graph fixtures.

Example:
```text
CASE-TEST-001
  Person P001
  Device D001
  Account A001
  IP I001
  Evidence E001
  Artifact ART001
  Observation OBS001
  TimelineEvent T001
```

## 134. GOLDEN SCENARIOS

Test:
- simple case
- high-degree entity
- provenance chain
- contradiction
- candidate identity
- temporal overlap
- realtime update
- case isolation
- graph diff
- replay

## 135. SECURITY TEST MATRIX

| Test | Expected |
|---|---|
| User A → Case A | ALLOW |
| User A → Case B | DENY |
| Cross-case path | DENY unless authorized |
| Excessive depth | CLAMP/DENY |
| Excessive limit | CLAMP/DENY |
| Cypher injection | BLOCK |
| Unauthorized export | DENY |
| Unauthorized WebSocket | DENY |
| Frontend Neo4j secret | ABSENT |
| MCP production write | DENY by default |

## 136. FAILURE TEST MATRIX

| Failure | Expected |
|---|---|
| Neo4j unavailable | degraded/503 |
| timeout | GRAPH_QUERY_TIMEOUT |
| invalid filter | 400/422 |
| unknown entity | 404 |
| unauthorized case | 403 |
| schema mismatch | safe failure |
| realtime sequence gap | snapshot/replay |
| stale graph | freshness warning |

## 137. PERFORMANCE TEST MATRIX

Measure:
- overview P50/P95/P99
- neighbor latency vs degree
- path latency vs hops
- search latency
- provenance latency
- payload bytes
- concurrent users
- connection pool stability
- timeout rate

## 138. STRESS TEST

Stress:
- high-degree nodes
- rapid progressive expansion
- repeated path requests
- large timeline windows
- concurrent graph users

## 139. SOAK TEST

Run sustained graph traffic and inspect:
- memory leaks
- connection leaks
- latency drift
- cache growth
- WebSocket stability

## 140. CHAOS / FAILURE INJECTION

Inject:
- Neo4j interruption
- network interruption
- stale projection
- service restart
- realtime disconnect
- invalid schema
- malformed requests

## 141. MCP VERIFICATION

Inside Google Antigravity:

```text
1. verify official Neo4j MCP server
2. verify target environment
3. verify database
4. run get-schema
5. run bounded read-cypher
6. run list-gds-procedures
7. verify actual CrimeKit graph state
8. verify Graph API output
```

Do not use MCP in the browser.

## 142. MCP READONLY

Current official Neo4j MCP documentation states that setting:

```text
NEO4J_READ_ONLY=true
```

disables write tools.

Use readonly as the default for production-adjacent inspection. citeturn425442search1

## 143. MCP WRITE POLICY

If write testing is genuinely required:
- development only
- synthetic test data
- explicit approval
- bounded Cypher
- post-write validation
- no production destructive testing

Do not let an LLM freely mutate production forensic data.

## 144. ANTIGRAVITY CONFIGURATION

Inspect the installed Antigravity version and its actual MCP configuration schema before editing.

Do not blindly copy configurations from:
- VS Code
- Cursor
- Claude Desktop
- older Gemini environments

Keep secrets out of project config.

## 145. MCP TARGET SEPARATION

Prefer unmistakable environment identities:

```text
neo4j-crimekit-dev
neo4j-crimekit-staging
```

Production access must require deliberate configuration.

Default production MCP:
```text
READONLY
```

## 146. MCP AS ENGINEERING LOOP

```text
Antigravity
  ↓
MCP schema inspection
  ↓
implement Graph API
  ↓
run tests
  ↓
MCP inspect result
  ↓
3D UI verification
```

This provides fast graph-aware engineering without coupling production to MCP.

## 147. NO MCP DEPENDENCY

Closing Antigravity must NOT break:
- API
- 3D graph
- timeline
- evidence
- reports
- authentication

## 148. GRAPH API + 3D REFERENCE DESIGN

Use the user's reference graph/AI-observability-inspired visual direction as a UX target:
- dark enterprise canvas
- dense information hierarchy
- graph-first workspace
- compact controls
- right-side inspector
- strong timeline/replay tools
- realtime status
- controlled accent system

Do not copy third-party branding, logos or proprietary implementation.
CrimeKit branding remains primary.

## 149. 3D SCREEN DATA FLOW

```text
Top Search
   ↓
Search API
   ↓
Entity
   ↓
Overview / Neighbors
   ↓
3D Graph
   ↓
Select Edge
   ↓
Provenance API
   ↓
Evidence / Timeline
```

## 150. GRAPH API UI STATES

Support:
- loading
- empty
- partial
- stale
- syncing
- failed
- unavailable
- realtime
- replay

## 151. EMPTY GRAPH

Correct:
```text
No graph relationships available yet.
```

Never fill an empty graph with fake demo edges in production.

## 152. PROJECTION IN PROGRESS

Display real status:
```text
Graph projection in progress
```

Include measured progress only when actually available.

## 153. GRAPH STALE STATE

Display:
```text
Graph may be stale.
Last synchronized: ...
```

Only when freshness is backed by actual timestamps/metrics.

## 154. GRAPH INSPECTOR QUESTIONS

The API should support:
- Why are these connected?
- What evidence supports this?
- When did the relation appear?
- What contradicts it?
- Which processing run created it?
- What changed after this evidence?

## 155. GRAPH EXPLANATION CONTRACT

```json
{
  "relationship": {},
  "basis": {
    "observations": [],
    "evidence": [],
    "processing_runs": []
  },
  "uncertainty": {},
  "review": {}
}
```

## 156. PROJECTION LINEAGE

Where available, a relationship should be traceable to:

```text
Evidence
 ↓
ProcessingRun
 ↓
SourceEvent
 ↓
ProjectionRule
 ↓
GraphIntent
 ↓
Neo4j relationship
```

This supports CrimeKit's 'SHOW THE WORK' principle.

## 157. GRAPH API + SHOW THE WORK

For an important graph result expose:
- what
- why
- source
- when
- processing
- model/rule
- review state
- uncertainty

## 158. QUERY COST PROTECTION

Prevent:
- global scans
- massive variable paths
- giant result sets
- repeated high-cost analytics
- AI query loops without budget

## 159. AI QUERY BUDGET

Agent tools should have their own limits:
- max entities
- max edges
- max paths
- max evidence
- max tokens/context
- max execution time

## 160. AI NO HALLUCINATED EDGE

An AI assistant may propose a hypothesis but cannot treat a plausible connection as a canonical graph fact.

## 161. GRAPH EXPORT SECURITY

Export must enforce:
- case access
- graph permissions
- field redaction
- scope limits
- audit
- asynchronous job for large exports

## 162. INVESTIGATOR AUDIT

Audit meaningful graph actions:
- graph opened
- search
- expansion
- path request
- provenance opened
- evidence opened
- review action
- export request

Do not store every mouse movement.

## 163. ADMIN OPERATIONS

Potential internal operations:
- reconcile
- rebuild
- replay
- schema diagnostics

All:
- internal
- strongly authorized
- audited
- environment-aware

## 164. NO HIDDEN GRAPH WRITES

GET:
- no canonical graph mutation

Investigator graph reads:
- read only

Canonical graph writes:
- projection engine

Review writes:
- explicit controlled workflow

## 165. GRAPH API + PROJECTION SEPARATION

```text
Projection Engine:
source → graph write

Graph API:
graph → safe read/analysis view

Realtime:
graph change → authorized event

MCP:
developer/agent → controlled graph inspection
```

## 166. GRAPH STATE RECONCILIATION

Support scoped reconciliation:
```text
PostgreSQL/source expectation
      ↕
Neo4j projection
```

Report:
- missing
- extra
- mismatched
- orphaned
- provenance gaps

## 167. REBUILD SUPPORT

Do not depend on current Neo4j state to rebuild Neo4j.

Rebuild source:
- authoritative data
- domain events
- projection rules

## 168. GRAPH VERSIONING

Every release that changes graph semantics should identify:
- ontology version
- projection version
- API version
- graph migration
- compatibility impact

## 169. SCHEMA CHANGE REVIEW

Review:
- node identity
- relationship direction
- relationship semantics
- properties
- provenance
- API DTO
- 3D impacts
- AI impacts
- test impacts

## 170. BLUE/GREEN / SHADOW API

For major Graph API changes:
- current route/result
- candidate route/result
- compare
- validate
- cut over

Do not silently alter semantics during a rolling deployment.

## 171. GRAPH API PERFORMANCE PRINCIPLE

Current Neo4j guidance notes transaction overhead and retry behavior; optimize only from measured workloads. citeturn425442search4turn425442search0

## 172. GRAPH CAPACITY DIMENSIONS

Measure separately:
1. persisted graph size
2. event throughput
3. query concurrency
4. graph expansion size
5. analytics workload
6. 3D viewport workload
7. realtime event rate

## 173. NO UNSUPPORTED SCALE CLAIMS

Never claim:
```text
supports 1M nodes
supports 10k concurrent users
all queries <50 ms
```

unless benchmarked on a named deployment configuration.

## 174. GRAPH API SECURITY CHECKLIST

```text
[ ] authentication
[ ] case authorization
[ ] tenant isolation
[ ] typed filters
[ ] Cypher parameterization
[ ] bounded depth
[ ] bounded limits
[ ] timeouts
[ ] safe errors
[ ] response minimization
[ ] export controls
[ ] realtime controls
[ ] cache isolation
[ ] secret protection
[ ] MCP readonly
```

## 175. GRAPH API PERFORMANCE CHECKLIST

```text
[ ] bounded queries
[ ] indexes
[ ] deterministic ordering
[ ] pagination
[ ] N+1 avoided
[ ] payload minimized
[ ] caching validated
[ ] high-degree handling
[ ] query timeouts
[ ] load testing
[ ] soak testing
```

## 176. 3D READINESS CHECKLIST

```text
[ ] overview
[ ] neighbors
[ ] stable IDs
[ ] edge IDs
[ ] progressive loading
[ ] truncation metadata
[ ] realtime events
[ ] provenance drill-down
[ ] timeline linkage
[ ] graph diff
[ ] replay
```

## 177. AI READINESS CHECKLIST

```text
[ ] typed graph tools
[ ] scoped authorization
[ ] result limits
[ ] evidence references
[ ] provenance references
[ ] uncertainty
[ ] contradiction visibility
[ ] no unrestricted Cypher
[ ] no hallucinated edges
```

## 178. MCP READINESS CHECKLIST

```text
[ ] official Neo4j MCP
[ ] correct environment
[ ] correct database
[ ] authentication
[ ] get-schema
[ ] read-cypher
[ ] list-gds-procedures
[ ] readonly default
[ ] secrets not committed
[ ] production write guarded
```

## 179. API TEST PYRAMID

```text
Unit
 ↓
Policy
 ↓
Repository integration
 ↓
API integration
 ↓
Security
 ↓
Realtime
 ↓
Performance
 ↓
3D end-to-end
```

## 180. END-TO-END GOLDEN PATH

```text
Evidence / Domain Record
      ↓
Graph Projection
      ↓
Neo4j
      ↓
Graph API
      ↓
3D Overview
      ↓
Select Person
      ↓
Expand Device
      ↓
Select Relationship
      ↓
Open Provenance
      ↓
Open Evidence
      ↓
Inspect Timeline
      ↓
Review Contradiction
      ↓
Human Decision
```

## 181. END-TO-END AI PATH

```text
Investigator Question
      ↓
Scoped Graph Tool
      ↓
Graph API
      ↓
Bounded Neighborhood / Path
      ↓
Evidence + Provenance
      ↓
Context Pack
      ↓
LLM
      ↓
Grounded Explanation
      ↓
Human Review
```

## 182. END-TO-END MCP PATH

```text
Antigravity
      ↓
Official Neo4j MCP
      ↓
get-schema
      ↓
read-cypher
      ↓
list-gds-procedures
      ↓
Inspect DEV graph
      ↓
Implement API
      ↓
Run API tests
      ↓
Verify 3D result
```

## 183. REQUIRED FILE MAP

Return actual repository paths in these categories:

```text
EXISTING — KEEP
EXISTING — MODIFY
NEW — CREATE
DEPRECATED — REVIEW
UNKNOWN — INVESTIGATE
```

Never invent repository paths.

## 184. REQUIRED QUERY MAP

| Query | Purpose | Required scope | Index | Timeout |
|---|---|---|---|---|
| CASE_OVERVIEW | initial graph | case | | |
| ENTITY_LOOKUP | entity | case | | |
| ENTITY_NEIGHBORS | expansion | case | | |
| PATH_SEARCH | connectivity | case | | |
| PROVENANCE_THREAD | lineage | case | | |
| TIMELINE_GRAPH | timeline | case/time | | |
| GRAPH_DIFF | change | case/checkpoint | | |

## 185. REQUIRED DTO MAP

| DTO | Consumer | Sensitivity | Version |
|---|---|---|---|
| GraphOverviewDTO | 3D | medium | |
| GraphNodeDTO | 3D | medium | |
| GraphEdgeDTO | 3D | medium | |
| GraphInspectorDTO | inspector | high | |
| ProvenanceDTO | inspector/AI | high | |
| PathDTO | 3D/AI | medium | |
| GraphDiffDTO | diff/replay | medium | |
| GraphStatusDTO | UI | low/medium | |

## 186. REQUIRED ROLE MATRIX

| Role | Read | Expand | Path | Provenance | Analytics | Export | Review |
|---|---:|---:|---:|---:|---:|---:|---:|
| Investigator | | | | | | | |
| Reviewer | | | | | | | |
| Admin | | | | | | | |
| AI Assistant | scoped | scoped | scoped | scoped | limited | no | proposal |
| Developer MCP | dev/controlled | dev/controlled | dev/controlled | dev/controlled | dev/controlled | no | no |

## 187. REQUIRED OBSERVABILITY TABLE

| Metric | Meaning |
|---|---|
| graph_api_requests_total | API volume |
| graph_api_errors_total | error volume |
| graph_query_latency_seconds | query duration |
| graph_query_timeout_total | timeout count |
| graph_nodes_returned | result size |
| graph_edges_returned | result size |
| graph_payload_bytes | response size |
| graph_projection_lag_seconds | source→graph lag |
| graph_realtime_gap_total | realtime gaps |

## 188. REQUIRED MCP VERIFICATION TABLE

| Check | Expected | Actual | Status |
|---|---|---|---|
| Official MCP | yes | | |
| Antigravity visibility | yes | | |
| Correct environment | dev/staging/approved | | |
| Authentication | success | | |
| get-schema | success | | |
| read-cypher | success | | |
| list-gds-procedures | success if available | | |
| readonly default | enabled | | |
| production arbitrary write | blocked | | |

## 189. REQUIRED FINAL REPORT

Return:

1. Current Graph API State
2. Existing Implementation
3. Reused Components
4. Modified Components
5. New Components
6. Endpoint Inventory
7. Query Inventory
8. DTO Inventory
9. Authorization Model
10. Performance Controls
11. Realtime Contract
12. Provenance Contract
13. 3D Contract
14. AI Tool Contract
15. Security Findings
16. Performance Findings
17. MCP / Antigravity Verification
18. Test Results
19. Remaining Risks
20. Production Readiness
21. Next Handoff

## 190. FINAL READINESS SCORE

Score /10 with evidence:

- architecture
- authorization
- case isolation
- tenant isolation
- query safety
- ontology
- provenance
- temporal semantics
- realtime
- 3D DTO
- AI tools
- performance
- resilience
- observability
- testing
- MCP integration
- documentation
- production operations

## 191. NOT-READY CONDITIONS

Declare NOT READY if any critical condition remains:
- direct frontend→Neo4j
- unrestricted public Cypher
- missing case authorization
- arbitrary production MCP writes
- fake graph data
- fake provenance
- fake freshness
- missing provenance for required relationships
- unbounded traversal
- unrecoverable graph state
- untested realtime isolation

## 192. PRODUCTION-READY DEFINITION

Declare PRODUCTION READY only when:

```text
Authorized user
   ↓
Safe Graph API
   ↓
Bounded Neo4j query
   ↓
Correct graph DTO
   ↓
3D visualization
   ↓
Evidence/provenance drill-down
   ↓
Realtime without leakage
   ↓
AI grounding without unrestricted DB access
```

and the system has:
- measured performance
- security testing
- graph freshness
- error handling
- recovery path
- reproducible contracts
- documented MCP tooling

## 193. FINAL GOLDEN ARCHITECTURE

```text
                    CRIMEKIT

                PostgreSQL
             authoritative data
                     |
                     v
               Graph Projection
                     |
                     v
                  Neo4j Aura
                     |
              +------+------+
              |             |
            Cypher         GDS
              |
              v
          Graph Service
              |
         Auth + Scope
              |
         Query Policy
              |
          Graph API
        /      |            3D    Inspector   AI
       |       |        |
       +-------+--------+
               |
      Evidence / Timeline
               |
          Human Review


Developer plane:
Antigravity → Official Neo4j MCP → Neo4j DEV/STAGING
```

## 194. FINAL CREATIVE TARGET

CrimeKit should feel like a **forensic knowledge operating system** rather than a graph viewer.

The Graph API must make this interaction possible:

```text
SELECT EDGE
   ↓
WHY?
   ↓
GRAPH PATH
   ↓
TEMPORAL CONTEXT
   ↓
PROVENANCE THREAD
   ↓
SUPPORTING EVIDENCE
   ↓
PROCESSING RUN
   ↓
MODEL / RULE
   ↓
CONTRADICTIONS
   ↓
UNCERTAINTY
   ↓
HUMAN REVIEW
```

And:

```text
SELECT EVIDENCE
   ↓
WHAT DID THIS CHANGE?
   ↓
EVIDENCE IMPACT
   ↓
ENTITIES
   ↓
RELATIONSHIPS
   ↓
TIMELINE
   ↓
CONTRADICTIONS
   ↓
INVESTIGATIVE QUESTIONS
```

## 195. FINAL DIRECTIVE

Act like a principal engineer responsible for a globally deployable enterprise investigation platform.

Inspect before coding.
Verify before changing.
Reuse before replacing.
Authorize before querying.
Bound before traversing.
Validate before returning.
Measure before scaling.
Test before claiming.
Document before handoff.

Never:
- invent facts
- fake relationships
- fake provenance
- fake confidence
- fake realtime
- expose secrets
- bypass authorization
- expose Neo4j to browsers
- use MCP as the production web API
- give AI unrestricted production Cypher
- treat graph analytics as guilt
- hide contradictions
- confuse hypotheses with evidence

The final Graph API is successful only when:

**the investigator sees a beautiful 3D graph because the underlying graph is correct, the graph is useful because the API is bounded and semantic, the graph is trustworthy because every important relationship can be traced to evidence/provenance, the graph is safe because authorization is enforced before retrieval, and the system remains operational even when MCP or Neo4j temporarily fails.**

## 196. NEXT HANDOFF

After completion, hand off these stable contracts to:

**Prompt #7 — 3D GRAPH ENGINE**

Handoff:
- Graph API endpoints
- node/edge DTOs
- graph query modes
- realtime events
- provenance API
- timeline API
- graph diff/replay API
- 3D loading strategy
- graph lens definitions
- security policy
- performance budgets
- MCP development workflow

## 197. OFFICIAL CURRENT REFERENCES

Neo4j Python Driver:
https://neo4j.com/docs/python-manual/current/
https://neo4j.com/docs/python-manual/current/transactions/
https://neo4j.com/docs/python-manual/current/performance/
https://neo4j.com/docs/api/python-driver/current/api.html

Cypher parameters:
https://neo4j.com/docs/cypher-manual/current/syntax/parameters/

Official Neo4j MCP:
https://neo4j.com/docs/mcp/current/
https://neo4j.com/docs/mcp/current/tools/
https://neo4j.com/docs/mcp/current/quickstart/
https://neo4j.com/docs/mcp/current/installation/
https://neo4j.com/docs/mcp/current/configuration/
https://github.com/neo4j/mcp

Use current official documentation for any version-sensitive configuration.

### APPENDIX CHECK 001 — REPOSITORY INVENTORY

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 002 — FASTAPI ROUTER AUDIT

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 003 — GRAPH SERVICE AUDIT

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 004 — NEO4J CLIENT AUDIT

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 005 — NEO4J DRIVER LIFECYCLE

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 006 — CONNECTION POOL

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 007 — TRANSACTION POLICY

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 008 — QUERY TIMEOUTS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 009 — CASE AUTHORIZATION

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 010 — TENANT AUTHORIZATION

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 011 — GRAPH SCOPE

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 012 — PERMISSION MAPPING

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 013 — SCHEMA REGISTRY

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 014 — NODE REGISTRY

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 015 — RELATIONSHIP REGISTRY

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 016 — PROVENANCE FIELDS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 017 — TEMPORAL FIELDS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 018 — CONFIDENCE FIELDS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 019 — REVIEW STATE

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 020 — CONTRADICTION MODEL

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 021 — SEARCH CONTRACT

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 022 — NEIGHBOR CONTRACT

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 023 — PATH CONTRACT

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 024 — TIMELINE CONTRACT

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 025 — PROVENANCE CONTRACT

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 026 — DIFF CONTRACT

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 027 — REPLAY CONTRACT

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 028 — STATUS CONTRACT

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 029 — REALTIME CONTRACT

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 030 — 3D DTO

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 031 — INSPECTOR DTO

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 032 — AI DTO

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 033 — EXPORT CONTRACT

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 034 — PAGINATION

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 035 — CURSOR SECURITY

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 036 — CACHING

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 037 — CACHE INVALIDATION

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 038 — PII MINIMIZATION

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 039 — REDACTION

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 040 — ERROR HANDLING

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 041 — RETRY POLICY

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 042 — CIRCUIT BREAKING

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 043 — OBSERVABILITY

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 044 — METRICS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 045 — TRACING

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 046 — STRUCTURED LOGGING

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 047 — SECURITY TESTS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 048 — LOAD TESTS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 049 — SOAK TESTS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 050 — CHAOS TESTS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 051 — GOLDEN GRAPHS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 052 — CONTRACT TESTS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 053 — OPENAPI

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 054 — VERSIONING

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 055 — ROLLBACK

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 056 — SCHEMA MIGRATION

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 057 — SHADOW DEPLOYMENT

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 058 — CANARY

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 059 — RECONCILIATION

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 060 — REBUILD

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 061 — MCP INSTALLATION

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 062 — MCP AUTHENTICATION

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 063 — MCP READONLY

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 064 — MCP ENVIRONMENT SEPARATION

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 065 — ANTIGRAVITY CONFIGURATION

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 066 — MCP SCHEMA VERIFICATION

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 067 — GDS DISCOVERY

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 068 — AI GRAPH TOOLS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 069 — GRAPHRAG GROUNDING

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 070 — AI TOKEN BUDGETS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 071 — ETHICAL SEMANTICS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 072 — KNOWLEDGE GAPS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 073 — HYPOTHESIS SANDBOX

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 074 — EVIDENCE IMPACT

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 075 — PROCESSING IMPACT

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 076 — PROVENANCE THREAD

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 077 — TEMPORAL GRAPH

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 078 — GRAPH DIFF

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 079 — INVESTIGATION REPLAY

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 080 — 3D PROGRESSIVE LOADING

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 081 — HIGH-DEGREE HANDLING

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 082 — GRAPH AGGREGATION

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 083 — GRAPH LENSES

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 084 — ACCESSIBILITY

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 085 — RESPONSIVE BEHAVIOR

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 086 — UI ERROR STATES

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 087 — DEVELOPER DIAGNOSTICS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 088 — ADMIN OPERATIONS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 089 — AUDIT EVENTS

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 090 — PRODUCTION RUNBOOK

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 091 — DISASTER RECOVERY

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 092 — CREDENTIAL ROTATION

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 093 — DEPENDENCY PINNING

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 094 — RELEASE GATE

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?

### APPENDIX CHECK 095 — PRODUCTION SCORECARD

Verify this area against the actual repository.

Required question set:
- What exists?
- Where does it live?
- Is it implemented, partial, mocked, dead, duplicated, deprecated or planned?
- What is the source of truth?
- What is the security boundary?
- What is the failure behavior?
- What is the performance impact?
- What is the testing evidence?
- Does it affect the 3D graph?
- Does it affect AI/GraphRAG?
- Does it affect provenance?
- Does it affect MCP/Antigravity?
- What must change before production?
