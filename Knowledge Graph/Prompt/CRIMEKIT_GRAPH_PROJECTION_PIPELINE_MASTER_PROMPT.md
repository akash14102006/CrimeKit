# CRIMEKIT — GRAPH PROJECTION PIPELINE
## MASTER IMPLEMENTATION PROMPT
### Prompt #5 — Production Neo4j Graph Projection + 3D Forensic Knowledge Graph

> **Role:** Principal Graph Platform Architect • Neo4j Architect • Event-Driven Systems Engineer • Digital Forensics Architect • Security Architect • MCP Engineer • 3D Knowledge Graph Architect • Production Reliability Lead

## 0. EXECUTION CONTRACT

Treat this document as an implementation contract. Inspect before modifying. Reuse before replacing. Validate before writing. Test before claiming. Measure before scaling. Preserve source truth. Make every important graph relationship traceable.

---

## 0. MISSION

Act as CrimeKit’s Principal Graph Platform Architect, Forensic Data Architect, Neo4j Architect, Event-Driven Systems Engineer, Security Architect, MCP Engineer, 3D Knowledge-Graph Architect, and Production Reliability Lead.

Implement a real production Graph Projection Pipeline. Do not create a simple database sync. Build a deterministic forensic graph compiler that converts authoritative CrimeKit facts and processing events into a traceable Neo4j projection that can safely power the future 3D Knowledge Graph.

The result must be scalable, explainable, secure, case-isolated, replayable, observable, testable, ethically designed, and production-ready.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MISSION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 1. NOVELTY STANDARD

Create an unusually differentiated forensic graph system by combining provenance, time, contradiction, uncertainty, replay, graph-diff, evidence-impact mapping, entity resolution, controlled AI, and 3D visualization as one coherent architecture.

Do not claim literal global uniqueness or “nobody has ever built this” without evidence. Use language such as “proposed CrimeKit differentiator”, “original design”, or “novel combination”.

Innovation must be real functionality backed by source data, not visual effects.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `NOVELTY STANDARD` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 2. SOURCE OF TRUTH

PostgreSQL remains the authoritative CrimeKit domain/forensic record. Object storage remains authoritative for binary evidence. Redis/event infrastructure is the transport layer. Neo4j is the relationship-intelligence projection. FastAPI is the application security/service boundary. The 3D UI is a read/interaction surface. AI explains and reasons over retrieved data; it does not become evidence.

Never silently promote Neo4j into the source of truth. Every important graph record must be reconstructible from authorized source records/events.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `SOURCE OF TRUTH` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 3. REFERENCE ARCHITECTURE

Target flow:

PostgreSQL + Object Storage → Domain/Processing Events → Redis Streams/Event Layer → Projection Validator → Normalizer → Enricher → Graph Rule Engine → GraphIntent → Idempotency/Ordering → Neo4j Writer → Neo4j Aura → Graph API → 3D Graph Read Model → Investigator → Evidence/Timeline/Provenance → Human Review.

Developer/agent flow:
Google Antigravity → Official Neo4j MCP → DEV/STAGING Neo4j.

MCP is a development/agent access path. It is not the CrimeKit browser API and it must not be a production data dependency.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `REFERENCE ARCHITECTURE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 4. REPOSITORY-FIRST

Inspect the actual CrimeKit repository before editing. Identify the current backend, event model, Redis streams, workers, Neo4j client, graph services, database migrations, authentication, realtime layer, frontend graph implementation, test suite, deployment files, and any MCP configuration.

Classify each relevant component as IMPLEMENTED, PARTIAL, MOCKED, DEAD, DUPLICATED, DEPRECATED, PLANNED, EXPERIMENTAL, or UNKNOWN.

Reuse and harden working components before adding replacements.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `REPOSITORY-FIRST` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 5. DO NOT DUPLICATE

Do not create multiple competing Neo4j clients, projection workers, event buses, or graph write paths. Find the existing owner and consolidate responsibility.

If two components currently write the graph, document both, identify the authoritative path, and remove or deprecate the unsafe duplicate only after confirming call sites and tests.

Do not introduce Kafka, Temporal, OpenSearch, or another graph database solely because an old planning document mentions them.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `DO NOT DUPLICATE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 6. CANONICAL EVENT ENVELOPE

Create or adapt one canonical internal event envelope. It should support, where applicable: event_id, event_type, event_version, case_id, investigation_id, source_system, source_entity_id, occurred_at, emitted_at, correlation_id, causation_id, projection_version, actor_type, and payload.

The repository’s existing event schema is authoritative. Do not introduce duplicate fields when equivalent fields already exist.

Event identity and versioning must support replay and idempotent projection.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `CANONICAL EVENT ENVELOPE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 7. EVENT TIME VS SYSTEM TIME

Preserve the difference between event/observation time, ingestion/receipt time, and projection time where operationally useful.

Late-arriving forensic information must not be rewritten as if it originally occurred when it was received.

Where timestamps are uncertain or ranged, preserve uncertainty rather than fabricating an exact instant.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `EVENT TIME VS SYSTEM TIME` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 8. ORDERING

Never assume arrival order is domain order.

If ordering matters for an entity or relationship, use the existing source sequence/version/causation strategy. If no such strategy exists, document the limitation rather than inventing false ordering semantics.

Test out-of-order event delivery explicitly.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `ORDERING` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 9. IDEMPOTENCY

The projection path must tolerate duplicate delivery. Replaying the same event must not create duplicate semantic nodes or edges.

Use stable source identifiers or deterministic relationship identifiers. Do not rely on random IDs generated inside the projection worker for data that must be idempotent.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `IDEMPOTENCY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 10. PROJECTION STATES

Track projection lifecycle with explicit states such as RECEIVED, VALIDATED, PLANNED, PROJECTED, ACKNOWLEDGED, RETRYING, FAILED, and DEAD_LETTERED where the repository needs them.

Never silently drop an unsupported or invalid event.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PROJECTION STATES` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 11. GRAPH INTENT LAYER

Introduce a GraphIntent intermediate representation when the existing code does not already provide an equivalent abstraction.

Example intent:
operation=UPSERT_RELATIONSHIP; relationship_type=USES; source_id=P001; target_id=D001; case_id=CASE-01; provenance={evidence_id:E44}.

GraphIntent must be pure enough to test without a live database. This creates a clean boundary between domain mapping and Neo4j infrastructure.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH INTENT LAYER` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 12. GRAPH RULE REGISTRY

Create one explicit mapping from event type/version to projection handler/rules. Each rule must document source fields, normalization, node actions, relationship actions, provenance, idempotency, failure semantics, and tests.

Make the registry discoverable by developers and CI. Do not bury all graph logic in one giant project_everything() function.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH RULE REGISTRY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 13. ONTOLOGY CONTRACT

Maintain one canonical graph ontology definition shared by projection validation, documentation, API DTO mapping, tests, and 3D semantics.

Potential labels include Case, Investigation, Person, Device, Account, Phone, Email, IPAddress, Location, Vehicle, Evidence, Artifact, TimelineEvent, Observation, ProcessingRun, IdentityCandidate, GraphAssertion, GraphAnalysisRun, and Hypothesis, but only materialize labels supported by the actual domain.

Every relationship type requires direction, semantic definition, allowed source/target labels, required fields, provenance policy, temporal semantics, and review semantics.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `ONTOLOGY CONTRACT` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 14. NODE IDENTITY

Use stable domain IDs. Display names are not identity.

Separate immutable identity properties from mutable display/derived fields.

Avoid broad MERGE patterns that could accidentally merge distinct entities because names or weak attributes happen to match.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `NODE IDENTITY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 15. RELATIONSHIP IDENTITY

Every important relationship must have a stable identity strategy.

If the source domain already supplies relationship IDs, use them. Otherwise derive a deterministic key only when one logical relationship is intended. Do not collapse multiple legitimate observations into one edge merely because endpoints and relationship type match.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `RELATIONSHIP IDENTITY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 16. OBSERVATION VS SEMANTIC EDGE

Use direct semantic edges for common fast traversal, such as Person-[:USES]->Device, when the semantics are stable.

Use Observation/Assertion nodes when the relationship requires rich provenance, multiple observations, temporal context, source quality, or conflicting support.

A hybrid model is acceptable when it improves both investigation queries and auditability.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `OBSERVATION VS SEMANTIC EDGE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 17. PROVENANCE CHAIN

Important source-backed graph facts should remain traceable through:
Evidence → Artifact → ProcessingRun → Observation/Assertion → Entity → Relationship.

Do not store large binary evidence or full document contents in Neo4j merely to simplify navigation. Store IDs, metadata, provenance references, and retrieval pointers.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PROVENANCE CHAIN` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 18. PROVENANCE THREAD

Implement a proposed CrimeKit differentiator called the Provenance Thread.

Selecting a graph edge should allow the system to traverse back from Relationship → Assertion/Observation → Artifact → Evidence → Original Source.

The UI should show “why this edge exists” and the backend must answer it from real stored metadata.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PROVENANCE THREAD` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 19. OBSERVED VS INFERRED

Never collapse direct observation, algorithmic inference, AI hypothesis, and human-reviewed conclusion into one semantic type.

Candidate or inferred relationships must remain visibly and structurally distinct from verified facts.

Never turn a model similarity score into an identity assertion without the approved CrimeKit review workflow.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `OBSERVED VS INFERRED` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 20. CONFIDENCE MODEL

Confidence is not decoration. Where confidence is stored, preserve the source of the score, method, model/rule version, timestamp, and review status when appropriate.

Keep model confidence, source quality, temporal uncertainty, identity uncertainty, and human review state conceptually separate.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `CONFIDENCE MODEL` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 21. CONTRADICTION MODEL

Contradictory observations are first-class investigation information.

Do not resolve contradictions by overwriting one source with another. Preserve both observations and represent the contradiction explicitly when supported.

Create a Contradiction Lens in the UI as a proposed differentiator.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `CONTRADICTION MODEL` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 22. CASE ISOLATION

Every projection and query path must preserve case ownership. Where multi-tenancy exists, preserve tenant_id as well.

Do not rely on frontend filtering. Authorization is enforced server-side before graph reads/expansion and before graph writes.

Cross-case relationships require an explicit policy, explicit scope, and audit.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `CASE ISOLATION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 23. ENTITY RESOLUTION

Entity resolution may use name, email, phone, device identifiers, account references, location, image/face candidates, documents, or other supported signals.

Never merge weakly similar entities into one canonical Person without the approved identity policy.

Prefer candidate states such as UNRESOLVED, CANDIDATE, LIKELY, VERIFIED, and REJECTED where appropriate.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `ENTITY RESOLUTION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 24. CASE-SAFE GRAPH QUERIES

All graph reads must be case-scoped or backed by an identity model that guarantees safe global uniqueness plus independent authorization.

Never expose unrestricted MATCH (n)-[*]-(m) traversal.

Use max_hops, node/edge limits, relationship filters, time windows, and query timeouts.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `CASE-SAFE GRAPH QUERIES` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 25. EVENT VALIDATION

Validate required identifiers, event type/version, case ownership, timestamps, source references, allowed relationship semantics, provenance requirements, and data types before generating GraphIntent.

Invalid events must go to a controlled error/DLQ path. Never project malformed data simply because the graph writer can accept it.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `EVENT VALIDATION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 26. NORMALIZATION

Normalize graph-ready values such as IDs, timestamps, timezones, email/phone representations, IP formats, and device identifiers according to existing CrimeKit policies.

Do not mutate authoritative source data during normalization. Store derived/normalized attributes separately where necessary.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `NORMALIZATION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 27. ENRICHMENT

Enrichment can attach resolved entity IDs, source classifications, graph IDs, processing metadata, temporal quality, or model metadata.

Do not manufacture facts. Every enrichment that can materially affect investigation semantics must be traceable to a source or algorithm output.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `ENRICHMENT` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 28. GRAPH WRITER

The graph writer is infrastructure. It executes validated GraphIntent transactions, handles driver/session lifecycle, returns typed results, and exposes retry-compatible failures.

It must not contain case-resolution business rules or unrelated application logic.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH WRITER` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 29. TRANSACTIONS

Group semantically related changes into safe Neo4j transactions. Avoid giant transactions that can exhaust memory or block the graph for long periods.

A single evidence event may atomically create an Evidence node and its relationship to Case when the semantics require it.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `TRANSACTIONS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 30. MERGE POLICY

Use MERGE for stable identity upserts. Use CREATE only when duplicate records are intentionally meaningful and identity semantics guarantee that behavior.

Avoid MERGE on weak attributes such as a display name alone.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MERGE POLICY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 31. RETRY POLICY

Retry transient database/network failures with bounded exponential backoff. Do not retry authorization errors, invalid Cypher, invalid data, or schema failures forever.

Separate retryable and non-retryable errors with stable error codes.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `RETRY POLICY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 32. DEAD LETTER QUEUE

Repeatedly failed events enter a DLQ containing safe operational metadata: event_id, case_id, error_code, attempt_count, timestamps, projection_version, and enough context to diagnose.

Protect DLQ contents because forensic metadata may be sensitive.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `DEAD LETTER QUEUE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 33. BACKPRESSURE

Projection workers must respect Neo4j capacity. Measure queue depth, write latency, worker throughput, and error rates.

Do not let event intake grow without bound simply because the worker can read messages quickly.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `BACKPRESSURE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 34. BATCHING

Batch independent projection work when benchmarks show a benefit. Keep transactions bounded and observable.

Never create million-event transactions by default.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `BATCHING` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 35. CHECKPOINTING

Persist a restart-safe projection checkpoint appropriate to the existing Redis/event architecture: stream position, sequence, event offset, or equivalent.

After worker failure, resume safely. Idempotency must protect against replay around the checkpoint boundary.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `CHECKPOINTING` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 36. REPLAY

Support controlled replay of a single event, case scope, event range, or projection version when operationally justified.

Replay must be safe, auditable, and idempotent.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `REPLAY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 37. REBUILD

Neo4j should be reconstructible from authoritative CrimeKit sources/events. Provide a development/test rebuild procedure and a production runbook.

Rebuild should produce a logically equivalent graph for deterministic source data.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `REBUILD` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 38. SHADOW PROJECTION

For high-risk ontology changes, project the same source data into a shadow graph using the candidate projection version.

Compare current vs candidate graphs before cutover. Prefer blue/green or shadow strategies for major schema/projection changes.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `SHADOW PROJECTION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 39. GRAPH DIFF

Build a semantic graph-diff capability for development and governance.

Compare nodes added/removed, edges added/removed, changed properties, provenance changes, and case-level parity.

Counts alone are insufficient; inspect representative investigation paths.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH DIFF` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 40. RECONCILIATION

Create a reconciliation workflow that compares authoritative source expectations with Neo4j projection state.

Detect missing nodes, extra nodes, missing relationships, extra relationships, property mismatches, missing case ownership, and broken provenance references.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `RECONCILIATION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 41. NO AUTO-REPAIR

Do not auto-delete or auto-merge forensic graph data as a “repair”.

Preferred sequence: detect → report → review → controlled repair/reprojection → verify.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `NO AUTO-REPAIR` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 42. SCHEMA MIGRATIONS

Use explicit/versioned schema migrations or a safe initialization process. Never DROP ALL on application startup.

Schema changes require review of indexes, constraints, projection rules, API queries, 3D UI assumptions, and AI tools.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `SCHEMA MIGRATIONS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 43. CONSTRAINTS

Implement stable-ID uniqueness constraints for required labels, using the actual Neo4j version and syntax supported by the deployment.

Do not blindly add every possible constraint. Generate the final list from the canonical ontology and repository needs.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `CONSTRAINTS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 44. INDEXES

Add indexes only for measured access patterns such as stable IDs, frequently queried properties, temporal queries, or text/vector retrieval where required.

Validate actual query plans in development/staging. Do not create dozens of unused indexes.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `INDEXES` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 45. TEMPORAL MODEL

Support event time, validity intervals, first/last seen values, and projection time only where their semantics are clear.

A timeline query must distinguish “state at time T” from “event observed at time T”. Do not fake historical states from current mutable properties.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `TEMPORAL MODEL` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 46. TIME MACHINE

Implement a proposed CrimeKit differentiator: Temporal Graph Time Machine.

Allow investigators/developers to request a graph snapshot or replay at a selected point in time, using actual event history/checkpoints rather than animation-only effects.

The UI must communicate when a view is a historical reconstruction.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `TIME MACHINE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 47. EVIDENCE EMERGENCE

When a real projection creates a new relationship, the 3D view may subtly animate its emergence as a representation of graph change.

Never fabricate movement. Never use emergence animation to imply guilt or danger.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `EVIDENCE EMERGENCE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 48. EVIDENCE IMPACT MAP

From one evidence item, provide a structured impact chain:
Evidence → Artifacts → Observations → Entities → Relationships → Timeline Effects → Contradictions.

Only show actual computed results.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `EVIDENCE IMPACT MAP` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 49. PROCESSING IMPACT MAP

For a processing run such as OCR, TSK, metadata extraction, Face Trace, entity extraction, or timeline extraction, expose which graph entities/relationships were created or changed.

Retain processor/version/run provenance.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PROCESSING IMPACT MAP` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 50. KNOWLEDGE GAPS

Make unknowns visible. Proposed states include KNOWN, UNKNOWN, UNRESOLVED, MISSING, and CONFLICTED.

Never create placeholder edges to make the graph appear complete.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `KNOWLEDGE GAPS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 51. NEXT BEST EVIDENCE

A future AI/analytic layer can ask: “What additional evidence could reduce this uncertainty?”

Return evidence-review questions, not accusations. Recommendations must be grounded in the graph’s actual gaps and provenance.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `NEXT BEST EVIDENCE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 52. SOURCE DIVERSITY

Allow investigators to see whether a relationship is supported by different source categories such as CCTV, device log, document, communication, metadata, or human review.

Source diversity is context, not proof.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `SOURCE DIVERSITY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 53. RELATIONSHIP EVIDENCE STACK

When an edge is selected, show a structured stack:
semantic relationship → supporting observations → provenance → source evidence.

This should be one of the main enterprise UX differentiators of CrimeKit.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `RELATIONSHIP EVIDENCE STACK` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 54. HYPOTHESIS SANDBOX

Provide a clearly separated non-authoritative graph for analyst hypotheses, scenario exploration, and what-if reasoning.

Hypotheses never modify the canonical forensic graph. They must be labeled HYPOTHESIS and remain auditable.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `HYPOTHESIS SANDBOX` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 55. UNCERTAINTY STACK

Represent uncertainty dimensions separately where data supports them: identity uncertainty, temporal uncertainty, source quality, model confidence, review state.

Avoid a single mysterious “truth score”.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `UNCERTAINTY STACK` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 56. GRAPH ANALYTICS

Use Neo4j GDS only for justified analysis. Candidate algorithms may include centrality, community detection, path, similarity, or other supported algorithms.

Verify availability on the actual deployment. Keep persistent domain facts separate from transient analytics results.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH ANALYTICS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 57. GDS PROVENANCE

A GraphAnalysisRun should capture algorithm, scope, parameters, graph/projection version, timestamp, status, and result reference where needed.

Never encode “high centrality” as “criminal” or “guilty”.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GDS PROVENANCE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 58. GRAPH SEARCH

Provide bounded graph search and entity lookup using existing indexes. Search should support exact IDs, names, device references, account references, evidence IDs, and time constraints where required.

Do not create user-controlled Cypher.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH SEARCH` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 59. QUERY AST

For advanced graph filters, prefer a typed filter/AST contract translated by the backend into parameterized Cypher.

Never concatenate untrusted user input into Cypher text.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `QUERY AST` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 60. QUERY SAFETY

Every traversal has bounded depth and result limits. Every expensive path/analytics operation has a timeout or async job model.

Do not use unrestricted variable-length traversals in production endpoints.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `QUERY SAFETY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 61. GRAPH API

The 3D UI should call FastAPI graph services. The frontend never connects directly to Neo4j and never receives Neo4j credentials.

Define bounded operations such as case overview, neighbor expansion, path, search, timeline, provenance, diff, and checkpoints only where required by the existing API.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH API` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 62. GRAPH DTO

Return normalized DTOs rather than raw driver records.

Typical graph response:
nodes[], edges[], meta{case_id, graph_version, projection_version, generated_at, truncated, freshness}.

Mark truncation explicitly.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH DTO` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 63. GRAPH PAYLOAD

Keep graph payloads compact. Do not send binaries, giant transcripts, raw document bodies, or secrets through the graph API.

Return identifiers and references that allow the UI to request detailed evidence separately.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH PAYLOAD` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 64. 3D PROGRESSIVE LOADING

Initial graph = small, scoped overview. User action = bounded neighborhood expansion. Large clusters = collapsed representations with drill-down.

Never render the entire case graph merely because Neo4j can store it.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `3D PROGRESSIVE LOADING` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 65. 3D SCALE

Separate persisted graph size from simultaneously rendered graph size. Performance limits must be measured.

Use progressive loading, level of detail, instancing, frustum culling, and clustering according to the actual renderer and benchmarks.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `3D SCALE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 66. 3D NODE SEMANTICS

Use the existing reference screens to define the visual language. Preserve CrimeKit branding while borrowing structural/interaction inspiration only.

Suggested semantic mappings can include abstract geometry per entity type, but the final design must follow the approved reference and repository components.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `3D NODE SEMANTICS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 67. 3D EDGE SEMANTICS

Edges may encode type, direction, temporal state, provenance status, and uncertainty where justified.

Do not encode criminality, guilt, or danger using color, size, centrality, or motion.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `3D EDGE SEMANTICS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 68. PROVENANCE RIBBON

Proposed 3D interaction: selecting an evidence-backed edge opens a thin provenance ribbon connecting the semantic edge to Observation, Artifact, and Evidence metadata.

This is a visualization of an existing lineage chain, not a decorative fake relationship.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PROVENANCE RIBBON` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 69. GRAPH LENSES

Support optional graph lenses:
Evidence, Timeline, Device, Identity, Communication, Location, Provenance, Contradiction, Analysis, Hypothesis.

A lens changes query scope, emphasis, layout, or overlays; it does not mutate source facts.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH LENSES` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 70. GRAPH REPLAY

Use the same projection/replay event semantics to drive an Investigation Replay mode.

Replay should be deterministic for the same event set and projection version.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH REPLAY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 71. GRAPH CHECKPOINTS

Allow named analytical graph checkpoints such as Initial Intake, Post-Processing, Entity Resolution, Human Review, and Report State where operationally useful.

A user-facing visualization checkpoint is not the same as an evidence retention snapshot.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH CHECKPOINTS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 72. CASE GRAPH VIEW STATE

UI state such as camera position, selected nodes, filters, and layout belongs in the frontend/read-model layer, not in domain entity properties.

A saved graph view should reference case, scope, filters, and projection/checkpoint context so it can be reproduced.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `CASE GRAPH VIEW STATE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 73. REALTIME

If CrimeKit already uses Redis + WebSocket/SSE, extend that architecture.

Preferred flow:
source event → Redis → projection → Neo4j → authorized graph event → WebSocket/SSE → 3D update.

Do not poll Neo4j continuously as the default realtime mechanism.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `REALTIME` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 74. REALTIME SECURITY

Authorize WebSocket/SSE subscriptions per case/tenant. Never broadcast all graph changes globally.

A user who cannot read a case must not receive its graph update events.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `REALTIME SECURITY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 75. FRESHNESS

Expose actual graph freshness: last successful projection, projection lag, and graph status where supported.

Never claim “realtime” when the graph is materially stale.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `FRESHNESS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 76. GRAPH HEALTH

Track Neo4j connectivity, query failures, projection lag, DLQ count, reconciliation mismatches, and schema version.

Separate backend health from graph health.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH HEALTH` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 77. MCP PURPOSE

Use the official Neo4j MCP for controlled developer/agent access from Google Antigravity.

MCP should help inspect schema, run bounded reads, inspect development graph data, discover available GDS procedures, and validate projection results.

MCP must not replace the CrimeKit application graph API.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MCP PURPOSE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 78. OFFICIAL NEO4J MCP

Use the official Neo4j MCP project and current documentation.
Official docs: https://neo4j.com/docs/mcp/current/
Tools currently documented include get-schema, read-cypher, write-cypher, and list-gds-procedures.
Readonly mode is documented through NEO4J_READ_ONLY=true and removes write tools from the client surface.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `OFFICIAL NEO4J MCP` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 79. MCP AURA

Current Neo4j documentation describes an Aura MCP URL pattern using the actual instance ID, such as https://<INSTANCE_ID>.mcp-instances.neo4j.io, and documents enabling Tool authentication for the relevant Aura organization.

Never invent the instance ID. Never commit credentials.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MCP AURA` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 80. MCP LOCAL

For local/self-hosted development, the official Neo4j documentation currently documents installation with pip install neo4j-mcp-server and a stdio setup using environment variables.

Use the actual compatible version and current docs rather than copying stale snippets.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MCP LOCAL` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 81. ANTIGRAVITY MCP

Configure MCP using the actual Google Antigravity version installed in the environment. Current Google documentation demonstrates project/global MCP configuration patterns and Antigravity MCP management.

Possible project scope: .agents/mcp_config.json. Possible global scope: ~/.gemini/config/mcp_config.json. Inspect first; do not overwrite unrelated servers.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `ANTIGRAVITY MCP` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 82. MCP CONFIG MERGE

If .agents/mcp_config.json already exists, parse and merge. Preserve unrelated MCP servers. Validate JSON. Never hardcode secrets into committed project configuration.

Do not paste a configuration copied from VS Code, Cursor, Claude Desktop, or another client without checking Antigravity’s current schema.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MCP CONFIG MERGE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 83. MCP TARGET SEPARATION

Use clearly named environments such as CrimeKit DEV, STAGING, and PROD. Antigravity development sessions should default to DEV or a dedicated staging graph.

Production MCP should be read-only by default and require formal governance for any write-capable access.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MCP TARGET SEPARATION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 84. MCP WRITE SAFETY

The current official Neo4j docs caution that LLM-generated write Cypher can cause harm and recommend write mode only in development contexts.

Never test write-capable MCP against production. Do not let an AI agent arbitrarily execute CREATE, MERGE, DELETE, SET, DROP, index, or constraint operations on production.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MCP WRITE SAFETY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 85. MCP VALIDATION FLOW

Developer validation sequence:
1. Confirm target environment.
2. get-schema.
3. Run a bounded read-cypher query.
4. Inspect a known synthetic case.
5. list-gds-procedures if GDS is expected.
6. Verify projection-created nodes/edges.
7. Verify provenance.

Do not dump the entire graph.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MCP VALIDATION FLOW` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 86. MCP QUERY DISCIPLINE

Prefer natural-language, bounded diagnostics:
“Inspect the schema.”
“Count nodes by label.”
“Show relationship types.”
“Inspect relationships in CASE-TEST-001.”
“Find orphan nodes in CASE-TEST-001.”

The agent should summarize findings and identify the query scope.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MCP QUERY DISCIPLINE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 87. MCP FAILURE TESTS

Test MCP failure modes: server unavailable, wrong target, invalid credentials, wrong database, invalid query, Neo4j unavailable, read-only write attempt, and configuration syntax failure.

Failure messages should identify the class of problem without revealing secrets.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MCP FAILURE TESTS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 88. NO MCP DEPENDENCY

CrimeKit production must work when Antigravity is closed, the developer laptop is offline, and the MCP server is unavailable.

The production system must use its own FastAPI/Neo4j driver path.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `NO MCP DEPENDENCY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 89. MCP VS AI AGENT

Developer agent:
Antigravity → Neo4j MCP.

Investigator-facing AI:
CrimeKit AI tool layer → authenticated Graph API.

Do not give the investigator AI broader access than the investigator. Prefer typed graph tools over arbitrary Cypher.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MCP VS AI AGENT` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 90. GRAPH AI SAFETY

AI must not invent relationships. Every factual graph claim must be grounded in retrieved nodes/edges/provenance.

AI output must distinguish fact, inference, unknown, and recommendation.

Never convert graph centrality, anomaly scores, similarity, or associations into guilt.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH AI SAFETY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 91. PROJECTION TO AI

AI context should be a bounded graph neighborhood plus relevant evidence/provenance, not a full graph dump.

Use graph retrieval to reduce token cost and improve relevance, while keeping authoritative evidence access separate.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PROJECTION TO AI` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 92. FACE TRACE

Face Trace candidate outputs may project into an IdentityCandidate or equivalent structure. Preserve frame, detection, track, embedding, model/version, threshold policy, and review state where the existing system supports them.

Similarity is a candidate signal, not identity proof.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `FACE TRACE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 93. VIDEO/CCTV

High-volume CCTV pipelines should not necessarily create a permanent graph node for every frame. Prefer semantically useful objects such as Track, Observation, Sighting, Candidate, Camera, Location, and Evidence references.

Aggregate repeated observations only when the aggregation is reversible/traceable.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `VIDEO/CCTV` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 94. TIMELINE

Project timeline events with authoritative time semantics and source references. A graph timeline connection should be retrievable back to the artifact/evidence source.

Synchronize graph selection and timeline selection in the UI without duplicating timeline truth.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `TIMELINE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 95. COMMUNICATION

Messages, email, calls, or communication events may become explicit nodes or observations when their provenance and temporal context matter.

Do not infer intent solely from communication connectivity.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `COMMUNICATION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 96. LOCATION

Location relationships must preserve source semantics. Device location does not automatically prove person presence.

Use explicit observation/event semantics where needed.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `LOCATION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 97. DEVICE

Device relationships such as USES, OWNS, or CONNECTED_TO require source-backed definitions. Preserve observed time ranges where appropriate.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `DEVICE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 98. IP

Account/IP relationships should retain timestamps and source context. Do not automatically infer that an IP identifies a person.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `IP` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 99. EVIDENCE HASH

Where evidence hashes are part of CrimeKit, preserve the relationship between hash and source evidence.

Do not treat hash equality as equality of investigative context.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `EVIDENCE HASH` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 100. LARGE TEXT

Large documents/transcripts remain outside the graph unless a derived text index is specifically required. Store references and searchable summaries/metadata rather than duplicating entire source documents by default.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `LARGE TEXT` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 101. PII

Graph projections must never widen access compared with PostgreSQL. Sensitive properties should be minimized, masked, or protected according to CrimeKit’s RBAC and privacy policy.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PII` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 102. AUDIT

Track meaningful sensitive graph actions: graph search, path request, provenance opening, relationship review, export, admin graph operations, and controlled writes.

Do not log raw sensitive evidence or credentials.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `AUDIT` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 103. ADMIN OPERATIONS

Graph reconciliation, replay, rebuild, schema migration, and repair are administrative operations. Protect them with strong authorization and audit.

Do not expose reset/rebuild endpoints to the public application.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `ADMIN OPERATIONS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 104. OBSERVABILITY

Metrics should cover events, success/failure, retries, queue lag, projection latency, Neo4j transaction latency, DLQ, reconciliation, and graph query latency.

Use existing telemetry conventions instead of inventing a second observability stack.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `OBSERVABILITY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 105. TRACING

When distributed tracing exists, preserve request_id, correlation_id, event_id, and projection_run_id. Consider spans such as projection.validate, projection.plan, projection.write, projection.verify.

Avoid raw sensitive parameters in traces.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `TRACING` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 106. PERFORMANCE

Benchmark single events, small batches, realistic bursts, and sustained load. Measure events/sec, P50/P95/P99 projection latency, queue lag, Neo4j query latency, payload size, and duplicate rates.

Do not state unsupported capacity numbers.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PERFORMANCE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 107. LOAD/PHYSICAL SCALE

Separate persisted graph size from render size. A graph can be large while the browser shows only a bounded subset.

Use measured thresholds for node/edge counts returned per request and rendered per viewport.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `LOAD/PHYSICAL SCALE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 108. SOAK TEST

Run sustained projection for a realistic period. Look for memory growth, connection leaks, queue growth, latency drift, duplicate creation, and worker instability.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `SOAK TEST` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 109. FAILURE INJECTION

Test Redis interruption, Neo4j outage, worker crash, network interruption, schema mismatch, duplicate events, invalid events, and out-of-order events.

Prove recovery behavior rather than simply logging the failure.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `FAILURE INJECTION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 110. SECURITY TESTING

Test case bypass, tenant bypass, Cypher injection, credential leakage, unauthorized graph API, unsafe export, MCP unauthorized write, and direct browser-to-Neo4j access.

All failures must be denied safely.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `SECURITY TESTING` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 111. GOLDEN GRAPH

Create deterministic synthetic graph fixtures and golden expected states. Include simple, high-degree, contradiction, temporal, duplicate-event, identity-candidate, orphan, and multi-case scenarios.

Compare logical graph state rather than property order.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GOLDEN GRAPH` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 112. GRAPH REBUILD TEST

For a disposable development graph:
1. Project source fixture.
2. Capture expected graph.
3. Reset disposable graph.
4. Replay source.
5. Compare logical graph state.
6. Validate provenance and counts.

Rebuild parity is a major production acceptance gate.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH REBUILD TEST` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 113. PROJECTION DRY RUN

Support a dry-run mode that transforms events into GraphIntent without writing Neo4j.

Return the proposed nodes, relationships, validation warnings, provenance, and rule versions. Dry-run results can be reviewed before a rule is activated.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PROJECTION DRY RUN` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 114. PROJECTION IMPACT PREVIEW

For a new projection rule version, estimate the graph delta before production rollout:
new nodes, new edges, removed edges, changed provenance, changed temporal semantics.

Use shadow projection for high-risk changes.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PROJECTION IMPACT PREVIEW` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 115. CANARY

For major projection releases, use a synthetic or designated canary case, compare graph parity, inspect realtime output, and only then expand to broader production scope.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `CANARY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 116. ROLLBACK

Understand that application rollback does not automatically reverse Neo4j graph mutations. Prefer forward fixes, controlled re-projection, or rebuild when safer.

Document rollback/recovery per migration and projection version.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `ROLLBACK` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 117. SCHEMA VERSION

Track graph schema version, ontology version, and projection version separately where useful. Do not use one version number to represent everything.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `SCHEMA VERSION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 118. PROJECTION RELEASE

Every projection release should identify:
application version
ontology version
schema version
projection version
migration dependencies
compatibility notes.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PROJECTION RELEASE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 119. RELEASE GATES

Do not release a projection change if it causes unexplained duplicate relationships, loss of provenance, failed case isolation, rebuild mismatch, critical query regression, or schema incompatibility.

Require tests to pass before graph migration is considered complete.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `RELEASE GATES` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 120. GRAPH HEALTH SCORE

A developer/admin graph-health summary may include projection freshness, reconciliation, provenance completeness, schema validity, DLQ, and error rate.

This is a system quality indicator, not evidence truth or guilt scoring.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH HEALTH SCORE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 121. GRAPH TRUST VIEW

A case may show counts such as source-backed relationships, provenance-complete relationships, reviewed relationships, disputed relationships, and unresolved candidates.

Always define how each number is calculated.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH TRUST VIEW` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 122. UNKNOWN STATE

Absence of an edge is not proof of absence. Missing evidence is not proof of innocence or guilt. Unknowns remain unknown until evidence changes the state.

This principle should be reflected in graph semantics and UI copy.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `UNKNOWN STATE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 123. ETHICAL VISUALIZATION

Never use graph size, centrality, edge brightness, anomaly score, or face similarity as a proxy for criminality.

Use accessible, multi-channel visual encoding: shape, line style, text, iconography, and explicit status labels.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `ETHICAL VISUALIZATION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 124. REFERENCE UI

Use the user-provided reference screens and AI Agent Observatory-style 3D reference as visual direction. Reproduce the useful interaction language—dense graph workspace, strong inspector, temporal controls, visual focus—not third-party branding or proprietary code.

Preserve CrimeKit identity, labels, domain terminology, and forensic workflow.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `REFERENCE UI` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 125. GRAPH CANVAS

The 3D canvas is the primary workspace, surrounded by compact controls for search, filters, graph lenses, timeline, provenance, and replay.

Avoid turning the experience into a generic dashboard of giant cards.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH CANVAS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 126. INSPECTOR

Inspector should reveal:
identity
relationships
source/provenance
timeline
evidence
uncertainty
contradictions
review state
analysis

Do not show unsupported fields merely to fill space.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `INSPECTOR` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 127. GRAPH EMPTY STATE

If a case has no graph data, show a truthful empty state. Never inject fake nodes or relationships to make the graph look attractive.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH EMPTY STATE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 128. GRAPH STALE STATE

If projection lag is real, communicate graph freshness. If projection failed, communicate failure and recovery status.

Do not hide stale graph state behind a spinning animation.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH STALE STATE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 129. GRAPH TRUNCATION

When the backend truncates results, return truncated=true plus an explanation. The UI should provide refine/expand actions rather than silently hiding results.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH TRUNCATION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 130. GRAPH API AUTHORIZATION

Before every graph operation:
authenticate → authorize tenant/case → authorize operation → validate bounds → execute → return scoped DTO.

Do not rely on the fact that a node ID is unguessable.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH API AUTHORIZATION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 131. GRAPH EXPORT

Any export is a high-sensitivity operation. Scope it by case, user permission, filters, graph version, and time. Audit the export.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH EXPORT` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 132. SAVED VIEWS

A saved graph view stores presentation/read-model context, not mutable forensic truth. It may include case_id, graph snapshot/checkpoint reference, filters, selected node/edge IDs, layout mode, and camera state.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `SAVED VIEWS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 133. ANNOTATIONS

Investigator notes should remain separate from domain evidence. Use an Annotation or CaseNote model rather than writing analyst opinion into Person, Device, or Evidence factual fields.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `ANNOTATIONS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 134. HUMAN REVIEW

Relationships with material uncertainty should support review workflows such as accept, reject, dispute, or request more evidence.

Review actions must be auditable and must not mutate original evidence.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `HUMAN REVIEW` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 135. GRAPH WRITES

Canonical graph writes should originate from authorized application/projection workflows. Manual Cypher is a development/admin tool, not the hidden canonical application path.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH WRITES` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 136. NO ARBITRARY PRODUCTION WRITES

The frontend never writes Neo4j. Investigator AI never directly writes canonical facts. Antigravity MCP is read-only by default in production. Any exceptional write must have environment, authorization, explicit approval, and post-write validation.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `NO ARBITRARY PRODUCTION WRITES` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 137. SOURCE EVENT LINEAGE

Where practical, link a graph mutation to source_event_id, projection_rule_id, projection_version, and projection_run_id.

This creates a strong engineering lineage:
Source Event → Projection Rule → GraphIntent → Neo4j Node/Relationship.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `SOURCE EVENT LINEAGE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 138. SHOW THE WORK

Adopt CrimeKit’s “SHOW THE WORK” principle for graph projection. A developer or auditor should be able to see what was created, why it was created, which rule generated it, which source supported it, and when it was projected.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `SHOW THE WORK` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 139. PROJECTION DEBUGGER

A developer-only projection debugger may offer:
select event → validate → preview GraphIntent → project to DEV → inspect graph → reconcile.

Keep this path clearly separated from investigator UI and production admin operations.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PROJECTION DEBUGGER` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 140. GRAPH SIMULATOR

Provide a controlled sandbox for synthetic events. The simulator should demonstrate evidence registration, artifact extraction, entity resolution, observations, relationship creation, contradiction, and replay without touching production facts.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH SIMULATOR` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 141. EVENT SCENARIOS

Create synthetic scenarios for:
case creation
multiple evidence types
artifact extraction
entity resolution
device linkage
communication
location
face candidate
timeline
contradiction
late event
duplicate event
rebuild.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `EVENT SCENARIOS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 142. PROJECTION COVERAGE

Measure which source event types have projection rules, which rules have automated tests, which rules require provenance, and which rules are unsupported.

Unsupported events are visible rather than silently ignored.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PROJECTION COVERAGE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 143. SCHEMA DRIFT

Create a developer check comparing expected ontology vs actual Neo4j schema. Detect unexpected labels, relationships, missing constraints/indexes, and incompatible properties.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `SCHEMA DRIFT` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 144. ONTOLOGY CHANGE

Any node/relationship semantic change requires review of:
projection rules
Cypher
API DTOs
3D mappings
AI tools
queries
fixtures
migrations
reconciliation.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `ONTOLOGY CHANGE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 145. RELATIONSHIP DICTIONARY

For every edge type document:
name
meaning
direction
source labels
target labels
required properties
provenance
temporal semantics
review status
UI label.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `RELATIONSHIP DICTIONARY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 146. NODE DICTIONARY

For every node type document:
identity
source
case scope
lifecycle
PII/sensitivity
important properties
UI geometry/label
projection events.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `NODE DICTIONARY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 147. PROPERTY OWNERSHIP

Classify graph properties as:
source
normalized
derived
analytics
presentation.

Do not persist presentation state as domain truth.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PROPERTY OWNERSHIP` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 148. HIGH-DEGREE NODES

High-degree nodes can overwhelm a graph view. Backend and UI should aggregate or paginate connections while preserving drill-down to the underlying records.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `HIGH-DEGREE NODES` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 149. EDGE AGGREGATION

Repeated communication/sighting edges can be aggregated by semantic/time window where justified. Aggregated representations must retain a path back to their supporting observations.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `EDGE AGGREGATION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 150. CLUSTERING

Clusters may represent graph communities, entity types, evidence groups, timeline windows, or application-defined scopes. Never label a graph cluster as a criminal group without evidence and human interpretation.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `CLUSTERING` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 151. LAYOUT

Support force-directed, radial, temporal, hierarchical, clustered, and geospatial layout modes only where they improve an investigation task.

Layout is presentation logic, not a source-of-truth transformation.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `LAYOUT` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 152. GRAPH DIFF UI

A graph-diff screen should visually isolate new, removed, and changed relationships between checkpoints/versions. Each change should be selectable for provenance inspection.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH DIFF UI` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 153. TEMPORAL UI

Time slider controls must operate on actual event/projection history. Distinguish current graph, historical reconstruction, and replay mode in the UI.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `TEMPORAL UI` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 154. INVESTIGATION STORY

Generate a structured Investigation Story from actual events:
Evidence registered → artifact processed → entity resolved → relationship created → contradiction detected → review completed.

AI may summarize the story but cannot invent missing steps.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `INVESTIGATION STORY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 155. NEXT-QUESTION ENGINE

A future AI layer can identify graph knowledge gaps and propose review questions. Example: “Which source could verify ownership of Device D1?”

Never state that the missing fact is true.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `NEXT-QUESTION ENGINE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 156. GRAPH EVIDENCE INDEX

A proposed navigational metric can summarize support using source diversity, provenance completeness, review state, and contradiction indicators.

Name and define it carefully. Do not call it a “truth score”. Components must be inspectable and validated.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH EVIDENCE INDEX` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 157. GRAPH CONTENT POLICY

Do not send sensitive raw evidence into generic AI prompts. Retrieve only the minimum graph/evidence context needed for a question.

AI tool results should use structured IDs and evidence references.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH CONTENT POLICY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 158. AI TOOL CONTRACTS

Prefer typed tools:
find_entity
get_neighbors
find_path
get_timeline
get_evidence
get_provenance
get_graph_diff
get_graph_checkpoint.

Tool authorization must inherit authenticated case/tenant context.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `AI TOOL CONTRACTS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 159. AI EXPLANATION

Every AI graph explanation should provide:
Finding
Graph path
Evidence/source references
Uncertainty
Caveats
Human review state.

Do not call AI-generated text “evidence”.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `AI EXPLANATION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 160. MCP TOOL CONTRACT

The current official Neo4j MCP exposes schema discovery, read/write Cypher and GDS procedure discovery. Use read-only inspection by default and reserve writes for isolated development contexts.

The agent should never assume that a tool exists; inspect the currently connected tool set.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MCP TOOL CONTRACT` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 161. MCP READONLY

Prefer NEO4J_READ_ONLY=true when using the documented local/self-hosted MCP configuration. In this mode, write tools are not exposed.

For Aura, follow the current official Tool Authentication flow while maintaining the same least-privilege principle.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MCP READONLY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 162. MCP GDS

Use list-gds-procedures to discover actual GDS availability. GDS functionality may be absent; if it is absent, the MCP server can still provide other graph tools according to the current Neo4j documentation.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MCP GDS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 163. MCP TELEMETRY

Follow organizational privacy/security policy for MCP telemetry and logging. Do not disable required enterprise observability without authorization.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MCP TELEMETRY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 164. MCP VERSIONING

Record Neo4j MCP version and Neo4j driver/server version. For reproducible engineering environments, control upgrades and verify configuration/tool changes before adoption.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MCP VERSIONING` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 165. CONFIG SECRETS

Never store real Neo4j passwords, API keys, Bearer tokens, or OAuth client secrets in source control, screenshots, browser bundles, or documentation.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `CONFIG SECRETS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 166. FRONTEND SECRET TEST

Prove that browser bundles do not contain Neo4j credentials or MCP credentials. Frontend runtime should only receive authorized API data.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `FRONTEND SECRET TEST` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 167. NETWORK BOUNDARY

Production path:
Browser → FastAPI → Neo4j.

Developer path:
Antigravity → Neo4j MCP → Neo4j DEV/STAGING.

Never expose Neo4j directly to the browser.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `NETWORK BOUNDARY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 168. GRAPH HEALTH ENDPOINT

Reuse the existing health/readiness conventions. Distinguish backend process health, Neo4j reachability, schema readiness, and projection freshness where useful.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH HEALTH ENDPOINT` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 169. NO STARTUP DESTRUCTIVE ACTIONS

Application startup must not automatically drop graphs, delete indexes, or recreate the schema destructively.

Startup should check compatibility and fail clearly when the graph schema is incompatible.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `NO STARTUP DESTRUCTIVE ACTIONS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 170. MIGRATION SAFETY

Schema migration sequence:
inspect current schema → validate migration assumptions → apply safe changes → verify constraints/indexes → validate application compatibility → run projection tests → monitor.

Do not hide migration failures.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MIGRATION SAFETY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 171. GRAPH STATUS STATES

Useful states include HEALTHY, DEGRADED, UNAVAILABLE, SYNCING, STALE, and SCHEMA_INCOMPATIBLE.

Only expose a state when backed by actual measurements.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH STATUS STATES` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 172. QUERY ERROR MODEL

Use safe application error codes such as GRAPH_UNAVAILABLE, GRAPH_QUERY_TIMEOUT, GRAPH_FORBIDDEN, GRAPH_NOT_FOUND, GRAPH_SCHEMA_INCOMPATIBLE, GRAPH_PROJECTION_FAILED, and GRAPH_INVALID_REQUEST.

Do not return raw Cypher stack traces to investigators.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `QUERY ERROR MODEL` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 173. QUERY OBSERVABILITY

Track query template name, latency, returned node/edge counts, timeout/error class, and case/tenant scope. Avoid logging sensitive raw parameters.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `QUERY OBSERVABILITY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 174. CACHE SAFETY

If graph responses are cached, cache keys must include tenant/case/scope/filter/version context. Never use a global cache key for sensitive graph results.

Invalidate safely when realtime graph changes materially.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `CACHE SAFETY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 175. GRAPH FRESHNESS CACHE

When a cached graph snapshot is stale, surface the actual snapshot/projection time. Never silently return old forensic relationships as if they were current.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH FRESHNESS CACHE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 176. GRAPH EXPORT METADATA

Every export should record scope, case, user, timestamp, graph/projection version, filters, and result type where policy requires it.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH EXPORT METADATA` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 177. DATA RETENTION

Derived graph data must follow CrimeKit case/evidence retention rules. Do not invent legal-retention policy. Implement the policy that the organization actually defines.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `DATA RETENTION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 178. LEGAL HOLD

If legal-hold functionality exists, graph retention/reprojection/cleanup must honor it. Do not auto-delete or archive protected records.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `LEGAL HOLD` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 179. CLOSED CASE

Closing a case should change application/case state according to policy. It must not silently erase the graph.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `CLOSED CASE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 180. GRAPH REOPEN

If a case can be reopened, preserve auditability and graph history. Do not erase previous review states.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH REOPEN` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 181. FORENSIC INTEGRITY

Never modify original evidence from the graph pipeline. Preserve hashes and chain-of-custody semantics from the authoritative evidence system.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `FORENSIC INTEGRITY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 182. SOURCE QUALITY

If OCR quality, timestamp quality, image quality, or face quality are available, preserve them as source-quality metadata. Do not turn source quality into relationship certainty.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `SOURCE QUALITY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 183. MULTI-DIMENSIONAL TRUST

A relationship can expose independent dimensions:
source quality
model confidence
review state
temporal confidence
identity confidence.

Use explicit definitions for each dimension.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MULTI-DIMENSIONAL TRUST` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 184. GRAPH ASSERTIONS

A GraphAssertion can model derived/inferred claims without confusing them with source observations. It should reference its inputs, method, version, and review state when implemented.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH ASSERTIONS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 185. REVIEW EVENTS

Human review actions are events/audit records. A review does not rewrite the original source event. It changes the status of an assertion/candidate according to policy.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `REVIEW EVENTS` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 186. PROJECTION RULE VERSION

When a relationship is created, retain projection rule/version metadata where useful. This allows future debugging when two relationships look similar but came from different rule generations.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PROJECTION RULE VERSION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 187. PROJECTION RUN

Group projections into observable runs. A run can record start/end, worker version, source range, rule version, success count, failure count, retry count, and reconciliation status.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PROJECTION RUN` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 188. GRAPH CHECKSUM

For deterministic environments, consider a logical projection checksum or graph fingerprint over stable IDs, relationship types, and selected properties. Use it for rebuild/diff validation, not as a cryptographic proof of evidence truth.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH CHECKSUM` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 189. REBUILD PARITY

A rebuild is successful when the expected logical graph matches the rebuilt graph for the defined scope and projection version. Explain intentional nondeterminism such as timestamps generated at projection time.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `REBUILD PARITY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 190. SOURCE EVENT REPLAY

Replay should preserve event semantics. Do not create a new event identity just because the event is replayed; the same event should remain idempotent under the same projection version.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `SOURCE EVENT REPLAY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 191. PROJECTION VERSION REPLAY

If a new projection version is intentionally replayed, the version itself becomes part of the deployment/change context. Do not accidentally mix old and new semantic projections without a compatibility plan.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PROJECTION VERSION REPLAY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 192. GRAPH REPAIR

Prefer repairs that regenerate the affected graph slice from source truth instead of hand-editing arbitrary properties. Where manual administrative Cypher is unavoidable, record who, why, what changed, and how it was verified.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH REPAIR` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 193. GRAPH INCIDENT RUNBOOK

Prepare a runbook for:
Neo4j unavailable
projection stuck
DLQ growth
schema mismatch
wrong relationship
duplicate relationship
case leakage
credential compromise
rebuild/reconciliation.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH INCIDENT RUNBOOK` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 194. CREDENTIAL ROTATION

Neo4j credentials must be injected through deployment secrets/configuration. The application should support credential rotation without code changes.

MCP credentials/Tool Authentication should be rotated independently where the environment supports it.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `CREDENTIAL ROTATION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 195. DR PLAN

Because Neo4j is reconstructible projection data, disaster recovery can use authoritative PostgreSQL/events plus object-storage metadata to rebuild graph state.

Document the actual RTO/RPO targets; do not invent them.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `DR PLAN` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 196. CAPACITY PLANNING

Plan capacity around:
persisted node/edge growth
event throughput
query concurrency
analytics load
3D rendering load.

These are distinct scaling dimensions.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `CAPACITY PLANNING` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 197. GRAPH GROWTH

Monitor node/edge growth, degree distribution, high-degree hotspots, property growth, index size, and per-case graph density.

Do not allow uncontrolled relationship explosion.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH GROWTH` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 198. SEMANTIC COMPRESSION

For repeated structures, provide compact graph DTOs and bounded neighborhood retrieval. AI context can summarize repeated patterns rather than sending every repeated relationship in raw form.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `SEMANTIC COMPRESSION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 199. 3D GRAPH API MODES

Design bounded read modes such as:
overview
neighborhood
path
provenance
timeline
diff
analysis
replay.

Each mode has a documented result budget.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `3D GRAPH API MODES` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 200. 3D NODE SELECTION

Every rendered node maps to a stable domain/graph ID. Selecting a node should not require guessing the underlying entity from visual state.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `3D NODE SELECTION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 201. 3D EDGE SELECTION

Every rendered edge maps to a stable relationship/assertion identifier. Selecting it should open provenance when available.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `3D EDGE SELECTION` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 202. GRAPH-to-EVIDENCE

Implement a direct path from graph edge/node to supporting Evidence/Artifact/ProcessingRun. The investigator should not need to manually search the evidence library again.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH-to-EVIDENCE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 203. EVIDENCE-to-GRAPH

Implement a reverse path from Evidence/Artifact to graph impact. This shows what the evidence contributed to graph knowledge.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `EVIDENCE-to-GRAPH` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 204. GRAPH-to-TIMELINE

Selecting a graph entity should reveal relevant timeline events, with actual time and source references.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH-to-TIMELINE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 205. TIMELINE-to-GRAPH

Selecting a timeline event should focus/highlight graph entities and relationships involved in that event.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `TIMELINE-to-GRAPH` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 206. CONTRADICTION-to-EVIDENCE

Selecting a contradiction should show the competing observations and their source evidence. Never hide the conflict behind one resolved value unless a human review policy explicitly resolves it.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `CONTRADICTION-to-EVIDENCE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 207. GRAPH DIFF-to-PROVENANCE

Every graph-diff change should be traceable to the source event/rule responsible for the change when that metadata is available.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH DIFF-to-PROVENANCE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 208. GRAPH LENS-to-QUERY

A graph lens should correspond to a controlled backend query or filter contract. Do not implement lenses only by hiding nodes client-side when security/scoping requires server-side filtering.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH LENS-to-QUERY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 209. GRAPH VIEW PERFORMANCE

Measure initial-load latency, expansion latency, selection latency, path latency, and realtime update handling. Optimize the query first, then the renderer.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `GRAPH VIEW PERFORMANCE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 210. WEBGL FAILURE

If 3D rendering fails or the device cannot sustain it, provide a usable 2D/structured fallback where the frontend architecture supports it. Never make a low-power client unusable because the 3D layer cannot initialize.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `WEBGL FAILURE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 211. MOBILE/RESPONSIVE

Where required, adapt the inspector and graph controls for smaller screens without changing graph semantics. Large graph tasks may remain desktop-first if the product explicitly targets forensic workstations.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MOBILE/RESPONSIVE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 212. ACCESSIBILITY

Do not rely on color alone. Provide text labels, icons, line styles, keyboard/focus alternatives, and accessible descriptions for important graph states.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `ACCESSIBILITY` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 213. VISUAL RESTRAINT

Avoid glassmorphism, excessive neon, rainbow edges, giant cards, or decorative animation unless the approved reference explicitly requires a restrained version.

Enterprise forensic UI should prioritize readability and traceability over spectacle.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `VISUAL RESTRAINT` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 214. NO FAKE REALTIME

Realtime animation must be triggered by actual graph events. If no event is available, do not animate the graph simply to make it look live.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `NO FAKE REALTIME` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 215. NO FAKE CONFIDENCE

Every confidence/similarity number must come from an actual model/rule result. Never fabricate random confidence values for demos that could be confused with production data.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `NO FAKE CONFIDENCE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 216. DEMO DATA

Synthetic/demo graph data must be clearly labeled and isolated. Never mix synthetic data into production investigation cases.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `DEMO DATA` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 217. DEVELOPER ENVIRONMENT

Local/dev should have a safe disposable graph. MCP should default to that environment. Production data must not be copied into developer laptops unless policy explicitly allows it.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `DEVELOPER ENVIRONMENT` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 218. STAGING

Staging should contain realistic synthetic datasets large enough to validate projection, 3D loading, realtime updates, provenance, reconciliation, and GDS behavior.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `STAGING` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 219. PRODUCTION ENVIRONMENT

Production graph access should use secure networking, least-privilege runtime credentials, audited admin access, monitored projection workers, and a documented recovery plan.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PRODUCTION ENVIRONMENT` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 220. FILE CHANGE MAP

At the end, report actual repository paths under:
EXISTING—KEEP
EXISTING—MODIFY
NEW—CREATE
DEPRECATED—REMOVE/REVIEW
UNKNOWN—INVESTIGATE.

Never invent file paths.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `FILE CHANGE MAP` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 221. IMPLEMENTATION ORDER

Recommended order:
1 repository audit
2 ontology contract
3 event envelope
4 validation/normalization
5 GraphIntent
6 schema
7 writer
8 idempotency/order
9 retries/DLQ/checkpoint
10 reconciliation/rebuild
11 graph API
12 realtime
13 GDS
14 3D
15 AI tools
16 MCP
17 production QA.

Do not optimize the 3D graph before the projection semantics are correct.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `IMPLEMENTATION ORDER` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 222. REQUIRED TEST MATRIX

Unit: rules, validators, GraphIntent.
Integration: Redis/event → projection → Neo4j.
Security: case isolation, injection, credentials, MCP.
Reliability: duplicates, out-of-order, retry, crash/restart.
Data quality: reconciliation, provenance, schema drift.
Performance: load/soak/query latency.
UI: overview/expand/path/provenance/replay/realtime.
Recovery: rebuild parity.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `REQUIRED TEST MATRIX` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 223. MCP ACCEPTANCE TABLE

Produce:
MCP server installed | expected | actual | status
Antigravity sees server | expected | actual | status
Target environment | expected | actual | status
get-schema | expected | actual | status
read-cypher | expected | actual | status
list-gds-procedures | expected | actual | status
readonly protection | expected | actual | status
production guardrail | expected | actual | status.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `MCP ACCEPTANCE TABLE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 224. PROJECTION ACCEPTANCE TABLE

Produce:
Event validation
GraphIntent correctness
Node identity
Relationship identity
Idempotency
Ordering
Retry/DLQ
Provenance
Case isolation
Reconciliation
Replay
Rebuild
Realtime freshness
3D DTO
Security
Performance.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `PROJECTION ACCEPTANCE TABLE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 225. FINAL SCORECARD

Score with evidence:
ontology correctness /10
projection correctness /10
idempotency /10
ordering /10
provenance /10
case isolation /10
reliability /10
rebuildability /10
reconciliation /10
API readiness /10
realtime /10
3D readiness /10
AI readiness /10
MCP integration /10
security /10
performance /10
observability /10
testing /10
documentation /10
operational readiness /10.

Never inflate scores to make the project look complete.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `FINAL SCORECARD` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 226. FINAL READINESS GATES

Declare PRODUCTION READY only when source truth is preserved, graph projection is deterministic for defined inputs, case isolation is tested, provenance is traceable, failures are recoverable, graph is rebuildable, queries are bounded, MCP is governed, 3D uses real data, AI is grounded, and observability/testing are present.

Otherwise state READY AFTER FIXES or NOT READY and list the blockers.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `FINAL READINESS GATES` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 227. FINAL ARCHITECTURE

Canonical path:
PostgreSQL/Object Storage → Events → Redis → Forensic Graph Compiler → GraphIntent → Neo4j Aura.

Consumer path:
Neo4j → Graph Service → Authorized Graph API → 3D Knowledge Graph → Timeline/Evidence/Provenance → Human Review.

Developer path:
Google Antigravity → Official Neo4j MCP → Neo4j DEV/STAGING.

AI path:
Authenticated CrimeKit AI Tools → Graph API → bounded graph/evidence retrieval → grounded explanation.

These paths intentionally coexist without collapsing responsibilities.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `FINAL ARCHITECTURE` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 228. FINAL INNOVATION TARGET

The final experience should answer two questions better than a generic graph:

1. “Why are these connected?”
Relationship → observation/assertion → evidence → artifact → processing → model/rule → review → contradiction.

2. “What did this evidence change?”
Evidence → derived artifacts → new entities → new relationships → timeline changes → contradictions → knowledge gaps → next review question.

This is the core proposed CrimeKit differentiator.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `FINAL INNOVATION TARGET` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 229. HANDOFF

Prepare Prompt #6 — GRAPH API with:
schema
projection events
GraphIntent contract
projection version
case isolation
provenance
reconciliation
3D DTO
realtime events
MCP developer workflow.

Do not move forward with visual polish while projection correctness remains unresolved.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `HANDOFF` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

## 230. OFFICIAL REFERENCES

Use current official documentation when implementation details may have changed:
Neo4j MCP introduction: https://neo4j.com/docs/mcp/current/
Neo4j MCP tools: https://neo4j.com/docs/mcp/current/tools/
Neo4j MCP quickstart: https://neo4j.com/docs/mcp/current/quickstart/
Neo4j MCP installation: https://neo4j.com/docs/mcp/current/installation/
Neo4j MCP configuration: https://neo4j.com/docs/mcp/current/configuration/
Neo4j MCP GitHub: https://github.com/neo4j/mcp
Google developer MCP/Antigravity guidance: https://developers.google.com/knowledge/mcp

The current Neo4j MCP docs state that the official server provides get-schema, read-cypher, write-cypher, and list-gds-procedures; readonly mode uses NEO4J_READ_ONLY=true and removes write tools. The current Aura quickstart documents the instance-specific mcp-instances.neo4j.io URL pattern and Tool authentication flow. Verify the exact client syntax against the installed Antigravity version before editing configuration.

### Required engineering behavior

- Determine whether this is already implemented before creating code.
- Prefer the current repository architecture over stale plans.
- Record actual repository paths, actual schema, and actual runtime behavior.
- Separate implemented, partial, planned, and proposed behavior.

### Acceptance

- The `OFFICIAL REFERENCES` capability is not considered complete until it is demonstrated with repository evidence, tests, or a concrete verified runtime check.

---

# APPENDIX A — RECOMMENDED EVENT TYPES

Use only event types actually present in CrimeKit; this is a candidate taxonomy for mapping and gap analysis.

```text
CASE_CREATED
INVESTIGATION_CREATED
EVIDENCE_REGISTERED
EVIDENCE_METADATA_UPDATED
ARTIFACT_CREATED
ARTIFACT_EXTRACTED
PROCESSING_RUN_STARTED
PROCESSING_RUN_COMPLETED
PROCESSING_RUN_FAILED
ENTITY_CREATED
ENTITY_RESOLUTION_CANDIDATE_CREATED
ENTITY_RESOLUTION_VERIFIED
OBSERVATION_CREATED
TIMELINE_EVENT_CREATED
COMMUNICATION_EVENT_CREATED
LOCATION_EVENT_CREATED
RELATIONSHIP_ASSERTED
RELATIONSHIP_VERIFIED
RELATIONSHIP_DISPUTED
FACE_CANDIDATE_CREATED
FACE_REVIEWED
REPORT_GENERATED
```

# APPENDIX B — GRAPH INTENT EXAMPLE

```json
{
  "operation": "UPSERT_RELATIONSHIP",
  "relationship_type": "USES",
  "source_id": "P001",
  "target_id": "D001",
  "case_id": "CASE-TEST-001",
  "source_event_id": "EVT-123",
  "projection_version": "crimekit-graph-1.0",
  "provenance": {
    "evidence_id": "E-44",
    "artifact_id": "A-91",
    "processing_run_id": "PR-12"
  }
}
```

# APPENDIX C — SAFE CYPHER PATTERNS

Use parameterized queries. Adapt syntax to the actual Neo4j version.

```cypher
MATCH (p:Person {person_id: $person_id, case_id: $case_id})
RETURN p
LIMIT 1
```

```cypher
MATCH (n {case_id: $case_id})
RETURN labels(n) AS labels, count(*) AS count
ORDER BY count DESC
LIMIT $limit
```

```cypher
MATCH (a {id: $source_id, case_id: $case_id})
MATCH (b {id: $target_id, case_id: $case_id})
MERGE (a)-[r:USES {relationship_id: $relationship_id}]->(b)
SET r.source_event_id = $source_event_id,
    r.projection_version = $projection_version
RETURN r
```

# APPENDIX D — PROJECTION HANDLER TEMPLATE

```text
Rule ID:
Event Type:
Event Version:
Source Fields:
Validation:
Normalization:
Identity Resolution:
Temporal Semantics:
GraphIntents:
Cypher Strategy:
Provenance:
Idempotency:
Ordering:
Retryable Errors:
Permanent Errors:
Metrics:
Tests:
Projection Version:
```

# APPENDIX E — MCP VERIFICATION PROMPT FOR ANTIGRAVITY

Paste a variant of the following into the developer agent only after confirming the target environment:

```text
You are operating on the CrimeKit DEVELOPMENT Neo4j instance.
First use the Neo4j MCP schema tool and summarize labels, relationship types, and important property keys.
Then run one bounded read query against the synthetic CASE-TEST-001.
Validate that evidence, artifact, observation, and relationship provenance exists where expected.
Then list available GDS procedures if that MCP tool is present.
Do not perform any write, schema, delete, or administrative operation.
Report findings, anomalies, and recommended engineering changes.
```

# APPENDIX F — DEVELOPER MCP GUARDRAIL

```text
Environment: DEV/STAGING
Default mode: READ ONLY
Target database: explicit
Scope: bounded
No raw evidence dump
No unrestricted traversal
No production write
No credentials in repository
Human approval for exceptional writes
```

# APPENDIX G — MINIMUM GRAPH API CONTRACT

```text
GET  /api/cases/{case_id}/graph/overview
GET  /api/cases/{case_id}/graph/entities/{entity_id}/neighbors
POST /api/cases/{case_id}/graph/path
GET  /api/cases/{case_id}/graph/timeline
GET  /api/cases/{case_id}/graph/provenance/{relationship_id}
GET  /api/cases/{case_id}/graph/diff
```

Use only endpoints consistent with the existing CrimeKit API. Do not duplicate routes that already exist under different names.

# APPENDIX H — FINAL IMPLEMENTATION REPORT

Return a final report with:

```text
1. Existing architecture discovered
2. Existing graph writer discovered
3. Event source discovered
4. Projection rules discovered
5. Schema state
6. Idempotency implementation
7. Ordering implementation
8. Retry/DLQ state
9. Reconciliation state
10. Rebuild/replay state
11. Graph API state
12. Realtime state
13. 3D readiness
14. AI integration state
15. MCP/Antigravity state
16. Security findings
17. Performance findings
18. Tests executed
19. Remaining risks
20. Production readiness decision
```

# FINAL DIRECTIVE

> **Do not build a graph that merely looks connected. Build a projection system in which every important relationship has a legitimate source, every projection is reproducible, every query is bounded, every case boundary is enforced, every developer connection targets the correct environment, every MCP capability is governed, every visual relationship maps to structured data, and the complete graph can be regenerated from authoritative CrimeKit data.**

## End — Prompt #5
