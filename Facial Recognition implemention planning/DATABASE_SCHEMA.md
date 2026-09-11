# CRIMEKIT — FACE TRACE INVESTIGATOR
# DATABASE SCHEMA SPECIFICATION

**Document:** `DATABASE_SCHEMA.md`  
**Subsystem:** Face Trace Investigator  
**Scope:** PostgreSQL domain schema, pgvector storage, Neo4j projection, indexes, constraints, provenance relationships, lifecycle, migrations, retention, integrity validation  
**Primary concern:** Store face-trace intelligence as traceable, case-scoped, versioned derived data without weakening the authoritative CrimeKit evidence model  
**Audience:** Backend engineers, database engineers, forensic engineers, ML engineers, infrastructure, security, QA  
**Status:** Authoritative database specification

---

# 1. PURPOSE

This document defines the persistence model for Face Trace Investigator.

The database must preserve the distinction between:

    Evidence
       ↓
    Processing
       ↓
    Machine Observation
       ↓
    Candidate
       ↓
    Sighting
       ↓
    Human Review

The relational database should remain the authoritative domain store according to the CrimeKit architecture.

pgvector supports retrieval.

Neo4j supports relationship projection.

Neither should silently replace the relational forensic record.

---

# 2. STORAGE RESPONSIBILITIES

Recommended responsibilities:

    PostgreSQL
        authoritative structured domain state

    pgvector
        embedding retrieval/indexing

    Neo4j
        graph projection/correlation

    Object Storage
        source/derived media

    Redis
        transient coordination/cache/queue support

---

# 3. SOURCE-OF-TRUTH RULE

The database design must not create a second independent evidence-management system.

Face Trace references existing:

    case
    investigation
    evidence
    artifact

records where those domain records already exist.

---

# 4. CORE DOMAIN MODEL

Conceptual hierarchy:

    Case
      └── Investigation
            ├── Face Reference
            └── Face Search
                  └── Processing Run
                        ├── Source
                        │    └── Frame
                        │         └── Detection
                        │              └── Track
                        │                   └── Embedding
                        │                        └── Candidate
                        │                             └── Sighting
                        │                                  └── Review

The exact physical schema may use normalized references and separate tables.

---

# 5. ENTITY CATEGORIES

Recommended categories:

## 5.1 Control entities

    face_search
    processing_run
    matching_policy
    model_registry/context

## 5.2 Observation entities

    face_frame
    face_detection
    face_track
    face_embedding
    face_candidate

## 5.3 Investigation entities

    face_reference
    face_sighting
    face_review

## 5.4 Projection/operational entities

    event_outbox
    graph_projection_state
    vector_projection_state

Only add entities actually required by the implementation.

---

# 6. NAMING PRINCIPLE

Use the existing CrimeKit database naming convention.

Do not introduce a different naming style only for Face Trace.

Recommended examples:

    face_searches
    face_references
    face_processing_runs
    face_detections
    face_tracks
    face_embeddings
    face_candidates
    face_sightings
    face_reviews

Actual names must match the existing codebase.

---

# 7. ID STRATEGY

Every major domain entity needs a stable identifier.

Examples:

    search_id
    reference_id
    processing_run_id
    detection_id
    track_id
    embedding_id
    candidate_id
    sighting_id
    review_id

Do not expose database-specific row identifiers as domain identity if CrimeKit uses opaque IDs.

---

# 8. CASE SCOPE

Sensitive Face Trace records should contain or resolve to:

    case_id

through authoritative parent relationships.

This enables:

    authorization
    indexing
    isolation
    audit
    retention

---

# 9. INVESTIGATION SCOPE

Investigation-level entities should retain:

    investigation_id

This prevents accidental case-wide access where narrower scope is intended.

---

# 10. FACE SEARCH

Conceptual fields:

    id
    investigation_id
    reference_id
    status
    policy_id
    policy_version
    requested_by
    created_at
    started_at
    completed_at
    error_code
    error_summary

---

# 11. FACE SEARCH RESPONSIBILITY

`face_search` represents the investigator's logical request.

It is not the same thing as:

    processing_run

because one logical search can have operational execution context.

---

# 12. FACE REFERENCE

Conceptual fields:

    id
    investigation_id
    source_artifact_id
    selected_face_id/selection metadata
    quality_state
    processing_run_id
    model_id
    model_version
    preprocessing_version
    created_by
    created_at

---

# 13. REFERENCE EMBEDDING

A reference should link to its embedding through an explicit relationship.

Do not hide reference identity inside vector metadata alone.

---

# 14. PROCESSING RUN

Conceptual fields:

    id
    search_id
    investigation_id
    source_scope
    status
    model_id
    model_version
    detector_version
    tracker_version
    preprocessing_version
    matching_policy_id
    matching_policy_version
    sampling_policy
    runtime_context
    started_at
    completed_at

---

# 15. PROCESSING RUN PURPOSE

The run is the reproducibility boundary.

A historical result must be attributable to the run that created it.

---

# 16. PROCESSING RUN VERSIONING

Do not update historical processing-run context merely because the deployment changes.

Create a new run for materially different processing.

---

# 17. MATCHING POLICY

A policy entity/configuration should capture:

    policy_id
    version
    metric
    threshold
    top_k
    quality requirements
    aggregation configuration
    effective metadata

Only fields actually used should be persisted.

---

# 18. POLICY IMMUTABILITY

After a production run uses a policy version, its historical interpretation must remain stable.

Prefer immutable versioned policy records.

---

# 19. MODEL CONTEXT

Model metadata may be stored in a registry/configuration layer.

Each face result should retain enough information to identify:

    provider
    model
    version
    embedding dimension

---

# 20. MODEL REGISTRY RESPONSIBILITY

The model registry identifies approved runtime artifacts.

It should not become the source of:

    candidate identity
    investigator review
    evidence

---

# 21. SOURCE RECORD

Face Trace should reference the existing evidence/artifact system.

Conceptually:

    face processing record
       ↓
    source artifact ID

Do not duplicate the original artifact record.

---

# 22. SOURCE ID

Where a source abstraction exists:

    source_id

may represent:

    CCTV camera
    uploaded video artifact
    image source

The exact source entity follows CrimeKit design.

---

# 23. FRAME RECORD

A retained source frame may contain:

    id
    processing_run_id
    artifact_id
    source_id
    frame_number
    source_timestamp
    width
    height
    frame_reference
    frame_hash where applicable
    created_at

Do not persist every frame unless required.

---

# 24. FRAME RETENTION

Frame persistence should follow the forensic/provenance policy.

Internal temporary frames may remain outside PostgreSQL.

Retained frames must remain traceable.

---

# 25. DETECTION TABLE

Conceptual fields:

    id
    frame_id
    processing_run_id
    bbox
    detector_score
    quality_state
    quality_metadata
    created_at

---

# 26. DETECTION SOURCE RELATIONSHIP

Every retained detection should resolve to:

    frame
       ↓
    artifact
       ↓
    evidence

---

# 27. BBOX STORAGE

Use a consistent representation.

Possible:

    x
    y
    width
    height

or a structured JSON object if the existing schema uses JSON.

Do not mix coordinate conventions.

---

# 28. BBOX COORDINATE SYSTEM

Record/define whether coordinates are:

    absolute pixel coordinates

or:

    normalized coordinates

The frontend and APIs must interpret them consistently.

---

# 29. QUALITY METADATA

If quality metadata is persisted, store only useful structured information.

Potential:

    face_size
    blur_score
    pose
    occlusion_state

Do not invent unused fields solely for documentation completeness.

---

# 30. QUALITY POLICY VERSION

Where quality rules can change, retain the relevant policy/version context.

---

# 31. TRACK TABLE

Conceptual fields:

    id
    processing_run_id
    source_id
    first_frame_id
    last_frame_id
    first_seen_at
    last_seen_at
    tracker_version
    status
    created_at
    closed_at

---

# 32. TRACK-DETECTION RELATIONSHIP

A track contains/links to detections.

Depending on expected scale, use a join table:

    face_track_detections

instead of storing a huge detection-ID array.

---

# 33. TRACK JOIN TABLE

Conceptual:

    track_id
    detection_id
    sequence_number

Useful indexes:

    track_id
    detection_id

---

# 34. TRACK NAMESPACE

Track identity is source/run scoped.

Do not assume:

    TRACK-12

is globally unique across all sources and processing runs.

---

# 35. EMBEDDING TABLE

Conceptual fields:

    id
    detection_id or observation_id
    track_id where applicable
    processing_run_id
    model_id
    model_version
    embedding_dimension
    vector
    normalization_scheme
    created_at
    retention_state

---

# 36. VECTOR COLUMN

Use pgvector only where the PostgreSQL deployment supports the extension and approved schema.

The vector column should have the known dimensionality expected by the selected model family.

---

# 37. VECTOR DIMENSION

Do not accept arbitrary vector dimensions into one index.

Model compatibility is part of the schema contract.

---

# 38. MULTI-MODEL STORAGE

If multiple models are supported:

    model_id/model_version

must distinguish their vectors.

Do not mix incompatible embeddings into one generic index without explicit architecture.

---

# 39. VECTOR INDEX STRATEGY

Select the pgvector index strategy based on actual:

    corpus size
    query pattern
    dimensionality
    supported deployment

Do not hard-code an index type simply because it is popular.

---

# 40. VECTOR INDEX FILTERING

Where supported, combine vector retrieval with metadata filtering such as:

    case_id
    investigation_id
    model_id
    retention state
    source scope

---

# 41. VECTOR SECURITY

Do not depend on UI filtering to protect the vector corpus.

Server-side/database-level restrictions are required.

---

# 42. CASE-SCOPED VECTOR ACCESS

Every query must enforce the authorized case/investigation scope before candidate exposure.

---

# 43. VECTOR RETENTION

Expired embeddings must not remain searchable.

Retention state must participate in retrieval policy.

---

# 44. EMBEDDING PRIVACY

Treat embeddings as sensitive biometric-derived data.

Do not expose raw vector values through normal APIs.

---

# 45. EMBEDDING PROVENANCE

Every persisted embedding must resolve to:

    source observation
    model context
    processing run

---

# 46. FACE CANDIDATE

Conceptual fields:

    id
    search_id
    processing_run_id
    reference_embedding_id
    candidate_embedding_id
    source_id
    evidence_id
    artifact_id
    detection_id
    track_id
    similarity
    metric
    rank
    quality_state
    policy_id
    policy_version
    review_state
    created_at

---

# 47. CANDIDATE CONSTRAINT

A candidate cannot exist without a valid processing/search context.

Use foreign-key constraints where practical.

---

# 48. CANDIDATE SCORE

Store the machine-derived similarity score separately from:

    review decision
    candidate tier
    human notes

---

# 49. SCORE SEMANTICS

Field:

    similarity

means the defined similarity metric.

It does not mean:

    probability
    accuracy
    certainty

---

# 50. CANDIDATE METRIC

Persist the metric where historical interpretation requires it.

Example:

    cosine

---

# 51. CANDIDATE RANK

Rank is context-specific.

A rank of 1 means:

    top-ranked within that retrieval/evaluation context

not:

    confirmed identity.

---

# 52. CANDIDATE OBSERVATION

If the architecture distinguishes:

    candidate observation

from:

    aggregated candidate/sighting

use separate domain records.

This is preferable when one sighting contains many observations.

---

# 53. SIGHTING TABLE

Conceptual fields:

    id
    search_id
    investigation_id
    source_id
    track_id
    first_observed_at
    last_observed_at
    best_candidate_id
    observation_count
    review_state
    created_at
    updated_at

---

# 54. SIGHTING PURPOSE

Sighting is the investigator-friendly aggregate of candidate observations.

It reduces duplicate alerts while retaining underlying evidence lineage.

---

# 55. SIGHTING OBSERVATIONS

If many observations can belong to a sighting, use a relation:

    sighting_id
    candidate_id
    sequence/order metadata

rather than embedding a potentially unbounded candidate array.

---

# 56. SIGHTING SOURCE CONSISTENCY

A sighting should normally belong to one source/track context.

Cross-camera correlation should be represented separately.

---

# 57. CROSS-CAMERA CORRELATION

If implemented, introduce a separate correlation domain instead of changing the meaning of `face_sightings`.

Example concept:

    face_trace_correlation
       ├── sighting A
       └── sighting B

---

# 58. REVIEW TABLE

Conceptual fields:

    id
    sighting_id
    reviewer_id
    decision
    notes
    previous_state
    new_state
    created_at

---

# 59. REVIEW IMMUTABILITY

Review history should not overwrite prior decisions when audit requirements require historical records.

---

# 60. CURRENT REVIEW STATE

A convenient current state may exist on `face_sightings`.

Historical transitions remain in `face_reviews`.

---

# 61. REVIEW CONCURRENCY

Use optimistic concurrency/version checks if multiple investigators can edit the same sighting.

---

# 62. AUDIT RELATIONSHIP

Face Trace should use the existing CrimeKit audit system where available.

Do not create a competing generic audit framework.

---

# 63. EVENT OUTBOX

If the architecture uses an outbox:

    face result transaction
       ↓
    domain state
       +
    event_outbox record

This prevents durable state from being lost merely because event publication fails.

---

# 64. OUTBOX FIELDS

Potential:

    event_id
    event_type
    aggregate_type
    aggregate_id
    case_id
    investigation_id
    payload
    created_at
    published_at
    retry_count
    status

Only fields supported by the actual event architecture should be used.

---

# 65. OUTBOX SECURITY

Do not place:

    raw embeddings
    credentials
    full biometric image bytes

inside event payloads.

---

# 66. GRAPH PROJECTION STATE

If Neo4j projection state is tracked relationally, use:

    domain_object_id
    projection_version
    status
    last_projected_at
    error_code

---

# 67. GRAPH AS PROJECTION

Neo4j nodes/edges should be reconstructable from authoritative domain state where practical.

---

# 68. GRAPH NODE IDENTITY

Use stable CrimeKit domain IDs.

Example:

    SIGHT-001

The graph should reference the domain identity rather than create an unrelated ID.

---

# 69. GRAPH EDGES

Potential relationships:

    Sighting → OBSERVED_IN → Evidence
    Sighting → ON_TRACK → Track
    Candidate → FROM → Detection
    Detection → IN_FRAME → Frame

The exact graph model follows CrimeKit knowledge-graph conventions.

---

# 70. VECTOR PROJECTION STATE

Where embedding insertion/indexing is asynchronous:

    embedding domain record

can be authoritative while:

    vector_projection_status

is tracked separately.

---

# 71. PROJECTION FAILURE

A failed graph/vector projection must not delete or invalidate the source relational record.

---

# 72. DATABASE NORMALIZATION

Normalize stable relationships.

Avoid large unbounded JSON blobs for core lineage.

JSON may be used for:

    flexible metadata
    model-specific fields
    runtime context

where justified.

---

# 73. JSON USAGE

Do not put critical foreign-key relationships only inside JSON.

---

# 74. FOREIGN KEYS

Use foreign keys for critical relationships where transaction/scale architecture permits.

Potential:

    candidate → search
    candidate → processing_run
    candidate → detection
    candidate → track
    sighting → search
    sighting → track
    review → sighting

---

# 75. FOREIGN KEY DELETE POLICY

Do not use cascading deletion casually on forensic records.

Deletion must follow evidence/retention policy.

---

# 76. SOFT DELETE

If CrimeKit uses soft deletion, follow the existing convention.

Do not create a Face Trace-specific deletion semantic unless required.

---

# 77. UNIQUE CONSTRAINTS

Potential uniqueness candidates:

    domain_id
    event_id
    policy_id + version
    model_id + version

Actual constraints depend on repository conventions.

---

# 78. IDEMPOTENCY KEY

Search/job creation may persist:

    idempotency_key

under the appropriate requester/scope to prevent accidental duplicate jobs.

---

# 79. IDEMPOTENCY CONSTRAINT

If idempotency is promised, enforce uniqueness appropriately.

Do not rely only on application-memory checks.

---

# 80. INDEX — CASE

Index sensitive records by:

    case_id

where frequently filtered.

---

# 81. INDEX — INVESTIGATION

Index:

    investigation_id

on search/reference/candidate/sighting records.

---

# 82. INDEX — PROCESSING RUN

Index:

    processing_run_id

for lineage traversal and operational queries.

---

# 83. INDEX — SOURCE

Index:

    source_id

for camera/source filtering.

---

# 84. INDEX — TIMESTAMP

Index source observation time where the UI/API uses time-range searches.

---

# 85. INDEX — REVIEW STATE

Index:

    review_state

when investigator queues depend on it.

---

# 86. INDEX — CANDIDATE RANK

Index only if actual list/ranking queries benefit from it.

---

# 87. COMPOSITE INDEXES

Potential combinations:

    investigation_id + created_at
    investigation_id + source_id + first_observed_at
    search_id + review_state
    processing_run_id + source_id

Use query-plan evidence before adding many indexes.

---

# 88. VECTOR INDEX

Vector index should be designed separately from relational indexing.

Benchmark actual query performance.

---

# 89. INDEX WRITE COST

Every index increases write overhead.

Do not create indexes solely because fields exist.

---

# 90. PARTITIONING

Large-scale face observation tables may eventually require partitioning.

Potential partition keys:

    case
    time
    processing run

Do not partition prematurely.

---

# 91. MULTI-TENANT MODEL

If CrimeKit is multi-tenant:

    tenant_id

must participate in appropriate authorization/indexing policies.

---

# 92. TENANT ISOLATION

Tenant scope must not be inferred from:

    UI
    graph
    vector index

alone.

Server/database policies must enforce it.

---

# 93. ROW-LEVEL SECURITY

If CrimeKit uses PostgreSQL RLS:

    integrate Face Trace tables into the established RLS model.

Do not create bypass roles for normal application access.

---

# 94. SERVICE ROLES

Worker roles should receive minimum required database permissions.

---

# 95. READ ROLES

Reporting/analytics roles should not automatically receive:

    raw embeddings
    unrestricted biometric tables

---

# 96. ADMIN ACCESS

Administrative database access remains separate from investigator access.

---

# 97. VECTOR ACCESS ROLE

Only authorized services should directly query biometric vector tables/indexes.

---

# 98. DATABASE ENCRYPTION

Use approved encryption at rest and transport.

Do not rely on application-level redaction alone.

---

# 99. CONNECTION SECURITY

Database connections must use approved secure transport/configuration.

---

# 100. SECRET STORAGE

Database credentials belong in approved secret management.

Never in:

    Git
    frontend
    migration files
    logs

---

# 101. MIGRATION STRATEGY

Database changes must be versioned through the project's established migration tool.

Do not manually modify production schemas outside the migration process except under documented emergency procedure.

---

# 102. MIGRATION ORDER

Recommended conceptual order:

    base extension/configuration
       ↓
    policy/model metadata
       ↓
    references/searches/runs
       ↓
    frames/detections/tracks
       ↓
    embeddings
       ↓
    candidates
       ↓
    sightings/reviews
       ↓
    projection/event support

---

# 103. EXTENSION MIGRATION

If pgvector is not already provisioned:

    enable extension through approved infrastructure/migration process.

Do not assume extension availability.

---

# 104. MIGRATION SAFETY

Large production migrations should consider:

    lock duration
    index creation strategy
    backfill cost
    rollback implications

---

# 105. NON-BLOCKING INDEX BUILD

Where supported and appropriate, use safe production index-building techniques.

Do not blindly run heavy index creation inside a transaction if the database/version/tooling does not support it.

---

# 106. BACKFILL

When adding fields to existing data:

    backfill deterministically

and validate before making assumptions about completeness.

---

# 107. NULL TRANSITION

New provenance fields may initially require:

    nullable
       ↓
    backfill
       ↓
    validate
       ↓
    non-null

where appropriate.

---

# 108. SCHEMA COMPATIBILITY

Deploy database changes in an order compatible with:

    old application
    new application

during rolling deployments.

---

# 109. MIGRATION ROLLBACK

Rollback strategy must account for data already written using the new schema.

Do not assume every migration can simply be reversed.

---

# 110. MODEL CHANGE

Model changes normally do not require replacing historical embedding records.

They create new processing/model context.

---

# 111. POLICY CHANGE

Policy versioning should not mutate historical policy metadata.

---

# 112. REPROCESSING DATA

New runs produce new observations/candidates.

Old run data remains historically attributable according to retention policy.

---

# 113. DUPLICATE PROCESSING

Unique logical job constraints/idempotency should prevent accidental duplication where required.

---

# 114. SIGHTING UPSERT

Sighting aggregation may need controlled upsert logic.

Ensure concurrent workers cannot create duplicate sightings unintentionally.

---

# 115. CONCURRENCY CONTROL

Use:

    unique constraints
    row locking
    optimistic versioning

as appropriate.

---

# 116. RACE CONDITION

Two frames arriving concurrently for the same track must not create inconsistent sighting state.

---

# 117. ATOMIC SIGHTING UPDATE

Where needed, update:

    last_observed_at
    best_candidate
    observation_count
    updated_at

atomically.

---

# 118. CANDIDATE INSERT CONCURRENCY

Concurrent workers may create observations for different frames.

Use stable source/track/run relationships and idempotency where required.

---

# 119. DATABASE TRANSACTION

A critical candidate transaction should persist enough context to avoid:

    candidate without processing run
    sighting without candidate

where the domain requires immediate consistency.

---

# 120. ASYNC PROJECTIONS

Graph/vector/event projection can remain asynchronous if:

    relational record is authoritative
    projection status is visible/observable

---

# 121. CONSISTENCY MODEL

Use:

    strong consistency

for core relational forensic relationships where required.

Use:

    eventual consistency

for:

    graph projection
    realtime delivery
    optional vector indexing

where appropriate.

---

# 122. EVENTUAL CONSISTENCY UX

Frontend may show:

    "Graph syncing"
    "Indexing"

rather than hiding the delay.

---

# 123. DATABASE TRANSACTION + OUTBOX

Preferred:

    BEGIN
       write candidate/sighting
       write event_outbox
    COMMIT

Then:

    publisher → event bus

This keeps domain state and event intent durable.

---

# 124. VECTOR TRANSACTION

If vector insertion cannot share the same transaction as PostgreSQL domain records:

    use projection state/idempotency

rather than pretending both are atomic.

---

# 125. GRAPH TRANSACTION

Same principle applies to Neo4j.

---

# 126. REBUILDABILITY

Where practical:

    Neo4j
    vector index

should be rebuildable from authoritative stored data/configuration.

---

# 127. REBUILD TEST

Test:

    delete projection
       ↓
    rebuild
       ↓
    compare

Expected:

    domain-equivalent result

---

# 128. ORPHAN DETECTION

Periodic integrity checks should identify:

    orphan detection
    orphan embedding
    orphan candidate
    orphan sighting
    orphan projection

---

# 129. INTEGRITY CONSTRAINT

An accepted candidate should resolve to a valid:

    processing run
    source
    observation
    model
    policy

---

# 130. TIMESTAMP INTEGRITY

Validate:

    first_observed_at ≤ last_observed_at

where both exist.

---

# 131. FRAME INTEGRITY

Validate:

    bbox within valid frame dimensions

according to coordinate policy.

---

# 132. TRACK INTEGRITY

Validate:

    first_seen_at ≤ last_seen_at

and linked detection timestamps are consistent where applicable.

---

# 133. SIGHTING INTEGRITY

Validate:

    observation_count

matches authoritative association data if maintained transactionally.

---

# 134. REVIEW INTEGRITY

Review must resolve to an existing sighting.

---

# 135. POLICY INTEGRITY

Candidate policy/version must resolve to the policy context actually used.

---

# 136. MODEL INTEGRITY

Embedding model/version metadata must resolve to approved/known model context.

---

# 137. VECTOR INTEGRITY

Embedding dimension must equal model-context dimension.

---

# 138. RETENTION INTEGRITY

Expired embeddings must not remain active in retrieval indexes.

---

# 139. CASE ISOLATION INTEGRITY

Candidate references must not cross case scope unexpectedly.

---

# 140. INVESTIGATION ISOLATION INTEGRITY

Investigation-level references must remain in the correct investigation scope.

---

# 141. DATA CLASSIFICATION

Recommended classification:

    Case metadata → sensitive
    Evidence metadata → sensitive
    Face image → highly sensitive
    Face embedding → highly sensitive biometric-derived
    Candidate metadata → sensitive
    Review record → sensitive

Follow CrimeKit's actual data-classification policy.

---

# 142. RETENTION TABLE

Retention should define separately:

    source evidence
    reference image
    reference embedding
    candidate embedding
    detection
    track
    candidate
    sighting
    review

Do not apply one global retention number without policy support.

---

# 143. EMBEDDING DELETE

When a biometric artifact must be deleted/expired:

    prevent future vector retrieval
    remove/expire projection
    handle dependent records
    preserve required audit metadata

according to policy.

---

# 144. SOURCE DELETE

Deletion of source evidence must follow the core evidence/retention system.

Face Trace must respond appropriately.

---

# 145. DERIVED DELETE

Derived crops/temporary frames can be deleted independently only when doing so does not violate provenance or preservation requirements.

---

# 146. LEGAL HOLD

If an investigation/evidence is on legal hold:

    retention workflows must honor the hold.

---

# 147. BACKUP

Database backups containing Face Trace data are sensitive.

Apply the same protection as production data.

---

# 148. RESTORE

Restore testing must verify:

    domain references
    vector availability
    graph rebuild/projection
    event state

---

# 149. BACKUP ENCRYPTION

Use approved encrypted backup storage.

---

# 150. DATABASE OBSERVABILITY

Monitor:

    connections
    query latency
    slow queries
    locks
    deadlocks
    vector query latency
    storage growth
    index health

---

# 151. BIOMETRIC TABLE MONITORING

Monitor table growth without exposing actual biometric content.

---

# 152. SLOW QUERY MONITORING

Investigate expensive queries involving:

    candidate lists
    provenance
    time ranges
    vector search

---

# 153. LOCK MONITORING

Long migrations/transactions must not block investigators indefinitely.

---

# 154. VACUUM/MAINTENANCE

PostgreSQL maintenance should account for:

    high-write observation tables
    vector tables
    indexes

Follow database operations standards.

---

# 155. PARTITION MAINTENANCE

If partitioning is later introduced:

    define retention
    vacuum
    index
    archival

per partition.

---

# 156. DATA GROWTH ESTIMATION

Before production rollout, estimate:

    frames retained
    detections per frame
    tracks
    embeddings
    candidates
    sightings

Use actual deployment assumptions.

---

# 157. DO NOT STORE EVERYTHING BY DEFAULT

Storing:

    every frame
    every crop
    every embedding

may create unnecessary storage and privacy cost.

Retention must be purpose-driven.

---

# 158. HIGH-VOLUME TABLE DESIGN

For high-volume observations:

    minimize row size
    avoid excessive JSON
    index selectively
    batch writes
    archive according to policy

---

# 159. CANDIDATE TABLE VOLUME

Candidates should normally be much smaller than raw detections/embeddings if policy filtering is functioning.

---

# 160. SIGHTING TABLE VOLUME

Sighting aggregation is expected to reduce UI-level result volume.

---

# 161. QUERY PATTERN — INVESTIGATOR QUEUE

Common query:

    investigation
      +
    review_state = REVIEW_PENDING
      +
    newest/high-priority

Ensure this path is indexed.

---

# 162. QUERY PATTERN — TIMELINE

Common:

    investigation
      +
    source
      +
    source timestamp range

Index accordingly.

---

# 163. QUERY PATTERN — PROVENANCE

Common:

    sighting
       ↓
    candidate
       ↓
    track/detection
       ↓
    frame
       ↓
    processing run

Foreign keys and indexes should support this traversal.

---

# 164. QUERY PATTERN — SOURCE FILTER

Investigators may ask:

    show sightings from CAM-02 between time A and B

Optimize this deliberately.

---

# 165. QUERY PATTERN — REVIEW

Investigator queue:

    all pending sightings

should use appropriate composite indexes.

---

# 166. QUERY PATTERN — SEARCH

Search detail:

    source statuses
    progress
    candidate counts
    sighting counts

should not scan raw embeddings unnecessarily.

---

# 167. VECTOR QUERY PATH

Typical:

    reference vector
       ↓
    authorized filtered vector search
       ↓
    top-K
       ↓
    candidate metadata join

Avoid large unnecessary joins before vector retrieval where possible.

---

# 168. VECTOR RESULT JOIN

Retrieved vector rows should resolve efficiently to the source observation/domain record.

---

# 169. VECTOR INDEX HEALTH

Monitor index/query performance after:

    large ingestion
    rebuild
    migration
    model expansion

---

# 170. MULTI-MODEL VECTOR STRATEGY

If several models are active:

    separate indexes
    or metadata-compatible strategy

must prevent incompatible retrieval.

---

# 171. MODEL DIMENSION MIGRATION

A new embedding dimension may require:

    new vector column/index
    new model-specific table
    or other explicitly designed migration

Do not change vector dimension in place blindly.

---

# 172. VECTOR TYPE SAFETY

Database/application validation must reject:

    wrong dimension
    NaN
    invalid numeric values

where applicable.

---

# 173. PII MINIMIZATION

Database should store:

    minimum personal metadata necessary

Face Trace should not create an independent large identity registry merely for matching.

---

# 174. PERSON ENTITY LINK

If a later reviewed identity is linked to an existing CrimeKit entity:

    retain candidate/sighting provenance.

Do not replace candidate IDs with person IDs.

---

# 175. REVIEWED IDENTITY

A reviewed identity link is a higher-level relationship.

It must remain distinguishable from:

    raw machine candidate.

---

# 176. GRAPHENTITY LINK

Neo4j can represent:

    Sighting → possibly_related_to → Person/Entity

only under the authorized reviewed/domain semantics.

---

# 177. NO AUTOMATIC PERSON CREATION

A machine candidate should not automatically create a confirmed person identity.

---

# 178. SCHEMA AND AI AGENTS

AI agents should query controlled APIs/domain services.

Do not grant direct unrestricted database access to an agent.

---

# 179. AI PROVENANCE

Agent-generated conclusions should reference:

    candidate/sighting IDs

rather than copying all biometric/raw fields.

---

# 180. REPORTING VIEWS

If reporting views are created:

    minimize sensitive fields
    preserve source references
    preserve review state

---

# 181. ANALYTICS

Aggregated operational analytics should not expose individual biometric content.

---

# 182. DATABASE TEST DATABASE

Automated tests should use isolated database schemas/containers.

---

# 183. TEST VECTOR DATA

Use non-sensitive synthetic/approved test embeddings.

---

# 184. TEST CASE ISOLATION

Each test should use unique case/investigation IDs where possible.

---

# 185. MIGRATION TEST

Every migration should run against:

    empty schema
    representative existing schema

where CI policy permits.

---

# 186. DOWN-MIGRATION

Down migrations should be used only where safe and meaningful.

Do not automatically provide destructive rollback if it risks data loss.

---

# 187. SCHEMA DIFF

CI should detect unintended:

    table drops
    column drops
    constraint removal
    index changes

according to project database governance.

---

# 188. PERFORMANCE MIGRATION TEST

For large tables, validate migration time and locking behavior against representative data volume.

---

# 189. SEED DATA

Development seed data must be clearly labeled:

    DEMO/TEST

and must not look like real case evidence.

---

# 190. DEVELOPMENT ENVIRONMENT

Development database should not contain production biometric data.

---

# 191. STAGING ENVIRONMENT

Staging should use:

    synthetic
    controlled
    approved

data according to security policy.

---

# 192. PRODUCTION ACCESS

Only authorized production services/users can query biometric records.

---

# 193. DATABASE AUDIT

Database-level sensitive operations should be auditable where required.

---

# 194. EXPORT CONTROL

Database dumps containing Face Trace data are highly sensitive.

Do not casually export them.

---

# 195. DEBUG DATABASE ACCESS

Developers should not gain unrestricted production biometric access merely for debugging.

Use controlled diagnostics.

---

# 196. DATA MASKING

Non-production copies must mask/remove sensitive biometric content unless explicitly approved.

---

# 197. MIGRATION DATA MASKING

Any migration test fixture with biometric metadata should be synthetic or approved.

---

# 198. DATABASE SCHEMA DOCUMENTATION

Keep schema documentation aligned with:

    migrations
    ORM models
    API schemas

The migration is the executable source of schema truth.

---

# 199. ORM BOUNDARY

ORM models should represent domain relationships.

Do not make ORM design force poor forensic semantics.

---

# 200. REPOSITORY BOUNDARY

Create repositories for:

    searches
    references
    candidates
    sightings
    reviews
    embeddings

as appropriate.

---

# 201. DIRECT SQL

Performance-sensitive vector queries may use carefully reviewed SQL if required.

Do not scatter raw SQL throughout the application.

---

# 202. TRANSACTION BOUNDARY

Service layer should determine transaction boundaries.

Repositories should not silently commit partial forensic state in ways the caller cannot control.

---

# 203. DATABASE ERROR TRANSLATION

Translate:

    foreign key violation
    unique conflict
    connection failure
    timeout

into safe domain/application errors.

---

# 204. DEADLOCK RETRY

Retry database deadlocks only where operation is safe/idempotent.

---

# 205. CONNECTION POOL

Tune connection pools according to:

    API workers
    background workers
    vector queries
    database capacity

---

# 206. WORKER DATABASE ACCESS

Do not let every video-processing worker open unlimited connections.

---

# 207. BATCH INSERTS

For high-volume detections/embeddings:

    use controlled batch insertion

where it preserves correctness.

---

# 208. BATCH TRANSACTION SIZE

Do not create huge transactions that:

    lock excessively
    exhaust memory
    create long rollback times

---

# 209. PARTIAL BATCH FAILURE

Batch processing must preserve which records were successfully committed and which were not.

---

# 210. IDEMPOTENT BATCHING

Retries should not create duplicate observations.

Use deterministic IDs/constraints where needed.

---

# 211. SOURCE FRAME RETENTION

Retaining frame rows without retaining the referenced source context creates misleading provenance.

---

# 212. DELETION ORDER

When derived data is removed:

    vector
       ↓
    embedding/derived record
       ↓
    candidate/sighting

dependency rules must be defined.

Do not delete a parent before understanding child semantics.

---

# 213. LEGAL/FORENSIC PRESERVATION

Any deletion/retention behavior must follow the broader CrimeKit preservation policy.

---

# 214. VECTOR DEINDEXING

When an embedding expires/deletes:

    remove/disable it from searchable vector scope.

Do not rely only on a future cleanup job if the policy requires immediate exclusion.

---

# 215. PROJECTION RECONCILIATION

Periodic process:

    PostgreSQL
       ↓
    compare
       ↓
    pgvector
    Neo4j
    events

identify drift.

---

# 216. RECONCILIATION OUTPUT

Potential statuses:

    CONSISTENT
    VECTOR_MISSING
    GRAPH_MISSING
    ORPHAN
    PROJECTION_STALE

---

# 217. RECONCILIATION SECURITY

Reconciliation logs must not expose raw biometric data.

---

# 218. DATABASE HEALTH CHECK

Application readiness should verify only necessary dependencies.

Do not expose detailed database internals publicly.

---

# 219. FAILURE MODE — DB DOWN

Expected:

    API returns safe dependency error
    workers back off
    no false completion

---

# 220. FAILURE MODE — VECTOR DOWN

Expected:

    upstream source processing can remain identifiable
    matching stage fails/degrades
    no-match is not fabricated

---

# 221. FAILURE MODE — GRAPH DOWN

Expected:

    core relational result remains available
    projection marked unavailable

---

# 222. FAILURE MODE — EVENT OUTBOX DELAY

Expected:

    domain result durable
    realtime delivery delayed

---

# 223. SCHEMA SECURITY PRINCIPLE

A database schema is part of the security boundary.

Correctness alone is insufficient.

---

# 224. DATABASE ACCESS PRINCIPLE

Least privilege:

    investigators → APIs
    API → required domain tables
    workers → processing tables
    vector service → vector data
    graph projector → projection inputs
    admins → controlled elevated access

---

# 225. NO FRONTEND DB ACCESS

React must never directly connect to:

    PostgreSQL
    pgvector
    Neo4j

---

# 226. NO MODEL DB BYPASS

InsightFace worker must not create its own separate database for face records unless explicitly approved.

---

# 227. NO SHADOW STORAGE

Do not create:

    local SQLite
    arbitrary JSON file database
    hidden vector index

as a permanent parallel source of truth.

---

# 228. DATABASE DEPENDENCY MATRIX

| Component | Reads | Writes |
|---|---|---|
| FastAPI | domain state | search/job/review |
| Processing worker | source/config | detection/track/embedding |
| Matching worker | reference/vector | candidate/sighting |
| Vector layer | embeddings | vector index |
| Graph projector | domain events/state | Neo4j |
| Realtime layer | events/domain state | transient state |
| React | API/events | review through API |

Actual implementation may consolidate components.

---

# 229. SCHEMA REVIEW CHECKLIST

Before implementation:

[ ] Existing CrimeKit case/evidence schema inspected.

[ ] Existing audit schema inspected.

[ ] Existing user/RBAC schema inspected.

[ ] Existing evidence/artifact IDs reused.

[ ] Existing migration tool identified.

[ ] Existing pgvector setup inspected.

[ ] Existing Neo4j conventions inspected.

[ ] Naming conventions matched.

---

# 230. IMPLEMENTATION ORDER

Recommended:

## Phase 1

    inspect existing schema

## Phase 2

    create policy/model metadata

## Phase 3

    create reference/search/run

## Phase 4

    create frame/detection/track

## Phase 5

    create embedding/vector support

## Phase 6

    create candidate/sighting

## Phase 7

    create reviews

## Phase 8

    create outbox/projection state

## Phase 9

    indexes/constraints

## Phase 10

    retention/reconciliation

---

# 231. FIRST MIGRATION RULE

Before adding Face Trace tables, verify whether CrimeKit already has equivalent:

    evidence
    artifacts
    jobs
    audit
    users
    review
    event

tables.

Reuse instead of duplicating.

---

# 232. NO DUPLICATE CASE TABLE

Do not create:

    face_cases

if CrimeKit already has:

    cases.

---

# 233. NO DUPLICATE EVIDENCE TABLE

Do not create:

    face_evidence

if CrimeKit already has:

    evidence.

---

# 234. NO DUPLICATE USER TABLE

Use existing identity/RBAC tables.

---

# 235. NO DUPLICATE AUDIT SYSTEM

Use existing CrimeKit audit architecture.

---

# 236. NO DUPLICATE JOB SYSTEM

If Temporal/workflow owns durable jobs:

    Face Trace tables should reference that execution context.

---

# 237. NO DUPLICATE EVENT BUS

Use established CrimeKit event infrastructure.

---

# 238. NO DUPLICATE VECTOR STORE

If pgvector is already established:

    extend it safely.

Do not introduce another vector database without architectural justification.

---

# 239. NO DUPLICATE GRAPH

If Neo4j is the established graph:

    project into Neo4j

rather than adding another graph store.

---

# 240. SCHEMA COMPATIBILITY

The Face Trace schema must coexist with existing:

    evidence
    chain of custody
    forensic processing
    artifact normalization
    entity graph
    AI pipeline

without duplicating their responsibilities.

---

# 241. CHAIN OF CUSTODY LINK

When the selected evidence system has chain-of-custody records, Face Trace must reference the evidence identity rather than rebuilding chain-of-custody history.

---

# 242. FORENSIC PROCESSING LINK

Face Trace processing runs should be distinguishable from generic forensic jobs while remaining compatible with the existing processing architecture.

---

# 243. ARTIFACT LINK

Face Trace references source artifact IDs.

---

# 244. ENTITY LINK

A reviewed relationship to a CrimeKit entity remains a separate relationship from the original candidate.

---

# 245. TIMELINE LINK

Sighting can feed the common timeline through stable sighting IDs/source timestamps.

---

# 246. REPORT LINK

Reports reference sighting/provenance IDs rather than copying all underlying state.

---

# 247. SCHEMA DEFINITION OF DONE

[ ] Existing CrimeKit schema inspected.

[ ] No duplicate case/evidence/user/audit system.

[ ] Search schema implemented.

[ ] Reference schema implemented.

[ ] Processing run schema implemented.

[ ] Detection/track schema implemented.

[ ] Embedding/pgvector schema implemented.

[ ] Candidate schema implemented.

[ ] Sighting schema implemented.

[ ] Review history implemented.

[ ] Provenance foreign keys implemented.

[ ] Case/investigation isolation enforced.

[ ] Required indexes added.

[ ] Retention policy represented.

[ ] Projection state handled.

[ ] Event/outbox integration handled.

[ ] Migration tested.

[ ] Backup/restore tested.

[ ] Integrity checks implemented.

---

# 248. FINAL DATA MODEL

The authoritative relational flow is:

    CASE
      ↓
    INVESTIGATION
      ↓
    FACE_REFERENCE
      ↓
    REFERENCE_EMBEDDING

    CASE
      ↓
    INVESTIGATION
      ↓
    FACE_SEARCH
      ↓
    PROCESSING_RUN
      ↓
    SOURCE_ARTIFACT
      ↓
    FRAME
      ↓
    DETECTION
      ↓
    TRACK
      ↓
    CANDIDATE_EMBEDDING
      ↓
    FACE_CANDIDATE
      ↓
    FACE_SIGHTING
      ↓
    FACE_REVIEW

Supporting projections:

    FACE_EMBEDDING → pgvector
    DOMAIN RECORDS → Neo4j
    DOMAIN EVENTS → event bus
    DOMAIN + OUTBOX → realtime delivery

---

# 249. FINAL DATABASE PRINCIPLE

The database must never reduce Face Trace to:

    vector
       ↓
    score

Instead it must preserve:

    source
      ↓
    processing context
      ↓
    observation
      ↓
    machine comparison
      ↓
    candidate
      ↓
    sighting
      ↓
    human review

The schema is successful only when an authorized investigator can trace a result from the candidate back to the original evidence and understand exactly which processing/model/policy context produced it.

---

# 250. FINAL RULE

PostgreSQL is the authoritative forensic domain record according to the CrimeKit architecture.

pgvector answers:

    "Which compatible vectors are nearest?"

Neo4j answers:

    "How are authorized domain records related?"

The API answers:

    "What may this investigator see?"

The realtime layer answers:

    "What changed?"

The evidence system answers:

    "What is the source?"

Face Trace must preserve all five boundaries rather than collapse them into one database record.
