# CRIMEKIT — 3D INTERACTIONS
## IMPLEMENTATION + RELEASE CHECKLIST

## FOUNDATION
- [ ] Repository audited before changes
- [ ] Existing graph UI identified
- [ ] Existing Graph API identified
- [ ] Existing state/store identified
- [ ] Existing realtime infrastructure identified
- [ ] Existing evidence inspector reused where possible
- [ ] Existing timeline reused where possible
- [ ] Existing design tokens reused

## NEO4J / MCP
- [ ] Official Neo4j MCP configured in Antigravity
- [ ] Current official MCP configuration verified
- [ ] `get-schema` verified
- [ ] `read-cypher` verified
- [ ] Readonly mode verified
- [ ] Development/staging instance used for agent exploration
- [ ] MCP kept separate from production browser data plane
- [ ] No Neo4j credentials in browser code

## GRAPH API
- [ ] Case-scoped API
- [ ] Parameterized graph queries
- [ ] Bounded hops
- [ ] Bounded node/edge count
- [ ] Query timeout
- [ ] Request cancellation
- [ ] Stale response protection
- [ ] Stable DTOs

## 3D CORE
- [ ] Orbit
- [ ] Pan
- [ ] Zoom
- [ ] Focus
- [ ] Reset
- [ ] Fit selection
- [ ] Node selection
- [ ] Edge selection
- [ ] Multi-select
- [ ] Context menu
- [ ] Expand / collapse
- [ ] Isolate
- [ ] Search-to-focus
- [ ] Mini-map
- [ ] 2D fallback

## FORENSIC INTERACTIONS
- [ ] Evidence Gravity
- [ ] Provenance Thread
- [ ] Evidence Impact
- [ ] Processing Impact
- [ ] Relationship Microscope
- [ ] Temporal Time Machine
- [ ] Graph Diff
- [ ] Contradiction Layer
- [ ] Uncertainty Layer
- [ ] Source Diversity
- [ ] Review Boundary
- [ ] Hypothesis Sandbox
- [ ] Knowledge Gap Explorer
- [ ] Investigation Replay

## REALTIME
- [ ] Actual event source
- [ ] No fake pulses
- [ ] Event IDs
- [ ] Idempotent updates
- [ ] Reconnect
- [ ] Backpressure handling
- [ ] Event batching
- [ ] Stale state banner
- [ ] Projection freshness
- [ ] User attention protection

## PERFORMANCE
- [ ] LOD
- [ ] Label budget
- [ ] Instancing where justified
- [ ] Resource disposal
- [ ] Dense graph tests
- [ ] Realtime burst tests
- [ ] Long-session soak
- [ ] WebGL context loss recovery
- [ ] GPU capability tiers

## SECURITY / PRIVACY
- [ ] Case isolation
- [ ] Tenant isolation if applicable
- [ ] WebSocket authorization
- [ ] Cache isolation
- [ ] PII field filtering server-side
- [ ] Export authorization
- [ ] Scene sharing authorization
- [ ] Deep-link authorization
- [ ] Cross-case analysis explicitly controlled

## FORENSIC TRUST
- [ ] Every important edge has WHY?
- [ ] Evidence links are real
- [ ] Provenance links are real
- [ ] Timeline links are real
- [ ] Candidate vs observed is visible
- [ ] Hypothesis is separated
- [ ] Contradictions are explicit
- [ ] Unknown time is not fabricated
- [ ] Unknown confidence is not fabricated
- [ ] Similarity is not presented as identity
- [ ] Centrality is not presented as guilt

## ACCESSIBILITY
- [ ] Keyboard interaction
- [ ] Screen-reader representation
- [ ] Graph table
- [ ] Relationship table
- [ ] 2D mode
- [ ] Reduced motion
- [ ] Color not sole status signal
- [ ] Accessible focus management

## FINAL GO / NO-GO

### GO ONLY WHEN
```text
REAL DATA
+ REAL PROVENANCE
+ REAL EVIDENCE
+ REAL TIMELINE
+ REAL REVIEW STATE
+ REAL AUTHORIZATION
+ REAL REALTIME
+ MEASURED PERFORMANCE
```

### NO-GO WHEN
```text
FAKE GRAPH
FAKE REALTIME
FAKE PROVENANCE
FAKE CONFIDENCE
HIDDEN CASE LEAK
UNBOUNDED QUERIES
3D WITHOUT 2D / ACCESSIBLE ALTERNATIVE
```
