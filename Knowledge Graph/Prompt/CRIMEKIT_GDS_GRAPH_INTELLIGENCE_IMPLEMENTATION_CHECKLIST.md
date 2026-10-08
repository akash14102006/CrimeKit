
# CRIMEKIT — GDS GRAPH INTELLIGENCE
# IMPLEMENTATION + PRODUCTION ACCEPTANCE CHECKLIST

## A. Repository and architecture

- [ ] Existing graph API inspected
- [ ] Existing Neo4j driver/service inspected
- [ ] Existing Neo4j schema inspected
- [ ] Existing 3D renderer inspected
- [ ] Existing search/filter/progressive loading inspected
- [ ] Existing realtime infrastructure inspected
- [ ] PostgreSQL authoritative boundary preserved
- [ ] Evidence/object storage boundary preserved

## B. Neo4j / GDS readiness

- [ ] Actual Neo4j version verified
- [ ] Actual GDS availability verified
- [ ] `list-gds-procedures` checked through MCP in developer/staging environment
- [ ] Required algorithms confirmed available
- [ ] Projection strategy documented
- [ ] Projection naming/versioning policy implemented
- [ ] Graph scope rules implemented
- [ ] Case isolation tested

## C. MCP / Antigravity

- [ ] Official Neo4j MCP configured
- [ ] Antigravity can inspect schema
- [ ] Antigravity can list GDS procedures
- [ ] Read-only mode enabled for production-adjacent environments
- [ ] Production UI does not call MCP
- [ ] Browser never receives Neo4j credentials
- [ ] MCP write capability restricted to controlled environments
- [ ] Developer mutations audited

## D. Analytics lifecycle

- [ ] REQUESTED
- [ ] AUTHORIZED
- [ ] PLANNED
- [ ] RUNNING
- [ ] READY
- [ ] STALE
- [ ] INVALIDATED
- [ ] FAILED
- [ ] CANCELED

## E. Provenance

- [ ] analysis_id
- [ ] case_id
- [ ] projection_id
- [ ] graph revision
- [ ] ontology version
- [ ] algorithm/version
- [ ] parameters
- [ ] scope
- [ ] timestamps
- [ ] result checksum where required
- [ ] interpretation policy version
- [ ] source graph object references

## F. Core GDS algorithms

- [ ] Degree Centrality
- [ ] PageRank
- [ ] Betweenness
- [ ] Closeness where justified
- [ ] Community detection
- [ ] Shortest paths
- [ ] Node Similarity
- [ ] KNN where justified
- [ ] Link Prediction only as candidate state
- [ ] Graph ML only with full evaluation/governance

## G. Explainability

- [ ] “Why this result?” implemented
- [ ] Method card implemented
- [ ] Scope visible
- [ ] Parameters visible
- [ ] Direction/weight semantics visible
- [ ] Limitations visible
- [ ] Evidence path available
- [ ] Provenance path available
- [ ] No unexplained composite risk score

## H. 3D intelligence

- [ ] Metric overlays are semantic
- [ ] Dynamic legend
- [ ] Signal constellation
- [ ] Algorithm disagreement field
- [ ] Community explode/collapse
- [ ] Temporal drift
- [ ] Graph revision comparison
- [ ] Evidence flight path
- [ ] Uncertainty represented separately from guilt/risk
- [ ] 2D fallback
- [ ] Table fallback
- [ ] Reduced-motion mode

## I. Search / filter integration

- [ ] Search can focus entity
- [ ] Search can initiate analytics
- [ ] Filters define analytics scope
- [ ] Time range changes scope correctly
- [ ] Progressive loading preserves analytics semantics
- [ ] Local vs global analysis explicitly labeled

## J. Realtime

- [ ] Analysis job status events
- [ ] Authorized WebSocket/SSE
- [ ] Reconnect
- [ ] Stale detection after graph changes
- [ ] No fake progress
- [ ] No unauthorized result broadcast

## K. Security

- [ ] RBAC enforced server-side
- [ ] Case isolation verified
- [ ] Cross-case analysis privileged
- [ ] Query limits
- [ ] Resource limits
- [ ] Export authorization
- [ ] Audit logging
- [ ] Prompt-injection defenses
- [ ] MCP isolated from production UI
- [ ] No sensitive logging

## L. AI

- [ ] AI only reads typed structured analytics
- [ ] AI cannot invent results
- [ ] AI cites analysis_id
- [ ] AI cites graph/evidence identifiers
- [ ] AI communicates uncertainty
- [ ] AI never equates graph analytics with guilt
- [ ] AI tool authorization matches user authorization

## M. Performance

- [ ] local graph benchmark
- [ ] medium graph benchmark
- [ ] large graph benchmark
- [ ] high-degree-node test
- [ ] memory pressure test
- [ ] concurrent analytics test
- [ ] 3D frame-time test
- [ ] progressive rendering test
- [ ] result pagination test
- [ ] long-session test

## N. Reliability

- [ ] Neo4j unavailable
- [ ] GDS unavailable
- [ ] Redis unavailable
- [ ] API restart
- [ ] worker restart
- [ ] duplicate job request
- [ ] out-of-order event
- [ ] stale projection
- [ ] partial analytics failure
- [ ] cancellation behavior
- [ ] recovery / reconciliation

## O. Ethics and forensic trust

- [ ] Centrality is never labeled guilt
- [ ] Community is never labeled criminal group without independent evidence
- [ ] Similarity is never identity proof
- [ ] Link prediction remains candidate
- [ ] Hypothesis graph is visibly non-authoritative
- [ ] Algorithm disagreement is visible
- [ ] Data quality warnings are separate from investigative priority
- [ ] Evidence remains authoritative outside GDS

## P. Release gate

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] API contract tests pass
- [ ] Graph isolation tests pass
- [ ] GDS algorithm tests pass
- [ ] Provenance tests pass
- [ ] Security tests pass
- [ ] Performance tests pass
- [ ] Accessibility tests pass
- [ ] Visual regression tests pass
- [ ] 3D fallback tests pass
- [ ] No fake analytics
- [ ] No fake realtime
- [ ] No fake confidence
- [ ] No fake progress
- [ ] Production build passes

## Golden acceptance journey

```text
LOGIN
 ↓
OPEN CASE
 ↓
KNOWLEDGE GRAPH
 ↓
SEARCH ENTITY
 ↓
CHOOSE GDS LENS
 ↓
DEFINE SCOPE
 ↓
RUN ANALYSIS
 ↓
3D RESULT
 ↓
WHY THIS RESULT?
 ↓
ALGORITHM / SCOPE / PARAMETERS
 ↓
CONFLICT / STABILITY
 ↓
GRAPH PATH
 ↓
PROVENANCE
 ↓
EVIDENCE
 ↓
TIMELINE
 ↓
SAVE VIEW
 ↓
REPORT
```

## Non-negotiable final gate

> **Every GDS result must be inspectable as an analytical statement about a defined graph projection — never as an unexplained verdict about a person.**
