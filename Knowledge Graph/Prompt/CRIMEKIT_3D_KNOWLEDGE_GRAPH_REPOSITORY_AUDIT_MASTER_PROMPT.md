# CrimeKit — 3D Knowledge Graph
# MASTER PROMPT — REPOSITORY AUDIT
## World-Class Enterprise Architecture + Novel 3D Graph Readiness Audit
### Role: Principal Architect • Neo4j Graph Architect • 3D Visualization Architect • Digital Forensics Engineer • Security Architect • Distributed Systems Engineer • UX Systems Lead • Production QA Lead

---

# 0. MISSION

You are auditing an existing production-oriented digital-forensics platform called **CrimeKit**.

Your objective is NOT to immediately write code.

Your objective is to perform a **deep, evidence-based repository audit** that establishes exactly:

1. What CrimeKit already has.
2. What CrimeKit actually implements.
3. What is partial, broken, mocked, duplicated, obsolete, or planned.
4. Where Neo4j is already integrated.
5. Where the current Knowledge Graph implementation exists.
6. How the existing architecture can support a world-class interactive 3D forensic knowledge graph.
7. What must be reused.
8. What must be extended.
9. What must be redesigned.
10. What must not be touched.
11. What technical risks will prevent production readiness.
12. What architectural changes are required before implementation.
13. What opportunities exist for genuinely differentiated 3D forensic graph interactions.
14. How to turn the existing CrimeKit graph into a **high-value forensic investigation instrument**, not merely an attractive visualization.

The final objective is to prepare an implementation-ready architectural baseline for the next prompts.

---

# 1. CORE PRODUCT VISION

CrimeKit is intended to become an enterprise-grade digital-forensics and investigation platform.

The target Knowledge Graph is not just:

> "A 3D graph of nodes and edges."

The target is:

> **A secure, evidence-grounded, provenance-preserving, explainable, real-time forensic intelligence environment in which investigators can explore how people, devices, accounts, locations, communications, evidence, artifacts and timeline events are connected across a case.**

The 3D layer must make investigation easier rather than making the product visually impressive but operationally weak.

The graph should eventually support:

```text
Evidence
   ↓
Forensic Processing
   ↓
Artifact Extraction
   ↓
Entity Extraction
   ↓
Entity Resolution
   ↓
Relationship Inference
   ↓
PostgreSQL / authoritative records
   ↓
Graph Projection
   ↓
Neo4j
   ↓
Graph Analytics
   ↓
3D Knowledge Graph
   ↓
Investigator Exploration
   ↓
Evidence / Provenance
   ↓
Human Review
```

---

# 2. ABSOLUTE RULE — AUDIT BEFORE CHANGE

DO NOT begin by coding.

DO NOT "improve" code you have not inspected.

DO NOT replace technologies simply because you prefer another stack.

DO NOT create a new architecture that ignores existing CrimeKit services.

DO NOT assume that a file exists because a task description mentions it.

DO NOT assume that a feature is implemented because a button or page exists.

DO NOT assume Neo4j is configured correctly because a dependency is present.

DO NOT assume a realtime system is working because a WebSocket route exists.

DO NOT assume the current graph is connected to authoritative forensic data because the UI displays nodes.

---

# 3. REQUIRED WORKING METHOD

Follow this exact sequence:

```text
Repository Discovery
        ↓
Architecture Reconstruction
        ↓
Dependency / Runtime Audit
        ↓
Frontend Audit
        ↓
Backend Audit
        ↓
Database Audit
        ↓
Neo4j Audit
        ↓
Realtime Audit
        ↓
Security Audit
        ↓
Forensic Provenance Audit
        ↓
3D Readiness Audit
        ↓
Performance Audit
        ↓
UX / Interaction Audit
        ↓
Innovation / Novelty Gap Analysis
        ↓
Risk Classification
        ↓
Implementation Readiness Matrix
        ↓
Recommended Architecture
        ↓
Execution Plan for Next Prompts
```

Do not skip stages.

---

# 4. REPOSITORY DISCOVERY

First inspect the entire repository structure.

Identify:

- root directories
- frontend applications
- backend applications
- services
- workers
- shared packages
- database packages
- graph packages
- UI packages
- tests
- scripts
- deployment files
- Docker files
- CI/CD
- environment files
- migrations
- seed data
- configuration
- documentation
- prototypes
- archived directories
- generated files
- unused directories

Produce a repository map.

Example:

```text
CrimeKit/
├── frontend/
├── backend/
├── workers/
├── database/
├── graph/
├── tests/
├── deployment/
├── docs/
└── ...
```

Do not assume this exact structure.

Use the actual repository.

---

# 5. FILE CLASSIFICATION

For every relevant file, classify it as:

| Status | Meaning |
|---|---|
| IMPLEMENTED | actively used production code |
| PARTIAL | partially connected or incomplete |
| MOCKED | demo/mock/static data |
| DEAD | appears unused |
| DUPLICATED | functionality exists in multiple places |
| DEPRECATED | old implementation |
| PLANNED | documentation only |
| EXPERIMENTAL | prototype/research |
| UNKNOWN | cannot safely determine |

Every important conclusion must include repository evidence:

- file path
- symbol/function/component
- route
- import relationship
- configuration
- migration
- test
- or runtime reference

Do not infer implementation status from filenames alone.

---

# 6. TECH STACK INVENTORY

Build a complete technology inventory.

Inspect:

- package.json
- lockfiles
- requirements files
- pyproject.toml
- environment configuration
- Dockerfiles
- compose files
- CI files
- deployment manifests
- build configuration
- TypeScript configuration
- lint configuration
- test configuration

Identify exact versions where present.

Report:

```text
Technology
Version
Purpose
Where used
Runtime
Status
Risk
```

Pay special attention to:

- Next.js
- React
- TypeScript
- Three.js
- graph visualization libraries
- WebGL libraries
- FastAPI
- Python
- PostgreSQL
- pgvector
- Neo4j driver
- Redis
- WebSocket/SSE
- authentication
- state management
- testing tools
- observability tools
- containerization

---

# 7. FRONTEND AUDIT

Perform a deep frontend audit.

Inspect:

- routing
- layouts
- Knowledge Graph page
- case workspace
- sidebar
- global navigation
- global search
- state management
- API clients
- websocket clients
- UI component library
- CSS/Tailwind/design tokens
- loading states
- error states
- empty states
- responsive behavior
- accessibility
- suspense/client boundaries
- SSR/CSR boundaries
- hydration-sensitive code
- browser-only APIs
- WebGL usage
- canvas usage

Determine:

1. Which Knowledge Graph page currently exists?
2. Is it static, 2D, 3D, mock, or API-backed?
3. What data does it consume?
4. Where does graph state live?
5. Is graph state global or local?
6. How is selection represented?
7. Is there existing entity inspection?
8. Is there existing graph filtering?
9. Is there existing search-to-focus behavior?
10. Is there existing realtime graph updating?

---

# 8. KNOWLEDGE GRAPH PAGE AUDIT

Find every implementation associated with:

- Knowledge Graph
- graph
- neo4j
- entity graph
- relationship graph
- relationship explorer
- graph visualization
- graph analytics
- timeline graph
- graph search

Search by:

```text
KnowledgeGraph
Knowledge Graph
neo4j
cypher
graph
nodes
edges
relationships
entity
entities
GDS
Bloom
force graph
three
three.js
WebGL
WebSocket
```

For every implementation identify:

- page
- component
- data source
- backend endpoint
- data model
- visualization engine
- interaction model
- styling
- performance approach
- error handling
- tests

---

# 9. BACKEND AUDIT

Inspect the complete FastAPI/backend architecture.

Find:

- routers
- services
- repositories
- database sessions
- graph clients
- workers
- event handlers
- background jobs
- authentication
- authorization
- middleware
- exceptions
- telemetry
- WebSockets
- queues
- event schemas

Determine the existing service boundaries.

Do not merge responsibilities just because they appear related.

---

# 10. POSTGRESQL AUDIT

Inspect PostgreSQL schemas/models/migrations.

Identify:

- case model
- investigation model
- evidence model
- artifact model
- entity model
- timeline model
- processing run
- audit
- user
- role
- permissions
- provenance
- relationships if already represented relationally
- vector tables

Determine:

1. What is authoritative?
2. What is derived?
3. What can be projected into Neo4j?
4. What information is missing for graph reconstruction?
5. Are stable IDs available?
6. Are timestamps reliable?
7. Are case boundaries explicit?

Do not redesign PostgreSQL during this audit.

---

# 11. NEO4J AUDIT

Perform the deepest audit here.

Inspect:

- Neo4j dependency
- driver initialization
- connection handling
- environment variables
- database selection
- Cypher queries
- repository/service layer
- node creation
- relationship creation
- updates
- deletion
- indexes
- constraints
- migrations
- seeding
- graph projection
- graph analytics
- tests

Answer:

### Connection

- Is Neo4j actually connected?
- Where?
- With which driver?
- Which database?
- Which credentials?
- Is pooling configured?
- Are timeouts configured?
- Are retries present?
- Is TLS used?

### Schema

- Which labels exist?
- Which relationship types exist?
- Which properties exist?
- Which constraints exist?
- Which indexes exist?

### Data

- Is the graph populated from real CrimeKit data?
- Is it mock data?
- Is it manually seeded?
- Is it event-driven?
- Is it batch-projected?
- Is it rebuilt from PostgreSQL?

### Query safety

- Are Cypher queries parameterized?
- Are variable-length traversals bounded?
- Are result sizes bounded?
- Are expensive paths controlled?

---

# 12. GRAPH SOURCE-OF-TRUTH AUDIT

Determine whether the existing system has a clear rule:

```text
PostgreSQL
    ↓
authoritative
```

and:

```text
Neo4j
    ↓
relationship projection
```

If not, explicitly report the architectural ambiguity.

Detect:

- duplicated entities
- duplicated case records
- duplicated evidence records
- conflicting graph records
- graph-only facts with no provenance
- relationships that cannot be reconstructed
- graph mutations not traceable to a source

---

# 13. GRAPH PROJECTION AUDIT

Determine whether this pipeline exists:

```text
CrimeKit Domain Data
        ↓
Event / Outbox
        ↓
Queue
        ↓
Graph Projection Worker
        ↓
Neo4j
```

Inspect whether the repository supports:

- idempotency
- retries
- dead-letter handling
- reconciliation
- replay
- incremental updates
- deletions
- corrections
- relationship replacement
- provenance preservation

Report what exists and what does not.

---

# 14. FORENSIC PROVENANCE AUDIT

This is mandatory for CrimeKit.

For graph relationships determine whether the system can identify:

```text
case_id
evidence_id
artifact_id
processing_run_id
source_event_id
observed_at
created_at
confidence
extraction_method
model_version
source_system
```

For every graph-derived fact ask:

> Can the investigator trace this statement back to source evidence?

If no, mark the gap as critical.

---

# 15. CASE ISOLATION AUDIT

Verify case isolation through every layer:

```text
Frontend
   ↓
API
   ↓
Authorization
   ↓
Graph query
   ↓
Neo4j
   ↓
Cache
   ↓
Realtime
```

Look for:

- missing case filters
- client-only filtering
- unrestricted graph traversal
- cache-key collisions
- websocket over-broadcast
- cross-case query vulnerabilities
- graph relationships crossing cases unintentionally

Case isolation must be a server-side security invariant.

---

# 16. AUTHORIZATION AUDIT

Inspect:

- authentication
- session handling
- tokens
- roles
- case membership
- permissions
- graph endpoint protection
- websocket authorization

Verify:

```text
User
  ↓
Authentication
  ↓
Authorization
  ↓
Case Permission
  ↓
Graph Permission
  ↓
Neo4j Query
```

Report any direct browser-to-database exposure.

---

# 17. REALTIME AUDIT

Inspect existing:

- Redis
- Redis Streams
- Redis Pub/Sub
- WebSockets
- SSE
- background workers
- event schemas
- event dispatch
- frontend event handlers

Determine whether realtime graph updates are architecturally possible without rebuilding the platform.

Evaluate:

```text
New Event
   ↓
Event Broker
   ↓
Graph Update
   ↓
Realtime Event
   ↓
3D Graph
```

Check:

- reconnect
- duplicate events
- event ordering
- backpressure
- stale event handling
- subscription authorization
- heartbeat
- cleanup

---

# 18. 3D READINESS AUDIT

Determine current capability for:

- Three.js
- WebGL
- 3D force graph
- custom shaders
- instancing
- GPU rendering
- animation loop
- camera management
- orbit controls
- raycasting
- labels
- LOD
- graph clustering
- dynamic graph updates

Answer:

1. What 3D libraries already exist?
2. Which should be reused?
3. Which are unnecessary?
4. Is the frontend architecture compatible with 3D rendering?
5. Are there SSR/hydration risks?
6. Is there already a canvas component?
7. Are there performance bottlenecks?

---

# 19. REFERENCE DESIGN AUDIT

Use the supplied CrimeKit/Neo4j/3D reference screenshots as **visual and interaction references**, not as code to copy.

Reference concepts include:

- dark enterprise workspace
- compact side navigation
- large graph canvas
- spatial 3D node visualization
- relationship lines
- node labels
- camera controls
- graph minimap
- side inspector
- analysis controls
- live event context
- search
- filtering

The file-folder screenshot supplied with this task establishes that the user has a dedicated reference-design collection under a Knowledge Graph design folder.

The audit must account for the fact that those references may contain multiple UI directions.

Do not assume one screenshot is the final design.

---

# 20. VISUAL REFERENCE COMPARISON

Compare the current CrimeKit Knowledge Graph implementation against the visual direction represented by the reference materials.

Evaluate:

### Layout

- navigation
- header
- graph canvas
- filters
- inspector
- analysis bar

### Visual language

- background
- contrast
- borders
- typography
- node colors
- graph density
- control density

### Interaction

- zoom
- pan
- rotate
- node selection
- graph focus
- graph expansion
- live graph updates

### Enterprise quality

- clarity
- information hierarchy
- consistency
- accessibility
- error handling
- forensic context

Do not recommend visual novelty merely for novelty.

---

# 21. NOVELTY MISSION

The ultimate target is a Knowledge Graph experience that is **meaningfully differentiated** from ordinary enterprise network graphs.

Important:

Do NOT make unsupported claims such as:

> "Nobody in the world has ever built this."

You cannot prove global uniqueness from a repository audit.

Instead:

Identify:

- original interaction opportunities
- CrimeKit-specific graph semantics
- underused forensic visualization patterns
- novel evidence-to-graph workflows
- novel temporal + graph combinations
- novel provenance visualization
- novel graph risk explanation
- novel human-review interactions

The desired innovation must emerge from the **forensic problem**, not cosmetic 3D effects.

---

# 22. INNOVATION DISCOVERY AREAS

During the audit, search the existing code for whether the platform already supports or could support these future concepts.

## 22.1 Evidence Gravity

Visual importance based on evidence density:

```text
More supporting evidence
        ↓
larger visual mass / stronger presence
```

Do not map importance directly to guilt.

---

## 22.2 Provenance Threads

Instead of a relationship being only:

```text
PERSON ──USES──> DEVICE
```

the future 3D interface can reveal a provenance thread:

```text
Evidence
   ↓
Artifact
   ↓
Extraction
   ↓
Relationship
   ↓
Entity
```

The audit must determine whether current data models contain enough information to enable this.

---

## 22.3 Temporal Graph Layers

A graph should potentially show:

```text
Past
  ↓
Present
  ↓
Investigative projection
```

with clear visual distinction between:

- observed historical facts
- derived relationships
- current events
- analytical predictions

Audit whether timestamps and event models can support this.

---

## 22.4 Investigation Replay

Potential future interaction:

```text
Play investigation
       ↓
Evidence arrives
       ↓
Entities appear
       ↓
Relationships appear
       ↓
Timeline evolves
       ↓
Graph changes
```

Audit whether event/provenance history already exists.

---

## 22.5 Graph Time Machine

Potential future interaction:

```text
[ 08:00 ]──────────[ 12:00 ]──────────[ 16:00 ]

Drag time
   ↓
graph rewinds / advances
```

Audit whether event timestamps can support deterministic reconstruction.

---

## 22.6 Relationship Confidence Field

Relationships could visually communicate:

```text
Observed
Derived
Inferred
Possible
Conflicting
Deprecated
```

Audit whether the current graph model supports relationship state.

---

## 22.7 Contradiction Mode

Potential future feature:

```text
Evidence A
   ↓
supports relationship

Evidence B
   ↓
contradicts relationship
```

Visualize conflicting evidence rather than hiding it.

Audit whether current provenance and evidence models can support contradiction tracking.

---

## 22.8 Forensic Lens System

Future 3D lens modes:

```text
Relationship Lens
Timeline Lens
Evidence Lens
Risk Lens
Provenance Lens
Entity Lens
Location Lens
Communication Lens
```

Determine whether the current UI architecture can support pluggable graph lenses.

---

## 22.9 Graph Story Mode

Investigator could select:

```text
Start Entity
      ↓
Evidence
      ↓
Relationship
      ↓
Entity
      ↓
Timeline Event
```

and CrimeKit could generate a structured investigation path.

The audit must determine whether existing graph APIs can support path narratives.

---

## 22.10 Explainable Graph Focus

When an entity becomes visually important, explain:

```text
Why is this entity highlighted?
```

Possible basis:

- degree
- centrality
- evidence volume
- recency
- repeated appearance
- anomaly score
- investigator selection
- graph path membership

The audit must identify which metrics are already available.

---

# 23. 3D SEMANTIC RENDERING AUDIT

Do not focus only on geometry.

Determine how future visual encoding can represent:

### Node type

- geometry
- icon
- text
- material

### Relationship type

- line type
- arrow
- thickness
- label

### Confidence

- opacity
- halo
- badge
- pattern

### Temporal state

- motion
- fading
- layer
- timeline lock

### Evidence support

- visible provenance link

### Investigation priority

- subtle size/emphasis

Do not use color as the only semantic channel.

---

# 24. ANTI-GIMMICK RULE

The following are NOT acceptable as "innovation" by themselves:

```text
❌ random floating planets
❌ excessive glowing effects
❌ decorative particles
❌ unnecessary holograms
❌ constant node animation
❌ cyberpunk styling
❌ game-like camera motion
❌ meaningless neon colors
❌ 3D purely for visual novelty
```

Every visual effect must communicate information or improve navigation.

---

# 25. PERFORMANCE READINESS AUDIT

Determine whether the repository can support:

```text
100 graph nodes
1,000 graph nodes
10,000 persisted entities
100,000+ persisted graph relationships
```

Important distinction:

> Persisted graph size is not equal to simultaneously rendered graph size.

Audit:

- graph query limits
- API pagination
- progressive loading
- lazy expansion
- client-side graph state
- render loop
- labels
- WebGL
- memory management
- event batching
- cache
- database indexes

---

# 26. GRAPH QUERY PERFORMANCE AUDIT

Look for dangerous patterns such as:

```cypher
MATCH (n)
RETURN n
```

or:

```cypher
MATCH p=(a)-[*]-(b)
RETURN p
```

without bounded scope.

Flag:

- unbounded traversals
- huge result sets
- missing indexes
- expensive path searches
- accidental Cartesian products
- repeated queries
- N+1 graph requests

---

# 27. FRONTEND RENDER PERFORMANCE AUDIT

Determine whether the current architecture can avoid:

- full graph re-render on every event
- full React tree updates on node movement
- unnecessary object recreation
- expensive label rendering
- excessive shadow/material calculations
- memory leaks
- uncontrolled animation loops
- repeated force simulation

Recommend architecture, but do not implement it during this audit.

---

# 28. GRAPH API CONTRACT AUDIT

Find every existing graph-related endpoint.

For each endpoint document:

```text
Method
Path
Authentication
Authorization
Input
Output
Pagination
Limits
Errors
Performance
Source
Status
```

Determine whether a clean future graph API is possible without breaking existing APIs.

---

# 29. DATA CONTRACT AUDIT

Verify whether the current backend can return:

```text
nodes[]
edges[]
meta{}
```

with:

- stable IDs
- entity type
- display label
- selected properties
- risk/priority if available
- relationship type
- direction
- confidence
- provenance references

If missing, identify exactly which source model prevents it.

---

# 30. ENTITY RESOLUTION AUDIT

Investigate current entity resolution capabilities.

Look for:

- exact matching
- fuzzy matching
- embeddings
- vector search
- identity resolution
- duplicate detection
- entity linking

Determine whether graph relationships are:

```text
Observed
or
Resolved
or
Inferred
```

The future 3D graph must distinguish these categories.

---

# 31. SEARCH AUDIT

Inspect current search.

Determine whether it can search:

- names
- entity IDs
- devices
- IPs
- emails
- accounts
- evidence
- artifacts

Determine whether search can eventually drive:

```text
search
 ↓
entity result
 ↓
graph focus
 ↓
local expansion
 ↓
inspector
```

---

# 32. TIMELINE AUDIT

Inspect current timeline implementation.

Determine:

- event model
- timestamps
- timezone normalization
- confidence
- source
- evidence linkage
- case scope
- processing run linkage

Determine whether graph/timeline synchronization is architecturally possible.

---

# 33. EVIDENCE AUDIT

Inspect evidence workflow:

```text
Upload
 ↓
Hash
 ↓
Store
 ↓
Process
 ↓
Extract artifact
 ↓
Extract entity
 ↓
Relationship
```

Determine exactly where graph projection should occur.

---

# 34. PROCESSING AUDIT

Inspect forensic processing workers and workflows.

Look for integrations such as:

- TSK
- libewf
- OCR
- metadata extraction
- media processing
- speech-to-text
- entity extraction
- timeline extraction
- face trace
- file analysis

Determine which outputs can become graph entities/relationships.

Do not assume planned integrations are implemented.

---

# 35. FACE TRACE / VIDEO GRAPH AUDIT

If CrimeKit contains face tracing or video analysis:

Determine whether the graph can eventually represent:

```text
Person
   ↓
Face Observation
   ↓
Frame
   ↓
Video
   ↓
Camera
   ↓
Location
   ↓
Timestamp
```

Audit:

- detection IDs
- track IDs
- embeddings
- candidate matches
- confidence
- provenance
- evidence linkage

Do not classify a candidate face match as identity confirmation.

---

# 36. AI INTEGRATION AUDIT

Inspect existing:

- AI agents
- LLM service
- RAG
- embeddings
- graph tools
- tool calling
- agent memory
- orchestration

Determine whether AI currently:

```text
reads graph facts
```

or:

```text
invents / constructs graph facts
```

The future architecture must enforce:

```text
Graph = source of relationship facts
Evidence = source of forensic support
AI = explanation/reasoning layer
Human = final decision
```

---

# 37. ETHICAL / LEGAL SAFETY AUDIT

The graph must never silently transform:

```text
risk
```

into:

```text
guilt
```

Audit UI and code for terminology such as:

- suspect
- offender
- guilty
- criminal
- dangerous

Determine whether language is evidence-grounded.

Prefer:

- person of interest
- investigation subject
- high-priority entity
- anomaly
- risk score
- confidence
- analytical result

where appropriate.

---

# 38. AUDIT AI HALLUCINATION BOUNDARIES

Look for any code where AI can create:

- relationships
- identities
- conclusions
- evidence assertions

without validation.

Flag as high risk.

The future architecture should require:

```text
AI claim
 ↓
retrieval
 ↓
source evidence / graph
 ↓
verification
 ↓
display with provenance
```

---

# 39. SECURITY RISK SCORING

Classify findings:

### P0 — Critical

Could:

- expose evidence
- cross case boundaries
- compromise credentials
- corrupt forensic provenance
- allow unsafe graph mutation

### P1 — High

Could:

- break core graph operations
- create inconsistent graph state
- cause severe performance problems

### P2 — Medium

Could:

- degrade usability
- increase maintenance cost
- reduce observability

### P3 — Low

Cosmetic or future improvement.

---

# 40. ARCHITECTURAL RISK MATRIX

Produce:

| Finding | Severity | Evidence | Impact | Recommended action |
|---|---|---|---|---|

Do not inflate severity merely to justify changes.

---

# 41. REUSE-FIRST ANALYSIS

For every required future component, answer:

```text
Already exists?
    |
    +-- YES → Reuse / extend
    |
    +-- PARTIAL → complete / refactor carefully
    |
    +-- NO → introduce minimal new component
```

Do NOT introduce a new component if an existing one can safely support the requirement.

---

# 42. "DO NOT TOUCH" LIST

Create an explicit list of modules that should remain unchanged because they are stable or unrelated.

Examples could include:

- authentication
- evidence ingestion
- case management
- audit system
- existing report generator

But only list actual repository components after inspection.

---

# 43. "MUST CHANGE" LIST

Create an explicit list of files/modules that must change for 3D graph integration.

For every item state:

```text
Path
Current role
Required change
Why
Risk
Dependencies
```

---

# 44. "NEW COMPONENTS NEEDED" LIST

Only after repository analysis identify genuinely missing components.

Potential categories:

```text
Graph API
Graph Projection Worker
Graph Schema
Graph Query Service
3D Canvas
Graph Interaction Controller
Graph Inspector
Realtime Graph Adapter
GDS Service
Graph Performance Layer
```

Do not assume all are required.

---

# 45. DEPENDENCY GAP ANALYSIS

Determine:

```text
Already installed
Can be reused
Needs upgrade
Needs new dependency
Should NOT be added
```

Pay attention to:

- Three.js
- graph renderer
- camera controls
- label rendering
- state management
- testing tools

Avoid competing graph libraries.

---

# 46. ARCHITECTURE CONSISTENCY CHECK

Compare the current system against the desired boundary:

```text
PostgreSQL
    ↓
Domain Event
    ↓
Redis
    ↓
Projection
    ↓
Neo4j
    ↓
FastAPI
    ↓
3D UI
```

Identify every deviation.

For each deviation explain:

- why it exists
- whether it is dangerous
- whether it should be retained
- whether it must change

---

# 47. PRODUCTION READINESS SCORECARD

Score from 0–10:

| Area | Score |
|---|---:|
| Repository structure | /10 |
| Backend architecture | /10 |
| Frontend architecture | /10 |
| PostgreSQL data model | /10 |
| Neo4j integration | /10 |
| Graph ontology | /10 |
| Projection pipeline | /10 |
| Graph API | /10 |
| 3D readiness | /10 |
| Realtime | /10 |
| Security | /10 |
| Case isolation | /10 |
| Provenance | /10 |
| Performance | /10 |
| Testing | /10 |
| Observability | /10 |
| UX readiness | /10 |
| Innovation readiness | /10 |

Do not give arbitrary high scores.

Each score must be supported by evidence.

---

# 48. 3D KNOWLEDGE GRAPH READINESS SCORE

Give one overall score:

```text
Current readiness:
__/100
```

Use:

```text
Architecture
Data
Neo4j
API
3D
Realtime
Security
Provenance
Performance
UX
Innovation
```

Explain the score with evidence.

---

# 49. INNOVATION READINESS

Create three categories:

## Existing strengths

What CrimeKit already does that can support differentiation.

## Unique opportunities

Potential CrimeKit-specific interactions that are technically feasible.

## Speculative ideas

Interesting ideas that require new research or substantial architecture.

Never present speculative ideas as implemented features.

---

# 50. NOVELTY EVALUATION FRAMEWORK

Evaluate candidate innovations using:

| Criterion | Question |
|---|---|
| Forensic value | Does it improve investigation? |
| Explainability | Can the UI show why? |
| Evidence grounding | Can claims trace to source evidence? |
| Technical feasibility | Can current architecture support it? |
| Differentiation | Is it meaningfully different from ordinary graph UI? |
| Scalability | Can it work beyond a demo? |
| Ethics | Could it create misleading conclusions? |
| UX value | Does it reduce investigator effort? |
| Performance | Can it run interactively? |
| Defensibility | Can the behavior be explained to reviewers? |

Rank proposed concepts.

---

# 51. DO NOT OVERENGINEER

Do NOT recommend:

- Kafka merely because realtime exists
- OpenSearch merely because search exists
- GraphQL merely because Neo4j supports it
- microservices merely because enterprise systems use them
- Kubernetes merely because production systems use containers
- GPU rendering where CPU is sufficient
- custom shader systems without measurable value
- multiple graph databases for the same job

Use the simplest architecture that meets the requirements.

---

# 52. GRAPH DATABASE RESPONSIBILITY CHECK

Confirm that Neo4j is being used where it has a strong architectural reason:

```text
Entity relationship traversal
Graph analytics
Path discovery
Community detection
Graph-based retrieval
Relationship exploration
```

Do not use Neo4j as a dumping ground for:

- every evidence byte
- large binary files
- full document contents when unnecessary
- duplicate relational records with no graph value

---

# 53. GRAPH VERSUS RELATIONAL RESPONSIBILITY

Produce a table:

| Requirement | PostgreSQL | Neo4j | Why |
|---|---|---|---|
| Case record | ✅ | reference | authoritative |
| Evidence metadata | ✅ | reference | authoritative |
| Original file | ❌ | ❌ | object storage |
| Person entity | authoritative | projection | graph traversal |
| Person-device relation | reference if needed | ✅ | graph |
| Timeline event | authoritative | projection | temporal correlation |
| Vector search | existing pgvector where applicable | optional | contextual retrieval |

Adapt to actual repository data.

---

# 54. REQUIRED AUDIT OUTPUT — EXECUTIVE SUMMARY

At the end provide a concise executive summary:

```text
Current architecture:
...

Current graph status:
...

Current Neo4j status:
...

Current 3D status:
...

Biggest production risk:
...

Biggest architectural gap:
...

Strongest reusable component:
...

Strongest innovation opportunity:
...

Recommended next implementation step:
...
```

---

# 55. REQUIRED AUDIT OUTPUT — ARCHITECTURE MAP

Produce:

```text
CURRENT

[Actual CrimeKit components and flows]
```

and:

```text
TARGET

CrimeKit
  ↓
Graph Event Pipeline
  ↓
Neo4j
  ↓
FastAPI Graph API
  ↓
3D Graph
```

Clearly label:

```text
EXISTING
PARTIAL
MISSING
RECOMMENDED
```

---

# 56. REQUIRED AUDIT OUTPUT — FILE MAP

Generate:

```text
FRONTEND
Backend
Neo4j
Data
Realtime
Security
Testing
Deployment
```

For each important file:

```text
Path
Role
Status
Dependencies
Relevant finding
```

---

# 57. REQUIRED AUDIT OUTPUT — GRAPH IMPLEMENTATION MAP

Create:

```text
Entity
Source model
Neo4j label
Stable ID
Relationships
Provenance
Projection source
API endpoint
UI representation
```

This becomes the foundation for the next graph ontology prompt.

---

# 58. REQUIRED AUDIT OUTPUT — 3D IMPLEMENTATION MAP

Create:

```text
Feature
Existing capability
Current file
Target component
Dependency
Risk
Priority
```

Features:

- 3D canvas
- nodes
- edges
- labels
- camera
- hover
- click
- drag
- expansion
- focus
- path
- filters
- search
- inspector
- minimap
- timeline
- provenance
- analytics
- realtime
- table mode

---

# 59. REQUIRED AUDIT OUTPUT — INNOVATION MAP

Create a ranked matrix:

| Concept | Forensic value | Feasible now? | Differentiation | Risk | Priority |
|---|---:|---:|---:|---:|---:|

Include only ideas grounded in the actual CrimeKit architecture.

Possible themes:

```text
Evidence Gravity
Provenance Threads
Graph Time Machine
Investigation Replay
Temporal Layers
Contradiction Mode
Forensic Lenses
Graph Story Mode
Explainable Focus
Confidence-aware Relationships
Live Evidence Emergence
Case Network Comparison
Cross-artifact Correlation
```

These are candidate concepts, not claims of global novelty.

---

# 60. REQUIRED AUDIT OUTPUT — SECURITY FINDINGS

Provide:

```text
Critical
High
Medium
Low
```

with exact code locations.

---

# 61. REQUIRED AUDIT OUTPUT — PERFORMANCE FINDINGS

Provide:

- likely bottlenecks
- graph query risks
- frontend rendering risks
- realtime risks
- memory risks
- scaling risks
- recommended measurements

Do not make unsupported performance claims.

---

# 62. REQUIRED AUDIT OUTPUT — TEST GAPS

Identify missing:

- unit tests
- integration tests
- graph tests
- projection tests
- authorization tests
- cross-case isolation tests
- websocket tests
- UI tests
- 3D interaction tests
- performance tests
- recovery tests

---

# 63. REQUIRED AUDIT OUTPUT — DEPLOYMENT GAPS

Inspect deployment.

Determine compatibility with the intended production direction.

Audit:

- environment variables
- secret handling
- frontend deployment
- backend deployment
- database
- Neo4j Aura
- Redis
- object storage
- WebSockets
- HTTPS
- CORS
- health checks
- logging
- monitoring

Do not redesign hosting during this audit unless the current setup creates a blocking risk.

---

# 64. REQUIRED AUDIT OUTPUT — IMPLEMENTATION GATES

Define gates:

## Gate A — Data correctness

Graph records map correctly to authoritative data.

## Gate B — Provenance

Every important derived relationship is traceable.

## Gate C — Security

No cross-case access.

## Gate D — Graph correctness

Relationships have defensible semantics.

## Gate E — API

Graph API has bounded queries.

## Gate F — 3D

Graph is interactively usable.

## Gate G — Realtime

Events update graph without destabilizing the UI.

## Gate H — Performance

Representative datasets remain usable.

## Gate I — Testing

Critical paths are automated.

## Gate J — Production

Monitoring/recovery/security are complete.

---

# 65. HARD QUALITY BAR

The audit must think like an international enterprise software company.

Ask continuously:

> Would we trust this architecture in a serious production investigation environment?

> Can another engineer understand it six months from now?

> Can the graph be rebuilt if Neo4j is lost?

> Can every relationship be explained?

> Can every graph result be scoped to a case?

> Can the system fail gracefully?

> Can we observe it?

> Can we test it?

> Can the UI remain usable with a large graph?

> Can an investigator distinguish fact from inference?

> Can a reviewer understand why the graph looks the way it does?

If the answer is no, document the gap.

---

# 66. NO FALSE CONFIDENCE

Never write:

```text
"Everything is production-ready."
```

unless repository evidence supports it.

Never write:

```text
"Neo4j is fully integrated."
```

unless actual code/data flow proves it.

Never write:

```text
"Realtime graph works."
```

unless the full event-to-UI path exists.

Never write:

```text
"3D rendering is scalable."
```

without testing or architecture evidence.

---

# 67. NO IMPLEMENTATION DURING THIS PROMPT

This is a **REPOSITORY AUDIT**.

Unless required to prove an issue, DO NOT:

- rewrite application files
- redesign the UI
- replace dependencies
- migrate data
- change schema
- deploy services
- alter production configuration

The output of this prompt should be an **implementation blueprint**, not a speculative rewrite.

If you absolutely must execute a non-destructive command or isolated experiment to verify something, do so only when necessary and document it.

---

# 68. EVIDENCE STANDARD

Every important finding must point to evidence.

Preferred evidence:

1. source code
2. imports
3. route declarations
4. database schema/migrations
5. configuration
6. tests
7. actual API contracts
8. build configuration
9. documentation only when code does not establish behavior

Documentation alone is not proof of implementation.

---

# 69. CONFLICT RESOLUTION

If documentation says:

```text
Neo4j is implemented
```

but source code indicates:

```text
Neo4j connection exists but no projection
```

report:

```text
Documentation status: IMPLEMENTED
Repository status: PARTIAL
```

Do not silently reconcile them.

Use actual implementation evidence as the implementation-status source.

---

# 70. LEGACY CODE DETECTION

Search for:

- duplicate graph services
- abandoned graph components
- old APIs
- previous graph schemas
- legacy libraries
- stale environment variables
- unused imports
- old Neo4j drivers
- old websocket handlers
- duplicate types

Do not delete anything during audit.

Mark candidates for later cleanup.

---

# 71. MOCK DATA DETECTION

Detect whether graph screens use:

- hardcoded arrays
- static JSON
- placeholder entities
- fake risk scores
- fake relationship counts
- demo labels
- seeded development data

Classify:

```text
UI demo
development seed
test fixture
production data path
```

---

# 72. GRAPH INTEGRITY CHECK

If possible, verify representative relationships.

Example:

```text
Person → Device
Device → IP
IP → Location
Evidence → Artifact
Artifact → Person
```

Trace each one backward to its source.

Document any broken chain.

---

# 73. 3D TECHNOLOGY DECISION AUDIT

Do not automatically recommend one library.

Inspect current dependencies and compare candidate approaches based on:

- performance
- WebGL support
- React compatibility
- dynamic updates
- force-directed layouts
- labels
- interaction
- maintainability
- license
- bundle size
- developer experience

The final recommendation must be repository-aware.

---

# 74. VISUAL DESIGN SYSTEM AUDIT

Identify:

- fonts
- typography scale
- spacing
- border radius
- colors
- shadows
- icons
- buttons
- panels
- tables
- badges

Determine whether the current design system can support the new 3D graph without creating a visually disconnected subsystem.

---

# 75. INVESTIGATOR EXPERIENCE AUDIT

Evaluate task completion.

Could an investigator quickly:

```text
open case
find person
focus node
expand device
inspect relationship
view evidence
inspect provenance
find path
inspect timeline
run graph analytics
return to evidence
```

If not, identify UX bottlenecks.

---

# 76. GRAPH DENSITY AUDIT

Determine whether the current architecture distinguishes:

```text
Overview graph
Local graph
Path graph
Evidence graph
Timeline graph
Community graph
```

A production forensic tool should avoid showing everything at once.

---

# 77. GRAPH VIEW MODES

Audit whether the architecture could support future modes:

```text
3D
2D
Table
Timeline
Path
Community
Evidence-centric
Relationship-centric
```

3D should be the primary exploratory mode but not the only representation.

---

# 78. DEEP LINKING AUDIT

Determine whether routes can represent:

```text
/cases/{case_id}/knowledge-graph
```

and optionally:

```text
?entity={entity_id}
```

without exposing unauthorized data.

---

# 79. OBSERVABILITY AUDIT

Look for:

- structured logging
- request IDs
- correlation IDs
- metrics
- traces
- health endpoints
- error monitoring

For graph systems identify future metrics:

```text
graph_query_latency
graph_projection_lag
neo4j_connection_state
graph_api_errors
graph_nodes_returned
graph_edges_returned
realtime_graph_events
graph_event_lag
```

---

# 80. FINAL REPORT STRUCTURE

Produce the final audit report in exactly this high-level order:

```text
1. Executive Summary
2. Repository Map
3. Current Architecture
4. Technology Inventory
5. Frontend Audit
6. Backend Audit
7. PostgreSQL Audit
8. Neo4j Audit
9. Graph Ontology Status
10. Graph Projection Status
11. API Status
12. Realtime Status
13. Security Status
14. Forensic Provenance Status
15. 3D Readiness
16. UX / Design Audit
17. Performance Audit
18. AI / GraphRAG Audit
19. Ethics / Explainability Audit
20. Innovation Opportunities
21. Risk Matrix
22. Reuse / Modify / New Matrix
23. Required File Changes
24. Do-Not-Touch List
25. Missing Components
26. Test Gaps
27. Deployment Gaps
28. Readiness Scorecard
29. Recommended Target Architecture
30. Next Implementation Prompts
31. Final Decision
```

---

# 81. FINAL DECISION

At the end explicitly classify the repository:

```text
READY TO IMPLEMENT 3D
```

or:

```text
READY AFTER BLOCKING FIXES
```

or:

```text
MAJOR ARCHITECTURE REPAIR REQUIRED
```

Explain exactly why.

---

# 82. NEXT-PROMPT HANDOFF

The final section must create a precise handoff for the next prompt.

Generate:

```text
NEXT PROMPT 03 — GRAPH ONTOLOGY
```

with:

- confirmed existing entities
- confirmed relationships
- missing fields
- provenance gaps
- source tables
- projection requirements
- Neo4j schema requirements

Then:

```text
NEXT PROMPT 04 — NEO4J PRODUCTION SETUP
```

with confirmed technical requirements.

Then:

```text
NEXT PROMPT 05 — GRAPH PROJECTION
```

with confirmed source → event → graph flow.

Do not write the full next prompts yet unless specifically requested.

---

# 83. FINAL ARCHITECTURE PRINCIPLE

The audit must ultimately validate or correct toward this conceptual separation:

```text
                    CRIMEKIT

Evidence ───────────────┐
                        ↓
                 Forensic Processing
                        ↓
                 PostgreSQL
              AUTHORITATIVE RECORDS
                        ↓
                  Domain Events
                        ↓
                    Redis
                        ↓
              Graph Projection Worker
                        ↓
                    Neo4j Aura
                        ↓
              Relationship Intelligence
                        ↓
                Graph Analytics / Search
                        ↓
                    FastAPI
                        ↓
                 3D Graph Engine
                        ↓
                Investigator Workspace
                        ↓
        Evidence + Timeline + Provenance
                        ↓
                   Human Review
```

---

# 84. FINAL SUCCESS CRITERIA

This prompt is successful only when the repository audit gives us enough concrete information to build the next stage **without guessing**.

The next engineer should be able to read the audit and know:

```text
WHAT EXISTS
WHAT WORKS
WHAT DOES NOT
WHAT IS CONNECTED
WHAT IS MOCKED
WHAT IS DANGEROUS
WHAT MUST STAY
WHAT MUST CHANGE
WHAT IS MISSING
WHAT CAN BE REUSED
WHAT THE GRAPH SHOULD REPRESENT
HOW 3D CAN FIT
HOW REALTIME CAN FIT
HOW PROVENANCE CAN FIT
HOW SECURITY CAN FIT
HOW PERFORMANCE CAN FIT
WHERE INNOVATION IS POSSIBLE
WHAT TO BUILD NEXT
```

The audit is the architectural truth baseline for the subsequent CrimeKit 3D Knowledge Graph implementation prompts.

---

# 85. MASTER DIRECTIVE

Think like:

- a principal engineer reviewing a mission-critical platform
- a forensic systems architect protecting evidence integrity
- a Neo4j graph architect designing for complex relationship analysis
- a 3D graphics engineer building interactive visualization at scale
- a security architect protecting case boundaries
- a UX architect reducing investigator cognitive load
- a distributed systems engineer designing reliable event flows
- an enterprise CTO evaluating long-term maintainability
- a product strategist looking for meaningful differentiation

Do NOT optimize for:

```text
"looks impressive in a screenshot"
```

Optimize for:

```text
trust
clarity
evidence
provenance
security
performance
explainability
investigator workflow
reliability
maintainability
meaningful innovation
```

The desired future is not merely a graph.

It is:

> **CrimeKit — a living 3D forensic knowledge environment where evidence-derived relationships, time, provenance, analytical signals, and investigator intent can be explored together while maintaining strict security, explainability, ethical boundaries, and production-grade reliability.**

Perform the audit first.

Prove what exists.

Expose what is missing.

Protect what already works.

Identify what must change.

Find the strongest opportunities for differentiation.

Then produce the implementation blueprint for the next prompt.
