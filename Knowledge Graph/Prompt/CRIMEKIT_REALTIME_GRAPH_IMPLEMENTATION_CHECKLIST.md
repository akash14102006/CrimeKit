# CRIMEKIT — REAL-TIME GRAPH
# IMPLEMENTATION + PRODUCTION ACCEPTANCE CHECKLIST

## Purpose

Release gate for the CrimeKit Real-Time Graph subsystem.

The subsystem is complete only when the following are verified with actual repository code, actual configured infrastructure, actual bounded data, and measured runtime behavior.

---

## 1. Architecture

| Gate | Pass condition |
|---|---|
| Authoritative source | PostgreSQL/domain records remain authoritative |
| Evidence | Original evidence remains in authoritative evidence storage |
| Graph | Neo4j is a projection / relationship intelligence layer |
| Event pipeline | Existing event infrastructure is reused where appropriate |
| API | FastAPI is the production graph boundary |
| Frontend | React/Next.js consumes normalized graph DTOs |
| Realtime | WebSocket/SSE uses authorized application gateway |
| Renderer | 3D rendering is separated from data reconciliation |

---

## 2. MCP / Antigravity

- [ ] Antigravity is configured as a development client.
- [ ] Official Neo4j MCP is used for development graph inspection.
- [ ] `get-schema` is available where supported.
- [ ] `read-cypher` is available where supported.
- [ ] `list-gds-procedures` is available where GDS is installed.
- [ ] `write-cypher` is disabled in production-facing development unless explicitly justified.
- [ ] Read-only mode is used by default where possible.
- [ ] `NEO4J_READ_ONLY=true` is used for readonly environments when applicable.
- [ ] MCP is never exposed to browser clients.
- [ ] MCP credentials are never shipped to frontend code.

---

## 3. Event Contract

- [ ] Event type is versioned.
- [ ] Event ID is stable.
- [ ] Case ID is present.
- [ ] Investigation scope is present where required.
- [ ] Source event ID is present where applicable.
- [ ] Sequence/watermark is defined.
- [ ] Source observed time is separate from ingestion time.
- [ ] Projection time is recorded separately.
- [ ] Graph revision is defined where replay/diff depends on it.
- [ ] Projection version is recorded.
- [ ] Provenance is attached where required.

---

## 4. Delivery Correctness

- [ ] Duplicate events are harmless.
- [ ] Out-of-order events are handled.
- [ ] Missing sequence is detected.
- [ ] Sequence gap triggers bounded recovery.
- [ ] Reconnect is tested.
- [ ] Resubscription is authorized again.
- [ ] Snapshot + delta consistency is tested.
- [ ] Stale events are handled explicitly.
- [ ] Events cannot cross case boundaries.

---

## 5. Neo4j Projection

- [ ] Stable domain IDs map to graph identities.
- [ ] Projection is idempotent.
- [ ] Projection supports retries.
- [ ] Projection failures are observable.
- [ ] Dead-letter handling exists where required.
- [ ] Reconciliation exists between authoritative records and Neo4j.
- [ ] Graph schema is verified against actual deployment.
- [ ] Constraints are verified.
- [ ] Indexes are verified.
- [ ] Query limits are enforced.
- [ ] Timeouts are enforced.
- [ ] Connection pooling/retry policy is configured appropriately.

---

## 6. Graph Revision / Freshness

- [ ] Graph revision/checkpoint semantics are defined.
- [ ] Event watermark is tracked.
- [ ] Projection lag is measurable.
- [ ] Source lag is distinguishable from projection lag.
- [ ] UI lag is distinguishable from source lag.
- [ ] Stale analytics are labeled.
- [ ] Old results are not presented as current.
- [ ] Revisions can be compared where supported.

---

## 7. WebSocket / SSE

- [ ] Authentication required.
- [ ] Case authorization enforced server-side.
- [ ] Graph permission enforced server-side.
- [ ] Subscription scope is bounded.
- [ ] Heartbeat/liveness is implemented where needed.
- [ ] Reconnect uses bounded backoff.
- [ ] Sequence recovery is implemented.
- [ ] Unauthorized event injection is rejected.
- [ ] Connection cleanup occurs on unmount/session end.
- [ ] Old-case subscription is closed before new-case subscription.

---

## 8. Client Reconciler

- [ ] Snapshot can initialize graph state.
- [ ] Deltas can mutate graph state deterministically.
- [ ] Same event can be applied twice safely.
- [ ] Event order is validated.
- [ ] Missing event is detected.
- [ ] Reconciliation can replace stale client state.
- [ ] Renderer is not the authoritative state holder.
- [ ] Reconciler can be unit-tested without WebGL.

---

## 9. 3D Renderer

- [ ] Stable camera.
- [ ] Stable selection.
- [ ] Stable manual layout where practical.
- [ ] Local/incremental layout preferred.
- [ ] Global layout is not triggered by every event.
- [ ] Node/edge budgets exist.
- [ ] Label budgets exist.
- [ ] Level of detail exists.
- [ ] High-degree node strategy exists.
- [ ] Burst mode exists.
- [ ] Frame pressure is monitored.
- [ ] Rendering can degrade without corrupting data state.
- [ ] 2D/table fallback exists.

---

## 10. Real-Time Visual Semantics

- [ ] New node animation is semantically meaningful.
- [ ] New edge animation is semantically meaningful.
- [ ] Update state is distinct from new state.
- [ ] Retraction is explicit.
- [ ] Correction is explicit.
- [ ] Prediction is visually separate.
- [ ] Hypothesis is visually separate.
- [ ] Contradiction has explicit semantics.
- [ ] Knowledge gap has explicit semantics.
- [ ] Stale analytics have explicit semantics.
- [ ] Source health has explicit semantics.
- [ ] Transport health is not confused with data freshness.

---

## 11. Search + Filters

- [ ] Search stays active while realtime updates arrive.
- [ ] Filters are re-applied to new deltas.
- [ ] Server-side filters reduce large-query pressure.
- [ ] Bounded graph expansion is used.
- [ ] Ghost nodes are clearly labeled.
- [ ] Ghost edges are clearly labeled.
- [ ] Search does not download the entire graph.
- [ ] Filtered-out events remain available in authoritative/replay state.

---

## 12. Timeline

- [ ] Live graph events can map to existing TimelineEvent records where supported.
- [ ] Event time is preserved.
- [ ] Unknown time is explicit.
- [ ] Timeline selection can focus graph context.
- [ ] Graph selection can focus timeline context.
- [ ] Replay does not silently become live mode.

---

## 13. Evidence / Provenance

- [ ] Graph relationship can open provenance.
- [ ] Provenance can reach artifact.
- [ ] Artifact can reach evidence.
- [ ] Evidence can reach original source.
- [ ] Processing run is visible where relevant.
- [ ] Missing lineage is shown as a provenance gap.
- [ ] Evidence impact is computed from real records only.
- [ ] No fake source links exist.
- [ ] No fake confidence exists.

---

## 14. GDS / Graph Intelligence

- [ ] Installed GDS version is verified.
- [ ] Actual available procedures are verified.
- [ ] Algorithm maturity is reviewed.
- [ ] Projection strategy is documented.
- [ ] Heavy jobs are asynchronous where necessary.
- [ ] Algorithm parameters are recorded.
- [ ] Scope is recorded.
- [ ] Graph revision is recorded.
- [ ] Result timestamp is recorded.
- [ ] Staleness is visible.
- [ ] Algorithms are not executed for every event by default.
- [ ] Centrality is not displayed as guilt.
- [ ] Community membership is not displayed as guilt.
- [ ] Similarity is not displayed as identity proof.
- [ ] Predicted relationships are not silently promoted to facts.

---

## 15. Realtime GDS UX

- [ ] Local change metrics are separated from global analytics.
- [ ] Analytics invalidation is explicit.
- [ ] Algorithm refresh is bounded.
- [ ] Analysis results have provenance.
- [ ] Revision comparison is available where supported.
- [ ] Analytical disagreement can be shown without inventing a composite truth.
- [ ] Algorithm limitations are visible.

---

## 16. Contradictions

- [ ] Contradiction definition is domain-reviewed.
- [ ] Conflicting source records are preserved.
- [ ] Contradiction status is explicit.
- [ ] A contradiction is not labeled as deception.
- [ ] Impact radius is bounded.
- [ ] Resolution is human-governed where required.

---

## 17. Knowledge Gaps

- [ ] Missing source is distinguishable from missing UI data.
- [ ] Missing provenance is distinguishable from low confidence.
- [ ] Missing timestamp is explicit.
- [ ] Unresolved identity is explicit.
- [ ] Incomplete projection is explicit.
- [ ] Stale analysis is explicit.
- [ ] Investigator can see what could resolve the gap when known.

---

## 18. Security

- [ ] Case isolation is enforced in every graph query.
- [ ] Case isolation is enforced in every realtime subscription.
- [ ] Case isolation is enforced in caches.
- [ ] Case isolation is enforced in analytics.
- [ ] Case isolation is enforced in AI retrieval.
- [ ] Cross-tenant leakage test passes.
- [ ] Graph query injection test passes.
- [ ] WebSocket authorization test passes.
- [ ] Session expiration test passes.
- [ ] Redaction test passes.
- [ ] Export authorization test passes.
- [ ] Secrets are not logged.

---

## 19. Privacy / Ethics

- [ ] Only authorized sources are processed.
- [ ] Sensitive data is minimized in realtime payloads.
- [ ] Predictions are separated from observations.
- [ ] AI cannot silently alter evidence.
- [ ] AI cannot silently create canonical relationships.
- [ ] Graph analytics cannot be interpreted as guilt.
- [ ] Identity claims follow configured review policy.
- [ ] User-facing terminology is neutral and forensic.
- [ ] Investigator decisions remain human-controlled.

---

## 20. Performance

- [ ] Snapshot size is bounded.
- [ ] Delta batch size is bounded.
- [ ] WebSocket buffer is bounded.
- [ ] Renderer object budget is bounded.
- [ ] Label budget is bounded.
- [ ] Edge budget is bounded.
- [ ] High-degree nodes are handled.
- [ ] Heavy GDS workloads are isolated.
- [ ] Query timeouts are measured.
- [ ] Cache behavior is measured.
- [ ] Long-session memory usage is measured.

---

## 21. Burst / Backpressure

- [ ] Synthetic burst test exists.
- [ ] Event coalescing rules are deterministic.
- [ ] UI intermediate states can be collapsed safely.
- [ ] Durable forensic events are not silently lost.
- [ ] Client queue can recover from overload.
- [ ] Degraded mode is visible.
- [ ] Automatic recovery is tested.

---

## 22. Failure / Recovery

- [ ] Neo4j outage tested.
- [ ] Redis outage tested.
- [ ] WebSocket disconnect tested.
- [ ] Network interruption tested.
- [ ] Worker crash tested.
- [ ] Duplicate event tested.
- [ ] Out-of-order event tested.
- [ ] Sequence gap tested.
- [ ] Projection lag tested.
- [ ] Browser tab suspension/resume tested.
- [ ] Renderer failure does not corrupt graph state.

---

## 23. Observability

- [ ] Correlation ID propagated.
- [ ] Event throughput metric.
- [ ] Projection latency metric.
- [ ] Source-to-display latency metric.
- [ ] Reconnect count.
- [ ] Sequence gap count.
- [ ] Dropped visual frame metric where available.
- [ ] Queue depth.
- [ ] Error rate.
- [ ] GDS job runtime.
- [ ] Graph query latency.
- [ ] Case-scoped operational dashboards.

---

## 24. Accessibility

- [ ] Keyboard navigation.
- [ ] Focus management.
- [ ] Reduced motion.
- [ ] Non-color semantics.
- [ ] Screen-reader graph summaries.
- [ ] 2D/table fallback.
- [ ] High contrast.
- [ ] Zoomed UI remains usable.

---

## 25. Test Matrix

| Test | Expected |
|---|---|
| Duplicate event | no duplicate graph object |
| Out-of-order event | deterministic correction/recovery |
| Missing sequence | gap detected and reconciled |
| Neo4j outage | clear degraded state |
| Redis outage | controlled recovery |
| WebSocket loss | reconnect + resume/resync |
| Large burst | bounded queues + coalesced UI |
| High-degree node | bounded rendering |
| Stale GDS result | clearly labeled stale |
| Retraction | historical transition preserved |
| Case switch | no old-case events after switch |
| Unauthorized subscription | rejected |
| AI request | only authorized graph context |
| 3D renderer failure | 2D/table fallback |
| Long session | no unbounded memory growth |

---

## 26. Golden End-to-End Scenario

```text
OPEN CASE
 ↓
OPEN KNOWLEDGE GRAPH
 ↓
LOAD BOUNDED SNAPSHOT
 ↓
CONNECT LIVE
 ↓
SOURCE HEALTH = HEALTHY
 ↓
NEW FORENSIC EVENT
 ↓
AUTHORITATIVE RECORD
 ↓
GRAPH PROJECTION
 ↓
REALTIME DELTA
 ↓
3D GRAPH UPDATE
 ↓
SELECT NEW RELATIONSHIP
 ↓
INSPECTOR
 ↓
PROVENANCE
 ↓
EVIDENCE
 ↓
TIMELINE
 ↓
GRAPH IMPACT
 ↓
ANALYTICS STALE
 ↓
RUN BOUNDED GDS REFRESH
 ↓
COMPARE GRAPH REVISION
 ↓
HUMAN REVIEW
 ↓
SAVE INVESTIGATION VIEW
```

---

## 27. Final Release Gate

Do not mark production-ready until:

```text
[ ] REALTIME is real
[ ] FRESHNESS is measured
[ ] GRAPH is authorized
[ ] EVENTS are ordered / recoverable
[ ] PROJECTION is idempotent
[ ] CASE ISOLATION is verified
[ ] PROVENANCE works
[ ] EVIDENCE links work
[ ] TIMELINE synchronization works
[ ] GDS availability is verified
[ ] ANALYTICS staleness is visible
[ ] 3D rendering is bounded
[ ] 2D fallback works
[ ] BURST mode works
[ ] RECONNECT works
[ ] RECONCILIATION works
[ ] SECURITY tests pass
[ ] ACCESSIBILITY tests pass
[ ] LOAD tests pass
[ ] SOAK tests pass
[ ] CHAOS tests pass
[ ] NO FAKE TELEMETRY
[ ] NO FAKE PROVENANCE
[ ] NO FAKE GRAPH RELATIONSHIPS
[ ] NO AUTOMATIC GUILT DETERMINATION
```

---

## Final Rule

**Do not ship a graph that merely looks live. Ship a graph whose live behavior can be proven from event history, graph revision, timestamps, provenance, authorization, and measured runtime telemetry.**
