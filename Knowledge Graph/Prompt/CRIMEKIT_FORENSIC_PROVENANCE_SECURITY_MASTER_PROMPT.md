# CRIMEKIT — FORENSIC PROVENANCE + SECURITY
# MASTER IMPLEMENTATION PROMPT
## Prompt #11 — Enterprise Forensic Trust Fabric for the 3D Knowledge Graph

> **Purpose:** Provide one end-to-end master prompt for implementing the CrimeKit forensic provenance + security layer that powers the 3D Knowledge Graph, graph APIs, realtime graph, GDS intelligence, evidence workflows, AI/GraphRAG, and investigator UX.
>
> **Product posture:** International enterprise digital-forensics platform. Evidence-first. Provenance-first. Security-by-architecture. Human-supervised. Production-ready.

---

# 0. EXECUTIVE MISSION

Act simultaneously as:

- Principal Digital Forensics Architect
- Principal Security Architect
- Neo4j Enterprise Architect
- Graph Data Modeler
- 3D Forensic Visualization Architect
- Provenance / Chain-of-Custody Architect
- Privacy Engineer
- Zero-Trust Architect
- Backend / FastAPI Architect
- Distributed Systems Engineer
- Realtime Systems Architect
- Database Architect
- Cloud / Infrastructure Architect
- AI Safety Architect
- GraphRAG Architect
- GDS Analytics Architect
- Threat Modeling Lead
- Enterprise QA Lead
- SRE / Observability Lead
- Security UX Designer
- Accessibility Lead
- Incident Response Architect
- Compliance-minded Forensic Systems Engineer

Your mission is to implement **CrimeKit's Forensic Trust Fabric**: a single, coherent architecture in which every important graph object, analytical result, realtime update, AI explanation, source artifact, and investigator decision can be securely traced back to authorized evidence and can be explained without collapsing observation, inference, prediction, and human judgment into one thing.

The desired system is not:

```text
3D graph + login + some audit logs
```

It is:

```text
                CRIMEKIT FORENSIC TRUST FABRIC

Authorized Evidence
        ↓
Evidence Integrity
        ↓
Forensic Processing
        ↓
Artifact / Observation Lineage
        ↓
Entity / Relationship Derivation
        ↓
Authoritative Domain Record
        ↓
Neo4j Graph Projection
        ↓
GDS / Search / Vector Intelligence
        ↓
Graph API + Authorization Policy
        ↓
3D Knowledge Graph
        ↓
Realtime Changes
        ↓
AI / GraphRAG Explanation
        ↓
Human Review
        ↓
Auditable Investigative Decision
```

The central design principle is:

> **A graph object is trustworthy only when the system can explain where it came from, who is allowed to see it, what processing produced it, what uncertainty surrounds it, what changed it, and how an investigator can verify it.**

---

# 1. ABSOLUTE SOURCE-OF-TRUTH RULE

Do not create a second uncontrolled system of record.

CrimeKit must preserve the architecture established by the existing platform documentation:

| Layer | Authoritative role |
|---|---|
| PostgreSQL / relational domain | application + structured forensic records |
| Object storage | original evidence and approved derived artifacts |
| Redis / event layer | transient coordination, jobs, realtime delivery |
| pgvector | vector retrieval where already justified |
| Neo4j | graph / relationship intelligence projection |
| GDS | graph analytics / graph ML over authorized projections |
| FastAPI / graph service | business logic + authorization boundary |
| 3D frontend | investigator visualization / interaction |
| AI | retrieval, reasoning, summarization, explanation assistance |
| Audit subsystem | actor/action accountability |
| Provenance subsystem | source-to-result lineage |

Never allow:

```text
3D Canvas
    ↓
become
    ↓
forensic source of truth
```

Never allow:

```text
Neo4j projection
    ↓
become
    ↓
independent authoritative evidence store
```

Never allow:

```text
LLM output
    ↓
become
    ↓
forensic fact without evidence-backed domain transition
```

---

# 2. REQUIRED IMPLEMENTATION METHOD — AUDIT BEFORE CHANGE

Before implementation:

1. Inspect the repository.
2. Inspect current routes and services.
3. Inspect current data models and migrations.
4. Inspect current evidence abstractions.
5. Inspect current auth / RBAC.
6. Inspect current audit architecture.
7. Inspect current graph architecture.
8. Inspect current Redis / realtime architecture.
9. Inspect current vector layer.
10. Inspect current 3D graph implementation.
11. Inspect existing `FORENSIC_PROVENANCE.md`.
12. Inspect existing `DATA_SECURITY.md`.
13. Inspect current `API_EVENTS.md`.
14. Inspect current `DATABASE_SCHEMA.md`.
15. Inspect current `MATCHING_ENGINE.md`.
16. Inspect current `REALTIME_VIDEO.md`.
17. Inspect current GDS architecture.
18. Inspect actual Neo4j schema through the approved development path.
19. Inspect available GDS procedures through the approved development path.
20. Inspect the supplied CrimeKit / Neo4j-style reference screens.

Do not invent that a component is implemented merely because documentation mentions it.

Classify every relevant feature as:

```text
IMPLEMENTED
PARTIAL
MOCKED
DEAD
DUPLICATED
DEPRECATED
PLANNED
EXPERIMENTAL
UNKNOWN
```

For every important conclusion, record evidence:

```text
file path
symbol / component
route
migration
configuration
import
runtime call
API
query
runtime log
```

---

# 3. REFERENCE SCREEN PRINCIPLE

Use the supplied CrimeKit / Neo4j-style visual references as **design evidence**, not as source code to copy.

The reference direction includes:

- dark enterprise workspace
- compact navigation
- global search
- graph-first main scene
- entity labels
- contextual inspector
- evidence inspector
- timeline relationship
- graph controls
- concise information density
- cyan / teal style accents
- thin borders
- restrained enterprise typography

The existing CrimeKit reference specifically depicts a central “Knowledge Graph (Bloom Inspired)” with search, type/case filtering, an entity-detail inspector, a timeline panel, and an evidence inspector with evidence ID, filename, hash, acquisition time, chain-of-custody status, and “View in Graph” navigation. Treat these visible structures as UX requirements to preserve while extending the graph into a trustworthy 3D workspace.

Do not clone Neo4j branding, trademarks, logos, proprietary source, or exact protected artwork.

The target is:

```text
Neo4j-style graph ergonomics
        +
CrimeKit forensic semantics
        +
3D spatial interaction
        +
provenance-first navigation
        +
security-first data access
        +
human-review boundaries
```

---

# 4. TRUST MODEL — FOUR DIFFERENT THINGS MUST NEVER COLLAPSE

CrimeKit must visually and semantically distinguish:

```text
OBSERVED
DERIVED
PREDICTED
HUMAN-REVIEWED
```

Use a richer model:

```text
1. SOURCE OBSERVATION
2. MACHINE DERIVATION
3. GRAPH STRUCTURAL ANALYSIS
4. MODEL PREDICTION
5. HYPOTHESIS
6. HUMAN REVIEW
7. HUMAN DECISION
```

Never display these as if they are equivalent.

Examples:

```text
A face detection
≠
A person identity
```

```text
A track
≠
a confirmed person
```

```text
A graph path
≠
causation
```

```text
High centrality
≠
guilt
```

```text
Model prediction
≠
forensic fact
```

```text
AI explanation
≠
source evidence
```

---

# 5. PROVENANCE MASTER CHAIN

The authoritative semantic chain for machine-generated forensic findings should follow the existing CrimeKit lineage model.

For general graph data:

```text
CASE
 ↓
INVESTIGATION
 ↓
SEARCH / ANALYSIS JOB
 ↓
PROCESSING RUN
 ↓
SOURCE EVIDENCE
 ↓
SOURCE ARTIFACT
 ↓
FORENSIC OBSERVATION
 ↓
ENTITY / RELATIONSHIP DERIVATION
 ↓
GRAPH PROJECTION
 ↓
ANALYTIC RESULT
 ↓
INVESTIGATOR REVIEW
```

For Face Trace, preserve the more granular lineage:

```text
Case
 ↓
Investigation
 ↓
Search Job
 ↓
Processing Run
 ↓
Source Evidence
 ↓
Source Artifact
 ↓
Source Frame
 ↓
Face Detection
 ↓
Quality Evaluation
 ↓
Face Track
 ↓
Face Embedding
 ↓
Candidate Observation
 ↓
Face Sighting
 ↓
Investigator Review
```

Every child must retain enough identifiers to walk backward to the authorized source and forward to the result/review.

---

# 6. PROVENANCE AS A FIRST-CLASS DOMAIN OBJECT

Do not treat provenance as a comment field or debug log.

Treat it as a durable domain capability.

A provenance record should conceptually support:

```text
provenance_id
case_id
investigation_id
source_record_id
source_type
source_version
parent_record_id
child_record_id
processing_run_id
algorithm_id
algorithm_version
model_id
model_version
policy_id
policy_version
created_at
observed_at
confidence
status
actor_type
actor_id
review_state
```

Only store fields that actually exist in the architecture.

Never invent values merely to make the UI complete.

---

# 7. PROVENANCE DAG, NOT JUST A LINE

Do not assume all forensic lineage is linear.

The system must support branching and merging.

Example:

```text
                      Evidence E1
                           |
                    +------+------+
                    |             |
                  OCR run      TSK run
                    |             |
                Artifact A     Artifact B
                    |             |
                    +------+------+
                           |
                    Entity Candidate
                           |
                     Human Review
```

Another example:

```text
Video
 ├── Frame 100
 │    └── Detection D1
 │         └── Track T1
 │              └── Candidate C1
 ├── Frame 101
 │    └── Detection D2
 │         └── Track T1
 └── Frame 102
      └── Detection D3
           └── Track T1
```

The UI must never erase these branch relationships merely to simplify visualization.

---

# 8. PROVENANCE EDGE SEMANTICS

Every important provenance edge should answer:

```text
WHO / WHAT created the child?
FROM WHAT source?
WHEN?
USING WHICH processing context?
UNDER WHICH POLICY?
WITH WHAT CONFIDENCE?
WHAT REVIEW STATE?
```

Examples:

```text
DERIVED_FROM
EXTRACTED_FROM
OBSERVED_IN
GENERATED_BY
PRODUCED_BY
SUPPORTED_BY
REVIEWED_BY
SUPERSEDES
CORRECTS
INVALIDATES
RETRACTS
```

Do not use vague generic links when a precise provenance relationship exists.

---

# 9. SOURCE IMMUTABILITY

Original evidence must never be overwritten by processing.

Do not:

- overwrite original video
- replace original image
- destructively crop evidence
- modify source hashes
- replace source metadata silently
- annotate original binary in place
- re-encode original in place

Use derived artifacts instead.

The forensic principle is:

```text
SOURCE
  ↓
DERIVED ARTIFACT
```

never:

```text
SOURCE
  ↓
DESTRUCTIVE MODIFICATION
```

---

# 10. SOURCE HASH / INTEGRITY BOUNDARY

If CrimeKit already records cryptographic hashes, reference those authoritative integrity records.

Do not create a competing hash authority.

Always distinguish:

```text
source evidence hash
```

from:

```text
derived artifact hash
```

and from:

```text
UI export hash
```

A hash must not be presented as proof of semantic correctness; it verifies the bytes represented by the hash.

---

# 11. REPROCESSING RULE

Every materially different processing run must be identifiable.

When any of the following changes materially:

- model
- detector
- tracker
- preprocessing
- matching policy
- threshold
- processing configuration
- graph projection rule

create or reference a new processing context according to CrimeKit workflow rules.

Never make historical output appear to have been generated by today's model.

---

# 12. SOURCE REVISION RULE

If evidence metadata changes after processing:

```text
past processing context
```

must remain interpretable.

Do not silently mutate historical processing records to match current metadata.

---

# 13. CORRECTION WITHOUT HISTORY DESTRUCTION

When a derived relationship is found to be wrong:

Do not silently delete history if policy requires historical traceability.

Prefer explicit semantic transitions such as:

```text
ACTIVE
 →
DISPUTED
 →
REJECTED
 →
RETIRED
```

or the project's established equivalent.

The correction must preserve:

```text
previous state
new state
actor
reason
timestamp
source of correction
```

---

# 14. SUPERSESSION VS DELETION

A new result may supersede an old result without erasing it.

Example:

```text
Candidate C1
   |
   | SUPERSEDED_BY
   v
Candidate C2
```

The UI should distinguish:

```text
historically produced
```

from:

```text
currently preferred
```

---

# 15. PROVENANCE COMPLETENESS SCORE

Create a **Provenance Completeness** indicator only from actual lineage fields.

Example conceptual categories:

```text
COMPLETE
PARTIAL
DEGRADED
MISSING
```

Do not fabricate percentages.

The score should indicate lineage completeness, not certainty of guilt or identity.

---

# 16. PROVENANCE QUALITY GATE

Before surfacing a machine-derived finding as a normal investigative object, verify required lineage.

For a Face Trace candidate, verify as applicable:

```text
case
investigation
source evidence
artifact
frame
processing run
detection/track
model context
matching policy
candidate identity
```

If required lineage is absent:

```text
mark degraded
show why
prevent misleading presentation
```

Do not silently fill provenance gaps.

---

# 17. PROVENANCE "WHY" EXPERIENCE

Every important graph relationship must support:

> **Why does CrimeKit believe this relationship exists?**

The UI must allow the investigator to inspect:

```text
Relationship
 ↓
Observation(s)
 ↓
Artifact(s)
 ↓
Processing Run
 ↓
Model / Algorithm
 ↓
Policy / Threshold
 ↓
Evidence
 ↓
Original Source
```

Do not stop at:

```text
Confidence: 0.91
```

Confidence without lineage is insufficient.

---

# 18. FORENSIC GRAPH RELATIONSHIP TRUST STATES

Use explicit semantics for graph edges.

Recommended controlled set:

```text
OBSERVED
DERIVED
CANDIDATE
REVIEWED
CONFIRMED_BY_POLICY
DISPUTED
REJECTED
HYPOTHESIS
RETIRED
SUPERSEDED
```

Each state must have documented meaning.

Never use color alone to communicate the state.

---

# 19. FORENSIC GRAPH NODE TRUST STATES

Nodes may also have state:

```text
OBSERVED_ENTITY
DERIVED_ENTITY
CANDIDATE_ENTITY
RESOLVED_ENTITY
MERGED_ENTITY
DISPUTED_ENTITY
RETIRED_ENTITY
HYPOTHESIS_ENTITY
```

Identity resolution must remain separate from visual display convenience.

---

# 20. SECURITY OBJECTIVE

The security objective is:

```text
AUTHORIZED ACCESS
+
MINIMUM NECESSARY EXPOSURE
+
STRONG CASE / TENANT ISOLATION
+
PROTECTED SENSITIVE DATA
+
AUDITABILITY
+
TRACEABLE FORENSIC LINEAGE
```

Security must exist at every layer:

```text
Browser
 ↓
API
 ↓
Service
 ↓
Worker
 ↓
Storage
 ↓
Database
 ↓
Vector Search
 ↓
Neo4j
 ↓
Realtime
 ↓
Export
 ↓
AI
 ↓
Logs
```

---

# 21. ZERO-TRUST REQUEST PATH

Every sensitive request follows conceptually:

```text
Request
 ↓
Authentication
 ↓
Authorization
 ↓
Tenant Scope
 ↓
Case Scope
 ↓
Resource Scope
 ↓
Action Scope
 ↓
Policy Check
 ↓
Data Access
```

Do not trust:

- frontend-selected case IDs
- client-side hidden fields
- route parameters alone
- graph node IDs
- evidence IDs
- websocket channel names
- signed UI state

Server-side authorization is mandatory.

---

# 22. CASE ISOLATION AS A SECURITY INVARIANT

Case isolation must be enforced in:

- API
- database queries
- graph queries
- vector retrieval
- caches
- jobs
- workers
- realtime subscriptions
- AI retrieval
- GDS graphs
- exports
- saved graph views
- search history
- audit visibility

Frontend filtering is never the security boundary.

---

# 23. TENANT ISOLATION

For multi-tenant deployments:

```text
Tenant
 ↓
Case
 ↓
Investigation
 ↓
Evidence
 ↓
Derived Intelligence
```

Tenant boundaries must be enforced server-side.

Do not trust browser-provided tenant IDs.

---

# 24. RESOURCE AUTHORIZATION

Use resource-level checks, not only role checks.

Conceptually:

```text
User
 ↓
Role
 ↓
Case membership
 ↓
Investigation permission
 ↓
Evidence permission
 ↓
Graph permission
 ↓
Requested resource
```

A user who can access the Face Trace feature does not automatically gain access to every case.

---

# 25. ACTION-LEVEL AUTHORIZATION

Distinguish at least conceptually between:

```text
VIEW_CASE
VIEW_EVIDENCE
VIEW_GRAPH
SEARCH_GRAPH
RUN_ANALYTICS
RUN_CROSS_CASE_SEARCH
VIEW_RESTRICTED_PROVENANCE
VIEW_SOURCE_MEDIA
PERFORM_REVIEW
EXPORT
ADMINISTER_MODELS
ALTER_POLICIES
WRITE_GRAPH
```

Use actual CrimeKit permissions where already defined.

Do not invent a parallel permission system if one exists.

---

# 26. OBJECT-LEVEL AUTHORIZATION

Every sensitive object access should be checked against its authoritative ownership relationship.

Do not authorize based only on:

```text
resource ID exists
```

Correct:

```text
user
 ↓
case membership
 ↓
resource ownership
 ↓
requested action
```

This prevents IDOR-style access patterns.

---

# 27. PROVENANCE ACCESS CONTROL

Provenance itself is sensitive.

A user authorized to view one candidate must not automatically gain visibility into unrelated restricted evidence through provenance traversal.

The provenance graph is subject to the same authorization policy as the main graph.

---

# 28. PROVENANCE SIDE-CHANNEL PROTECTION

Do not reveal hidden objects through:

- error text
- result counts
- timing differences where practical
- graph traversal failures
- search suggestions
- autocomplete
- “related entities” suggestions
- AI answers
- graph statistics
- realtime event counts

Examples of forbidden leakage:

```text
"Evidence E-991 exists but you don't have permission."
```

Prefer an authorization-safe response consistent with the platform policy.

---

# 29. HIDDEN-RESOURCE NON-DISCLOSURE

The system must not expose through unauthorized access:

- hidden evidence existence
- hidden case names
- hidden persons
- hidden devices
- hidden relationships
- hidden investigation notes
- hidden graph communities
- hidden GDS results
- hidden biometric vectors

Do not let AI become a side channel.

---

# 30. AI SECURITY BOUNDARY

AI receives no broader authorization than the authenticated investigator.

Correct:

```text
User
 ↓
Case authorization
 ↓
Typed graph tools
 ↓
Graph API
 ↓
Authorized structured context
 ↓
LLM
```

Incorrect:

```text
User
 ↓
LLM
 ↓
unrestricted Cypher
 ↓
all cases
```

---

# 31. AI GROUNDING RULE

Every important factual AI statement should be traceable to structured sources such as:

```text
node_id
relationship_id
evidence_id
artifact_id
timeline_event_id
provenance_id
analysis_id
```

When supporting evidence is absent:

```text
state that evidence is unavailable
```

Do not invent provenance.

---

# 32. AI CLAIM TAXONOMY

AI responses must distinguish:

```text
SOURCE FACT
DERIVED FACT
ANALYTICAL RESULT
MODEL PREDICTION
INVESTIGATOR HYPOTHESIS
AI INTERPRETATION
```

Use explicit labels in the UI.

---

# 33. AI NO-FACT-WRITE RULE

AI must not silently:

- create forensic facts
- modify evidence
- rewrite chain of custody
- change a relationship to CONFIRMED
- change a review decision
- delete provenance
- promote hypothesis to fact

AI may propose actions through controlled workflows.

Sensitive mutations follow:

```text
AI proposal
 ↓
Human review
 ↓
Authorized application command
 ↓
Audited state transition
```

---

# 34. GRAPH API SECURITY BOUNDARY

The frontend must never connect directly to Neo4j.

Required production path:

```text
Browser
 ↓
CrimeKit FastAPI
 ↓
Authorization / policy
 ↓
Graph Service
 ↓
Neo4j
```

The browser must never receive:

- Neo4j credentials
- database URI secrets
- privileged Cypher permissions
- unrestricted graph connection details

---

# 35. NEO4J MCP + ANTIGRAVITY BOUNDARY

Developer / engineering path:

```text
Google Antigravity
        ↓
Official Neo4j MCP
        ↓
DEV / STAGING
```

Production investigator path:

```text
CrimeKit UI
        ↓
FastAPI Graph API
        ↓
Authorization
        ↓
Neo4j
```

Never implement:

```text
Browser → MCP → Neo4j
```

MCP is a developer/agent tooling plane, not a browser data plane.

---

# 36. MCP READ-FIRST POLICY

Use MCP to:

- inspect schema
- validate relationship types
- inspect available GDS procedures
- inspect data shape in development
- test controlled queries
- validate projection behavior

Prefer read-only behavior for production-adjacent environments.

If write tooling is enabled:

```text
synthetic / dev data
+
explicit approval
+
least privilege
+
full audit
```

Never permit an engineering agent to casually mutate production forensic graph data.

---

# 37. ANTIGRAVITY IMPLEMENTATION LOOP

Required developer loop:

```text
Inspect repository
 ↓
Inspect current graph implementation
 ↓
Inspect current provenance model
 ↓
Inspect current security model
 ↓
Inspect Neo4j schema through MCP
 ↓
Inspect GDS availability through MCP
 ↓
Design minimal change
 ↓
Implement
 ↓
Run tests
 ↓
Run security tests
 ↓
Run provenance tests
 ↓
Verify graph output
 ↓
Verify 3D behavior
 ↓
Verify evidence navigation
 ↓
Verify case isolation
 ↓
Document result
```

---

# 38. NEO4J SCHEMA SECURITY

The application must not assume that Neo4j schema equals authorization.

Neo4j relationships and labels are data structures.

Application authorization still determines what an investigator may see.

Use:

```text
case_id
investigation scope
resource ownership
authorization policy
```

as first-class controls.

---

# 39. CASE-SCOPED CYPHER

Graph queries must include explicit case scope or another authoritative access boundary.

Avoid unrestricted patterns in application endpoints.

Example conceptually:

```cypher
MATCH (n)-[r]->(m)
WHERE n.case_id = $case_id
  AND m.case_id = $case_id
RETURN n, r, m
LIMIT $limit
```

Actual query must follow the real schema and relationships.

Never expose arbitrary user-generated Cypher in normal investigator workflows.

---

# 40. CROSS-CASE SEARCH GATE

Cross-case graph search is a high-sensitivity operation.

Require:

```text
explicit permission
scope selection
reason / justification where policy requires
audit event
result minimization
```

Do not make cross-case retrieval the default.

---

# 41. CROSS-CASE RESULT CONTEXT

If cross-case search is allowed, clearly distinguish:

```text
SOURCE CASE
TARGET CASE
RELATIONSHIP OF DISCOVERY
AUTHORIZATION SCOPE
```

Do not imply that a cross-case similarity or relationship is a universal identity fact.

---

# 42. GRAPH PROJECTION SECURITY

Projection workers may write to Neo4j, but only through controlled server-side processes.

Projection inputs must be:

- authoritative domain records
- validated events
- authorized processing results
- deterministic identifiers

Never allow:

```text
frontend → Neo4j write
```

---

# 43. PROJECTION IDEMPOTENCY

Duplicate events must not create duplicate forensic facts.

For replay:

```text
event A
+
event A
```

must remain semantically idempotent according to domain rules.

Use deterministic identifiers and safe merge/update semantics where appropriate.

---

# 44. PROJECTION REVISION

Every graph projection should be explainable by a projection version or equivalent configuration.

Distinguish:

```text
API version
Ontology version
Projection version
Graph revision
Model version
Policy version
```

Never collapse these into one `version` field if that destroys meaning.

---

# 45. GRAPH REVISION AS SECURITY + PROVENANCE OBJECT

Every significant graph state should be identifiable by a graph revision/checkpoint/state marker where architecture supports it.

This enables:

- historical replay
- analytic reproducibility
- graph diff
- incident review
- debugging
- evidence impact analysis
- post-event audits

The 3D UI may show:

```text
GRAPH REVISION
CURRENT
```

but must not imply a revision exists if backend history is unavailable.

---

# 46. SECURITY OF GRAPH REVISIONS

A user must not retrieve historical graph snapshots outside their authorization scope.

For every replay/checkpoint request:

```text
authorize case
authorize requested time
authorize requested data
authorize requested operation
```

---

# 47. FORENSIC TIME SEMANTICS

Preserve different clocks:

```text
SOURCE TIME
INGESTION TIME
PROCESSING TIME
PROJECTION TIME
REVIEW TIME
```

Do not replace unknown source time with ingestion time without labeling it.

This distinction is critical for a realtime graph.

---

# 48. TEMPORAL UNCERTAINTY

Support when applicable:

```text
EXACT
APPROXIMATE
INTERVAL
UNKNOWN
```

The 3D graph should visualize temporal uncertainty distinctly from confidence.

---

# 49. TEMPORAL PROVENANCE

A graph relationship should be able to answer:

```text
When was this observed?
When was it derived?
When was it projected?
When was it reviewed?
```

These are different events.

---

# 50. REALTIME EVENT SECURITY

Realtime graph delivery must follow:

```text
Authenticate
 ↓
Authorize case
 ↓
Authorize subscription
 ↓
Subscribe
 ↓
Filter events
 ↓
Deliver
```

Never broadcast all graph events and rely on frontend filtering.

---

# 51. WEBSOCKET / SSE CASE ISOLATION

Per-case realtime subscriptions must be authorization-aware.

A client subscribed to CASE-A must never receive CASE-B events.

This must remain true after:

- reconnect
- tab switching
- case switching
- token refresh
- network recovery
- worker restart
- event replay

---

# 52. REALTIME SEQUENCE CONTROL

Use event sequence / ordering metadata where appropriate.

On reconnect:

```text
detect sequence gap
 ↓
request bounded replay or snapshot
 ↓
reconcile
 ↓
resume live stream
```

Do not silently render an incomplete graph as if it were current.

---

# 53. REALTIME STALENESS SEMANTICS

The UI should distinguish:

```text
LIVE
RECOVERING
STALE
DEGRADED
OFFLINE
```

Do not call the graph “live” if projection freshness is not actually measured.

---

# 54. REALTIME EVENT MINIMIZATION

Events should reference domain identifiers rather than unnecessarily reproducing sensitive data.

Example concept:

```json
{
  "event_type": "GRAPH_EDGE_CREATED",
  "case_id": "CASE-001",
  "sequence": 104,
  "relationship_id": "REL-001",
  "occurred_at": "...",
  "projection_version": "..."
}
```

Fetch protected detail through authorized APIs.

---

# 55. GRAPH DELTA AUTHORIZATION

A delta must be authorized just like a snapshot.

Do not assume:

```text
user had access to previous snapshot
```

means:

```text
user has access to every future delta
```

Authorization is evaluated against current policy.

---

# 56. 3D PROVENANCE UX — SOURCE THREAD

Create an interaction called conceptually:

**SOURCE THREAD**

Selecting a node or edge reveals a visual trail:

```text
Node / Edge
   ↓
Observation
   ↓
Artifact
   ↓
Processing
   ↓
Evidence
   ↓
Source
```

The trail is clickable at every stage.

---

# 57. 3D PROVENANCE UX — FORENSIC X-RAY

Create a view conceptually called:

**FORENSIC X-RAY**

Purpose:

Temporarily peel away the semantic visualization to reveal the engineering lineage beneath one graph object.

Layers:

```text
Visible Graph Object
        ↓
Relationship Record
        ↓
Observation
        ↓
Artifact
        ↓
Processing Run
        ↓
Model / Algorithm
        ↓
Evidence
```

This is not decorative.

It is a forensic audit interaction.

---

# 58. 3D PROVENANCE UX — EVIDENCE GRAVITY

Use an **Evidence Gravity** visualization only when it has a defensible metric.

Possible input dimensions:

- number of supporting evidence objects
- source diversity
- observation count
- review state
- provenance completeness

Do not map gravity directly to:

```text
guilt
criminality
intent
truth
```

The legend must explain what gravity means.

---

# 59. 3D PROVENANCE UX — EVIDENCE SHADOW

A graph object can have a subtle “evidence shadow” representing supporting source count or traceability only when those values are real.

Conceptually:

```text
Entity
 └── evidence shadow
      ├── source count
      ├── artifact count
      └── provenance completeness
```

Never manufacture a shadow for missing data.

---

# 60. 3D PROVENANCE UX — ORIGIN BEACON

When a relationship is selected, display a small origin indicator connecting it to its source record.

Example:

```text
Person ──USES── Device
             |
             | origin
             v
        Evidence E-44
```

This is a compact alternative to opening a large detail card.

---

# 61. 3D PROVENANCE UX — LINEAGE THREAD

Render a provenance thread as a temporary secondary path.

Example:

```text
             GRAPH
               |
        ───────┴───────
        |              |
   Relationship      Evidence
        |              |
    Artifact          Source
```

The main graph remains visually stable.

The provenance thread is contextual and dismissible.

---

# 62. 3D PROVENANCE UX — TRUST HALO

A trust halo may encode one or more actual provenance states:

```text
COMPLETE
PARTIAL
DEGRADED
MISSING
```

It must never imply legal guilt, innocence, or identity certainty.

---

# 63. 3D PROVENANCE UX — UNCERTAINTY VOLUME

When uncertainty is meaningful, represent it separately from confidence.

Possible representation:

```text
solid core = known representation
soft volume = uncertainty range
```

The volume must be derived from a documented uncertainty source.

Never use uncertainty animation merely for visual effect.

---

# 64. 3D PROVENANCE UX — RELATIONSHIP MICROSCOPE

Selecting an edge should offer:

**Relationship Microscope**

The graph temporarily focuses on:

```text
source node
relationship
observation(s)
target node
supporting evidence
processing context
```

This turns an edge from a line into an inspectable forensic object.

---

# 65. 3D PROVENANCE UX — EVIDENCE IMPACT

Selecting Evidence E-100 should optionally reveal:

```text
Evidence
 ↓
Artifacts derived
 ↓
Entities affected
 ↓
Relationships affected
 ↓
Timeline events affected
 ↓
GDS results potentially invalidated
 ↓
AI context potentially changed
```

This is one of CrimeKit's central differentiated interaction opportunities.

---

# 66. 3D PROVENANCE UX — PROCESSING IMPACT

Selecting a Processing Run should reveal:

```text
Run
 ↓
Artifacts
 ↓
Entities discovered
 ↓
Relationships proposed
 ↓
Timeline events generated
 ↓
Graph projection changes
 ↓
Analytics changed / stale
```

All counts must come from actual records.

---

# 67. 3D PROVENANCE UX — GRAPH DIFF

Support comparison between two authorized graph states:

```text
GRAPH A
vs
GRAPH B
```

Show:

```text
ADDED
REMOVED
CHANGED
REVIEWED
DISPUTED
```

Every diff must be traceable to source event / processing context where available.

---

# 68. 3D PROVENANCE UX — CONTRADICTION FRACTURE

When two authorized records contradict each other, do not hide the conflict.

Represent it as a contradiction object or relation.

Example:

```text
Event A
   X
Event B
```

Inspector must show:

```text
Conflict type
Source A
Source B
Time relationship
Evidence
Status
Review state
```

Do not label the conflict as “fraud” or “lying” unless the actual domain supports such a statement.

---

# 69. 3D PROVENANCE UX — KNOWLEDGE GAP LAYER

Missing information can be visualized as a distinct state:

```text
KNOWN
UNKNOWN
UNSUPPORTED
CONFLICTING
```

Knowledge gaps must never be rendered as negative evidence unless such semantics are explicitly established by the domain.

---

# 70. 3D PROVENANCE UX — REVIEW BOUNDARY

Create a visible transition boundary:

```text
MACHINE DERIVED
        |
        | HUMAN REVIEW REQUIRED
        v
HUMAN-REVIEWED
```

This is one of the most important ethical UI elements.

The graph must make it obvious which objects have not been reviewed.

---

# 71. 3D PROVENANCE UX — HYPOTHESIS QUARANTINE

Investigator-created hypotheses must live in a separate semantic layer.

```text
CANONICAL GRAPH
        ||
        || safe boundary
        ↓
HYPOTHESIS GRAPH
```

Hypotheses may be visualized attractively in 3D, but must never mutate canonical facts without an explicit authorized action.

---

# 72. 3D PROVENANCE UX — PREDICTION QUARANTINE

Machine predictions must have a dedicated state:

```text
PREDICTED
```

Do not let predicted relationships inherit the same visual treatment as observed relationships.

---

# 73. BIOMETRIC DATA PROTECTION

Treat as sensitive when present:

- reference face images
- source video
- face crops
- embeddings
- candidate matches
- sightings
- similarity values
- biometric metadata

Apply the strongest available access control and data minimization.

---

# 74. RAW EMBEDDING NON-DISCLOSURE

Do not expose raw embeddings in normal UI responses.

Do not send them through:

- generic graph DTOs
- websocket payloads
- AI context
- browser logs
- analytics tooltips
- export by default

If an internal service requires an embedding, use the controlled service path and minimize exposure.

---

# 75. FACE RESULT SEMANTICS

For Face Trace:

```text
Detection
≠
Track
≠
Embedding
≠
Candidate
≠
Sighting
≠
Human-confirmed identity
```

The UI must preserve these distinctions.

---

# 76. FACE TRACK SEMANTICS

A track means:

> observations associated by the tracking algorithm.

It does not mean:

> legally or conclusively the same person.

Do not allow visual shorthand to collapse this distinction.

---

# 77. CANDIDATE SEMANTICS

A candidate is an analytical observation requiring interpretation / policy / human review according to the workflow.

Do not display:

```text
MATCHED PERSON
```

when the actual state is:

```text
CANDIDATE
```

unless the domain explicitly supports that promoted state.

---

# 78. SIMILARITY SCORE SEMANTICS

A similarity value is a model output.

It must not be displayed as:

```text
identity certainty
```

Use labels such as:

```text
Similarity
Candidate Score
Model Distance
```

with model / policy context when relevant.

---

# 79. MODEL PROVENANCE

Every machine-generated result should retain, where applicable:

```text
provider
model ID
model version
preprocessing version
runtime / execution provider
threshold policy
processing run
```

Historical outputs must remain attributable to the model context that generated them.

---

# 80. CONFIGURATION PROVENANCE

Important processing configuration is part of provenance.

Examples:

```text
sampling profile
quality threshold
similarity threshold
tracker settings
detector settings
GDS parameters
graph query template
```

Do not silently overwrite historical configuration.

---

# 81. POLICY PROVENANCE

Record policy context for result classification where applicable:

```text
policy_id
policy_version
effective_at
scope
```

A changed policy should not silently rewrite historical labels.

---

# 82. GDS ANALYTIC PROVENANCE

Every important GDS result should carry:

```text
algorithm
algorithm version
parameters
graph projection identifier
graph revision / checkpoint if available
case scope
timestamp
result status
```

The UI must answer:

> **What graph and algorithm produced this analytical pattern?**

---

# 83. GDS SECURITY

Analytics are authorized data access.

Do not allow an analyst with basic graph read permission to automatically run every high-cost analytic.

Gate:

- algorithm access
- graph scope
- case scope
- cross-case scope
- execution cost
- exportability

---

# 84. GDS SAFETY LANGUAGE

Never communicate:

```text
high centrality = offender
community = criminal group
similarity = identity
anomaly = crime
bridge = mastermind
PageRank = guilt
```

Prefer:

```text
high network centrality
structural community
similarity signal
anomalous topology
bridge-like structural position
ranking metric
```

Then explain the metric.

---

# 85. ALGORITHM DISAGREEMENT

Introduce an optional **Algorithm Disagreement Lens**.

Purpose:

Show where different graph analyses do not agree.

Example:

```text
PageRank            HIGH
Betweenness         LOW
Degree              HIGH
Community relevance MEDIUM
```

The visualization should emphasize:

```text
disagreement
```

rather than pretending one metric is absolute truth.

---

# 86. GRAPH STABILITY LENS

A high-value enterprise innovation is the ability to show whether a graph insight is stable across graph revisions.

Example:

```text
Revision A → Centrality HIGH
Revision B → Centrality HIGH
Revision C → Centrality MEDIUM
```

The inspector can state:

```text
Pattern persistence: stable / changing / newly emerged
```

Only when historical result data actually exists.

---

# 87. ANALYTIC INVALIDATION

When the graph changes, determine whether existing analytics are stale.

Examples:

```text
new relationship added
 ↓
community detection result potentially stale
```

```text
new node added
 ↓
centrality result potentially stale
```

Mark stale analytics explicitly.

Never display a stale analysis as current.

---

# 88. SECURITY OF ANALYTIC CACHE

Cached GDS results must retain case / tenant authorization context.

Cache keys should include sufficient scope dimensions to prevent cross-case reuse.

Do not use:

```text
analysis_id only
```

as a security boundary.

---

# 89. SEARCH SECURITY

Search suggestions, autocomplete, and fuzzy retrieval must be authorized.

Never let autocomplete reveal hidden entities.

Never let fuzzy search escape the user's case scope.

---

# 90. VECTOR SEARCH SECURITY

Vector retrieval must enforce:

```text
tenant
case
investigation
purpose
retention
```

where applicable.

A vector index must not become an anonymous biometric database.

---

# 91. VECTOR + GRAPH LEAKAGE CONTROL

If vector search finds an entity, graph expansion must re-check authorization before returning neighbors.

Do not assume:

```text
vector result authorized
```

means:

```text
all connected graph objects authorized
```

---

# 92. OBJECT STORAGE SECURITY

Original evidence must remain private.

Use existing approved storage abstractions.

Prefer:

- private containers/buckets
- authenticated access
- scoped access
- time-limited access where supported
- server-side authorization

Do not put permanent public URLs into graph nodes.

---

# 93. SIGNED MEDIA URL SAFETY

If signed URLs are used:

- short-lived where practical
- scoped to one resource
- authorized before issue
- never expose storage credentials
- never place unrestricted bucket access in the frontend

The URL is not the authorization policy; it is a delivery mechanism after policy validation.

---

# 94. FILE UPLOAD SECURITY

Treat evidence and reference media as untrusted input.

Validate:

```text
size
content type
magic bytes where appropriate
decoder compatibility
malformed media behavior
path safety
```

Do not trust filename extension alone.

---

# 95. MEDIA PARSING ISOLATION

Where architecture permits, isolate untrusted media decoding and extraction from the primary API process.

A malformed file must not compromise the investigator session or control plane.

---

# 96. PATH TRAVERSAL PROTECTION

Never construct filesystem paths directly from user-controlled values.

Use stable internal storage IDs and the existing artifact abstraction.

---

# 97. SECRET MANAGEMENT

Never store secrets in:

- source code
- frontend bundles
- Git history
- logs
- graph properties
- audit records
- error messages

Use existing approved secret/configuration management.

---

# 98. CREDENTIAL SEPARATION

Separate credentials by purpose:

```text
application
worker
Neo4j
object storage
database
AI provider
MCP / development
```

Least privilege for each.

Do not reuse an administrator secret across all services.

---

# 99. SERVICE-TO-SERVICE AUTHENTICATION

If CrimeKit has separate:

```text
API
worker
projection worker
AI service
video worker
```

use the existing internal service authentication mechanism.

Do not treat network location as sufficient trust.

---

# 100. ENCRYPTION

Use platform-approved encryption at rest and in transit.

Protect, as applicable:

- PostgreSQL
- vector data
- Neo4j
- object storage
- backups
- derived media
- logs containing protected metadata

Do not invent custom cryptography.

---

# 101. KEY MANAGEMENT

Use an approved secret / key-management mechanism.

Never hard-code keys.

Document rotation requirements and operational ownership.

---

# 102. LOGGING SECURITY

Logs should support investigation without becoming a second sensitive-data store.

Never log by default:

- raw embeddings
- passwords
- private RTSP credentials
- API keys
- full restricted media
- unrestricted evidence content

Use IDs and correlation references.

---

# 103. ERROR MESSAGE SECURITY

User-visible errors must not reveal:

- stack traces
- database URLs
- credentials
- internal network addresses
- filesystem paths
- hidden case existence
- restricted graph relationships

---

# 104. SECURITY TELEMETRY

Record operational security signals such as:

```text
request_id
user_id
case_id where appropriate
action
target class
result
reason code
latency
```

Do not place raw sensitive payloads into generic telemetry.

---

# 105. AUDIT VS PROVENANCE

Keep two concepts separate.

### AUDIT

> Who did what?

### PROVENANCE

> Where did this result come from?

They complement each other.

Do not replace one with the other.

---

# 106. AUDIT EVENTS

Sensitive actions should be auditable according to CrimeKit policy.

Examples:

```text
open case
view evidence
view restricted source
start search
cancel search
run GDS analysis
run cross-case search
review candidate
change review state
create hypothesis
export graph
export evidence
change policy
manage model
```

---

# 107. AUDIT RECORD CONTENT

Capture conceptually:

```text
actor
actor type
action
target
case
investigation
timestamp
request ID
outcome
reason / justification where required
```

Distinguish:

```text
human-initiated action
```

from:

```text
automated service action
```

---

# 108. AUDIT IMMUTABILITY

Follow the existing CrimeKit audit architecture.

Application users must not be able to freely edit historical audit records.

If corrections are required, preserve the history of the correction.

---

# 109. REVIEW AUDIT

Every review transition should preserve:

```text
reviewer
previous state
new state
time
notes / reason where supported
```

Do not silently overwrite old decisions.

---

# 110. SOURCE ACCESS AUDIT

Where policy requires, viewing protected source media should produce an audit trail.

This may include:

```text
source requested
actor
case
purpose
time
outcome
```

---

# 111. EXPORT SECURITY

Exports are high-sensitivity operations.

Require as applicable:

```text
permission
case scope
explicit filters
field minimization
audit
async processing for large exports
watermark / labeling when required
```

---

# 112. EXPORT PROVENANCE

Every export should be attributable to:

```text
export_id
case
scope
filters
graph revision / projection revision where relevant
created_at
actor
```

The export should not masquerade as original source evidence.

---

# 113. DERIVED MEDIA LABELING

Annotated frames, crops, rendered graph images, and exports are derived outputs.

Clearly label them as derived where the UI/reporting context requires it.

Never allow a screenshot of the graph to masquerade as raw evidence.

---

# 114. SOURCE FRAME VS ANNOTATED FRAME

If a graph interaction opens a frame:

```text
SOURCE FRAME
```

must remain distinguishable from:

```text
ANNOTATED / DERIVED DISPLAY FRAME
```

The overlay should never overwrite the source.

---

# 115. CHAIN-OF-CUSTODY UX

Expose chain-of-custody information without overloading the main graph.

Possible compact inspector:

```text
CHAIN OF CUSTODY
Status: Verified
Acquired: ...
Custodian events: 7
Integrity: Verified
```

Every value must come from authoritative data.

---

# 116. CHAIN-OF-CUSTODY NEVER FABRICATED

Do not show:

```text
Verified
```

merely because an evidence row exists.

Verification status must come from the actual domain state.

---

# 117. RETENTION ARCHITECTURE

Retention must consider the complete lineage.

Example:

```text
Source Evidence
 ↓
Artifact
 ↓
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
Sighting
 ↓
Graph Projection
 ↓
Vector Index
 ↓
Derived Media
 ↓
Audit / Review
```

Deleting one object must not accidentally leave orphaned sensitive intelligence.

---

# 118. BIOMETRIC DELETION COMPLETENESS

When a biometric artifact expires or is deleted, consider all searchable representations:

```text
authoritative record
 ↓
vector index
 ↓
caches
 ↓
Neo4j projection if applicable
 ↓
derived crops
 ↓
exports
```

The implementation must follow actual policy and dependencies.

---

# 119. LEGAL HOLD

If CrimeKit supports legal hold / evidence preservation:

```text
LEGAL HOLD
```

must override automatic deletion where required by policy.

Related derived artifacts must be evaluated for preservation.

Do not automatically purge protected data.

---

# 120. DATA MINIMIZATION

Only collect and expose data necessary for:

- investigation
- evidence processing
- provenance
- review
- reporting
- authorized analytics

Avoid adding unrelated sensitive attributes merely because models can infer them.

---

# 121. PROHIBITED INFERENCE CLASS

Do not create unrelated profiling such as:

- race inference
- religion inference
- political affiliation
- sexual orientation
- inferred criminal propensity
- unrelated personality profiling

unless a future explicitly governed and lawful subsystem defines a different purpose. The baseline CrimeKit forensic graph must not silently introduce these attributes.

---

# 122. PURPOSE LIMITATION

Sensitive evidence intelligence must remain bound to the authorized investigative purpose.

Do not turn CrimeKit into a general-purpose people profiling system.

---

# 123. DATA CLASSIFICATION

Conceptually classify:

### CRITICAL / HIGHLY SENSITIVE

- original evidence
- source media
- biometric vectors
- face crops
- restricted cross-case results

### INVESTIGATIVE

- candidates
- sightings
- timeline events
- graph relationships
- GDS results
- confidence/similarity

### OPERATIONAL

- job IDs
- queue depth
- worker health
- latency

Classification must be aligned with actual organizational policy.

---

# 124. GRAPH DATA CLASSIFICATION

Not all graph nodes are equally sensitive.

A `Case` node may be sensitive.

An `Evidence` node is more sensitive.

A relationship revealing a hidden association may itself be sensitive.

The authorization system must protect **relationships**, not only nodes.

---

# 125. RELATIONSHIP CONFIDENTIALITY

Do not assume:

```text
Node A authorized
+
Node B authorized
=
Relationship A-B authorized
```

A relationship can reveal sensitive intelligence that neither node alone reveals.

Authorize relationship visibility explicitly through the same policy model.

---

# 126. GRAPH PATH CONFIDENTIALITY

A path can reveal sensitive information through multiple individually permissible edges.

Example:

```text
A → Device → Account → Person
```

The complete path may reveal information the investigator is not authorized to infer.

Apply access policy to the returned path and all intermediate objects.

---

# 127. GRAPH PATH MINIMIZATION

Return only as much path context as required for the requested operation.

Do not automatically expand:

```text
all paths
all neighbors
all provenance
```

---

# 128. PROVENANCE QUERY DEPTH

Bound provenance traversal.

Default behavior:

```text
summary first
 ↓
detail on demand
```

Never return millions of lineage records because one inspector panel was opened.

---

# 129. GRAPH QUERY LIMITS

All graph retrieval endpoints should have safe limits.

Use:

```text
max nodes
max edges
max hops
query timeout
pagination
request cancellation
```

Actual values must be tuned from measured workload.

---

# 130. GRAPH DENIAL-OF-SERVICE PROTECTION

Protect against expensive graph queries such as:

- unconstrained traversal
- huge variable-length paths
- full graph sorting
- repeated shortest-path calls
- massive GDS jobs
- unbounded provenance expansion

Use request budgets and server-side controls.

---

# 131. GDS RESOURCE GOVERNANCE

Heavy analytics should be asynchronous.

Conceptual flow:

```text
request
 ↓
authorization
 ↓
job creation
 ↓
worker
 ↓
Neo4j / GDS
 ↓
result persistence
 ↓
API
```

Capture:

```text
algorithm
parameters
scope
revision
time
status
```

---

# 132. GRAPH ANALYTIC BUDGET

Consider a budget for:

```text
CPU
memory
query time
result size
concurrency
```

This is an operational control, not a forensic conclusion.

---

# 133. GDS GRAPH PROJECTION ISOLATION

Prefer controlled named graph projections or equivalent GDS scope constructs.

Never allow users to create arbitrary production-wide analytical graphs without authorization.

---

# 134. GRAPH PROJECTION LIFECYCLE

Define lifecycle states for analytical projections as needed:

```text
CREATED
READY
RUNNING
STALE
EXPIRED
DELETED
```

Do not leave temporary graph projections forever without policy.

---

# 135. ANALYTIC RESULT LIFECYCLE

Results may be:

```text
CURRENT
STALE
SUPERSEDED
REVOKED
INVALIDATED
ARCHIVED
```

This is different from relationship trust state.

---

# 136. SECURITY OF STALE RESULTS

A stale result can still reveal sensitive data.

Apply authorization to stale results exactly as to current results.

---

# 137. INCIDENT RESPONSE — FORENSIC DATA BREACH

If sensitive data is exposed:

```text
Detect
 ↓
Contain
 ↓
Preserve logs
 ↓
Assess scope
 ↓
Identify affected cases
 ↓
Invalidate leaked access paths
 ↓
Review provenance / audit
 ↓
Recover
 ↓
Report according to policy
```

Do not delete forensic logs to hide the incident.

---

# 138. SECURITY INCIDENT CORRELATION

Use distributed identifiers:

```text
request_id
job_id
processing_run_id
investigation_id
case_id
projection_id
analysis_id
```

This helps connect application, operational, and forensic views.

---

# 139. OPERATIONAL TRACE VS FORENSIC PROVENANCE

Keep separate:

### Operational trace

```text
Which service handled this request?
```

### Forensic provenance

```text
Which evidence produced this result?
```

A service trace cannot replace evidence lineage.

---

# 140. DISTRIBUTED TRACE PROPAGATION

Carry correlation identifiers through:

```text
API
 ↓
Workflow
 ↓
Worker
 ↓
Inference
 ↓
Persistence
 ↓
Projection
 ↓
Realtime
```

Never put sensitive payloads into trace attributes merely for convenience.

---

# 141. SECURITY OBSERVABILITY

Monitor:

- authentication failures
- authorization failures
- unusual cross-case access
- unusual export activity
- repeated expensive graph queries
- MCP write attempts
- projection errors
- provenance gaps
- realtime authorization failures
- graph reconciliation mismatches

Use actual observability capabilities available in CrimeKit.

---

# 142. PROVENANCE MONITORING

Track operational health of provenance itself:

```text
provenance completeness
orphan count
unresolved parent count
missing source count
projection trace failures
stale provenance
```

Do not silently accept broken lineage.

---

# 143. ORPHAN DETECTION

Detect records such as:

```text
candidate without processing run
relationship without source
artifact without evidence
sighting without source frame
vector without embedding context
GDS result without graph revision
```

Classify each according to actual domain rules.

---

# 144. RECONCILIATION

Provide a controlled reconciliation process between:

```text
PostgreSQL
 ↔
Neo4j
```

and where applicable:

```text
PostgreSQL
 ↔
pgvector
```

Reconciliation must be auditable.

Never silently rewrite forensic history merely to make counts match.

---

# 145. GRAPH RECONCILIATION SECURITY

Only authorized services/operators should run reconciliation.

Reconciliation must not bypass normal case or tenant boundaries.

---

# 146. PROVENANCE REPAIR POLICY

If lineage is damaged:

Do not guess missing provenance.

Use controlled states such as:

```text
PROVENANCE_DEGRADED
PROVENANCE_MISSING
PROVENANCE_REPAIR_REQUIRED
```

Repair using verified source records or replayable events.

---

# 147. REPLAY SAFETY

Replay must not create indistinguishable new facts.

Represent replay mode explicitly in operational context.

Example:

```text
original event
vs
replayed event
```

Historical output must remain attributable to original processing context.

---

# 148. EVENT REPLAY AUTHORIZATION

Replaying forensic events is a sensitive operation.

Require:

```text
authorization
scope
purpose
audit
```

---

# 149. GRAPH TIME MACHINE SECURITY

Historical graph replay can reveal historical secrets.

Authorize every time slice.

Do not assume current access grants access to all historical graph states.

---

# 150. INVESTIGATION REPLAY

Support an investigator replay mode only from real historical events / snapshots.

Never fake historical graph motion.

Use:

```text
real event
→
real state transition
→
real graph change
```

---

# 151. 3D GRAPH SECURITY UX — TRUSTED CAMERA

Camera controls should not obscure security state.

When a user rotates / zooms / isolates a graph:

```text
authorization remains unchanged
```

The visual camera is not a security boundary.

---

# 152. 3D GRAPH SECURITY UX — ISOLATION BADGE

Show case scope visibly:

```text
CASE CK-001
```

and optionally:

```text
TENANT T-01
```

where policy allows.

The badge is a user-awareness control, not the actual authorization control.

---

# 153. 3D GRAPH SECURITY UX — RESTRICTED NODE

When authorized semantics allow a node to be partially visible but details are restricted, use an explicit restricted state instead of leaking fields.

Example:

```text
RESTRICTED OBJECT
Details unavailable under current permissions
```

Do not reveal forbidden properties.

---

# 154. 3D GRAPH SECURITY UX — REDACTION

Redact fields at the API boundary.

Never fetch forbidden values to the browser and merely hide them with CSS.

---

# 155. 3D GRAPH SECURITY UX — SECURE INSPECTOR

Inspector fields must be capability-aware.

Potentially sensitive fields:

```text
source URI
raw media path
embedding reference
cross-case metadata
restricted notes
```

Only render when authorized.

---

# 156. 3D GRAPH SECURITY UX — PRIVACY MODE

Provide an optional privacy-preserving display mode where policy requires.

Example:

```text
full name
→
masked display
```

```text
exact location
→
coarse location
```

Do not implement privacy transformations that alter canonical data.

This is a display/read model policy only.

---

# 157. 3D GRAPH SECURITY UX — EXPORT WARNING

Before exporting sensitive graph context, clearly show:

```text
CASE
SCOPE
OBJECT COUNT
SENSITIVE DATA TYPES
DESTINATION
AUDIT STATUS
```

Then follow policy-controlled confirmation.

---

# 158. GRAPH SCREEN SECURITY STATE

The top-level graph workspace should make visible, as appropriate:

```text
Case scope
Connection status
Graph freshness
Permission context
Current lens
Current graph revision
```

Do not clutter the screen with security banners that do not help decisions.

---

# 159. GRAPH TRUST LEGEND

The legend should include not only node types but also trust semantics:

```text
Observed
Derived
Candidate
Prediction
Hypothesis
Reviewed
Disputed
```

The legend is part of forensic safety.

---

# 160. COLOR IS NOT THE ONLY SIGNAL

Do not communicate critical forensic states through color alone.

Combine:

```text
shape
outline
icon
label
pattern
motion
text
```

for accessibility.

---

# 161. REDACTED GRAPH SEMANTICS

When information is hidden, avoid making absence itself a misleading inference.

Do not render:

```text
missing = none
```

when the actual meaning is:

```text
restricted
```

Distinguish:

```text
UNKNOWN
NOT FOUND
RESTRICTED
NOT APPLICABLE
NOT YET PROCESSED
```

---

# 162. UNKNOWN VS ABSENT

This distinction is mandatory.

```text
NO RELATIONSHIP FOUND
```

is different from:

```text
RELATIONSHIP UNKNOWN
```

which is different from:

```text
RELATIONSHIP RESTRICTED
```

The UI must not collapse these states.

---

# 163. PROVENANCE GAP UX

When provenance is incomplete, show the gap explicitly.

Example:

```text
PROVENANCE DEGRADED

Relationship source available.
Processing context unavailable.
```

Do not substitute a guessed model/version.

---

# 164. GRAPH AI EXPLANATION SECURITY

When AI explains a graph relationship, include only authorized context.

The AI must not mention:

```text
hidden evidence
hidden nodes
restricted case relationships
```

even when the model has indirect access to embeddings or broad retrieval tools.

---

# 165. AI PROMPT-INJECTION DEFENSE

Evidence can contain adversarial text.

Treat evidence content as untrusted data.

Never let text inside evidence redefine system instructions or authorization policy.

Conceptually:

```text
System policy
    >
Application policy
    >
User request
    >
Evidence content
```

Evidence content must never gain control-plane authority.

---

# 166. DOCUMENT / MESSAGE INJECTION

If OCR, email, chat, or documents are fed to an AI system:

Clearly label their content as evidence-derived data.

Do not allow embedded phrases such as:

```text
Ignore previous instructions
```

to become trusted instructions.

---

# 167. TOOL AUTHORIZATION FOR AI

AI tools should be typed and narrow.

Prefer:

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

over arbitrary unrestricted database access.

---

# 168. AI TOOL RESULT MINIMIZATION

Return compact structured context:

```text
IDs
relationship types
time
provenance refs
minimal properties
```

Then retrieve protected detail only when required and authorized.

---

# 169. AI RESPONSE LABELS

Use visual badges such as:

```text
SOURCE
DERIVED
ANALYTICS
MODEL
HYPOTHESIS
AI INTERPRETATION
```

This helps prevent model prose from being mistaken for evidence.

---

# 170. HUMAN REVIEW GATE

Sensitive promotions should require human review when defined by policy.

Example:

```text
Candidate
 ↓
Review Queue
 ↓
Human Decision
 ↓
Audited Transition
```

Do not let the 3D graph itself become the decision engine.

---

# 171. REVIEW DECISION SEMANTICS

Use explicit review states such as:

```text
PENDING
SUPPORTED
REJECTED
DISPUTED
INCONCLUSIVE
```

Use actual CrimeKit terminology where it exists.

---

# 172. REVIEW DOES NOT ALTER SOURCE

Human review may change the classification of a derived result.

It must not overwrite the original source evidence or erase the fact that the machine generated the observation.

---

# 173. HUMAN REVIEW PROVENANCE

A reviewed result should retain:

```text
reviewer
review time
previous state
new state
reason / note if policy supports
```

---

# 174. REVIEW CONFLICTS

If reviewers disagree:

Do not overwrite one decision with the other.

Represent:

```text
decision A
vs
decision B
```

and route according to adjudication policy.

---

# 175. HYPOTHESIS SYSTEM SECURITY

Investigator hypotheses must have strong semantic and authorization boundaries.

They must not:

- silently enter canonical evidence
- alter authoritative relationships
- affect automated decisions without explicit promotion
- leak across cases

---

# 176. HYPOTHESIS AUDIT

Record:

```text
creator
created_at
source observations
assumptions
status
last edited
promotion / rejection action
```

---

# 177. PROVENANCE-SAFE ANNOTATIONS

Annotations, bookmarks and investigator notes should be stored in the existing authoritative application domain when possible.

Do not write arbitrary investigator notes directly into canonical Neo4j forensic entities unless the architecture explicitly requires it.

---

# 178. GRAPH VIEW SECURITY

A saved graph view is itself sensitive.

It may encode:

- target entities
- hidden relationships
- investigative hypotheses
- search terms
- filters
- path selections

Protect saved views using the same case authorization model.

---

# 179. SEARCH HISTORY SECURITY

Search history can reveal investigative intent.

Protect it accordingly.

Do not expose one investigator's search history to another unless explicitly permitted.

---

# 180. COMMAND PALETTE SECURITY

The 3D workspace command bar must enforce authorization per action.

Examples:

```text
Export Graph
Run Centrality
Open Restricted Evidence
Cross-Case Search
```

A command visible in UI does not imply permission.

---

# 181. ACCESSIBLE SECURITY STATES

Security and provenance states must be accessible to keyboard and assistive technology users.

Do not encode:

```text
restricted
stale
candidate
reviewed
```

through visual effects only.

---

# 182. REDUCED-MOTION TRUST UX

If reduced motion is enabled:

Critical trust states must remain understandable without animation.

Do not make provenance discovery dependent on motion.

---

# 183. 2D FALLBACK MUST RETAIN FORENSIC SEMANTICS

If WebGL / 3D is unavailable:

```text
3D graph
 ↓
2D graph
 ↓
TABLE / LIST
```

must preserve:

- provenance
- authorization
- evidence links
- trust state
- timeline
- audit visibility

3D is an interaction layer, not the only source of meaning.

---

# 184. PERFORMANCE SECURITY

Performance controls are also security controls.

Prevent attackers or accidental users from consuming excessive resources through:

- huge graph expansions
- repeated expensive GDS requests
- huge provenance traversals
- realtime subscription abuse
- giant exports
- AI tool loops

Use:

```text
rate limits
concurrency limits
query budgets
timeouts
pagination
cancellation
```

---

# 185. REALTIME BACKPRESSURE

A realtime security and reliability requirement:

Never allow unbounded event queues.

Use explicit:

```text
capacity
sampling / coalescing policy
backpressure
drop policy
recovery behavior
```

Durable forensic events must not be silently lost merely because the UI cannot render every update.

---

# 186. LIVE GRAPH EVENT COALESCING

Where multiple non-critical events occur rapidly, the UI may coalesce visual presentation.

Example:

```text
10 node-updates
```

may become:

```text
Graph cluster updated
```

but the authoritative event history remains durable.

Never use UI coalescing to delete forensic records.

---

# 187. SECURITY OF UI DELTAS

A coalesced visual delta must not aggregate information across unauthorized scopes.

Coalescing keys must include the authorization / case scope.

---

# 188. GRAPH FRESHNESS DISCLOSURE

Show where useful:

```text
Last graph update
Projection lag
Realtime state
```

Use measured values only.

---

# 189. NO FAKE FRESHNESS

Never fabricate:

```text
LIVE
Updated 2 sec ago
Real-time
```

unless the system can substantiate it.

---

# 190. PROVENANCE FRESHNESS

Distinguish:

```text
source captured
processing completed
projection updated
UI received
```

These timestamps may differ.

---

# 191. CASE SWITCH SECURITY

When the user changes case:

1. cancel old requests
2. close old realtime subscriptions
3. clear unauthorized graph state
4. clear case-sensitive caches
5. establish new authorization
6. request new snapshot
7. verify scope

Never display CASE-B data during a transient CASE-A → CASE-B transition.

---

# 192. BROWSER STATE CLEANUP

Clear or replace case-sensitive state from:

- memory stores
- local cache
- IndexedDB if used
- session state if appropriate
- websocket subscriptions
- URL state

Follow the actual security architecture.

---

# 193. CACHE SECURITY

Every cache entry holding sensitive data must include enough authorization scope dimensions.

At minimum, evaluate whether the key needs:

```text
tenant
case
investigation
user / role class
resource ID
version
```

Do not over-cache sensitive graph objects globally.

---

# 194. CDN / EDGE CACHE RULE

Do not publicly cache restricted evidence or sensitive graph responses.

Use server-side protected delivery as required.

---

# 195. BROWSER DEVTOOLS CONSIDERATION

Assume authorized investigators can inspect their own browser memory.

Therefore:

Do not send data to the browser unless the user is allowed to see it.

Hiding an element in React is not data protection.

---

# 196. DOM REDACTION RULE

Forbidden data must never be present in the rendered DOM merely hidden with CSS.

Authorization happens before data delivery.

---

# 197. URL SECURITY

Do not place sensitive data directly in URLs when avoidable.

Prefer stable opaque references and server-side authorization.

Never put:

- secrets
- raw embeddings
- sensitive evidence content

into query strings.

---

# 198. DEEP-LINK SECURITY

A deep link such as:

```text
/cases/CASE-001/graph/entity/P001
```

is a navigation request, not an authorization grant.

Re-check authorization on every load.

---

# 199. GRAPH SNAPSHOT EXPORT SECURITY

If the graph canvas can export PNG/SVG/JSON:

- validate permission
- apply field minimization
- include case metadata only as allowed
- audit export
- mark derived output

Do not expose hidden graph fields through JSON export when they are hidden in the UI.

---

# 200. JSON EXPORT SECURITY

Graph exports should not blindly serialize backend objects.

Use an explicit export DTO.

Never export raw internal models.

---

# 201. REPORT SECURITY

Reports should distinguish:

```text
SOURCE EVIDENCE
DERIVED ARTIFACT
GRAPH RELATIONSHIP
ANALYTICS
MODEL OUTPUT
HUMAN REVIEW
```

Do not generate a final report from a canvas screenshot.

---

# 202. REPORT PROVENANCE REFERENCES

Where appropriate, report claims should include stable references back to:

```text
evidence ID
artifact ID
relationship ID
analysis ID
review ID
```

---

# 203. FORENSIC REPORT INTEGRITY

Where CrimeKit uses report hashing/signing, preserve the existing architecture.

A generated report must not overwrite source evidence.

---

# 204. EVIDENCE-TO-GRAPH SECURITY

When the investigator navigates:

```text
Evidence → Graph
```

the graph query must inherit evidence authorization.

---

# 205. GRAPH-TO-EVIDENCE SECURITY

When the investigator navigates:

```text
Graph → Evidence
```

the evidence access check must be repeated.

A graph relationship is not an access token.

---

# 206. TIMELINE-TO-GRAPH SECURITY

A timeline event can reveal connected entities.

Authorize graph expansion from timeline events the same way as direct graph queries.

---

# 207. GRAPH-TO-TIMELINE SECURITY

The graph should only expose authorized timeline events.

Do not infer that a visible graph node means every event linked to it is visible.

---

# 208. EVIDENCE-IMPACT SECURITY

The Evidence Impact Lens may expose many derived objects.

Apply authorization to every child object.

Do not expose hidden downstream results merely because their parent evidence is visible.

---

# 209. PROCESSING-IMPACT SECURITY

A Processing Run can reveal which analytical mechanisms were used.

Protect processing metadata where it is sensitive.

Do not expose private model credentials, internal endpoints, or secrets.

---

# 210. MODEL METADATA SAFETY

The UI may show:

```text
model name
version
provider
```

when policy allows.

It must not expose:

```text
private credentials
internal filesystem path
secret endpoint
license secret
```

---

# 211. MATCHING POLICY SAFETY

If threshold/policy metadata is visible:

show only the necessary information.

Do not expose sensitive internals merely because a “Why?” panel exists.

---

# 212. SOURCE URI SAFETY

Do not display raw internal storage URIs or private network paths when a stable artifact reference is sufficient.

---

# 213. RTSP SECURITY

For live CCTV sources:

- keep credentials server-side
- never send credentials to React
- never log credentials
- never place passwords in events
- store only approved source identifiers in UI

Use existing CrimeKit source registry / storage abstractions.

---

# 214. LIVE SOURCE AUTHORIZATION

A live source should be represented with a controlled identity such as:

```text
CAM-001
```

The identifier should not reveal:

- password
- secret URI
- network credentials
- private infrastructure details

---

# 215. LIVE SOURCE HEALTH SECURITY

Health metrics may reveal infrastructure details.

Return only what the investigator needs.

Avoid exposing raw internal addresses unnecessarily.

---

# 216. FACE DATA DISPLAY MINIMIZATION

The graph should prefer:

```text
Face Sighting
Candidate
Track
```

over automatically rendering face crops everywhere.

Open sensitive media on demand after authorization.

---

# 217. CROP RETENTION

If face crops are retained:

- link to source frame
- link to processing run
- protect access
- apply retention policy
- do not keep anonymous crop files

---

# 218. SOURCE FRAME PROVENANCE

Every derived source-frame snapshot should identify, where applicable:

```text
derived frame ID
source artifact
frame number
timestamp
bbox
processing run
```

---

# 219. ANNOTATED FRAME PROVENANCE

When drawing bounding boxes or graph overlays:

```text
source frame
+
overlay
→
derived display artifact
```

Never replace the source.

---

# 220. FACE RESULT ACCESS POLICY

Sensitive Face Trace actions should be separately permissioned where policy requires:

```text
search
view candidate
view source
review
cross-case search
export
model administration
```

Use existing CrimeKit permission conventions if available.

---

# 221. PRIVACY-AWARE GRAPH LENS

Create a **Privacy Lens** that can reduce exposure without modifying canonical data.

Possible transformations:

```text
full name → masked name
exact coordinates → area
full account identifier → partial mask
full device identifier → partial mask
```

Only implement transformations allowed by policy.

---

# 222. PRIVACY LENS MUST NOT ALTER FORENSIC TRUTH

The privacy lens is:

```text
read-model transformation
```

not:

```text
source-data mutation
```

---

# 223. ROLE-AWARE 3D DETAIL

The same graph object may be rendered at different detail levels based on authorization.

Example:

```text
Analyst → graph structure
Forensic examiner → more provenance
Administrator → operational metadata
```

Do not weaken the canonical domain model to support UI variants.

---

# 224. SECURITY POLICY ENGINE

Centralize security decisions enough to avoid policy fragmentation.

Conceptually:

```text
AuthorizationContext
 ├── tenant
 ├── case
 ├── investigation
 ├── roles
 ├── permissions
 ├── resource
 └── action
```

Then:

```text
authorize(context)
```

Do not copy authorization logic into twenty UI components.

---

# 225. AUTHORIZATION DECISION CACHING

Where authorization decisions are cached:

- scope them correctly
- respect policy changes
- define expiry
- invalidate on role/case membership change

Never create a stale permission cache that silently preserves access after revocation.

---

# 226. PERMISSION REVOCATION

When access is revoked:

```text
future API requests denied
websocket subscription invalidated
cached sensitive responses reconsidered
saved views access rechecked
```

The exact implementation follows CrimeKit infrastructure.

---

# 227. LIVE REVOCATION

A user whose case access is revoked while connected should not continue receiving realtime events.

Use:

```text
policy update
 ↓
subscription invalidation
 ↓
connection refresh / disconnect
```

according to implementation.

---

# 228. SESSION EXPIRY

When authentication expires:

- stop sensitive requests
- close protected subscriptions
- clear or lock sensitive UI state as policy requires
- require re-authentication

---

# 229. TOKEN LEAST PRIVILEGE

Browser tokens must provide only necessary authority.

Do not ship service-account privileges to clients.

---

# 230. CSRF / REQUEST ORIGIN CONTROLS

Use the existing web security model appropriate to CrimeKit's authentication style.

Do not weaken CSRF / origin controls simply to make WebSocket or graph requests easier.

---

# 231. CORS SECURITY

Allow only intended origins.

Do not use permissive wildcard CORS for protected graph APIs without a justified architecture.

---

# 232. API RATE LIMITING

Apply rate limits to:

- graph search
- path search
- provenance requests
- GDS jobs
- exports
- AI graph queries
- login / auth endpoints

Tune based on actual workload.

---

# 233. QUERY COST FEEDBACK

Before expensive graph analysis, the UI can show:

```text
Estimated scope
Estimated nodes
Potentially expensive operation
```

Only use real measurements / planner metadata when available.

Never show fake costs.

---

# 234. SECURITY TEST MATRIX

Test at minimum:

```text
Authorized user
Unauthorized user
Wrong case
Wrong tenant
Revoked role
Expired session
Restricted relationship
Hidden evidence
Cross-case access
Realtime unauthorized event
Export authorization
Graph traversal escalation
AI tool escalation
MCP write attempt
```

---

# 235. PROVENANCE TEST MATRIX

Test:

```text
source exists
source hash preserved
artifact linked
processing run linked
model linked
policy linked
relationship linked
review linked
reprocessing differentiated
correction preserved
replay safe
```

---

# 236. NEGATIVE PROVENANCE TESTS

Explicitly test that the system rejects or marks degraded:

```text
candidate without source
embedding without model context
edge without source record
sighting without case
GDS result without graph scope
AI claim without source reference
```

---

# 237. GRAPH SECURITY TESTS

Test that malicious or malformed queries cannot:

- escape case scope
- traverse hidden relationships
- read another tenant
- trigger unbounded expansion
- execute arbitrary writes
- bypass API authorization

---

# 238. NEO4J QUERY INJECTION

Do not construct Cypher using raw string interpolation from untrusted input.

Use parameterized queries and whitelisted identifiers / relationship types.

Dynamic structural elements must be validated against controlled schema metadata.

---

# 239. GDS PARAMETER VALIDATION

Validate:

- algorithm name
- graph projection
- case scope
- hop limits
- node limits
- iteration counts
- concurrency where exposed

Use allowlists for production algorithms.

---

# 240. PROVENANCE QUERY INJECTION

Provenance IDs and artifact IDs must be treated as untrusted request parameters.

Never use them to construct arbitrary query fragments.

---

# 241. EXPORT INJECTION

If exporting CSV or spreadsheet-like output, protect against formula injection where applicable.

Sanitize exported display fields according to file type and policy.

---

# 242. LOG INJECTION

Normalize / structure user-provided values before writing security logs.

Do not allow attacker-controlled newline sequences to forge log records.

---

# 243. SSR / HYDRATION SECURITY

3D graph rendering is browser-specific.

Keep browser-only APIs inside appropriate client boundaries.

Never expose secrets merely because a component is client-rendered.

---

# 244. 3D RENDERER SECURITY

The 3D renderer should consume normalized DTOs.

Do not pass raw database driver objects into Three.js components.

This creates a cleaner security and architecture boundary.

---

# 245. 3D OBJECT DATA MINIMIZATION

A graph node's render model should contain only what the canvas needs:

```text
id
label
semantic type
position
visual state
authorized display metadata
```

Sensitive forensic metadata remains in the inspector API.

---

# 246. PICK / RAYCAST SECURITY

Selecting an object in 3D reveals only authorized details.

The renderer cannot bypass API permission by knowing an internal ID.

---

# 247. HIDDEN NODE SECURITY

Do not render hidden nodes as invisible geometry merely to maintain layout if their existence itself is sensitive.

Prefer a layout that does not require forbidden objects to be sent to the browser.

---

# 248. OCCLUDED-DATA SECURITY

Do not send sensitive graph data merely because it is outside the camera view.

Camera visibility and data authorization are separate concerns.

---

# 249. LOD SECURITY

Level-of-detail should reduce rendering cost, not bypass authorization.

Every LOD representation must be based only on authorized data.

---

# 250. CLUSTER SECURITY

Cluster summaries must not leak hidden counts.

Example:

Do not return:

```text
47 hidden entities
```

when the user is not authorized to know that 47 exist.

---

# 251. COMMUNITY SECURITY

GDS community detection may expose group structure.

Apply graph authorization before generating and before displaying community membership.

---

# 252. CENTRALITY SECURITY

Centrality can reveal sensitive importance patterns.

Treat analytical results as protected case intelligence.

---

# 253. PATH SECURITY

A shortest path can expose restricted intermediate nodes.

Every node and relationship in the path must pass authorization before return.

---

# 254. GRAPH SEARCH RESULT ORDER SECURITY

Search ranking must not reveal hidden objects through gaps in the ranking.

Return only authorized records.

Do not include placeholders that reveal restricted content.

---

# 255. AUTOCOMPLETE SIDE-CHANNEL

Never return autocomplete suggestions from:

```text
all cases
```

when the current user is scoped to one case.

---

# 256. ERROR TIMING / COUNT SIDE-CHANNEL

Where practical, avoid distinguishable behavior that tells a user:

```text
object exists but is forbidden
```

rather than:

```text
object does not exist
```

Follow the real application's security response policy.

---

# 257. PROVENANCE THREAD AUTHORIZATION RECHECK

When an investigator clicks a provenance hop:

```text
Edge
 ↓
Artifact
 ↓
Evidence
```

re-check authorization at each resource boundary.

---

# 258. PROVENANCE THREAD NO-AUTO-ESCALATION

Opening a permitted relationship must not automatically reveal every downstream object.

Progressively load only what the investigator is authorized to inspect.

---

# 259. EVIDENCE IMPACT NO-AUTO-ESCALATION

Evidence Impact should use bounded, authorized expansion.

Do not treat “impact” as permission to reveal all affected records.

---

# 260. INCIDENT FORENSICS OF THE FORENSICS PLATFORM

CrimeKit itself must be investigable.

Security incidents should leave enough operational evidence to answer:

```text
Who accessed what?
Which API?
Which graph query?
Which evidence?
Which export?
When?
What policy was in effect?
```

This is **meta-provenance**.

---

# 261. META-PROVENANCE

Introduce a concept:

**Meta-Provenance** = lineage of the platform's own operation around a forensic result.

Example:

```text
Forensic Result
 ↓
Processing Run
 ↓
Worker
 ↓
Service Version
 ↓
Deployment
 ↓
Operational Trace
```

This supplements, but does not replace, forensic provenance.

---

# 262. TRUST STACK

The UI may expose a layered trust stack:

```text
SOURCE INTEGRITY
      ↓
PROVENANCE COMPLETENESS
      ↓
PROCESSING ATTRIBUTION
      ↓
ANALYTIC VALIDITY
      ↓
REVIEW STATE
      ↓
CURRENT ACCESS AUTHORIZATION
```

Never collapse this into a single magical trust number.

---

# 263. FORENSIC TRUST SCORE — OPTIONAL AND RESTRICTED

Do not create a single “truth score” by default.

If a future workflow needs an aggregate health indicator, call it something explicit such as:

```text
Forensic Record Health
```

and decompose it into independently inspectable dimensions.

---

# 264. TRUST VECTOR

A differentiated concept is a **Trust Vector** instead of one score:

```text
Integrity
Provenance
Attribution
Temporal Quality
Source Diversity
Review State
Authorization State
Analytic Freshness
```

The user can inspect each dimension separately.

---

# 265. TRUST VECTOR VISUALIZATION

In 3D inspector UI, show a compact multidimensional trust visualization only when values are actual data.

Example:

```text
Integrity       VERIFIED
Provenance      COMPLETE
Attribution     COMPLETE
Temporal        APPROXIMATE
Sources         4
Review          PENDING
Freshness       CURRENT
```

---

# 266. SOURCE DIVERSITY

A finding supported by multiple independent source classes can be presented differently from one supported by a single source.

But do not equate source count with truth.

Example categories:

```text
1 source
2 source classes
3+ source classes
```

Use actual data.

---

# 267. SOURCE CORRELATION RISK

Multiple records may derive from the same original source.

Do not count duplicated derivatives as independent evidence merely because there are many records.

The provenance graph should help identify common origin.

---

# 268. DERIVATIVE COUNT VS SOURCE COUNT

Distinguish:

```text
10 derived artifacts
```

from:

```text
3 independent source evidences
```

This is a powerful forensic visualization safeguard.

---

# 269. PROVENANCE COLLAPSE DETECTOR

If many graph objects ultimately trace to one source, the UI may offer:

**Source Origin Collapse**

to show that apparent diversity may share one origin.

This must be calculated from real provenance.

---

# 270. COMMON-ORIGIN WARNING

Do not let the graph visually imply independent corroboration when several edges derive from the same artifact.

Provide an optional warning:

```text
COMMON SOURCE ORIGIN
```

---

# 271. RELATIONSHIP SUPPORT MATRIX

For selected relationship:

```text
Source Type | Record | Time | Support State
------------|--------|------|--------------
Video       | E-01   | ...  | Supports
Message     | E-07   | ...  | Supports
Artifact    | A-08   | ...  | Derived
```

This turns visual graph trust into inspectable evidence structure.

---

# 272. PROVENANCE EVIDENCE STACK

The inspector can show:

```text
TOP
────────────────────
Current graph relationship
────────────────────
Machine derivation
────────────────────
Observation
────────────────────
Processing context
────────────────────
Source artifact
────────────────────
Original evidence
────────────────────
BOTTOM
```

Each layer is clickable.

---

# 273. EVIDENCE FIRST PRINCIPLE

When a graph finding cannot be understood without a source, make the source one interaction away.

Never bury provenance ten screens deep.

---

# 274. ONE-CLICK SOURCE NAVIGATION

For permitted users:

```text
Graph Edge
 → View Source
```

or:

```text
Entity
 → Evidence
```

must preserve context:

```text
which edge
which artifact
which frame / event
```

---

# 275. INVESTIGATION STORY SECURITY

A saved investigation story is sensitive.

Protect it with:

```text
case scope
creator / collaborators
sharing permissions
audit
```

---

# 276. COLLABORATION SECURITY

If multiple investigators collaborate:

Distinguish:

```text
private note
team note
case-visible annotation
```

Use actual collaboration policy.

---

# 277. GRAPH BOOKMARK SECURITY

Bookmarks should inherit case visibility rules.

Do not create globally searchable bookmarks from sensitive case data.

---

# 278. GRAPH PRESENTATION MODE

A presentation/demo mode must still respect security.

Do not create a “demo mode” that disables authorization in production.

---

# 279. SYNTHETIC DATA BOUNDARY

Development / demo / testing data should be clearly labeled synthetic.

Never let synthetic graph objects be confused with real evidence.

---

# 280. NO FAKE PROVENANCE IN DEMO

Even synthetic demo data should have internally coherent provenance.

Do not use:

```text
random evidence IDs
fake hashes
fake review claims
```

without clear synthetic labeling.

---

# 281. TEST FIXTURE PROVENANCE

Approved test fixtures should contain:

```text
case
source evidence
artifact
processing run
expected relationships
expected provenance
```

---

# 282. GOLDEN PROVENANCE TEST

Create a golden lineage fixture:

```text
Evidence E1
 ↓
Artifact A1
 ↓
Observation O1
 ↓
Entity N1
 ↓
Relationship R1
 ↓
Review V1
```

Then verify:

```text
R1 → O1 → A1 → E1
```

and:

```text
R1 → V1
```

---

# 283. GOLDEN SECURITY TEST

Create a protected fixture where:

```text
User A → CASE-001 → allowed
User A → CASE-002 → denied
User B → CASE-002 → allowed
```

Verify graph, evidence, timeline, provenance, AI and realtime all obey the same policy.

---

# 284. CROSS-LAYER CONSISTENCY TEST

A denial at the API must correspond to denial in:

```text
graph
provenance
vector search
timeline
AI
WebSocket
export
```

Do not create a “secure API” with an insecure side channel.

---

# 285. SECURITY REGRESSION TESTS

Every future feature touching graph data should run:

```text
case isolation
authorization
provenance
audit
realtime scope
AI grounding
export controls
```

before release.

---

# 286. PROVENANCE REGRESSION TESTS

Every future change to processing / matching / GDS should verify:

```text
source link preserved
version context preserved
historical run preserved
correction history preserved
```

---

# 287. SCHEMA DRIFT DETECTION

Detect divergence between:

```text
application ontology
Neo4j labels
Neo4j relationships
indexes / constraints
GDS expectations
API DTOs
```

Schema drift should be visible before it becomes a forensic correctness bug.

---

# 288. AUTHORIZATION POLICY DRIFT

Ensure policy definitions remain aligned across:

```text
API
WebSocket
Graph Service
AI tools
GDS jobs
Export
```

Do not maintain separate slightly different case-scope rules.

---

# 289. POLICY VERSIONING

Where meaningful policy changes occur, retain version metadata.

Examples:

```text
authorization policy version
retention policy version
matching policy version
graph projection policy version
```

---

# 290. INCIDENT REPLAY WITH AUTHORIZATION

Security incident analysts may need to replay historical events.

Replay should use historical context for forensic analysis but current authorization to determine who is allowed to inspect the replay.

Do not bypass access controls merely because the replay is historical.

---

# 291. FORENSIC DISCOVERY OF SECURITY EVENTS

Security events affecting a case may themselves become case-related metadata.

Keep operational security data appropriately separated from source evidence.

---

# 292. META-SECURITY GRAPH

A future extension may represent security events as a separate protected graph layer:

```text
User
 ↓
Access Event
 ↓
Case
 ↓
Resource
 ↓
Outcome
```

This should remain security telemetry, not ordinary investigative graph data.

---

# 293. SECURITY GRAPH NEVER LEAKS INTO NORMAL CASE VIEW

Do not accidentally visualize internal access logs in the investigator graph.

Keep the domain boundaries explicit.

---

# 294. ROLE OF NEO4J IN SECURITY

Neo4j provides relationship storage / intelligence.

CrimeKit application services enforce business authorization.

Do not outsource the entire security model to graph labels.

---

# 295. ROLE OF POSTGRESQL IN SECURITY

PostgreSQL remains authoritative for application-domain permissions / relationships where existing architecture places them.

Do not silently move access-control truth into Neo4j just because the graph makes traversal convenient.

---

# 296. ROLE OF REDIS IN SECURITY

Redis may carry transient jobs / events.

Do not treat Redis cache presence as evidence of authorization.

Subscriptions must be authorization-aware.

---

# 297. ROLE OF OBJECT STORAGE IN SECURITY

Object storage holds sensitive bytes.

Its access path must be mediated by CrimeKit policy.

---

# 298. ROLE OF THE 3D RENDERER

The renderer is a presentation layer.

It must never decide:

```text
authorized or not
fact or not
identity or not
guilty or not
```

---

# 299. ROLE OF AI

AI helps:

```text
retrieve
summarize
explain
suggest investigation paths
```

AI does not become:

```text
source of truth
authorization authority
chain-of-custody authority
final decision authority
```

---

# 300. CORE DIFFERENTIATED PRODUCT IDEA — FORENSIC TRUST FABRIC

Make CrimeKit's 3D Knowledge Graph visually operate like a **Trust Fabric**.

Every important object can be “opened” into five dimensions:

```text
WHAT
WHERE FROM
HOW GENERATED
WHO MAY SEE IT
WHO REVIEWED IT
```

The graph is not only a relationship map.

It is a map of relationship **trust context**.

---

# 301. DIFFERENTIATED IDEA — PROVENANCE CONSTELLATION

A selected graph object becomes the center of a temporary constellation:

```text
                  MODEL
                    |
                    |
Evidence ── Artifact ── Relationship ── Entity
                    |
                 Processing
                    |
                  Review
```

Each spoke is clickable.

The constellation disappears when focus changes.

---

# 302. DIFFERENTIATED IDEA — FORENSIC CAUSALITY GUARDRAIL

When an investigator selects a graph path, the inspector should include a machine-generated semantic warning:

```text
GRAPH CONNECTIVITY ≠ CAUSATION
```

The exact warning should adapt to the selected relationship type.

Examples:

```text
SIMILARITY ≠ IDENTITY
CENTRALITY ≠ GUILT
CO-OCCURRENCE ≠ CAUSATION
LOCATION ASSOCIATION ≠ PRESENCE
```

This protects against cognitive overreach.

---

# 303. DIFFERENTIATED IDEA — SOURCE DIVERSITY RING

For an entity or relationship, optionally show a ring segmented by source class:

```text
video
message
file
location
device
account
```

Only segments supported by actual evidence appear.

The center may show:

```text
SOURCE ORIGIN COUNT
```

not “truth score”.

---

# 304. DIFFERENTIATED IDEA — PROVENANCE THREAD REPLAY

Replay how a graph object came into existence:

```text
Evidence loaded
 ↓
Artifact extracted
 ↓
Entity detected
 ↓
Relationship derived
 ↓
Graph projected
 ↓
Analysis changed
```

This is a **forensic birth replay** of the object.

It must use real processing events.

---

# 305. DIFFERENTIATED IDEA — EVIDENCE SHOCKWAVE

When new evidence changes a graph, show an evidence shockwave only around affected objects.

Example:

```text
New Evidence
   ↓
Affected Artifact
   ↓
Affected Entity
   ↓
Affected Relationships
   ↓
Affected Analytics
```

The shockwave communicates **impact**, not danger.

---

# 306. DIFFERENTIATED IDEA — ANALYTIC STABILITY WAVE

When an insight persists across multiple graph revisions, show a stability trail.

Example:

```text
Revision 1  ●
Revision 2  ●
Revision 3  ●
Revision 4  ○
```

This visually separates:

```text
persistent structural pattern
```

from:

```text
temporary analytical artifact
```

---

# 307. DIFFERENTIATED IDEA — PROVENANCE COLLISION

When two relationships appear independently supported but share a common source artifact, reveal:

```text
COMMON ORIGIN
```

This can prevent inflated assumptions of independent corroboration.

---

# 308. DIFFERENTIATED IDEA — TRUST DECOMPOSITION

Click one trust indicator and decompose it rather than opening a generic score:

```text
Integrity       ✓
Provenance      ✓
Attribution     ✓
Temporal        ~
Freshness       ✓
Review          !
```

Each symbol has textual explanation for accessibility.

---

# 309. DIFFERENTIATED IDEA — FORENSIC OBJECT PASSPORT

Every important graph object can have a compact **Forensic Passport**:

```text
Object ID
Semantic Type
State
Source
Processing Run
Model / Algorithm
Graph Revision
Provenance
Review
Current Permission
```

This makes the graph object operationally self-explaining.

---

# 310. FORENSIC PASSPORT SECURITY

The passport must itself obey field-level authorization.

Do not treat “passport view” as an unrestricted debug panel.

---

# 311. DIFFERENTIATED IDEA — PROVENANCE CHECKSUM PATH

Display a compact non-secret fingerprint for provenance state when useful:

```text
PROVENANCE FINGERPRINT
```

It can help investigators detect that two exported/report contexts reference the same lineage state without exposing sensitive underlying fields.

Do not invent a custom cryptographic scheme. Reuse established cryptographic primitives and approved project architecture.

---

# 312. DIFFERENTIATED IDEA — RELATIONSHIP LIFE CYCLE STRIP

For a selected edge:

```text
CANDIDATE → REVIEWED → DISPUTED → ACTIVE
```

or the actual lifecycle.

This makes graph relationships historical objects rather than permanent truths.

---

# 313. DIFFERENTIATED IDEA — PROVENANCE WATERFALL

A selected graph object can open a waterfall-like lineage:

```text
Source
████████
Artifact
  █████
Observation
    ████
Relationship
      ██
Review
       █
```

The visualization can show processing reduction / derivation depth.

Never make bar length represent certainty unless specifically defined.

---

# 314. DIFFERENTIATED IDEA — SECURE LENS SWITCH

Provide lenses:

```text
FORENSIC
PROVENANCE
SECURITY
TEMPORAL
GDS
EVIDENCE
REVIEW
```

A lens changes emphasis, not canonical truth.

Security lens example:

```text
authorized objects
restricted objects
current scope
recent access
```

Only if policy allows those concepts to be visible.

---

# 315. DIFFERENTIATED IDEA — PROVENANCE-AWARE GDS

When running a graph algorithm, do not merely highlight nodes.

Also expose:

```text
Which source data contributed to this analytic graph?
Which relationships were included?
Which were excluded?
Which revision?
```

This links mathematical graph intelligence back to forensic provenance.

---

# 316. DIFFERENTIATED IDEA — ANALYTIC SUPPORT PATH

For a selected GDS result:

```text
Analytic Result
 ↓
Node / Edge
 ↓
Graph Projection
 ↓
Underlying Relationship(s)
 ↓
Artifact(s)
 ↓
Evidence
```

This is the bridge between graph data science and evidence.

---

# 317. DIFFERENTIATED IDEA — SECURITY IMPACT OF GRAPH EXPANSION

Before a large expansion, the API may return a safe summary:

```text
Requested expansion
Possible authorized objects
Potentially restricted descendants
```

Do not reveal hidden counts.

Use only policy-safe information.

---

# 318. DIFFERENTIATED IDEA — FORENSIC DEAD-RECKONING WARNING

If a graph state is temporarily stale because realtime projection is delayed:

show:

```text
GRAPH PROJECTION LAG
```

Do not render it as if it were current.

---

# 319. DIFFERENTIATED IDEA — PROVENANCE HEARTBEAT

A subtle non-decorative indicator can show whether new graph objects still have valid lineage.

Example:

```text
PROVENANCE HEALTH
✓ stable
```

or:

```text
PROVENANCE DEGRADED
3 objects require review
```

This must be driven by actual health checks.

---

# 320. SECURITY + PROVENANCE MASTER RULE

The graph should answer four questions simultaneously:

```text
IS IT AUTHORIZED TO SEE?
IS IT TRACEABLE?
IS IT CURRENT?
IS IT REVIEWED?
```

If one is unknown, say so.

---

# 321. SECURE GRAPH API CONTRACT

Normalize graph responses into explicit DTOs.

Conceptually:

```json
{
  "case_id": "CASE-001",
  "graph_revision": "REV-42",
  "nodes": [],
  "edges": [],
  "meta": {
    "freshness": "...",
    "authorization_scope": "case",
    "generated_at": "..."
  }
}
```

Do not copy raw Neo4j driver records to the frontend.

---

# 322. NODE DTO SECURITY

Only return:

```text
stable ID
semantic type
authorized display fields
trust state
relationship counts when safe
provenance summary when safe
```

Do not automatically include all database properties.

---

# 323. EDGE DTO SECURITY

Return only:

```text
stable relationship ID
source ID
target ID
semantic type
authorized state
selected metadata
provenance summary
```

Do not expose hidden internals.

---

# 324. INSPECTOR API SECURITY

Inspector endpoints may have a larger data budget than the graph scene but must remain permission-controlled.

Separate:

```text
scene DTO
inspector DTO
source DTO
export DTO
```

Do not use one giant “get everything” endpoint.

---

# 325. PROVENANCE API SECURITY

Potential service boundary:

```text
GET /graph/relationships/{id}/provenance
```

or project convention.

The endpoint must:

1. authenticate
2. authorize case
3. authorize relationship
4. traverse only authorized lineage
5. minimize response
6. preserve provenance semantics

---

# 326. PROVENANCE PAGINATION

Long lineage chains and many observations should be paginated / lazy-loaded.

Summary first:

```text
6 supporting artifacts
```

then:

```text
open details
```

---

# 327. PROVENANCE N+1 PROTECTION

Do not issue one database request per lineage item.

Use batched, bounded retrieval where practical.

Measure query performance.

---

# 328. GRAPH + PROVENANCE TRANSACTION BOUNDARY

Where domain consistency requires it, ensure the source record and the event that causes graph projection can be correlated deterministically.

Do not rely on eventual graph appearance as proof that a domain mutation succeeded.

---

# 329. OUTBOX / EVENT LINKAGE

Use the existing outbox / domain event mechanism where available.

An event should identify the authoritative source record rather than duplicating sensitive payloads.

---

# 330. EVENT SCHEMA EVOLUTION

Version event contracts.

Do not silently change payload semantics.

Example:

```text
event_type
schema_version
case_id
aggregate_id
occurred_at
sequence
payload refs
```

---

# 331. SECURITY OF EVENT BUS

Protect Redis / event infrastructure.

Do not expose internal pub/sub channels directly to browsers.

The WebSocket gateway should be the controlled delivery boundary.

---

# 332. EVENT RETENTION

Event retention should follow system needs and policy.

Do not assume transient events are sufficient forensic evidence unless the domain explicitly defines them that way.

---

# 333. SOURCE EVENT VS GRAPH EVENT

Distinguish:

```text
SOURCE / DOMAIN EVENT
```

from:

```text
GRAPH PROJECTION EVENT
```

This matters for provenance and replay.

---

# 334. GRAPH EVENT PROVENANCE

A `GRAPH_EDGE_CREATED` event should be traceable to:

```text
source domain record
projection run/version
relationship ID
case
```

---

# 335. REALTIME PROVENANCE UX

When a new edge appears live:

show a subtle explanation chip such as:

```text
NEW
Source: E-44
```

or the safe equivalent.

Animation alone is not enough.

---

# 336. LIVE GRAPH UPDATE — CAMERA PRESERVATION

Realtime updates should not unexpectedly rotate, reset or jump the investigator's camera.

Preserve:

```text
camera
selection
current lens
filters
scroll / panel state
```

where practical.

---

# 337. LIVE GRAPH UPDATE — SELECTION PRESERVATION

If a selected node updates:

keep selection when safe.

If it becomes unauthorized due to policy change:

remove it from view and clear sensitive detail.

---

# 338. LIVE GRAPH UPDATE — REMOVAL SEMANTICS

If an object is retired/deleted:

show the correct state transition when policy requires.

Do not silently remove it if historical presentation needs explicit retirement.

---

# 339. LIVE GRAPH UPDATE — PROJECTION FAILURE

If a source event exists but graph projection has failed:

show:

```text
SOURCE UPDATED
GRAPH PROJECTION PENDING / FAILED
```

Do not claim graph freshness.

---

# 340. SOURCE-GRAPH CONSISTENCY STATUS

An enterprise graph workspace may show:

```text
AUTHORITATIVE DATA
GRAPH PROJECTION
REALTIME DELIVERY
```

as separate statuses.

This is more honest than one generic “Connected” badge.

---

# 341. FORENSIC GRAPH HEALTH PANEL

Provide a compact health view:

```text
Source Integrity     ✓
Projection           ✓
Provenance           ✓
Authorization        ✓
Realtime             ~
Analytics Freshness  !
```

Only actual measured conditions.

---

# 342. HEALTH STATE SEMANTICS

Use:

```text
HEALTHY
DEGRADED
STALE
FAILED
UNKNOWN
```

Never use optimistic status while data is unavailable.

---

# 343. UNKNOWN MUST REMAIN UNKNOWN

When a dependency cannot be checked:

show:

```text
UNKNOWN
```

not:

```text
HEALTHY
```

---

# 344. SECURITY STATUS MUST NOT LEAK INTERNALS

Health messages should be informative but not expose:

- credentials
- internal IPs
- database connection strings
- infrastructure topology beyond policy

---

# 345. PROVENANCE MONITORING DASHBOARD

For administrators / authorized forensic engineers, provide:

```text
orphaned graph records
missing provenance
stale analytics
projection lag
reconciliation mismatches
review backlog
```

This is separate from ordinary investigator UX.

---

# 346. ADMIN VS INVESTIGATOR DATA

Do not expose operational internals to normal investigators merely because the application has an admin API.

Use role-scoped UI and API boundaries.

---

# 347. FORENSIC PLATFORM SECURITY ARCHITECTURE

Target:

```text
                INTERNET / BROWSER
                        |
                   TLS / AUTH
                        |
                +-------v-------+
                |   FastAPI     |
                | AuthZ / ABAC  |
                +-------+-------+
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
      PostgreSQL      Redis       Graph Service
          |                           |
          |                           v
          |                         Neo4j
          |                           |
          v                           v
   Evidence /       Vector / GDS / Analytics
   Object Storage
          |
          +--------------+
                         |
                         v
                    Authorized DTOs
                         |
                         v
                     3D Frontend
                         |
                         v
                    Human Review
```

---

# 348. SECURITY CONTROL PLANE VS DATA PLANE

Separate conceptually:

```text
CONTROL PLANE
Auth
RBAC
Policy
Secrets
Model registry
MCP dev tooling
Operations
```

from:

```text
DATA PLANE
Evidence
Artifacts
Graph
Vectors
Realtime
Reports
```

Do not let a data-plane client access the control plane casually.

---

# 349. MCP AS DEVELOPMENT CONTROL PLANE

MCP belongs primarily to engineering / controlled agent workflows:

```text
inspect schema
inspect GDS
run controlled query
validate projection
```

Never use MCP as a shortcut around production application authorization.

---

# 350. MCP WRITE GOVERNANCE

Any graph mutation through MCP in development requires:

```text
environment confirmation
synthetic / safe dataset
explicit approval
auditable execution
rollback strategy
```

Never use an agent to perform unexplained destructive production writes.

---

# 351. PRODUCTION DEPLOYMENT SECURITY

Deployment must protect:

- environment variables
- secrets
- network boundaries
- database ports
- Neo4j ports
- Redis ports
- internal APIs
- object storage

Expose only intended public endpoints.

---

# 352. DATABASE NETWORK SECURITY

Databases should not be directly exposed to the public internet unless the actual architecture explicitly requires it and strong controls are present.

---

# 353. NEO4J NETWORK SECURITY

Use protected connectivity and approved TLS / credentials according to deployment environment.

The browser never receives direct Neo4j access.

---

# 354. REDIS NETWORK SECURITY

Redis should remain internal / protected.

Do not expose raw Redis to browsers.

---

# 355. POSTGRESQL NETWORK SECURITY

PostgreSQL should remain behind appropriate network access controls.

---

# 356. OBJECT STORAGE NETWORK SECURITY

Original evidence should remain private and scoped.

---

# 357. BACKUP SECURITY

Backups inherit data sensitivity.

Protect:

```text
PostgreSQL backups
Neo4j backups where used
Object storage versions
Audit logs
Provenance records
```

---

# 358. BACKUP PROVENANCE

A restored environment must preserve enough metadata to explain:

```text
what backup
when created
source environment
restoration event
```

---

# 359. DISASTER RECOVERY

After restore, validate:

```text
source evidence integrity
PostgreSQL consistency
Neo4j projection consistency
vector consistency
provenance completeness
audit availability
realtime resynchronization
```

---

# 360. RECOVERY MUST NOT CREATE FALSE HISTORY

A restored graph must not appear as a newly generated forensic graph state merely because the database was restored.

Maintain original source / processing timestamps and recovery metadata separately.

---

# 361. BUSINESS CONTINUITY

Define degraded behavior:

```text
Neo4j unavailable
→ evidence access still available

Realtime unavailable
→ graph snapshot still usable

GDS unavailable
→ core graph remains usable

3D unavailable
→ 2D / table fallback
```

Security controls remain active in all modes.

---

# 362. FAIL-CLOSED SECURITY

When authorization cannot be established:

prefer deny / safe failure over speculative access.

Do not:

```text
Auth service timeout
→ allow access
```

---

# 363. DEGRADED FORENSIC MODE

A degraded system may say:

```text
Graph unavailable
Source evidence available
```

or:

```text
Projection lagging
Canonical data current
```

This honesty is a production requirement.

---

# 364. SECURITY OF DEGRADED MODE

Do not weaken:

- authorization
- logging
- provenance
- data minimization

just because some services are unavailable.

---

# 365. LONG-SESSION SECURITY

Long investigator sessions should manage:

- token expiry
- permission refresh
- websocket reconnection
- sensitive state cleanup
- stale graph revision
- case switching

---

# 366. IDLE SESSION POLICY

Where policy requires, lock or expire sensitive views after inactivity.

The 3D graph should not silently remain fully exposed after prolonged inactivity if the security model requires re-authentication.

---

# 367. SCREEN CAPTURE AWARENESS

The platform cannot fully control OS-level screenshots.

Therefore reduce unnecessary persistent exposure:

```text
minimal sensitive data in main canvas
on-demand details
clear labeling
```

---

# 368. COPY / CLIPBOARD SECURITY

Sensitive inspector fields should not be copied automatically.

Clipboard actions may be auditable where policy requires.

---

# 369. DOWNLOAD SECURITY

Downloads should use explicit user actions and authorization checks.

Do not auto-download evidence or graph exports.

---

# 370. WATERMARK / CONTEXT LABEL

Where policy requires, derived visual outputs may include:

```text
CASE
DERIVED VIEW
GENERATED AT
```

Never imply that the visualization itself is original evidence.

---

# 371. FORENSIC CORRECTNESS OVER VISUAL BEAUTY

When a visual effect conflicts with forensic correctness:

```text
choose correctness
```

When animation conflicts with performance:

```text
choose performance
```

When AI convenience conflicts with authorization:

```text
choose authorization
```

When a graph shortcut conflicts with provenance:

```text
choose provenance
```

---

# 372. SECURITY UX LANGUAGE

Use precise language:

```text
Restricted
Unknown
Not processed
Not reviewed
Candidate
Disputed
Stale
Derived
Observed
```

Avoid ambiguous labels such as:

```text
Bad
Danger
Criminal
Truth
Fake
```

unless those are formally defined domain states.

---

# 373. ETHICAL GRAPH LANGUAGE

The platform must never visually or semantically imply:

```text
relationship = guilt
centrality = guilt
prediction = guilt
similarity = identity
anomaly = criminality
location = presence
association = intent
```

This is a permanent product rule.

---

# 374. INVESTIGATOR COGNITIVE SAFETY

The graph should help investigators inspect evidence rather than encourage premature conclusions.

Use:

```text
Why?
Sources?
When?
Derived how?
Reviewed?
Contradictions?
```

as high-value interactions.

---

# 375. GRAPH STORYTELLING SAFETY

When an investigator saves an investigative story:

Each narrative claim should remain linked to underlying graph/evidence objects.

Avoid free-floating narrative statements that appear authoritative without sources.

---

# 376. AI STORY SAFETY

AI-generated investigation summaries should cite source IDs / graph refs where appropriate.

Do not create a narrative that smooths away uncertainty or contradiction.

---

# 377. CONTRADICTION PRESERVATION

AI must not silently resolve contradictions by choosing one source without explaining the conflict.

Show:

```text
Source A says X
Source B says Y
Status: unresolved
```

when appropriate.

---

# 378. MISSINGNESS PRESERVATION

A missing field is not evidence that the opposite is true.

The graph should preserve:

```text
unknown
```

without converting it to a negative fact.

---

# 379. PROVENANCE DELETION SAFETY

When deleting derived data, verify whether dependent objects must also be deleted, expired, or marked orphaned.

Do not leave searchable sensitive remnants.

---

# 380. VECTOR REMNANT CHECK

After deletion workflows, verify:

```text
no unauthorized vector remains searchable
```

where applicable.

---

# 381. GRAPH REMNANT CHECK

After deletion / expiry workflows, verify:

```text
no unauthorized graph projection remains
```

where policy requires removal.

---

# 382. CACHE REMNANT CHECK

After deletion or permission revocation, evaluate sensitive caches.

Do not leave stale sensitive data available through cache even when canonical data is gone.

---

# 383. AUDIT REMNANT CHECK

Audit records may need to survive deletion for accountability.

Do not delete audit blindly when source data is deleted.

Follow governing policy.

---

# 384. FORENSIC DATA DELETION GRAPH

Deletion workflows should model dependencies:

```text
Source Evidence
 ↓
Derived Artifact
 ↓
Observation
 ↓
Embedding
 ↓
Candidate
 ↓
Sighting
 ↓
Graph Projection
 ↓
Vector Index
```

This dependency graph should be reasoned about explicitly before destructive operations.

---

# 385. PRIVACY + FORENSICS BALANCE

When privacy deletion and forensic preservation conflict:

The system must invoke the governing retention / legal-hold policy rather than invent a product-level override.

---

# 386. SECURITY RELEASE GATE

No production release is complete unless:

[ ] no browser → Neo4j
[ ] no browser → Redis
[ ] no browser → private object storage without authorization
[ ] case isolation tested
[ ] tenant isolation tested
[ ] resource authorization tested
[ ] provenance tested
[ ] audit tested
[ ] realtime authorization tested
[ ] GDS access tested
[ ] export tested
[ ] AI grounding tested
[ ] secrets absent from client
[ ] secrets absent from logs
[ ] stale cache risks reviewed
[ ] permission revocation tested

---

# 387. FORENSIC RELEASE GATE

[ ] source evidence preserved
[ ] hash integrity preserved
[ ] processing run attributable
[ ] model version attributable
[ ] policy version attributable
[ ] graph projection attributable
[ ] timeline linkage valid
[ ] provenance navigable
[ ] review history preserved
[ ] reprocessing distinguishable
[ ] corrections auditable
[ ] graph/evidence navigation works

---

# 388. 3D RELEASE GATE

[ ] trust states are visible
[ ] restricted data is not sent to browser
[ ] provenance accessible
[ ] source navigation works
[ ] graph-to-evidence works
[ ] evidence-to-graph works
[ ] 3D / 2D / table parity
[ ] camera state stable
[ ] realtime state honest
[ ] no fake graph data
[ ] no fake provenance
[ ] no fake confidence
[ ] no fake freshness

---

# 389. AI RELEASE GATE

[ ] AI receives only authorized graph context
[ ] evidence is treated as untrusted input
[ ] tool access is scoped
[ ] no arbitrary Cypher for normal users
[ ] claims are grounded
[ ] contradictions preserved
[ ] AI cannot silently write facts
[ ] AI cannot bypass review
[ ] AI output identifies uncertainty

---

# 390. GDS RELEASE GATE

[ ] algorithms verified available
[ ] algorithm access authorized
[ ] graph scope authorized
[ ] case isolation verified
[ ] parameters bounded
[ ] results provenance-complete
[ ] stale status handled
[ ] analytical language safe
[ ] export controlled

---

# 391. REALTIME RELEASE GATE

[ ] authenticated WebSocket/SSE
[ ] case authorization
[ ] sequence control
[ ] reconnect
[ ] snapshot reconciliation
[ ] no duplicate events
[ ] no unauthorized events
[ ] freshness measured
[ ] backpressure
[ ] resource cleanup

---

# 392. PERFORMANCE RELEASE GATE

Benchmark:

```text
small graph
medium graph
large graph
high-degree node
high provenance depth
burst realtime
GDS job
reconnect storm
```

Record measured:

```text
latency
throughput
memory
CPU
query time
render FPS
queue depth
error rate
```

---

# 393. SOAK TEST

Run long-duration tests for:

- realtime graph
- worker lifecycle
- websocket subscriptions
- GDS jobs
- memory growth
- cache growth
- graph renderer stability

Do not rely only on a short manual demo.

---

# 394. CHAOS TESTING

Controlled failures:

```text
Neo4j unavailable
Redis unavailable
PostgreSQL degraded
object storage timeout
worker crash
network partition
realtime reconnect
permission revocation
projection mismatch
```

Verify safe behavior.

---

# 395. SECURITY CHAOS

Test:

```text
role revoked
case access revoked
session expired
MCP disconnected
AI tool denied
graph query denied
export denied
```

The system must fail safely.

---

# 396. FORENSIC CHAOS

Test:

```text
duplicate event
out-of-order event
reprocessed source
changed model
changed threshold
missing provenance field
corrupt source artifact
```

Verify historical traceability.

---

# 397. OBSERVABILITY DASHBOARD

Authorized operations should expose:

```text
Auth health
Graph health
Projection health
Provenance health
Realtime health
GDS health
Evidence health
AI tool health
```

This is an operations view, not ordinary investigator data.

---

# 398. FORENSIC PROVENANCE HEALTH METRICS

Possible metrics:

```text
provenance complete rate
orphan rate
missing source rate
projection lag
stale analytics count
review backlog
reconciliation mismatch count
```

Use actual computed values.

---

# 399. SECURITY HEALTH METRICS

Possible metrics:

```text
auth failure rate
authz failure rate
cross-case access attempts
export count
suspicious query count
websocket authorization failures
```

Protect access to these metrics themselves.

---

# 400. FINAL ARCHITECTURE

The final CrimeKit design should converge on:

```text
                     CRIMEKIT
                        |
                 Authorized User
                        |
                Authentication
                        |
               Authorization Policy
                        |
               +--------+--------+
               |                 |
               v                 v
        Evidence Domain      Graph Service
               |                 |
               v                 v
          PostgreSQL          Neo4j / GDS
               |                 |
               v                 v
        Object Storage      Graph Analytics
               |                 |
               +--------+--------+
                        |
                Provenance Fabric
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
       Timeline      Vector       Realtime
          |             |             |
          +-------------+-------------+
                        |
                  Secure Graph API
                        |
                    3D Graph
                        |
         +--------------+--------------+
         |              |              |
         v              v              v
     Inspector       Timeline      Evidence View
         |
         v
    Human Review
         |
         v
      Audit Trail
```

---

# 401. GOLDEN USER JOURNEY

The final experience should allow an investigator to:

```text
LOGIN
 ↓
OPEN CASE
 ↓
KNOWLEDGE GRAPH
 ↓
VIEW 3D GRAPH
 ↓
SELECT ENTITY
 ↓
VIEW FORENSIC PASSPORT
 ↓
VIEW RELATIONSHIP MICROSCOPE
 ↓
OPEN SOURCE THREAD
 ↓
VIEW EVIDENCE
 ↓
VIEW TIMELINE
 ↓
VIEW PROVENANCE
 ↓
CHECK TRUST VECTOR
 ↓
CHECK CONTRADICTIONS
 ↓
VIEW ANALYTICS
 ↓
CHECK ANALYTIC FRESHNESS
 ↓
ASK GROUNDED AI
 ↓
VERIFY SOURCES
 ↓
HUMAN REVIEW
 ↓
SAVE INVESTIGATION STORY
 ↓
AUDITED REPORT / EXPORT
```

At every transition:

```text
authorization
provenance
data minimization
ethical semantics
```

remain intact.

---

# 402. FINAL IMPLEMENTATION DIRECTIVE

Do not merely build:

```text
security middleware
+
audit table
+
3D graph
```

Build a coherent **Forensic Trust Fabric** where security and provenance are inseparable from the graph experience.

The user should feel that every graph object has a passport, every relationship has an origin, every analytical result has a context, every sensitive action has a permission boundary, every realtime update has a source, and every AI statement can be verified.

---

# 403. FINAL NON-NEGOTIABLE RULES

```text
NEVER overwrite original evidence.
NEVER expose Neo4j directly to the browser.
NEVER expose MCP directly to the investigator browser.
NEVER treat frontend filtering as security.
NEVER leak hidden graph objects through autocomplete.
NEVER expose raw embeddings by default.
NEVER fabricate provenance.
NEVER fabricate confidence.
NEVER fabricate timestamps.
NEVER fabricate realtime status.
NEVER fabricate GDS outputs.
NEVER equate similarity with identity.
NEVER equate centrality with guilt.
NEVER equate graph connectivity with causation.
NEVER let AI silently create forensic facts.
NEVER let AI bypass case authorization.
NEVER let replay destroy historical meaning.
NEVER let stale analytics masquerade as current.
NEVER let case switching leak previous-case state.
NEVER let deleted sensitive data remain searchable through forgotten indexes.
NEVER use hidden CSS as authorization.
NEVER expose secrets in logs.
NEVER weaken security for demo convenience.
NEVER sacrifice forensic correctness for visual novelty.
```

---

# 404. FINAL GOLDEN PRINCIPLE

> **CrimeKit must not only show investigators what the graph says. It must show why the graph says it, where the information came from, which computation produced it, what is uncertain, who can access it, whether it is current, whether it has been reviewed, and how the investigator can verify it from source evidence.**

That is the standard for an enterprise-grade, evidence-grounded, secure, explainable 3D forensic knowledge platform.

---

# 405. HANDOFF TO THE NEXT IMPLEMENTATION STAGE

After implementing this prompt, the next engineering stage should verify the repository in reality:

```text
Repository Audit
 ↓
Provenance Model Audit
 ↓
Security Model Audit
 ↓
Graph API Audit
 ↓
Neo4j / MCP Audit
 ↓
Realtime Audit
 ↓
3D Renderer Audit
 ↓
Implementation
 ↓
Security Test Suite
 ↓
Provenance Test Suite
 ↓
Performance / Soak
 ↓
Production Gate
```

Do not claim completion until implementation, runtime behavior, tests, and evidence-backed verification agree.

---

# APPENDIX A — FORENSIC PROVENANCE FIELD CHECKLIST

For relevant derived graph objects, evaluate:

```text
[ ] case_id
[ ] investigation_id
[ ] source evidence ID
[ ] source artifact ID
[ ] parent object
[ ] child object
[ ] processing run ID
[ ] source timestamp
[ ] creation / derivation timestamp
[ ] detector/model information where relevant
[ ] algorithm information where relevant
[ ] policy version
[ ] confidence where actually defined
[ ] review state
[ ] correction / supersession history
[ ] graph projection version
[ ] graph revision where supported
```

---

# APPENDIX B — SECURITY CHECKLIST

```text
[ ] authentication
[ ] resource authorization
[ ] case isolation
[ ] tenant isolation
[ ] relationship authorization
[ ] path authorization
[ ] provenance authorization
[ ] websocket authorization
[ ] export authorization
[ ] cross-case authorization
[ ] vector authorization
[ ] AI tool authorization
[ ] secret management
[ ] TLS / transport security
[ ] storage security
[ ] log redaction
[ ] cache scope
[ ] permission revocation
[ ] session expiry
[ ] rate limits
[ ] query limits
[ ] GDS resource limits
[ ] audit logging
```

---

# APPENDIX C — 3D TRUST UX CHECKLIST

```text
[ ] observed vs derived
[ ] candidate vs reviewed
[ ] prediction vs fact
[ ] hypothesis quarantine
[ ] provenance thread
[ ] source navigation
[ ] evidence impact
[ ] processing impact
[ ] graph diff
[ ] contradiction view
[ ] knowledge gap view
[ ] trust vector
[ ] analytic freshness
[ ] common-origin warning
[ ] restricted-state semantics
[ ] 2D fallback
[ ] accessibility
[ ] reduced motion
```

---

# APPENDIX D — AI SAFETY CHECKLIST

```text
[ ] evidence treated as untrusted input
[ ] typed graph tools
[ ] no unrestricted Cypher
[ ] authorization inherited
[ ] source references returned
[ ] no unsupported claims
[ ] uncertainty visible
[ ] contradiction preserved
[ ] no silent fact creation
[ ] no silent source mutation
[ ] no provenance invention
```

---

# APPENDIX E — REALTIME CHECKLIST

```text
[ ] event schema versioned
[ ] event source identifiable
[ ] sequence / ordering
[ ] authorization on subscription
[ ] reconnect
[ ] snapshot recovery
[ ] gap detection
[ ] backpressure
[ ] UI coalescing safe
[ ] no unauthorized delta
[ ] freshness state measured
[ ] camera preserved
[ ] selection preserved
[ ] case switch safe
```

---

# APPENDIX F — GDS CHECKLIST

```text
[ ] algorithm availability verified
[ ] graph projection scoped
[ ] case isolation
[ ] parameters validated
[ ] job bounded
[ ] result persisted
[ ] provenance captured
[ ] graph revision captured
[ ] stale result handling
[ ] safe language
[ ] analytics export control
```

---

# APPENDIX G — ENTERPRISE DEFINITION OF DONE

CrimeKit's Forensic Provenance + Security layer is complete only when:

```text
AUTHENTICATION
    ✓
AUTHORIZATION
    ✓
CASE ISOLATION
    ✓
TENANT ISOLATION
    ✓
EVIDENCE INTEGRITY
    ✓
PROVENANCE COMPLETENESS
    ✓
MODEL / POLICY ATTRIBUTION
    ✓
GRAPH PROJECTION TRACEABILITY
    ✓
GDS TRACEABILITY
    ✓
REALTIME AUTHORIZATION
    ✓
AI GROUNDING
    ✓
HUMAN REVIEW BOUNDARY
    ✓
EXPORT AUDIT
    ✓
RETENTION / LEGAL HOLD
    ✓
3D / 2D / TABLE PARITY
    ✓
SECURITY TESTS
    ✓
PROVENANCE TESTS
    ✓
PERFORMANCE TESTS
    ✓
SOAK TESTS
    ✓
CHAOS TESTS
    ✓
PRODUCTION OBSERVABILITY
    ✓
```

---

# END OF MASTER PROMPT

**Implementation motto:**

```text
SOURCE FIRST.
PROVENANCE ALWAYS.
SECURITY EVERYWHERE.
GRAPH WITH CONTEXT.
AI WITH BOUNDARIES.
HUMANS IN CONTROL.
```


# IMPLEMENTATION MATRIX 01 — Repository Evidence Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 02 — Threat Model Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 03 — Trust-State Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 04 — Authorization Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 05 — Data Classification Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 06 — Provenance Field Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 07 — Graph Object Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 08 — Realtime Event Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 09 — GDS Result Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 10 — AI Claim Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 11 — Export Control Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 12 — Retention Dependency Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 13 — Security Test Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 14 — Provenance Test Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 15 — 3D Semantic Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 16 — Failure-State Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 17 — Observability Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 18 — Incident Response Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.

# IMPLEMENTATION MATRIX 19 — Production Gate Matrix

Before coding, create a concrete table in the implementation notes with: `Object / Source / Status / Owner / Authorization / Provenance / API / Storage / Failure Mode / Test / Acceptance`. Do not fill unknown fields with guesses. Mark them `UNKNOWN` and resolve them from repository evidence.
